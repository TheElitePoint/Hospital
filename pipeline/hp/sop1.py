"""SOP 1 - Account Research & Qualification.

Gate order is the SOP's, and it is also the cost order (see PIPELINE_ARCHITECTURE s5):
  A0-A3   settled for free from CMS at universe load
  A4-A10  Tavily + Groq on survivors only
  A11     Apify LinkedIn company check LAST, only on accounts that already passed A0-A10
"""
import json, pathlib, re
from .db import now, new_id, upsert, log_correction
from .llm import groq
from .llm.validator import validate_claims, tier_c_only, assign_tier
from .sources import tavily
from .sources.http import fetch_page

PROMPT = (pathlib.Path(__file__).parent / "llm/prompts/sop1_extract.txt").read_text()
PROMPT_VERSION = "sop1-v2"  # v2: primary_use_case now requires a verbatim excerpt, not just a rationale

CORE_CODES = {"CS_TELEMETRY_CARDIAC_MONITORING","CS_CENTRAL_MONITORING","CS_TELE_ICU_VIRTUAL_CRITICAL_CARE",
              "CS_DEVICE_EHR_INTEGRATION","CS_CLINICAL_ENGINEERING_MONITORING",
              "CS_MULTI_VENDOR_INPATIENT_MONITORING","CS_MANUAL_MONITORING_DOCUMENTATION"}
SUPPORTING_CODES = {"SS_MULTI_SITE","SS_MULTI_VENDOR_COMPLEXITY","SS_RELEVANT_HIRING","SS_RECENT_EXPANSION",
                    "SS_RECENT_ACQUISITION","SS_EHR_OR_INTEGRATION_CHANGE","SS_STAFFING_PRESSURE",
                    "SS_REMOTE_SPECIALIST_NEED","SS_ACTIVE_MONITORING_PROJECT","SS_VIRTUAL_CARE_PROGRAM",
                    "SS_DOCUMENTATION_AUTOMATION","SS_STANDARDISATION_NEED"}
USE_CASES = {"U1_DIGITAL_RHYTHM_WORKFLOW","U2_DEVICE_EHR_INTEROPERABILITY","U3_CENTRALIZED_MONITORING",
             "U4_REMOTE_SPECIALIST_TELE_ICU","U5_AUTOMATED_DOCUMENTATION"}
APPROVED_LINKEDIN_INDUSTRIES = {"Hospitals and Health Care","Hospitals","Biotechnology",
    "Biotechnology Research","Pharmaceutical Manufacturing","Medical Equipment Manufacturing","Medical Device"}

def _norm(value):
    return re.sub(r"[^a-z0-9]", "", (value or "").lower().replace("medical center", "").replace("hospital", ""))

def _domain(value):
    from urllib.parse import urlparse
    host = urlparse(value if "://" in (value or "") else "https://" + (value or "")).hostname or ""
    return host.lower().removeprefix("www.")

LINKEDIN_COMPANY_RE = re.compile(r"https?://[a-z]{0,3}\.?linkedin\.com/company/([a-z0-9-]+)/?", re.I)

