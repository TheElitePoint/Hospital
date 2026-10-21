"""SOP 4 - Golden 1,000 Selection & Final Validation.

Pure computation. No API calls, fully deterministic, instantly re-runnable - which
matters because every post-lock replacement (s15) re-runs it.

Non-negotiables encoded here:
  - only VALIDATED_PASS + handoff_ready may compete (s01.1); ineligibility is recorded
    with a reason, never silently dropped
  - all eight component scores are STORED SEPARATELY (s03, s22 "no black-box score")
  - counting is by canonical_person_id, never by row (s00.4)
  - LinkedIn activity is 5 of 100 and the LAST tie-break (s13.4, s20)
  - if fewer than the target meet the standard, the standard does NOT move (s06 G10)
"""
import hashlib, json, itertools
from .db import now

TARGET = 1000

ACCOUNT_QUALITY = {"A_PRIORITY": 20, "B_PRIORITY": 15, "PASS_UNRANKED": 14}
USE_CASE_STRENGTH = {"DIRECT_CURRENT": 15, "DIRECT_STRUCTURAL": 12, "CREDIBLE_SUPPORTED": 9}
PROBLEM_OWNERSHIP = {"DIRECT_OWNER": 20, "CO_OWNER": 18, "CLINICAL_EVALUATOR": 15,
                     "TECHNICAL_EVALUATOR": 15, "EXECUTIVE_SPONSOR": 11, "INTERNAL_ROUTE": 7}
INFLUENCE = {"HIGH": 15, "MEDIUM": 10, "LOW": 5}
PRIORITY = {"P1": 10, "P2": 7, "P3": 4}
CURRENT_SIGNAL = {"STRONG": 8, "PRESENT": 5, "NONE_FOUND": 2}
EVIDENCE_CONF = {"STRONG": 7, "SUFFICIENT": 5, "MINIMUM": 3}
REACHABILITY = {"ACTIVE": 5, "INACTIVE": 2, "UNKNOWN": 1}

VALID_COMMERCIAL_ROLES = set(PROBLEM_OWNERSHIP)
VALID_ACTIVITY = set(REACHABILITY)
ACTIVITY_REQUIRED_FROM = "2026-10-05"

# s12 - role families that matter per use case, used for buying-group balance
USE_CASE_ROLE_PRIORITY = {
 "U1_DIGITAL_RHYTHM_WORKFLOW": ["TELEMETRY_CARDIAC_MONITORING","NURSING_EXECUTIVE","NURSING_INFORMATICS",
                                "CLINICAL_ENGINEERING_HTM","IT_CIO","CLINICAL_SYSTEMS_INTEGRATION"],
 "U2_DEVICE_EHR_INTEROPERABILITY": ["CLINICAL_ENGINEERING_HTM","CLINICAL_SYSTEMS_INTEGRATION","IT_CIO",
                                    "CLINICAL_INFORMATICS","NURSING_INFORMATICS"],
 "U3_CENTRALIZED_MONITORING": ["TELEMETRY_CARDIAC_MONITORING","NURSING_EXECUTIVE","VIRTUAL_CARE_TELEHEALTH",
                               "CLINICAL_ENGINEERING_HTM","IT_CIO","CLINICAL_OPERATIONS"],
 "U4_REMOTE_SPECIALIST_TELE_ICU": ["VIRTUAL_CARE_TELEHEALTH","NURSING_EXECUTIVE","CRITICAL_CARE_LEADERSHIP",
                                   "CLINICAL_INFORMATICS","IT_CIO","CLINICAL_OPERATIONS"],
 "U5_AUTOMATED_DOCUMENTATION": ["NURSING_INFORMATICS","TELEMETRY_CARDIAC_MONITORING",
                                "CLINICAL_SYSTEMS_INTEGRATION","CLINICAL_INFORMATICS","NURSING_EXECUTIVE"],
}

