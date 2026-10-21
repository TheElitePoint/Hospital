---
document_id: SOP-03-INDEPENDENT-PERSON-VALIDATION-DATA-QA
document_type: VALIDATION_SOP
title: "SOP 3 - Independent Person Validation & Data QA"
version: "1.0"
status: "Production Draft"
last_updated: "2026-09-12"
scope: "Independent validation of SOP 2 PERSON_PASS records before Golden selection"
input_requirement: "SOP 2 person_status = PERSON_PASS"
decision_vocabulary:
  - VALIDATED_PASS
  - VALIDATED_REVIEW
  - VALIDATED_REJECT
workflow_statuses:
  - RETURN_TO_SOP1
  - RETURN_TO_SOP2
primary_handoff: "SOP 4 - Golden 1,000 Selection & Final Validation"
source_of_truth: "Fresh independent evidence, canonical entity match, and auditable validation decisions"
volume_policy: "No fixed validated-person count. Validation thresholds must never move to satisfy a target."
validation_mode: "Independent and adversarial; attempt to disprove the upstream record before approving it."
---

# ASSIGNMENT INTERPRETATION

## Target input

Only records that have already passed SOP 2.

Every incoming person record must contain:

- `person_id`
- `account_id`
- full name
- matched LinkedIn profile URL
- current company
- current title
- role family
- primary use case inherited from SOP 1
- initial P1/P2/P3 candidate classification
- SOP 2 role evidence
- SOP 1 validated account identity
- SOP 1 LinkedIn company page
- SOP 1 LinkedIn sector status
- SOP 1 account archetype
- SOP 1 account priority
- SOP 1 current signal

If any required upstream field is absent, do not invent it.

Route the record back to the responsible upstream SOP.

## Validation objective

Independently determine whether the person record is:

1. the correct human;
2. attached to the correct validated account/entity;
3. still employed by that account or correct parent system;
4. carrying the correct current title and function;
5. operating at the correct organisational scope;
6. materially relevant to the inherited account use case;
7. correctly classified as P1/P2/P3;
8. unique rather than a duplicate representation of the same person;
9. supported by sufficiently current evidence;
10. ready for Golden consideration.

## Validation philosophy

SOP 3 is not a second discovery exercise.

It is an independent truth and quality-control layer.

The validator must not ask:

> "How can I confirm this person is good?"

The validator must ask:

> **"What evidence would prove this record wrong, stale, duplicated, misclassified, or commercially weaker than claimed?"**

## LinkedIn activity rule

LinkedIn activity is validated only after identity, employment, role, relevance, and duplicate checks have passed.

Controlled rule:

- `ACTIVE` = at least one visible LinkedIn reaction in the previous 12 months.
- `INACTIVE` = activity check completed successfully and zero visible reactions were found in the previous 12 months.
- `UNKNOWN` = a reliable activity result could not be obtained.

LinkedIn inactivity is not a commercial-relevance rejection reason.

A commercially strong person may remain `VALIDATED_PASS` with `linkedin_activity_status = INACTIVE`.

---

# 00. Document Control

## 00.1 Purpose

This SOP governs:

- independent person validation;
- person identity verification;
- employer and entity matching;
- current-role validation;
- role-scope validation;
- commercial relevance validation;
- P1/P2/P3 challenge;
- duplicate/person canonicalization;
- LinkedIn activity validation;
- evidence conflict handling;
- correction logging;
- upstream return logic;
- final validation handoff to SOP 4.

## 00.2 This SOP does not

SOP 3 does not:

- rediscover accounts from zero;
- repeat full SOP 1 account research;
- repeat full SOP 2 buying-group discovery;
- enrich paid email or phone data;
- select the final Golden 1,000;
- reject a person solely for LinkedIn inactivity;
- force a predetermined validated-person count.

## 00.3 Core operating question

> **Can an independent reviewer trust this person record enough to let it compete for Golden 1,000 selection?**

## 00.4 Independence rule

Where operationally possible, SOP 3 must use a different validation agent, prompt, or reviewer from the one that produced the SOP 2 conclusion.

The validator must not simply restate SOP 2 reasoning.

## 00.5 Volume rule

There is no fixed number of people that must receive `VALIDATED_PASS`.

Do not lower validation standards to create a larger pool.

---

# 01. Purpose and Success Definition

## 01.1 Successful validated record

A `VALIDATED_PASS` person must have:

- confirmed identity;
- confirmed or sufficiently current employer;
- confirmed correct account/entity relationship;
- current title established;
- current function understood;
- role scope established;
- inherited use-case relevance independently confirmed;
- one valid commercial role classification;
- validated P1/P2/P3 classification;
- duplicate/person canonicalization complete;
- LinkedIn profile still valid;
- LinkedIn activity status captured;
- no unresolved material conflict;
- all corrections logged;
- evidence traceable;
- handoff-ready status true.

## 01.2 What does not automatically invalidate a person

