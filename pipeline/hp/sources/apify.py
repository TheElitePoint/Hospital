"""Durable, cached Apify actor execution with key rotation and charge caps."""
from __future__ import annotations

import hashlib
import json
import re
import time

import requests

from .. import cache
from ..db import now
from ..keys import KeyPool, classify_error
from .http import session

API = "https://api.apify.com/v2"

# An actor run can ABORT/FAIL for a billing reason ("reached its maximum cost of
# $0.00", "reached the maximum usage for your current billing cycle") that never
# touches the submit/poll HTTP status codes classify_error() looks at. Caught here
# so a dead-budget token routes to the same key-rotation/NEEDS_KEY path as an HTTP
# 402, instead of being silently retried with the same exhausted key - which is
# what happened before "maximum usage"/"usage limit" were added: the key stayed
# ACTIVE, so every retry re-submitted a fresh run against the same dead account
# and immediately aborted again, burning cycles without rotating away from it.
BUDGET_PATTERNS = re.compile(r"(maximum (cost|usage)|usage limit|billing cycle|out of (credit|fund)|insufficient (fund|credit)|budget)", re.I)


def _request_key(actor_id, payload):
    blob = json.dumps([actor_id, payload], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def run_actor(con, pool: KeyPool, actor_id: str, payload: dict, *, max_charge_usd: float,
              timeout_seconds: int = 600, ttl_days: int = 30, run_timeout_secs: int = None):
    """Return actor dataset items. A completed request is cache-first and idempotent.

    run_timeout_secs overrides Apify's own server-side actor execution limit (the
    `timeout` run option) - separate from timeout_seconds, which only bounds how long
    THIS function polls. A slow actor (e.g. scraping many companies' employee lists)
    can be given more server-side time without us polling any differently, and our
    poll deadline is raised to match so we don't give up before Apify would."""
    if run_timeout_secs:
        timeout_seconds = max(timeout_seconds, run_timeout_secs + 60)
    request = {"actor": actor_id, "input": payload, "max_charge_usd": max_charge_usd,
               "run_timeout_secs": run_timeout_secs}
    hit = cache.get(con, "apify", request, ttl_days)
    if hit is not None:
        return hit
    request_key = _request_key(actor_id, payload)
    prior = con.execute("SELECT * FROM apify_runs WHERE request_key=?", (request_key,)).fetchone()
    if prior and prior["status"] == "UNCERTAIN" and not prior["run_id"]:
        raise RuntimeError("Prior Apify submission outcome is uncertain; inspect the Apify console before authorizing a retry")
    run_id = prior["run_id"] if prior else None
    dataset_id = prior["dataset_id"] if prior else None
    key_id = secret = None

    if not run_id:
        key_id, secret = pool.acquire()
        pool.mark_used(key_id)
        actor = actor_id.replace("/", "~")
        params = {"maxTotalChargeUsd": max_charge_usd}
        if run_timeout_secs:
            params["timeout"] = run_timeout_secs
        try:
            response = session().post(
                f"{API}/acts/{actor}/runs",
                params=params,
                headers={"Authorization": f"Bearer {secret}"},
                json=payload,
                timeout=60,
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            # ConnectionError (DNS failure / connection refused) never reached Apify's
            # servers at all. A Timeout on THIS call is the run-creation endpoint,
            # which only queues a run and acks in well under a second normally - one
            # empirically confirmed case (checked every Apify account's run history
            # for a match, found none) showed a 60s read-timeout here never produced a
            # run either. Both are treated as safe to retry rather than requiring a
            # human to manually clear a stuck apify_runs row every time the network
            # hiccups, which defeats unattended operation.
            raise RuntimeError(f"Apify submission failed before a run was created ({error}); safe to retry") from error
        except Exception as error:
            # Any other exception (e.g. a read timeout) may have left the request sent
            # but the response lost - genuinely unknown whether Apify started billing.
            # That case still requires a human to check the console before a retry.
            con.execute("INSERT OR REPLACE INTO apify_runs VALUES (?,?,?,?,?,?,?,?,?)",
                        (request_key, actor_id, None, None, "UNCERTAIN", max_charge_usd,
                         now(), now(), str(error)[:500]))
            con.commit()
            raise RuntimeError("Apify submission outcome is uncertain; inspect the Apify console before retrying") from error
        if not response.ok:
            kind = classify_error(response.status_code, response.text)
            pool.mark_failure(key_id, kind, f"{response.status_code}: {response.text[:300]}")
            if kind in {"EXHAUSTED", "INVALID", "RATE_LIMITED"}:
                return run_actor(con, pool, actor_id, payload, max_charge_usd=max_charge_usd,
                                 timeout_seconds=timeout_seconds, ttl_days=ttl_days)
            raise RuntimeError(f"Apify actor submission failed: HTTP {response.status_code}")
        data = response.json().get("data", {})
        run_id, dataset_id = data.get("id"), data.get("defaultDatasetId")
        con.execute("INSERT OR REPLACE INTO apify_runs VALUES (?,?,?,?,?,?,?,?,?)",
                    (request_key, actor_id, run_id, dataset_id, "SUBMITTED", max_charge_usd,
                     now(), now(), None))
        con.commit()

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not secret:
            key_id, secret = pool.acquire()
        response = session().get(f"{API}/actor-runs/{run_id}",
                                 headers={"Authorization": f"Bearer {secret}"}, timeout=45)
        if response.status_code == 403 and "insufficient-permissions" in response.text.lower():
            # A run started by one key cannot be polled by another - Apify itself has
            # no cross-account read access, so this is never a sign the CURRENT key is
            # bad. It only happens on a resumed poll of a cached apify_runs row whose
            # original key later became exhausted/rotated out (e.g. a subprocess killed
            # mid-run, leaving the row stuck at "RUNNING" forever). Blaming the polling
            # key here (as classify_error would) burns through the whole pool one key at
            # a time for a run nobody here can ever actually check again. Clear the
            # stale row and let the caller resubmit fresh instead.
            con.execute("DELETE FROM apify_runs WHERE request_key=?", (request_key,))
            con.commit()
            raise RuntimeError(f"Apify run {run_id} belongs to a different, no-longer-usable key "
                               "(stale cached run); cleared, safe to retry")
        if response.status_code in (401, 402, 429):
            kind = classify_error(response.status_code, response.text)
            pool.mark_failure(key_id, kind, f"poll {response.status_code}: {response.text[:250]}")
            key_id, secret = pool.acquire()
            continue
        if response.status_code == 403:
            kind = classify_error(response.status_code, response.text)
            pool.mark_failure(key_id, kind, f"poll {response.status_code}: {response.text[:250]}")
            key_id, secret = pool.acquire()
            continue
        response.raise_for_status()
        data = response.json().get("data", {})
        status = data.get("status", "RUNNING")
        dataset_id = data.get("defaultDatasetId") or dataset_id
        con.execute("UPDATE apify_runs SET status=?,dataset_id=?,updated_at=? WHERE request_key=?",
                    (status, dataset_id, now(), request_key))
        con.commit()
        if status == "SUCCEEDED":
            result = session().get(f"{API}/datasets/{dataset_id}/items",
                                   params={"format": "json", "clean": "true"},
                                   headers={"Authorization": f"Bearer {secret}"}, timeout=90)
            result.raise_for_status()
            items = result.json()
            cache.put(con, "apify", request, items, ttl_days)
            return items
        if status in {"FAILED", "ABORTED", "TIMED-OUT"}:
            error = (data.get("statusMessage") or status)[:500]
            # FAILED/ABORTED/TIMED-OUT are terminal, not "uncertain" - unlike a
            # submission that might still be running, there is nothing left to poll,
            # so the stale row is cleared unconditionally. Without this, a caller that
            # catches the RuntimeError below and retries the identical accounts later
            # would find this same request_key, reuse its dead run_id, and just
            # re-poll a run that will never produce a result, instead of submitting
            # a fresh one.
            con.execute("DELETE FROM apify_runs WHERE request_key=?", (request_key,))
            con.commit()
            if key_id and BUDGET_PATTERNS.search(error):
                pool.mark_failure(key_id, "EXHAUSTED", error)
                return run_actor(con, pool, actor_id, payload, max_charge_usd=max_charge_usd,
                                 timeout_seconds=timeout_seconds, ttl_days=ttl_days)
            raise RuntimeError(f"Apify actor {actor_id} {status}: {error}")
        time.sleep(4)
    raise RuntimeError(f"Apify actor {actor_id} is still running after {timeout_seconds}s; rerun to resume it")
