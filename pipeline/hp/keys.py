"""Rotating API key pool.

Built for the stated operating reality: multiple Apify tokens that WILL exhaust,
with new ones added over time. Rules:
  - keys are drawn round-robin from ACTIVE keys with the fewest calls
  - a quota/credit error marks that key EXHAUSTED and immediately retries on the next key
  - an auth error marks the key INVALID (never retried, unlike exhausted)
  - a rate-limit error puts the key on a timed cooldown but keeps it ACTIVE
  - adding a key later is a single CLI call; nothing else changes
  - when every key for a provider is unusable, callers get NoKeysAvailable and the
    stage halts cleanly with work already committed, so a re-run resumes
"""
import datetime, hashlib, itertools, json, os, re
from .db import now, new_id

class NoKeysAvailable(RuntimeError):
    pass

# Classified from provider error text/status. Order matters: check auth before quota.
AUTH_PATTERNS = re.compile(r"(invalid|unauthorized|forbidden|authentication|bad token|no such token)", re.I)
# "insufficient" alone used to match Apify's "Insufficient permissions for the Actor
# run" - a transient, request-scoped 403 that has nothing to do with credit or quota
# (confirmed empirically: the same token succeeded on a plain retry moments later).
# That false match permanently marked a genuinely fresh, funded key EXHAUSTED off a
# single blip. Requiring "insufficient" to co-occur with fund/credit/quota/balance
# keeps the real "insufficient funds" case while letting a permissions hiccup fall
# through to RATE_PATTERNS below instead.
QUOTA_PATTERNS = re.compile(r"(quota|credit|usage limit|monthly limit|insufficient (fund|credit|quota|balance)|payment required|exceeded|max-total-charge-usd-must-be-greater-than-zero|must be greater than zero)", re.I)
RATE_PATTERNS = re.compile(r"(rate.?limit|too many requests|throttl|insufficient permissions)", re.I)

def classify_error(status: int, body: str) -> str:
    body = body or ""
    # Request/model/schema errors can contain the word "invalid" but do not say
    # anything about the credential. Never burn a whole key pool for one bad model ID.
    # Apify answers a zero-budget account with a 400 whose type is "...must-be-greater-than-zero".
    if status == 400 and re.search(r"max-total-charge-usd-must-be-greater-than-zero", body, re.I):
        return "EXHAUSTED"
    if status in (400, 404, 405, 413, 422) and not re.search(r"invalid (?:api )?key|invalid token|unauthorized", body, re.I):
        return "OTHER"
    # Rate-limit errors (e.g. Groq's "rate_limit_exceeded" type) legitimately contain
    # the word "exceeded", which QUOTA_PATTERNS also matches. Check rate-limit FIRST so
    # a recoverable per-minute throttle gets a cooldown instead of being permanently
    # marked EXHAUSTED - a real quota/credit error is never also a 429.
    if status == 429 or RATE_PATTERNS.search(body):
        return "RATE_LIMITED"
    if status in (401, 403) or AUTH_PATTERNS.search(body):
        if QUOTA_PATTERNS.search(body):
            return "EXHAUSTED"
        return "INVALID"
    if status == 402 or QUOTA_PATTERNS.search(body):
        return "EXHAUSTED"
    return "OTHER"

def _fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()[:16]

