import sys, pathlib, tempfile, os, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp import db
from hp.keys import KeyPool, NoKeysAvailable, classify_error

con = db.init(tempfile.mktemp(suffix=".db"))
pool = KeyPool(con, "apify")
pool.add_many(["apify_tok_AAA", "apify_tok_BBB", "apify_tok_CCC"], "seed")
assert len(pool.status()) == 3
print("1 seeded 3 apify tokens          ->", [k["key_id"][-6:] for k in pool.status()])

# error classification
assert classify_error(402, "Monthly usage limit exceeded") == "EXHAUSTED"
assert classify_error(401, "Invalid token") == "INVALID"
assert classify_error(429, "Too Many Requests") == "RATE_LIMITED"
assert classify_error(403, "insufficient credit on account") == "EXHAUSTED"
assert classify_error(500, "upstream boom") == "OTHER"
print("2 error classification           -> EXHAUSTED/INVALID/RATE_LIMITED/EXHAUSTED/OTHER")

# token A is out of credit, token B is revoked -> the call must still succeed on C
dead = {"apify_tok_AAA": (402, "Monthly usage limit exceeded"),
        "apify_tok_BBB": (401, "Invalid token")}
attempts = []
def scrape(secret):
    attempts.append(secret)
    if secret in dead:
        s, b = dead[secret]
        return False, s, b
    return True, 200, {"items": ["hospital-linkedin-page"]}

key_id, payload = pool.call(scrape)
assert payload == {"items": ["hospital-linkedin-page"]}, payload
assert len(attempts) == 3, attempts
states = {k["key_id"][-6:]: k["state"] for k in pool.status()}
print("3 two tokens die mid-request     -> recovered on 3rd, states:", states)
assert sorted(states.values()) == ["ACTIVE", "EXHAUSTED", "INVALID"]

# when everything is dead the stage halts cleanly with an actionable message
def always_dead(secret):
    return False, 402, "credit exhausted"
try:
    pool.call(always_dead)
    raise SystemExit("should have raised")
except NoKeysAvailable as e:
    assert "hp keys add" in str(e) or "all keys failed" in str(e)
    print("4 all tokens exhausted           -> NoKeysAvailable, run halts cleanly")

# topping up: re-adding the same secret revives it, no duplicate row
pool.add("apify_tok_AAA", "topped-up")
assert len(pool.status()) == 3
assert [k for k in pool.status() if k["key_id"].endswith(pool.add("apify_tok_AAA")[-16:])][0]["state"] == "ACTIVE"
print("5 re-add topped-up token         -> revived ACTIVE, still 3 rows (no dupes)")

# a brand new token added later is picked up with no code change
pool.add("apify_tok_DDD", "bought-later")
ok_key, payload = pool.call(scrape)
print("6 new token added later          -> used immediately:", ok_key[-6:])

# a 429 whose body happens to say "exceeded" (e.g. Groq's rate_limit_exceeded) must
# still cool down, not get permanently EXHAUSTED - real quota errors are never a 429
assert classify_error(429, '{"error":{"type":"rate_limit_exceeded","message":"Rate limit reached"}}') == "RATE_LIMITED"
print("7 429 body containing 'exceeded' -> RATE_LIMITED, not EXHAUSTED")

# EXHAUSTED keys are never deleted and are retried automatically once their monthly
# quota window has plausibly reset - never immediately, only after exhausted_retry_days
gpool = KeyPool(con, "groq", exhausted_retry_days=30)
gpool.add("gsk_monthly", "seed")
try:
    gpool.call(lambda secret: (False, 402, "credit exhausted"))
    raise SystemExit("should have raised")
except NoKeysAvailable:
    pass
assert gpool.status()[0]["state"] == "EXHAUSTED"
con.execute("UPDATE api_keys SET exhausted_at=? WHERE provider='groq'",
           ((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=31)).isoformat(timespec="seconds"),))
con.commit()
key_id, payload = gpool.call(lambda secret: (True, 200, {"ok": True}))
state = gpool.status()[0]
assert state["state"] == "ACTIVE" and state["exhausted_at"] is None, state
print("8 EXHAUSTED key past 30 days     -> auto-revived, kept as backup not deleted")

# Apify's "Insufficient permissions for the Actor run" is a transient, request-scoped
# 403 that has nothing to do with credit/quota (empirically: the same token succeeds
# on a plain retry). It must not be classified the same as "insufficient funds" -
# that false match previously marked a genuinely fresh, funded key EXHAUSTED off one
# blip, forcing the user to supply a brand new key every time it happened.
assert classify_error(403, 'Insufficient permissions for the Actor run. Make sure you are passing a correct API token') == "RATE_LIMITED"
assert classify_error(402, "insufficient funds on account") == "EXHAUSTED"
assert classify_error(403, "insufficient credit on account") == "EXHAUSTED"
print("9 'insufficient permissions' 403 -> RATE_LIMITED (transient), not EXHAUSTED like real insufficient funds/credit")

print("\nkey pool: 9/9")
