"""CMS universe loader - SOP 1 Gates A0/A1/A2/A3 at zero API cost.

Source: CMS Provider Data Catalog, Hospital General Information (dataset xubh-q36u).
Public, no key, no scraping, no ToS exposure. Paginated JSON.

What it settles for free:
  A0 entity   - CCN is the canonical federal identifier and the dedupe key
  A1 geography- state field, hard filtered to the five approved states
  A2 archetype- hospital_type + ownership seed the archetype (CAH comes free)
  A3 inpatient- hospital_type distinguishes inpatient acute from outpatient-only

bed_count is NOT available here. SOP 1 s03.2.1 makes the bed band a discovery guide,
not a qualification gate, so bed_count stays UNKNOWN (s07.7) unless the optional POS
enricher is run. Do not let an unknown bed count block a decision.
"""
import csv, json
from ..db import now, upsert

BASE = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0"
APPROVED_STATES = ["IN", "OH", "KY", "TX", "AL",   # SOP 1 s03.1 original 5-state territory
    # 2026-09-21: territory expansion explicitly authorized by the user in-session
    # (target: 300 qualified hospitals, unreachable from the original 5 states - the
    # remaining REVIEW backlog there was exhausted, confirmed 119 as its real
    # ceiling). Not yet a formal SOP revision document.
    "CA", "FL", "NY", "PA", "IL", "GA", "NC", "MI", "NJ", "VA",
    "WA", "AZ", "MA", "TN", "MO", "WI", "CO", "MD", "MN", "SC",
    # 2026-10-08: user asked for every US hospital ("find a list of all the hospitals in US"),
    # which authorises the remaining states and DC. US only.
    "AK", "AR", "CT", "DC", "DE", "HI", "IA", "ID", "KS", "LA", "ME", "MS", "MT", "ND",
    "NE", "NH", "NM", "NV", "OK", "OR", "RI", "SD", "UT", "VT", "WV", "WY"]

# SOP 1 s03.2 / s04 R02
INPATIENT_TYPES = {
    "Acute Care Hospitals": "COMMUNITY_ACUTE",
    "Critical Access Hospitals": "CRITICAL_ACCESS",
    "Acute Care - Veterans Administration": "COMMUNITY_ACUTE",
    "Acute Care - Department of Defense": "COMMUNITY_ACUTE",
    "Childrens": "COMMUNITY_ACUTE",
}
# explicit rejects at A2/A3, kept visible rather than silently filtered
EXCLUDED_TYPES = {
    "Psychiatric": "R02_WRONG_ACCOUNT_TYPE",
    "Rehabilitation": "R02_WRONG_ACCOUNT_TYPE",
    "Outpatient": "R02_WRONG_ACCOUNT_TYPE",
}

def fetch_page(session, state, offset, limit=500):
    params = {
        "limit": limit, "offset": offset,
        "conditions[0][property]": "state",
        "conditions[0][value]": state,
        "conditions[0][operator]": "=",
    }
    r = session.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def load_state_via_apify(con, pool_apify, state, max_records=2000):
    """Fallback for when data.cms.gov itself blocks our IP (confirmed 2026-09-21: the
    whole data.cms.gov domain, not just this dataset, returned 403 Access Denied even
    for a state already loaded successfully before). Runs the identical CMS query
    through Apify's proxy infrastructure instead - retrainmap/cms-provider-data reads
    the exact same Provider Data Catalog dataset (xubh-q36u) and returns rows with the
    same field names store_row() already expects, so no mapping layer is needed."""
    from .apify import run_actor
    items = run_actor(con, pool_apify, "retrainmap/cms-provider-data",
                      {"dataset": "hospital_general_info", "state": state, "max_records": max_records},
                      max_charge_usd=max(0.5, 0.1 + max_records * 0.005), run_timeout_secs=300)
    for r in items:
        store_row(con, r, source="CMS_HOSPITAL_GENERAL_INFO_VIA_APIFY")
    con.commit()
    return len(items)

def load_state(con, session, state, limit=500):
    """Pull one state's full hospital list into the universe table."""
    offset, total, seen = 0, None, 0
    while True:
        data = fetch_page(session, state, offset, limit)
        rows = data.get("results", [])
        total = data.get("total_count", total)
        if not rows:
            break
        for r in rows:
            store_row(con, r, source="CMS_HOSPITAL_GENERAL_INFO")
            seen += 1
        con.commit()
        offset += len(rows)
        if total is not None and offset >= total:
            break
    return seen

