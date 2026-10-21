"""Citation validator - the quality guarantee of the whole pipeline.

A model asked to "classify signals with evidence" will emit a plausible signal with an
invented excerpt. SOP 1 s21 forbids this; prompts do not enforce it, code does.

Every model claim is dropped unless ALL hold:
  1. it cites >= 1 evidence_id
  2. every cited evidence_id exists for that subject
  3. the excerpt is a VERBATIM substring of the fetched page text (normalised whitespace)
  4. tier is derived from the source domain by rule, never self-reported (s08.2-08.5)
  5. a SUPPORTING signal may not reuse the CORE signal's only evidence row (s03.6)
  6. claim_type FACT requires DIRECT evidence, else it is downgraded to INFERENCE (s05)

Dropped claims do not get repaired. They route the record to REVIEW with a specific
missing_fact, never "needs more research" (s22).
"""
import re, datetime
from urllib.parse import urlparse

# --- s08 tier assignment by source, not by model self-report ---
DISCOVERY_DOMAINS = {
    "apollo.io", "zoominfo.com", "rocketreach.co", "linkedin.com", "crunchbase.com",
    "signalhire.com", "lusha.com", "leadiq.com", "contactout.com", "hunter.io",
    "bing.com", "google.com", "duckduckgo.com", "yelp.com", "healthgrades.com",
    "usnews.com", "ratemds.com", "indeed.com", "glassdoor.com", "ziprecruiter.com",
}
GOV_DOMAINS = (".gov", ".mil", "cms.gov", "hhs.gov", "cdc.gov")
PRESS_DOMAINS = {
    "beckershospitalreview.com", "healthcareitnews.com", "fiercehealthcare.com",
    "modernhealthcare.com", "healthcaredive.com", "himss.org", "aha.org",
    "chiefhealthcareexecutive.com", "healthleadersmedia.com",
}
JOB_PATH_HINTS = ("/careers", "/jobs", "/job/", "/employment", "workday", "icims", "taleo", "greenhouse")

NON_FACT_CLAIM_TYPES = {"INFERENCE", "HYPOTHESIS"}

def _host(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower().lstrip("www.")
    except Exception:
        return ""

def assign_tier(url: str, account_domain: str = None) -> str:
    """s08.2-08.5. Returns A1 | A2 | B | C."""
    host = _host(url)
    if not host:
        return "C"
    if any(host.endswith(g) or g in host for g in GOV_DOMAINS):
        return "A1"
    own = bool(account_domain) and (host.endswith(account_domain.lower()) or account_domain.lower() in host)
    if own:
        # official but time-sensitive surfaces are A2, durable pages are A1
        low = url.lower()
        if any(h in low for h in JOB_PATH_HINTS) or "/news" in low or "/press" in low or "/blog" in low:
            return "A2"
        return "A1"
    if host in DISCOVERY_DOMAINS or any(host.endswith("." + d) for d in DISCOVERY_DOMAINS):
        return "C"
    if host in PRESS_DOMAINS or any(host.endswith("." + d) for d in PRESS_DOMAINS):
        return "B"
    return "B"

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()

def excerpt_is_verbatim(excerpt: str, page_text: str) -> bool:
    """s08.8 - store the shortest excerpt that PROVES the claim. Paraphrase is not proof."""
    e, p = normalise(excerpt), normalise(page_text)
    if not e or not p or len(e) < 15:
        return False
    return e in p

def freshness(source_date: str, window_days: int = 365) -> str:
    if not source_date:
        return "UNKNOWN"
    try:
        d = datetime.date.fromisoformat(source_date[:10])
    except Exception:
        return "UNKNOWN"
    age = (datetime.date.today() - d).days
    return "CURRENT" if age <= window_days else "STALE"

class ValidationReport:
    def __init__(self):
        self.accepted = []      # claims that survived
        self.dropped = []       # (claim_key, reason)
        self.evidence = []      # evidence rows to persist
        self.downgraded = []    # (claim_key, FACT -> INFERENCE)

    @property
    def ok(self):
        return not self.dropped

    def drop(self, claim_key, reason):
        self.dropped.append((claim_key, reason))

    def missing_fact(self):
        """The specific, resolvable gap required by s22 - never 'needs more research'."""
        if not self.dropped:
            return None
        parts = [f"{k}: {r}" for k, r in self.dropped[:3]]
        return "; ".join(parts)

def validate_claims(claims, evidence_index, pages, account_domain=None):
    """claims: [{claim_key, claim_class, claim_value, claim_type, evidence_ids[]}]
    evidence_index: {evidence_id: {source_url, evidence_excerpt, source_date, ...}}
    pages: {source_url: fetched_page_text}
    """
    report = ValidationReport()
    core_evidence_used = set()

    ordered = sorted(claims, key=lambda c: 0 if c.get("claim_class") == "CORE" else 1)

    for claim in ordered:
        ck = claim.get("claim_key") or "unknown_claim"
        eids = [e for e in (claim.get("evidence_ids") or []) if e]

        # Rule 1
        if not eids:
            report.drop(ck, "no evidence cited")
            continue

        good_eids = []
        for eid in eids:
            ev = evidence_index.get(eid)
            # Rule 2
            if not ev:
                report.drop(ck, f"cited evidence {eid} does not exist")
                continue
            url = ev.get("source_url", "")
            page_text = pages.get(url, "")
            # Rule 3
            if not excerpt_is_verbatim(ev.get("evidence_excerpt", ""), page_text):
                report.drop(ck, f"excerpt for {eid} is not verbatim in {url or 'source'}")
                continue
            # Rule 4
            ev["source_tier"] = assign_tier(url, account_domain)
            ev["freshness_status"] = freshness(ev.get("source_date"))
            ev["verbatim_verified"] = 1
            good_eids.append(eid)

        if not good_eids:
            continue

        # Rule 5. s03.6 is about the evidence RECORD, not the row id: the same source with a
        # genuinely different excerpt proving a second fact is allowed, the identical
        # source+excerpt is not. Compare on (url, normalised excerpt).
        def _fingerprints(eids):
            return {(evidence_index[e].get("source_url"),
                     normalise(evidence_index[e].get("evidence_excerpt", ""))) for e in eids}
        fps = _fingerprints(good_eids)
        if claim.get("claim_class") == "SUPPORTING":
            if fps and fps.issubset(core_evidence_used):
                report.drop(ck, "supporting signal reuses the core signal's only evidence (s03.6)")
                continue
        if claim.get("claim_class") == "CORE":
            core_evidence_used.update(fps)

        # Rule 6
        claim_type = claim.get("claim_type", "FACT")
        tiers = {evidence_index[e].get("source_tier") for e in good_eids}
        directness = {evidence_index[e].get("directness", "DIRECT") for e in good_eids}
        if claim_type == "FACT" and ("DIRECT" not in directness or tiers <= {"C"}):
            claim_type = "INFERENCE"
            report.downgraded.append((ck, "FACT->INFERENCE: no direct non-discovery evidence"))
        claim["claim_type"] = claim_type
        claim["evidence_ids"] = good_eids
        report.accepted.append(claim)
        for e in good_eids:
            if evidence_index[e] not in report.evidence:
                report.evidence.append(evidence_index[e])

    return report

def tier_c_only(report) -> bool:
    """s08.5 / Gate A8 - Tier C alone cannot carry a material PASS claim."""
    tiers = {e.get("source_tier") for e in report.evidence}
    return bool(tiers) and tiers <= {"C"}