SHORTAGE_BY_ROLE = {
    "DIRECT_OWNER": "SHORTAGE_DIRECT_OWNERS",
    "TECHNICAL_EVALUATOR": "SHORTAGE_TECHNICAL_EVALUATORS",
    "CLINICAL_EVALUATOR": "SHORTAGE_CLINICAL_STAKEHOLDERS",
}

def eligibility(rec):
    """s01.1 mandatory Golden conditions. Returns (bool, reason_or_None)."""
    if rec.get("validation_status") != "VALIDATED_PASS":
        return False, "NOT_VALIDATED_PASS"
    if not rec.get("handoff_ready"):
        return False, "NOT_HANDOFF_READY"
    if not rec.get("canonical_person_id"):
        return False, "NO_CANONICAL_PERSON_ID"
    if rec.get("employment_status") != "CURRENT_CONFIRMED":
        return False, "EMPLOYMENT_NOT_CONFIRMED"   # s07.3 CURRENT_PROBABLE cannot pass
    if rec.get("account_entity_match") not in {"DIRECT_ACCOUNT_MATCH","PARENT_SYSTEM_MATCH","MULTI_FACILITY_MATCH"}:
        return False, "ENTITY_MATCH_INVALID"
    if not rec.get("validated_current_title"):
        return False, "TITLE_NOT_VALIDATED"
    if rec.get("role_scope") not in {"SYSTEM_LEVEL","MULTI_FACILITY","FACILITY_LEVEL"}:
        return False, "ROLE_SCOPE_INVALID"
    if rec.get("primary_use_case") not in USE_CASE_ROLE_PRIORITY:
        return False, "USE_CASE_INVALID"
    if rec.get("validated_commercial_role") not in VALID_COMMERCIAL_ROLES:
        return False, "COMMERCIAL_ROLE_INVALID"
    if rec.get("validated_priority") not in PRIORITY:
        return False, "PRIORITY_INVALID"
    if rec.get("conflict_status") == "UNRESOLVED":
        return False, "UNRESOLVED_MATERIAL_CONFLICT"
    if not rec.get("linkedin_profile_url"):
        return False, "LINKEDIN_PROFILE_MISSING"
    if rec.get("linkedin_activity_status") not in VALID_ACTIVITY:
        return False, "ACTIVITY_STATUS_INVALID"
    if rec.get("duplicate_status") not in {"UNIQUE", "SYSTEM_LEVEL_SHARED_PERSON"}:
        return False, "DUPLICATE_ROW"
    # User rule: people added from this date on need a LinkedIn reaction in the last 90
    # days. The earlier golden set was validated before the rule and is left as it was.
    if (rec.get("validated_at") or "") >= ACTIVITY_REQUIRED_FROM and rec.get("linkedin_activity_status") not in ("ACTIVE", "INACTIVE"):  # INACTIVE allowed per user 2026-10-15 (lower gates); UNKNOWN/error still blocked
        return False, "NO_ACTIVITY_IN_90_DAYS"
    return True, None

def score(rec):
    """s03. Every component stays visible - s22 forbids a single black-box number."""
    s = {
      "account_quality_score":      ACCOUNT_QUALITY.get(rec.get("account_priority"), 0),
      "use_case_strength_score":    USE_CASE_STRENGTH.get(rec.get("use_case_evidence_class"), 9),
      "problem_ownership_score":    PROBLEM_OWNERSHIP.get(rec.get("validated_commercial_role"), 0),
      "commercial_influence_score": INFLUENCE.get(rec.get("commercial_influence"), 5),
      "validated_priority_score":   PRIORITY.get(rec.get("validated_priority"), 0),
      "current_signal_score":       CURRENT_SIGNAL.get(rec.get("current_signal"), 2),
      "evidence_confidence_score":  EVIDENCE_CONF.get(rec.get("evidence_confidence"), 3),
      "linkedin_reachability_score":REACHABILITY.get(rec.get("linkedin_activity_status"), 1),
    }
    s["golden_priority_score"] = sum(s.values())
    return s

