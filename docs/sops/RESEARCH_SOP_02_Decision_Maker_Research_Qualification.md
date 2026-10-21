---
document_id: SOP-02-DECISION-MAKER-RESEARCH-QUALIFICATION
document_type: RESEARCH_SOP
title: "SOP 2 - Decision-Maker Research & Qualification"
version: "1.0"
status: "Production Draft"
last_updated: "2026-09-12"
scope: "Decision-maker discovery and initial qualification inside SOP 1 PASS accounts"
input_requirement: "SOP 1 qualification_status = PASS and handoff_ready = true"
decision_vocabulary:
  - PERSON_PASS
  - REVIEW
  - REJECT
person_priority_vocabulary:
  - P1_CANDIDATE
  - P2_CANDIDATE
  - P3_CANDIDATE
primary_handoff: "SOP 3 - Independent Data Validation & QA"
source_of_truth: "Stored current person evidence and role-to-problem mapping"
volume_policy: "No fixed total-person PASS quota and no forced number of people per account."
---

# ASSIGNMENT INTERPRETATION

## Target input

Only accounts that have already passed SOP 1.

Every incoming account must contain:

- verified account identity;
- account archetype;
- primary U1-U5 use case;
- relevant Core Signal;
- relevant Supporting Signal;
- relationship-overlap clearance;
- qualification evidence;
- concise account rationale.

If any of these are absent, return the account to SOP 1. Do not reconstruct account qualification inside SOP 2.

## Research objective

For every qualified account, identify the strongest commercially relevant people who collectively represent the likely buying and evaluation group for the account's primary use case.

The objective is not to find the most senior executives.

The objective is to identify people who:

- own the operating problem;
- supervise the affected workflow;
- evaluate relevant technology;
- influence technical or clinical adoption;
- sponsor change;
- control or influence implementation;
- can route a credible internal discussion.

## Expected account coverage

Typical account:

**up to approximately 10-12 relevant people.**

This is not a quota.

A small hospital may legitimately produce 6-8 strong people.

A complex regional health system may justify 10-12.

Never add a weak person simply to reach 10 or 12.

## LinkedIn requirement

This dataset is being built for LinkedIn relationship development.

Therefore every `PERSON_PASS` must have a confidently matched LinkedIn profile URL.

SOP 2 verifies:

- correct profile;
- correct person;
- correct employer;
- current role appears valid.

SOP 2 does **not** evaluate LinkedIn activity.

The 12-month reaction activity rule belongs to SOP 3.

## Product context

The underlying platform is relevant to hospital environments involving real-time vitals and waveforms, alarms and events, digital rhythm strips, multi-vendor device integration, centralized monitoring, remote monitoring and EHR-connected workflows.

Decision-makers must therefore be selected based on ownership or influence over these workflows, not simply general healthcare seniority.

---

# 00. Document Control

## 00.1 Purpose

This SOP governs:

- person discovery;
- identity matching;
- current-role verification;
- functional qualification;
- role-to-problem mapping;
- buying-group construction;
- initial P1/P2/P3 classification;
- duplicate removal;
- evidence capture;
- handoff to independent validation.

## 00.2 This SOP does not

This SOP does not:

- requalify accounts;
- check LinkedIn reactions/activity;
- purchase email or phone enrichment;
- conduct final Golden selection;
- decide final outreach sequencing;
- lower person standards to achieve a total count.

## 00.3 Core operating question

> **Given the account's verified primary use case, is this person a current and materially relevant owner, evaluator, influencer, sponsor, or internal route for that specific problem?**

---

# 01. Purpose and Success Definition

## 01.1 Successful person record

A `PERSON_PASS` record must establish:

- correct identity;
- correct SOP 1 PASS account;
- current employment plausibly verified;
- current title;
- current function;
- relevant role bucket;
- defensible problem ownership or influence;
- clear relationship to primary account use case;
- valid LinkedIn profile;
- no duplicate;
- evidence stored;
- initial priority classification;
- no unresolved material contradiction.

## 01.2 What does not qualify

A person does not qualify simply because they are:

- CEO;
- CIO;
- CNO;
- VP;
- physician;
- senior;
- hospital administrator;
- technology executive;
- active on LinkedIn;
- listed in Sales Navigator.

Title prestige is not sufficient.

## 01.3 Core qualification question

> **Would this person naturally participate in, influence, evaluate, sponsor, implement, or route a discussion about the account's specific U1-U5 problem?**

If the answer depends only on seniority, the person is not sufficiently qualified.

---

# 02. Business / Product Understanding

Researchers must inherit the account's primary use case.

They must not independently invent a different commercial thesis unless new person-level research reveals a material account contradiction.

The five approved use cases are:

| Code | Use case |
|---|---|
| `U1_DIGITAL_RHYTHM_WORKFLOW` | Digital telemetry / rhythm-strip workflow |
| `U2_DEVICE_EHR_INTEROPERABILITY` | Multi-vendor device and EHR integration |
| `U3_CENTRALIZED_MONITORING` | Centralized / cross-site monitoring |
| `U4_REMOTE_SPECIALIST_TELE_ICU` | Remote specialist / tele-ICU coverage |
| `U5_AUTOMATED_DOCUMENTATION` | Monitoring/documentation automation |

Decision-maker research must remain tied to the inherited use case.

---

# 03. Decision-Maker ICP

A person is a decision-maker candidate only when their **current function** maps to the account's primary problem.

## 03.1 Approved role families

Controlled values:

- `TELEMETRY_CARDIAC_MONITORING`
- `NURSING_EXECUTIVE`
- `NURSING_INFORMATICS`
- `CLINICAL_ENGINEERING_HTM`
- `IT_CIO`
- `CLINICAL_SYSTEMS_INTEGRATION`
- `CLINICAL_INFORMATICS`
- `VIRTUAL_CARE_TELEHEALTH`
- `CLINICAL_OPERATIONS`
- `CRITICAL_CARE_LEADERSHIP`
- `DOCUMENTATION_REVENUE_INTEGRITY`
- `EXECUTIVE_SPONSOR`

Do not create arbitrary role families.

## 03.2 Mandatory conditions

Every `PERSON_PASS` must have:

1. correct person identity;
2. correct current account;
3. current title/function reasonably verified;
4. valid LinkedIn profile;
5. relevant role family;
6. plausible U1-U5 relevance;
7. material problem ownership, evaluation influence, commercial influence, or internal-routing value;
8. no unresolved identity/employment conflict;
9. no duplicate record.

## 03.3 Preferred conditions

Preferred:

- directly owns affected workflow;
- runs relevant department;
- system-level scope for multi-site account;
- recent responsibility relevant to current initiative;
- named in official hospital project/program;
- combines operational ownership with buying influence.

## 03.4 Not required

Not required at SOP 2:

- public LinkedIn posting;
- recent LinkedIn reaction;
- email;
- phone;
- board membership;
- C-suite title;
- budget ownership explicitly proven.

---

# 04. Hard Person Exclusions

| Code | Condition | Decision |
|---|---|---|
| `P-R01_WRONG_COMPANY` | Person belongs to different organisation | REJECT |
| `P-R02_FORMER_EMPLOYEE` | Reliable current evidence shows person left account | REJECT |
| `P-R03_WRONG_FUNCTION` | Role does not materially relate to use case | REJECT |
| `P-R04_NO_PROBLEM_RELEVANCE` | Senior role but no defensible relationship to problem | REJECT |
| `P-R05_DUPLICATE_PERSON` | Same person already represented | REJECT duplicate |
| `P-R06_IDENTITY_AMBIGUOUS` | Same-name/profile ambiguity cannot be resolved | REVIEW then REJECT if unresolved |
| `P-R07_ROLE_CONFLICT` | Current role/employment evidence conflicts | REVIEW |
| `P-R08_INSUFFICIENT_INFLUENCE` | Role too disconnected/junior to influence or own relevant workflow | REJECT |
| `P-R09_EXTERNAL_ONLY` | Consultant/vendor/advisor not employed by account | REJECT |
| `P-R10_NO_LINKEDIN_PROFILE` | No confidently matched LinkedIn profile after defined search | REJECT from this LinkedIn dataset |
| `P-R11_BOARD_ONLY` | Board/advisory role without current operating responsibility | REJECT |
| `P-R12_WRONG_ENTITY_LEVEL` | Person is at parent/subsidiary unrelated to qualified account scope | REVIEW/REJECT |

---

# 05. Qualification Definitions

## `PROBLEM_OWNER`

Person directly responsible for the operating workflow affected by the primary use case.

Examples:

- Telemetry Director for rhythm-strip workflow;
- Clinical Engineering Director for device integration;
- Virtual Care leader for tele-ICU.

## `FUNCTIONAL_BUYER`

Functional leader whose department would adopt, supervise, or materially influence the solution.

## `TECHNICAL_EVALUATOR`

Person responsible for:

- integration;
- architecture;
- devices;
- clinical systems;
- security/technical implementation.

## `CLINICAL_EVALUATOR`

Person responsible for clinical workflow, nursing operations, informatics, monitoring, or patient-care implementation.

## `EXECUTIVE_SPONSOR`

Senior person capable of sponsoring cross-functional adoption but not necessarily the first contact.

## `CHAMPION_CANDIDATE`

Person close enough to the problem to care materially and influential enough to carry the discussion internally.

## `P1_CANDIDATE`

