---
document_id: SOP-04-GOLDEN-1000-SELECTION-FINAL-VALIDATION
document_type: SELECTION_SOP
title: "SOP 4 - Golden 1,000 Selection & Final Validation"
version: "1.0"
status: "Production Draft"
last_updated: "2026-09-12"
scope: "Selection of exactly 1,000 unique highest-priority decision-makers from SOP 3 VALIDATED_PASS records"
input_requirement: "SOP 3 validation_status = VALIDATED_PASS and handoff_ready = true"
selection_vocabulary:
  - GOLDEN_SELECTED
  - ELIGIBLE_NOT_SELECTED
  - RETURN_TO_SOP3
primary_output: "Exactly 1,000 unique canonical decision-makers when the eligible pool is sufficient"
source_of_truth: "SOP 1 account evidence + SOP 3 validated person evidence + transparent Golden ranking dimensions"
volume_policy: "Exactly 1,000 are selected only from records meeting the Golden minimum standard. Never lower the standard to reach 1,000."
---

# ASSIGNMENT INTERPRETATION

## Input

Only SOP 3 `VALIDATED_PASS` records may enter SOP 4.

Each record must already contain:

- unique canonical person identity;
- validated LinkedIn profile;
- validated current employment;
- validated current title/function;
- validated entity/account match;
- validated organisational scope;
- inherited primary use case;
- validated commercial role;
- validated P1/P2/P3 priority;
- duplicate resolution;
- LinkedIn activity status;
- evidence confidence;
- account priority;
- account current signal;
- no unresolved material conflict.

SOP 4 must not become the stage where former employees, wrong profiles, duplicates, or wrong roles are discovered routinely.

## Core objective

Select exactly **1,000 unique people** who offer the strongest combination of:

1. account attractiveness;
2. problem/use-case strength;
3. direct problem ownership;
4. commercial/evaluation influence;
5. validated stakeholder priority;
6. timing/current signal;
7. evidence confidence;
8. practical LinkedIn reachability;
9. buying-group diversity;
10. incremental value relative to other people from the same account.

## Golden principle

The 1,000 number is an outreach-capacity decision, not a qualification target.

Therefore:

- upstream qualification remains independent of volume;
- Golden selection may be exactly 1,000;
- only people meeting the Golden minimum standard may compete;
- if fewer than 1,000 meet the minimum standard, do not lower the standard;
- replenish upstream through SOP 1 -> SOP 2 -> SOP 3 and rerun Golden selection.

## What Golden means

`GOLDEN_SELECTED` does not mean "valid person."

SOP 3 already established validity.

Golden means:

> **This person is one of the strongest 1,000 commercially useful and practically reachable stakeholders in the entire validated pool for the current campaign cycle.**

---

# 00. Document Control

## 00.1 Purpose

This SOP governs:

- Golden eligibility;
- comparative ranking;
- account-person prioritisation;
- stakeholder diversity;
- marginal-value checks;
- transparent score construction;
- tie-breaking;
- final 1,000 selection;
- final freshness/validation lock;
- replacement logic;
- handoff to outreach operations.

## 00.2 This SOP does not

SOP 4 does not:

- discover new accounts;
- discover new people;
- redo full SOP 1 research;
- redo full SOP 2 buying-group research;
- redo full SOP 3 validation;
- enrich paid email/phone data;
- lower quality to complete 1,000;
- create a "Super 200" or any branded tier below the Golden 1,000.

## 00.3 Core operating question

> **Among all already validated people, which 1,000 deserve limited relationship-development capacity first?**

## 00.4 Unique-human rule

The final Golden 1,000 must contain exactly:

**1,000 unique canonical people.**

Not 1,000 rows.

One system executive linked to multiple hospitals still counts as one person.

---

# 01. Golden Minimum Standard

A person may compete for Golden selection only when every mandatory condition below is true.

## 01.1 Mandatory Golden conditions

1. `validation_status = VALIDATED_PASS`
2. `handoff_ready = true`
3. canonical person is unique
4. current employment is confirmed
5. account/entity match is valid
6. current title/function is validated
7. role scope is validated
8. primary use case is valid
9. commercial role is one of:
   - `DIRECT_OWNER`
   - `CO_OWNER`
   - `TECHNICAL_EVALUATOR`
   - `CLINICAL_EVALUATOR`
   - `EXECUTIVE_SPONSOR`
   - `INTERNAL_ROUTE`