class KeyPool:
    def __init__(self, con, provider: str, cooldown_seconds: int = 90, exhausted_retry_days: int = 30):
        self.con = con
        self.provider = provider
        self.cooldown_seconds = cooldown_seconds
        # Most providers reset quota monthly (the dev Tavily keys in env-keys/.env are
        # literally "1,000 credits/month"). An EXHAUSTED key is never deleted and is
        # never dead forever - it becomes retryable again after this many days, same as
        # a manual `hp keys add` revive but automatic. A key that is really gone
        # (revoked/INVALID) is a different failure mode and is never auto-retried.
        self.exhausted_retry_days = exhausted_retry_days

    # ---- management ----
    def add(self, secret: str, label: str = None) -> str:
        key_id = f"{self.provider}-{_fingerprint(secret)}"
        existing = self.con.execute("SELECT key_id,state FROM api_keys WHERE key_id=?", (key_id,)).fetchone()
        if existing:
            # re-adding a key is how you revive one after topping up credit
            self.con.execute("UPDATE api_keys SET state='ACTIVE', exhausted_at=NULL, last_error=NULL,"
                             " cooldown_until=NULL WHERE key_id=?", (key_id,))
            self.con.commit()
            return key_id
        self.con.execute(
            "INSERT INTO api_keys (key_id,provider,secret,label,state,added_at) VALUES (?,?,?,?,'ACTIVE',?)",
            (key_id, self.provider, secret, label or "", now()))
        self.con.commit()
        return key_id

    def add_many(self, secrets, label_prefix="env"):
        return [self.add(s.strip(), f"{label_prefix}-{i+1}") for i, s in enumerate(secrets) if s.strip()]

    def status(self):
        return [dict(r) for r in self.con.execute(
            "SELECT key_id,label,state,calls,failures,last_used_at,exhausted_at,last_error"
            " FROM api_keys WHERE provider=? ORDER BY state,calls", (self.provider,))]

    # ---- acquisition ----
    def acquire(self):
        ts = now()
        retry_cutoff = (datetime.datetime.now(datetime.timezone.utc)
                        - datetime.timedelta(days=self.exhausted_retry_days)).isoformat(timespec="seconds")
        # ACTIVE-and-not-cooling-down keys are tried first (state='EXHAUSTED' sorts
        # after '' in the ORDER BY); an EXHAUSTED key past its retry window is only a
        # fallback, so a known-good key is always preferred while any exist.
        row = self.con.execute(
            "SELECT key_id,secret,state FROM api_keys WHERE provider=? AND ("
            "  (state='ACTIVE' AND (cooldown_until IS NULL OR cooldown_until <= ?))"
            "  OR (state='EXHAUSTED' AND exhausted_at IS NOT NULL AND exhausted_at <= ?)"
            ") ORDER BY state, calls ASC, last_used_at ASC LIMIT 1",
            (self.provider, ts, retry_cutoff)).fetchone()
        if not row:
            pending = self.con.execute(
                "SELECT COUNT(*) c FROM api_keys WHERE provider=? AND state='ACTIVE'"
                " AND cooldown_until > ?", (self.provider, ts)).fetchone()["c"]
            raise NoKeysAvailable(
                f"{self.provider}: no usable key "
                f"({pending} cooling down). Add one: `hp keys add {self.provider} <token>`")
        if row["state"] == "EXHAUSTED":
            # Give it a real shot before declaring it revived: acquire() only marks it
            # eligible again, mark_used/mark_failure/call() decide whether it stuck.
            self.con.execute("UPDATE api_keys SET state='ACTIVE' WHERE key_id=?", (row["key_id"],))
            self.con.commit()
        return row["key_id"], row["secret"]

    def mark_used(self, key_id: str):
        self.con.execute("UPDATE api_keys SET calls=calls+1, last_used_at=? WHERE key_id=?", (now(), key_id))
        self.con.commit()

    def mark_failure(self, key_id: str, kind: str, detail: str = ""):
        detail = (detail or "")[:500]
        if kind == "EXHAUSTED":
            self.con.execute("UPDATE api_keys SET state='EXHAUSTED', exhausted_at=?, last_error=?,"
                             " failures=failures+1 WHERE key_id=?", (now(), detail, key_id))
        elif kind == "INVALID":
            self.con.execute("UPDATE api_keys SET state='INVALID', last_error=?, failures=failures+1"
                             " WHERE key_id=?", (detail, key_id))
        elif kind == "RATE_LIMITED":
            until = (datetime.datetime.now(datetime.timezone.utc)
                     + datetime.timedelta(seconds=self.cooldown_seconds)).isoformat(timespec="seconds")
            self.con.execute("UPDATE api_keys SET cooldown_until=?, last_error=?, failures=failures+1"
                             " WHERE key_id=?", (until, detail, key_id))
        else:
            self.con.execute("UPDATE api_keys SET failures=failures+1, last_error=? WHERE key_id=?",
                             (detail, key_id))
        self.con.commit()

    def call(self, fn, max_key_switches: int = None):
        """Run fn(secret) -> (ok, status, body_or_result).

        Rotates to the next key on EXHAUSTED/INVALID/RATE_LIMITED and re-runs the same
        request, so a token dying mid-batch costs one retry, not a lost run.
        """
        tried = set()
        limit = max_key_switches or 10
        last_detail = ""
        for _ in range(limit):
            key_id, secret = self.acquire()
            if key_id in tried:
                # every remaining key already failed this request
                break
            tried.add(key_id)
            self.mark_used(key_id)
            ok, status, payload = fn(secret)
            if ok:
                # Clears a stale exhausted_at/last_error left over from a key that
                # acquire() just brought back out of its 30-day retry window.
                self.con.execute("UPDATE api_keys SET exhausted_at=NULL, last_error=NULL WHERE key_id=?", (key_id,))
                self.con.commit()
                return key_id, payload
            kind = classify_error(status, str(payload))
            last_detail = f"{status}: {str(payload)[:200]}"
            self.mark_failure(key_id, kind, last_detail)
            if kind == "OTHER":
                return key_id, None   # a genuine request error, not a key problem
        raise NoKeysAvailable(f"{self.provider}: all keys failed. Last error -> {last_detail}")

def load_from_env(con, provider: str, env_var: str):
    """Seed the pool from a comma/newline separated env var (matches your existing .env)."""
    raw = os.environ.get(env_var, "")
    parts = [p for p in re.split(r"[,\s]+", raw) if p]
    return KeyPool(con, provider).add_many(parts, label_prefix=env_var.lower())
