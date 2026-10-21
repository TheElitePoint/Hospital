import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp.sop4 import select, score, eligibility, select_sop2_only, sop2_only_eligibility

def rec(**kw):
    base = dict(canonical_person_id=kw.get("cid","P-1"), person_id=kw.get("cid","P-1"),
        account_id="US-IN-CCN150001", full_name="Test Person",
        linkedin_profile_url="https://linkedin.com/in/test",
        validation_status="VALIDATED_PASS", handoff_ready=1,
        employment_status="CURRENT_CONFIRMED", account_entity_match="DIRECT_ACCOUNT_MATCH",
        validated_current_title="Director", role_scope="FACILITY_LEVEL",
        primary_use_case="U1_DIGITAL_RHYTHM_WORKFLOW",
        validated_commercial_role="DIRECT_OWNER", validated_priority="P1",
        validated_role_family="TELEMETRY_CARDIAC_MONITORING",
        commercial_influence="HIGH", account_priority="A_PRIORITY",
        current_signal="PRESENT", evidence_confidence="STRONG",
        use_case_evidence_class="DIRECT_CURRENT",
        linkedin_activity_status="ACTIVE", conflict_status="NONE", duplicate_status="UNIQUE")
    base.update({k:v for k,v in kw.items() if k!="cid"})
    return base

# 1. SOP 4 s23.1 - direct owner INACTIVE must outrank weaker ACTIVE VP
a = rec(cid="P-owner", validated_commercial_role="DIRECT_OWNER", validated_priority="P1",
        linkedin_activity_status="INACTIVE", validated_role_family="TELEMETRY_CARDIAC_MONITORING")
b = rec(cid="P-vpit", validated_commercial_role="TECHNICAL_EVALUATOR", validated_priority="P2",
        linkedin_activity_status="ACTIVE", validated_role_family="IT_CIO", commercial_influence="MEDIUM")
sel, ns, inel, sm = select([a,b], target=2)
assert sel[0]["canonical_person_id"] == "P-owner", [r["canonical_person_id"] for r in sel]
print("1 s23.1 inactive direct owner    -> ranks above active VP IT",
      f"({a['scores']['golden_priority_score']} vs {b['scores']['golden_priority_score']})")

# 2. one human across four hospitals = ONE golden person (s00.4 / s23.3)
rows = [rec(cid="P-sysCIO", account_id=f"US-OH-CCN36{i:04d}", validated_role_family="IT_CIO",
            role_scope="SYSTEM_LEVEL", validated_commercial_role="TECHNICAL_EVALUATOR") for i in range(4)]
sel, ns, inel, sm = select(rows, target=10)
assert sm["golden_selected_unique_people"] == 1, sm
assert len(sel[0]["related_account_ids"]) == 4
print("2 system CIO under 4 hospitals   -> 1 unique person, 4 related accounts")

# 3. eligibility is hard - a high score never rescues a failed condition (s03.9)
probable = rec(cid="P-probable", employment_status="CURRENT_PROBABLE")
ok, why = eligibility(probable)
assert not ok and why == "EMPLOYMENT_NOT_CONFIRMED"
sel, ns, inel, sm = select([probable], target=10)
assert inel[0]["golden_ineligible_reason"] == "EMPLOYMENT_NOT_CONFIRMED"
assert sm["golden_selected_unique_people"] == 0
print("3 CURRENT_PROBABLE, perfect score-> INELIGIBLE (s07.3 enforced)")