10. validated priority is P1, P2, or P3
11. no unresolved material conflict
12. evidence confidence is sufficient for SOP 3 PASS
13. LinkedIn profile remains valid
14. LinkedIn activity status is one of:
   - `ACTIVE`
   - `INACTIVE`
   - `UNKNOWN`

## 01.2 Additional Golden rule for `INTERNAL_ROUTE`

A pure `INTERNAL_ROUTE` person may enter Golden only when they add clear account-level value that is not already represented by stronger owners/evaluators.

Do not fill Golden with generic internal routes.

## 01.3 LinkedIn inactivity

`INACTIVE` does not make a person Golden-ineligible.

`UNKNOWN` does not make a person Golden-ineligible.

LinkedIn activity is a small reachability factor, not a replacement for commercial relevance.

---

# 02. Golden Selection Philosophy

## 02.1 Account + person, not person alone

Golden ranking must evaluate the combination:

> **Account quality x use-case strength x stakeholder quality**

A perfect title inside a weak account should not automatically outrank a strong problem owner inside a highly attractive account.

## 02.2 Problem ownership before title prestige

A Telemetry Director who directly owns U1 may outrank a CIO.

A Clinical Engineering leader who directly owns U2 may outrank a generic C-suite executive.

## 02.3 Reachability after relevance

LinkedIn activity should help separate otherwise comparable people.

It must not rescue a weak stakeholder.

## 02.4 Buying-group value

Golden selection should represent commercially useful stakeholder combinations.

Do not select five similar IT executives while leaving out:

- telemetry;
- nursing;
- clinical engineering;
- informatics;
- virtual care;
- executive sponsorship;

when those functions are relevant to the account's use case.

## 02.5 Marginal value

Every additional person selected from the same account must add something.

Examples:

- distinct problem ownership;
- distinct clinical influence;
- distinct technical influence;
- distinct executive sponsorship;
- distinct facility/system scope.

A near-duplicate stakeholder from the same narrow function has low marginal value.

---

# 03. Golden Ranking Dimensions

Golden uses separate dimensions.

A composite score may be calculated for consistent ranking, but the component scores must remain visible.

A high composite score can never override a failed mandatory Golden condition.

## 03.1 Account Quality - 20 points

Based on SOP 1 priority.

| SOP 1 priority | Points |
|---|---:|
| `A_PRIORITY` | 20 |
| `B_PRIORITY` | 15 |
| `PASS_UNRANKED` | 14 |

`PASS_UNRANKED` is not treated as bad. It simply had insufficient evidence for a fair A/B distinction.

## 03.2 Use-Case Strength - 15 points

Golden evaluator uses stored SOP 1 evidence only.

| Use-case evidence | Points |
|---|---:|
| Direct, current, account-specific evidence | 15 |
| Direct structural evidence with no strong current timing signal | 12 |
| Credible supported use case, less direct/current | 9 |

Do not invent a stronger use case during SOP 4.

If the stored use case is materially questionable, return the record to SOP 3/SOP 1 as appropriate.

## 03.3 Problem Ownership - 20 points

| Validated commercial role | Points |
|---|---:|
| `DIRECT_OWNER` | 20 |
| `CO_OWNER` | 18 |
| `CLINICAL_EVALUATOR` | 15 |
| `TECHNICAL_EVALUATOR` | 15 |
| `EXECUTIVE_SPONSOR` | 11 |
| `INTERNAL_ROUTE` | 7 |

## 03.4 Commercial / Evaluation Influence - 15 points

Normalize SOP 3 influence fields into:

| Influence | Points |
|---|---:|
| `HIGH` | 15 |
| `MEDIUM` | 10 |
| `LOW` | 5 |

A `LOW` score does not automatically reject an otherwise eligible record, but it makes Golden selection less likely.

## 03.5 Validated Priority - 10 points

| SOP 3 validated priority | Points |
|---|---:|
| `P1` | 10 |
| `P2` | 7 |
| `P3` | 4 |

## 03.6 Current Signal / Timing - 8 points

Inherited from SOP 1.

| Current signal | Points |
|---|---:|
| `STRONG` | 8 |
| `PRESENT` | 5 |
| `NONE_FOUND` | 2 |

No public current signal does not invalidate strong structural fit.

## 03.7 Evidence Confidence / Freshness - 7 points

