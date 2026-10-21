"""Local production control plane for the hospital research pipeline."""
from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db
from .keys import KeyPool
from .orchestrator import create_job, launch, metrics, provider_status, providers_needing_keys


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = PIPELINE_ROOT / "web"
DB_PATH = os.environ.get("HP_DB", str(PIPELINE_ROOT / "data" / "hospitals.db"))
ENV_FILE = PIPELINE_ROOT.parent / "env-keys" / ".env"
ENV_VAR_BY_PROVIDER = {"apify": "APIFY_TOKENS", "groq": "GROQ_API_KEYS", "tavily": "TAVILY_API_KEYS"}


def _persist_env_keys(provider: str, new_keys: list[str]) -> bool:
    """Append newly added keys into env-keys/.env so a future `hp cli init` reseeds
    them too. The SQLite pool (already updated by the caller) is what the *running*
    pipeline uses - this is only so a rebuilt database doesn't lose keys added here."""
    var = ENV_VAR_BY_PROVIDER[provider]
    if not ENV_FILE.exists():
        return False
    lines = ENV_FILE.read_text().splitlines(keepends=True)
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{var}="):
            found = True
            newline = "\n" if line.endswith("\n") else ""
            current = line[:-1] if newline else line
            existing = [k.strip() for k in current.split("=", 1)[1].split(",") if k.strip()]
            for k in new_keys:
                if k not in existing:
                    existing.append(k)
            lines[i] = f"{var}={','.join(existing)}{newline}"
            break
    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(f"{var}={','.join(new_keys)}\n")
    tmp = ENV_FILE.with_suffix(".env.tmp")
    tmp.write_text("".join(lines))
    tmp.replace(ENV_FILE)
    return True

app = FastAPI(title="Hospital Research Pipeline", version="1.0.0", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=STATIC_ROOT), name="assets")

@app.on_event("startup")
def resume_interrupted_job():
    """A laptop/app restart resumes committed jobs and any journaled Apify run."""
    con = _con()
    try:
        row = con.execute("SELECT job_id FROM pipeline_jobs WHERE status IN ('QUEUED','RUNNING') ORDER BY created_at DESC LIMIT 1").fetchone()
        if row:
            con.execute("UPDATE pipeline_jobs SET status='QUEUED',updated_at=? WHERE job_id=?", (db.now(), row["job_id"]))
            con.commit()
            launch(DB_PATH, row["job_id"])
    finally:
        con.close()


class StartRequest(BaseModel):
    target: int = Field(ge=1, le=10000)
    mode: str = Field(default="FULL")


class KeyRequest(BaseModel):
    provider: str
    keys: str = Field(min_length=8, max_length=8000)  # one or more, comma/whitespace-separated
    label: str = Field(default="dashboard", max_length=80)
    job_id: str | None = None


def _con():
    return db.init(DB_PATH)


def _job(row):
    return dict(row) if row else None


@app.get("/")
def index():
    return FileResponse(STATIC_ROOT / "index.html")


@app.get("/api/status")
def status():
    con = _con()
    try:
        latest = con.execute("SELECT * FROM pipeline_jobs ORDER BY created_at DESC LIMIT 1").fetchone()
        target = latest["target_golden"] if latest else 300
        events = []
        if latest:
            events = [dict(row) for row in con.execute(
                "SELECT id,level,stage,message,created_at FROM dashboard_events WHERE job_id=? ORDER BY id DESC LIMIT 120",
                (latest["job_id"],),
            ).fetchall()][::-1]
        providers = provider_status(con)
        return {"job": _job(latest), "metrics": metrics(con, target, latest["starting_golden"] if latest else 0),
                "providers": providers, "providers_needing_keys": providers_needing_keys(providers), "events": events}
    finally:
        con.close()


@app.post("/api/jobs", status_code=202)
def start(request: StartRequest):
    con = _con()
    try:
        try:
            job_id = create_job(con, request.target, request.mode)
        except (ValueError, RuntimeError) as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
    finally:
        con.close()
    launch(DB_PATH, job_id)
    return {"job_id": job_id, "status": "QUEUED"}


@app.post("/api/keys")
def add_key(request: KeyRequest):
    provider = request.provider.strip().lower()
    if provider not in {"apify", "tavily", "groq"}:
        raise HTTPException(status_code=422, detail="Provider must be apify, tavily or groq")
    prefixes = {"apify": "apify_api_", "tavily": "tvly-", "groq": "gsk_"}
    raw_keys = [k.strip() for k in re.split(r"[\s,]+", request.keys) if k.strip()]
    if not raw_keys:
        raise HTTPException(status_code=422, detail="Paste at least one key")
    bad = [k for k in raw_keys if not k.startswith(prefixes[provider])]
    if bad:
        raise HTTPException(status_code=422,
                             detail=f"{len(bad)} of {len(raw_keys)} key(s) do not match the expected {provider} prefix")
    con = _con()
    try:
        key_ids = [KeyPool(con, provider).add(k, request.label) for k in raw_keys]
        persisted = False
        try:
            persisted = _persist_env_keys(provider, raw_keys)
        except OSError:
            pass  # the SQLite pool (already updated above) is what the live run actually uses
        resumed = False
        if request.job_id:
            job = con.execute("SELECT * FROM pipeline_jobs WHERE job_id=?", (request.job_id,)).fetchone()
            if job and job["status"] == "NEEDS_KEY" and job["required_provider"] == provider:
                con.execute("UPDATE pipeline_jobs SET status='QUEUED',required_provider=NULL,error=NULL,updated_at=? WHERE job_id=?",
                            (db.now(), request.job_id))
                con.execute("INSERT INTO dashboard_events(job_id,level,stage,message,created_at) VALUES (?,?,?,?,?)",
                            (request.job_id, "INFO", "KEYS",
                             f"Added {len(raw_keys)} replacement {provider} key(s) ({', '.join(key_ids)}); resuming", db.now()))
                con.commit()
                resumed = True
    finally:
        con.close()
    if resumed:
        launch(DB_PATH, request.job_id)
    return {"key_ids": key_ids, "provider": provider, "count": len(raw_keys),
            "resumed": resumed, "persisted_to_env": persisted}


@app.get("/api/export")
def download_export():
    con = _con()
    try:
        latest = con.execute("SELECT workbook_path FROM pipeline_jobs WHERE workbook_path IS NOT NULL ORDER BY created_at DESC LIMIT 1").fetchone()
    finally:
        con.close()
    path = Path(latest["workbook_path"]) if latest else PIPELINE_ROOT.parent / "outputs" / "pipeline-dashboard" / "Hospital_People_Golden.xlsx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No workbook has been exported yet")
    return FileResponse(path, filename=path.name, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/api/health")
def health():
    return {"status": "ok", "database": Path(DB_PATH).exists()}
