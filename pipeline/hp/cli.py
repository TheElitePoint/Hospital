#!/usr/bin/env python3
"""hp - hospital decision-maker pipeline CLI. Every stage is resumable and idempotent."""
import argparse, json, os, sys, pathlib, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from hp import db, sop4, sheets
from hp.keys import KeyPool, NoKeysAvailable, load_from_env

def _con(args):
    return db.init(args.db)

def cmd_init(args):
    con = _con(args)
    print(f"database ready: {args.db or db.DEFAULT_DB}")
    for p, env in (("apify","APIFY_TOKENS"), ("groq","GROQ_API_KEYS"), ("tavily","TAVILY_API_KEYS")):
        added = load_from_env(con, p, env)
        if added:
            print(f"  seeded {len(added)} {p} key(s) from {env}")

def cmd_keys(args):
    con = _con(args)
    pool = KeyPool(con, args.provider)
    if args.action == "add":
        print("added:", pool.add(args.token, args.label))
    elif args.action == "list":
        for k in pool.status():
            print(f"  {k['state']:<10} {k['key_id']:<28} calls={k['calls']:<6} fails={k['failures']}"
                  f" {k['last_error'] or ''}"[:140])
    elif args.action == "revive":
        print("revived:", pool.add(args.token, "revived"))

def cmd_universe(args):
    con = _con(args)
    from hp.sources import cms
    from hp.sources.http import session
    s = session()
    total = 0
    states = args.states or cms.APPROVED_STATES
    via_apify = False
    for st in states:
        try:
            if via_apify:
                raise RuntimeError("already switched to Apify fallback for this run")
            n = cms.load_state(con, s, st)
            print(f"  {st}: {n} facilities")
            total += n
        except Exception as error:
            if not via_apify:
                print(f"  data.cms.gov direct API unavailable ({error}); falling back to Apify proxy for remaining states")
                via_apify = True
            try:
                n = cms.load_state_via_apify(con, KeyPool(con, "apify"), st)
                print(f"  {st}: {n} facilities (via Apify)")
                total += n
            except Exception as apify_error:
                pos = pathlib.Path(args.pos_file or pathlib.Path(__file__).resolve().parents[1] / "data" / "posotherdec2024.csv")
                if not pos.exists():
                    raise RuntimeError(f"CMS API and Apify fallback both unavailable ({apify_error}); "
                                       f"download the Provider of Services CSV to {pos}") from apify_error
                n = cms.load_pos_file(con, pos, [st])
                print(f"  {st}: {n} facilities (via Provider of Services CSV)")
                total += n
    created = cms.promote_to_accounts(con, state=None, limit=args.limit)
    ins = con.execute("SELECT COUNT(*) c FROM universe WHERE in_scope=1").fetchone()["c"]
    print(f"loaded {total}; in scope {ins}; account shells created {created}")