| Validation evidence | Points |
|---|---:|
| Strong current evidence, no material conflict | 7 |
| Sufficient validated evidence, minor non-material limitations | 5 |
| Minimum acceptable validated evidence | 3 |

A material unresolved conflict is not scoreable; return to SOP 3.

## 03.8 LinkedIn Reachability - 5 points

| Activity status | Points |
|---|---:|
| `ACTIVE` | 5 |
| `INACTIVE` | 2 |
| `UNKNOWN` | 1 |

This is deliberately a small part of the score.

## 03.9 Total comparative score

Maximum:

`100`

Field:

`golden_priority_score`

Important:

The score is for ordering eligible people.

It is not a qualification gate by itself.

---

# 04. Golden Eligibility vs Golden Ranking

## 04.1 Eligibility comes first

First determine:

`golden_eligible = true / false`

Only eligible people receive a comparative ranking.

## 04.2 Ranking comes second

Rank eligible people using:

- component scores;
- marginal account value;
- buying-group diversity;
- tie-break rules.

## 04.3 No automatic top-third rule

Do not say:

> "Take the top 33.33%."

The validated pool size may vary.

Golden selection is exactly 1,000 only after minimum standards are met.

---

# 05. Account-Level Buying-Group Rules

## 05.1 Core account representation

For strong accounts, first look for the best available combination of:

1. primary problem owner;
2. clinical/nursing stakeholder;
3. technical/integration stakeholder;
4. executive sponsor/operating authority;

plus additional roles that materially matter to the inherited use case.

## 05.2 No forced number per account

There is no fixed account quota.

A small critical-access hospital may contribute 3-5 Golden people.

A complex regional system may justify more.

The number is determined by stakeholder value.

## 05.3 Same-function concentration

After the strongest person from a narrow function is selected, additional people from the same function must add a clearly distinct scope or buying role.

Examples that may justify both:

- facility Telemetry Director + system Telemetry Executive;
- Clinical Engineering Director + system VP HTM with different authority;
- hospital CNO + system CNO where both materially influence adoption.

Examples that usually do not justify multiple Golden slots:

- CIO + VP IT + IT Director + Infrastructure Director + Network Director for a U1 telemetry problem.

## 05.4 Marginal-value classification

For each candidate within an account assign:

- `HIGH_INCREMENTAL_VALUE`
- `MEDIUM_INCREMENTAL_VALUE`
- `LOW_INCREMENTAL_VALUE`

### `HIGH_INCREMENTAL_VALUE`

Adds a distinct essential buying-group role or distinct authority scope.

### `MEDIUM_INCREMENTAL_VALUE`

Useful complementary stakeholder but role is partially represented.

### `LOW_INCREMENTAL_VALUE`

Mostly duplicates an already selected function, influence type, or scope.

When scores are similar, prefer the person with higher incremental value.

---

# 06. Golden Selection Pipeline

Run sequentially.

# Gate G0 - Input Integrity

**Question:**  
Is this a complete SOP 3 VALIDATED_PASS record?

**PASS**
Yes.

**RETURN_TO_SOP3**
Missing validation fields, stale lock, or unresolved conflict.

No other input may continue.

---

# Gate G1 - Unique Canonical Person

**Question:**  
Is this a unique canonical human?

**PASS**
Unique canonical person.

**DO NOT COUNT**
Duplicate row or duplicate account representation.

The final 1,000 is counted by `canonical_person_id`.

---

# Gate G2 - Golden Minimum Standard

Check Section 01.

**PASS**
`golden_eligible = true`

**NOT ELIGIBLE**
Record remains valid data but does not compete for this Golden cycle.

Do not convert "not Golden" into "bad person."

---

# Gate G3 - Account Quality

Assign Account Quality component using stored SOP 1 data.

Do not redo account research.

If a material account contradiction appears:

`RETURN_TO_SOP3` or `RETURN_TO_SOP1` through the validation workflow.

---

# Gate G4 - Person Value

Assign:

- Problem Ownership;
- Commercial/Evaluation Influence;
- Validated Priority;
- Evidence Confidence.

Store every component separately.

---

# Gate G5 - Timing and Reachability

Assign:

- Current Signal;
- LinkedIn Reachability.

Do not let `ACTIVE` override weak account/person fit.

---

# Gate G6 - Marginal Stakeholder Value

Compare the person against other eligible people from the same account.

Assign:

