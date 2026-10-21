import sys, pathlib, tempfile, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp import db, sop4, sheets
from hp.db import upsert

con = db.init(tempfile.mktemp(suffix=".db"))
rng = random.Random(7)

FAMS = ["TELEMETRY_CARDIAC_MONITORING","NURSING_EXECUTIVE","CLINICAL_ENGINEERING_HTM",
        "IT_CIO","NURSING_INFORMATICS","VIRTUAL_CARE_TELEHEALTH"]
ROLES = ["DIRECT_OWNER","CO_OWNER","CLINICAL_EVALUATOR","TECHNICAL_EVALUATOR","EXECUTIVE_SPONSOR","INTERNAL_ROUTE"]

# 40 accounts, 8 people each = 320 people
for ai in range(40):
    aid = f"US-IN-CCN15{ai:04d}"
    upsert(con, "accounts", {"account_id": aid, "ccn": f"15{ai:04d}",
        "canonical_account_name": f"Test Regional Hospital {ai}", "city": "Indianapolis",
        "state": "IN", "account_archetype": "COMMUNITY_ACUTE",
        "qualification_status": "PASS",
        "priority_class": rng.choice(["A_PRIORITY","B_PRIORITY","PASS_UNRANKED"]),
        "primary_use_case": "U1_DIGITAL_RHYTHM_WORKFLOW",
        "current_signal": rng.choice(["STRONG","PRESENT","NONE_FOUND"]),
        "handoff_ready": 1}, pk="account_id")
    for pi in range(8):
        pid = f"PER-{ai:03d}-{pi}"
        upsert(con, "people", {"person_id": pid, "account_id": aid,
            "full_name": f"Person {ai}-{pi}", "linkedin_profile_url": f"https://linkedin.com/in/p{ai}{pi}",
            "current_title": "Director", "person_status": "PERSON_PASS"}, pk="person_id")
        # 12% land in review, to exercise the 30% queue
        review = rng.random() < 0.12
        upsert(con, "validations", {"person_id": pid, "canonical_person_id": f"CP-{ai:03d}-{pi}",
            "account_id": aid,
            "employment_status": "CURRENT_CONFIRMED" if not review else "CONFLICT",
            "account_entity_match": "DIRECT_ACCOUNT_MATCH",
            "validated_current_title": "Director of Telemetry",
            "validated_department": "Telemetry", "validated_role_family": rng.choice(FAMS),
            "role_scope": rng.choice(["FACILITY_LEVEL","SYSTEM_LEVEL"]),
            "primary_use_case": "U1_DIGITAL_RHYTHM_WORKFLOW",
            "validated_commercial_role": rng.choice(ROLES),
            "validated_priority": rng.choice(["P1","P2","P3"]),
            "commercial_influence": rng.choice(["HIGH","MEDIUM","LOW"]),
            "evidence_confidence": rng.choice(["STRONG","SUFFICIENT","MINIMUM"]),
            "linkedin_activity_status": rng.choice(["ACTIVE","INACTIVE","UNKNOWN"]),
            "conflict_status": "UNRESOLVED" if review else "NONE",
            "validation_status": "VALIDATED_REVIEW" if review else "VALIDATED_PASS",
            "handoff_ready": 0 if review else 1,
            "missing_fact": "LinkedIn shows VP Clinical Systems; hospital directory lists a predecessor" if review else None,
            "why_it_matters": "Current title determines commercial role and P1 fit" if review else None,
            "best_verification_source": "Current hospital leadership page" if review else None,
            "next_verification_action": "Open the leadership page and confirm the current holder" if review else None,
            }, pk="person_id")
con.commit()

cands = sop4.load_candidates(con)
print(f"loaded {len(cands)} validated person records")
sel, ns, inel, summary = sop4.select(cands, target=150, cycle="CYCLE-TEST")
sop4.persist(con, sel, ns, inel, summary)

print(f"eligible={summary['golden_eligible_unique_people']} selected={summary['golden_selected_unique_people']}"
      f" not_selected={len(ns)} ineligible={len(inel)} shortage={summary['shortage_status']}")
assert summary["golden_selected_unique_people"] == 150

g = sheets.golden_records(con, cycle="CYCLE-TEST")
assert len(g) == 150 and g[0]["golden_rank"] == 1
missing = [k for k,_ in sheets.GOLDEN_COLUMNS if k not in g[0]]
assert not missing, f"golden tab missing columns: {missing}"
print("golden tab: 150 rows, all", len(sheets.GOLDEN_COLUMNS), "columns resolve")
print("  rank1:", g[0]["full_name"], "|", g[0]["validated_current_title"], "|",
      g[0]["account_name"], "| score", g[0]["golden_priority_score"])
print("  why  :", g[0]["golden_selection_reason"])

rows, cap, total = sheets.review_queue(con, share=0.30)
print(f"review queue: {total} in review, cap at 30% of PASS = {cap}, queued {len(rows)}")
assert len(rows) <= cap
assert all(r["review_value_score"] > 0 for r in rows)
assert rows[0]["review_value_score"] >= rows[-1]["review_value_score"]
print("  top item:", rows[0]["subject_type"], rows[0]["full_name"],
      "| value", rows[0]["review_value_score"], "|", rows[0]["next_verification_action"][:46])

# no REVIEW record leaked into the deliverable
review_ids = {r["subject_id"] for r in rows}
golden_pids = {r["person_id"] for r in g}
assert not (review_ids & golden_pids), "a REVIEW record reached the Golden sheet"
print("no REVIEW record reached the Golden tab (SOP 4 s01.1 holds)")

print("\ncontrol:")
for row in sheets.control_rows(con)[:11]:
    print(f"  {row['metric']:<34} {row['value']}")
print("\nend-to-end: PASS")
