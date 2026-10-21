"""Import the live SOP pipeline JSON into the architecture SQLite store.

The legacy runner remains the data-acquisition engine while the architecture build is
completed. SQLite is authoritative for the web dashboard and exports. Imports are keyed,
transactional and preserve one canonical LinkedIn URL per person.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from . import db


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "input.json"


def _columns(con, table):
    return {row[1] for row in con.execute(f"PRAGMA table_info({table})")}


def _filtered(con, table, record):
    allowed = _columns(con, table)
    return {key: value for key, value in record.items() if key in allowed}


def _json(value):
    return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value


def _upsert(con, table, record, pk):
    row = _filtered(con, table, record)
    if not row.get(pk):
        return False
    keys = list(row)
    assignments = ",".join(f"{key}=excluded.{key}" for key in keys if key != pk)
    con.execute(
        f"INSERT INTO {table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)}) "
        f"ON CONFLICT({pk}) DO UPDATE SET {assignments}",
        [_json(row[key]) for key in keys],
    )
    return True


def import_current(con, input_path=None):
    path = Path(input_path or DEFAULT_INPUT)
    if not path.exists():
        # Fresh architecture installs have no legacy JSON. The CMS universe is the
        # source in that case; importing is an optional migration, never a blocker.
        return {name: 0 for name in ("accounts", "people", "validations", "evidence", "corrections")} | {
            "skipped_duplicate_profiles": 0, "source": "not_present"
        }
    payload = json.loads(path.read_text())
    counts = {name: 0 for name in ("accounts", "people", "validations", "evidence", "corrections")}
    skipped_duplicates = 0
    with con:
        for account in payload.get("accounts", []):
            row = dict(account)
            row["why_operating_environment"] = row.get("why_operating_environment") or row.get("why_this_account_operating_environment")
            row["why_likely_problem"] = row.get("why_likely_problem") or row.get("why_this_account_likely_problem")
            row["why_commercial_route"] = row.get("why_commercial_route") or row.get("why_this_account_commercial_route")
            row["stage_status"] = "PASS" if row.get("qualification_status") == "PASS" else row.get("qualification_status", "PENDING")
            counts["accounts"] += int(_upsert(con, "accounts", row, "account_id"))
            con.execute("DELETE FROM account_signals WHERE account_id=?", (row.get("account_id"),))
            for signal_class, field in (("CORE", "core_signals"), ("SUPPORTING", "supporting_signals")):
                for signal in account.get(field, []) or []:
                    con.execute("INSERT OR IGNORE INTO account_signals(account_id,signal_class,signal_code) VALUES (?,?,?)",
                                (row.get("account_id"), signal_class, signal))

        for person in payload.get("people", []):
            row = dict(person)
            from .dedupe import linkedin_key, norm
            row["linkedin_canonical_key"] = linkedin_key(row.get("linkedin_profile_url"))
            row["normalized_name"] = norm(row.get("full_name")); row["normalized_title"] = norm(row.get("current_title"))
            row["better_person_json"] = row.get("better_person_json") or row.get("better_person_test")
            row["stage_status"] = "PASS" if row.get("person_status") == "PERSON_PASS" else row.get("person_status", "PENDING")
            try:
                counts["people"] += int(_upsert(con, "people", row, "person_id"))
            except sqlite3.IntegrityError as error:
                if "people.linkedin_profile_url" not in str(error):
                    raise
                skipped_duplicates += 1

        for validation in payload.get("validations", []):
            row = dict(validation)
            row["handoff_ready"] = int(bool(row.get("handoff_ready", row.get("validation_status") == "VALIDATED_PASS")))
            row["problem_ownership_level"] = row.get("problem_ownership_level") or row.get("validated_problem_ownership_level")
            counts["validations"] += int(_upsert(con, "validations", row, "person_id"))

        for evidence in payload.get("evidence", []):
            row = dict(evidence)
            row["subject_type"] = "PERSON" if row.get("person_id") not in (None, "", "NOT_APPLICABLE") else "ACCOUNT"
            row["subject_id"] = row.get("person_id") if row["subject_type"] == "PERSON" else row.get("account_id")
            row["verbatim_verified"] = int(bool(row.get("evidence_excerpt") and row.get("source_url")))
            counts["evidence"] += int(_upsert(con, "evidence", row, "evidence_id"))

        existing_corrections = {
            (r[0], r[1], r[2], r[3], r[4]) for r in con.execute(
                "SELECT subject_id,field_name,old_value,new_value,changed_at FROM correction_log"
            )
        }
        for correction in payload.get("corrections", []):
            row = dict(correction)
            key = (str(row.get("subject_id") or row.get("person_id") or row.get("account_id") or ""),
                   str(row.get("field_name") or row.get("field") or ""), str(row.get("old_value") or ""),
                   str(row.get("new_value") or ""), str(row.get("changed_at") or row.get("corrected_at") or ""))
            if key in existing_corrections:
                continue
            con.execute("""INSERT INTO correction_log
                (subject_type,subject_id,field_name,old_value,new_value,change_type,reason,evidence_ids,changed_at,changed_by)
                VALUES (?,?,?,?,?,?,?,?,?,?)""", (
                    row.get("subject_type") or "PERSON", key[0], key[1], key[2], key[3],
                    row.get("change_type") or row.get("correction_type") or "CORRECTION",
                    row.get("reason") or row.get("correction_reason") or "Imported correction",
                    _json(row.get("evidence_ids") or []), key[4] or db.now(),
                    row.get("changed_by") or row.get("corrected_by") or "pipeline-import",
                ))
            existing_corrections.add(key)
            counts["corrections"] += 1
    counts["skipped_duplicate_profiles"] = skipped_duplicates
    return counts

def import_google_sheet(con, sheet_id, credentials_path):
    """One-time/idempotent migration of the current operational Sheet into SQLite."""
    from .sheets import open_sheet
    sheet = open_sheet(sheet_id, credentials_path)
    specs = [("01 Accounts", "accounts", "account_id"), ("02 People", "people", "person_id"),
             ("03 Validation", "validations", "person_id"), ("04 Golden", "golden", "canonical_person_id")]
    counts = {}
    with con:
        for tab, table, pk in specs:
            n = 0
            for source in sheet.worksheet(tab).get_all_records(default_blank=""):
                row = {k: v for k, v in source.items() if k in _columns(con, table) and v not in ("", None)}
                if table == "people":
                    from .dedupe import linkedin_key, norm
                    url = str(row.get("linkedin_profile_url") or "")
                    if "linkedin.com/in/" not in url.lower():
                        row.pop("linkedin_profile_url", None)
                        row.update({"linkedin_identity_status":"NOT_FOUND", "person_status":"REVIEW",
                                    "missing_fact":"A valid matched LinkedIn profile is required",
                                    "next_verification_action":"Find and verify the exact LinkedIn /in/ profile"})
                    else:
                        row["linkedin_canonical_key"] = linkedin_key(url)
                    row["normalized_name"] = norm(row.get("full_name")); row["normalized_title"] = norm(row.get("current_title"))
                if table == "accounts": row.setdefault("stage_status", row.get("qualification_status", "PENDING"))
                if table == "validations": row["handoff_ready"] = int(str(row.get("handoff_ready", "")).lower() in {"1","true","yes"})
                n += int(_upsert(con, table, row, pk))
            counts[tab] = n
        n = 0
        for source in sheet.worksheet("Evidence").get_all_records(default_blank=""):
            row = {k: v for k, v in source.items() if k in _columns(con, "evidence") and v not in ("", None)}
            row["subject_type"] = "PERSON" if source.get("person_id") not in ("", "NOT_APPLICABLE") else "ACCOUNT"
            row["subject_id"] = source.get("person_id") if row["subject_type"] == "PERSON" else source.get("account_id")
            if row.get("evidence_id") and row.get("subject_id"):
                n += int(_upsert(con, "evidence", row, "evidence_id"))
        counts["Evidence"] = n
    return counts