- `HIGH_INCREMENTAL_VALUE`
- `MEDIUM_INCREMENTAL_VALUE`
- `LOW_INCREMENTAL_VALUE`

A high raw score with low incremental value may rank below a slightly lower-scoring person who adds an essential missing function.

---

# Gate G7 - Global Comparative Ranking

Calculate `golden_priority_score`.

Then rank the complete eligible unique-person pool.

Tie-breaking order:

1. higher Problem Ownership;
2. higher Account Quality;
3. stronger Use-Case Strength;
4. higher Validated Priority;
5. higher Commercial/Evaluation Influence;
6. higher Incremental Value;
7. stronger Current Signal;
8. stronger Evidence Confidence;
9. LinkedIn `ACTIVE` before `INACTIVE`, then `UNKNOWN`.

LinkedIn activity is intentionally the last tie-breaker.

---

# Gate G8 - Buying-Group Balance Review

Before locking the 1,000, inspect account-level composition.

Reject selection patterns where:

- one narrow function crowds out clearly more useful complementary functions;
- multiple near-duplicate stakeholders from one account consume capacity;
- system-level executive duplication is present;
- P3/internal-route people displace stronger direct owners/evaluators without a clear reason.

Adjust only by applying the stated marginal-value and role-diversity rules.

Do not manually "favorite" accounts.

---

# Gate G9 - Golden Freshness Lock

Before final selection is locked:

- confirm SOP 3 validation belongs to the current campaign cycle;
- confirm no known material change has appeared since validation;
- confirm LinkedIn URL still resolves to the same person;
- confirm person has not been returned to SOP 3.

If any material freshness issue appears:

`RETURN_TO_SOP3`

Do not fix it casually inside SOP 4.

---

# Gate G10 - Final 1,000 Selection

If at least 1,000 people meet the Golden minimum standard:

1. rank all eligible unique people;
2. apply buying-group and marginal-value rules;
3. select exactly the strongest 1,000;
4. set:
   - `GOLDEN_SELECTED` for ranks 1-1000;
   - `ELIGIBLE_NOT_SELECTED` for eligible people below rank 1000.

If fewer than 1,000 meet the Golden minimum standard:

- do not lower the standard;
- identify shortage pattern;
- request additional upstream research/validation;
- rerun Golden selection when new VALIDATED_PASS records arrive.

---

# 07. Shortage / Replenishment Logic

If Golden-eligible pool is below 1,000, diagnose why.

Controlled shortage reasons:

- `SHORTAGE_HIGH_FIT_ACCOUNTS`
- `SHORTAGE_DIRECT_OWNERS`
- `SHORTAGE_TECHNICAL_EVALUATORS`
- `SHORTAGE_CLINICAL_STAKEHOLDERS`
- `SHORTAGE_VALIDATED_CURRENT_ROLES`
- `SHORTAGE_ENTITY_CLEAN_RECORDS`
- `SHORTAGE_USE_CASE_DIVERSITY`
- `SHORTAGE_OTHER`

Then send a precise replenishment request upstream.

Example:

> "Golden pool lacks sufficient U2 direct owners in A/B priority regional systems. Add new qualified accounts and Clinical Engineering/Clinical Systems owners through SOP 1 -> SOP 2 -> SOP 3. Do not lower Golden thresholds."

Do not tell upstream:

> "Find 100 more people."

Tell them what quality gap exists.

---

# 08. Final Golden Statuses

## `GOLDEN_SELECTED`

Person is one of the final 1,000.

## `ELIGIBLE_NOT_SELECTED`

Person is valid and Golden-eligible but falls below the final 1,000 for the current cycle.

This is not a rejection.

Do not create a branded second tier such as "Super 200."

## `RETURN_TO_SOP3`

A material validation/freshness issue appeared.

Person cannot be ranked until resolved.

---

# 09. Required Golden Output Schema

## 09.1 Identity

- `canonical_person_id`
- `person_id`
- `account_id`
- `full_name`
- `linkedin_profile_url`

## 09.2 Current validated role

- `validated_current_title`
- `validated_department`
- `validated_role_family`
- `role_scope`
- `validated_commercial_role`
- `validated_priority`

## 09.3 Account context

- `account_priority`
- `account_archetype`
- `primary_use_case`
- `current_signal`

## 09.4 Golden dimensions

- `account_quality_score`
- `use_case_strength_score`
- `problem_ownership_score`
- `commercial_influence_score`
- `validated_priority_score`
- `current_signal_score`
- `evidence_confidence_score`
- `linkedin_reachability_score`
- `golden_priority_score`