def cmd_sop1(args):
    con = _con(args)
    from hp import sop1
    # REVIEW is a genuine SOP1 verdict (an evidence gap), not a queue state, so it's
    # excluded by default - re-running it would just burn Tavily/Groq re-confirming
    # the same gap for most reasons. --retry-review-reason opts a specific reason code
    # back in, for the case where the original failure was actually an infra outage
    # (e.g. A11_LINKEDIN_COMPANY_NOT_RESOLVED while every Apify key was exhausted)
    # rather than missing evidence.
    where = "stage_status IN ('PENDING','ERROR')"
    params = []
    if args.retry_review_reason:
        where += " OR (stage_status='REVIEW' AND review_reason_code=?)"
        params.append(args.retry_review_reason)
    if args.state:
        where = f"({where}) AND state=?"
        params.append(args.state)
    # Never-tried (PENDING) hospitals go before ERROR ones: an account that errors
    # (malformed model output, a page that never loads) re-enters this query every
    # round, and sorting purely by id lets a cluster of persistent failures hold the
    # front of every limited batch while fresh hospitals wait behind them.
    q = (f"SELECT * FROM accounts WHERE {where} ORDER BY (stage_status='ERROR'), account_id"
         + (f" LIMIT {int(args.limit)}" if args.limit else ""))
    rows = [dict(r) for r in con.execute(q, params).fetchall()]
    con.close()
    workers = max(1, int(args.workers))
    print(f"SOP 1 over {len(rows)} accounts ({workers} workers)")

    # Each account is ~6 Tavily searches + page fetches + 1 Groq call - all network
    # I/O, done serially per account. Fanning accounts out across threads (each with
    # its own SQLite connection; the schema runs in WAL mode so concurrent writers
    # don't block readers) is what actually raises throughput - a bigger --limit alone
    # just queues more accounts to run one at a time.
    tally = {}
    print_lock = threading.Lock()
    halted = threading.Event()
    halt_detail = []

    def worker(row):
        if halted.is_set():
            return row, "SKIPPED"
        wcon = db.connect(args.db)
        try:
            pt, pg = KeyPool(wcon, "tavily"), KeyPool(wcon, "groq")
            return row, sop1.run_account(wcon, row, pt, pg, args.model)
        except NoKeysAvailable as e:
            halted.set()
            halt_detail.append(str(e))
            return row, "HALTED"
        except Exception as e:
            # One account's bad response (malformed model JSON, a transient parse bug)
            # must not take the other 39 down with it. Mark it ERROR so the next sop1
            # run retries just this account, and keep the batch moving.
            try:
                db.upsert(wcon, "accounts", {"account_id": row["account_id"], "stage_status": "ERROR"},
                          pk="account_id")
                wcon.commit()
            except Exception:
                pass
            with print_lock:
                print(f"  ERROR on {row.get('canonical_account_name','?')}: {e}")
            return row, "ERROR"
        finally:
            wcon.close()

    completed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(worker, row) for row in rows]
        for future in as_completed(futures):
            row, status = future.result()
            completed += 1
            with print_lock:
                tally[status] = tally.get(status, 0) + 1
                print(f"  [{completed}/{len(rows)}] {row['canonical_account_name'][:46]:<46} {status}")
    if halted.is_set():
        print(f"\nhalted: {halt_detail[0]}\nwork so far is committed; re-run to resume.")
    print("tally:", tally)

def _safe_apify_batch(label, fn):
    """An Apify actor infra hiccup (TIMED-OUT, a transient ABORTED that isn't a budget
    problem, etc.) is not a key issue and not this batch's fault - log it and let the
    next round retry the same accounts instead of crashing the whole orchestrator job
    to FAILED. A real key exhaustion still raises NoKeysAvailable, which is left to
    propagate so the orchestrator's existing key-popup path handles it correctly."""
    try:
        print(json.dumps(fn(), indent=2))
    except NoKeysAvailable:
        raise
    except Exception as e:
        # Deliberately NOT the word "halted:" - the orchestrator's _run_command greps
        # for that literal substring to detect cmd_sop1's no-more-keys case (which also
        # exits 0) and escalate to NEEDS_KEY. This is a different, self-healing case:
        # print it, exit 0, and let the next round's fresh query retry these same
        # (still-unattempted) records instead of pausing for a human.
        print(f"recoverable batch error, will retry next round: {label}: {e}")


def cmd_a11(args):
    con = _con(args)
    from hp import sop1
    # handoff_ready=0 is already the authoritative "A11 hasn't succeeded yet" signal;
    # the old linkedin_sector_status IS NULL check assumed a never-attempted account
    # always has an empty sector_status, but re-qualifying an account that previously
    # failed A11 (e.g. ENTITY_MISMATCH from a since-fixed key outage) leaves its stale
    # sector_status in place while flipping qualification_status back to PASS - the
    # extra filter then silently hid every one of those retryable accounts from A11.
    q = "SELECT * FROM accounts WHERE qualification_status='PASS' AND handoff_ready=0 ORDER BY account_id"
    if args.limit: q += f" LIMIT {int(args.limit)}"
    rows = [dict(r) for r in con.execute(q).fetchall()]
    print(f"SOP 1 A11 over {len(rows)} accounts")
    if args.via == "tavily":
        _safe_apify_batch("SOP 1 A11 (tavily)", lambda: sop1.run_a11_batch_tavily(con, rows, KeyPool(con, "tavily")))
    else:
        _safe_apify_batch("SOP 1 A11", lambda: sop1.run_a11_batch(con, rows, KeyPool(con, "apify")))