INCREMENTAL_RANK = {"HIGH_INCREMENTAL_VALUE": 2, "MEDIUM_INCREMENTAL_VALUE": 1, "LOW_INCREMENTAL_VALUE": 0}

def assign_incremental_value(account_records):
    """s05.4 / Gate G6, computed per account in descending score order.

    First person from a role family is HIGH. A later person from the SAME family is
    MEDIUM only when their scope genuinely differs (s05.3 facility vs system), else LOW.
    """
    # deterministic: score desc, then canonical id. Without the id tiebreak, two people
    # on an equal score inside one account would take HIGH/LOW incremental value by
    # input order, which silently changes the global ranking.
    ranked = sorted(account_records,
                    key=lambda r: (-r["scores"]["golden_priority_score"],
                                   r.get("canonical_person_id") or ""))
    seen_family = {}
    for r in ranked:
        fam = r.get("validated_role_family")
        scope = r.get("role_scope")
        if fam not in seen_family:
            r["incremental_value"] = "HIGH_INCREMENTAL_VALUE"
            r["role_family_already_represented"] = 0
            r["distinct_scope_value"] = scope or ""
            r["buying_group_contribution"] = f"first {fam} for the account"
            seen_family[fam] = {scope}
        else:
            r["role_family_already_represented"] = 1
            if scope and scope not in seen_family[fam]:
                r["incremental_value"] = "MEDIUM_INCREMENTAL_VALUE"
                r["buying_group_contribution"] = f"{fam} at distinct scope ({scope})"
                seen_family[fam].add(scope)
            else:
                r["incremental_value"] = "LOW_INCREMENTAL_VALUE"
                r["buying_group_contribution"] = f"duplicates {fam} at same scope"
    return ranked

def sort_key(r):
    """s20 tie-break order, applied strictly and with nothing hidden."""
    s = r["scores"]
    return (
      -s["golden_priority_score"],
      -s["problem_ownership_score"],
      -s["account_quality_score"],
      -s["use_case_strength_score"],
      -s["validated_priority_score"],
      -s["commercial_influence_score"],
      -INCREMENTAL_RANK.get(r.get("incremental_value"), 0),
      -s["current_signal_score"],
      -s["evidence_confidence_score"],
      -s["linkedin_reachability_score"],
      r.get("canonical_person_id") or "",     # final determinism, never a preference
    )

def canonicalise(records):
    """s00.4 - one human is one row. Keeps the highest-scoring row per canonical person
    and attaches the other account ids rather than counting the person twice."""
    by_person = {}
    for r in records:
        cid = r["canonical_person_id"]
        if cid not in by_person:
            r["related_account_ids"] = [r.get("account_id")]
            by_person[cid] = r
        else:
            keep = by_person[cid]
            keep.setdefault("related_account_ids", [keep.get("account_id")])
            if r.get("account_id") not in keep["related_account_ids"]:
                keep["related_account_ids"].append(r.get("account_id"))
            if r["scores"]["golden_priority_score"] > keep["scores"]["golden_priority_score"]:
                r["related_account_ids"] = keep["related_account_ids"]
                by_person[cid] = r
    return list(by_person.values())

def balance_review(selected, pool_by_account):
    """Gate G8. Flags, for human QA (s19), selection patterns the SOP calls out -
    it does not silently reorder, because s08 forbids hidden preference."""
    flags = []
    by_account = {}
    for r in selected:
        by_account.setdefault(r.get("account_id"), []).append(r)
    for acct, rows in by_account.items():
        fams = [r.get("validated_role_family") for r in rows]
        for fam in set(fams):
            if fams.count(fam) > 2:
                flags.append({"account_id": acct, "flag": "SAME_FUNCTION_CONCENTRATION",
                              "detail": f"{fams.count(fam)} x {fam}"})
        low = [r for r in rows if r.get("incremental_value") == "LOW_INCREMENTAL_VALUE"]
        if low:
            flags.append({"account_id": acct, "flag": "LOW_INCREMENTAL_VALUE_SELECTED",
                          "detail": f"{len(low)} row(s)"})
        routes = [r for r in rows if r.get("validated_commercial_role") == "INTERNAL_ROUTE"]
        owners = [r for r in rows if r.get("validated_commercial_role") in ("DIRECT_OWNER","CO_OWNER")]
        if routes and owners:
            flags.append({"account_id": acct, "flag": "INTERNAL_ROUTE_WITH_STRONGER_OWNER",
                          "detail": f"{len(routes)} internal route(s)"})   # s01.2 / s19
        p3 = [r for r in rows if r.get("validated_priority") == "P3"]
        unselected_p1 = [r for r in pool_by_account.get(acct, [])
                         if r.get("validated_priority") == "P1" and r not in selected]
        if p3 and unselected_p1:
            flags.append({"account_id": acct, "flag": "P3_SELECTED_OVER_P1",
                          "detail": f"{len(p3)} P3 in, {len(unselected_p1)} P1 out"})
    return flags