## 09.5 Account-composition fields

- `incremental_value`
- `role_family_already_represented`
- `distinct_scope_value`
- `buying_group_contribution`

## 09.6 Activity

- `linkedin_activity_status`
- `last_visible_reaction_date`
- `linkedin_activity_checked_at`

## 09.7 Final decision

- `golden_eligible`
- `golden_rank`
- `golden_status`
- `golden_selection_reason`
- `golden_exclusion_reason`
- `golden_locked_at`

---

# 10. Golden Selection Reason

Every `GOLDEN_SELECTED` record should have one concise reason.

Format:

> **[Account strength] + [person ownership/influence] + [use-case relevance] + [timing/reachability where useful].**

Example:

> A-priority regional system; direct telemetry workflow owner for U1; P1; strong current monitoring signal; active LinkedIn.

Do not write generic reasons such as:

> "Good prospect."

---

# 11. Golden Exclusion Reason

For `ELIGIBLE_NOT_SELECTED`, use controlled reasons where useful:

- `LOWER_GLOBAL_RANK`
- `LOW_INCREMENTAL_ACCOUNT_VALUE`
- `SAME_FUNCTION_ALREADY_STRONGLY_COVERED`
- `WEAKER_THAN_OTHER_ACCOUNT_STAKEHOLDERS`
- `P3_DISPLACED_BY_DIRECT_OWNER`
- `LOWER_ACCOUNT_PRIORITY`
- `LOWER_USE_CASE_STRENGTH`

Do not call these records bad leads.

They are simply not in the current 1,000.

---

# 12. Role-Diversity Logic by Use Case

These are selection guides, not quotas.

## U1 - Digital Rhythm Workflow

Strong Golden mix often includes:

- Telemetry / Cardiac Monitoring owner;
- Nursing leadership;
- Nursing Informatics / CNIO;
- Clinical Engineering;
- CIO / Clinical Systems;
- executive sponsor where useful.

Direct telemetry ownership should normally outrank generic IT seniority.

## U2 - Device/EHR Interoperability

Strong mix often includes:

- Clinical Engineering / HTM;
- Clinical Systems / Integration;
- CIO / VP IT;
- Clinical Informatics;
- CNIO / Nursing Informatics;
- executive sponsor where useful.

## U3 - Centralized Monitoring

Strong mix often includes:

- Central Monitoring / Telemetry owner;
- CNO / Nursing leadership;
- Virtual Care / Command Center;
- Clinical Engineering;
- CIO / Clinical Systems;
- operations sponsor.

## U4 - Remote Specialist / Tele-ICU

Strong mix often includes:

- Virtual Care / Tele-ICU leader;
- CNO;
- Critical Care leadership;
- CMIO / Clinical Informatics;
- CIO / Clinical Systems;
- executive/operations sponsor.

## U5 - Automated Documentation

Strong mix often includes:

- CNIO / Nursing Informatics;
- Telemetry / Nursing operations;
- Clinical Systems;
- Clinical Informatics;
- CNO;
- Clinical Engineering where device-data flow is material.

---

# 13. LinkedIn Reachability Treatment

## 13.1 ACTIVE

At least one visible reaction in the previous 12 months.

Score:

5/5.

## 13.2 INACTIVE

Successful check, zero visible reactions.

Score:

2/5.

May still be Golden.

## 13.3 UNKNOWN

Reliable activity result unavailable.

Score:

1/5.

May still be Golden.

## 13.4 Hard rule

Never select a weaker VP merely because they are ACTIVE over a materially stronger DIRECT_OWNER who is INACTIVE.

Relevance wins.

---

# 14. Final Freshness and Lock Rules

## 14.1 Current-cycle validation

Every Golden person must have SOP 3 validation belonging to the current campaign cycle.

## 14.2 Material changes

If any known material change occurs before outreach lock:

- employer change;
- title/function change affecting relevance;
- account/entity change;
- duplicate discovery;
- LinkedIn profile identity issue;

return the person to SOP 3.

## 14.3 Locked dataset

Once final 1,000 is approved:

set:

`golden_locked_at`

and export a locked version.

Any replacement after lock must be logged.

---

# 15. Replacement Logic

A Golden person may require replacement when:

- leaves organisation;
- profile identity becomes invalid;
- new conflict emerges;
- account becomes protected/unavailable;
- role changes and loses relevance;
- duplicate discovered.