Best natural first-contact candidate for the account's specific problem.

Not necessarily the most senior person.

## `P2_CANDIDATE`

Complementary stakeholder who materially evaluates, implements, or co-owns the use case.

## `P3_CANDIDATE`

Executive sponsor, secondary functional stakeholder, or internal route useful after initial problem validation.

## `CURRENT_ROLE_VERIFIED`

Current employer and role are supported by sufficiently current evidence with no material contradiction.

## `CURRENT_ROLE_PROBABLE`

Current profile strongly suggests employment, but stronger independent verification is not yet available.

`CURRENT_ROLE_PROBABLE` cannot leave SOP 3 as fully validated until resolved.

---

# 06. Data Architecture and Entity Model

## 06.1 Entities

### `account`
Inherited from SOP 1.

### `person`
Unique human record.

### `role`
Current title/function at the qualified account.

### `role_evidence`
Evidence supporting current employment/title/function.

### `person_use_case_mapping`
Why the person matters to the primary account use case.

### `priority_assignment`
P1/P2/P3 candidate classification.

### `linkedin_identity`
Matched LinkedIn profile.

### `person_decision`
PERSON_PASS / REVIEW / REJECT.

## 06.2 Relationships

- One account may have multiple people.
- One person may have one primary role family.
- One person may support multiple use cases.
- One person must have exactly one initial priority classification.
- One account should have multiple complementary role families.
- Same person must not appear twice because of title variations.

---

# 07. Required Output Schema

## 07.1 Person identity fields

- `person_id`
- `account_id`
- `full_name`
- `linkedin_profile_url`
- `current_title`
- `current_company_display_name`
- `role_family`
- `department`
- `seniority_level`
- `location_if_available`

## 07.2 Qualification fields

- `primary_use_case`
- `person_use_case_relevance`
- `problem_ownership_level`
- `evaluation_influence`
- `commercial_influence`
- `technical_influence`
- `internal_routing_value`
- `initial_priority`
- `person_status`

## 07.3 Role-verification fields

`current_role_status`

Allowed values:

- `VERIFIED`
- `PROBABLE`
- `CONFLICT`
- `STALE`
- `UNKNOWN`

`employment_evidence_ids`

`title_evidence_ids`

`profile_identity_confidence`

Allowed values:

- `HIGH`
- `MEDIUM`
- `LOW`

## 07.4 LinkedIn fields

`linkedin_profile_url`

`linkedin_identity_status`

Allowed values:

- `MATCHED`
- `AMBIGUOUS`
- `NOT_FOUND`

`linkedin_activity_status`

Set only to:

`NOT_CHECKED`

SOP 2 must not classify LinkedIn activity.

## 07.5 Evidence fields

Every PERSON_PASS must retain:

- source URL;
- source title;
- source type;
- access date;
- source date where available;
- exact supporting evidence;
- claim supported.

## 07.6 Null handling

Use only:

- `UNKNOWN`
- `NOT_APPLICABLE`
- `NONE_FOUND`
- `NOT_CHECKED`

Do not leave required fields blank.

---

# 08. Evidence Standard

## Tier A1 - Official current organisational evidence

Examples:

- hospital leadership page;
- department leadership page;
- official staff directory;
- official hospital bio;
- official current program page.

Best for:

- current employment;
- title;
- department;
- operating responsibility.

## Tier A2 - Current first-party professional evidence

Examples:

- person's LinkedIn profile;
- official LinkedIn announcement;
- current conference bio from the person's organisation;
- recent hospital announcement.

Useful for:

- current title;
- function;
- role changes;
- profile identity.

## Tier B - Credible secondary evidence

Examples:

- professional association;
- recent conference program;
- reputable healthcare publication;
- board/committee biography;
- credible speaker profile.

Use for triangulation.

## Tier C - Discovery only

Examples:

- Apollo;
- ZoomInfo;
- RocketReach;
- Sales Navigator search result;
- database exports;
- people-data vendors.

May discover a person.

Tier C alone should not establish `CURRENT_ROLE_VERIFIED`.

---

# 09. People Discovery Channels

## 09.1 LinkedIn / Sales Navigator

Primary discovery channel.

Use account/company filters plus title/function searches.

Do not accept a person merely because Sales Navigator returns them.

Verify role relevance separately.

## 09.2 Hospital website

Use for:

- leadership;
- department heads;
- nursing;
- clinical engineering;
- informatics;
- virtual care;
- operations.

## 09.3 Search engine

Example queries:

- `"{ACCOUNT}" "Director of Telemetry"`
- `"{ACCOUNT}" "Clinical Engineering"`
- `"{ACCOUNT}" CIO`
- `"{ACCOUNT}" "Nursing Informatics"`
- `"{ACCOUNT}" "Virtual Care"`

