"""Rule-based SOP 1 extraction (no LLM).

Same output schema as the Groq extractor in sop1.py, so everything downstream (citation
validator, gates, persistence) is unchanged. A signal fires only when a known phrase appears
within a window of the hospital's own distinctive name (or on a page whose host carries that
name), and the excerpt is the verbatim sentence that contains it - so the validator's
verbatim check holds by construction. Recall is lower than an LLM's; precision is held by
the proximity requirement and by the validator's tier and reuse rules.
"""
import re
from urllib.parse import urlparse

_GENERIC = {"hospital", "medical", "center", "centre", "health", "healthcare", "regional", "community", "memorial",
            "general", "university", "system", "systems", "saint", "the", "and", "of", "for", "inc", "llc", "campus",
            "clinic", "county", "district", "city", "state", "services", "care", "institute", "children", "childrens"}

CORE = [
    ("CS_TELE_ICU_VIRTUAL_CRITICAL_CARE", r"tele-?\s?icu|virtual (?:critical care|icu)|remote intensivist|\be-?icu\b"),
    ("CS_CENTRAL_MONITORING", r"central(?:ized|ised)? (?:patient )?(?:monitoring|surveillance)|command center|remote (?:patient )?monitoring (?:hub|center|unit)"),
    ("CS_TELEMETRY_CARDIAC_MONITORING", r"\btelemetry\b|cardiac monitoring|monitor tech(?:nician)?s?|\becg monitoring"),
    ("CS_DEVICE_EHR_INTEGRATION", r"medical device (?:integration|connectivity)|device (?:integration|connectivity)|device-to-ehr|physiologic (?:data|monitoring) integration|\bcapsule\b|\bbernoulli\b"),
]
CLIN_ENG = re.compile(r"clinical engineering|biomedical engineering|healthcare technology management|\bhtm\b", re.I)
MONITOR_NEAR = re.compile(r"monitor|telemetry|alarm", re.I)

SUPPORT = [
    ("SS_ACTIVE_MONITORING_PROJECT", r"(?:implement|deploy|install|upgrad|launch|roll(?:ed|ing)?\s?out|go-?live)\w*.{0,80}(?:monitoring|telemetry)|(?:monitoring|telemetry).{0,80}(?:implement|deploy|install|upgrad|launch|go-?live)"),
    ("SS_RELEVANT_HIRING", r"(?:telemetry|monitor tech\w*|biomed\w*|clinical engineer\w*|nursing informatic\w*|clinical informatic\w*).{0,80}(?:job|hiring|apply now|opening|career|position|vacanc)|(?:job|hiring|apply now|opening|career|position|vacanc)\w*.{0,80}(?:telemetry|monitor tech\w*|biomed\w*|clinical engineer\w*|nursing informatic\w*)"),
    ("SS_VIRTUAL_CARE_PROGRAM", r"virtual (?:nursing|care|hospital)|hospital at home|telehealth program|telemedicine program"),
    ("SS_EHR_OR_INTEGRATION_CHANGE", r"\b(?:epic|cerner|oracle health|meditech)\b.{0,80}(?:go-?live|implement|upgrade|migrat|transition|install)|(?:go-?live|implement|upgrade|migrat|transition).{0,80}\b(?:epic|cerner|oracle health|meditech)\b"),
    ("SS_RECENT_EXPANSION", r"(?:new|opens?|opened|opening|groundbreaking|expansion|expanding|construction of).{0,60}(?:tower|wing|pavilion|hospital|campus|unit|bed)"),
    ("SS_RECENT_ACQUISITION", r"\bacquir(?:ed|es|ing|ition)\b|\bmerger\b|\bmerged\b|\bjoins? (?:the )?[A-Z][\w ]{2,40} (?:health )?system"),
    ("SS_STAFFING_PRESSURE", r"(?:nurs\w+|staff\w*) shortage|staffing (?:crisis|challenge|pressure|shortage)"),
    ("SS_DOCUMENTATION_AUTOMATION", r"(?:automated|automatic) documentation|auto-?charting|ambient (?:documentation|listening)"),
    ("SS_MULTI_SITE", r"\b(?:\d+|two|three|four|five|six|seven|eight|nine|ten|several|multiple) (?:hospitals|campuses|facilities|locations)\b"),
]
USE_CASE_BY_CORE = [("CS_TELE_ICU_VIRTUAL_CRITICAL_CARE", "U4_REMOTE_SPECIALIST_TELE_ICU"),
                    ("CS_CENTRAL_MONITORING", "U3_CENTRALIZED_MONITORING"),
                    ("CS_TELEMETRY_CARDIAC_MONITORING", "U1_DIGITAL_RHYTHM_WORKFLOW"),
                    ("CS_DEVICE_EHR_INTEGRATION", "U2_DEVICE_EHR_INTEROPERABILITY"),
                    ("CS_CLINICAL_ENGINEERING_MONITORING", "U2_DEVICE_EHR_INTEROPERABILITY")]


