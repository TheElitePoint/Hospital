---
document_id: PIPELINE-ARCH-01
title: "Data Acquisition Pipeline — Architecture & Build Plan"
version: "0.1 (proposal)"
status: "For decision"
last_updated: "2026-09-15"
governed_by: "SOP 1-4 v1.0 (source of truth). Where this document and an SOP disagree, the SOP wins."
---

# 0. What this pipeline is actually solving

The SOPs are not a lead list spec. They are an **evidence-graph spec with gates**.
Every material claim must carry a URL, an excerpt, a date and a tier; every decision must
be traceable to claim IDs; and every stage must be independently re-runnable without
lowering thresholds to hit a count.

That has three consequences that drive the whole design:

1. **The store must hold one-to-many evidence per claim.** A spreadsheet row cannot do this.
2. **Expensive steps must sit behind cheap gates.** SOP 1 has explicit stop rules
   (A0 stop rule, A6 stop rule, A11 runs last). Spending an Apify credit before
   geography/archetype/inpatient checks have run is a direct SOP violation and the
   single biggest avoidable cost in the build.
3. **SOP 3 must not see SOP 2's reasoning.** Independence (SOP 3 §00.4) has to be enforced
   in code by masking fields on the payload, not by prompt politeness.

---

# 1. The one architectural disagreement to settle first

**Do not make Google Sheets the database.**