def diagnose_shortage(eligible, target):
    """s07 - say what quality gap exists, never 'find more people'."""
    reasons = []
    if not eligible:
        return ["SHORTAGE_OTHER"]
    roles = [r.get("validated_commercial_role") for r in eligible]
    for role, code in SHORTAGE_BY_ROLE.items():
        share = roles.count(role) / max(len(eligible), 1)
        if share < 0.15:
            reasons.append(code)
    accounts = {r.get("account_id") for r in eligible}
    if len(accounts) * 6 < target:
        reasons.append("SHORTAGE_HIGH_FIT_ACCOUNTS")
    ucs = {r.get("primary_use_case") for r in eligible}
    if len(ucs) <= 2:
        reasons.append("SHORTAGE_USE_CASE_DIVERSITY")
    probable = [r for r in eligible if r.get("employment_status") == "CURRENT_PROBABLE"]
    if probable:
        reasons.append("SHORTAGE_VALIDATED_CURRENT_ROLES")
    return reasons or ["SHORTAGE_OTHER"]

def select(records, target=TARGET, cycle=None):
    """Full G0-G10 run. records: dicts merging validation + account context."""
    cycle = cycle or f"CYCLE-{now()[:10]}"
    eligible, ineligible = [], []
    for r in records:
        ok, reason = eligibility(r)
        r["scores"] = score(r)
        if ok:
            r["golden_eligible"] = 1
            eligible.append(r)
        else:
            r["golden_eligible"] = 0
            r["golden_ineligible_reason"] = reason
            ineligible.append(r)

    eligible = canonicalise(eligible)                       # G1
    by_account = {}
    for r in eligible:
        by_account.setdefault(r.get("account_id"), []).append(r)
    for acct, rows in by_account.items():
        assign_incremental_value(rows)                      # G6

    ranked = sorted(eligible, key=sort_key)                 # G7
    for i, r in enumerate(ranked, 1):
        r["golden_rank"] = i

    shortage, shortage_reasons = "NONE", []
    if len(ranked) >= target:
        selected = ranked[:target]
        not_selected = ranked[target:]
    else:
        selected = ranked                                   # G10 - standard does not move
        not_selected = []
        shortage = "SHORTAGE"
        shortage_reasons = diagnose_shortage(ranked, target)

    for r in selected:
        r["golden_status"] = "GOLDEN_SELECTED"
        r["golden_selection_reason"] = selection_reason(r)
        r["golden_locked_at"] = now()
    for r in not_selected:
        r["golden_status"] = "ELIGIBLE_NOT_SELECTED"
        r["golden_exclusion_reason"] = exclusion_reason(r)

    flags = balance_review(selected, by_account)             # G8

    summary = {
      "selection_cycle": cycle,
      "validated_input_unique_people": len({r.get("canonical_person_id") for r in records}),
      "golden_eligible_unique_people": len(ranked),
      "golden_selected_unique_people": len(selected),
      "golden_person_ids": [r["canonical_person_id"] for r in selected],
      "shortage_status": shortage,
      "shortage_reasons": shortage_reasons,
      "return_to_sop3_count": sum(1 for r in records if r.get("workflow_status") == "RETURN_TO_SOP3"),
      "balance_flags": flags,
      "human_qa_required": bool(flags),
      "locked_at": now() if shortage == "NONE" else None,
      "qa_status": "PENDING_HUMAN_QA" if flags else "CLEAN",
    }
    return selected, not_selected, ineligible, summary

