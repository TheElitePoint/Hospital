"""Find hospitals with inpatient-monitoring signals using Tavily, per state.

Searches for telemetry / central monitoring / tele-ICU / clinical-engineering activity, pulls
hospital names out of the results, and matches them against the hospitals already in the
database. Writes leads to run/tavily_leads.json:
  matched   - hospital already known; reports its current status and the evidence sentence
  unmatched - names not in the database (candidate new hospitals, state-tagged)
Dry by default; APPLY=1 promotes known-but-rejected/review hospitals that have a verbatim
core-signal sentence naming them (tagged RELAXED_TAVILY_LEAD) so the normal pipeline can search them.
Run from the pipeline directory.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hp import db, sop1_rules
from hp.keys import KeyPool
from hp.sources import tavily

APPLY = os.environ.get("APPLY") == "1"
STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
          "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia",
          "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
          "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
          "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
          "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
          "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
          "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
          "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
          "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
QUERIES = [
    '{S} hospital "telemetry unit" OR "central monitoring" OR "monitor technician" nurse',
    '{S} hospital "tele-ICU" OR "virtual nursing" OR "centralized monitoring" implementation',
    '{S} hospital "clinical engineering" OR "biomedical" "patient monitoring" OR "device integration"',
]
NAME_RE = re.compile(r"\b((?:[A-Z][A-Za-z0-9.&'’\-]+\s+){1,5}(?:Hospital|Medical Center|Medical Centre|Health System|Regional Medical Center|Healthcare))\b")
GENERIC = {"hospital", "medical", "center", "centre", "health", "healthcare", "regional", "community", "memorial", "general",
           "university", "system", "systems", "saint", "the", "and", "for", "inc", "llc", "campus", "clinic", "county",
           "district", "city", "state", "services", "care", "institute", "children", "childrens", "network", "group"}


def toks(name):
    return {w for w in re.findall(r"[a-z]{3,}", (name or "").lower().replace("'", "").replace("’", "")) if w not in GENERIC}


con = db.init("data/hospitals.db")
pool = KeyPool(con, "tavily")
accounts = {}
for r in con.execute("select account_id, canonical_account_name, state, stage_status, qualification_status, handoff_ready from accounts"):
    accounts.setdefault(r["state"], []).append((r["account_id"], r["canonical_account_name"], toks(r["canonical_account_name"]),
                                                r["stage_status"], r["handoff_ready"]))

matched, unmatched = {}, {}
for code, state in STATES.items():
    for q in QUERIES:
        try:
            res = tavily.search(con, pool, q.format(S=state), max_results=10)
        except Exception as e:
            print("search failed", code, str(e)[:80]); continue
        for item in res.get("results", []):
            text = f"{item.get('title', '')}. {item.get('content', '')}"
            for m in NAME_RE.finditer(text):
                name = m.group(1).strip()
                t = toks(name)
                if not t:
                    continue
                hit = next(((aid, n, st, ho) for aid, n, at, st, ho in accounts.get(code, []) if at and (t <= at or at <= t)), None)
                sent = sop1_rules._sentence(text, m.start(), m.end())
                core = any(re.search(p, sent, re.I) for _, p in sop1_rules.CORE)
                rec = {"name": name, "state": code, "url": item.get("url"), "evidence": sent[:300], "core": core}
                if hit:
                    key = hit[0]
                    cur = matched.setdefault(key, {"account_id": key, "db_name": hit[1], "stage": hit[2], "handoff": hit[3], "hits": []})
                    cur["hits"].append(rec)
                else:
                    unmatched.setdefault((code, " ".join(sorted(t))), rec)

known = list(matched.values())
by_stage = {}
for k in known:
    by_stage[k["stage"]] = by_stage.get(k["stage"], 0) + 1
rescue = [k for k in known if k["stage"] in ("REJECT", "REVIEW", "ERROR") and any(h["core"] for h in k["hits"])]
new = list(unmatched.values())
print("known hospitals mentioned:", len(known), by_stage)
print("rescue candidates (not PASS, verbatim core-signal sentence names them):", len(rescue))
print("unmatched names (candidate new hospitals):", len(new))
json.dump({"matched": known, "rescue": rescue, "unmatched": new}, open("run/tavily_leads.json", "w"), indent=1)

if APPLY and rescue:
    for k in rescue:
        con.execute("""UPDATE accounts SET qualification_status='PASS', stage_status='PASS', priority_class=COALESCE(NULLIF(priority_class,''),'B_PRIORITY'),
            review_reason_code='RELAXED_TAVILY_LEAD', reject_reason_code=NULL, missing_fact=NULL WHERE account_id=?""", (k["account_id"],))
    con.commit()
    print("promoted", len(rescue))
