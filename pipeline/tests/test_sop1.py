import sys, pathlib, tempfile, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp import db, sop1
from hp.db import upsert
from hp.sources import cms

PAGE_TELEM = ("Riverbend Community Hospital operates a 32-bed inpatient telemetry unit. "
  "Certified monitor technicians observe cardiac rhythms continuously from the unit. "
  "Rhythm strips are printed, measured by hand and scanned into the medical record each shift.")
PAGE_JOBS = ("Careers at Riverbend. Now hiring: Clinical Engineering Technician II, responsible for "
  "maintaining bedside patient monitoring devices across both campuses.")
PAGE_NEG  = "Riverbend Community Hospital annual community benefit report. Charity care totals."

PAGES = {"https://riverbendhospital.org/services/telemetry": PAGE_TELEM,
         "https://riverbendhospital.org/careers/clin-eng": PAGE_JOBS,
         "https://beckershospitalreview.com/riverbend": PAGE_NEG}

def fake_gather(con, pool, account, max_pages=14):
    srcs, pages = [], {}
    for i, (url, text) in enumerate(PAGES.items(), 1):
        sid = f"EV-{account['account_id'][-6:]}-{i:02d}"
        srcs.append({"evidence_id": sid, "source_url": url, "source_title": "t",
                     "source_date": "2026-05-02", "text": text})
        pages[url] = text
    return srcs, pages

def make_account(con, aid="US-IN-CCN150999"):
    upsert(con, "accounts", {"account_id": aid, "ccn": "150999",
      "canonical_account_name": "Riverbend Community Hospital", "facility_name": "Riverbend",
      "city": "Bloomington", "state": "IN", "account_archetype": "COMMUNITY_ACUTE",
      "stage_status": "PENDING", "gate_trace": json.dumps({"A0":"PASS","A1":"PASS","A2":"PASS","A3":"PASS"})},
      pk="account_id")
    con.commit()
    return dict(con.execute("SELECT * FROM accounts WHERE account_id=?", (aid,)).fetchone())

def run_with(model_output, aid):
    con = db.init(tempfile.mktemp(suffix=".db"))
    acct = make_account(con, aid)
    sop1.gather_sources = fake_gather
    sop1.extract = lambda *a, **k: model_output
    status = sop1.run_account(con, acct, None, None, "mock")
    row = dict(con.execute("SELECT * FROM accounts WHERE account_id=?", (aid,)).fetchone())
    sigs = [dict(r) for r in con.execute("SELECT * FROM account_signals WHERE account_id=?", (aid,))]
    ev = [dict(r) for r in con.execute("SELECT * FROM evidence WHERE subject_id=?", (aid,))]
    return status, row, sigs, ev

def ids(aid):
    """fake_gather mints ids from the account id, so build citations to match."""
    return f"EV-{aid[-6:]}-01", f"EV-{aid[-6:]}-02"

AID = "US-IN-CCN150999"
E1, E2 = ids(AID)
honest = {
 "core_signals":[{"code":"CS_TELEMETRY_CARDIAC_MONITORING","evidence_ids":[E1],
   "excerpt":"Certified monitor technicians observe cardiac rhythms continuously from the unit"}],
 "supporting_signals":[{"code":"SS_RELEVANT_HIRING","evidence_ids":[E2],
   "excerpt":"Now hiring: Clinical Engineering Technician II"}],
 "primary_use_case":{"code":"U1_DIGITAL_RHYTHM_WORKFLOW","evidence_ids":[E1],
   "excerpt":"Rhythm strips are printed, measured by hand and scanned into the medical record each shift",
   "rationale":"manual strip processing"},
 "secondary_use_cases":["U5_AUTOMATED_DOCUMENTATION"],
 "current_signal":{"value":"PRESENT","evidence_ids":[E2],"rationale":"relevant hiring"},
 "technology_context":{"telemetry_evidence_status":"CONFIRMED","cardiac_monitoring_status":"CONFIRMED",
   "clinical_engineering_status":"CONFIRMED","ehr_platform":"NOT_CHECKED","monitoring_vendors_found":[],
   "central_monitoring_status":"NOT_FOUND","tele_icu_status":"NOT_FOUND","virtual_care_status":"UNKNOWN",
   "manual_documentation_status":"CONFIRMED","interoperability_status":"UNKNOWN"},
 "core_problem_already_solved": False, "negative_evidence_summary":"NONE_FOUND",
 "parent_system_name":"NOT_APPLICABLE","canonical_domain":"riverbendhospital.org",
 "why_this_account":{"operating_environment":"32-bed telemetry unit with manual strip workflow",
   "likely_problem":"manual rhythm-strip handling","commercial_route":"telemetry leadership"},
 "unresolved_material_fact": None}

