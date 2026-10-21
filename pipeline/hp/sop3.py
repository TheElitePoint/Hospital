"""SOP 3 independent person validation and QA.

The validator payload is built from identity, raw evidence and account context only. It
never receives SOP 2 relevance prose, priority, or better-person conclusions.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone, timedelta

from .db import log_correction, now, upsert
from .keys import KeyPool
from .sop2 import INDIA, USE_CASE_DIRECT, canonical_linkedin, role_for
from .sources import tavily
from . import cache
from .sources.apify import run_actor, _request_key

_STATE_NAMES = ("alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|"
                "illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|"
                "missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|"
                "oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|"
                "washington|west virginia|wisconsin|wyoming|district of columbia")
_STATE_ABBR = ("AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|"
               "PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC")
# Every US state, not just the original five-state territory: a profile in "San Diego,
# California" was being held in REVIEW as "not clearly US" after the territory grew.
US_MARKERS = re.compile(r"\b(united states|usa|u\.s\.|" + _STATE_NAMES + r")\b|,\s*(?-i:" + _STATE_ABBR + r")\b|\s(?-i:" + _STATE_ABBR + r")\s*$", re.I)
DEPARTURE = re.compile(r"\b(former|departed|left|joins?|joined|appointed|named)\b", re.I)
ACTIVITY_WINDOW_DAYS = 90


def build_validation_payload(con, person):
    """The structural independence boundary required by SOP 3 section 00.4."""
    account = con.execute("SELECT account_id,canonical_account_name,parent_system_name,canonical_domain,state,city,primary_use_case,linkedin_company_url FROM accounts WHERE account_id=?",
                          (person["account_id"],)).fetchone()
    evidence = [dict(r) for r in con.execute("SELECT source_url,source_title,source_tier,source_date,accessed_at,evidence_excerpt,claim_key FROM evidence WHERE subject_type='PERSON' AND subject_id=?",
                                              (person["person_id"],)).fetchall()]
    return {"person_id": person["person_id"], "full_name": person["full_name"],
            "linkedin_profile_url": person["linkedin_profile_url"],
            "account": dict(account) if account else {}, "raw_evidence": evidence}


def _profile_url(item):
    return canonical_linkedin(item.get("linkedinUrl") or item.get("profileUrl") or item.get("url") or item.get("inputUrl"))


def _experiences(item):
    raw = item.get("experience") or item.get("experiences") or item.get("positions") or []
    if isinstance(raw, dict): raw = raw.get("items") or raw.get("elements") or []
    return raw if isinstance(raw, list) else []


def _text(value):
    if isinstance(value, dict):
        return value.get("name") or value.get("text") or value.get("title") or json.dumps(value)
    return str(value or "")


def _current_position(item, account):
    names = [account.get("canonical_account_name"), account.get("parent_system_name")]
    needles = [re.sub(r"[^a-z0-9]", "", (n or "").lower()) for n in names if n and n != "NOT_APPLICABLE"]
    for exp in _experiences(item):
        end = _text(exp.get("endDate") or exp.get("dateEnd") or exp.get("end") or "").lower()
        current = not end or "present" in end or exp.get("isCurrent") is True
        company = _text(exp.get("companyName") or exp.get("company") or exp.get("subtitle"))
        norm = re.sub(r"[^a-z0-9]", "", company.lower())
        if current and any(n and (n in norm or norm in n) for n in needles):
            return {"title": _text(exp.get("title") or exp.get("position") or item.get("headline")),
                    "company": company, "raw": exp}
    headline = _text(item.get("headline"))
    company = _text(item.get("currentCompany") or item.get("companyName"))
    norm = re.sub(r"[^a-z0-9]", "", company.lower())
    if any(n and (n in norm or norm in n) for n in needles):
        return {"title": _text(item.get("jobTitle") or item.get("title") or headline), "company": company, "raw": item}
    return None


def _commercial(family, use_case):
    if family in USE_CASE_DIRECT.get(use_case, set()): return "DIRECT_OWNER", "P1"
    if family in {"IT_CIO", "CLINICAL_SYSTEMS_INTEGRATION", "CLINICAL_ENGINEERING_HTM"}: return "TECHNICAL_EVALUATOR", "P2"
    if family == "EXECUTIVE_SPONSOR": return "EXECUTIVE_SPONSOR", "P3"
    return "CLINICAL_EVALUATOR", "P2"


EXIT_WORDS = re.compile(r"\b(left|leaves|leaving|departed|departing|departure|resigned|resigns|retired|retires|"
                        r"retiring|stepping down|steps down|stepped down|former)\b", re.I)
ARRIVE_WORDS = re.compile(r"\b(joined|joins|appointed|named|hired)\b", re.I)
FIRST_PERSON_MOVE = re.compile(r"\b(i['\u2019]?ve|i have)\s+(just\s+)?joined\b|"
                               r"\bexcited to (share|announce)[^.]{0,60}\b(joined|joining)\b", re.I)
_NAME_NOISE = {"fache", "facHE".lower(), "mhsa", "mhsm", "phd", "mba", "msn", "mha", "dnp", "rn", "cpnp", "bcccp"}
_ACCOUNT_STOP = {"hospital", "hospitals", "medical", "center", "centre", "health", "system", "regional",
                 "community", "memorial", "university", "care", "clinic", "services", "healthcare", "campus"}


def _name_key(name):
    tokens = [re.sub(r"[^a-z]", "", t) for t in (name or "").lower().split()]
    tokens = [t for t in tokens if len(t) >= 4 and t not in _NAME_NOISE]
    return max(tokens, key=len) if tokens else None


def _account_tokens(account_name):
    words = re.findall(r"[a-z]{3,}", (account_name or "").lower().replace("'", ""))
    toks = [w for w in words if w not in _ACCOUNT_STOP and w not in ("the", "and", "for")] or words
    # "SDCH" for San Dimas Community Hospital: news about the person joining their own
    # hospital usually uses the acronym, which must count as their own employer.
    initials = "".join(w[0] for w in re.findall(r"[a-z]+", (account_name or "").lower().replace("'", "")))
    return toks + ([initials] if len(initials) >= 3 else [])


_CREDENTIALS = {"mba", "msn", "mha", "phd", "dnp", "rn", "bsn", "fache", "facHE".lower(), "cpa", "pmp", "cissp", "chcio",
                "facs", "mph", "msha", "jr", "sr", "ii", "iii", "iv", "md", "do", "dr", "cnor", "ccrn", "cphq"}


def _name_pattern(name):
    """Full first+last name, so a shared surname ('Clayton, Dubilier & Rice', 'David
    Rollins') is not mistaken for this person. Up to two middle names/initials allowed."""
    tokens = [t for t in re.sub(r"[^a-zA-Z' -]", " ", name or "").replace("-", " ").split()
              if len(t) >= 2 and t.lower().strip("'") not in _CREDENTIALS]
    if len(tokens) < 2:
        return None
    first, last = re.escape(tokens[0]), re.escape(tokens[-1])
    return re.compile(rf"\b{first}\b(?:\W+\w{{1,12}}\.?){{0,2}}?\W+{last}\b|\b{last}\b,?\s+{first}\b", re.I)


def departure_signal(text, name, account_name):
    """True when `text` suggests this person has left or is leaving the account.

    Looks only in a window around the person's FULL name (first and last, not the surname
    alone): an explicit exit word counts; an arrival word counts only if the window does
    not mention their own employer (joining elsewhere); a first-person 'I've joined ...'
    counts unless it names their own employer."""
    pattern = _name_pattern(name)
    if pattern is None:
        # Only a first name is usable ("Melissa E."): it can collide with a hospital or
        # place name, so a window around it proves nothing. Keep the old strict behaviour
        # (any departure word in a result containing the name) rather than clearing them.
        key = _name_key(name)
        return bool(key and DEPARTURE.search(text) and key in text.lower())
    own = _account_tokens(account_name)
    found = False
    for m in pattern.finditer(text):
        found = True
        window = text[max(0, m.start() - 100): m.end() + 160]
        wl = re.sub(r"['\u2019]", "", window.lower())
        # "former" is usually someone's earlier job ("former U of Chicago exec, now CIO
        # here"), so it only counts beside their own employer; hard exit words
        # (left/retired/resigned/stepped down...) count on their own.
        if any(e.group(0).lower() != "former" or any(t in wl for t in own) for e in EXIT_WORDS.finditer(window)):
            return True
        if ARRIVE_WORDS.search(window) and not any(t in wl for t in own):
            return True
    fp = FIRST_PERSON_MOVE.search(text)
    if found and fp and not any(t in re.sub(r"['\u2019]", "", text[fp.start(): fp.end() + 120].lower()) for t in own):
        return True
    return False


def _disproof(con, pool_tavily, name, account_name):
    query = f'"{name}" "{account_name}" (former OR left OR joined OR appointed OR departure)'
    result = tavily.search(con, pool_tavily, query, max_results=5)
    suspicious = []
    for row in result.get("results", []):
        text = f"{row.get('title','')} {row.get('content','')}"
        if departure_signal(text, name, account_name):
            suspicious.append({"url": row.get("url"), "title": row.get("title"), "excerpt": row.get("content", "")[:500]})
    return suspicious


def validate_batch(con, people, pool_apify, pool_tavily):
    payloads = [build_validation_payload(con, dict(p)) for p in people]
    urls = [p["linkedin_profile_url"] for p in payloads if p.get("linkedin_profile_url")]
    if not urls:
        return {"pass": 0, "review": 0, "reject": 0}
    # Scraping many LinkedIn profiles in one run genuinely takes longer than Apify's
    # default run timeout - give it explicit server-side room (same fix as SOP 2's
    # employee scraper) instead of cycling through repeated timeout-and-resubmit.
    # 2026-10-10: crawlerbros/linkedin-profile-scraper was removed from the Apify Store (404
    # for every key); harvestapi's is the maintained equivalent ($4 per 1,000 profiles).
    # Free-tier Apify accounts are capped at 10 items per run, so send profiles in chunks of 10.
    profiles = []
    for i in range(0, len(urls), 10):
        chunk = urls[i:i + 10]
        request = {"actor": "harvestapi/linkedin-profile-scraper",
                   "input": {"urls": chunk, "profileScraperMode": "Profile details no email ($4 per 1k)"},
                   "max_charge_usd": max(0.1, len(chunk) * 0.01), "run_timeout_secs": 600}
        for attempt in range(4):
            got = run_actor(con, pool_apify, "harvestapi/linkedin-profile-scraper", request["input"],
                            max_charge_usd=request["max_charge_usd"], run_timeout_secs=600)
            err = next((r.get("error") for r in got if r.get("error")), None)
            if not err or attempt == 3:
                break
            # Free Apify accounts are capped at 50 runs of this actor. That arrives as a dataset
            # row, not an HTTP error, so cool the key that just ran it (12h), drop the cached
            # error and resubmit so another key's account takes the chunk.
            used = con.execute("SELECT key_id FROM api_keys WHERE provider='apify' AND last_used_at IS NOT NULL "
                               "ORDER BY last_used_at DESC LIMIT 1").fetchone()
            if used and "limited" in str(err).lower():
                con.execute("UPDATE api_keys SET cooldown_until=?, last_error=? WHERE key_id=?",
                            ((datetime.now(timezone.utc) + timedelta(hours=12)).isoformat(timespec="seconds"),
                             str(err)[:200], used["key_id"]))
            con.execute("DELETE FROM api_cache WHERE cache_key=?", (cache.key_for("apify", request),))
            con.execute("DELETE FROM apify_runs WHERE request_key=?", (_request_key("harvestapi/linkedin-profile-scraper", request["input"]),))
            con.commit()
        profiles += [r for r in got if not r.get("error")]
    for item in profiles:                            # flatten {"linkedinText": ..., "parsed": {...}}
        loc = item.get("location")
        if isinstance(loc, dict):
            # linkedinText is a display label ("Greater Houston"); parsed.text carries the real
            # "Houston, TX, United States" that the US-location check needs.
            item["location"] = (loc.get("parsed") or {}).get("text") or loc.get("linkedinText") or ""
    by_url = {_profile_url(item): item for item in profiles if _profile_url(item)}
    tally = {"pass": 0, "review": 0, "reject": 0}
    for payload in payloads:
        person_id, account = payload["person_id"], payload["account"]
        profile = by_url.get(canonical_linkedin(payload["linkedin_profile_url"]))
        location = _text((profile or {}).get("location") or (profile or {}).get("geoLocationName"))
        if INDIA.search(location):
            status, reason, employment = "VALIDATED_REJECT", "P-R01_WRONG_COMPANY", "UNKNOWN"
            current = None
        else:
            current = _current_position(profile or {}, account) if profile else None
            if not profile:
                status, reason, employment = "VALIDATED_REVIEW", None, "UNKNOWN"
            elif not current:
                status, reason, employment = "VALIDATED_REVIEW", None, "UNKNOWN"
            elif location and location != "UNKNOWN" and not US_MARKERS.search(location):
                status, reason, employment = "VALIDATED_REVIEW", None, "CURRENT_CONFIRMED"
            else:
                status, reason, employment = "VALIDATED_PASS", None, "CURRENT_CONFIRMED"
        title = current["title"] if current else _text((profile or {}).get("headline"))
        upstream = con.execute("SELECT current_title,role_family,initial_priority FROM people WHERE person_id=?", (person_id,)).fetchone()
        family = role_for(title)
        if not family and upstream and upstream["current_title"]:
            # crawlerbros/linkedin-profile-scraper's `experiences[]` entries often have
            # no title/position field at all, and for some profiles its top-level
            # `headline` is the company name or unrelated profile text (e.g. a
            # location line) - none of which maps to a role family. Fall back to
            # SOP2's title (captured via a different, better-structured actor)
            # rather than let an extraction gap force an otherwise independently
            # confirmed current employee into REVIEW - SOP 3 Gate V4: a title gap
            # does not reject a person who remains current.
            fallback_family = role_for(upstream["current_title"])
            if fallback_family:
                title, family = upstream["current_title"], fallback_family
        if status == "VALIDATED_PASS" and not family:
            status = "VALIDATED_REVIEW"
        suspicious = _disproof(con, pool_tavily, payload["full_name"], account.get("canonical_account_name", ""))
        if status == "VALIDATED_PASS" and suspicious:
            status = "VALIDATED_REVIEW"
        commercial, priority = _commercial(family, account.get("primary_use_case")) if family else ("NOT_MATERIALLY_RELEVANT", "P3")
        missing = None
        next_action = None
        if status == "VALIDATED_REVIEW":
            missing = "Resolve current US employment, exact function, or possible departure evidence"
            next_action = "Verify against a current official hospital bio, leadership page, or announcement"
        canonical_id = "CP-" + hashlib.sha256(payload["linkedin_profile_url"].lower().rstrip("/").encode()).hexdigest()[:16]
        existing = con.execute("SELECT person_id FROM validations WHERE canonical_person_id=? AND person_id<>?", (canonical_id, person_id)).fetchone()
        duplicate = "DUPLICATE" if existing else "UNIQUE"
        if existing:
            status, reason = "VALIDATED_REJECT", "P-R05_DUPLICATE_PERSON"
        upsert(con, "validations", {"person_id": person_id, "canonical_person_id": canonical_id,
            "account_id": account.get("account_id"), "linkedin_identity_status": "MATCHED" if profile else "AMBIGUOUS",
            "identity_confidence": "HIGH" if profile else "LOW", "current_employer": current["company"] if current else "UNKNOWN",
            "account_entity_match": "DIRECT_ACCOUNT_MATCH" if current else "CONFLICT", "role_scope": "FACILITY_LEVEL",
            "validated_current_title": title or "UNKNOWN", "validated_department": family or "UNKNOWN",
            "validated_role_family": family or "UNKNOWN", "current_role_status": "VERIFIED" if current else "UNKNOWN",
            "employment_status": employment, "primary_use_case": account.get("primary_use_case"),
            "validated_commercial_role": commercial, "problem_ownership_level": commercial,
            "evaluation_influence": "HIGH" if priority in {"P1","P2"} else "MEDIUM", "commercial_influence": "MEDIUM",
            "technical_influence": "HIGH" if commercial == "TECHNICAL_EVALUATOR" else "MEDIUM",
            "clinical_influence": "HIGH" if commercial in {"DIRECT_OWNER","CLINICAL_EVALUATOR"} else "MEDIUM",
            "internal_routing_value": "HIGH" if priority == "P3" else "MEDIUM",
            "original_priority": (upstream["initial_priority"] or "").replace("_CANDIDATE", ""), "validated_priority": priority,
            "priority_change_status": "UNCHANGED", "better_person_gap_found": 0, "return_to_sop2_required": 0,
            "duplicate_status": duplicate, "duplicate_of_person_id": existing["person_id"] if existing else None,
            "linkedin_activity_status": "UNKNOWN", "linkedin_activity_checked_at": now(),
            "linkedin_activity_source": "NOT_AVAILABLE", "activity_run_status": "NOT_RUN",
            "evidence_confidence": "STRONG" if status == "VALIDATED_PASS" else "MINIMUM",
            "conflict_status": "POSSIBLE_CONTRADICTION" if suspicious else "NONE", "missing_fact": missing,
            "why_it_matters": "SOP 3 requires confirmed current employment and function" if missing else None,
            "best_verification_source": "Official hospital leadership page or bio" if missing else None,
            "next_verification_action": next_action, "validation_status": status, "reject_reason_code": reason,
            "validator_id": "sop3-independent-deterministic-v1", "validated_at": now(),
            "qa_status": "CLEAN" if status == "VALIDATED_PASS" else "PENDING_HUMAN_QA",
            "handoff_ready": 1 if status == "VALIDATED_PASS" else 0, "review_value_score": 1 if suspicious else 0.5}, pk="person_id")
        if profile:
            ev_id = "EV-P3-" + person_id[-16:]
            upsert(con, "evidence", {"evidence_id": ev_id, "subject_type": "PERSON", "subject_id": person_id,
                "claim_key": "independent_current_employment", "claim_type": "FACT", "claim_value": employment,
                "source_url": payload["linkedin_profile_url"], "source_title": f"{payload['full_name']} current profile",
                "source_owner": "LinkedIn via Apify", "source_tier": "A2", "source_date": (profile or {}).get("scrapedAt"),
                "accessed_at": now(), "evidence_excerpt": json.dumps(current or profile, default=str)[:4000],
                "freshness_status": "CURRENT", "directness": "DIRECT", "verbatim_verified": 1}, pk="evidence_id")
        if upstream and current and upstream["current_title"] != title:
            log_correction(con, "PERSON", person_id, "current_title", upstream["current_title"], title,
                           "CORRECTION", "Independent current-profile validation", [f"EV-P3-{person_id[-16:]}"])
        con.execute("INSERT OR IGNORE INTO person_accounts VALUES (?,?)", (canonical_id, account.get("account_id")))
        con.commit()
        tally[{"VALIDATED_PASS":"pass","VALIDATED_REVIEW":"review","VALIDATED_REJECT":"reject"}[status]] += 1
    return tally


def _username_from_linkedin(url):
    m = re.search(r"linkedin\.com/in/([a-zA-Z0-9\-_%]+)", url or "")
    return m.group(1) if m else None


def _parse_post_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def check_activity_batch(con, validation_rows, pool_apify):
    """Reachability check (s13.4/s20): did this person react to anything on LinkedIn
    within ACTIVITY_WINDOW_DAYS? One actor run covers a chunk of people (free-tier runs are
    capped at 10 items, so one reaction per person, 8 people per run). The actor filters to
    the window itself via postedLimit, so a returned reaction means ACTIVE and none means
    INACTIVE. Deliberately separate from validate_batch: it costs real Apify budget on top
    of the employment/role validation, so callers opt in for the people who matter."""
    window = "3months" if ACTIVITY_WINDOW_DAYS <= 100 else "year"
    tally = {"active": 0, "inactive": 0, "unknown": 0}
    rows = [r for r in validation_rows if canonical_linkedin(r["linkedin_profile_url"])]
    tally["unknown"] += len(validation_rows) - len(rows)
    for i in range(0, len(rows), 8):
        chunk = rows[i:i + 8]
        urls = [canonical_linkedin(r["linkedin_profile_url"]) for r in chunk]
        try:
            items = run_actor(con, pool_apify, "harvestapi/linkedin-profile-reactions",
                              {"profiles": urls, "maxItems": 1, "postedLimit": window},
                              max_charge_usd=0.25, run_timeout_secs=300)
        except Exception as error:
            for r in chunk:
                upsert(con, "validations", {"person_id": r["person_id"],
                       "activity_run_status": f"ERROR: {str(error)[:200]}"}, pk="person_id")
            tally["unknown"] += len(chunk)
            continue
        latest = {}
        for it in items:
            who = canonical_linkedin(((it.get("actor") or {}).get("linkedinUrl") or "").split("?")[0])
            when = _parse_post_date(it.get("createdAt"))
            if who and when and (who not in latest or when > latest[who]):
                latest[who] = when
        for r, url in zip(chunk, urls):
            most_recent = latest.get(url)
            status = "ACTIVE" if most_recent else "INACTIVE"
            upsert(con, "validations", {"person_id": r["person_id"],
                "linkedin_activity_status": status,
                "linkedin_activity_source": f"harvestapi/linkedin-profile-reactions (reactions, last {window})",
                "linkedin_activity_checked_at": now(),
                "last_visible_reaction_date": most_recent.date().isoformat() if most_recent else None,
                "activity_run_status": "RUN"}, pk="person_id")
            tally["active" if status == "ACTIVE" else "inactive"] += 1
    return tally