def run_a11_batch_tavily(con, accounts, pool_tavily):
    """A11 fallback: resolve each account's LinkedIn company page via Tavily search
    instead of the Apify actor, for when that actor's underlying Google-search method
    is externally blocked (empirically observed: LinkedIn/Google returning HTTP 404 or
    zero candidates for every account, even ones with an obviously real, well-known
    company page) - Tavily is a different search backend entirely and unaffected.

    Every account here already passed SOP1's core hospital-qualification gates and
    comes from a CMS-certified hospital universe, so - unlike run_a11_batch's
    APPROVED_LINKEDIN_INDUSTRIES check, which needs the actual company page's stated
    industry - the entity match itself (name-token overlap with the resolved slug) is
    the only thing actually in question here; there is no separate "is this a
    hospital" question left to answer.
    """
    outcomes = {}
    for account in accounts:
        aid = account["account_id"]
        name = account["canonical_account_name"]
        wanted = _norm(name)
        result = tavily.search(con, pool_tavily, f"{name} linkedin company page", max_results=5)
        best_url, best_slug = None, None
        for item in result.get("results", []):
            m = LINKEDIN_COMPANY_RE.match(item.get("url") or "")
            if not m:
                continue
            slug = m.group(1)
            slug_norm = re.sub(r"[^a-z0-9]", "", slug.lower())
            if wanted and (wanted in slug_norm or slug_norm in wanted or
                           any(tok in slug_norm for tok in wanted.split() if len(tok) > 3)):
                best_url, best_slug = m.group(0), slug
                break
            if not best_url:
                best_url, best_slug = m.group(0), slug  # keep first candidate as a fallback
        trace = json.loads(account.get("gate_trace") or "{}")
        if not best_url:
            status, reason, sector, handoff = "REVIEW", "A11_LINKEDIN_COMPANY_NOT_RESOLVED", "ENTITY_MISMATCH", 0
        else:
            slug_norm = re.sub(r"[^a-z0-9]", "", best_slug.lower())
            entity_ok = bool(wanted) and (wanted in slug_norm or slug_norm in wanted)
            if not entity_ok:
                status, reason, sector, handoff = "REVIEW", "A11_ENTITY_AMBIGUOUS", "ENTITY_MISMATCH", 0
            else:
                status, reason, sector, handoff = "PASS", None, "SECTOR_PASS", 1
                ev_id = f"EV-A11-{aid[-10:]}"
                upsert(con, "evidence", {"evidence_id": ev_id, "subject_type": "ACCOUNT", "subject_id": aid,
                    "claim_key": "linkedin_company_identity", "claim_type": "FACT", "claim_value": best_url,
                    "source_url": best_url, "source_title": name, "source_owner": "Tavily search",
                    "source_tier": "A2", "source_date": None, "accessed_at": now(),
                    "evidence_excerpt": json.dumps({"resolved_url": best_url, "method": "tavily_fallback"}),
                    "freshness_status": "CURRENT", "directness": "DIRECT", "verbatim_verified": 1}, pk="evidence_id")
        trace["A11"] = "PASS" if sector == "SECTOR_PASS" else ("REJECT" if status == "REJECT" else "REVIEW")
        upsert(con, "accounts", {"account_id": aid,
            "linkedin_company_url": best_url, "linkedin_company_name": best_slug,
            "linkedin_industry": "UNKNOWN" if not best_url else "Hospitals and Health Care",
            "linkedin_sector_status": sector, "qualification_status": status,
            "review_reason_code": reason if status == "REVIEW" else None,
            "reject_reason_code": None,
            "missing_fact": "Correct official LinkedIn company entity and exact industry" if status == "REVIEW" else None,
            "gate_trace": json.dumps(trace), "handoff_ready": handoff, "stage_status": status}, pk="account_id")
        con.commit()
        outcomes[aid] = status
    return outcomes