The following do not automatically cause rejection:

- title became more senior;
- title wording changed;
- person moved from facility level to system level;
- original P1 becomes P2;
- LinkedIn activity is `INACTIVE`;
- one stale source exists where stronger current evidence resolves it;
- an upstream field needs correction but the person remains relevant.

## 01.3 What does invalidate a person

Examples:

- wrong human;
- former employee;
- unrelated employer;
- wrong entity relationship;
- role has no material relation to the use case;
- duplicate representation of an existing canonical person;
- LinkedIn profile belongs to another person;
- unresolved identity conflict;
- material role conflict cannot be resolved.

---

# 02. Validation Scope and Upstream Boundaries

## 02.1 SOP 1 fields inherited, not re-researched by default

Do not normally redo:

- geography;
- account archetype;
- bed count;
- Core Signal;
- Supporting Signal;
- account use-case research;
- LinkedIn company-sector validation;
- account negative research;
- relationship-overlap research.

## 02.2 SOP 2 fields inherited, then challenged

SOP 3 must independently challenge:

- person identity;
- employer;
- current role;
- function;
- role family;
- problem ownership;
- commercial influence;
- P1/P2/P3;
- duplicate status.

## 02.3 When upstream research must reopen

### `RETURN_TO_SOP1`

Use when new evidence materially challenges the account-level foundation.

Examples:

- hospital acquired and buying authority changed;
- person evidence reveals account is the wrong parent/facility entity;
- current entity relationship invalidates original account scope;
- protected relationship appears that SOP 1 missed;
- current evidence materially invalidates the primary use case.

### `RETURN_TO_SOP2`

Use when account remains valid but the buying-group map is incomplete or misconstructed.

Examples:

- P1 is demoted and no stronger owner is mapped;
- obvious required role family is missing;
- most mapped people are irrelevant;
- role-scope correction changes which decision-makers should be present.

Do not silently fix a structural upstream problem inside SOP 3.

---

# 03. Validation Definitions

## `IDENTITY_CONFIRMED`

The LinkedIn profile and supporting evidence belong to the intended human.

## `DIRECT_ACCOUNT_MATCH`

Person currently works directly for the validated account.

## `PARENT_SYSTEM_MATCH`

Person works for the validated parent health system and has relevant authority over the account.

## `MULTI_FACILITY_MATCH`

Person has responsibility across multiple relevant facilities in the validated system.

## `UNRELATED_ENTITY`

Person works for an organisation that does not control or materially relate to the qualified account.

## `CURRENT_ROLE_VERIFIED`

Current employer, title, and function are sufficiently supported by current evidence.

## `ROLE_SCOPE`

Controlled values:

- `SYSTEM_LEVEL`
- `MULTI_FACILITY`
- `FACILITY_LEVEL`

## `VALIDATED_COMMERCIAL_ROLE`

Allowed values:

- `DIRECT_OWNER`
- `CO_OWNER`
- `TECHNICAL_EVALUATOR`
- `CLINICAL_EVALUATOR`
- `EXECUTIVE_SPONSOR`
- `INTERNAL_ROUTE`

## `NOT_MATERIALLY_RELEVANT`

Current function does not justify inclusion for the inherited use case.

## `VALIDATED_PRIORITY`

Allowed values:

- `P1`
- `P2`
- `P3`

## `ACTIVITY_STATUS`

Allowed values:

- `ACTIVE`
- `INACTIVE`
- `UNKNOWN`

---

# 04. Hard Validation Rejections

| Code | Condition | Decision |
|---|---|---|
| `V-R01_WRONG_PERSON` | LinkedIn/profile evidence belongs to another human | VALIDATED_REJECT |
| `V-R02_FORMER_EMPLOYEE` | Current evidence confirms person left relevant account/system | VALIDATED_REJECT |
| `V-R03_WRONG_ACCOUNT` | Person works for unrelated organisation | VALIDATED_REJECT |
| `V-R04_WRONG_ENTITY_SCOPE` | Person is at a parent/subsidiary/facility with no material authority over qualified account | VALIDATED_REJECT |
| `V-R05_ROLE_NOT_RELEVANT` | Current role is not materially relevant to inherited use case | VALIDATED_REJECT |
| `V-R06_DUPLICATE_PERSON` | Same human already exists as canonical person | VALIDATED_REJECT duplicate record |
| `V-R07_LINKEDIN_PROFILE_INVALID` | LinkedIn URL belongs to another person or is unusable for identity | VALIDATED_REJECT |
| `V-R08_UNRESOLVED_IDENTITY` | Same-name/person ambiguity cannot be resolved | VALIDATED_REJECT after defined attempts |
| `V-R09_UNRESOLVED_ROLE_CONFLICT` | Material current-role conflict cannot be resolved | VALIDATED_REJECT after defined attempts |
| `V-R10_NO_CURRENT_EMPLOYMENT_PROOF` | Current employment cannot be supported to validation standard | VALIDATED_REJECT after defined attempts |