def selection_reason(r):
    """s10 format: account strength + ownership + use-case relevance + timing/reachability."""
    bits = [f"{(r.get('account_priority') or '').replace('_',' ').lower()} {r.get('account_archetype','').replace('_',' ').lower()}".strip(),
            f"{(r.get('validated_commercial_role') or '').replace('_',' ').lower()} for {r.get('primary_use_case')}",
            r.get("validated_priority") or ""]
    sig = r.get("current_signal")
    if sig and sig != "NONE_FOUND":
        bits.append(f"{sig.lower()} current signal")
    if r.get("linkedin_activity_status") == "ACTIVE":
        bits.append("active LinkedIn")
    return "; ".join(b for b in bits if b)

def exclusion_reason(r):
    if r.get("incremental_value") == "LOW_INCREMENTAL_VALUE":
        return "LOW_INCREMENTAL_ACCOUNT_VALUE"
    if r.get("role_family_already_represented"):
        return "SAME_FUNCTION_ALREADY_STRONGLY_COVERED"
    if r.get("validated_priority") == "P3":
        return "P3_DISPLACED_BY_DIRECT_OWNER"
    if r.get("account_priority") == "PASS_UNRANKED":
        return "LOWER_ACCOUNT_PRIORITY"
    return "LOWER_GLOBAL_RANK"


def persist(con, selected, not_selected, ineligible, summary):
    """Write the cycle to the system of record. Component scores are stored separately."""
    from .db import upsert
    cycle = summary["selection_cycle"]
    for bucket in (selected, not_selected, ineligible):
        for r in bucket:
            s = r.get("scores", {})
            upsert(con, "golden", {
              "canonical_person_id": r["canonical_person_id"],
              "person_id": r.get("person_id"), "account_id": r.get("account_id"),
              "full_name": r.get("full_name"), "linkedin_profile_url": r.get("linkedin_profile_url"),
              "validated_current_title": r.get("validated_current_title"),
              "validated_department": r.get("validated_department"),
              "validated_role_family": r.get("validated_role_family"),
              "role_scope": r.get("role_scope"),
              "validated_commercial_role": r.get("validated_commercial_role"),
              "validated_priority": r.get("validated_priority"),
              "account_priority": r.get("account_priority"),
              "account_archetype": r.get("account_archetype"),
              "primary_use_case": r.get("primary_use_case"),
              "current_signal": r.get("current_signal"),
              "linkedin_activity_status": r.get("linkedin_activity_status"),
              "last_visible_reaction_date": r.get("last_visible_reaction_date"),
              "account_quality_score": s.get("account_quality_score"),
              "use_case_strength_score": s.get("use_case_strength_score"),
              "problem_ownership_score": s.get("problem_ownership_score"),
              "commercial_influence_score": s.get("commercial_influence_score"),
              "validated_priority_score": s.get("validated_priority_score"),
              "current_signal_score": s.get("current_signal_score"),
              "evidence_confidence_score": s.get("evidence_confidence_score"),
              "linkedin_reachability_score": s.get("linkedin_reachability_score"),
              "golden_priority_score": s.get("golden_priority_score"),
              "incremental_value": r.get("incremental_value"),
              "role_family_already_represented": r.get("role_family_already_represented", 0),
              "distinct_scope_value": r.get("distinct_scope_value"),
              "buying_group_contribution": r.get("buying_group_contribution"),
              "golden_eligible": r.get("golden_eligible", 0),
              "golden_ineligible_reason": r.get("golden_ineligible_reason"),
              "golden_rank": r.get("golden_rank"),
              "golden_status": r.get("golden_status", "NOT_ELIGIBLE"),
              "golden_selection_reason": r.get("golden_selection_reason"),
              "golden_exclusion_reason": r.get("golden_exclusion_reason"),
              "selection_cycle": cycle,
              "golden_locked_at": r.get("golden_locked_at"),
              "qualification_tier": r.get("qualification_tier", "SOP3_VALIDATED"),
            }, pk="canonical_person_id")
            for acct in r.get("related_account_ids", []) or []:
                con.execute("INSERT OR IGNORE INTO person_accounts VALUES (?,?)",
                            (r["canonical_person_id"], acct))
    upsert(con, "golden_cycles", {
      "selection_cycle": cycle,
      "validated_input_unique_people": summary["validated_input_unique_people"],
      "golden_eligible_unique_people": summary["golden_eligible_unique_people"],
      "golden_selected_unique_people": summary["golden_selected_unique_people"],
      "shortage_status": summary["shortage_status"],
      "shortage_reasons": json.dumps(summary["shortage_reasons"]),
      "return_to_sop3_count": summary["return_to_sop3_count"],
      "locked_at": summary["locked_at"], "qa_status": summary["qa_status"],
    }, pk="selection_cycle")
    con.commit()

