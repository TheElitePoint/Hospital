"""Google Sheets export - the shareable layer.

Division of labour agreed at design time:
  SQLite = system of record (evidence graph, correction log, decisions)
  Sheets = what the team opens. The Golden tab is the contact-ready deliverable.

Write discipline:
  - machine tabs are rewritten wholesale from the DB on each sync, keyed by a stable
    row_key, so re-sorting in the UI can never corrupt state
  - exactly five columns are human-owned and read BACK into the DB; everything else
    is machine-owned and will be overwritten
  - a manual override without a reason is refused and reported on 00_Control
"""
import json
from .db import now

HUMAN_COLUMNS = ["qa_decision", "qa_reviewer_id", "qa_notes",
                 "manual_override_status", "override_reason"]

# The deliverable. Ordered for someone doing outreach, not for a database admin.
GOLDEN_COLUMNS = [
    ("golden_rank", "Rank"),
    ("qualification_tier", "Validated?"),
    ("full_name", "Name"),
    ("validated_current_title", "Title"),
    ("validated_department", "Department"),
    ("account_name", "Hospital / System"),
    ("city", "City"),
    ("state", "State"),
    ("linkedin_profile_url", "LinkedIn"),
    ("validated_priority", "Priority"),
    ("validated_commercial_role", "Commercial Role"),
    ("validated_role_family", "Function"),
    ("role_scope", "Scope"),
    ("primary_use_case", "Use Case"),
    ("golden_selection_reason", "Why This Person"),
    ("account_priority", "Account Priority"),
    ("account_archetype", "Archetype"),
    ("current_signal", "Timing Signal"),
    ("linkedin_activity_status", "LinkedIn Activity"),
    ("last_visible_reaction_date", "Last Reaction"),
    ("golden_priority_score", "Score"),
    # component scores stay visible - SOP 4 s22 forbids shipping one black-box number
    ("account_quality_score", "s: Account"),
    ("use_case_strength_score", "s: Use Case"),
    ("problem_ownership_score", "s: Ownership"),
    ("commercial_influence_score", "s: Influence"),
    ("validated_priority_score", "s: Priority"),
    ("current_signal_score", "s: Timing"),
    ("evidence_confidence_score", "s: Evidence"),
    ("linkedin_reachability_score", "s: Reach"),
    ("incremental_value", "Incremental Value"),
    ("account_id", "Account ID"),
    ("canonical_person_id", "Person ID"),
] + [(c, c.replace("_", " ").title()) for c in HUMAN_COLUMNS]

REVIEW_COLUMNS = [
    ("review_value_score", "Resolution Value"),
    ("subject_type", "Type"), ("subject_id", "ID"),
    ("full_name", "Name"), ("title", "Title"),
    ("account_name", "Hospital / System"), ("state", "State"),
    ("stage", "Stage"), ("status", "Status"),
    ("missing_fact", "Missing Fact"),
    ("why_it_matters", "Why It Matters"),
    ("best_verification_source", "Best Source"),
    ("next_verification_action", "Exact Next Action"),
    ("linkedin_profile_url", "LinkedIn"),
] + [(c, c.replace("_", " ").title()) for c in HUMAN_COLUMNS]

ACCOUNT_COLUMNS = [
    ("account_id","Account ID"), ("canonical_account_name","Account"),
    ("parent_system_name","Parent System"), ("city","City"), ("state","State"),
    ("account_archetype","Archetype"), ("bed_count","Beds"),
    ("qualification_status","Status"), ("priority_class","Priority"),
    ("primary_use_case","Primary Use Case"), ("current_signal","Current Signal"),
    ("core_signals","Core Signals"), ("supporting_signals","Supporting Signals"),
    ("linkedin_company_url","LinkedIn Company"), ("linkedin_industry","LinkedIn Industry"),
    ("linkedin_sector_status","Sector Status"),
    ("relationship_overlap_status","Relationship Overlap"),
    ("negative_evidence_summary","Negative Evidence"),
    ("why_operating_environment","Operating Environment"),
    ("why_likely_problem","Likely Problem"), ("why_commercial_route","Commercial Route"),
    ("reject_reason_code","Reject Code"), ("review_reason_code","Review Code"),
    ("evidence_count","Evidence Rows"), ("handoff_ready","Handoff Ready"),
] + [(c, c.replace("_", " ").title()) for c in HUMAN_COLUMNS]