def cmd_sop2(args):
    con = _con(args)
    from hp import sop2
    # Never-attempted accounts (sop2_attempted_at IS NULL) go first - a run that gets
    # interrupted partway should spread across the widest possible set of companies
    # before it ever spends a second Apify call topping up one that already has people.
    # Only once an account has been tried at least once does its person_count (capped
    # at SOP2_PEOPLE_TARGET) become the reason to skip or revisit it.
    # handoff_ready has been written as both the integer 1 and the text 'TRUE' by
    # different code paths over time; comparing with = alone silently drops any
    # 'TRUE' rows (SQLite does not coerce that to 1), permanently hiding them from
    # SOP2 no matter how many rounds run. Accept both forms here.
    q = f"""SELECT a.*, (SELECT COUNT(*) FROM people p WHERE p.account_id=a.account_id) AS person_count
           FROM accounts a WHERE a.qualification_status='PASS' AND a.handoff_ready IN (1,'TRUE')
           AND (SELECT COUNT(*) FROM people p WHERE p.account_id=a.account_id) < {sop2.SOP2_PEOPLE_TARGET}
           ORDER BY (a.sop2_attempted_at IS NULL) DESC, a.sop2_attempted_at ASC, a.account_id"""
    if args.limit_accounts: q += f" LIMIT {int(args.limit_accounts)}"
    rows = [dict(r) for r in con.execute(q).fetchall()]
    never_tried = sum(1 for r in rows if r["sop2_attempted_at"] is None)
    print(f"SOP 2 over {len(rows)} accounts ({never_tried} never attempted, "
          f"{len(rows)-never_tried} topping up under {sop2.SOP2_PEOPLE_TARGET})")
    _safe_apify_batch("SOP 2", lambda: sop2.discover_batch(con, rows, KeyPool(con, "apify"), args.max_employees))

def cmd_sop3(args):
    con = _con(args)
    from hp import sop3
    q = """SELECT p.* FROM people p WHERE p.person_status='PERSON_PASS'
           AND NOT EXISTS (SELECT 1 FROM validations v WHERE v.person_id=p.person_id) ORDER BY p.person_id"""
    if args.limit: q += f" LIMIT {int(args.limit)}"
    rows = [dict(r) for r in con.execute(q).fetchall()]
    print(f"SOP 3 over {len(rows)} people")
    _safe_apify_batch("SOP 3", lambda: sop3.validate_batch(con, rows, KeyPool(con, "apify"), KeyPool(con, "tavily")))
    from hp.dedupe import audit
    print("dedupe:", json.dumps(audit(con), sort_keys=True))

def cmd_activity(args):
    con = _con(args)
    from hp import sop3
    q = """SELECT v.person_id, p.linkedin_profile_url FROM validations v
           JOIN people p ON p.person_id=v.person_id
           WHERE v.validation_status='VALIDATED_PASS'"""
    if not args.recheck:
        q += " AND (v.activity_run_status='NOT_RUN' OR v.activity_run_status LIKE 'ERROR%')"
    if args.since:
        q += f" AND v.validated_at >= '{args.since}'"
    q += " ORDER BY v.person_id"
    if args.limit: q += f" LIMIT {int(args.limit)}"
    rows = [dict(r) for r in con.execute(q).fetchall()]
    print(f"Activity check over {len(rows)} people")
    tally = sop3.check_activity_batch(con, rows, KeyPool(con, "apify"))
    print(json.dumps(tally, indent=2))

def cmd_dedupe(args):
    from hp.dedupe import audit
    con = _con(args)
    print(json.dumps(audit(con), indent=2))

def cmd_golden(args):
    con = _con(args)
    cands = sop4.load_candidates(con)
    sel, ns, inel, summary = sop4.select(cands, target=args.target, cycle=args.cycle)
    sop4.persist(con, sel, ns, inel, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "golden_person_ids"}, indent=2))
    if summary["shortage_status"] == "SHORTAGE":
        print(f"\nSHORTAGE: {len(sel)}/{args.target} met the Golden minimum standard.")
        print("The standard does not move (SOP 4 s06 G10). Replenish upstream for:")
        for r in summary["shortage_reasons"]:
            print("  -", r)
        if args.allow_sop2_only:
            remaining = args.target - len(sel)
            selected_ids = {r["canonical_person_id"] for r in sel}
            sop2_cands = sop4.load_sop2_only_candidates(con, exclude_canonical_ids=selected_ids)
            sel2, ns2, inel2, summary2 = sop4.select_sop2_only(sop2_cands, remaining, selected_ids, cycle=args.cycle)
            sop4.persist(con, sel2, ns2, inel2, summary2)
            print(f"\nSOP2-only top-up: +{len(sel2)} unvalidated (name+LinkedIn+company match only), "
                  f"tagged qualification_tier=SOP2_ONLY_UNVALIDATED, {len(sel) + len(sel2)}/{args.target} total")