status, row, sigs, ev = run_with(honest, AID)
assert status == "PASS", (status, row["review_reason_code"])
assert row["primary_use_case"] == "U1_DIGITAL_RHYTHM_WORKFLOW"
assert row["priority_class"] == "B_PRIORITY" and row["current_signal"] == "PRESENT"
assert row["handoff_ready"] == 0, "handoff must stay false until Gate A11 runs"
assert {s["signal_code"] for s in sigs} == {"CS_TELEMETRY_CARDIAC_MONITORING","SS_RELEVANT_HIRING"}
assert all(e["verbatim_verified"] == 1 for e in ev)
assert {e["source_tier"] for e in ev} == {"A1","A2"}
print("1 honest extraction              -> PASS, U1, B_PRIORITY, 2 signals, tiers", sorted({e["source_tier"] for e in ev}))
print("   handoff_ready = 0 until A11 LinkedIn sector validation runs")

# model invents the core-signal excerpt -> must NOT pass
def retarget(payload, aid):
    a, b = ids(aid)
    out = json.loads(json.dumps(payload).replace(E1, a).replace(E2, b))
    return out

AID2 = "US-IN-CCN150998"
lying = retarget(honest, AID2)
lying["core_signals"][0]["excerpt"] = "the hospital runs a centralized monitoring command center"
status, row, sigs, ev = run_with(lying, AID2)
assert status == "REVIEW", status
assert row["review_reason_code"] == "A4_CORE_SIGNAL_UNVERIFIED"
assert "not verbatim" in row["missing_fact"]
assert "needs more research" not in (row["missing_fact"] or "").lower()
print("2 invented core excerpt          -> REVIEW", row["review_reason_code"])
print("   missing_fact:", row["missing_fact"][:72])

# supporting signal reusing the core evidence -> A5 review, not a free pass
AID3 = "US-IN-CCN150997"
reuse = retarget(honest, AID3)
reuse["supporting_signals"] = [{"code":"SS_DOCUMENTATION_AUTOMATION","evidence_ids":[ids(AID3)[0]],
  "excerpt":"Certified monitor technicians observe cardiac rhythms continuously from the unit"}]
status, row, sigs, ev = run_with(reuse, AID3)
assert status == "REVIEW" and row["review_reason_code"] == "A5_SUPPORTING_SIGNAL_MISSING"
print("3 supporting reuses core evidence-> REVIEW A5 (s03.6 held at gate level)")

# incumbent already solves the use case -> R04 reject
AID4 = "US-IN-CCN150996"
solved = retarget(honest, AID4)
solved["core_problem_already_solved"] = True
solved["negative_evidence_summary"] = "Enterprise vendor-neutral monitoring platform deployed across both campuses in 2026"
status, row, sigs, ev = run_with(solved, AID4)
assert status == "REJECT" and row["reject_reason_code"] == "R04_CORE_PROBLEM_ALREADY_SOLVED"
print("4 incumbent solves same use case -> REJECT R04")

# CMS classification gates
assert cms.classify({"state":"IN","hospital_type":"Acute Care Hospitals"})[:2] == (1,"COMMUNITY_ACUTE")
assert cms.classify({"state":"IN","hospital_type":"Critical Access Hospitals"})[:2] == (1,"CRITICAL_ACCESS")
assert cms.classify({"state":"WY","hospital_type":"Acute Care Hospitals"})[2] == "R01_OUT_OF_SCOPE_GEO"
assert cms.classify({"state":"TX","hospital_type":"Psychiatric"})[2] == "R02_WRONG_ACCOUNT_TYPE"
print("5 CMS free gates A1/A2/A3        -> COMMUNITY_ACUTE / CRITICAL_ACCESS / R01 / R02")
print("\nsop1: 5/5")