TABS = {
    "00_Control": None, "01_Universe": None, "02_Accounts": ACCOUNT_COLUMNS,
    "03_Account_Evidence": None, "04_People": None, "05_Validation": None,
    "06_Correction_Log": None, "07_Golden": GOLDEN_COLUMNS,
    "08_Review_Queue": REVIEW_COLUMNS, "09_Metrics": None, "10_Rejects": None,
}

def open_sheet(spreadsheet_id, credentials_path):
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    return gspread.authorize(creds).open_by_key(spreadsheet_id)

def _rows(records, columns):
    header = [label for _, label in columns]
    body = []
    for r in records:
        body.append([_cell(r.get(key)) for key, _ in columns])
    return [header] + body

def _cell(v):
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v)
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    return v

def write_tab(sheet, tab_name, records, columns, freeze_header=True):
    import gspread
    try:
        ws = sheet.worksheet(tab_name)
    except Exception:
        ws = sheet.add_worksheet(title=tab_name, rows=max(len(records) + 50, 100),
                                 cols=max(len(columns) + 2, 12))
    values = _rows(records, columns)
    ws.clear()
    ws.update(values, "A1", value_input_option="RAW")
    if freeze_header:
        ws.freeze(rows=1)
        ws.format("1:1", {"textFormat": {"bold": True},
                          "backgroundColor": {"red": .93, "green": .93, "blue": .93}})
    return len(values) - 1

def _green_rows(sheet, ws, ncols):
    """0-based data-row indexes (header excluded) where a person colored any cell green.
    Those rows belong to someone else's review, so the sync leaves their values alone."""
    meta = sheet.fetch_sheet_metadata(params={
        "includeGridData": True,
        "ranges": [f"'{ws.title}'!A1:{gspread_utils_a1(ncols)}"],
        "fields": "sheets.data.rowData.values.effectiveFormat.backgroundColor"})
    rows = meta["sheets"][0]["data"][0].get("rowData", [])
    body = rows[1:]
    hits = []
    for row in body:
        cols = set()
        for k, cell in enumerate(row.get("values", [])):
            c = (cell.get("effectiveFormat") or {}).get("backgroundColor") or {}
            r, g, b = c.get("red", 0), c.get("green", 0), c.get("blue", 0)
            if g > r + .08 and g > b + .08:
                cols.add(k)
        hits.append(cols)
    # A column that is green on most rows is the tab's own styling, not someone's review mark.
    counts = {}
    for cols in hits:
        for k in cols:
            counts[k] = counts.get(k, 0) + 1
    styled = {k for k, n in counts.items() if n > .5 * max(len(body), 1)}
    green = {i for i, cols in enumerate(hits) if cols - styled}
    return green

def gspread_utils_a1(ncols):
    import gspread
    return gspread.utils.rowcol_to_a1(1, ncols).rstrip("0123456789")

