"""Resumable web-triggered pipeline orchestration with durable job state."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from . import db, sop2, sop4
from .excel_export import export as export_excel


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PIPELINE_ROOT.parent
_lock = threading.Lock()
_running = set()


def add_event(con, job_id, message, stage=None, level="INFO"):
    con.execute("INSERT INTO dashboard_events(job_id,level,stage,message,created_at) VALUES (?,?,?,?,?)",
                (job_id, level, stage, str(message)[:2000], db.now()))
    con.commit()


def metrics(con, target=None, starting=0):
    def count(sql):
        return con.execute(sql).fetchone()[0]
    result = {
        "accounts": count("SELECT COUNT(*) FROM accounts"),
        "accounts_pass": count("SELECT COUNT(*) FROM accounts WHERE qualification_status='PASS'"),
        "researched_people": count("SELECT COUNT(*) FROM people"),
        "validated_people": count("SELECT COUNT(*) FROM validations WHERE validation_status='VALIDATED_PASS'"),
        "review_people": count("SELECT COUNT(*) FROM validations WHERE validation_status='VALIDATED_REVIEW'"),
        "rejected_people": count("SELECT COUNT(*) FROM validations WHERE validation_status='VALIDATED_REJECT'"),
        "duplicate_people": count("SELECT COUNT(*) FROM people WHERE duplicate_status<>'UNIQUE'"),
        "duplicate_candidates": count("SELECT COUNT(*) FROM duplicate_candidates WHERE resolution_status='UNRESOLVED'"),
        "golden_people": count("SELECT COUNT(*) FROM golden WHERE golden_status='GOLDEN_SELECTED'"),
        "evidence": count("SELECT COUNT(*) FROM evidence"),
        "universe": count("SELECT COUNT(*) FROM universe"),
    }
    if target is not None:
        result["target"] = int(target)
        result["new_golden"] = max(0, result["golden_people"] - int(starting))
        result["remaining"] = max(0, int(target) - result["new_golden"])
        result["progress_pct"] = min(100.0, round(100 * result["new_golden"] / max(int(target), 1), 1))
    return result


def provider_status(con):
    rows = con.execute("SELECT provider,state,COUNT(*) count,SUM(calls) calls,SUM(failures) failures FROM api_keys GROUP BY provider,state ORDER BY provider,state").fetchall()
    output = {}
    for row in rows:
        output.setdefault(row["provider"], []).append({key: row[key] for key in ("state", "count", "calls", "failures")})
    return output


ALL_PROVIDERS = ("apify", "groq", "tavily")


def providers_needing_keys(status: dict) -> list:
    """Every provider the pipeline calls, checked proactively - not just the one a
    stage happens to crash into. A provider needs attention when it has zero
    ACTIVE-state keys. A cooling-down ACTIVE key still counts as fine (that's the
    transient rate-limit case _run_command already retries through on its own); only
    all-EXHAUSTED, all-INVALID, or never-seeded is a real "add a key" situation."""
    needy = []
    for provider in ALL_PROVIDERS:
        active = sum(row["count"] for row in status.get(provider, []) if row["state"] == "ACTIVE")
        if active == 0:
            needy.append(provider)
    return needy


def _active_env(con):
    env = os.environ.copy()
    mapping = {"apify": "APIFY_API_TOKENS", "groq": "GROQ_API_KEYS", "tavily": "TAVILY_API_KEYS"}
    for provider, variable in mapping.items():
        secrets = [row[0] for row in con.execute(
            "SELECT secret FROM api_keys WHERE provider=? AND state='ACTIVE' ORDER BY calls,last_used_at", (provider,)
        )]
        if secrets:
            env[variable] = ",".join(secrets)
    env["PYTHONPATH"] = str(PIPELINE_ROOT)
    # Piped (non-tty) stdout is fully block-buffered by default, so the per-account
    # status lines cmd_sop1 prints only reach the dashboard in one big burst when the
    # buffer fills or the subprocess exits - the run looks frozen for minutes even
    # while work is genuinely happening. Force line buffering so events stream live.
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _set_job(con, job_id, **fields):
    fields["updated_at"] = db.now()
    con.execute(f"UPDATE pipeline_jobs SET {','.join(k+'=?' for k in fields)} WHERE job_id=?",
                [*fields.values(), job_id])
    con.commit()


TRANSIENT_COOLDOWN_RE = re.compile(r"no usable key \((\d+) cooling down\)", re.I)
MAX_COOLDOWN_RETRIES = 6


def _run_command(con, job_id, stage, command, cwd, env=None, _cooldown_attempt=0):
    _set_job(con, job_id, current_stage=stage, command=" ".join(command))
    add_event(con, job_id, f"Started {stage}" + (f" (retry {_cooldown_attempt})" if _cooldown_attempt else ""), stage)
    process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1)
    output = []
    for raw in process.stdout:
        line = raw.rstrip()
        output.append(line)
        if line:
            add_event(con, job_id, line, stage)
    code = process.wait()
    text = "\n".join(output)
    if code or "halted:" in text.lower():
        cooldown = TRANSIENT_COOLDOWN_RE.search(text)
        if cooldown and int(cooldown.group(1)) > 0 and _cooldown_attempt < MAX_COOLDOWN_RETRIES:
            # "(N cooling down)" with N > 0 means every key is ACTIVE and just rate-limited
            # (KeyPool.mark_failure gives RATE_LIMITED a timed cooldown, never EXHAUSTED) -
            # this self-heals in under cooldown_seconds. Wait it out and retry the same
            # stage instead of pausing the whole run and paging the user for a key that
            # isn't actually needed. Only truly dead keys (0 cooling down) or repeated
            # cooldowns past MAX_COOLDOWN_RETRIES escalate to NeedsKey below.
            wait_s = min(100, 30 + 15 * _cooldown_attempt)
            add_event(con, job_id, f"{stage}: all keys are temporarily rate-limited "
                                    f"({cooldown.group(1)} cooling down, not exhausted); retrying in {wait_s}s",
                      stage, "WARNING")
            time.sleep(wait_s)
            return _run_command(con, job_id, stage, command, cwd, env, _cooldown_attempt + 1)
        provider = next((p for p in ("APIFY", "TAVILY", "GROQ") if
                         p.lower() in text.lower() and any(x in text.lower() for x in ("no usable key", "all keys failed", "needs_"))), None)
        if provider:
            raise NeedsKey(provider.lower())
        raise RuntimeError(f"{stage} exited with status {code}: {text[-1000:]}")
    add_event(con, job_id, f"Completed {stage}", stage)
    return text


class NeedsKey(RuntimeError):
    pass

def _sync_google_if_configured(con, job_id):
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not sheet_id or not credentials or not Path(credentials).exists():
        return None
    try:
        from .sheets import sync_operational
        result = sync_operational(con, sheet_id, credentials)
        add_event(con, job_id, "Google Sheet synced: " + json.dumps(result, sort_keys=True), "SHEETS")
        return result
    except Exception as error:
        add_event(con, job_id, f"Google Sheet sync deferred: {error}", "SHEETS", "WARNING")
        return None


VALID_MODES = ("FULL", "PEOPLE_ONLY")


def create_job(con, target, mode="FULL", allow_sop2_only=False):
    target = int(target)
    if target < 1 or target > 10000:
        raise ValueError("Target must be between 1 and 10,000")
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {VALID_MODES}")
    running = con.execute("SELECT job_id FROM pipeline_jobs WHERE status IN ('QUEUED','RUNNING') LIMIT 1").fetchone()
    if running:
        raise RuntimeError(f"Job {running['job_id']} is already running")
    job_id = db.new_id("RUN")
    starting = con.execute("SELECT COUNT(*) FROM golden WHERE golden_status='GOLDEN_SELECTED'").fetchone()[0]
    con.execute("INSERT INTO pipeline_jobs(job_id,target_golden,starting_golden,status,mode,allow_sop2_only,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (job_id, target, starting, "QUEUED", mode, int(bool(allow_sop2_only)), db.now(), db.now()))
    con.commit()
    return job_id


def launch(db_path, job_id):
    with _lock:
        if job_id in _running:
            return
        _running.add(job_id)
    con = db.init(db_path)
    try:
        row = con.execute("SELECT mode FROM pipeline_jobs WHERE job_id=?", (job_id,)).fetchone()
        mode = (row["mode"] if row else None) or "FULL"
    finally:
        con.close()
    target_fn = _worker_people_only if mode == "PEOPLE_ONLY" else _worker
    thread = threading.Thread(target=target_fn, args=(db_path, job_id), daemon=True, name=f"pipeline-{job_id}")
    thread.start()


def _worker(db_path, job_id):
    con = db.init(db_path)
    try:
        job = con.execute("SELECT * FROM pipeline_jobs WHERE job_id=?", (job_id,)).fetchone()
        if not job:
            return
        target_new = int(job["target_golden"])
        starting = int(job["starting_golden"] or 0)
        target_total = starting + target_new
        _set_job(con, job_id, status="RUNNING", required_provider=None, error=None,
                 started_at=job["started_at"] or db.now())
        # CMS is the no-cost universe and A0-A3 prefilter. It runs once, then its local
        # rows are reused by every later target run.
        if metrics(con)["universe"] == 0:
            _run_command(con, job_id, "CMS_UNIVERSE",
                         [sys.executable, "-m", "hp.cli", "--db", str(db_path), "universe"],
                         PIPELINE_ROOT, _active_env(con))

        round_number = 0
        previous = metrics(con)["golden_people"]
        while previous < target_total:
            round_number += 1
            # Clear downstream work first: this keeps most run time on people and lets a
            # newly qualified account flow to SOP 2/3 without a complete-account barrier.
            _run_command(con, job_id, "SOP2_PEOPLE",
                         [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop2", "--limit-accounts", "3", "--max-employees", "25"],
                         PIPELINE_ROOT, _active_env(con))
            _run_command(con, job_id, "SOP3_VALIDATION",
                         [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop3", "--limit", "100"],
                         PIPELINE_ROOT, _active_env(con))
            current = metrics(con)
            if current["golden_people"] < target_total:
                _run_command(con, job_id, "SOP1_ACCOUNTS",
                             [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop1",
                              "--limit", "40", "--workers", "5"],
                             PIPELINE_ROOT, _active_env(con))
                _run_command(con, job_id, "SOP1_A11",
                             [sys.executable, "-m", "hp.cli", "--db", str(db_path), "a11", "--limit", "40"],
                             PIPELINE_ROOT, _active_env(con))
                _run_command(con, job_id, "SOP2_PEOPLE",
                             [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop2", "--limit-accounts", "3", "--max-employees", "25"],
                             PIPELINE_ROOT, _active_env(con))
                _run_command(con, job_id, "SOP3_VALIDATION",
                             [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop3", "--limit", "100"],
                             PIPELINE_ROOT, _active_env(con))
            candidates = sop4.load_candidates(con)
            selected, not_selected, ineligible, summary = sop4.select(candidates, target=target_total)
            sop4.persist(con, selected, not_selected, ineligible, summary)
            workbook = export_excel(con)
            current = metrics(con)
            if current["golden_people"] > previous or round_number % 5 == 0:
                _sync_google_if_configured(con, job_id)
            add_event(con, job_id, f"Checkpoint: {max(0,current['golden_people']-starting)}/{target_new} new Golden; workbook refreshed", "CHECKPOINT")
            if current["golden_people"] >= target_total:
                break
            actionable = sum(con.execute(sql).fetchone()[0] for sql in (
                "SELECT COUNT(*) FROM accounts WHERE stage_status IN ('PENDING','ERROR')",
                "SELECT COUNT(*) FROM accounts WHERE qualification_status='PASS' AND handoff_ready=0",
                "SELECT COUNT(*) FROM accounts a WHERE a.qualification_status='PASS' AND a.handoff_ready=1"
                f" AND (SELECT COUNT(*) FROM people p WHERE p.account_id=a.account_id) < {sop2.SOP2_PEOPLE_TARGET}",
                "SELECT COUNT(*) FROM people p WHERE p.person_status='PERSON_PASS' AND NOT EXISTS (SELECT 1 FROM validations v WHERE v.person_id=p.person_id)",
            ))
            previous = current["golden_people"]
            if actionable == 0:
                add_event(con, job_id, "No remaining actionable records can raise the Golden count without resolving review evidence.", "SHORTAGE", "WARNING")
                break

        candidates = sop4.load_candidates(con)
        selected, not_selected, ineligible, summary = sop4.select(candidates, target=target_total)
        sop4.persist(con, selected, not_selected, ineligible, summary)
        workbook = export_excel(con)
        _sync_google_if_configured(con, job_id)
        current = metrics(con, target_new, starting)
        final_status = "COMPLETE" if current["new_golden"] >= target_new else "SHORTAGE"
        _set_job(con, job_id, status=final_status, current_stage="DONE", workbook_path=workbook["path"],
                 researched_people=current["researched_people"], validated_people=current["validated_people"],
                 golden_people=current["golden_people"], review_people=current["review_people"],
                 rejected_people=current["rejected_people"], duplicate_people=current["duplicate_people"],
                 finished_at=db.now())
        add_event(con, job_id, f"Workbook exported with {workbook['people']} People and {workbook['golden']} Golden rows", "EXPORT")
    except NeedsKey as error:
        provider = str(error)
        _set_job(con, job_id, status="NEEDS_KEY", required_provider=provider, current_stage="PAUSED")
        add_event(con, job_id, f"All usable {provider} keys are unavailable. Work is committed; add a key to resume.", "KEYS", "WARNING")
    except Exception as error:
        _set_job(con, job_id, status="FAILED", error=str(error)[:2000], finished_at=db.now())
        add_event(con, job_id, str(error), "ERROR", "ERROR")
    finally:
        con.close()
        with _lock:
            _running.discard(job_id)


SOP2_DEPTH_LADDER = (25, 60, 90, 120)  # employees scraped per company; ramps up only
                                       # once the shallower depth stops finding new people


def _people_only_counts(con):
    pending_a11 = con.execute(
        "SELECT COUNT(*) FROM accounts WHERE qualification_status='PASS' AND handoff_ready=0").fetchone()[0]
    eligible_sop2 = con.execute(
        "SELECT COUNT(*) FROM accounts a WHERE qualification_status='PASS' AND handoff_ready=1"
        f" AND (SELECT COUNT(*) FROM people p WHERE p.account_id=a.account_id) < {sop2.SOP2_PEOPLE_TARGET}"
    ).fetchone()[0]
    return pending_a11, eligible_sop2


def _run_golden_and_sync(con, job_id, db_path, target_total, note):
    """Runs SOP4 with a generous target so every person who clears the Golden minimum
    standard is selected - not capped at whatever the run's original target was - then
    exports and pushes the live Google Sheet, mirroring the FULL-mode checkpoint."""
    candidates = sop4.load_candidates(con)
    generous_target = max(target_total, len(candidates), 1000)
    selected, not_selected, ineligible, summary = sop4.select(candidates, target=generous_target)
    sop4.persist(con, selected, not_selected, ineligible, summary)

    allow_sop2_only = con.execute(
        "SELECT allow_sop2_only FROM pipeline_jobs WHERE job_id=?", (job_id,)).fetchone()
    if allow_sop2_only and allow_sop2_only[0]:
        sop3_selected_ids = {r["canonical_person_id"] for r in selected}
        sop3_selected_total = con.execute(
            "SELECT COUNT(*) FROM golden WHERE golden_status='GOLDEN_SELECTED'"
            " AND qualification_tier='SOP3_VALIDATED'").fetchone()[0]
        shortfall = target_total - sop3_selected_total
        if shortfall > 0:
            sop2_candidates = sop4.load_sop2_only_candidates(con, exclude_canonical_ids=sop3_selected_ids)
            sel2, ns2, inel2, summary2 = sop4.select_sop2_only(sop2_candidates, shortfall, sop3_selected_ids)
            sop4.persist(con, sel2, ns2, inel2, summary2)
            if sel2:
                add_event(con, job_id, f"SOP2-only top-up: +{len(sel2)} unvalidated"
                          " (name+LinkedIn+company match only)", "CHECKPOINT")

    workbook = export_excel(con)
    _sync_google_if_configured(con, job_id)
    current = metrics(con)
    add_event(con, job_id, f"Checkpoint ({note}): {current['researched_people']} people,"
                           f" {current['validated_people']} validated, {current['golden_people']} golden", "CHECKPOINT")
    return current, workbook


def _worker_people_only(db_path, job_id):
    """PEOPLE_ONLY mode: never runs SOP1 (no new hospitals discovered). Only works
    accounts that already passed SOP1, clearing the A11 backlog in small batches (the
    LinkedIn actors time out on anything much bigger - see apify.py/sop2.py), then
    ramping SOP2's per-company scrape depth only once the current depth stops finding
    new people, running SOP3 + a generous SOP4 selection + a Sheet sync after every
    batch so nothing sits undiscovered or unsynced."""
    con = db.init(db_path)
    try:
        job = con.execute("SELECT * FROM pipeline_jobs WHERE job_id=?", (job_id,)).fetchone()
        if not job:
            return
        target_new = int(job["target_golden"])
        starting = int(job["starting_golden"] or 0)
        target_total = starting + target_new
        _set_job(con, job_id, status="RUNNING", required_provider=None, error=None,
                 started_at=job["started_at"] or db.now())

        current = metrics(con)
        while current["golden_people"] < target_total:
            # --- Phase 1: clear the A11 backlog (cheap, unlocks accounts for SOP2) ---
            pending_a11, _ = _people_only_counts(con)
            while pending_a11 > 0:
                _run_command(con, job_id, "A11_PEOPLE_ONLY",
                             [sys.executable, "-m", "hp.cli", "--db", str(db_path), "a11", "--limit", "10"],
                             PIPELINE_ROOT, _active_env(con))
                new_pending, _ = _people_only_counts(con)
                if new_pending == pending_a11:
                    add_event(con, job_id, "A11 backlog made no progress this batch; moving to SOP2", "A11_PEOPLE_ONLY", "WARNING")
                    break
                pending_a11 = new_pending

            # --- Phase 2: discover people, ramping scrape depth as shallower depths dry up ---
            for depth in SOP2_DEPTH_LADDER:
                _, eligible = _people_only_counts(con)
                if eligible == 0:
                    continue
                stall = 0
                while current["golden_people"] < target_total:
                    _, eligible = _people_only_counts(con)
                    if eligible == 0:
                        break
                    before = metrics(con)["researched_people"]
                    _run_command(con, job_id, "SOP2_PEOPLE",
                                 [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop2",
                                  "--limit-accounts", "3", "--max-employees", str(depth)],
                                 PIPELINE_ROOT, _active_env(con))
                    # Small batches: a 90+ person profile-scrape in one Apify run keeps
                    # cycling through timeout-and-resubmit (same lesson as SOP 2's
                    # employee scraper). 25 completes reliably; loop covers the backlog.
                    sop3_pending_sql = ("SELECT COUNT(*) FROM people p WHERE p.person_status='PERSON_PASS'"
                                        " AND NOT EXISTS (SELECT 1 FROM validations v WHERE v.person_id=p.person_id)")
                    sop3_attempts = 0
                    # SOP3's disproof search needs Tavily. When the job has opted into the
                    # SOP2-only tier and Tavily has no usable key, skip validation this
                    # pass instead of pausing the whole run on a provider that only one
                    # optional stage needs; unvalidated people are still picked up (and
                    # tagged) by the SOP2-only top-up, and SOP3 resumes once Tavily is back.
                    tavily_active = con.execute(
                        "SELECT COUNT(*) FROM api_keys WHERE provider='tavily' AND state='ACTIVE'").fetchone()[0]
                    sop2_only_on = con.execute(
                        "SELECT allow_sop2_only FROM pipeline_jobs WHERE job_id=?", (job_id,)).fetchone()[0]
                    if sop2_only_on and tavily_active == 0:
                        add_event(con, job_id, "Tavily has no usable key; skipping SOP3 this pass"
                                  " (SOP2-only tier still applies)", "SOP3_VALIDATION", "WARNING")
                        sop3_attempts = 8
                    while con.execute(sop3_pending_sql).fetchone()[0] > 0 and sop3_attempts < 8:
                        before_pending = con.execute(sop3_pending_sql).fetchone()[0]
                        _run_command(con, job_id, "SOP3_VALIDATION",
                                     [sys.executable, "-m", "hp.cli", "--db", str(db_path), "sop3", "--limit", "25"],
                                     PIPELINE_ROOT, _active_env(con))
                        sop3_attempts += 1
                        if con.execute(sop3_pending_sql).fetchone()[0] == before_pending:
                            add_event(con, job_id, "SOP3 batch made no progress; will retry next depth pass", "SOP3_VALIDATION", "WARNING")
                            break
                    current, _ = _run_golden_and_sync(con, job_id, db_path, target_total, f"people-only depth={depth}")
                    if current["researched_people"] == before:
                        stall += 1
                        if stall >= 3:
                            add_event(con, job_id, f"3 stalled SOP2 batches at depth={depth}; trying deeper", "SOP2_PEOPLE", "WARNING")
                            break
                    else:
                        stall = 0
                if current["golden_people"] >= target_total:
                    break

            pending_a11, eligible = _people_only_counts(con)
            if current["golden_people"] >= target_total:
                break
            if pending_a11 == 0 and eligible == 0:
                add_event(con, job_id, "No accounts left to unlock or discover people from at any scrape depth."
                                       " Run FULL mode to find more qualified hospitals.", "SHORTAGE", "WARNING")
                break

        current, workbook = _run_golden_and_sync(con, job_id, db_path, target_total, "final")
        final_status = "COMPLETE" if (current["golden_people"] - starting) >= target_new else "SHORTAGE"
        _set_job(con, job_id, status=final_status, current_stage="DONE", workbook_path=workbook["path"],
                 researched_people=current["researched_people"], validated_people=current["validated_people"],
                 golden_people=current["golden_people"], review_people=current["review_people"],
                 rejected_people=current["rejected_people"], duplicate_people=current["duplicate_people"],
                 finished_at=db.now())
        add_event(con, job_id, f"Workbook exported with {workbook['people']} People and {workbook['golden']} Golden rows", "EXPORT")
    except NeedsKey as error:
        provider = str(error)
        _set_job(con, job_id, status="NEEDS_KEY", required_provider=provider, current_stage="PAUSED")
        add_event(con, job_id, f"All usable {provider} keys are unavailable. Work is committed; add a key to resume.", "KEYS", "WARNING")
    except Exception as error:
        _set_job(con, job_id, status="FAILED", error=str(error)[:2000], finished_at=db.now())
        add_event(con, job_id, str(error), "ERROR", "ERROR")
    finally:
        con.close()
        with _lock:
            _running.discard(job_id)