## 09.4 Job / conference / association sources

Useful when:

- hospital site does not expose leadership;
- role responsibility is ambiguous;
- current person needs triangulation.

---

# 10. Search Query Library

Queries must derive from account use case.

## U1 - Digital Rhythm Workflow

- `"{ACCOUNT}" telemetry director`
- `"{ACCOUNT}" telemetry manager`
- `"{ACCOUNT}" cardiac monitoring director`
- `"{ACCOUNT}" cardiac services`
- `"{ACCOUNT}" nursing informatics`

## U2 - Device/EHR Interoperability

- `"{ACCOUNT}" clinical engineering director`
- `"{ACCOUNT}" HTM director`
- `"{ACCOUNT}" biomedical engineering`
- `"{ACCOUNT}" clinical systems director`
- `"{ACCOUNT}" integration director`
- `"{ACCOUNT}" CIO`
- `"{ACCOUNT}" clinical informatics`

## U3 - Centralized Monitoring

- `"{ACCOUNT}" central monitoring director`
- `"{ACCOUNT}" command center`
- `"{ACCOUNT}" telemetry director`
- `"{ACCOUNT}" virtual care`
- `"{ACCOUNT}" CNO`
- `"{ACCOUNT}" clinical engineering`

## U4 - Remote Specialist / Tele-ICU

- `"{ACCOUNT}" tele-ICU director`
- `"{ACCOUNT}" virtual critical care`
- `"{ACCOUNT}" virtual care director`
- `"{ACCOUNT}" CNO`
- `"{ACCOUNT}" critical care operations`
- `"{ACCOUNT}" CMIO`

## U5 - Automated Documentation

- `"{ACCOUNT}" nursing informatics`
- `"{ACCOUNT}" clinical informatics`
- `"{ACCOUNT}" telemetry manager`
- `"{ACCOUNT}" clinical systems`
- `"{ACCOUNT}" CNO`
- `"{ACCOUNT}" documentation integrity`

---

# 11. Person Qualification Pipeline

Qualification runs sequentially.

## Gate P0 - Input Account

**Exact question:**  
Is the account an SOP 1 PASS account with `handoff_ready = true`?

**PASS**  
Yes.

**RETURN**  
No.

Do not repair SOP 1 inside SOP 2.

---

## Gate P1 - Identity

**Question:**  
Can this human be uniquely identified?

**PASS**  
Full name + matched profile/entity.

**REVIEW**  
Same-name ambiguity.

**REJECT**  
Identity cannot be resolved.

---

## Gate P2 - Current Employment

**Question:**  
Does current evidence indicate the person still works at the qualified account?

**PASS**  
Current evidence supports employment.

**REVIEW**  
Only stale or conflicting evidence.

**REJECT**  
More recent evidence shows departure.

---

## Gate P3 - Current Function

**Question:**  
Is the person's actual current function understood?

**PASS**  
Title/function clearly maps to one role family.

**REVIEW**  
Title is ambiguous.

**REJECT**  
Function is unrelated.

Example:

`Director of Clinical Services`

cannot automatically be classified as telemetry, nursing, IT, or informatics.

Research what the role actually covers.

---

## Gate P4 - Use-Case Relevance

**Question:**  
Does this function materially relate to the account's primary U1-U5 use case?

**PASS**  
Clear direct or complementary relationship.

**REVIEW**  
Plausible but not adequately established.

**REJECT**  
Generic seniority only.

---

## Gate P5 - Problem Ownership / Influence

Classify:

- `DIRECT_OWNER`
- `CO_OWNER`
- `TECHNICAL_EVALUATOR`
- `CLINICAL_EVALUATOR`
- `EXECUTIVE_SPONSOR`
- `INTERNAL_ROUTE`
- `WEAK_RELEVANCE`

`WEAK_RELEVANCE` cannot receive PERSON_PASS.

---

## Gate P6 - LinkedIn Identity

**Question:**  
Is there a confidently matched LinkedIn profile?

**PASS**  
`MATCHED`.

**REVIEW**  
`AMBIGUOUS`.

**REJECT**  
No profile after defined searches.

Do not check activity here.

---

## Gate P7 - Better-Person Test

Ask:

> **Based on this use case and account structure, is another function or visible person materially more natural as the primary owner?**

If YES:

- current person cannot automatically be P1;
- person may remain P2/P3 when complementary;
- missing stronger function must be researched before account mapping is considered complete.

This gate prevents title-prestige bias.

---

## Gate P8 - Duplicate Check

Check:

- same LinkedIn URL;
- normalized name + account;
- same person with old/new title;
- same person at parent and facility;
- same person returned from multiple queries.

Duplicate record = REJECT duplicate.

---

## Gate P9 - Initial Priority

Assign:

- `P1_CANDIDATE`
- `P2_CANDIDATE`
- `P3_CANDIDATE`

according to Section 17.

---

## Gate P10 - Account Buying-Group Coverage

Do not evaluate only individuals.

Check whether the account now has adequate functional diversity.

A complete map should normally include:

- primary problem owner;
- clinical/nursing stakeholder;
- technical/integration stakeholder;
- executive sponsor or operating authority;

plus other functions required by the specific use case.

If an obvious required function is missing:

continue person research.

Do not fill missing coverage with irrelevant titles.

---

## Gate P11 - Final Person Decision

### PERSON_PASS

All mandatory person gates pass.

### REVIEW

One specific resolvable identity, role, or relevance gap remains.

### REJECT

Wrong person, wrong employer, wrong function, insufficient relevance, duplicate, or other hard failure.

---

# 12. Current Intent / Why Now

Person-level current intent is not required in SOP 2.

Do not search every person's posts trying to manufacture intent.

Account-level current signal is inherited from SOP 1.

A person's known involvement in a relevant current initiative may be stored as:

`initiative_relevance = CONFIRMED`

but is not mandatory for PERSON_PASS.

---

# 13. Person Scoring and Priority

Do not use a 100-point black-box score in SOP 2.

Use explicit functional classifications.

Person priority should be based on:

- problem ownership;
- use-case relevance;
- evaluation influence;
- commercial influence;
- technical/clinical role;
- account structure.

Final Golden scoring belongs to SOP 4.

---

# 14. Decision-Maker Research Strategy

This is the core of SOP 2.

## 14.1 Buying-group principle

Do not create:

> 12 most senior employees.

Create:

> a commercially coherent cross-functional buying group.

## 14.2 Recommended account coverage

Typical complex account:

| Function | Typical count |
|---|---:|
| Primary workflow/problem owners | 1-2 |
| Nursing/clinical leadership | 1-2 |
| Clinical engineering / HTM | 1-2 |
| IT / clinical systems | 1-2 |
| Informatics | 1-2 |
| Virtual care / operations / sponsor | 1-2 |

These are planning ranges, not quotas.

## 14.3 Diversity rule

Unless the account/use case specifically justifies it:

Do not allow more than **2 people from the same narrow function** in the core 10-12-person map.

Example:

CIO + VP IT may both qualify.

CIO + VP IT + IT Director + Infrastructure Director + Network Director + Applications Director should not all occupy the account map while telemetry, nursing, clinical engineering and informatics are missing.

---

# 15. People Discovery

## 15.1 Search order

For each account:

**Step 1:** read inherited primary use case.

**Step 2:** identify P1 function family.

**Step 3:** search P1 candidates.

**Step 4:** identify complementary P2 technical/clinical functions.

**Step 5:** identify P3 sponsor/operational route.

**Step 6:** run better-person test.

**Step 7:** check functional diversity.

**Step 8:** stop when additional people no longer add meaningful buying-group coverage.

This prevents volume-driven title collection.

---

# 16. Person Qualification Rules

## 16.1 Identity

Person must be uniquely identifiable.

## 16.2 Employer

Person must currently belong to the qualified account or correct controlling entity.

## 16.3 Role

Current function must be understood.

## 16.4 Problem ownership

At least one must be true:

- owns workflow;
- supervises workflow;
- evaluates relevant technology;
- controls technical integration;
- shapes clinical adoption;
- can sponsor cross-functional evaluation;
- is a clear internal route to the actual owner.

## 16.5 Seniority

Seniority matters only after functional relevance.

A manager directly owning telemetry may outrank a generic SVP.

## 16.6 Better-person test

Mandatory for every proposed P1.

## 16.7 Current person evidence

Prefer current first-party evidence.

If LinkedIn says current but official evidence is old, PERSON_PASS may proceed to SOP 3 with `current_role_status = PROBABLE`, provided no contradictory evidence exists.

If sources conflict:

REVIEW.

---

# 17. P1 / P2 / P3 Logic

## 17.1 P1_CANDIDATE

Purpose:

Best natural first person for the specific account problem.

Required characteristics:

- very strong functional fit;
- direct ownership or material evaluation influence;
- credible ability to engage internally;
- no visibly superior obvious function left unmapped.

### Typical P1 by use case

| Use case | Strong P1 functions |
|---|---|
| U1 | Telemetry Director/Manager, Cardiac Monitoring leader, Cardiac Services leader |
| U2 | Clinical Engineering/HTM leader, Clinical Systems/Integration leader, CIO/VP IT where architecture ownership is direct |
| U3 | Central Monitoring leader, Telemetry leader, Virtual Care leader, CNO where nursing owns program |
| U4 | Virtual Care/Tele-ICU leader, CNO, Critical Care operations leader |
| U5 | Nursing Informatics/CNIO, Telemetry leader, Clinical Systems/Integration |

