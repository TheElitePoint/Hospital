"""Groq client. High-volume extraction (SOP 1/2); a stronger model is used for the
SOP 3 adversarial pass and the SOP 2 better-person test - see config.yaml."""
import json, re
from .. import cache
from ..keys import KeyPool
from ..sources.http import session
from ..db import now, new_id

ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def complete(con, pool: KeyPool, model, system, user, temperature=0.0,
             json_mode=True, ttl_days=14, prompt_version="v1"):
    req = {"model": model, "system": system, "user": user, "t": temperature, "pv": prompt_version}
    hit = cache.get(con, "groq", req, ttl_days)
    if hit is not None:
        return hit
    body = {"model": model, "temperature": temperature,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    def call(secret):
        r = session().post(ENDPOINT, json=body,
                           headers={"Authorization": f"Bearer {secret}"}, timeout=120)
        if r.ok:
            return True, r.status_code, r.json()
        return False, r.status_code, r.text
    key_id, payload = pool.call(call)
    if payload is None:
        return None
    cache.put(con, "groq", req, payload, ttl_days)
    return payload

def parse_json(payload):
    """Models occasionally wrap JSON in prose even in json mode. Parse defensively,
    but never 'repair' content - a malformed response is a failed run, not a guess."""
    if not payload:
        return None
    try:
        content = payload["choices"][0]["message"]["content"]
    except Exception:
        return None
    try:
        return json.loads(content)
    except Exception:
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