def load_candidates(con):
    """Join SOP 3 validations with SOP 1 account context into SOP 4 input records.

    Excludes accounts a user has explicitly BLOCKED (e.g. an existing customer, a
    do-not-contact request) - checked live against the account's current status on
    every call, since SOP4 is fully re-runnable and a block must stick even for a
    person who was already scored in an earlier cycle."""
    rows = con.execute("""
      SELECT v.*, p.full_name, p.linkedin_profile_url,
             a.priority_class AS account_priority, a.account_archetype,
             a.current_signal, a.canonical_account_name
      FROM validations v
      JOIN people p ON p.person_id = v.person_id
      LEFT JOIN accounts a ON a.account_id = v.account_id
      WHERE a.qualification_status IS NULL OR a.qualification_status != 'BLOCKED'
    """).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["use_case_evidence_class"] = d.get("evidence_confidence_class") or _use_case_class(d)
        out.append(d)
    return out

def _use_case_class(d):
    """s03.2 mapping from stored SOP 1 evidence. Never invent a stronger use case here."""
    sig = d.get("current_signal")
    conf = d.get("evidence_confidence")
    if conf == "STRONG" and sig in ("STRONG", "PRESENT"):
        return "DIRECT_CURRENT"
    if conf in ("STRONG", "SUFFICIENT"):
        return "DIRECT_STRUCTURAL"
    return "CREDIBLE_SUPPORTED"


# ---------- SOP2-only tier: explicit, user-approved relaxation ----------
#
# The functions below are a deliberate exception to "only VALIDATED_PASS + handoff_ready
# may compete" (s01.1). They exist because the user explicitly chose, after being told
# what it costs, to accept SOP2's name+LinkedIn+company match alone as "qualified"
# rather than wait for SOP3's independent employment/role confirmation. Every row this
# produces is tagged qualification_tier='SOP2_ONLY_UNVALIDATED' in the golden table -
# never silently merged into the SOP3_VALIDATED tier - and select_sop2_only() only ever
# tops up a shortfall AFTER the fully-validated pool is exhausted, so a validated person
# is never displaced by an unvalidated one.

def sop2_only_eligibility(rec):
    """The reduced bar the user asked for: a name, a LinkedIn profile, and a matched
    company/account - nothing about current employment, role correctness, or conflicts
    is confirmed independently."""
    if not rec.get("full_name") or rec.get("full_name") == "UNKNOWN":
        return False, "NAME_MISSING"
    if not rec.get("linkedin_profile_url"):
        return False, "LINKEDIN_PROFILE_MISSING"
    if not rec.get("account_id"):
        return False, "ACCOUNT_MATCH_MISSING"
    if rec.get("person_status") != "PERSON_PASS":
        return False, "NOT_PERSON_PASS"
    if rec.get("duplicate_status") not in (None, "UNIQUE"):
        return False, "DUPLICATE_ROW"
    return True, None

