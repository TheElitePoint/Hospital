"""Tavily search - the SOP 1 s10 / SOP 2 s10 query libraries."""
from .. import cache
from ..keys import KeyPool
from .http import session

ENDPOINT = "https://api.tavily.com/search"

# SOP 1 s10. {ACCOUNT} is replaced with the exact verified account name.
CORE_MONITORING = ['"{ACCOUNT}" telemetry', '"{ACCOUNT}" "cardiac monitoring"',
                   '"{ACCOUNT}" "monitor technician"', '"{ACCOUNT}" "ECG monitoring"']
CENTRALIZED = ['"{ACCOUNT}" "central monitoring"', '"{ACCOUNT}" "centralized monitoring"',
               '"{ACCOUNT}" "command center" monitoring', '"{ACCOUNT}" "remote viewer"',
               '"{ACCOUNT}" "virtual nursing"']
TELE_ICU = ['"{ACCOUNT}" tele-ICU', '"{ACCOUNT}" "virtual critical care"',
            '"{ACCOUNT}" remote intensivist', '"{ACCOUNT}" "virtual ICU"']
DEVICE_EHR = ['"{ACCOUNT}" "medical device integration"', '"{ACCOUNT}" "device integration" EHR',
              '"{ACCOUNT}" physiologic data integration', '"{ACCOUNT}" interoperability monitors']
CLIN_ENG = ['"{ACCOUNT}" "clinical engineering"', '"{ACCOUNT}" HTM', '"{ACCOUNT}" "biomedical engineering"']
CHANGE = ['"{ACCOUNT}" acquisition', '"{ACCOUNT}" expansion', '"{ACCOUNT}" "new hospital"',
          '"{ACCOUNT}" modernization']
# s10.8 - mandatory for every likely PASS. Finding the problem already solved is a REJECT (R04).
NEGATIVE = ['"{ACCOUNT}" "enterprise monitoring platform"',
            '"{ACCOUNT}" "medical device integration platform"', '"{ACCOUNT}" Philips Capsule',
            '"{ACCOUNT}" Sickbay', '"{ACCOUNT}" Masimo monitoring', '"{ACCOUNT}" CARESCAPE',
            '"{ACCOUNT}" centralized monitoring implementation']

DISCOVERY_PACK = CORE_MONITORING + CENTRALIZED + TELE_ICU + DEVICE_EHR + CLIN_ENG + CHANGE

def search(con, pool: KeyPool, query: str, max_results=6, ttl_days=30):
    req = {"query": query, "max_results": max_results}
    hit = cache.get(con, "tavily", req, ttl_days)
    if hit is not None:
        return hit
    def call(secret):
        r = session().post(ENDPOINT, json={"api_key": secret, "query": query,
                                           "max_results": max_results,
                                           "search_depth": "basic"}, timeout=45)
        if r.ok:
            return True, r.status_code, r.json()
        return False, r.status_code, r.text
    key_id, payload = pool.call(call)
    if payload is None:
        return {"results": []}
    cache.put(con, "tavily", req, payload, ttl_days)
    return payload

def run_pack(con, pool, account_name, queries, max_results=6):
    out = []
    for q in queries:
        data = search(con, pool, q.replace("{ACCOUNT}", account_name), max_results)
        for r in data.get("results", []):
            out.append({"query": q, "url": r.get("url"), "title": r.get("title"),
                        "snippet": r.get("content", "")[:600],
                        "published": r.get("published_date")})
    seen, uniq = set(), []
    for r in out:
        if r["url"] and r["url"] not in seen:
            seen.add(r["url"]); uniq.append(r)
    return uniq