There is deliberately no rejection code for LinkedIn inactivity.

---

# 05. Validation Source Standard

## 05.1 Strong direct evidence

Examples:

- current hospital/system leadership page;
- current official staff directory;
- current department page;
- current official biography;
- current hospital announcement;
- current official program page.

May independently establish current role when clear and current.

## 05.2 Strong first-party professional evidence

Examples:

- current LinkedIn profile;
- current official LinkedIn announcement;
- recent conference bio clearly tied to current organisation;
- current professional society bio with employer/title.

Useful for:

- current employer;
- current title;
- role changes;
- identity matching.

## 05.3 Secondary evidence

Examples:

- healthcare press;
- professional association;
- recent conference agenda;
- credible speaker biography.

Use for triangulation.

## 05.4 Weak evidence

Examples:

- Apollo;
- ZoomInfo;
- RocketReach;
- stale people databases;
- generic profile aggregators;
- search snippets.

Weak evidence may discover or suggest a person but cannot independently carry `VALIDATED_PASS` where stronger current evidence is reasonably available.

## 05.5 No forced two-source rule

Do not require two sources for every person.

One strong, current, direct source may be sufficient.

Triangulate when:

- evidence is stale;
- official and LinkedIn evidence conflict;
- title is ambiguous;
- parent/facility scope is unclear;
- same-name ambiguity exists;
- P1 classification depends on inferred responsibility.

---

# 06. Freshness Standard

## 06.1 Current role / employer

Preferred:

- current official page;
- current LinkedIn profile;
- evidence refreshed within the current validation cycle.

Older evidence may be used only when no newer contradiction exists and the person remains clearly current.

## 06.2 Stale evidence treatment

Do not reject solely because one source is old.

Classify:

`STALE_REQUIRES_REFRESH`

Then seek current evidence.

## 06.3 Conflict precedence

Use:

**newer direct evidence > older direct evidence > newer credible secondary > database/discovery source**

unless the newer source is clearly weaker for the specific claim.

---

# 07. Required Output Schema

## 07.1 Person identity

- `person_id`
- `canonical_person_id`
- `account_id`
- `full_name`
- `linkedin_profile_url`
- `linkedin_identity_status`
- `identity_confidence`

## 07.2 Employer / entity

- `current_employer`
- `account_entity_match`
- `role_scope`
- `related_account_ids[]`

`account_entity_match` allowed:

- `DIRECT_ACCOUNT_MATCH`
- `PARENT_SYSTEM_MATCH`
- `MULTI_FACILITY_MATCH`
- `UNRELATED_ENTITY`
- `CONFLICT`

## 07.3 Current role

- `validated_current_title`
- `validated_department`
- `validated_role_family`
- `current_role_status`
- `employment_status`
- `role_evidence_ids[]`

`employment_status`:

- `CURRENT_CONFIRMED`
- `CURRENT_PROBABLE`
- `FORMER_CONFIRMED`
- `CONFLICT`
- `UNKNOWN`

`CURRENT_PROBABLE` cannot receive final `VALIDATED_PASS`.

## 07.4 Commercial validation

- `primary_use_case`
- `validated_commercial_role`
- `problem_ownership_level`
- `evaluation_influence`
- `commercial_influence`
- `technical_influence`
- `clinical_influence`
- `internal_routing_value`

## 07.5 Priority validation

- `original_priority`
- `validated_priority`
- `priority_change_status`
- `priority_change_reason`

`priority_change_status`:

- `UNCHANGED`
- `PROMOTED`
- `DEMOTED`

## 07.6 Better-person challenge

- `better_person_gap_found`
- `better_function`
- `better_person_name_if_known`
- `return_to_sop2_required`

## 07.7 Duplicate / canonicalization

- `duplicate_status`
- `duplicate_of_person_id`
- `canonical_person_id`
- `related_account_ids[]`

`duplicate_status`:

- `UNIQUE`
- `DUPLICATE`
- `SYSTEM_LEVEL_SHARED_PERSON`

## 07.8 LinkedIn activity

- `linkedin_activity_status`
- `last_visible_reaction_date`
- `linkedin_activity_checked_at`
- `linkedin_activity_source`

## 07.9 Evidence / QA

- `evidence[]`
- `conflict_status`
- `correction_log[]`
- `validation_notes`
- `validator_id`
- `validated_at`
- `qa_status`
- `validation_status`
- `handoff_ready`

---

# 08. Correction Log

Never silently overwrite an upstream field.

Every material correction must create a change record.

Canonical object:

```json
{
  "field_name": "current_title",
  "old_value": "Director of Clinical Engineering",
  "new_value": "Vice President, Clinical Engineering",
  "change_type": "CORRECTION",
  "reason": "Newer current evidence",
  "evidence_ids": ["EV-V-019"],
  "changed_at": "2026-09-12T12:00:00Z"
}
```

