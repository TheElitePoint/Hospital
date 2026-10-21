import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp.llm.validator import (validate_claims, assign_tier, excerpt_is_verbatim, tier_c_only)

PAGE = ("St Mary Regional Medical Center operates a 24-bed inpatient telemetry unit "
        "staffed by dedicated monitor technicians around the clock. "
        "Our clinical engineering department maintains all bedside monitoring devices.")
JOBS = "Now hiring: Monitor Technician, Telemetry. Full time nights."

def ev(eid, url, excerpt, date="2026-06-01", directness="DIRECT"):
    return {"evidence_id": eid, "source_url": url, "evidence_excerpt": excerpt,
            "source_date": date, "directness": directness}

idx = {
  "EV-1": ev("EV-1", "https://stmaryregional.org/services/telemetry",
             "inpatient telemetry unit staffed by dedicated monitor technicians"),
  "EV-2": ev("EV-2", "https://stmaryregional.org/careers/monitor-tech",
             "Now hiring: Monitor Technician, Telemetry"),
  "EV-3": ev("EV-3", "https://stmaryregional.org/services/telemetry",
             "the hospital plans to centralise all monitoring next year"),   # NOT on page
  "EV-4": ev("EV-4", "https://www.apollo.io/co/stmary", "inpatient telemetry unit", directness="INDIRECT"),
}
pages = {"https://stmaryregional.org/services/telemetry": PAGE,
         "https://stmaryregional.org/careers/monitor-tech": JOBS,
         "https://www.apollo.io/co/stmary": "inpatient telemetry unit"}

def run(claims):
    return validate_claims(claims, {k: dict(v) for k, v in idx.items()}, pages,
                           account_domain="stmaryregional.org")

# 1. clean core + independent supporting
r = run([
  {"claim_key":"core_signal.telemetry","claim_class":"CORE","claim_type":"FACT",
   "claim_value":"CS_TELEMETRY_CARDIAC_MONITORING","evidence_ids":["EV-1"]},
  {"claim_key":"supporting_signal.hiring","claim_class":"SUPPORTING","claim_type":"FACT",
   "claim_value":"SS_RELEVANT_HIRING","evidence_ids":["EV-2"]},
])
assert len(r.accepted) == 2, r.dropped
assert r.ok, r.dropped
print("1 clean core+supporting          -> PASS (2 accepted)")

# 2. hallucinated excerpt is dropped, not repaired
r = run([{"claim_key":"core_signal.central","claim_class":"CORE","claim_type":"FACT",
          "claim_value":"CS_CENTRAL_MONITORING","evidence_ids":["EV-3"]}])
assert not r.accepted and "not verbatim" in r.dropped[0][1]
assert r.missing_fact() and "needs more research" not in r.missing_fact()
print("2 invented excerpt               -> DROPPED:", r.dropped[0][1][:58])

# 3. supporting reusing the core's only evidence is refused (s03.6)
r = run([
  {"claim_key":"core_signal.telemetry","claim_class":"CORE","claim_type":"FACT",
   "claim_value":"CS_TELEMETRY_CARDIAC_MONITORING","evidence_ids":["EV-1"]},
  {"claim_key":"supporting_signal.docs","claim_class":"SUPPORTING","claim_type":"FACT",
   "claim_value":"SS_DOCUMENTATION_AUTOMATION","evidence_ids":["EV-1"]},
])
assert len(r.accepted) == 1 and "reuses the core" in r.dropped[0][1]
print("3 supporting reuses core evidence-> DROPPED (s03.6 enforced)")

# 4. uncited claim
r = run([{"claim_key":"core_signal.x","claim_class":"CORE","claim_type":"FACT",
          "claim_value":"CS_DEVICE_EHR_INTEGRATION","evidence_ids":[]}])
assert "no evidence cited" in r.dropped[0][1]
print("4 uncited claim                  -> DROPPED")

# 5. tier is derived, never self-reported; FACT on Tier C only is downgraded
r = run([{"claim_key":"core_signal.telemetry","claim_class":"CORE","claim_type":"FACT",
          "claim_value":"CS_TELEMETRY_CARDIAC_MONITORING","evidence_ids":["EV-4"]}])
assert r.accepted[0]["claim_type"] == "INFERENCE", r.accepted
assert tier_c_only(r) is True
print("5 apollo.io source               -> tier C, FACT downgraded to INFERENCE")

# 6. tier rules
assert assign_tier("https://stmaryregional.org/about", "stmaryregional.org") == "A1"
assert assign_tier("https://stmaryregional.org/careers/x", "stmaryregional.org") == "A2"
assert assign_tier("https://www.cms.gov/data", "stmaryregional.org") == "A1"
assert assign_tier("https://beckershospitalreview.com/x", "stmaryregional.org") == "B"
assert assign_tier("https://zoominfo.com/c/x", "stmaryregional.org") == "C"
print("6 tier assignment A1/A2/A1/B/C   -> PASS")
print("\nvalidator: 6/6")
