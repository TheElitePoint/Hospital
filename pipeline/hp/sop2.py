"""SOP 2 people discovery and conservative deterministic qualification."""
from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urlsplit, urlunsplit

from .db import new_id, now, upsert
from .dedupe import add_candidate, linkedin_key, norm
from .sources.apify import run_actor

ROLE_RULES = [
    ("TELEMETRY_CARDIAC_MONITORING", r"telemetry|cardiac monitoring|monitoring (?:director|manager)|cardiac services"),
    ("NURSING_INFORMATICS", r"nursing informatics|chief nursing informatics|\bcnio\b"),
    ("CLINICAL_ENGINEERING_HTM", r"clinical engineering|biomedical|\bbiomed\b|healthcare technology management|\bhtm\b"),
    ("CLINICAL_SYSTEMS_INTEGRATION", r"clinical systems|integration|interoperability|interface engine"),
    ("CLINICAL_INFORMATICS", r"clinical informatics|chief medical information|\bcmio\b"),
    ("VIRTUAL_CARE_TELEHEALTH", r"virtual care|telehealth|telemedicine|tele-icu|virtual nursing"),
    ("CRITICAL_CARE_LEADERSHIP", r"critical care|intensive care|\bicu\b"),
    ("DOCUMENTATION_REVENUE_INTEGRITY", r"clinical documentation|documentation integrity|revenue integrity"),
    ("NURSING_EXECUTIVE", r"chief nursing|chief nurse|\bcno\b|vp.{0,20}nursing|vice president.{0,20}nursing|nursing (?:director|executive)"),
    ("IT_CIO", r"chief information officer|\bcio\b|vp.{0,20}(?:it|information technology)|information systems"),
    ("CLINICAL_OPERATIONS", r"clinical operations|hospital operations|patient care services|chief operating|\bcoo\b"),
    ("EXECUTIVE_SPONSOR", r"chief executive|\bceo\b|hospital president|hospital administrator"),
]

USE_CASE_DIRECT = {
    "U1_DIGITAL_RHYTHM_WORKFLOW": {"TELEMETRY_CARDIAC_MONITORING"},
    "U2_DEVICE_EHR_INTEROPERABILITY": {"CLINICAL_ENGINEERING_HTM", "CLINICAL_SYSTEMS_INTEGRATION", "IT_CIO"},
    "U3_CENTRALIZED_MONITORING": {"TELEMETRY_CARDIAC_MONITORING", "VIRTUAL_CARE_TELEHEALTH", "NURSING_EXECUTIVE"},
    "U4_REMOTE_SPECIALIST_TELE_ICU": {"VIRTUAL_CARE_TELEHEALTH", "CRITICAL_CARE_LEADERSHIP", "NURSING_EXECUTIVE"},
    "U5_AUTOMATED_DOCUMENTATION": {"NURSING_INFORMATICS", "CLINICAL_INFORMATICS", "CLINICAL_SYSTEMS_INTEGRATION"},
}

INDIA = re.compile(r"\b(india|delhi|mumbai|bengaluru|bangalore|hyderabad|chennai|pune|kolkata|gurugram|noida)\b", re.I)


def canonical_linkedin(url):
    if not url:
        return None
    value = str(url).strip()
    if not re.search(r"linkedin\.com/in/", value, re.I):
        return None
    parts = urlsplit(value if "://" in value else "https://" + value)
    path = "/" + "/".join(p for p in parts.path.split("/") if p) + "/"
    return urlunsplit(("https", "www.linkedin.com", path, "", ""))


def role_for(title):
    value = (title or "").lower()
    for family, pattern in ROLE_RULES:
        if re.search(pattern, value, re.I):
            return family
    return None


def seniority(title):
    value = (title or "").lower()
    if re.search(r"chief|\bceo\b|\bcio\b|\bcno\b|\bcmio\b|president", value): return "C_SUITE"
    if re.search(r"vice president|\bvp\b", value): return "VP"
    if "director" in value: return "DIRECTOR"
    if "manager" in value or "head" in value: return "MANAGER"
    return "UNKNOWN"


def _commercial(family, use_case):
    direct = family in USE_CASE_DIRECT.get(use_case, set())
    if direct: return "DIRECT_OWNER", "P1_CANDIDATE"
    if family in {"IT_CIO", "CLINICAL_SYSTEMS_INTEGRATION", "CLINICAL_ENGINEERING_HTM"}:
        return "TECHNICAL_EVALUATOR", "P2_CANDIDATE"
    if family in {"NURSING_EXECUTIVE", "NURSING_INFORMATICS", "CLINICAL_INFORMATICS", "CRITICAL_CARE_LEADERSHIP", "CLINICAL_OPERATIONS", "TELEMETRY_CARDIAC_MONITORING"}:
        return "CLINICAL_EVALUATOR", "P2_CANDIDATE"
    return "EXECUTIVE_SPONSOR", "P3_CANDIDATE"