def load_sop2_only_candidates(con, exclude_canonical_ids=()):
    """SOP2 people who passed discovery but have no SOP3 VALIDATED_PASS row (either
    never validated, or validated and rejected/reviewed - SOP3's own verdict on a
    person it actually examined is never overridden by this weaker tier)."""
    rows = con.execute("""
      SELECT p.*, a.priority_class AS account_priority, a.account_archetype,
             a.current_signal, a.canonical_account_name
      FROM people p
      LEFT JOIN accounts a ON a.account_id = p.account_id
      WHERE p.person_status='PERSON_PASS'
        AND NOT EXISTS (SELECT 1 FROM validations v WHERE v.person_id = p.person_id)
        AND (a.qualification_status IS NULL OR a.qualification_status != 'BLOCKED')
    """).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        url = (d.get("linkedin_profile_url") or "").lower().rstrip("/")
        d["canonical_person_id"] = "CP-" + hashlib.sha256(url.encode()).hexdigest()[:16] if url else None
        if d["canonical_person_id"] in exclude_canonical_ids:
            continue
        d["validated_current_title"] = d.get("current_title")
        d["validated_department"] = d.get("department")
        d["validated_role_family"] = d.get("role_family")
        d["validated_commercial_role"] = d.get("problem_ownership_level")
        d["validated_priority"] = (d.get("initial_priority") or "").replace("_CANDIDATE", "")
        d["use_case_evidence_class"] = _use_case_class(d)
        d["evidence_confidence"] = "MINIMUM"          # never independently confirmed
        d["linkedin_activity_status"] = "UNKNOWN"
        out.append(d)
    return out

def select_sop2_only(records, target, already_selected_canonical_ids, cycle=None):
    """Top up a shortfall from the SOP2-only pool alone. Never called with the SOP3
    pool mixed in - the fully-validated tier is always selected and locked first."""
    cycle = cycle or f"CYCLE-{now()[:10]}"
    eligible, ineligible = [], []
    for r in records:
        ok, reason = sop2_only_eligibility(r)
        r["scores"] = score(r)
        r["qualification_tier"] = "SOP2_ONLY_UNVALIDATED"
        if ok and r["canonical_person_id"] not in already_selected_canonical_ids:
            r["golden_eligible"] = 1
            eligible.append(r)
        else:
            r["golden_eligible"] = 0
            r["golden_ineligible_reason"] = reason or "ALREADY_SELECTED_VIA_SOP3"
            ineligible.append(r)

    eligible = canonicalise(eligible)
    by_account = {}
    for r in eligible:
        by_account.setdefault(r.get("account_id"), []).append(r)
    for rows in by_account.values():
        assign_incremental_value(rows)

    ranked = sorted(eligible, key=sort_key)
    selected = ranked[:target]
    not_selected = ranked[target:]
    for i, r in enumerate(selected, 1):
        r["golden_rank"] = i
        r["golden_status"] = "GOLDEN_SELECTED"
        r["golden_selection_reason"] = "SOP2-only: name + LinkedIn + company match, not independently validated"
        r["golden_locked_at"] = now()
    for r in not_selected:
        r["golden_status"] = "ELIGIBLE_NOT_SELECTED"
        r["golden_exclusion_reason"] = "LOWER_GLOBAL_RANK"

    summary = {
      "selection_cycle": cycle, "validated_input_unique_people": len(records),
      "golden_eligible_unique_people": len(ranked), "golden_selected_unique_people": len(selected),
      "golden_person_ids": [r["canonical_person_id"] for r in selected],
      "shortage_status": "NONE" if len(selected) >= target else "SHORTAGE",
      "shortage_reasons": [] if len(selected) >= target else ["SHORTAGE_OTHER"],
      "return_to_sop3_count": 0, "balance_flags": [], "human_qa_required": True,
      "locked_at": None, "qa_status": "PENDING_HUMAN_QA",
    }
    return selected, not_selected, ineligible, summary