Allowed `change_type` values:

- `CORRECTION`
- `PROMOTION`
- `DEMOTION`
- `SCOPE_CHANGE`
- `ENTITY_CORRECTION`
- `DUPLICATE_MERGE`

---

# 09. Validation Pipeline

Run sequentially.

# Gate V0 - Input Integrity

**Question:**  
Is this a complete SOP 2 `PERSON_PASS` record tied to a valid SOP 1 PASS account?

**PASS**
Required upstream fields present.

**RETURN_TO_SOP2**
Person-level fields incomplete.

**RETURN_TO_SOP1**
Account-level foundation is incomplete or invalid.

Do not invent missing upstream data.

---

# Gate V1 - Person Identity Validation

**Question:**  
Does the LinkedIn URL and evidence definitely belong to the intended human?

Check:

- full name;
- current role;
- current employer;
- location where useful;
- employment history;
- account association.

**PASS**
`IDENTITY_CONFIRMED`.

**REVIEW**
Same-name ambiguity or partial mismatch with a clear verification path.

**REJECT**
Wrong person or unresolved identity after defined attempts.

---

# Gate V2 - Employer and Entity Match

**Question:**  
Does this person's current employer correctly map to the SOP 1 validated account or its controlling parent system?

Classify:

- `DIRECT_ACCOUNT_MATCH`
- `PARENT_SYSTEM_MATCH`
- `MULTI_FACILITY_MATCH`
- `UNRELATED_ENTITY`
- `CONFLICT`

**PASS**
Direct, parent, or multi-facility match with relevant authority.

**REVIEW**
Entity relationship or authority scope unclear.

**REJECT**
Unrelated entity.

Important:

Do not assume that similar company names belong to the same health system.

Use the SOP 1 canonical account and validated LinkedIn company identity as the entity reference.

---

# Gate V3 - Current Employment Validation

**Question:**  
Does current evidence support that this person still works at the relevant account/system?

**PASS**
`CURRENT_CONFIRMED`

**REVIEW**
Conflict or only stale evidence remains.

**REJECT**
`FORMER_CONFIRMED`

A database saying "current" does not override newer direct evidence of departure.

---

# Gate V4 - Current Title, Function and Scope

Validate separately:

1. current title;
2. department/function;
3. organisational scope.

Possible scope:

- `SYSTEM_LEVEL`
- `MULTI_FACILITY`
- `FACILITY_LEVEL`

If title changed but person remains relevant:

- update title;
- log correction;
- continue validation.

Do not reject a person merely because SOP 2 title is outdated.

---

# Gate V5 - Commercial Role Validation

**Question:**  
Given the inherited primary use case, does the person's actual current function still justify inclusion?

Allowed PASS classifications:

- `DIRECT_OWNER`
- `CO_OWNER`
- `TECHNICAL_EVALUATOR`
- `CLINICAL_EVALUATOR`
- `EXECUTIVE_SPONSOR`
- `INTERNAL_ROUTE`

Reject classification:

- `NOT_MATERIALLY_RELEVANT`

Examples:

A CIO may remain relevant for U1 as technical/evaluation support even when Telemetry is the direct owner.

A generic senior physician with no operating responsibility may be rejected.

---

# Gate V6 - P1/P2/P3 Challenge

Do not preserve SOP 2 priority automatically.

## Preserve

Original priority remains commercially correct.

## Promote

Example:
P2 -> P1 because current evidence confirms direct workflow ownership.

## Demote

Example:
P1 -> P2 because another function is materially closer to the problem.

## Reject

Only when the person themselves is not materially relevant.

Important:

> A better P1 does not make a valid P2/P3 person invalid.

Store:

- original priority;
- validated priority;
- change reason;
- evidence.

---

# Gate V7 - Better-Person / Buying-Group Gap Check

For every proposed validated P1 ask:

> **Is there an obvious materially better function or person who should be represented but is missing from SOP 2?**

If NO:
continue.

If YES and current person remains useful:
keep current person with corrected priority and set:

`return_to_sop2_required = true`

If YES and current person is not materially relevant:
reject current person and return account to SOP 2.

SOP 3 does not rebuild the whole buying group itself.

---

# Gate V8 - Canonical Person and Duplicate Validation

Check across the entire working dataset:

1. LinkedIn profile URL;
2. normalized full name;
3. current employer;
4. profile identifiers where available;
5. title/history overlap.

## One human = one canonical person

If same system-level executive appears under multiple facilities:

Do not count them as separate people.

Use one canonical record:

```json
{
  "canonical_person_id": "P-12345",
  "duplicate_status": "SYSTEM_LEVEL_SHARED_PERSON",
  "related_account_ids": ["A-1", "A-2", "A-3"]
}
```

Duplicate secondary rows receive:

`VALIDATED_REJECT - V-R06_DUPLICATE_PERSON`

The canonical record remains eligible.

---

# Gate V9 - LinkedIn Activity Validation