def name_tokens(account_name):
    words = re.findall(r"[a-z]{4,}", (account_name or "").lower().replace("'", ""))
    toks = [w for w in words if w not in _GENERIC]
    return toks or words[:2]


def _sentence(text, start, end, limit=320):
    left = max(text.rfind(". ", 0, start), text.rfind("\n", 0, start))
    left = 0 if left < 0 else left + 1
    right_candidates = [i for i in (text.find(". ", end), text.find("\n", end)) if i != -1]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    sentence = text[left:right].strip()
    if len(sentence) > limit:                       # keep a verbatim slice centred on the match
        a = max(0, start - left - limit // 2)
        sentence = text[left:right][a:a + limit].strip()
    return sentence


def _near_name(text, start, end, tokens, host):
    if any(t in host for t in tokens):
        return True
    window = text[max(0, start - 600): end + 600].lower()
    return any(t in window for t in tokens)


def _scan(sources, tokens, patterns, skip_negative=True):
    """Yield (code, source, excerpt) for the first qualifying match of each pattern."""
    found = {}
    for code, pattern in patterns:
        rx = re.compile(pattern, re.I | re.S)
        for src in sources:
            if skip_negative and src.get("negative"):
                continue
            text, host = src.get("text") or "", urlparse(src["source_url"]).hostname or ""
            for m in rx.finditer(text):
                if not _near_name(text, m.start(), m.end(), tokens, host):
                    continue
                excerpt = _sentence(text, m.start(), m.end())
                if len(excerpt) >= 20:
                    found[code] = (src, excerpt)
                    break
            if code in found:
                break
    return found


def extract(account, sources):
    tokens = name_tokens(account["canonical_account_name"])
    core = _scan(sources, tokens, CORE)
    # Clinical engineering counts only when the same sentence talks about monitoring.
    if "CS_CLINICAL_ENGINEERING_MONITORING" not in core:
        for src in sources:
            if src.get("negative"):
                continue
            text, host = src.get("text") or "", urlparse(src["source_url"]).hostname or ""
            for m in CLIN_ENG.finditer(text):
                s = _sentence(text, m.start(), m.end())
                if MONITOR_NEAR.search(s) and _near_name(text, m.start(), m.end(), tokens, host):
                    core["CS_CLINICAL_ENGINEERING_MONITORING"] = (src, s)
                    break
            if "CS_CLINICAL_ENGINEERING_MONITORING" in core:
                break

    used = {(s["source_url"], e) for s, e in core.values()}
    support = {c: v for c, v in _scan(sources, tokens, SUPPORT).items() if (v[0]["source_url"], v[1]) not in used}

    use_case = {"code": "", "evidence_ids": [], "excerpt": "", "rationale": ""}
    for core_code, uc in USE_CASE_BY_CORE:
        if core_code in core:
            src, ex = core[core_code]
            use_case = {"code": uc, "evidence_ids": [src["evidence_id"]], "excerpt": ex,
                        "rationale": f"rule-based: {core_code}"}
            break

    if "SS_ACTIVE_MONITORING_PROJECT" in support:
        signal = "STRONG"
    elif {"SS_RELEVANT_HIRING", "SS_RECENT_ACQUISITION", "SS_VIRTUAL_CARE_PROGRAM", "SS_RECENT_EXPANSION"} & set(support):
        signal = "PRESENT"
    else:
        signal = "NONE_FOUND"

    domain = ""
    for src in sources:
        host = (urlparse(src["source_url"]).hostname or "").removeprefix("www.")
        if host and any(t in host for t in tokens) and not any(x in host for x in ("linkedin", "facebook", "indeed", "wikipedia", "beckers")):
            domain = host
            break

    def pack(items):
        return [{"code": c, "evidence_ids": [s["evidence_id"]], "excerpt": e} for c, (s, e) in items.items()]

    return {"core_signals": pack(core), "supporting_signals": pack(support), "primary_use_case": use_case,
            "secondary_use_cases": [], "current_signal": {"value": signal, "evidence_ids": [], "rationale": "rule-based"},
            "technology_context": {}, "core_problem_already_solved": False, "negative_evidence_summary": "",
            "parent_system_name": "", "canonical_domain": domain,
            "why_this_account": {"operating_environment": "", "likely_problem": "", "commercial_route": ""},
            "unresolved_material_fact": None}