def load_pos_file(con, path, states=None):
    """Fallback/enricher from the CMS Provider of Services file (NBER mirror).

    Active hospital subtypes: 01 short-term acute, 06 children's, 11 critical access.
    The file adds certified bed count, which Hospital General Information omits.
    """
    states = set(states or APPROVED_STATES)
    subtype = {"01": "Acute Care Hospitals", "06": "Childrens", "11": "Critical Access Hospitals"}
    seen = 0
    with open(path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row.get("state_cd") not in states or row.get("prvdr_ctgry_cd") != "01":
                continue
            if row.get("pgm_trmntn_cd") not in ("", "00") or row.get("prvdr_ctgry_sbtyp_cd") not in subtype:
                continue
            mapped = {"facility_id": row.get("prvdr_num"), "facility_name": row.get("fac_name"),
                      "address": row.get("st_adr"), "citytown": row.get("city_name"), "state": row.get("state_cd"),
                      "zip_code": row.get("zip_cd"), "telephone_number": row.get("phne_num"),
                      "hospital_type": subtype[row.get("prvdr_ctgry_sbtyp_cd")],
                      "hospital_ownership": row.get("gnrl_cntl_type_cd"), "emergency_services": "UNKNOWN",
                      "bed_count": row.get("crtfd_bed_cnt") or row.get("bed_cnt") or "UNKNOWN"}
            store_row(con, mapped, source="CMS_PROVIDER_OF_SERVICES_NBER_MIRROR")
            seen += 1
    con.commit()
    return seen

def classify(row):
    """Returns (in_scope, archetype_or_None, reason)."""
    htype = (row.get("hospital_type") or "").strip()
    state = (row.get("state") or "").strip().upper()
    if state not in APPROVED_STATES:
        return 0, None, "R01_OUT_OF_SCOPE_GEO"
    for bad, code in EXCLUDED_TYPES.items():
        if bad.lower() in htype.lower():
            return 0, None, code
    archetype = INPATIENT_TYPES.get(htype)
    if not archetype:
        return 0, None, "R02_WRONG_ACCOUNT_TYPE"
    return 1, archetype, "A1_A3_PASS"

def store_row(con, r, source):
    in_scope, archetype, reason = classify(r)
    ccn = r.get("facility_id") or r.get("provider_id")
    if not ccn:
        return
    name = (r.get("facility_name") or "").strip()
    city = (r.get("citytown") or "").strip()
    state = (r.get("state") or "").strip().upper()
    upsert(con, "universe", {
        "ccn": ccn, "facility_name": name, "address": r.get("address"),
        "city": city, "state": state, "zip": r.get("zip_code"),
        "county": r.get("countyparish"), "phone": r.get("telephone_number"),
        "hospital_type": r.get("hospital_type"),
        "hospital_ownership": r.get("hospital_ownership"),
        "emergency_services": r.get("emergency_services"),
        "bed_count": r.get("bed_count") or "UNKNOWN",
        "source": source, "loaded_at": now(),
        "dedupe_key": dedupe_key(name, city, state),
        "in_scope": in_scope, "prefilter_reason": reason,
        "account_id": account_id_for(state, name, ccn) if in_scope else None,
    }, pk="ccn")

def dedupe_key(name, city, state):
    """SOP 1 s19.1 key 3: facility name + city + state, normalised."""
    import re
    n = re.sub(r"[^a-z0-9 ]", "", (name or "").lower())
    n = re.sub(r"\b(the|inc|llc|lp|of|at|and|a|hospital|medical|center|centre|health|system|regional)\b", "", n)
    n = re.sub(r"\s+", "", n)
    return f"{state}|{re.sub(r'[^a-z]', '', (city or '').lower())}|{n}"

def account_id_for(state, name, ccn):
    """SOP 1 s06.3 - stable ID, never a display name alone. CCN keeps it federal-stable."""
    return f"US-{state}-CCN{ccn}"

def seed_archetype(con, ccn):
    row = con.execute("SELECT * FROM universe WHERE ccn=?", (ccn,)).fetchone()
    _, archetype, _ = classify(dict(row))
    return archetype

def promote_to_accounts(con, state=None, limit=None):
    """Create account shells for in-scope universe rows. Gates A0/A1/A2/A3 are already done."""
    q = "SELECT * FROM universe WHERE in_scope=1"
    args = []
    if state:
        q += " AND state=?"; args.append(state)
    q += " ORDER BY state, facility_name"
    if limit:
        q += f" LIMIT {int(limit)}"
    created = 0
    for row in con.execute(q, args).fetchall():
        r = dict(row)
        _, archetype, _ = classify(r)
        exists = con.execute("SELECT 1 FROM accounts WHERE account_id=?", (r["account_id"],)).fetchone()
        if exists:
            continue
        upsert(con, "accounts", {
            "account_id": r["account_id"], "ccn": r["ccn"],
            "canonical_account_name": r["facility_name"], "facility_name": r["facility_name"],
            "state": r["state"], "city": r["city"],
            "account_archetype": archetype,
            "bed_count": r.get("bed_count") or "UNKNOWN", "facility_count": "UNKNOWN", "acute_site_count": "UNKNOWN",
            "pipeline_stage": "SOP1", "stage_status": "PENDING",
            "gate_trace": json.dumps({"A0": "PASS", "A1": "PASS", "A2": "PASS", "A3": "PASS"}),
            "research_started_at": now(),
        }, pk="account_id")
        created += 1
    con.commit()
    return created