Replacement process:

1. remove affected person from locked Golden set;
2. send affected record to SOP 3;
3. promote the highest-ranked currently eligible unique person that preserves account/buying-group logic;
4. log replacement;
5. Golden set returns to exactly 1,000.

Do not rerank casually for minor cosmetic changes.

---

# 16. No Outreach Execution in SOP 4

SOP 4 selects and prioritises people.

It does not:

- send connection requests;
- send InMails;
- write messages;
- assign daily outreach;
- enrich phone/email;
- schedule meetings.

Those are downstream campaign operations.

---

# 17. Automation Architecture

## 17.1 INPUT LOAD

Load all SOP 3 `VALIDATED_PASS` records.

## 17.2 CANONICAL UNIQUE-PERSON CHECK

Remove duplicate rows from selection counts.

## 17.3 GOLDEN ELIGIBILITY

Apply mandatory Golden conditions.

## 17.4 DIMENSION SCORING

Calculate all visible component scores.

## 17.5 ACCOUNT COMPOSITION

Calculate role-family representation and incremental stakeholder value.

## 17.6 GLOBAL RANKING

Rank eligible unique people.

## 17.7 BALANCE REVIEW

Apply buying-group/marginal-value rules.

## 17.8 FRESHNESS LOCK

Return stale/conflicted records to SOP 3.

## 17.9 FINAL 1,000

Lock exactly 1,000 unique people.

## 17.10 STORAGE

Persist:

- component scores;
- final score;
- rank;
- status;
- selection/exclusion reason;
- lock timestamp.

---

# 18. AI Usage Rules

AI may:

- calculate Golden component scores;
- compare stakeholder relevance;
- classify incremental value;
- identify same-function overconcentration;
- rank eligible unique people;
- generate selection reasons;
- diagnose Golden shortages;
- recommend upstream replenishment categories.

AI must not:

- invent new account evidence;
- invent new person responsibilities;
- change a person from VALIDATED_REJECT to Golden;
- override unresolved SOP 3 conflict;
- make LinkedIn activity a major relevance factor;
- select duplicate humans as separate Golden people;
- lower Golden standards to reach 1,000;
- create a Super 200 or extra branded tier.

---

# 19. Human QA Triggers

Human review is required when:

- more than one person has effectively identical score and account role;
- a P3 is selected over a strong P1/P2 from the same account;
- several same-function people from one account are selected;
- a system-level executive represents multiple accounts;
- a low-incremental-value candidate sits inside the provisional top 1,000;
- a material freshness issue appears;
- an `INTERNAL_ROUTE` person enters Golden despite stronger account stakeholders;
- upstream replenishment is required.

---

# 20. Tie-Break Rules

When `golden_priority_score` is equal, use this order:

1. higher Problem Ownership;
2. higher Account Quality;
3. higher Use-Case Strength;
4. P1 over P2 over P3;
5. higher Commercial/Evaluation Influence;
6. higher Incremental Value;
7. stronger Current Signal;
8. stronger Evidence Confidence;
9. `ACTIVE` over `INACTIVE` over `UNKNOWN`.

No other hidden tie-break rule is allowed.

---

# 21. Metrics and Feedback Loop

Track:

- number of SOP 3 VALIDATED_PASS records entering;
- number Golden-eligible;
- number not Golden-eligible;
- exactly 1,000 Golden selected;
- unique-person count;
- A/B/PASS_UNRANKED account mix;
- P1/P2/P3 mix;
- role-family mix;
- use-case mix;
- account-archetype mix;
- ACTIVE/INACTIVE/UNKNOWN mix;
- direct-owner share;
- technical-evaluator share;
- clinical-evaluator share;
- executive-sponsor share;
- same-account concentration;
- low-incremental-value selections;
- replacements after lock;
- RETURN_TO_SOP3 rate;
- downstream acceptance/reply/meeting performance by:
  - role family;
  - use case;
  - account priority;
  - activity status;
  - Golden score band.

## Feedback principle

Use campaign outcomes to improve upstream research and Golden weighting.

Do not change weighting after one anecdotal response.

Use meaningful batch evidence.

---

# 22. Common Failure Modes

