"""SQLite system of record."""
import sqlite3, os, json, uuid, datetime, pathlib

DEFAULT_DB = os.environ.get("HP_DB", str(pathlib.Path(__file__).resolve().parents[1] / "data" / "hospitals.db"))

def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

def connect(path: str = None) -> sqlite3.Connection:
    path = path or DEFAULT_DB
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init(path: str = None) -> sqlite3.Connection:
    con = connect(path)
    sql = (pathlib.Path(__file__).parent / "schema.sql").read_text()
    con.executescript(sql)
    # Small forward-only migrations for workspaces created by earlier builds.
    columns = {r[1] for r in con.execute("PRAGMA table_info(pipeline_jobs)")}
    if "starting_golden" not in columns:
        con.execute("ALTER TABLE pipeline_jobs ADD COLUMN starting_golden INTEGER DEFAULT 0")
    if "mode" not in columns:
        # 'FULL' (default) = normal SOP1->SOP4 pipeline. 'PEOPLE_ONLY' skips SOP1
        # entirely and only works accounts that already passed it - see
        # orchestrator._worker_people_only.
        con.execute("ALTER TABLE pipeline_jobs ADD COLUMN mode TEXT DEFAULT 'FULL'")
    if "allow_sop2_only" not in columns:
        # User-approved, per-job relaxation: when the target can't be met from the
        # fully-validated (SOP3) pool, top up the shortfall from SOP2-only people
        # (name+LinkedIn+company match, no independent validation) - see
        # sop4.select_sop2_only(). Off by default; SOPs stay authoritative unless a
        # job explicitly opts in.
        con.execute("ALTER TABLE pipeline_jobs ADD COLUMN allow_sop2_only INTEGER DEFAULT 0")
    universe_columns = {r[1] for r in con.execute("PRAGMA table_info(universe)")}
    if "bed_count" not in universe_columns:
        con.execute("ALTER TABLE universe ADD COLUMN bed_count TEXT DEFAULT 'UNKNOWN'")
    people_columns = {r[1] for r in con.execute("PRAGMA table_info(people)")}
    for name in ("linkedin_canonical_key", "normalized_name", "normalized_title"):
        if name not in people_columns:
            con.execute(f"ALTER TABLE people ADD COLUMN {name} TEXT")
    accounts_columns = {r[1] for r in con.execute("PRAGMA table_info(accounts)")}
    if "sop2_attempted_at" not in accounts_columns:
        # Distinguishes "never ran SOP2 discovery" (NULL) from "ran it and it came up
        # short" (a timestamp, but fewer than SOP2_PEOPLE_TARGET people) - without this,
        # the discovery query can only see "has zero people" and either re-scrapes a
        # confirmed-empty account forever or ignores an under-filled one forever.
        con.execute("ALTER TABLE accounts ADD COLUMN sop2_attempted_at TEXT")
    golden_columns = {r[1] for r in con.execute("PRAGMA table_info(golden)")}
    if "qualification_tier" not in golden_columns:
        # 'SOP3_VALIDATED' (default) = full independent validation (employment,
        # role, disproof search). 'SOP2_ONLY_UNVALIDATED' = name+LinkedIn+company
        # match only, no independent confirmation - see sop4.select_sop2_only().
        con.execute("ALTER TABLE golden ADD COLUMN qualification_tier TEXT DEFAULT 'SOP3_VALIDATED'")
    # Index creation in schema happens before old databases receive new columns.
    con.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_people_li_canonical ON people(linkedin_canonical_key) WHERE linkedin_canonical_key IS NOT NULL AND linkedin_canonical_key <> ''")
    con.execute("CREATE INDEX IF NOT EXISTS ix_people_name_account ON people(account_id,normalized_name)")
    con.commit()
    return con

def upsert(con, table: str, row: dict, pk: str):
    cols = list(row.keys())
    placeholders = ",".join("?" for _ in cols)
    updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != pk)
    sql = (f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders}) "
           f"ON CONFLICT({pk}) DO UPDATE SET {updates}" if updates else
           f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({placeholders})")
    con.execute(sql, [json.dumps(v) if isinstance(v, (list, dict)) else v for v in row.values()])

def log_correction(con, subject_type, subject_id, field, old, new, change_type, reason,
                   evidence_ids=None, changed_by="pipeline"):
    """SOP 3 s08 - no field is ever silently overwritten."""
    if str(old) == str(new):
        return
    con.execute(
        "INSERT INTO correction_log (subject_type,subject_id,field_name,old_value,new_value,"
        "change_type,reason,evidence_ids,changed_at,changed_by) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (subject_type, subject_id, field, str(old), str(new), change_type, reason,
         json.dumps(evidence_ids or []), now(), changed_by))
