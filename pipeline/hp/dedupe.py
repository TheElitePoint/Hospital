"""SOP 2/3 duplicate detection with hard and review-only keys."""
from __future__ import annotations

import re
from .db import now


def norm(value):
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def linkedin_key(url):
    match = re.search(r"linkedin\.com/in/([^/?#]+)", url or "", re.I)
    return match.group(1).lower().strip() if match else None


def add_candidate(con, person_id, candidate_id, key_type, key_value):
    a, b = sorted((person_id, candidate_id))
    con.execute("""INSERT OR IGNORE INTO duplicate_candidates
      (person_id,candidate_person_id,key_type,key_value,resolution_status,detected_at)
      VALUES (?,?,?,?,'UNRESOLVED',?)""", (a, b, key_type, key_value, now()))


def audit(con):
    """Backfill canonical keys and route ambiguous identities away from Golden."""
    rows = [dict(r) for r in con.execute("SELECT person_id,account_id,full_name,current_title,linkedin_profile_url FROM people ORDER BY person_id")]
    by_li, by_name_account, by_title_account = {}, {}, {}
    confirmed, ambiguous, title_collisions = 0, 0, 0
    for row in rows:
        lk, nn, nt = linkedin_key(row["linkedin_profile_url"]), norm(row["full_name"]), norm(row["current_title"])
        if lk:
            if lk in by_li:
                # Keep the canonical key on the winning row only. The duplicate remains
                # auditable without violating the unique-key invariant.
                con.execute("UPDATE people SET linkedin_canonical_key=NULL,normalized_name=?,normalized_title=? WHERE person_id=?",
                            (nn, nt, row["person_id"]))
                add_candidate(con, row["person_id"], by_li[lk], "LINKEDIN", lk)
                con.execute("UPDATE people SET duplicate_status='DUPLICATE',person_status='REJECT',reject_reason_code='P-R05_DUPLICATE_PERSON',stage_status='REJECT' WHERE person_id=?", (row["person_id"],))
                con.execute("UPDATE validations SET duplicate_status='DUPLICATE',duplicate_of_person_id=?,validation_status='VALIDATED_REJECT',handoff_ready=0,reject_reason_code='P-R05_DUPLICATE_PERSON' WHERE person_id=?", (by_li[lk], row["person_id"]))
                confirmed += 1
            else:
                con.execute("UPDATE people SET linkedin_canonical_key=?,normalized_name=?,normalized_title=? WHERE person_id=?",
                            (lk, nn, nt, row["person_id"]))
                by_li[lk] = row["person_id"]
        else:
            con.execute("UPDATE people SET linkedin_canonical_key=NULL,normalized_name=?,normalized_title=? WHERE person_id=?",
                        (nn, nt, row["person_id"]))
        nk = f"{row['account_id']}|{nn}" if nn else None
        if nk:
            if nk in by_name_account and by_name_account[nk] != row["person_id"]:
                other = by_name_account[nk]; add_candidate(con, row["person_id"], other, "NAME_ACCOUNT", nk)
                # Same name and account can be two humans. It is an identity REVIEW, never an automatic merge.
                con.execute("UPDATE people SET person_status='REVIEW',review_reason='P-R06_IDENTITY_AMBIGUOUS',missing_fact='Resolve same-name people at this account',next_verification_action='Compare LinkedIn member identity, title history and official bio' WHERE person_id IN (?,?)", (row["person_id"], other))
                con.execute("UPDATE validations SET validation_status='VALIDATED_REVIEW',handoff_ready=0,missing_fact='Resolve same-name identity collision' WHERE person_id IN (?,?)", (row["person_id"], other))
                ambiguous += 1
            else: by_name_account[nk] = row["person_id"]
        tk = f"{row['account_id']}|{nt}" if nt and nt != "unknown" else None
        if tk:
            if tk in by_title_account and by_title_account[tk] != row["person_id"]:
                add_candidate(con, row["person_id"], by_title_account[tk], "TITLE_ACCOUNT", tk)
                title_collisions += 1
            else: by_title_account[tk] = row["person_id"]
    con.commit()
    return {"people_scanned": len(rows), "confirmed_duplicates": confirmed,
            "identity_ambiguities": ambiguous, "title_collision_flags": title_collisions,
            "unresolved_candidates": con.execute("SELECT COUNT(*) FROM duplicate_candidates WHERE resolution_status='UNRESOLVED'").fetchone()[0]}