| Error | Why dangerous | Correction |
|---|---|---|
| Top 1,000 by title seniority | Misses real problem owners | Use ownership and use-case scoring |
| Top 1,000 by one black-box score | Hides weak dimensions | Keep component scores visible |
| Active LinkedIn bias | Reachability replaces commercial relevance | Activity only 5% |
| Too many people from one account/function | Wastes capacity | Apply incremental-value review |
| Duplicate humans counted twice | Inflates Golden size | Canonical-person rule |
| P3 beats P1 because of prestige | Weak first-contact set | Priority and ownership rules |
| Weak account + famous executive | Person prestige hides account weakness | Account-person combination |
| Lowering standard to reach 1,000 | Corrupts dataset | Upstream replenishment |
| Golden discovers former employee | SOP 3 failure | Return and tighten validation |
| Creating Super 200 | Unnecessary extra tier | Stop at Golden 1,000 |

---

# 23. Worked Examples

All examples are fictional.

## 23.1 Direct owner beats active executive

Account:
A_PRIORITY community acute hospital.

Primary use case:
U1.

Candidate A:
Director of Telemetry
- DIRECT_OWNER
- P1
- INACTIVE

Candidate B:
VP IT
- TECHNICAL_EVALUATOR
- P2
- ACTIVE

Golden result:
Candidate A ranks above Candidate B unless other material evidence strongly changes the account-specific buying logic.

Reason:
Problem ownership outweighs activity.

---

## 23.2 Complementary buying group

Regional system, U2.

Eligible people:

- VP Clinical Engineering - P1
- Director Clinical Systems - P1/P2
- CIO - P2
- CNIO - P2
- CNO - P3
- IT Infrastructure Director - P3
- Network Director - P3

Golden selection from the account should favor:

- VP Clinical Engineering
- Director Clinical Systems
- CIO
- CNIO
- possibly CNO

before filling capacity with multiple infrastructure/network roles.

---

## 23.3 System-level duplicate

System CIO appears under four hospitals.

SOP 3 canonicalized to one person.

Golden counts:

1 unique person.

Related accounts remain attached to the same canonical record.

---

## 23.4 Strong account, no public current signal

A_PRIORITY account.

Clear U3 structural fit.

Direct Central Monitoring leader.

`CURRENT_SIGNAL = NONE_FOUND`

Person may still rank highly because structural fit + direct ownership are strong.

---

## 23.5 Active but weak internal route

P3 executive.

`INTERNAL_ROUTE`

ACTIVE.

Account already has:

- direct problem owner;
- clinical evaluator;
- technical evaluator;
- executive sponsor.

The route adds little incremental value.

Likely:

`ELIGIBLE_NOT_SELECTED`

---

## 23.6 Only 930 meet Golden minimum standard

Do not select the next 70 weaker people.

Output shortage diagnosis.

Replenish upstream.

Rerun SOP 4.

Stop only when 1,000 genuine Golden people exist.

---

# 24. AI Execution Contract

```text
You are executing SOP 4 - Golden 1,000 Selection & Final Validation.

INPUT:
Only SOP 3 VALIDATED_PASS records with handoff_ready = true.

OBJECTIVE:
Select exactly 1,000 UNIQUE canonical people who provide the strongest combination of account quality, use-case relevance, direct problem ownership, commercial/evaluation influence, validated priority, timing, evidence confidence, practical LinkedIn reachability, and buying-group value.

DO NOT:
- discover new accounts;
- discover new people;
- redo full SOP 1/2/3 research;
- count duplicate humans twice;
- use LinkedIn activity as a major relevance factor;
- lower quality to reach 1,000;
- create a Super 200.

FIRST APPLY GOLDEN MINIMUM STANDARD.

Only eligible people may be ranked.

RANKING DIMENSIONS:
Account Quality = 20
Use-Case Strength = 15
Problem Ownership = 20
Commercial/Evaluation Influence = 15
Validated Priority = 10
Current Signal = 8
Evidence Confidence = 7
LinkedIn Reachability = 5

Maximum = 100.

Keep every component visible.

A high total score never overrides a failed mandatory condition.

LINKEDIN:
ACTIVE = 5
INACTIVE = 2
UNKNOWN = 1

Activity is a small reachability factor.
A stronger direct owner who is INACTIVE should normally outrank a weaker ACTIVE executive.

BUYING-GROUP RULE:
For each account, prefer complementary functions.
Every additional same-account person must add distinct ownership, evaluation, sponsorship, or scope value.

MARGINAL VALUE:
HIGH_INCREMENTAL_VALUE
MEDIUM_INCREMENTAL_VALUE
LOW_INCREMENTAL_VALUE

GLOBAL TIE-BREAK ORDER:
1. Problem Ownership
2. Account Quality
3. Use-Case Strength
4. P1 > P2 > P3
5. Commercial/Evaluation Influence
6. Incremental Value
7. Current Signal
8. Evidence Confidence
9. ACTIVE > INACTIVE > UNKNOWN

FINAL STATUS:
GOLDEN_SELECTED
ELIGIBLE_NOT_SELECTED
RETURN_TO_SOP3

FINAL COUNT:
If >= 1,000 people meet Golden minimum standard:
select exactly the strongest 1,000 unique people.

If < 1,000 meet Golden minimum standard:
do not lower the standard.
Diagnose the shortage and request targeted upstream replenishment through SOP 1 -> SOP 2 -> SOP 3.

Before lock:
confirm all selected records remain current-cycle VALIDATED_PASS records with no known material change.

OUTPUT:
Return deterministic Golden JSON for every eligible person and a final Golden summary containing exactly 1,000 unique canonical person IDs.
```