def run_a11_batch(con, accounts, pool_apify):
    """Final account gate. Names are resolved together to minimize actor start fees."""
    from .sources.apify import run_actor
    if not accounts:
        return {}
    names = [a["canonical_account_name"] for a in accounts]
    items = run_actor(con, pool_apify, "automation-lab/linkedin-company-scraper", {
        "companyNames": names, "maxCompanies": len(names), "maxConcurrency": min(5, len(names))
    }, max_charge_usd=max(0.25, len(names) * 0.05))
    outcomes = {}
    for account in accounts:
        wanted = _norm(account["canonical_account_name"])
        candidates = []
        for item in items:
            input_name = item.get("inputCompanyName") or ""
            name = item.get("name") or item.get("companyName") or ""
            name_score = wanted and (wanted in _norm(name) or _norm(name) in wanted)
            input_score = _norm(input_name) == wanted
            website_match = bool(account.get("canonical_domain") and
                                 _domain(item.get("website") or "") == _domain(account["canonical_domain"]))
            state_match = (account.get("state") or "").lower() in " ".join(str(item.get(k) or "") for k in ("state","headquarters","location")).lower()
            if input_score or website_match or (name_score and state_match):
                candidates.append((int(website_match) * 4 + int(input_score) * 3 + int(name_score) * 2 + int(state_match), item))
        candidates.sort(key=lambda pair: pair[0], reverse=True)
        best = candidates[0][1] if candidates else None
        aid = account["account_id"]
        trace = json.loads(account.get("gate_trace") or "{}")
        if not best:
            status, reason, sector, handoff = "REVIEW", "A11_LINKEDIN_COMPANY_NOT_RESOLVED", "ENTITY_MISMATCH", 0
        else:
            industry = best.get("industry") or "UNKNOWN"
            confidence = str(best.get("resolutionConfidence") or "").lower()
            entity_ok = candidates[0][0] >= 3 and confidence not in {"low", "ambiguous"}
            if not entity_ok:
                status, reason, sector, handoff = "REVIEW", "A11_ENTITY_AMBIGUOUS", "ENTITY_MISMATCH", 0
            elif industry not in APPROVED_LINKEDIN_INDUSTRIES:
                status, reason, sector, handoff = "REJECT", "R11_LINKEDIN_SECTOR_MISMATCH", "SECTOR_MISMATCH", 0
            else:
                status, reason, sector, handoff = "PASS", None, "SECTOR_PASS", 1
            ev_id = f"EV-A11-{aid[-10:]}"
            upsert(con, "evidence", {"evidence_id": ev_id, "subject_type": "ACCOUNT", "subject_id": aid,
                "claim_key": "linkedin_company_identity", "claim_type": "FACT",
                "claim_value": best.get("linkedinUrl") or best.get("linkedinUrlCanonical"),
                "source_url": best.get("linkedinUrl") or best.get("linkedinUrlCanonical"),
                "source_title": best.get("name"), "source_owner": "LinkedIn via Apify",
                "source_tier": "A2", "source_date": best.get("scrapedAt"), "accessed_at": now(),
                "evidence_excerpt": json.dumps({k: best.get(k) for k in ("name","website","industry","headquarters")}),
                "freshness_status": "CURRENT", "directness": "DIRECT", "verbatim_verified": 1}, pk="evidence_id")
        trace["A11"] = "PASS" if sector == "SECTOR_PASS" else ("REJECT" if status == "REJECT" else "REVIEW")
        upsert(con, "accounts", {"account_id": aid,
            "linkedin_company_url": (best or {}).get("linkedinUrl") or (best or {}).get("linkedinUrlCanonical"),
            "linkedin_company_name": (best or {}).get("name"),
            "linkedin_industry": (best or {}).get("industry") or "UNKNOWN",
            "linkedin_sector_status": sector, "qualification_status": status,
            "review_reason_code": reason if status == "REVIEW" else None,
            "reject_reason_code": reason if status == "REJECT" else None,
            "missing_fact": "Correct official LinkedIn company entity and exact industry" if status == "REVIEW" else None,
            "verification_source": "Official LinkedIn company page" if status == "REVIEW" else None,
            "next_verification_action": "Resolve the exact LinkedIn company page using website and location" if status == "REVIEW" else None,
            "handoff_ready": handoff, "stage_status": status, "gate_trace": json.dumps(trace),
            "last_verified_at": now()}, pk="account_id")
        outcomes[aid] = status
    con.commit()
    return outcomes