def _write_existing(sheet, tab_name, records):
    """Update an existing machine tab using its exact snake_case schema, in place.

    Never reorders or drops a row that was already in the tab - existing rows keep
    their exact sheet position (and whatever background color someone may have set on
    them, e.g. green for "reviewed"; untouched, not even reset). A row is updated with
    fresh values if the pipeline still has a record for that key, but the row itself
    stays where it is. Only genuinely new keys are appended at the bottom, with a
    plain white background so they read as new rather than inheriting a stale color
    from whatever used to be at that sheet position."""
    import gspread
    ws = sheet.worksheet(tab_name)
    headers = ws.row_values(1)
    if not headers and records:
        # A previous sync that died between clear() and update() leaves the tab blank;
        # rebuild the header row from the record keys instead of failing forever.
        headers = list(records[0].keys())
    key_col = headers[0] if headers else None
    existing_rows = ws.get_all_values()[1:] if key_col else []
    by_key = {str(r.get(key_col)): r for r in records}
    seen_keys = set()

    frozen = _green_rows(sheet, ws, len(headers)) if existing_rows else set()
    updated_existing = []
    for i, row in enumerate(existing_rows):
        key = row[0] if row else None
        seen_keys.add(key)
        rec = by_key.get(key)
        # Green rows were marked by someone else: keep their values exactly as they are.
        keep = row + [""] * (len(headers) - len(row)) if i in frozen else None
        updated_existing.append(keep if keep is not None else ([_cell(rec.get(h)) for h in headers] if rec else row))
    new_records = [r for r in records if str(r.get(key_col)) not in seen_keys]
    new_rows = [[_cell(r.get(h)) for h in headers] for r in new_records]

    values = [headers] + updated_existing + new_rows
    # Overwrite in place rather than clear-then-write: rows are never dropped, so the
    # new block always covers the old one, and a crash mid-sync can no longer leave
    # the tab blank.
    ws.update(values, "A1", value_input_option="RAW")
    ws.freeze(rows=1)
    ws.format("1:1", {"textFormat": {"bold": True},
                      "backgroundColor": {"red": .93, "green": .93, "blue": .93}})
    if new_rows:
        first_new_row = len(updated_existing) + 2  # +1 header, +1 to convert to 1-indexed
        last_new_row = first_new_row + len(new_rows) - 1
        ws.format(f"A{first_new_row}:{gspread.utils.rowcol_to_a1(last_new_row, len(headers))}",
                  {"backgroundColor": {"red": 1, "green": 1, "blue": 1}})
    return len(records)

def sync_operational(con, spreadsheet_id, credentials_path):
    """DB -> the user's existing seven-tab operational workbook."""
    sheet = open_sheet(spreadsheet_id, credentials_path)
    accounts = [dict(r) for r in con.execute("""SELECT a.*,
      (SELECT GROUP_CONCAT(signal_code) FROM account_signals s WHERE s.account_id=a.account_id AND s.signal_class='CORE') core_signals,
      (SELECT GROUP_CONCAT(signal_code) FROM account_signals s WHERE s.account_id=a.account_id AND s.signal_class='SUPPORTING') supporting_signals
      FROM accounts a WHERE a.qualification_status IS NOT NULL ORDER BY a.account_id""").fetchall()]
    people = [dict(r) for r in con.execute("SELECT * FROM people ORDER BY person_id").fetchall()]
    validations = [dict(r) for r in con.execute("""SELECT v.*,p.full_name,p.linkedin_profile_url FROM validations v
      LEFT JOIN people p ON p.person_id=v.person_id ORDER BY v.person_id""").fetchall()]
    golden = [dict(r) for r in con.execute("SELECT * FROM golden ORDER BY golden_rank,canonical_person_id").fetchall()]
    evidence = []
    for row in con.execute("SELECT * FROM evidence ORDER BY evidence_id").fetchall():
        d = dict(row); d["account_id"] = d["subject_id"] if d["subject_type"] == "ACCOUNT" else "NOT_APPLICABLE"
        d["person_id"] = d["subject_id"] if d["subject_type"] == "PERSON" else "NOT_APPLICABLE"; evidence.append(d)
    corrections = [dict(r) for r in con.execute("SELECT * FROM correction_log ORDER BY id").fetchall()]
    return {"01 Accounts": _write_existing(sheet, "01 Accounts", accounts),
            "02 People": _write_existing(sheet, "02 People", people),
            "03 Validation": _write_existing(sheet, "03 Validation", validations),
            "04 Golden": _write_existing(sheet, "04 Golden", golden),
            "Evidence": _write_existing(sheet, "Evidence", evidence),
            "Corrections": _write_existing(sheet, "Corrections", corrections)}