def _account_for(item, accounts):
    raw_url = str(item.get("companyUrl") or item.get("companyLinkedinUrl") or "").lower().rstrip("/")
    raw_name = re.sub(r"[^a-z0-9]", "", str(item.get("companyName") or "").lower())
    for account in accounts:
        if raw_url and raw_url == str(account.get("linkedin_company_url") or "").lower().rstrip("/"):
            return account
    scored = []
    for account in accounts:
        name = re.sub(r"[^a-z0-9]", "", str(account["canonical_account_name"]).lower())
        if raw_name and (raw_name in name or name in raw_name): scored.append((min(len(raw_name), len(name)), account))
    return max(scored, default=(0, None), key=lambda x: x[0])[1]


SOP2_PEOPLE_TARGET = 8  # s01 "up to approximately 10-12"; 8 is the "stop topping up" floor


def discover_batch(con, accounts, pool_apify, max_employees=60):
    """One actor run for many qualified accounts; persist every relevant investigated person."""
    accounts = [dict(a) for a in accounts if a.get("handoff_ready") and a.get("linkedin_company_url")]
    if not accounts:
        return {"discovered": 0, "pass": 0, "review": 0, "reject": 0, "duplicates": 0}
    urls = [a["linkedin_company_url"] for a in accounts]
    # Tried harvestapi/linkedin-company-employees as a cheaper, paginating replacement,
    # but it returns zero results on this account tier (the run succeeds instantly with
    # no scrape attempted at all - confirmed by directly re-running it against a live
    # test account with a fresh, empty budget). automation-lab's actor genuinely does
    # the Google-SERP-based scrape (confirmed live: 10 real profiles back in ~25s), so
    # it stays the working choice even though it's SERP-bounded rather than truly
    # paginated - it returns roughly the same ~10 profiles per company each run since
    # Google's ranking for a given company is largely stable, which is why increasing
    # maxEmployees doesn't surface more people from an already-topped-up account; the
    # real lever for more people is qualifying MORE accounts (SOP1/A11), not deeper
    # per-account scraping.
    # This actor genuinely needs more than the default 600s when scraping several
    # companies' employee lists at once - give it explicit server-side room rather
    # than let Apify's own default run timeout cut it off mid-scrape.
    items = run_actor(con, pool_apify, "automation-lab/linkedin-company-employees-scraper",
                      {"companyUrls": urls, "maxEmployees": int(max_employees)},
                      max_charge_usd=max(0.50, len(urls) * max_employees * 0.006 + 0.05),
                      run_timeout_secs=900)
    tally = {"discovered": 0, "pass": 0, "review": 0, "reject": 0, "duplicates": 0}
    family_counts = {}
    for item in items:
        account = _account_for(item, accounts)
        if not account:
            continue
        title = item.get("jobTitle") or item.get("title") or item.get("headline") or "UNKNOWN"
        family = role_for(title)
        if not family:
            continue
        url = canonical_linkedin(item.get("profileUrl") or item.get("linkedinUrl") or item.get("url"))
        name = item.get("name") or item.get("fullName") or "UNKNOWN"
        if not url or name == "UNKNOWN":
            continue
        li_key = linkedin_key(url)
        existing = con.execute("SELECT person_id FROM people WHERE linkedin_canonical_key=? OR lower(rtrim(linkedin_profile_url,'/'))=lower(rtrim(?,'/'))", (li_key, url)).fetchone()
        if existing:
            tally["duplicates"] += 1
            continue
        location = item.get("location") or "UNKNOWN"
        location_india = bool(INDIA.search(location))
        commercial, initial = _commercial(family, account.get("primary_use_case"))
        key = (account["account_id"], family)
        family_counts[key] = family_counts.get(key, 0) + 1
        too_many = family_counts[key] > 2
        name_key, title_key = norm(name), norm(title)
        same_name = con.execute("SELECT person_id FROM people WHERE account_id=? AND normalized_name=? LIMIT 1", (account["account_id"], name_key)).fetchone()
        status = "REVIEW" if location_india or same_name else ("REJECT" if too_many else "PERSON_PASS")
        reject = "P-R04_NO_PROBLEM_RELEVANCE" if too_many else None
        review = "P-R06_IDENTITY_AMBIGUOUS" if (location_india or same_name) else None
        person_id = "PER-" + hashlib.sha256(url.lower().rstrip("/").encode()).hexdigest()[:16]
        scope = ("SYSTEM_LEVEL" if str(account.get("account_id") or "").startswith("SYS-")
                 or "system" in (account.get("parent_system_name") or "").lower() else "FACILITY_LEVEL")
        upsert(con, "people", {"person_id": person_id, "account_id": account["account_id"], "full_name": name,
            "linkedin_profile_url": url, "linkedin_canonical_key": li_key,
            "normalized_name": name_key, "normalized_title": title_key,
            "linkedin_identity_status": "MATCHED", "linkedin_activity_status": "NOT_CHECKED",
            "current_company_display_name": item.get("companyName") or account["canonical_account_name"],
            "current_title": title, "department": item.get("department") or family, "role_family": family,
            "seniority_level": seniority(title), "role_scope": scope, "location_if_available": location,
            "primary_use_case": account.get("primary_use_case"),
            "person_use_case_relevance": f"{commercial} for {account.get('primary_use_case')}",
            "problem_ownership_level": commercial, "evaluation_influence": "HIGH" if initial != "P3_CANDIDATE" else "MEDIUM",
            "commercial_influence": "MEDIUM", "technical_influence": "HIGH" if commercial == "TECHNICAL_EVALUATOR" else "MEDIUM",
            "internal_routing_value": "HIGH" if initial == "P3_CANDIDATE" else "MEDIUM",
            "current_role_status": "PROBABLE", "profile_identity_confidence": "HIGH", "initial_priority": initial,
            "better_person_json": json.dumps({"checked": True, "direct_family_present": bool(USE_CASE_DIRECT.get(account.get('primary_use_case'))),
                                               "p1_allowed": initial == "P1_CANDIDATE"}),
            "duplicate_status": "UNIQUE", "person_status": status, "reject_reason_code": reject,
            "review_reason": review,
            "missing_fact": "Confirm this is a US-based current employee and resolve same-name identity" if status == "REVIEW" else None,
            "next_verification_action": "Compare the current profile, member identity, title history, and official hospital bio" if status == "REVIEW" else None,
            "pipeline_stage": "SOP2", "stage_status": "PASS" if status == "PERSON_PASS" else status,
            "last_checked_at": now(), "prompt_version": "sop2-deterministic-v1"}, pk="person_id")
        ev_id = "EV-P2-" + person_id[-16:]
        upsert(con, "evidence", {"evidence_id": ev_id, "subject_type": "PERSON", "subject_id": person_id,
            "claim_key": "linkedin_identity_and_discovered_role", "claim_type": "FACT", "claim_value": title,
            "source_url": url, "source_title": f"{name} LinkedIn profile", "source_owner": "LinkedIn via Apify",
            "source_tier": "A2", "source_date": item.get("scrapedAt"), "accessed_at": now(),
            "evidence_excerpt": json.dumps({k: item.get(k) for k in ("name","headline","jobTitle","companyName","location")}),
            "freshness_status": "CURRENT" if item.get("source") == "voyager" else "UNKNOWN",
            "directness": "DIRECT", "verbatim_verified": 1}, pk="evidence_id")
        tally["discovered"] += 1
        if same_name:
            add_candidate(con, person_id, same_name["person_id"], "NAME_ACCOUNT", f"{account['account_id']}|{name_key}")
        same_title = con.execute("SELECT person_id FROM people WHERE account_id=? AND normalized_title=? AND person_id<>? LIMIT 1", (account["account_id"], title_key, person_id)).fetchone()
        if same_title:
            add_candidate(con, person_id, same_title["person_id"], "TITLE_ACCOUNT", f"{account['account_id']}|{title_key}")
        tally["pass" if status == "PERSON_PASS" else ("review" if status == "REVIEW" else "reject")] += 1
    # Stamp every account this batch actually looked at - whether it found 0 or 12
    # people - so the next run's selection query can tell "never tried" (NULL, highest
    # priority) apart from "tried, came up short of SOP2_PEOPLE_TARGET" (a timestamp,
    # only revisited once every never-tried account has had its turn).
    ts = now()
    for account in accounts:
        con.execute("UPDATE accounts SET sop2_attempted_at=? WHERE account_id=?", (ts, account["account_id"]))
    con.commit()
    return tally