## 17.2 P2_CANDIDATE

Purpose:

Complementary evaluator or co-owner.

Examples:

- Clinical Engineering alongside CNO;
- CIO alongside Telemetry;
- CNIO alongside Clinical Systems;
- CMIO alongside Virtual Care.

P2 is not a lower-quality P1.

P2 represents a different role in the buying process.

## 17.3 P3_CANDIDATE

Purpose:

Executive sponsor, secondary stakeholder, or useful internal escalation route.

Examples:

- COO;
- system CIO;
- system CNO;
- CMIO;
- hospital administrator/CEO in smaller organisations.

## 17.4 CEO rule

CEO is **not automatically P1**.

CEO/President/Administrator becomes more relevant when:

- critical-access or small rural hospital has a compressed leadership structure;
- no dedicated CIO/clinical-engineering executive exists;
- CEO visibly owns strategic technology decisions;
- major cross-functional approval genuinely sits at CEO level.

Otherwise use as P3 or exclude.

## 17.5 CIO rule

CIO is not automatically P1 merely because the product has software.

For U1, a Telemetry Director may be stronger.

For U2, CIO may be P1.

Use the problem, not title.

## 17.6 CNO rule

CNO may be P1 for:

- centralized monitoring;
- nursing workflow;
- staffing/coverage;
- nursing-led virtual care.

CNO may be P2/P3 for deeply technical integration where Clinical Engineering/IT owns the immediate evaluation.

---

# 18. Contact Enrichment

No paid contact enrichment in SOP 2.

Mandatory:

`linkedin_profile_url`

Optional if already publicly available without cost:

- official business email;
- hospital directory phone.

Do not spend paid API credits on email/phone before SOP 3 validation.

---

# 19. Dedupe and Entity Integrity

Person dedupe keys:

1. LinkedIn profile URL;
2. normalized full name + account;
3. current title + account;
4. previous/current title variation.

If one executive holds system and facility responsibilities:

store once.

Record scope:

- `SYSTEM_LEVEL`
- `FACILITY_LEVEL`
- `MULTI_FACILITY`

Do not duplicate the same person under multiple facilities unless operational responsibility genuinely differs and the data model requires it.

---

# 20. Automation Architecture

## 20.1 SOURCE COLLECTION

Input:

SOP 1 PASS account.

Output:

candidate person list.

## 20.2 PARSING

Extract:

- name;
- title;
- company;
- location;
- profile URL;
- department;
- role evidence.

## 20.3 NORMALIZATION

Normalize:

- title;
- department;
- role family;
- seniority;
- account entity.

## 20.4 AI CLASSIFICATION

AI may:

- map title to role family;
- suggest use-case relevance;
- classify P1/P2/P3 candidate;
- identify possible duplicates;
- flag ambiguous titles.

## 20.5 VERIFICATION

Verify:

- correct identity;
- current employer;
- current title;
- relevant function;
- profile match.

## 20.6 HUMAN QA

Required for:

- ambiguous executives;
- same-name profiles;
- unusual titles;
- parent/facility conflicts;
- P1 with weak direct role evidence;
- CEO/President assigned P1;
- person selected only from Tier C database evidence.

## 20.7 HANDOFF

Only PERSON_PASS records move to SOP 3.

---

# 21. AI Usage Rules

AI may:

- find likely people;
- normalize titles;
- classify functions;
- compare role-to-use-case fit;
- recommend P1/P2/P3;
- detect duplicate people;
- identify likely better functions;
- summarise person evidence.

AI must not:

- invent responsibilities;
- assume budget authority;
- assume a CIO owns every technology decision;
- assume CNO owns every clinical workflow;
- infer current employment solely from stale database data;
- fabricate LinkedIn profiles;
- infer LinkedIn activity;
- promote a person because their title sounds senior;
- fill 10-12 slots with weak people;
- change the account's primary use case without flagging a contradiction.

---

# 22. Review / Reject / Approve Rules

## PERSON_PASS

Requires:

- identity resolved;
- current employment reasonably supported;
- function understood;
- use-case relevance established;
- relevant influence classification;
- LinkedIn profile matched;
- no duplicate;
- no unresolved conflict.

## REVIEW

Must state:

- `missing_fact`
- `why_it_matters`
- `verification_source`
- `exact_next_action`

Example:

> REVIEW - LinkedIn shows current VP Clinical Systems, but hospital leadership material still lists a predecessor. Verify employment through a recent official announcement or current conference bio before PASS.

## REJECT

Use controlled P-R reason.

Never use:

`not a good fit`

without specifying the failed gate.

---

# 23. Final Handoff Standard

A person may enter SOP 3 only when:

`person_status = PERSON_PASS`

and:

- account remains SOP 1 PASS;
- LinkedIn profile matched;
- current-role evidence stored;
- role family assigned;
- primary use case inherited;
- role-to-use-case interpretation stored;
- initial priority assigned;
- duplicate check passed;
- person evidence traceable.

SOP 3 should not need to rediscover why the person was selected.

It should independently validate whether SOP 2's conclusion is trustworthy.

---

# 24. Metrics and Feedback Loop

Track:

- people discovered per PASS account;
- PERSON_PASS rate;
- REVIEW rate;
- REJECT rate;
- rejection reason;
- duplicate rate;
- former-employee rate;
- wrong-function rate;
- role-conflict rate;
- no-LinkedIn-profile rate;
- P1/P2/P3 distribution;
- role-family distribution;
- accounts missing key buying-group functions;
- average people mapped per account;
- percentage of accounts with more than two people from same narrow function;
- SOP 3 reversal rate;
- SOP 3 stale-person rate;
- SOP 3 wrong-person rate;
- eventual Golden conversion by role family.

If SOP 3 repeatedly rejects a certain title pattern, modify SOP 2 upstream.

---

# 25. Common Failure Modes

| Error | Why dangerous | Correction |
|---|---|---|
| C-suite bias | Senior does not equal problem owner | Use use-case mapping |
| IT overpopulation | Buying group becomes technically narrow | Enforce function diversity |
| CEO as default | Often too far from operating workflow | Use only where structure justifies |
| Old employee | Wastes outreach | Current-role check |
| Same-name mismatch | Wrong person | Identity gate |
| Title-only inference | Responsibilities may differ | Verify function |
| 12-person quota | Weak names enter dataset | Stop when coverage is complete |
| Parent/facility mismatch | Person may not influence relevant facility | Verify scope |
| Database-only evidence | Often stale | Verify through current sources |
| Active LinkedIn bias | Reachability mistaken for relevance | Activity not checked until SOP 3 |
| Five similar IT roles | No buying-group diversity | Max about 2 per narrow function unless justified |
| Physician without operational role | Clinical prestige but no commercial influence | Require operational ownership |

---

# 26. Worked Examples

All examples are fictional.

## A. Excellent P1

Account primary use case:

`U1_DIGITAL_RHYTHM_WORKFLOW`

Person:

Director of Telemetry Services.

Current hospital employment verified.

Owns telemetry operations.

LinkedIn profile matched.

Decision:

`PERSON_PASS`

Priority:

`P1_CANDIDATE`

---

## B. Senior but wrong P1

Account primary use case:

`U1_DIGITAL_RHYTHM_WORKFLOW`

Person:

Chief Information Officer.

Current and legitimate.

Relevant to eventual integration, but telemetry operational problem is owned elsewhere.

Decision:

`PERSON_PASS`

Priority:

`P2_CANDIDATE` or `P3_CANDIDATE`

Do not assign P1 merely because CIO is senior.

---

## C. Strong U2 P1

Primary use case:

`U2_DEVICE_EHR_INTEROPERABILITY`

Person:

Director of Clinical Engineering.

Evidence confirms responsibility for patient-monitoring devices across multiple campuses.

Decision:

`PERSON_PASS`

Priority:

`P1_CANDIDATE`

---

## D. Plausible title, unclear responsibility

Person:

Director of Clinical Services.

No evidence establishes telemetry, nursing informatics, clinical systems, or monitoring ownership.

Decision:

`REVIEW`

Required action:

Resolve actual department/function.

---

## E. Former employee

LinkedIn/data provider lists person at hospital.

Recent official source announces departure.

Decision:

`REJECT - P-R02_FORMER_EMPLOYEE`

---

## F. Excellent executive with no LinkedIn

Person is clearly current CNO and commercially relevant.

No confidently matched LinkedIn profile exists.

Because this is the LinkedIn dataset:

`REJECT - P-R10_NO_LINKEDIN_PROFILE`

This does not mean the person is commercially irrelevant. It means they do not qualify for this specific dataset.

---

## G. Small critical-access hospital

Primary use case:

`U4_REMOTE_SPECIALIST_TELE_ICU`

Relevant people found:

- CEO/Administrator
- CNO
- IT Director
- Telehealth/Virtual Care lead
- Nursing Director
- Clinical Engineering contact
- Critical Care leader

Only seven strong people exist.

Stop at seven.

Do not manufacture five additional titles.

---

# 27. AI Execution Contract