Run after V1-V8.

For each surviving person, use the approved LinkedIn activity process.

## `ACTIVE`

At least one visible LinkedIn reaction in the previous 12 months.

## `INACTIVE`

The activity check completed successfully and zero visible reactions were found in the previous 12 months.

## `UNKNOWN`

A reliable activity result could not be obtained.

Required fields:

- `linkedin_activity_status`
- `last_visible_reaction_date`
- `linkedin_activity_checked_at`
- `linkedin_activity_source`

### Hard rule

`INACTIVE` does not cause `VALIDATED_REJECT`.

`UNKNOWN` does not cause `VALIDATED_REJECT`.

LinkedIn activity is a reachability signal for SOP 4, not a substitute for commercial relevance.

---

# Gate V10 - Evidence Conflict Resolution

Review all material person-level conflicts.

Examples:

- LinkedIn and hospital site show different titles;
- current company differs;
- parent/facility authority unclear;
- role family conflicts with actual responsibilities;
- official bio is stale relative to newer announcement.

Allowed conflict status:

- `NONE`
- `RESOLVED`
- `UNRESOLVED`

`UNRESOLVED` material conflict cannot receive `VALIDATED_PASS`.

---

# Gate V11 - Final Validation Decision

## `VALIDATED_PASS`

Requires:

- identity confirmed;
- current employment confirmed;
- entity match valid;
- current title/function validated;
- scope validated;
- commercial role valid;
- priority validated;
- duplicate check complete;
- LinkedIn activity status captured;
- no unresolved material conflict;
- corrections logged;
- evidence traceable.

## `VALIDATED_REVIEW`

Only a specific resolvable gap remains.

Must include:

- `missing_fact`
- `why_it_matters`
- `best_verification_source`
- `exact_next_action`

## `VALIDATED_REJECT`

Confirmed hard validation failure.

---

# 10. LinkedIn Activity Rules

## 10.1 Exact rule

The SOP uses one simple activity standard:

> **At least one visible LinkedIn reaction in the previous 12 months = ACTIVE.**

No additional post/comment/repost threshold is required.

## 10.2 No visible reaction

If the check completed successfully and no visible reaction is found:

`INACTIVE`

## 10.3 Failed or unreliable activity check

If the actor, page, source, or retrieval process does not provide a reliable result:

`UNKNOWN`

Never convert a technical failure into `INACTIVE`.

## 10.4 Commercial treatment

A commercially excellent:

- Telemetry Director;
- CNO;
- Clinical Engineering leader;
- CNIO;
- CIO;
- Virtual Care leader;

may remain fully validated even when `INACTIVE`.

SOP 4 may use `ACTIVE` as a practical reachability advantage.

---

# 11. Independent Validator Rules

## 11.1 Validator must actively search for disproof

For each person, attempt to find:

- departure from organisation;
- title change;
- employer change;
- parent/facility mismatch;
- wrong LinkedIn profile;
- better problem owner;
- duplicate representation;
- stale upstream evidence;
- function different from title assumption.

## 11.2 Validator must not

- search only for evidence confirming SOP 2;
- preserve P1 because SOP 2 marked P1;
- assume title equals responsibility;
- treat LinkedIn inactivity as disqualification;
- create missing facts;
- rebuild the entire account research;
- rebuild the whole buying group unless returning it to SOP 2.

---

# 12. Role Validation Rules

## 12.1 Direct owner

Strongest class for problem ownership.

Examples:

- Telemetry Director for U1;
- Clinical Engineering leader for U2;
- Central Monitoring leader for U3;
- Virtual Care leader for U4;
- CNIO/Nursing Informatics for U5 where workflow is nursing-owned.

## 12.2 Technical evaluator

Valid when responsible for:

- integration;
- device connectivity;
- architecture;
- clinical systems;
- technical implementation.

## 12.3 Clinical evaluator

Valid when responsible for:

- clinical workflow;
- nursing;
- monitoring practice;
- informatics;
- clinical adoption.

## 12.4 Executive sponsor

Valid when senior person can materially sponsor adoption.

Do not use executive status as substitute for direct problem ownership.

## 12.5 Internal route

Valid only when the person can credibly route the discussion to the actual owner.

Do not use `INTERNAL_ROUTE` to rescue a weak generic executive.

---

# 13. Priority Validation Rules

## P1

Best natural first person for the account's specific problem.

Usually one or a small number of people per account.

## P2

Complementary evaluator, co-owner, or technical/clinical counterpart.

## P3

Executive sponsor, secondary stakeholder, or credible internal route.

## Priority challenge rule

A P1 must survive this question:

> **Would a knowledgeable operator inside this hospital agree that this function is one of the most natural first owners of the problem?**

If not, demote or return to SOP 2.

---

# 14. Duplicate and Canonicalization Rules

## 14.1 Same LinkedIn URL

Automatic duplicate.

## 14.2 Same human, multiple titles