def cmd_sync(args):
    con = _con(args)
    sheet = sheets.open_sheet(args.sheet_id, args.credentials)
    g = sheets.golden_records(con, cycle=args.cycle)
    n = sheets.write_tab(sheet, "07_Golden", g, sheets.GOLDEN_COLUMNS)
    print(f"  07_Golden          {n} rows")
    rq, cap, total = sheets.review_queue(con, share=args.review_share)
    n = sheets.write_tab(sheet, "08_Review_Queue", rq, sheets.REVIEW_COLUMNS)
    print(f"  08_Review_Queue    {n} rows (cap {cap} = {int(args.review_share*100)}% of PASS, {total} in review)")
    accounts = [dict(r) for r in con.execute("""
        SELECT a.*, (SELECT COUNT(*) FROM evidence e WHERE e.subject_id=a.account_id) evidence_count,
               (SELECT GROUP_CONCAT(signal_code) FROM account_signals s
                 WHERE s.account_id=a.account_id AND s.signal_class='CORE') core_signals,
               (SELECT GROUP_CONCAT(signal_code) FROM account_signals s
                 WHERE s.account_id=a.account_id AND s.signal_class='SUPPORTING') supporting_signals,
               h.qa_decision,h.qa_reviewer_id,h.qa_notes,h.manual_override_status,h.override_reason
        FROM accounts a LEFT JOIN human_input h
          ON h.subject_type='ACCOUNT' AND h.subject_id=a.account_id
        ORDER BY a.qualification_status, a.priority_class""").fetchall()]
    n = sheets.write_tab(sheet, "02_Accounts", accounts, sheets.ACCOUNT_COLUMNS)
    print(f"  02_Accounts        {n} rows")
    ctrl = sheets.control_rows(con)
    n = sheets.write_tab(sheet, "00_Control", ctrl, [("metric","Metric"),("value","Value")])
    print(f"  00_Control         {n} rows")

def cmd_sync_operational(args):
    con = _con(args)
    print(json.dumps(sheets.sync_operational(con, args.sheet_id, args.credentials), indent=2))

def cmd_pull(args):
    con = _con(args)
    sheet = sheets.open_sheet(args.sheet_id, args.credentials)
    for tab, subject, idcol in (("07_Golden","GOLDEN","Person ID"),
                                ("08_Review_Queue","REVIEW","ID"),
                                ("02_Accounts","ACCOUNT","Account ID")):
        try:
            applied, refused = sheets.sync_human_input(con, sheet, tab, subject, idcol)
            print(f"  {tab}: {applied} human edits applied"
                  + (f", {len(refused)} REFUSED (override with no reason)" if refused else ""))
        except Exception as e:
            print(f"  {tab}: skipped ({e})")

def cmd_status(args):
    con = _con(args)
    for row in sheets.control_rows(con):
        print(f"  {row['metric']:<34} {row['value']}")

def cmd_import_current(args):
    from hp.bridge import import_current
    con = _con(args)
    print(json.dumps(import_current(con, args.input), indent=2))

def cmd_import_sheet(args):
    from hp.bridge import import_google_sheet
    con = _con(args)
    print(json.dumps(import_google_sheet(con, args.sheet_id, args.credentials), indent=2))

def cmd_export_excel(args):
    from hp.excel_export import export
    con = _con(args)
    print(json.dumps(export(con, args.output), indent=2))

def cmd_web(args):
    import uvicorn
    # Local-only binding protects the key-entry control plane from the LAN.
    uvicorn.run("hp.web:app", host=args.host, port=args.port, reload=False, access_log=True)