# 25. Canonical Golden JSON

```json
{
  "canonical_person_id": "",
  "person_id": "",
  "account_id": "",
  "full_name": "",
  "linkedin_profile_url": "",
  "validated_current_title": "",
  "validated_department": "",
  "validated_role_family": "",
  "role_scope": "",
  "validated_commercial_role": "",
  "validated_priority": "",
  "account_priority": "",
  "account_archetype": "",
  "primary_use_case": "",
  "current_signal": "",
  "linkedin_activity_status": "",
  "last_visible_reaction_date": null,
  "scores": {
    "account_quality_score": 0,
    "use_case_strength_score": 0,
    "problem_ownership_score": 0,
    "commercial_influence_score": 0,
    "validated_priority_score": 0,
    "current_signal_score": 0,
    "evidence_confidence_score": 0,
    "linkedin_reachability_score": 0,
    "golden_priority_score": 0
  },
  "incremental_value": "",
  "role_family_already_represented": false,
  "distinct_scope_value": "",
  "buying_group_contribution": "",
  "golden_eligible": false,
  "golden_rank": null,
  "golden_status": "",
  "golden_selection_reason": "",
  "golden_exclusion_reason": null,
  "golden_locked_at": null
}
```

# 26. Final Golden Summary JSON

```json
{
  "selection_cycle": "",
  "validated_input_unique_people": 0,
  "golden_eligible_unique_people": 0,
  "golden_selected_unique_people": 1000,
  "golden_person_ids": [],
  "shortage_status": "NONE",
  "shortage_reasons": [],
  "return_to_sop3_count": 0,
  "locked_at": "",
  "qa_status": ""
}
```

# 27. FINAL SELF-QA CHECKLIST

Before locking Golden 1,000:

- [ ] Every input is SOP 3 VALIDATED_PASS?
- [ ] Every selected record has handoff_ready = true?
- [ ] Final list contains 1,000 unique canonical people?
- [ ] No duplicate human counted twice?
- [ ] Every selected person meets Golden minimum standard?
- [ ] No unresolved material conflict?
- [ ] Account/entity match remains valid?
- [ ] Current role remains validated?
- [ ] Primary use case is inherited and still valid?
- [ ] Problem ownership scored correctly?
- [ ] Commercial/evaluation influence scored?
- [ ] Validated P1/P2/P3 used?
- [ ] Current signal scored?
- [ ] Evidence confidence scored?
- [ ] LinkedIn activity scored only as a small reachability factor?
- [ ] INACTIVE person was not automatically excluded?
- [ ] UNKNOWN activity was not automatically excluded?
- [ ] Buying-group diversity reviewed?
- [ ] Same-function concentration reviewed?
- [ ] Incremental value assigned?
- [ ] System-level duplicates canonicalized?
- [ ] Tie-break rules applied consistently?
- [ ] No hidden/manual preference changed the ranking?
- [ ] Current-cycle freshness lock completed?
- [ ] Any material issue returned to SOP 3?
- [ ] If fewer than 1,000 met the standard, upstream replenishment requested instead of lowering quality?
- [ ] No Super 200 or additional branded tier created?
- [ ] Final dataset locked and timestamped?

The Golden 1,000 is complete only when all mandatory checks pass and the locked output contains exactly 1,000 unique canonical people.