```text
You are executing SOP 2 - Decision-Maker Research & Qualification.

INPUT:
Only SOP 1 PASS accounts with handoff_ready = true.

YOUR TASK:
Build a high-quality, cross-functional buying-group map for each qualified account.

Do NOT:
- requalify the account from zero;
- search outside the inherited account;
- check LinkedIn activity;
- purchase email/phone enrichment;
- force 10-12 people;
- select people based only on title seniority.

START WITH THE ACCOUNT'S PRIMARY USE CASE.

USE CASES:
U1_DIGITAL_RHYTHM_WORKFLOW
U2_DEVICE_EHR_INTEROPERABILITY
U3_CENTRALIZED_MONITORING
U4_REMOTE_SPECIALIST_TELE_ICU
U5_AUTOMATED_DOCUMENTATION

FOR EVERY PERSON VERIFY:
1. unique identity;
2. correct account;
3. current employment;
4. current title/function;
5. role family;
6. use-case relevance;
7. problem ownership or material influence;
8. LinkedIn profile match;
9. duplicate status;
10. initial P1/P2/P3 candidate classification.

LINKEDIN:
A confidently matched LinkedIn profile is mandatory for PERSON_PASS.
Do NOT check reactions, posts, comments, or activity in SOP 2.
Set linkedin_activity_status = NOT_CHECKED.

BUYING-GROUP RULE:
Do not build a list of the most senior people.
Build a complementary group containing problem owners, clinical/nursing stakeholders, technical/integration stakeholders, and executive/operational influence.

10-12 people is an approximate upper working range, not a quota.
Stop earlier when no additional person adds meaningful buying-group coverage.

P1 means:
best natural first person for this specific problem.

P2 means:
complementary evaluator/co-owner.

P3 means:
executive sponsor, secondary stakeholder, or internal route.

Run the BETTER-PERSON TEST for every P1:
Is another visible role/function materially more natural as the primary owner?
If yes, current person cannot automatically remain P1.

DECISIONS:
PERSON_PASS
REVIEW
REJECT

REVIEW requires:
missing_fact
why_it_matters
best_verification_source
exact_next_action

Never invent responsibilities.
Never convert title prestige into problem ownership.
Never lower quality to increase person count.

OUTPUT:
Return deterministic structured JSON plus an account-level buying-group coverage summary.
```

# Canonical Person JSON

```json
{
  "person_id": "",
  "account_id": "",
  "full_name": "",
  "linkedin_profile_url": "",
  "linkedin_identity_status": "MATCHED",
  "linkedin_activity_status": "NOT_CHECKED",
  "current_company_display_name": "",
  "current_title": "",
  "department": "",
  "role_family": "",
  "seniority_level": "",
  "role_scope": "SYSTEM_LEVEL",
  "primary_use_case": "",
  "person_use_case_relevance": "",
  "problem_ownership_level": "",
  "evaluation_influence": "",
  "commercial_influence": "",
  "technical_influence": "",
  "internal_routing_value": "",
  "current_role_status": "",
  "profile_identity_confidence": "",
  "initial_priority": "",
  "better_person_test": {
    "clear_better_function_exists": false,
    "better_function": null,
    "reason": ""
  },
  "evidence": [],
  "duplicate_status": "UNIQUE",
  "person_status": "",
  "review_reason": null,
  "reject_reason_code": null,
  "missing_fact": null,
  "next_verification_action": null,
  "last_checked_at": ""
}
```

# Account Buying-Group Coverage JSON

```json
{
  "account_id": "",
  "primary_use_case": "",
  "person_pass_count": 0,
  "p1_candidates": [],
  "p2_candidates": [],
  "p3_candidates": [],
  "role_families_covered": [],
  "missing_critical_function": null,
  "functional_diversity_status": "COMPLETE",
  "additional_person_research_needed": false
}
```

# FINAL SELF-QA CHECKLIST

Before an account leaves SOP 2:

- [ ] Input account is SOP 1 PASS.
- [ ] Primary use case was inherited, not invented.
- [ ] People were selected from problem ownership, not title prestige.
- [ ] Each PERSON_PASS has a matched LinkedIn profile.
- [ ] LinkedIn activity was not checked here.
- [ ] Current employment was reasonably verified.
- [ ] Current role/function was understood.
- [ ] No clear former employees remain.
- [ ] No same-name identity ambiguity remains in PASS.
- [ ] No duplicates remain.
- [ ] Every person has one role family.
- [ ] Every person has a defensible U1-U5 relationship.
- [ ] Every P1 passed the better-person test.
- [ ] C-suite executives were not automatically made P1.
- [ ] Buying group contains complementary functions.
- [ ] One narrow function has not crowded out the rest of the account.
- [ ] 10-12 was not treated as a quota.
- [ ] Paid email/phone enrichment was not performed.
- [ ] Evidence URLs and dates are retained.
- [ ] REVIEW records identify exact missing evidence and next action.
- [ ] REJECT reasons use controlled values.
- [ ] The account can now move to SOP 3 without repeating person discovery.
