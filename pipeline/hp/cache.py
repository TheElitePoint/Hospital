"""Content-addressed cache for every external call.

Reason this exists: prompts and gate logic WILL change after the calibration batch.
Cached fetches mean re-running a stage after a prompt change costs zero scraping credit.
"""
import hashlib, json, datetime
from .db import now

def key_for(provider: str, request: dict) -> str:
    blob = json.dumps({"p": provider, "r": request}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()

def get(con, provider: str, request: dict, ttl_days: int = 30):
    ck = key_for(provider, request)
    row = con.execute("SELECT payload, fetched_at FROM api_cache WHERE cache_key=?", (ck,)).fetchone()
    if not row:
        return None
    fetched = datetime.datetime.fromisoformat(row["fetched_at"])
    age = (datetime.datetime.now(datetime.timezone.utc) - fetched).days
    if age > ttl_days:
        return None
    return json.loads(row["payload"])

def put(con, provider: str, request: dict, payload, ttl_days: int = 30, http_status: int = 200):
    ck = key_for(provider, request)
    con.execute(
        "INSERT INTO api_cache (cache_key,provider,request,payload,fetched_at,ttl_days,http_status)"
        " VALUES (?,?,?,?,?,?,?) ON CONFLICT(cache_key) DO UPDATE SET"
        " payload=excluded.payload, fetched_at=excluded.fetched_at, http_status=excluded.http_status",
        (ck, provider, json.dumps(request, sort_keys=True, default=str), json.dumps(payload),
         now(), ttl_days, http_status))
    con.commit()