def main():
    p = argparse.ArgumentParser(prog="hp", description="Hospital decision-maker research pipeline")
    p.add_argument("--db", default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(fn=cmd_init)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    imp = sub.add_parser("import-current")
    imp.add_argument("--input", default=str(pathlib.Path(__file__).resolve().parents[2] / "data" / "input.json"))
    imp.set_defaults(fn=cmd_import_current)
    imps = sub.add_parser("import-sheet"); imps.add_argument("--sheet-id", required=True)
    imps.add_argument("--credentials", default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")); imps.set_defaults(fn=cmd_import_sheet)
    exp = sub.add_parser("export-excel")
    exp.add_argument("--output", default=None)
    exp.set_defaults(fn=cmd_export_excel)
    web = sub.add_parser("web")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    web.set_defaults(fn=cmd_web)

    k = sub.add_parser("keys"); k.add_argument("action", choices=["add","list","revive"])
    k.add_argument("provider", choices=["apify","groq","tavily"])
    k.add_argument("token", nargs="?"); k.add_argument("--label", default="")
    k.set_defaults(fn=cmd_keys)

    u = sub.add_parser("universe"); u.add_argument("--states", nargs="*"); u.add_argument("--pos-file")
    u.add_argument("--limit", type=int); u.set_defaults(fn=cmd_universe)

    s1 = sub.add_parser("sop1"); s1.add_argument("--state"); s1.add_argument("--limit", type=int)
    s1.add_argument("--model", default=os.environ.get("HP_EXTRACT_MODEL","openai/gpt-oss-120b"))
    s1.add_argument("--workers", type=int, default=int(os.environ.get("HP_SOP1_WORKERS", 8)))
    s1.add_argument("--retry-review-reason",
                     help="Also re-attempt REVIEW accounts with this review_reason_code (e.g. a prior key "
                          "outage caused a resolvable gate to fail, not a genuine evidence gap)")
    s1.set_defaults(fn=cmd_sop1)

    a11 = sub.add_parser("a11"); a11.add_argument("--limit", type=int, default=10)
    a11.add_argument("--via", choices=["apify", "tavily"], default="apify",
                      help="tavily: fall back to Tavily search when Apify's LinkedIn-company "
                           "actor is externally blocked (Google-search based, shares no infra with Tavily)")
    a11.set_defaults(fn=cmd_a11)
    s2 = sub.add_parser("sop2"); s2.add_argument("--limit-accounts", type=int, default=10)
    s2.add_argument("--max-employees", type=int, default=60); s2.set_defaults(fn=cmd_sop2)
    s3 = sub.add_parser("sop3"); s3.add_argument("--limit", type=int, default=60); s3.set_defaults(fn=cmd_sop3)
    sub.add_parser("dedupe-audit").set_defaults(fn=cmd_dedupe)

    act = sub.add_parser("activity"); act.add_argument("--limit", type=int, default=20)
    act.add_argument("--since", help="Only people validated on/after this date (YYYY-MM-DD)")
    act.add_argument("--recheck", action="store_true", help="Re-check people already checked, not just NOT_RUN ones")
    act.set_defaults(fn=cmd_activity)

    g = sub.add_parser("golden"); g.add_argument("--target", type=int, default=1000)
    g.add_argument("--cycle", default=None)
    g.add_argument("--allow-sop2-only", action="store_true",
                    help="If the fully-validated (SOP3) pool falls short of --target, top up the "
                         "remainder from SOP2-only people (name+LinkedIn+company match, not "
                         "independently validated) - tagged qualification_tier=SOP2_ONLY_UNVALIDATED")
    g.set_defaults(fn=cmd_golden)

    sy = sub.add_parser("sync"); sy.add_argument("--sheet-id", required=True)
    sy.add_argument("--credentials", default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    sy.add_argument("--cycle", default=None); sy.add_argument("--review-share", type=float, default=0.30)
    sy.set_defaults(fn=cmd_sync)
    syo = sub.add_parser("sync-operational"); syo.add_argument("--sheet-id", required=True)
    syo.add_argument("--credentials", default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    syo.set_defaults(fn=cmd_sync_operational)

    pl = sub.add_parser("pull"); pl.add_argument("--sheet-id", required=True)
    pl.add_argument("--credentials", default=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    pl.set_defaults(fn=cmd_pull)

    args = p.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