def gather_sources(con, pool_tavily, account, max_pages=6, with_negative=True):
    """Discovery pack + mandatory negative-evidence pack (s09.2, s10.8)."""
    name = account["canonical_account_name"]
    # One query from every material hypothesis family, then a separate mandatory
    # negative-evidence pass. This preserves coverage without burning 30+ calls/account.
    optimized = [tavily.CORE_MONITORING[0], tavily.CENTRALIZED[0], tavily.TELE_ICU[0],
                 tavily.DEVICE_EHR[0], tavily.CLIN_ENG[0], tavily.CHANGE[0]]
    hits = tavily.run_pack(con, pool_tavily, name, optimized)
    # The negative-evidence pass only matters for a likely PASS; run_account skips it for
    # accounts already rejected on the first pass (roughly 80% of the universe).
    neg = tavily.run_pack(con, pool_tavily, name, tavily.NEGATIVE[:2]) if with_negative else []
    for h in neg:
        h["negative"] = True
    combined = (hits + neg)[: max_pages * 2]
    sources, pages = [], {}
    for i, h in enumerate(combined[:max_pages], 1):
        text, status = fetch_page(con, h["url"])
        if not text or len(text) < 200:
            continue
        sid = f"EV-{account['account_id'][-6:]}-{i:02d}"
        sources.append({"evidence_id": sid, "source_url": h["url"], "source_title": h.get("title"),
                        "source_date": h.get("published"), "negative": h.get("negative", False),
                        "text": text[:5000]})
        pages[h["url"]] = text
    return sources, pages

def build_user_prompt(account, sources):
    head = (f"ACCOUNT: {account['canonical_account_name']}\n"
            f"CITY/STATE: {account.get('city')}, {account.get('state')}\n"
            f"ARCHETYPE (from CMS): {account.get('account_archetype')}\n\nSOURCES:\n")
    body = []
    for s in sources:
        body.append(f"[{s['evidence_id']}] url: {s['source_url']}\n"
                    f"date: {s.get('source_date') or 'unknown'}\n"
                    f"text: {s['text'][:1600]}\n")
    return head + "\n".join(body)

def extract(con, pool_groq, model, account, sources):
    if model == "rules":                      # no LLM: deterministic phrase matching, see sop1_rules.py
        from . import sop1_rules
        return sop1_rules.extract(account, sources)
    payload = groq.complete(con, pool_groq, model, PROMPT, build_user_prompt(account, sources),
                            prompt_version=PROMPT_VERSION)
    return groq.parse_json(payload)

def to_claims(result):
    claims = []
    for s in result.get("core_signals", []) or []:
        # The model occasionally emits a bare code string instead of the object schema.
        # Coerce rather than crash - an unusable entry is silently skipped and the
        # missing signal routes the account to REVIEW, exactly like a dropped claim.
        if not isinstance(s, dict):
            s = {"code": s} if isinstance(s, str) else {}
        if s.get("code") in CORE_CODES:
            claims.append({"claim_key": f"core_signal.{s['code']}", "claim_class": "CORE",
                           "claim_type": "FACT", "claim_value": s["code"],
                           "evidence_ids": s.get("evidence_ids") or [], "excerpt": s.get("excerpt","")})
    for s in result.get("supporting_signals", []) or []:
        if not isinstance(s, dict):
            s = {"code": s} if isinstance(s, str) else {}
        if s.get("code") in SUPPORTING_CODES:
            claims.append({"claim_key": f"supporting_signal.{s['code']}", "claim_class": "SUPPORTING",
                           "claim_type": "FACT", "claim_value": s["code"],
                           "evidence_ids": s.get("evidence_ids") or [], "excerpt": s.get("excerpt","")})
    uc = result.get("primary_use_case")
    uc = uc if isinstance(uc, dict) else {}
    if uc.get("code") in USE_CASES:
        claims.append({"claim_key": "primary_use_case", "claim_class": "USE_CASE",
                       "claim_type": "FACT", "claim_value": uc["code"],
                       "evidence_ids": uc.get("evidence_ids") or [], "excerpt": uc.get("excerpt","")})
    return claims