Keep one canonical person and the current title.

Store previous title in history if relevant.

## 14.3 Same system executive mapped to multiple hospitals

Keep one canonical person with multiple related account IDs where their authority is genuinely system-wide.

## 14.4 Same name, different humans

Do not merge without identity evidence.

## 14.5 Duplicate impact on counts

Only canonical people may be counted in downstream Golden candidate totals.

---

# 15. Upstream Return Logic

## 15.1 Return to SOP 1 when

- account entity is wrong;
- acquisition changed commercial scope;
- parent/system relationship invalidates account logic;
- primary use case is materially wrong;
- protected relationship appears;
- current account-level evidence contradicts qualification.

## 15.2 Return to SOP 2 when

- correct person class is missing;
- buying group lacks direct problem owner;
- P1 is demoted and no replacement exists;
- role diversity is materially incomplete;
- person selection was based on title prestige rather than use-case ownership.

## 15.3 Do not silently fix upstream architecture

SOP 3 may correct person fields.

It should not quietly replace entire upstream account or buying-group logic without creating a return action.

---

# 16. Contact Enrichment

No paid email or phone enrichment in SOP 3.

Reason:

The next major selection step is Golden 1,000.

Do not spend enrichment cost on validated people who may not enter the final outreach set.

---

# 17. Automation Architecture

## 17.1 INPUT LOAD

Load:

- SOP 1 account record;
- SOP 2 person record;
- associated evidence;
- canonical entity identifiers.

## 17.2 IDENTITY VALIDATION

Check person/profile/entity consistency.

## 17.3 ROLE VALIDATION

Check current employer, title, function, and scope.

## 17.4 COMMERCIAL VALIDATION

Challenge role-to-use-case relevance.

## 17.5 PRIORITY CHALLENGE

Preserve, promote, or demote P1/P2/P3.

## 17.6 DUPLICATE RESOLUTION

Canonicalize person records.

## 17.7 LINKEDIN ACTIVITY

Run the approved activity process only after person survives preceding validation.

## 17.8 CONFLICT RESOLUTION

Resolve or route remaining material conflicts.

## 17.9 FINAL DECISION

Assign:

- VALIDATED_PASS
- VALIDATED_REVIEW
- VALIDATED_REJECT
- RETURN_TO_SOP1
- RETURN_TO_SOP2 where applicable

## 17.10 STORAGE

Persist:

- validated fields;
- correction log;
- evidence;
- activity status;
- decision;
- timestamps;
- validator identity.

---

# 18. AI Usage Rules

AI may:

- compare person and account identities;
- detect same-name ambiguity;
- validate title/function mapping;
- detect current/old role differences;
- challenge use-case relevance;
- suggest P1/P2/P3 changes;
- detect duplicate humans;
- identify account/facility scope issues;
- classify activity result as ACTIVE/INACTIVE/UNKNOWN;
- draft correction logs;
- recommend upstream return.

AI must not:

- invent responsibilities;
- assume current employment from stale data;
- assume same-name organisations are related;
- treat `INACTIVE` as rejection;
- silently overwrite corrected fields;
- preserve upstream priority without challenge;
- lower validation standards to increase pool size;
- create new account use cases without routing material changes upstream.

---

# 19. Human QA Triggers

Human QA is required when:

- same-name identity remains ambiguous;
- official source and LinkedIn materially conflict;
- person appears at multiple related entities;
- parent/facility authority is unclear;
- P1 is being demoted due to a better-person finding;
- person is a system-wide executive represented across multiple accounts;
- rejection depends on interpreting a complex role;
- new evidence would require RETURN_TO_SOP1;
- duplicate merge affects multiple account records.

---

# 20. Review Rules

Every `VALIDATED_REVIEW` must state:

1. exact unresolved fact;
2. why it blocks PASS/REJECT;
3. strongest next verification source;
4. exact next action.

Forbidden:

`Needs more research`

Example:

> `VALIDATED_REVIEW - LinkedIn lists VP Clinical Systems, while the hospital directory lists Director Clinical Applications. Verify the most current title through a recent official announcement or current department page before final validation.`

---

# 21. Final Handoff Standard

A person may enter SOP 4 only when:

- `validation_status = VALIDATED_PASS`;
- `handoff_ready = true`;
- current employment confirmed;
- identity confirmed;
- entity match valid;
- current title/function validated;
- role scope validated;
- commercial role validated;
- validated priority assigned;
- duplicate check complete;
- LinkedIn activity status captured;
- no unresolved material conflict;
- all material corrections logged.

## Required handoff package to SOP 4

- `canonical_person_id`
- `person_id`
- `account_id`
- `full_name`
- `linkedin_profile_url`
- `validated_current_title`
- `validated_department`
- `validated_role_family`
- `role_scope`
- `primary_use_case`
- `validated_commercial_role`
- `problem_ownership_level`
- `evaluation_influence`
- `commercial_influence`
- `technical_influence`
- `clinical_influence`
- `internal_routing_value`
- `validated_priority`
- `linkedin_activity_status`
- `last_visible_reaction_date`
- `account_priority`
- `account_current_signal`
- `evidence_confidence`
- `conflict_status`
- `validated_at`