# 4. shortage: standard does not move, diagnosis is emitted (s23.6)
pool = [rec(cid=f"P-{i}", account_id=f"US-TX-CCN45{i:04d}",
            validated_commercial_role="EXECUTIVE_SPONSOR", validated_priority="P3",
            validated_role_family="EXECUTIVE_SPONSOR") for i in range(930//100)]
sel, ns, inel, sm = select(pool, target=1000)
assert sm["shortage_status"] == "SHORTAGE"
assert sm["golden_selected_unique_people"] == len(pool)   # no padding with weaker people
assert "SHORTAGE_DIRECT_OWNERS" in sm["shortage_reasons"]
print("4 fewer than target eligible     -> no padding; reasons:", sm["shortage_reasons"][:3])

# 5. same-function concentration is flagged for human QA (G8 / s19)
crowd = [rec(cid=f"P-it{i}", validated_role_family="IT_CIO", role_scope="FACILITY_LEVEL",
             validated_commercial_role="TECHNICAL_EVALUATOR") for i in range(4)]
sel, ns, inel, sm = select(crowd, target=10)
flags = [f["flag"] for f in sm["balance_flags"]]
assert "SAME_FUNCTION_CONCENTRATION" in flags and "LOW_INCREMENTAL_VALUE_SELECTED" in flags
assert sm["human_qa_required"] and sm["qa_status"] == "PENDING_HUMAN_QA"
print("5 four IT people, one account    -> flagged:", sorted(set(flags)))

# 6. facility + system telemetry lead = legitimately distinct scope (s05.3)
two = [rec(cid="P-fac", role_scope="FACILITY_LEVEL"),
       rec(cid="P-sys", role_scope="SYSTEM_LEVEL", commercial_influence="MEDIUM")]
sel, ns, inel, sm = select(two, target=10)
vals = {r["canonical_person_id"]: r["incremental_value"] for r in sel}
assert vals["P-sys"] == "MEDIUM_INCREMENTAL_VALUE" or vals["P-fac"] == "MEDIUM_INCREMENTAL_VALUE"
print("6 facility + system telemetry    -> distinct scope kept as MEDIUM, not LOW")

# 7. determinism: identical input, identical order, twice
big = [rec(cid=f"P-{i}", account_id=f"US-KY-CCN18{i%40:04d}",
           validated_commercial_role=random.Random(i).choice(["DIRECT_OWNER","CO_OWNER","TECHNICAL_EVALUATOR","EXECUTIVE_SPONSOR"]),
           validated_priority=random.Random(i+1).choice(["P1","P2","P3"]),
           validated_role_family=random.Random(i+2).choice(["IT_CIO","NURSING_EXECUTIVE","TELEMETRY_CARDIAC_MONITORING","CLINICAL_ENGINEERING_HTM"]),
           linkedin_activity_status=random.Random(i+3).choice(["ACTIVE","INACTIVE","UNKNOWN"]),
           account_priority=random.Random(i+4).choice(["A_PRIORITY","B_PRIORITY","PASS_UNRANKED"]))
       for i in range(400)]
r1 = [r["canonical_person_id"] for r in select(list(big), target=150)[0]]
r2 = [r["canonical_person_id"] for r in select(list(reversed(big)), target=150)[0]]
assert r1 == r2, "ranking is not input-order independent"
print(f"7 400 people -> top 150          -> deterministic & order-independent")

# 8. SOP2-only tier: name+LinkedIn+company match is enough, tagged distinctly, and
# never displaces someone already selected via the real SOP3-validated tier
sop2_ok = dict(canonical_person_id="CP-unvalidated1", account_id="US-IN-CCN150001",
    full_name="Unvalidated Person", linkedin_profile_url="https://linkedin.com/in/unval1",
    person_status="PERSON_PASS", duplicate_status="UNIQUE",
    validated_role_family="NURSING_EXECUTIVE", validated_commercial_role="CLINICAL_EVALUATOR",
    validated_priority="P2", commercial_influence="MEDIUM", account_priority="A_PRIORITY",
    current_signal="PRESENT", use_case_evidence_class="DIRECT_CURRENT")
ok, reason = sop2_only_eligibility(sop2_ok)
assert ok, reason
missing_name = dict(sop2_ok, full_name="UNKNOWN")
ok, reason = sop2_only_eligibility(missing_name)
assert not ok and reason == "NAME_MISSING"
sel2, ns2, inel2, sm2 = select_sop2_only([sop2_ok], target=5, already_selected_canonical_ids=set())
assert len(sel2) == 1 and sel2[0]["qualification_tier"] == "SOP2_ONLY_UNVALIDATED"
assert sel2[0]["golden_status"] == "GOLDEN_SELECTED"
# already selected via the real tier -> excluded, not double-counted
sel3, ns3, inel3, sm3 = select_sop2_only([sop2_ok], target=5,
    already_selected_canonical_ids={"CP-unvalidated1"})
assert len(sel3) == 0
print("8 SOP2-only tier                 -> reduced bar works, tagged, never double-counts a validated person")
print("\nsop4: 8/8")