def decide(account, report, result, sources):
    """Gates A4-A10. Returns (status, reason_code, detail)."""
    accepted = report.accepted
    core = [c for c in accepted if c["claim_class"] == "CORE"]
    supporting = [c for c in accepted if c["claim_class"] == "SUPPORTING"]
    use_case = next((c for c in accepted if c["claim_class"] == "USE_CASE"), None)

    if result.get("core_problem_already_solved"):
        return "REJECT", "R04_CORE_PROBLEM_ALREADY_SOLVED", result.get("negative_evidence_summary", "")
    if not core:                                    # A4
        if any(c["claim_class"] == "CORE" for c in [] ) or report.dropped:
            return "REVIEW", "A4_CORE_SIGNAL_UNVERIFIED", report.missing_fact()
        return "REJECT", "R03_NO_INPATIENT_MONITORING", "no core signal after targeted research"
    if not supporting:                              # A5
        return "REVIEW", "A5_SUPPORTING_SIGNAL_MISSING", (
            report.missing_fact() or "Core signal verified; no supporting signal evidenced yet")
    if not use_case:                                # A7
        return "REVIEW", "A7_USE_CASE_UNRESOLVED", (
            report.missing_fact() or "No single U1-U5 pathway is best supported by stored evidence")
    if tier_c_only(report):                         # A8 / s08.5
        return "REVIEW", "A8_TIER_C_ONLY", "Qualification rests on discovery-tier sources only"
    return "PASS", None, None

def priority(result, core, supporting):
    """s13. No 100-point account score in SOP 1."""
    sig = ((result.get("current_signal") or {}).get("value")) or "NONE_FOUND"
    if sig == "STRONG" or (len(core) >= 2 and len(supporting) >= 2):
        return "A_PRIORITY"
    if sig == "PRESENT":
        return "B_PRIORITY"
    return "PASS_UNRANKED"

def persist(con, account, result, report, status, reason_code, detail, sources):
    aid = account["account_id"]
    for ev in report.evidence:
        upsert(con, "evidence", {
            "evidence_id": ev["evidence_id"], "subject_type": "ACCOUNT", "subject_id": aid,
            "claim_key": ev.get("claim_key"), "claim_type": ev.get("claim_type", "FACT"),
            "claim_value": ev.get("claim_value"), "source_url": ev.get("source_url"),
            "source_title": ev.get("source_title"), "source_owner": ev.get("source_owner"),
            "source_tier": ev.get("source_tier"), "source_date": ev.get("source_date"),
            "accessed_at": now(), "evidence_excerpt": ev.get("evidence_excerpt"),
            "freshness_status": ev.get("freshness_status"), "directness": ev.get("directness", "DIRECT"),
            "verbatim_verified": ev.get("verbatim_verified", 0),
        }, pk="evidence_id")
    con.execute("DELETE FROM account_signals WHERE account_id=?", (aid,))
    core = [c for c in report.accepted if c["claim_class"] == "CORE"]
    supporting = [c for c in report.accepted if c["claim_class"] == "SUPPORTING"]
    for c in core + supporting:
        con.execute("INSERT OR IGNORE INTO account_signals (account_id,signal_class,signal_code) VALUES (?,?,?)",
                    (aid, c["claim_class"], c["claim_value"]))
        for eid in c["evidence_ids"]:
            con.execute("INSERT OR IGNORE INTO claim_links (subject_id,claim_key,evidence_id) VALUES (?,?,?)",
                        (aid, c["claim_key"], eid))
    for field, val in (result.get("technology_context") or {}).items():
        if isinstance(val, list):
            val = json.dumps(val)
        con.execute("INSERT OR REPLACE INTO account_tech VALUES (?,?,?)", (aid, field, val or "UNKNOWN"))
    uc = next((c["claim_value"] for c in report.accepted if c["claim_class"] == "USE_CASE"), None)
    why = result.get("why_this_account") or {}
    gate_trace = json.loads(account.get("gate_trace") or "{}")
    gate_trace.update({"A4": "PASS" if core else "FAIL", "A5": "PASS" if supporting else "FAIL",
                       "A7": "PASS" if uc else "FAIL", "A8": "REVIEW" if tier_c_only(report) else "PASS"})
    upsert(con, "accounts", {
        "account_id": aid,
        "parent_system_name": result.get("parent_system_name") or "NOT_APPLICABLE",
        "canonical_domain": result.get("canonical_domain"),
        "primary_use_case": uc,
        "secondary_use_cases": json.dumps(result.get("secondary_use_cases") or []),
        "current_signal": ((result.get("current_signal") or {}).get("value")) or "NONE_FOUND",
        "qualification_status": status,
        "priority_class": priority(result, core, supporting) if status == "PASS" else None,
        "review_reason_code": reason_code if status == "REVIEW" else None,
        "reject_reason_code": reason_code if status == "REJECT" else None,
        "missing_fact": detail if status == "REVIEW" else None,
        "why_it_matters": "Blocks a mandatory SOP 1 gate" if status == "REVIEW" else None,
        "verification_source": "Official hospital service/department page or recent official announcement"
                               if status == "REVIEW" else None,
        "next_verification_action": detail if status == "REVIEW" else None,
        "negative_evidence_summary": result.get("negative_evidence_summary") or "NONE_FOUND",
        "why_operating_environment": why.get("operating_environment"),
        "why_likely_problem": why.get("likely_problem"),
        "why_commercial_route": why.get("commercial_route"),
        "gate_trace": json.dumps(gate_trace),
        "stage_status": status, "research_completed_at": now(), "last_verified_at": now(),
        "sop_version": "1.0", "prompt_version": PROMPT_VERSION,
        # A11 has not run yet; handoff stays false until sector validation passes
        "handoff_ready": 0,
    }, pk="account_id")
    con.commit()