SOP 4 should not discover that a person has left the organisation.

If that happens repeatedly, SOP 3 must be tightened.

---

# 22. Metrics and Feedback Loop

Track:

- SOP 2 -> VALIDATED_PASS rate;
- VALIDATED_REVIEW rate;
- VALIDATED_REJECT rate;
- former-employee rate;
- wrong-person rate;
- wrong-account rate;
- role-not-relevant rate;
- duplicate-person rate;
- P1 promotion rate;
- P1 demotion rate;
- RETURN_TO_SOP1 rate;
- RETURN_TO_SOP2 rate;
- ACTIVE rate;
- INACTIVE rate;
- UNKNOWN activity rate;
- title-correction rate;
- scope-correction rate;
- unresolved-conflict rate;
- average validation time per person;
- Golden conversion rate by validated role family;
- Golden conversion rate by validated priority.

## Feedback rule

If a recurring validation failure appears, fix it upstream.

Examples:

- high former-employee rate -> strengthen SOP 2 freshness;
- high wrong-function rate -> tighten SOP 2 title-to-role mapping;
- high duplicate rate -> improve SOP 2 canonicalization;
- high P1 demotion rate -> improve SOP 2 better-person logic;
- high RETURN_TO_SOP1 rate -> tighten account/entity qualification.

---

# 23. Common Failure Modes

| Error | Why dangerous | Correct treatment |
|---|---|---|
| Confirming instead of challenging | Upstream mistakes survive | Search for disproof |
| Same-name wrong profile | Outreach goes to wrong human | V1 identity gate |
| Former employee | Wasted outreach | V3 reject |
| Title changed | Good person incorrectly rejected | Correct + log + continue |
| Parent/facility confusion | Wrong scope | V2/V4 |
| Senior but irrelevant role | Prestige mistaken for ownership | V5 reject/demote |
| Wrong P1 | Outreach starts with weaker stakeholder | V6 demote |
| Duplicate system executive | Inflated dataset | V8 canonicalize |
| Actor failure marked inactive | False reachability conclusion | UNKNOWN |
| Inactive person rejected | Commercial quality lost | Keep PASS if commercially valid |
| Silent field correction | No audit trail | Correction log mandatory |
| Full upstream research repeated | Waste and inconsistency | Validate only material fields |

---

# 24. Worked Examples

All examples are fictional.

## 24.1 Title change - PASS

SOP 2:

`Director of Clinical Engineering`

Validation finds current official evidence:

`Vice President, Clinical Engineering`

Person remains at same system and retains relevant device/integration ownership.

Action:

- update title;
- log correction;
- keep commercial role;
- `VALIDATED_PASS`.

---

## 24.2 Former employee - REJECT

SOP 2 profile says:

`CNO - Current`

New official announcement confirms departure three months ago.

Decision:

`VALIDATED_REJECT - V-R02_FORMER_EMPLOYEE`

---

## 24.3 P1 demoted, person retained

Primary use case:

`U1_DIGITAL_RHYTHM_WORKFLOW`

SOP 2:

CIO = P1

Validation confirms a current Director of Telemetry with direct operational ownership.

Action:

- CIO remains commercially relevant;
- CIO -> P2;
- `return_to_sop2_required = true` if Telemetry Director was not already mapped;
- CIO may still receive `VALIDATED_PASS`.

---

## 24.4 Same system executive appears four times

System CIO appears once under each of four facilities.

Validation establishes system-wide authority.

Action:

- create one canonical person;
- attach four related account IDs;
- reject duplicate secondary rows;
- count one person downstream.

---

## 24.5 LinkedIn inactive but strong person

Current Director of Telemetry.

Identity, employer, role, scope and use-case ownership all validated.

Activity check completed successfully.

Zero visible reactions in previous 12 months.

Set:

`linkedin_activity_status = INACTIVE`

Decision:

`VALIDATED_PASS`

Reason:

Activity is a reachability signal, not a commercial relevance gate.

---

## 24.6 Apify/activity failure

All commercial validation passes.

Activity process returns unreliable/no usable result.

Set:

`linkedin_activity_status = UNKNOWN`

Decision:

`VALIDATED_PASS`

Do not label inactive.

---

## 24.7 Wrong entity scope

Person works for a similarly named hospital outside the validated system.

Decision:

`VALIDATED_REJECT - V-R03_WRONG_ACCOUNT`

---

# 25. AI Execution Contract

