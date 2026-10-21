"""Re-evaluate VALIDATED_REVIEW people against the current departure heuristic.

Reads only cached Tavily results (no paid calls). Dry run by default; APPLY=1 promotes.
Run from the pipeline directory: python recheck_review.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hp import cache, db
from hp.sop3 import INDIA, US_MARKERS, departure_signal

APPLY = os.environ.get("APPLY") == "1"
SINCE = os.environ.get("SINCE", "")
con = db.init("data/hospitals.db")
rows = con.execute("""
  SELECT v.person_id, v.conflict_status, p.full_name, p.location_if_available, a.canonical_account_name
  FROM validations v JOIN people p ON p.person_id=v.person_id
  LEFT JOIN accounts a ON a.account_id=v.account_id
  WHERE v.validation_status='VALIDATED_REVIEW' AND v.employment_status='CURRENT_CONFIRMED'
    AND v.validated_role_family IS NOT NULL AND v.validated_at >= ?""", (SINCE,)).fetchall()

promote, keep = [], []
for r in rows:
    loc = r["location_if_available"] or ""
    if INDIA.search(loc) or (loc and loc != "UNKNOWN" and not US_MARKERS.search(loc)):
        keep.append((r["person_id"], "non-US location"))
        continue
    if r["conflict_status"] == "POSSIBLE_CONTRADICTION":
        q = f'"{r["full_name"]}" "{r["canonical_account_name"]}" (former OR left OR joined OR appointed OR departure)'
        res = cache.get(con, "tavily", {"query": q, "max_results": 5}, 3650)
        if res is None:
            keep.append((r["person_id"], "no cached departure search"))
            continue
        hit = any(departure_signal(f"{x.get('title','')} {x.get('content','')}", r["full_name"], r["canonical_account_name"])
                  for x in res.get("results", []))
        if hit:
            keep.append((r["person_id"], "departure signal"))
            continue
    promote.append(r["person_id"])

print(f"review candidates: {len(rows)} | promote: {len(promote)} | keep: {len(keep)}")
for pid, why in keep:
    print("  keep", pid, why)
if APPLY and promote:
    con.executemany("""UPDATE validations SET validation_status='VALIDATED_PASS', conflict_status='NONE', qa_status='CLEAN',
        handoff_ready=1, evidence_confidence='STRONG', missing_fact=NULL,
        validated_at=datetime('now') WHERE person_id=?""", [(p,) for p in promote])
    con.commit()
    print("applied")