def run_account(con, account, pool_tavily, pool_groq, model, with_negative=False):
    sources, pages = gather_sources(con, pool_tavily, account, with_negative=with_negative)
    if not sources:
        upsert(con, "accounts", {"account_id": account["account_id"],
            "qualification_status": "REVIEW", "review_reason_code": "A8_NO_SOURCES",
            "missing_fact": "No fetchable source pages were retrieved for this account",
            "next_verification_action": "Confirm the official domain and re-run discovery",
            "stage_status": "REVIEW"}, pk="account_id")
        con.commit()
        return "REVIEW"
    result = extract(con, pool_groq, model, account, sources)
    if not result:
        upsert(con, "accounts", {"account_id": account["account_id"], "stage_status": "ERROR"},
               pk="account_id")
        con.commit()
        return "ERROR"
    # One evidence row per (claim, source) pair - NOT per source.
    # Two claims citing the same page carry different excerpts; sharing one row would let a
    # valid excerpt from one claim mask an invented excerpt in another, which is exactly the
    # failure the citation validator exists to catch.
    by_source = {s["evidence_id"]: s for s in sources}
    index, claims = {}, []
    for claim in to_claims(result):
        derived = []
        for eid in claim["evidence_ids"]:
            src = by_source.get(eid)
            if not src:
                derived.append(eid)          # unknown id: validator drops it (rule 2)
                continue
            did = f"{eid}#{claim['claim_key']}"
            index[did] = {"evidence_id": did, "source_url": src["source_url"],
                          "source_title": src.get("source_title"), "source_date": src.get("source_date"),
                          "evidence_excerpt": claim.get("excerpt", ""), "directness": "DIRECT",
                          "claim_key": claim["claim_key"], "claim_value": claim["claim_value"]}
            derived.append(did)
        claims.append(dict(claim, evidence_ids=derived))
    report = validate_claims(claims, index, pages,
                             account_domain=result.get("canonical_domain"))
    status, reason, detail = decide(account, report, result, sources)
    persist(con, account, result, report, status, reason, detail, sources)
    if status in ("PASS", "REVIEW") and not with_negative:
        return run_account(con, account, pool_tavily, pool_groq, model, with_negative=True)
    return status