Sheets cannot represent `evidence[]`, `correction_log[]`, `related_account_ids[]`,
`fact_evidence_interpretation_decisions[]`, or the canonical-person → many-accounts
relationship in SOP 3 §14.3. Forcing them in produces JSON-in-a-cell, which kills every
QA query you will actually want to run ("show me every PASS whose Core Signal rests on a
single Tier B source older than 12 months").

**Proposed split:**

| Layer | Technology | Role |
|---|---|---|
| System of record | SQLite file (`hospitals.db`) in this folder, upgradeable to Postgres/Supabase if more than one person writes concurrently | Entities, evidence, decisions, correction log, run log, API cache |
| Human interface | Google Sheets (one spreadsheet, multiple tabs) | Review queue, QA sign-off, metrics dashboards, final exports |
| Sync | One-way DB → Sheets for machine-owned columns; one-way Sheets → DB for a small set of human-owned columns only | Prevents the classic "someone sorted a column and destroyed row alignment" failure |

Sheets stays the thing you and reviewers look at every day. It just stops being the thing
the pipeline trusts.

If you overrule this and want Sheets-only, it is buildable — but evidence becomes an
append-only tab with foreign keys and you lose relational QA. Say so and I will redesign
around it.

---

# 2. Candidate universe — replace the 500-row list

SOP 1 needs a complete, state-scoped inpatient universe for IN / OH / KY / TX / AL.
A hand-assembled 500-row name list gives you no `bed_count`, no CAH designation, no
canonical entity, and no dedupe key — which means Gate A0 (entity integrity) fails
constantly and expensively.

**Use CMS public data instead** (free, no scraping, no ToS exposure):

- **CMS Hospital General Information** — CCN, legal name, address, state, hospital type,
  ownership. Gives A1 (geography) and most of A3 (inpatient) for free.
- **CMS Provider of Services (POS) file** — certified bed counts and Critical Access
  Hospital designation. Gives `bed_count` and materially determines `account_archetype`
  (`CRITICAL_ACCESS` vs `RURAL_ACUTE` vs `COMMUNITY_ACUTE`) without a single API call.
- **CMS Cost Report (HCRIS)** — parent system / chain affiliation, which seeds
  `parent_system_name`, `facility_count` and the `REGIONAL_MULTI_SITE` archetype.

This makes Gates A0–A3 a **deterministic, zero-cost local join**. Your 500-row list becomes
an input to reconcile against, not the universe.

Estimated universe after filtering to short-term acute + CAH in the five states:
**roughly 1,000–1,100 facilities** (to be confirmed exactly in Step 1 — this number matters,
see §8).

---

# 3. Data model (SQLite)

```
accounts              account_id PK, canonical_account_name, facility_name, parent_system_name,
                      canonical_domain, state, city, account_archetype, bed_count, facility_count,
                      acute_site_count, ccn, primary_use_case, current_signal,
                      relationship_overlap_status, qualification_status, priority_class,
                      hard_exclusion_code, review_reason_code, reject_reason_code,
                      linkedin_company_url, linkedin_company_name, linkedin_industry,
                      linkedin_sector_status, why_operating_env, why_likely_problem,
                      why_commercial_route, negative_evidence_summary, handoff_ready,
                      pipeline_stage, stage_status, last_verified_at

account_signals       id PK, account_id FK, signal_type (CORE|SUPPORTING), signal_code
account_tech          account_id FK, field_name, status            -- §07.3 status fields
evidence              evidence_id PK, subject_type (ACCOUNT|PERSON), subject_id, claim_key,
                      claim_type (FACT|INFERENCE|HYPOTHESIS), claim_value, source_url,
                      source_title, source_owner, source_tier, source_date, accessed_at,
                      evidence_excerpt, freshness_status, directness, conflict_status
claim_links           id PK, subject_id, claim_key, evidence_id FK  -- many-to-many
fed_decisions         id PK, account_id FK, fact, interpretation, decision_impact, confidence
                      (+ join table to evidence_ids)

people                person_id PK, canonical_person_id, account_id FK, full_name,
                      linkedin_profile_url, current_title, current_company_display_name,
                      role_family, department, seniority_level, role_scope,
                      person_use_case_relevance, problem_ownership_level,
                      evaluation_influence, commercial_influence, technical_influence,
                      internal_routing_value, current_role_status,
                      profile_identity_confidence, initial_priority,
                      better_person_json, duplicate_status, person_status,
                      reject_reason_code, last_checked_at

validations           person_id FK, canonical_person_id, identity_confidence,
                      current_employer, account_entity_match, role_scope,
                      validated_current_title, validated_department, validated_role_family,
                      employment_status, validated_commercial_role, clinical_influence,
                      original_priority, validated_priority, priority_change_status,
                      priority_change_reason, better_person_gap_found, better_function,
                      return_to_sop2_required, linkedin_activity_status,
                      last_visible_reaction_date, linkedin_activity_checked_at,
                      linkedin_activity_source, conflict_status, validation_status,
                      reject_reason_code, validator_id, validated_at, handoff_ready

person_accounts       canonical_person_id, account_id     -- SOP 3 §14.3 system-level executives
correction_log        id PK, subject_id, field_name, old_value, new_value, change_type,
                      reason, evidence_ids, changed_at
golden                canonical_person_id PK, 8 component scores, golden_priority_score,
                      incremental_value, role_family_already_represented,
                      distinct_scope_value, buying_group_contribution, golden_eligible,
                      golden_rank, golden_status, golden_selection_reason,
                      golden_exclusion_reason, golden_locked_at, selection_cycle

api_cache             cache_key PK (sha256 of provider+query/url), provider, payload,
                      fetched_at, ttl_days
run_log               run_id PK, sop, subject_id, model, prompt_version, tokens, cost,
                      status, started_at, finished_at, error
```

`correction_log` is append-only and mandatory (SOP 3 §08) — no field is ever silently overwritten.

---

# 4. Google Sheets layout

One spreadsheet, tabs:

| Tab | Contents | Who writes |
|---|---|---|
| `00_Control` | cycle ID, run config, live counts by stage, shortage diagnostics | machine |
| `01_Universe` | CMS-derived candidate universe, dedupe keys, pipeline_stage | machine |
| `02_Accounts` | flat SOP 1 output per §07.1–07.2, one row per account | machine |
| `03_Account_Evidence` | every evidence row, FK to account, append-only | machine |
| `04_People` | SOP 2 output per §07 | machine |
| `05_Validation` | SOP 3 output per §07 | machine |
| `06_Correction_Log` | SOP 3 §08 change records | machine |
| `07_Golden` | SOP 4 output, all 8 component scores as separate visible columns | machine |
| `08_Review_Queue` | every REVIEW record + `missing_fact`, `why_it_matters`, `best_verification_source`, `exact_next_action` | machine writes rows, **human writes decision** |
| `09_Metrics` | SOP 1 §24 / SOP 2 §24 / SOP 3 §22 / SOP 4 §21 metric sets | machine |
| `10_Rejects` | rejects with controlled reason codes, for audit and pattern analysis | machine |

**Human-owned columns (the only ones synced back):** `qa_decision`, `qa_reviewer_id`,
`qa_notes`, `manual_override_status`, `override_reason`. A manual override without a
reason is refused by the sync job and flagged on `00_Control`.

Every machine tab carries a hidden stable `row_key` and is written with keyed batch updates,
never positional ones, so re-sorting in the UI cannot corrupt state.

Access: service-account JSON + `gspread`; the sheet is shared with the service account email.
(The Drive connector in this session can read/write files but not do cell-level Sheets
operations, so the service account is the right path.)

---

# 5. Stage machine and cost discipline

Every subject carries `pipeline_stage` ∈ {`UNIVERSE`, `SOP1`, `SOP2`, `SOP3`, `SOP4`} and
`stage_status` ∈ {`PENDING`, `RUNNING`, `PASS`, `REVIEW`, `REJECT`, `RETURNED`, `ERROR`}.
Runs are idempotent and keyed on `(subject_id, sop, prompt_version)` — a re-run skips
completed work unless `--force`. Every external call goes through `api_cache` first, so
re-running a stage after a prompt change costs nothing in scraping.

**SOP 1 execution order (strictly cheapest-first):**

| Step | Gate | Cost | Notes |
|---|---|---|---|
| 1 | A0 entity, A1 geography, A2 archetype, A3 inpatient | **£0** — local CMS join | Kills the majority of the universe for free |
| 2 | Tavily search pack (§10 query library, ~10 queries/account) + page fetch | low | Survivors only |
| 3 | Groq extraction → Core/Supporting signals, tech context, use case | low | Citation-validated (see §6) |
| 4 | **Mandatory negative-evidence search (§10.8)** | low | Non-skippable for any likely PASS |
| 5 | A4–A10 decision | £0 | |
| 6 | **A11 LinkedIn company page + industry (Apify)** | **highest per-unit** | Runs only after A0–A10 PASS, exactly as the SOP specifies |
| 7 | A12 final decision + reviewer card | £0 | |

Same principle in SOP 2/3: LinkedIn people-search runs only on PASS accounts, and the
activity check (SOP 3 §V9) runs only on people who survived V1–V8.

---

# 6. The part that actually determines data quality: the citation validator

An LLM asked to "classify signals with evidence" will happily emit a plausible
`CS_TELEMETRY_CARDIAC_MONITORING` with an invented excerpt. SOP 1 §21 forbids this, but
prompts do not enforce it. Code does.

Every model call returns strict JSON. A deterministic validator then rejects the response
unless **all** of the following hold:

1. Every signal, use case and status field cites ≥1 `evidence_id`.
2. Every cited `evidence_id` exists in the evidence table for that subject.
3. Every `evidence_excerpt` is a **verbatim substring of the fetched page text** — not
   a paraphrase. Fails → the claim is dropped, not repaired.
4. Tier is derived from the source domain by rule (hospital's own domain → A1/A2;
   Apollo/ZoomInfo/aggregator → C), never self-reported by the model.
5. A Supporting Signal citing the identical evidence row as the Core Signal is rejected
   unless the excerpt independently proves both facts (SOP 1 §03.6).
6. `claim_type` = `FACT` requires direct evidence; anything else is forced to `INFERENCE`.

Any claim failing validation is dropped and the record routes to `REVIEW` with a specific
`missing_fact` — never "needs more research" (SOP 1 §22).

**SOP 3 independence is enforced the same way:** the SOP 3 payload builder is a separate
function that emits only identity fields, raw evidence rows and account context. SOP 2's
`person_use_case_relevance`, `initial_priority`, `better_person_json` and reasoning text
are structurally absent from the payload. Different model and different prompt lineage from
SOP 2. The validator then compares SOP 3's independent conclusion against SOP 2's stored
one and writes the delta to `correction_log`.

**LinkedIn activity hard rule (SOP 3 §10.3):** `INACTIVE` is only written when the actor
run status is `SUCCEEDED`, the profile resolved, and the activity section parsed with zero
reactions in 12 months. Every other outcome — timeout, block, empty payload, parse failure
— writes `UNKNOWN`. This is a code branch, not a judgement call, because getting it wrong
silently corrupts SOP 4's reachability score.

---

# 7. SOP 4 is pure computation

No API calls. Load `VALIDATED_PASS`, apply the §01.1 eligibility checks as hard booleans,
compute the eight component scores, store each separately, rank with a stable sort key
built from the §20 tie-break tuple in order, apply the §05 marginal-value and buying-group
balance pass, then lock exactly 1,000 or emit a shortage diagnosis with controlled reason
codes. Deterministic and instantly re-runnable — which matters, because you will re-run it
every time a replacement is needed (§15).

---

# 8. The risk worth arguing about now, not in month two

**Will the five-state universe actually yield 1,000 Golden people?**

Rough funnel on ~1,050 facilities:

- SOP 1 PASS rate at the stated evidence bar: realistically **25–40%** → 260–420 accounts
- SOP 2 at 6–10 strong people per account → 1,800–3,400 people
- SOP 3 `VALIDATED_PASS` at 60–75% → 1,100–2,500 people
- SOP 4 Golden-eligible subset, after the §01.1 minimum standard → **plausibly above 1,000, but not by a comfortable margin**

If SOP 1's PASS rate lands nearer 20% — entirely possible, because the Core+Supporting+
use-case bar is genuinely strict and small hospitals publish very little — you will not
reach 1,000 from five states, and SOP 4 §07 correctly forbids lowering the bar to fix it.
The fix is a controlled geography expansion via SOP revision, and that decision has a long
lead time.

**So: run a 25-account calibration batch before building the full system.** It costs a day
and tells you the real PASS rate, the real REVIEW rate, and the real cost per PASS account.
Every downstream capacity decision depends on those three numbers, and guessing them is how
pipelines get built twice.

---

# 9. Build sequence

| Phase | Deliverable | Est. |
|---|---|---|
| 0 | Load CMS data, build the five-state universe, dedupe, confirm the real facility count | 0.5 day |
| 1 | SQLite schema + Sheets scaffold + two-way sync job + service-account auth | 1 day |
| 2 | SOP 1 Steps 1–5 (local gates, Tavily, Groq extraction, citation validator, negative evidence) | 2 days |
| 3 | **Calibration batch: 25 accounts, manual review of every decision against the SOP checklist** | 1 day |
| 4 | Gate A11 (Apify LinkedIn company + sector validation) + SOP 1 decision/card output | 1 day |
| 5 | SOP 2 people discovery, role-family mapping, better-person test, buying-group coverage | 2 days |
| 6 | SOP 3 independent validator (separate model/prompt, masked payload) + activity check + canonicalization | 2 days |
| 7 | SOP 4 scoring, ranking, balance review, lock, shortage diagnostics | 1 day |
| 8 | Metrics tabs, run log, reviewer workflow, replacement logic | 1 day |

Phase 3 is a real gate, not a formality. If the calibration batch shows a 15% PASS rate or
a 50% REVIEW rate, phases 4–8 get re-scoped before they get built.

---

# 10. Open decisions for you

1. **SQLite + Sheets view, or Sheets-only?** (§1 — recommend the former)
2. **CMS universe, or stay with the 500-row list?** (§2 — recommend CMS, keep your list as a reconciliation input)
3. **Which Apify actors** for (a) LinkedIn company page + industry, (b) people search by company, (c) profile activity/reactions — and is the Sales Navigator seat available, since it changes actor choice and cost materially?
4. **Model split:** Groq for high-volume extraction is right on cost; SOP 3's adversarial validation and the SOP 2 better-person test are the two places a stronger model likely pays for itself. Agree?
5. **Reviewer capacity:** how many REVIEW records per week can actually be cleared by a human? This caps throughput more than any API limit.