def golden_records(con, cycle=None):
    """The contact-ready deliverable. Joins account context onto the locked Golden set."""
    q = """SELECT g.*, a.canonical_account_name AS account_name, a.city, a.state,
                  h.qa_decision, h.qa_reviewer_id, h.qa_notes,
                  h.manual_override_status, h.override_reason
           FROM golden g
           LEFT JOIN accounts a ON a.account_id = g.account_id
           LEFT JOIN human_input h ON h.subject_type='GOLDEN' AND h.subject_id=g.canonical_person_id
           WHERE g.golden_status='GOLDEN_SELECTED'"""
    args = []
    if cycle:
        q += " AND g.selection_cycle=?"; args.append(cycle)
    q += " ORDER BY g.golden_rank"
    return [dict(r) for r in con.execute(q, args).fetchall()]

def review_queue(con, pass_count=None, share=0.30):
    """The 30% review slice.

    SOP 4 s01.1 bars a REVIEW record from Golden, so this is NOT an alternate route into
    the deliverable. It is a human work queue, capped at `share` of PASS volume and ranked
    by resolution value: how likely clearing this record is to yield a Golden-eligible
    person. Records that resolve to PASS then compete normally on the next SOP 4 run.
    """
    if pass_count is None:
        pass_count = con.execute(
            "SELECT COUNT(*) c FROM validations WHERE validation_status='VALIDATED_PASS'"
        ).fetchone()["c"]
    cap = max(int(round(pass_count * share)), 0)

    rows = []
    for r in con.execute("""
        SELECT v.person_id AS subject_id, 'PERSON' AS subject_type, p.full_name, 
               COALESCE(v.validated_current_title, p.current_title) AS title,
               a.canonical_account_name AS account_name, a.state,
               'SOP3' AS stage, v.validation_status AS status,
               v.missing_fact, v.why_it_matters, v.best_verification_source,
               v.next_verification_action, p.linkedin_profile_url,
               v.validated_priority, v.validated_commercial_role, a.priority_class
        FROM validations v
        JOIN people p ON p.person_id = v.person_id
        LEFT JOIN accounts a ON a.account_id = v.account_id
        WHERE v.validation_status='VALIDATED_REVIEW'""").fetchall():
        d = dict(r)
        d["review_value_score"] = round(resolution_value(d), 2)
        rows.append(d)

    for r in con.execute("""
        SELECT a.account_id AS subject_id, 'ACCOUNT' AS subject_type,
               a.canonical_account_name AS full_name, '' AS title,
               a.canonical_account_name AS account_name, a.state,
               'SOP1' AS stage, a.qualification_status AS status,
               a.missing_fact, a.why_it_matters, a.verification_source AS best_verification_source,
               a.next_verification_action, '' AS linkedin_profile_url,
               '' AS validated_priority, '' AS validated_commercial_role, a.priority_class
        FROM accounts a WHERE a.qualification_status='REVIEW'""").fetchall():
        d = dict(r)
        d["review_value_score"] = round(resolution_value(d), 2)
        rows.append(d)

    rows.sort(key=lambda d: (-d["review_value_score"], d["subject_id"]))
    return rows[:cap], cap, len(rows)