```text
You are executing SOP 3 - Independent Person Validation & Data QA.

INPUT:
Only SOP 2 PERSON_PASS records tied to SOP 1 PASS accounts.

YOUR JOB:
Independently challenge each person record and determine whether it is trustworthy enough for Golden selection.

DO NOT:
- repeat full account research;
- repeat full buying-group discovery;
- assume SOP 2 is correct;
- enrich paid email/phone data;
- reject a person because LinkedIn is inactive;
- lower standards to increase validated volume.

VALIDATE:
1. correct human;
2. correct LinkedIn profile;
3. correct current employer;
4. correct account/entity relationship;
5. current title;
6. current function;
7. organisational scope;
8. inherited use-case relevance;
9. commercial role;
10. P1/P2/P3 classification;
11. duplicate/canonical-person status;
12. LinkedIn activity status;
13. evidence conflicts.

VALIDATOR MINDSET:
Actively search for evidence that would disprove the upstream record:
- person left;
- title changed;
- employer changed;
- wrong entity;
- wrong scope;
- wrong function;
- stronger problem owner exists;
- duplicate person exists;
- upstream evidence is stale.

CORRECTIONS:
Do not reject a good person merely because a field changed.
Correct the field, log the change, and continue.

UPSTREAM RETURNS:
RETURN_TO_SOP1 when the account foundation is materially wrong.
RETURN_TO_SOP2 when the account is valid but the buying-group map is incomplete or mis-prioritized.

LINKEDIN ACTIVITY RULE:
ACTIVE = at least 1 visible LinkedIn reaction in the previous 12 months.
INACTIVE = check completed successfully and 0 visible reactions found in the previous 12 months.
UNKNOWN = reliable activity result could not be obtained.

INACTIVE and UNKNOWN are not rejection reasons.

FINAL DECISIONS:
VALIDATED_PASS
VALIDATED_REVIEW
VALIDATED_REJECT

Every VALIDATED_REVIEW must state:
missing_fact
why_it_matters
best_verification_source
exact_next_action

Every material correction must be logged.

OUTPUT:
Return deterministic JSON using the canonical validation schema.
```

# 26. Canonical Validation JSON

```json
{
  "person_id": "",
  "canonical_person_id": "",
  "account_id": "",
  "full_name": "",
  "linkedin_profile_url": "",
  "linkedin_identity_status": "",
  "identity_confidence": "",
  "current_employer": "",
  "account_entity_match": "",
  "role_scope": "",
  "related_account_ids": [],
  "validated_current_title": "",
  "validated_department": "",
  "validated_role_family": "",
  "current_role_status": "",
  "employment_status": "",
  "primary_use_case": "",
  "validated_commercial_role": "",
  "problem_ownership_level": "",
  "evaluation_influence": "",
  "commercial_influence": "",
  "technical_influence": "",
  "clinical_influence": "",
  "internal_routing_value": "",
  "original_priority": "",
  "validated_priority": "",
  "priority_change_status": "UNCHANGED",
  "priority_change_reason": null,
  "better_person_gap_found": false,
  "better_function": null,
  "better_person_name_if_known": null,
  "return_to_sop2_required": false,
  "duplicate_status": "UNIQUE",
  "duplicate_of_person_id": null,
  "linkedin_activity_status": "",
  "last_visible_reaction_date": null,
  "linkedin_activity_checked_at": "",
  "linkedin_activity_source": "",
  "evidence": [],
  "correction_log": [],
  "conflict_status": "NONE",
  "missing_fact": null,
  "next_verification_action": null,
  "validation_status": "",
  "reject_reason_code": null,
  "validator_id": "",
  "validated_at": "",
  "qa_status": "",
  "handoff_ready": false
}
```

# 27. FINAL SELF-QA CHECKLIST

Before `VALIDATED_PASS` or SOP 4 handoff:

- [ ] Input person was SOP 2 PERSON_PASS?
- [ ] SOP 1 account remains valid?
- [ ] Correct human confirmed?
- [ ] LinkedIn profile belongs to the correct human?
- [ ] Current employer confirmed?
- [ ] Employer maps to the correct validated account/system?
- [ ] Current title validated?
- [ ] Current function understood?
- [ ] Role scope established?
- [ ] Primary use case inherited correctly?
- [ ] Commercial role independently validated?
- [ ] P1/P2/P3 challenged rather than blindly preserved?
- [ ] Better-person gap checked?
- [ ] Duplicate/canonical-person check complete?
- [ ] LinkedIn activity checked after person validation?
- [ ] ACTIVE/INACTIVE/UNKNOWN assigned correctly?
- [ ] Technical/API failure was not labelled INACTIVE?
- [ ] LinkedIn inactivity was not used as a rejection reason?
- [ ] Material corrections recorded in correction log?
- [ ] Material conflicts resolved?
- [ ] Evidence traceable?
- [ ] No paid email/phone enrichment performed?
- [ ] RETURN_TO_SOP1/SOP2 used where upstream structure is wrong?
- [ ] Final decision independent of any desired dataset count?
- [ ] Handoff package complete for SOP 4?

One unresolved material conflict means the record cannot receive `VALIDATED_PASS`.