def resolution_value(d):
    """How much Golden capacity clearing this record is likely to unlock."""
    v = 0.0
    v += {"A_PRIORITY": 3.0, "B_PRIORITY": 2.0, "PASS_UNRANKED": 1.5}.get(d.get("priority_class"), 1.0)
    v += {"P1": 3.0, "P2": 2.0, "P3": 1.0}.get(d.get("validated_priority"), 0.5)
    v += {"DIRECT_OWNER": 3.0, "CO_OWNER": 2.5, "CLINICAL_EVALUATOR": 2.0,
          "TECHNICAL_EVALUATOR": 2.0, "EXECUTIVE_SPONSOR": 1.0, "INTERNAL_ROUTE": 0.5
          }.get(d.get("validated_commercial_role"), 1.0)
    # an account in review can unlock a whole buying group, so it outranks a single person
    if d.get("subject_type") == "ACCOUNT":
        v *= 1.6
    # a record with no concrete next action cannot be worked - deprioritise, don't hide
    if not (d.get("next_verification_action") or "").strip():
        v *= 0.4
    return v

def sync_human_input(con, sheet, tab_name, subject_type, id_column="ID"):
    """Sheets -> DB for the five human-owned columns only."""
    ws = sheet.worksheet(tab_name)
    records = ws.get_all_records()
    applied, refused = 0, []
    for row in records:
        sid = row.get(id_column) or row.get("Person ID") or row.get("Account ID")
        if not sid:
            continue
        payload = {c: (row.get(c.replace("_", " ").title()) or "").strip() for c in HUMAN_COLUMNS}
        if not any(payload.values()):
            continue
        if payload["manual_override_status"] and not payload["override_reason"]:
            refused.append(sid)          # s08: no hidden preference without a stated reason
            continue
        con.execute("""INSERT INTO human_input
            (subject_type,subject_id,qa_decision,qa_reviewer_id,qa_notes,
             manual_override_status,override_reason,synced_at)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(subject_type,subject_id) DO UPDATE SET
              qa_decision=excluded.qa_decision, qa_reviewer_id=excluded.qa_reviewer_id,
              qa_notes=excluded.qa_notes, manual_override_status=excluded.manual_override_status,
              override_reason=excluded.override_reason, synced_at=excluded.synced_at""",
            (subject_type, str(sid), payload["qa_decision"], payload["qa_reviewer_id"],
             payload["qa_notes"], payload["manual_override_status"],
             payload["override_reason"], now()))
        applied += 1
    con.commit()
    return applied, refused

def control_rows(con):
    def c(sql, *a):
        return con.execute(sql, a).fetchone()[0]
    return [
      {"metric": "Universe loaded", "value": c("SELECT COUNT(*) FROM universe")},
      {"metric": "Universe in scope (A1/A3 pass)", "value": c("SELECT COUNT(*) FROM universe WHERE in_scope=1")},
      {"metric": "Accounts created", "value": c("SELECT COUNT(*) FROM accounts")},
      {"metric": "Accounts PASS", "value": c("SELECT COUNT(*) FROM accounts WHERE qualification_status='PASS'")},
      {"metric": "Accounts REVIEW", "value": c("SELECT COUNT(*) FROM accounts WHERE qualification_status='REVIEW'")},
      {"metric": "Accounts REJECT", "value": c("SELECT COUNT(*) FROM accounts WHERE qualification_status='REJECT'")},
      {"metric": "People PERSON_PASS", "value": c("SELECT COUNT(*) FROM people WHERE person_status='PERSON_PASS'")},
      {"metric": "VALIDATED_PASS", "value": c("SELECT COUNT(*) FROM validations WHERE validation_status='VALIDATED_PASS'")},
      {"metric": "VALIDATED_REVIEW", "value": c("SELECT COUNT(*) FROM validations WHERE validation_status='VALIDATED_REVIEW'")},
      {"metric": "Golden selected", "value": c("SELECT COUNT(*) FROM golden WHERE golden_status='GOLDEN_SELECTED'")},
      {"metric": "Evidence rows", "value": c("SELECT COUNT(*) FROM evidence")},
      {"metric": "Corrections logged", "value": c("SELECT COUNT(*) FROM correction_log")},
      {"metric": "Last sync", "value": now()},
    ]
