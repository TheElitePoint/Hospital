---
document_id: SOP-01-ACCOUNT-RESEARCH-QUALIFICATION
document_type: RESEARCH_SOP
title: "SOP 1 - Account Research & Qualification"
version: "1.0"
status: "Production Draft"
last_updated: "2026-09-12"
scope: "United States inpatient hospitals and health systems within approved first-cycle states"
decision_vocabulary:
  - PASS
  - REVIEW
  - REJECT
primary_handoff: "SOP 2 - Decision-Maker Research & Qualification"
source_of_truth: "Stored evidence and controlled fields, not researcher opinion"
volume_policy: "No fixed PASS quota. Qualification thresholds must never move to satisfy a count."
---

# ASSIGNMENT INTERPRETATION

## Target market

United States inpatient hospitals and health systems in the approved first-cycle states:

1. Indiana
2. Ohio
3. Kentucky
4. Texas
5. Alabama

No other state is in scope for this SOP version. Researchers and AI agents must not expand geography independently.

## Product / service being sold

A hospital monitoring, interoperability, and clinical workflow platform designed for inpatient environments. Supplied product material describes capabilities including:

- real-time access to patient vitals and waveforms;
- live and historical physiological data;
- alarm and event capture;
- digital rhythm-strip workflows;
- patient monitoring across multiple devices;
- vendor-agnostic device integration;
- EMR/EHR-connected workflows;
- automated admit, discharge, and transfer-related workflow support;
- centralized and remote monitoring visibility;
- configurable patient-monitoring views;
- cloud or hospital-hosted deployment;
- deployment that, in many cases, does not require additional hardware;
- support for a large device-integration library;
- development of new device integrations where needed.

Company-supplied product claims and partner-supplied deployment examples are research context. They are not independent proof of fit for a prospect account.

## Core buying problem

The research system is looking for inpatient organisations where one or more of the following conditions is commercially relevant:

1. Telemetry or rhythm-strip workflows remain operationally burdensome.
2. Existing bedside monitoring devices are fragmented across vendors or sites.
3. Device data does not move cleanly into the EHR or clinical workflow.
4. A hospital or system wants centralized or cross-site patient monitoring.
5. Rural or distributed facilities need remote specialist or tele-ICU coverage.
6. Monitoring, alarm, vitals, or rhythm-strip documentation still requires avoidable manual work.
7. A multi-site system has a standardisation problem across monitoring environments.

## Approved account archetypes

Active discovery is limited to:

- `COMMUNITY_ACUTE`
- `REGIONAL_MULTI_SITE`
- `CRITICAL_ACCESS`
- `RURAL_ACUTE`
- `LTACH_POST_ACUTE`

`ACADEMIC_TERTIARY` is exception-only. Do not proactively search academic/tertiary hospitals. An academic/tertiary organisation may enter only when a specific current monitoring, interoperability, tele-ICU, or centralized-monitoring use case is already visible during discovery.

## Likely downstream buyer functions

Account research does not select people. It only confirms that a relevant buying group is likely to exist.

Relevant downstream functions may include:

- Telemetry / Cardiac Monitoring
- Nursing leadership
- Clinical Engineering / HTM / Biomedical Engineering
- CIO / IT / Clinical Systems
- Nursing Informatics
- Clinical Informatics
- Virtual Care / Telehealth / Command Center
- Clinical Operations
- Clinical Documentation / Revenue Integrity where directly relevant

Detailed person selection belongs to SOP 2.

## Hard exclusions

- outpatient-only organisations;
- home-RPM-only organisations without relevant inpatient operations;
- veterinary organisations;
- accounts outside the five approved states;
- closed or inactive facilities;
- duplicate entities;
- protected existing or partner-owned accounts not available for new attribution;
- organisations with no credible inpatient monitoring relevance;
- wrong parent/facility entity;
- accounts where current, credible evidence shows the same core problem is already comprehensively solved by a recently implemented enterprise platform;
- accounts where no defensible primary use case can be established.

## Major signals

A qualified account must satisfy the signal rules in Section 03. In summary:

- at least one `CORE_SIGNAL`; and
- at least one `SUPPORTING_SIGNAL`; and
- one evidence-backed primary use case from U1-U5.

## Unresolved assumptions

None may be silently invented. Any material unresolved fact must be routed to `REVIEW` with an exact verification action.

# 00. Document Control

## 00.1 Purpose of this document

This SOP governs account-level discovery, research, evidence capture, qualification, prioritisation, QA, and handoff.

Its job is to answer one question:

> **Is this organisation sufficiently relevant, evidenced, current, and commercially plausible to justify decision-maker research?**

It does not find decision-makers, enrich contacts, check LinkedIn activity, or select the final Golden dataset.

## 00.2 Intended users

- AI research agents
- research analysts
- research operations staff
- data engineers
- automation developers
- human QA reviewers
- research managers

## 00.3 Related documents

- SOP 2 - Decision-Maker Research & Qualification
- SOP 3 - Independent Data Validation & QA
- SOP 4 - Golden 1,000 Selection & Final Validation

## 00.4 Source-of-truth rule

The source of truth is the evidence stored against each claim.

Researcher opinion, AI confidence language, database scores, company fame, or title prestige must never override evidence.

## 00.5 Volume rule

There is no fixed number of accounts that must PASS.

Never ask:

> "How many accounts do we still need?"

while deciding an account.

Ask:

> "Does this account independently meet the qualification standard?"

If downstream volume is later insufficient, discovery scope is expanded through a controlled SOP revision or manager-approved scope change. Qualification standards are never lowered.

# 01. Purpose and Success Definition

## 01.1 Research objective

Find the strongest inpatient hospital and health-system accounts in the approved first-cycle states where the operating environment creates a defensible commercial pathway for the platform.

The objective is not broad market coverage.

The objective is high-confidence account qualification.

## 01.2 Successful account record

A successful `PASS` account must have:

- verified organisation identity;
- approved geography;
- approved account archetype;
- credible inpatient monitoring relevance;
- at least one Core Signal;
- at least one Supporting Signal;
- one primary use case from U1-U5;
- no unresolved hard exclusion;
- protected-relationship status cleared;
- material evidence stored with source date or access date;
- no unresolved contradiction that changes the qualification decision;
- a concise, evidence-backed "why this account" statement;
- final self-QA complete.

## 01.3 What does not qualify

The following are insufficient by themselves:

- hospital is large;
- hospital is famous;
- hospital has an ICU;
- hospital says it is innovative;
- hospital has an AI strategy;
- hospital uses Epic;
- hospital has a telehealth program;
- hospital hired a CIO;
- hospital has a digital-transformation page;
- hospital is in healthcare;
- a data provider labels it as a target account.

## 01.4 Final commercial objective

Pass only accounts where SOP 2 can immediately research a relevant buying group around a specific operating problem rather than starting from a generic executive list.

## 01.5 Core qualification question

> **Does current, traceable evidence show that this organisation operates an inpatient monitoring environment where at least one defined platform use case is commercially relevant enough to justify decision-maker research?**

# 02. Business / Product Understanding

## 02.1 Operational description

The platform is best understood as a hospital monitoring, device-connectivity, and clinical-workflow layer.

The research team should not reduce it to generic remote patient monitoring.

The commercially relevant capabilities are:

- live multi-patient vitals and waveform visibility;
- historical physiological data;
- alarm and event capture;
- digital rhythm-strip workflows;
- vendor-agnostic device integration;
- device-to-EHR / EMR data flow;
- centralized monitoring;
- remote clinical visibility;
- configurable patient views;
- workflow automation around admits, discharges, transfers, telemetry, and monitoring documentation;
- cloud or internal hospital deployment;
- ability in many environments to work without wholesale hardware replacement.

## 02.2 Strongest account-level commercial ideas

### A. Preserve existing monitoring investment

The strongest account is often not one looking to replace all monitoring hardware.

The stronger opening can be an organisation with valuable existing equipment that needs a better interoperability or workflow layer.

### B. Digital telemetry and rhythm-strip workflow

Paper strips, manual measurement, manual labelling, scanning, filing, or manual EHR workflow are strong operational signals.

### C. Multi-vendor interoperability

Different device manufacturers across sites, units, or acquired facilities can create a standardisation and interface-management problem.

### D. Centralised and cross-site monitoring

Regional and multi-campus systems can have a stronger commercial case when monitoring visibility or documentation must work across locations.

### E. Remote specialist coverage

Rural and distributed facilities can have a strong case when specialist capacity is limited and remote critical-care monitoring is relevant.

### F. Automated monitoring documentation

Manual transcription or fragmented documentation of alarms, observations, vitals, or strips can create a measurable workflow problem.

## 02.3 What the product does not imply

Do not infer that every:

- home RPM program is relevant;
- telehealth program is relevant;
- ICU requires this platform;
- multi-site system has fragmented monitoring;
- Epic hospital has an integration problem;
- major monitoring-vendor user needs an independent layer;
- rural hospital has budget;
- large hospital has stronger fit than a small hospital.

Research must prove the relevant operating condition.

## 02.4 Claims discipline

Supplied product material may be used to understand product architecture, possible use cases, possible buyer problems, and research keywords.

Do not use supplied product outcome claims as evidence that a prospect account has the same problem or would achieve the same result.

# 03. Ideal Customer Profile

## 03.1 Geography - exact current scope

Only these states are in scope:

| Research order | State | Status |
|---:|---|---|
| 1 | Indiana | `IN_SCOPE_CORE` |
| 2 | Ohio | `IN_SCOPE_CORE` |
| 3 | Kentucky | `IN_SCOPE_CORE` |
| 4 | Texas | `IN_SCOPE_CORE` |
| 5 | Alabama | `IN_SCOPE_CORE` |

Any other state is `OUT_OF_SCOPE` and receives `REJECT - R01_OUT_OF_SCOPE_GEO` under this SOP version.

No researcher or AI agent may independently add Canada, the UK, another U.S. state, or another country.

## 03.2 Active-discovery account archetypes

### 03.2.1 `COMMUNITY_ACUTE`

Definition: Independent or system-affiliated acute-care hospital serving a community or regional catchment.

Active discovery band: approximately 50-350 beds.

Important: the bed range guides discovery. It is not a hard qualification gate.

Best evidence patterns:
- telemetry/cardiac monitoring;
- active inpatient monitoring;
- clinical engineering;
- manual monitoring documentation;
- device-to-EHR integration;
- multi-vendor environment;
- central monitoring;
- recent technology change.

### 03.2.2 `REGIONAL_MULTI_SITE`

Definition: Regional health system with multiple acute-care facilities or campuses.

Active discovery band: typically 2-8 acute sites.

Best evidence patterns:
- different sites acquired/built at different times;
- cross-site standardisation;
- centralised monitoring;
- multiple EHR/device environments;
- common clinical-engineering structure;
- virtual care or remote monitoring;
- current expansion or acquisition.

Systems with more than 8 acute sites are not automatically rejected, but must have a clearly identifiable regional, divisional, or facility-level entry point. Otherwise route to `REVIEW`.

### 03.2.3 `CRITICAL_ACCESS`

Definition: Critical-access hospital or equivalent very small acute inpatient facility.

No minimum bed count.

Mandatory additional condition: must show a direct monitoring-related operating signal, not merely rural status.

### 03.2.4 `RURAL_ACUTE`

Definition: Rural acute-care hospital that is not necessarily formally designated critical access.

No minimum bed count.

Mandatory additional condition: must show a direct monitoring-related operating signal.

### 03.2.5 `LTACH_POST_ACUTE`

Definition: Long-term acute-care or post-acute inpatient organisation with clinically relevant continuous monitoring.

Mandatory additional condition: continuous monitoring, telemetry, rhythm-strip, ventilator/device integration, or comparable inpatient monitoring must be evidenced.

Do not qualify a generic post-acute facility without this evidence.

## 03.3 Exception-only archetype

### `ACADEMIC_TERTIARY`

Do not proactively discover this category.

It may enter the pipeline only when a specific current use case is already visible during research, such as:

- active tele-ICU;
- current central monitoring program;
- device-integration project;
- specific telemetry workflow initiative;
- multi-site monitoring standardisation;
- remote specialist coverage.

Large academic status alone is never enough.

## 03.4 Mandatory account conditions

All must pass:

1. In approved state.
2. Correct entity identified.
3. Approved account archetype or valid academic exception.
4. Inpatient operation verified.
5. At least one Core Signal verified.
6. At least one Supporting Signal verified.
7. One primary use case assigned.
8. No unresolved hard exclusion.
9. Relationship-overlap status cleared.
10. Minimum evidence standard met.

## 03.5 Core Signals

At least one Core Signal is mandatory.

Controlled values:

- `CS_TELEMETRY_CARDIAC_MONITORING`
- `CS_CENTRAL_MONITORING`
- `CS_TELE_ICU_VIRTUAL_CRITICAL_CARE`
- `CS_DEVICE_EHR_INTEGRATION`
- `CS_CLINICAL_ENGINEERING_MONITORING`
- `CS_MULTI_VENDOR_INPATIENT_MONITORING`
- `CS_MANUAL_MONITORING_DOCUMENTATION`

### Exact interpretation

`CS_TELEMETRY_CARDIAC_MONITORING`: evidence shows an active inpatient telemetry, cardiac monitoring, monitor-tech, ECG monitoring, or equivalent service/workflow.

`CS_CENTRAL_MONITORING`: evidence shows central surveillance, remote viewer, centralized monitoring unit, monitoring command center, or cross-site monitoring.

`CS_TELE_ICU_VIRTUAL_CRITICAL_CARE`: evidence shows tele-ICU, virtual critical care, remote intensivist, or equivalent inpatient remote specialist coverage.

`CS_DEVICE_EHR_INTEGRATION`: evidence shows medical-device-to-EHR integration, physiologic data integration, device connectivity, or a related current integration environment.

`CS_CLINICAL_ENGINEERING_MONITORING`: evidence shows clinical engineering / HTM / biomedical engineering responsibility for inpatient monitoring or related bedside devices.

`CS_MULTI_VENDOR_INPATIENT_MONITORING`: evidence supports multiple relevant monitoring/device manufacturers or heterogeneous device environments.

`CS_MANUAL_MONITORING_DOCUMENTATION`: evidence directly indicates manual telemetry, rhythm-strip, vitals, alarm, or monitoring documentation.

## 03.6 Supporting Signals

At least one Supporting Signal is mandatory.

Controlled values:

- `SS_MULTI_SITE`
- `SS_MULTI_VENDOR_COMPLEXITY`
- `SS_RELEVANT_HIRING`
- `SS_RECENT_EXPANSION`
- `SS_RECENT_ACQUISITION`
- `SS_EHR_OR_INTEGRATION_CHANGE`
- `SS_STAFFING_PRESSURE`
- `SS_REMOTE_SPECIALIST_NEED`
- `SS_ACTIVE_MONITORING_PROJECT`
- `SS_VIRTUAL_CARE_PROGRAM`
- `SS_DOCUMENTATION_AUTOMATION`
- `SS_STANDARDISATION_NEED`

A Supporting Signal cannot be the same evidence record used to create the Core Signal unless the evidence independently proves both facts.

## 03.7 Preferred conditions

Preferred but not mandatory:

- 2-8 facility regional structure;
- current telemetry department;
- known clinical-engineering team;
- recent acquisition;
- central monitoring or remote viewer;
- technology modernisation;
- multiple device vendors;
- active relevant hiring;
- current virtual-care or tele-ICU initiative;
- evidence of manual documentation burden.

## 03.8 Optional conditions

Optional only:

- technology awards;
- broad innovation strategy;
- AI initiative unrelated to monitoring;
- generic digital-transformation program;
- general nurse recruitment;
- general capital project;
- general hospital growth.

Optional conditions cannot create PASS on their own.

## 03.9 Primary Use Case

Every PASS account must receive exactly one primary use case.

Allowed values:

### `U1_DIGITAL_RHYTHM_WORKFLOW`
Use when the strongest evidence points to telemetry, rhythm strips, ECG review, monitor technicians, or manual strip processing/review.

### `U2_DEVICE_EHR_INTEROPERABILITY`
Use when the strongest evidence points to multi-vendor device estate, device-to-EHR integration, clinical-engineering interface burden, physiologic data integration, or cross-site device standardisation.

### `U3_CENTRALIZED_MONITORING`
Use when the strongest evidence points to central monitoring, remote viewer, cross-site surveillance, command center, central monitoring unit, or multi-campus monitoring.

### `U4_REMOTE_SPECIALIST_TELE_ICU`
Use when the strongest evidence points to tele-ICU, virtual critical care, remote intensivist, rural specialist shortage, or distributed critical-care coverage.

### `U5_AUTOMATED_DOCUMENTATION`
Use when the strongest evidence points to manual vitals/monitoring documentation, alarm/event documentation, telemetry documentation, clinical-documentation burden, device-data charting, or workflow automation around monitoring records.

Only one may be `primary_use_case`.

Additional applicable use cases may be stored in `secondary_use_cases`.

# 04. Hard Exclusions

Hard exclusions are checked before account prioritisation.

| Code | Condition | Decision |
|---|---|---|
| `R01_OUT_OF_SCOPE_GEO` | Outside Indiana, Ohio, Kentucky, Texas, Alabama | REJECT |
| `R02_WRONG_ACCOUNT_TYPE` | Outpatient-only, home-RPM-only, non-inpatient, veterinary, or otherwise outside approved archetypes | REJECT |
| `R03_NO_INPATIENT_MONITORING` | Adequate research finds no credible inpatient monitoring relevance | REJECT |
| `R04_CORE_PROBLEM_ALREADY_SOLVED` | Current, credible evidence shows a recent comprehensive enterprise solution already solves the same primary use case | REJECT unless a separate unsolved use case is directly evidenced |
| `R05_PROTECTED_RELATIONSHIP` | Existing direct, strategic-partner, or device-partner account unavailable for new attribution | REJECT from new-account dataset |
| `R06_DUPLICATE_ENTITY` | Same canonical facility/system already exists | REJECT duplicate |
| `R07_CLOSED_INACTIVE` | Closed, inactive, or no longer operating as the researched entity | REJECT |
| `R08_EVIDENCE_INSUFFICIENT` | Only weak discovery evidence remains after defined verification attempts | REJECT |
| `R09_WRONG_ENTITY` | Record is a wrong facility, parent, subsidiary, or entity match | REJECT or correct entity and restart |
| `R10_NO_CREDIBLE_USE_CASE` | Core/supporting evidence does not produce a defensible U1-U5 route | REJECT |
| `R11_LINKEDIN_SECTOR_MISMATCH` | Correct LinkedIn company page is confirmed but its industry is outside the approved healthcare/medical sector list | REJECT |

## 04.1 Incumbent solution rule

Do not reject because a hospital uses a major monitoring vendor.

Reject only when current evidence establishes that a recently implemented solution already addresses the same core problem across the relevant scope.

## 04.2 Protected relationship rule

Controlled field: `relationship_overlap_status`

Allowed values:

- `NONE_FOUND`
- `EXISTING_DIRECT_RELATIONSHIP`
- `STRATEGIC_PARTNER_RELATIONSHIP`
- `DEVICE_PARTNER_RELATIONSHIP`
- `POSSIBLE_OVERLAP_REVIEW`
- `UNKNOWN_REVIEW`

Only `NONE_FOUND` may proceed to final PASS.

`POSSIBLE_OVERLAP_REVIEW` and `UNKNOWN_REVIEW` remain REVIEW until resolved.

# 05. Qualification Definitions

## `QUALIFIED_ACCOUNT`

An account that passes all mandatory gates and has one verified Core Signal, one verified Supporting Signal, one evidence-backed primary use case, no unresolved exclusion, and sufficient current evidence.

## `CURRENT_SIGNAL`

Allowed values:

- `STRONG`
- `PRESENT`
- `NONE_FOUND`

`STRONG` examples:
- active monitoring pilot;
- active central-monitoring initiative;
- active device-integration project;
- new facility with relevant monitoring build-out;
- current tele-ICU deployment;
- current EHR/device integration change directly tied to U1-U5.

`PRESENT` examples:
- relevant hiring;
- recent acquisition;
- virtual-care initiative;
- recent technology modernisation;
- recent expansion;
- new clinical-engineering leadership.

`NONE_FOUND` means research completed but no current public timing signal was found. It does not cause automatic rejection.

## `FACT`
A claim directly supported by stored evidence.

## `INFERENCE`
A reasoned interpretation based on facts. Must be labelled as inference.

## `HYPOTHESIS`
A proposition to be tested downstream. Must never be written as fact.

## `DISCOVERY_SOURCE`
A source used to find a potential account, signal, keyword, or lead.

## `VERIFICATION_SOURCE`
A source strong enough to support a qualification claim.

## `CURRENT`
Within the field-specific freshness window.

## `STALE`
Outside the preferred freshness window and not independently refreshed.

## `REVIEW`
A record with a specific, resolvable gap that materially blocks PASS or REJECT.

# 06. Data Architecture and Entity Model

## 06.1 Entities

- `account`
- `parent_system`
- `facility`
- `signal`
- `evidence`
- `use_case`
- `qualification_decision`
- `relationship_overlap`
- `conflict`

## 06.2 Relationships

- One parent system may contain multiple facilities.
- One account may have multiple signals.
- One signal may have multiple evidence records.
- One account must have exactly one primary use case at PASS.
- One account may have multiple secondary use cases.
- One account may have multiple conflicts, but no material unresolved conflict may remain at PASS.
- Parent and facility must not be treated as the same entity unless the research assignment deliberately uses the parent system as the commercial account.

## 06.3 Canonical account rule

Every account receives a stable `account_id`.

Recommended format:

`US-{STATE}-{NORMALIZED_DOMAIN_OR_ENTITY_KEY}`

Do not use a changing display name as the only identifier.

# 07. Required Output Schema

## 07.1 Company / account fields

| field_name | type | required | rule |
|---|---|---:|---|
| `account_id` | string | yes | canonical unique ID |
| `canonical_account_name` | string | yes | verified operating name |
| `facility_name` | string/null | yes | facility or `NOT_APPLICABLE` |
| `parent_system_name` | string/null | yes | system or `NOT_APPLICABLE` |
| `canonical_domain` | string | yes | official domain |
| `linkedin_company_url` | string | yes for final PASS | official matched LinkedIn company page |
| `linkedin_company_name` | string | yes for final PASS | company name shown on matched LinkedIn page |
| `linkedin_industry` | string | yes for final PASS | exact LinkedIn industry value |
| `linkedin_sector_status` | enum | yes for final PASS | `SECTOR_PASS`, `SECTOR_MISMATCH`, or `ENTITY_MISMATCH` |
| `state` | enum | yes | IN, OH, KY, TX, AL |
| `city` | string | yes | current city |
| `account_archetype` | enum | yes | approved values only |
| `bed_count` | integer/string | yes | value or `UNKNOWN` |
| `facility_count` | integer/string | yes | value or `UNKNOWN` |
| `acute_site_count` | integer/string | yes | value, `UNKNOWN`, or `NOT_APPLICABLE` |

## 07.2 Qualification fields

- `core_signals[]`
- `supporting_signals[]`
- `primary_use_case`
- `secondary_use_cases[]`
- `current_signal`
- `qualification_status`
- `priority_class`
- `relationship_overlap_status`
- `hard_exclusion_code`
- `review_reason_code`
- `reject_reason_code`

## 07.3 Technology / operating fields

These are conditionally required. Do not spend time proving every field when it does not affect qualification.

- `telemetry_evidence_status`
- `cardiac_monitoring_status`
- `clinical_engineering_status`
- `ehr_platform`
- `monitoring_vendors_found[]`
- `central_monitoring_status`
- `tele_icu_status`
- `virtual_care_status`
- `manual_documentation_status`
- `interoperability_status`

Status values:

- `CONFIRMED`
- `NOT_FOUND`
- `UNKNOWN`
- `NOT_APPLICABLE`
- `NOT_CHECKED`

## 07.4 Evidence object

```json
{
  "evidence_id": "EV-001",
  "claim_key": "core_signal.telemetry",
  "claim_type": "FACT",
  "claim_value": "Inpatient telemetry service confirmed",
  "source_url": "https://...",
  "source_title": "Official source title",
  "source_owner": "Hospital / vendor / government / publication",
  "source_tier": "A1",
  "source_date": "2026-05-01",
  "accessed_at": "2026-09-12T12:00:00Z",
  "evidence_excerpt": "Short exact supporting excerpt",
  "freshness_status": "CURRENT",
  "directness": "DIRECT",
  "conflict_status": "NONE"
}
```

## 07.5 Fact -> Evidence -> Interpretation -> Decision object

```json
{
  "fact": "Three acute campuses with centralized telemetry are confirmed.",
  "evidence_ids": ["EV-101", "EV-102"],
  "interpretation": "Cross-site monitoring standardisation is commercially relevant.",
  "decision_impact": "Supports U3_CENTRALIZED_MONITORING and account PASS.",
  "confidence": "HIGH"
}
```

## 07.6 Workflow / QA fields

- `researcher_id`
- `research_started_at`
- `research_completed_at`
- `last_verified_at`
- `qa_status`
- `qa_reviewer_id`
- `conflict_status`
- `missing_fact`
- `next_verification_action`
- `negative_evidence_summary`
- `why_this_account`
- `handoff_ready`

## 07.7 Null handling

Never leave an important field blank.

Use:

- `UNKNOWN` = fact could not be established.
- `NONE_FOUND` = active search completed and no evidence found.
- `NOT_APPLICABLE` = field does not apply.
- `NOT_CHECKED` = field intentionally not researched because it was not material at this stage.

# 08. Evidence Standard

## 08.1 Claim-specific hierarchy

No source is globally best for every claim.

A source must be evaluated against the exact claim it supports.

## 08.2 Tier A1 - Direct durable evidence

Examples:
- official hospital/system website;
- official annual report;
- official facility/service page;
- official procurement/RFP;
- official government/state source;
- official hospital press release;
- official technology/project documentation.

## 08.3 Tier A2 - Direct but time-sensitive evidence

Examples:
- official hospital job posting;
- official hospital LinkedIn post;
- official executive announcement;
- official vendor customer announcement;
- official event presentation by the hospital.

A2 evidence requires date capture.

## 08.4 Tier B - Credible secondary evidence

Examples:
- respected healthcare press;
- credible business press;
- recognised industry publication;
- credible local news;
- professional association;
- conference biography;
- credible vendor case study where hospital participation is clear.

## 08.5 Tier C - Discovery evidence only

Examples:
- Sales Navigator;
- Apollo;
- ZoomInfo;
- database exports;
- generic directories;
- search snippets;
- scraped datasets;
- non-official profile aggregators.

Tier C can discover a lead, but Tier C alone cannot establish a material PASS claim when stronger verification is reasonably available.

## 08.6 Unacceptable evidence

- AI-generated statement without underlying source;
- unsourced listicle;
- another spreadsheet row with no source;
- researcher memory;
- assumed device vendor;
- assumed EHR;
- inferred need written as fact;
- outdated profile mirror used as proof of current operations.

## 08.7 Triangulation required when

- first source is Tier B;
- material claim is older than its freshness window;
- claim materially affects exclusion or use-case selection;
- vendor marketing case study is older than 12 months;
- current technology is uncertain;
- entity identity is ambiguous;
- two sources disagree.

## 08.8 Evidence excerpt rule

Store the shortest excerpt that proves the claim.

## 08.9 URL rule

Store the direct page URL, not only a search-result URL.

# 09. Research / Discovery Channels

## 09.1 Hospital / health-system website

Use for entity verification, services, sites, programs, facility structure, and official technology initiatives.

## 09.2 Search engine

Use for external evidence, recent changes, and negative evidence.

Every likely PASS account must receive at least one targeted search outside the hospital domain.

## 09.3 Current job postings

Use to detect telemetry, monitor-tech, clinical engineering, HTM, biomedical engineering, informatics, virtual care, command center, and relevant integration roles.

A job posting proves hiring demand, not purchasing intent.

## 09.4 Technology / vendor sources

Use to discover installed technology, prior integrations, or incumbent solutions.

Any vendor source older than 12 months that materially affects current qualification must be refreshed or triangulated.

## 09.5 News / press releases

Use for expansion, acquisition, technology deployment, hospital opening, virtual-care program, or integration change.

## 09.6 Government / state / rural-health sources

Use to confirm rural transformation, telehealth, interoperability, hospital structure, critical-access designation, or public initiatives.

## 09.7 LinkedIn

Use LinkedIn in SOP 1 for:

- official hospital/company post discovery;
- program/project keyword discovery;
- leadership context;
- final company-page and industry-sector validation under Gate A11.

Do not perform person qualification or LinkedIn activity validation here.

The company-page sector check is performed only after the account has passed the preceding qualification gates.

# 10. Search Query Library

Use exact hospital/system name in place of `{ACCOUNT}`.

## 10.1 Core monitoring

- `"{ACCOUNT}" telemetry`
- `"{ACCOUNT}" "cardiac monitoring"`
- `"{ACCOUNT}" "monitor technician"`
- `"{ACCOUNT}" "ECG monitoring"`

## 10.2 Centralized monitoring

- `"{ACCOUNT}" "central monitoring"`
- `"{ACCOUNT}" "centralized monitoring"`
- `"{ACCOUNT}" "command center" monitoring`
- `"{ACCOUNT}" "remote viewer"`
- `"{ACCOUNT}" "virtual nursing"`

## 10.3 Tele-ICU / remote specialist coverage

- `"{ACCOUNT}" tele-ICU`
- `"{ACCOUNT}" "virtual critical care"`
- `"{ACCOUNT}" remote intensivist`
- `"{ACCOUNT}" "virtual ICU"`

## 10.4 Device / EHR integration

- `"{ACCOUNT}" "medical device integration"`
- `"{ACCOUNT}" "device integration" EHR`
- `"{ACCOUNT}" physiologic data integration`
- `"{ACCOUNT}" interoperability monitors`

## 10.5 Clinical engineering

- `"{ACCOUNT}" "clinical engineering"`
- `"{ACCOUNT}" HTM`
- `"{ACCOUNT}" "biomedical engineering"`

## 10.6 EHR - only when material

- `"{ACCOUNT}" Epic`
- `"{ACCOUNT}" Meditech`
- `"{ACCOUNT}" "Oracle Health"`
- `"{ACCOUNT}" Cerner`

## 10.7 Change signals

- `"{ACCOUNT}" acquisition`
- `"{ACCOUNT}" expansion`
- `"{ACCOUNT}" "new hospital"`
- `"{ACCOUNT}" modernization`

## 10.8 Negative evidence / incumbents

Run at least one negative-evidence search for every likely PASS account.

- `"{ACCOUNT}" "enterprise monitoring platform"`
- `"{ACCOUNT}" "medical device integration platform"`
- `"{ACCOUNT}" Philips Capsule`
- `"{ACCOUNT}" Sickbay`
- `"{ACCOUNT}" Masimo monitoring`
- `"{ACCOUNT}" CARESCAPE`
- `"{ACCOUNT}" centralized monitoring implementation`

# 11. Company Qualification Pipeline

Run sequentially. Do not score before mandatory gates.

## Gate A0 - Entity Integrity

**Question:** Is this the correct operating entity, and is the facility-parent relationship understood?

**PASS:** official identity/domain verified and parent/facility structure clear enough.

**REVIEW:** affiliation, ownership, or operating entity unclear.

**REJECT:** duplicate, wrong facility, closed/inactive entity, wrong parent.

**Stop rule:** do not continue until entity is resolved.

## Gate A1 - Geography

**Question:** Is the account in Indiana, Ohio, Kentucky, Texas, or Alabama?

**PASS:** yes.

**REJECT:** no.

## Gate A2 - Account Archetype

**PASS:** approved active-discovery archetype.

**REVIEW:** academic/tertiary account with visible specific use case requiring validation.

**REJECT:** outpatient, home-only, veterinary, generic post-acute without relevant continuous monitoring, or unsupported type.

## Gate A3 - Inpatient Operation

**PASS:** current evidence confirms relevant inpatient operation.

**REVIEW:** mixed inpatient/outpatient scope unclear.

**REJECT:** no relevant inpatient operation.

## Gate A4 - Core Signal

**PASS:** at least one Core Signal verified.

**REVIEW:** plausible Core Signal exists but evidence is weak/stale and a clear verification route exists.

**REJECT:** no Core Signal after reasonable targeted research.

## Gate A5 - Supporting Signal

**PASS:** at least one Supporting Signal verified.

**REVIEW:** strong Core Signal exists but additional condition remains unresolved.

**REJECT:** no Supporting Signal after targeted research and insufficient additional fit.

## Gate A6 - Hard Exclusions

**PASS:** none.

**REVIEW:** possible overlap, incumbent, or entity issue unresolved.

**REJECT:** confirmed exclusion.

**Stop rule:** stop expensive research after confirmed REJECT.

## Gate A7 - Primary Use Case

**PASS:** exactly one U1-U5 pathway best supported by evidence.

**REVIEW:** multiple possible use cases but none sufficiently supported as primary.

**REJECT:** no credible U1-U5 pathway.

## Gate A8 - Evidence Sufficiency

**PASS:** entity, Core Signal, Supporting Signal, and use case are traceably evidenced; material dates captured; no unresolved decision-changing conflict.

**REVIEW:** one specific evidence gap remains.

**REJECT:** qualification depends on assumptions, Tier C-only evidence, or unsupported inference.

## Gate A9 - Current Signal

Classify only:

- `STRONG`
- `PRESENT`
- `NONE_FOUND`

This gate does not automatically reject an otherwise strong account.

## Gate A10 - Direct Commercial Suitability

**Question:** Can this organisation plausibly evaluate and adopt this type of inpatient monitoring/interoperability platform?

**PASS:** direct hospital/system evaluation route plausible.

**REVIEW:** buying authority or system-vs-facility control unclear.

**REJECT:** no plausible direct adoption path for the researched entity.

## Gate A11 - LinkedIn Company Sector Validation

This is the final validation gate before the account decision and SOP 2 handoff.

**Purpose:** prevent a same-name or incorrectly matched company from entering the qualified dataset.

For every account that has passed Gates A0-A10:

1. Retrieve the official LinkedIn company page.
2. Capture:
   - `linkedin_company_url`
   - `linkedin_company_name`
   - `linkedin_industry`
3. Match the LinkedIn page to the researched account using the company name, official domain/website, location, and company description/context.
4. Validate the exact LinkedIn industry against the approved healthcare/medical sector list below.

### Approved LinkedIn industries

A correctly matched company page receives `SECTOR_PASS` only when the LinkedIn industry is one of:

- `Hospitals and Health Care`
- `Hospitals`
- `Biotechnology`
- `Biotechnology Research`
- `Pharmaceutical Manufacturing`
- `Medical Equipment Manufacturing`
- `Medical Device`

This sector gate does not replace any earlier hospital, inpatient, archetype, Core Signal, Supporting Signal, or use-case requirement.

### Decision logic

**SECTOR_PASS**

The LinkedIn page is the correct entity and its industry is on the approved list.

The account may proceed to the final account decision.

**ENTITY_MISMATCH**

The retrieved LinkedIn page belongs to a different same-name or similar-name company.

Example: the researched hospital name resolves to an IT consulting, construction, consulting, real-estate, staffing, financial-services, or unrelated software company.

Action: locate the correct LinkedIn company page and rerun Gate A11. Do not PASS while the entity mismatch remains.

**SECTOR_MISMATCH**

The LinkedIn page is confirmed to be the correct company, but its LinkedIn industry is not on the approved healthcare/medical sector list.

Decision: `REJECT - R11_LINKEDIN_SECTOR_MISMATCH`.

The account cannot be moved to SOP 2.

## Gate A12 - Final Account Decision

### PASS
All mandatory gates pass, including `linkedin_sector_status = SECTOR_PASS`.

### REVIEW
Only a specific resolvable gap remains.

Every REVIEW must include:
- missing fact;
- why it matters;
- best verification source;
- exact next action.

### REJECT
Hard exclusion or failed mandatory gate.

# 12. Intent and Why Now

Do not confuse structural fit with timing.

`FIT` asks whether this is a strong type of hospital for the platform.

`CURRENT_SIGNAL` asks whether there is a recent reason timing may be better now.

An account may PASS with `CURRENT_SIGNAL = NONE_FOUND`.

Invalid timing signals include generic AI strategy, generic digital transformation, general hospital awards, general nurse-shortage articles, and industry trends with no account-specific evidence.

# 13. Company Priority

No 100-point account score is required in SOP 1.

## `A_PRIORITY`
All mandatory gates PASS, plus strong direct evidence and a clear use case. Usually has either a STRONG/PRESENT current signal or exceptionally clear structural fit.

## `B_PRIORITY`
All mandatory gates PASS, but timing, scale, or commercial value is lower than A.

## `PASS_UNRANKED`
Account passes, but current public evidence is insufficient to fairly distinguish A vs B.

Do not force ranking.

# 14. Decision-Maker Research Strategy

Not Applicable - person research belongs to SOP 2.

SOP 1 may identify relevant downstream functions only to confirm a plausible buying group exists.

# 15. People Discovery

Not Applicable - handled in SOP 2.

# 16. Person Qualification Rules

Not Applicable - handled in SOP 2 and SOP 3.

# 17. P1 / P2 / P3 Logic

Not Applicable - handled in SOP 2 and SOP 4.

# 18. Contact Enrichment

Not Applicable - no email, phone, or paid person enrichment in SOP 1.

This is a hard cost-control rule.

# 19. Dedupe and Entity Integrity

## 19.1 Company dedupe keys

Check in this order:

1. canonical domain;
2. parent-system identity;
3. facility name + city + state;
4. official address where needed;
5. known acquired/renamed entity history.

## 19.2 Parent / subsidiary handling

A parent health system and an individual hospital may both exist as records only when there is a clear commercial reason.

Do not create both merely to increase volume.

## 19.3 Acquired hospital

If acquired:
- retain current operating identity;
- store former name as alias;
- store parent system;
- determine facility-level vs system-level buying authority;
- REVIEW if commercial account level is unclear.

## 19.4 Multiple campuses

Do not create separate campus accounts automatically.

Separate only when technology environment differs materially, local buying authority exists, or the use case is facility-specific.

# 20. Automation Architecture

## SOURCE COLLECTION
Input -> candidate account name / source.
Process -> collect relevant URLs and metadata.
Output -> unverified source bundle.
Failure -> REVIEW at A0 if entity unresolved.

## PARSING
Input -> source bundle.
Process -> extract entity, location, structure, signals, dates, vendors, negative evidence.
Output -> raw structured claims.

## NORMALIZATION
Input -> raw claims.
Process -> map to controlled fields/enums.
Output -> normalized account record.

## AI CLASSIFICATION
AI may classify archetype/signals, propose use case, detect conflicts, and recommend decision.
AI may not final-approve unsupported claims.

## VERIFICATION
Check directness, freshness, contradictions, relationship overlap, exclusions, and the final LinkedIn company-page/industry match under Gate A11.

## HUMAN QA
Required when:
- relationship overlap possible;
- current technology conflict exists;
- entity structure ambiguous;
- academic/tertiary exception proposed;
- Tier B carries a major qualification claim;
- REJECT depends on competitor-lock conclusion.

## STORAGE
Store canonical record, evidence, decision, reasons, timestamps, and QA identity.

## OUTREACH HANDOFF
Not Applicable. PASS accounts go only to SOP 2.

# 21. AI Usage Rules

## AI may

- discover candidate accounts;
- extract facts;
- normalize names;
- classify archetypes;
- classify Core/Supporting Signals;
- detect duplicates;
- detect stale evidence;
- detect conflicts;
- summarise evidence;
- propose primary use case;
- validate the final LinkedIn company-page/industry match under Gate A11;
- recommend PASS/REVIEW/REJECT;
- draft reviewer card.

## AI must not

- invent bed counts;
- invent EHR;
- invent device vendors;
- assume multi-vendor complexity;
- assume manual documentation;
- assume current technology from old source;
- assume buying authority;
- assume partner overlap absent;
- accept a same-name LinkedIn company page without matching it to the researched entity;
- treat generic technology initiative as monitoring signal;
- convert inference into fact;
- lower thresholds to increase PASS count;
- conduct person-level enrichment in SOP 1.

Every material AI conclusion must point to one or more `evidence_id` values.

# 22. Review / Reject / Approve Rules

## PASS
All mandatory gates pass.

## REVIEW
Only a specific resolvable gap remains.

Required:
- `missing_fact`
- `why_it_matters`
- `verification_source`
- `exact_next_action`

Forbidden review reason: `Needs more research`.

## REJECT
Hard exclusion or failed mandatory gate.

Controlled rejection codes:
- `R01_OUT_OF_SCOPE_GEO`
- `R02_WRONG_ACCOUNT_TYPE`
- `R03_NO_INPATIENT_MONITORING`
- `R04_CORE_PROBLEM_ALREADY_SOLVED`
- `R05_PROTECTED_RELATIONSHIP`
- `R06_DUPLICATE_ENTITY`
- `R07_CLOSED_INACTIVE`
- `R08_EVIDENCE_INSUFFICIENT`
- `R09_WRONG_ENTITY`
- `R10_NO_CREDIBLE_USE_CASE`
- `R11_LINKEDIN_SECTOR_MISMATCH`

# 23. Final Handoff Standard

A record may leave SOP 1 only when:

- `qualification_status = PASS`;
- `handoff_ready = true`;
- self-QA complete;
- canonical entity complete;
- Core Signal complete;
- Supporting Signal complete;
- primary use case complete;
- relationship overlap cleared;
- LinkedIn company page matched;
- `linkedin_sector_status = SECTOR_PASS`;
- evidence traceable;
- no unresolved material conflict.

## Required handoff package to SOP 2

- account identity;
- parent/facility structure;
- state/city;
- archetype;
- bed count if known;
- site count if known;
- Core Signals;
- Supporting Signals;
- primary use case;
- secondary use cases;
- current signal;
- known EHR only where material;
- known monitoring vendors only where material;
- negative evidence summary;
- relationship-overlap status;
- LinkedIn company URL;
- LinkedIn company name;
- LinkedIn industry;
- LinkedIn sector status;
- priority class;
- reviewer-ready account card;
- evidence links.

SOP 2 must not have to rediscover why the account qualified.

# 24. Metrics and Feedback Loop

Track:

- candidate accounts discovered;
- entity-failure rate;
- discovery-to-PASS rate;
- REVIEW rate;
- REJECT rate;
- rejection reasons by code;
- percentage of PASS accounts with A1/A2 primary evidence;
- stale-evidence rate;
- conflict rate;
- duplicate rate;
- LinkedIn entity-mismatch rate;
- LinkedIn sector-mismatch rate;
- average research time per PASS;
- average research time per REJECT;
- current-signal distribution;
- downstream qualified people per PASS account;
- downstream Golden representation per PASS account once SOP 4 data exists.

If downstream data shows a recurring failure pattern, update this SOP using batch evidence, not intuition.

# 25. Common Failure Modes

| Error | Why dangerous | Detection | Correction |
|---|---|---|---|
| Famous-hospital bias | Wastes capacity | No Core + Supporting Signal | Reject |
| Bed-count bias | Misses strong small hospitals | Direct monitoring signal despite small size | Apply archetype logic |
| ICU-only inference | Too broad | No specific monitoring/integration evidence | Do not PASS |
| Generic virtual-care bias | Wrong use case | Program unrelated to physiologic monitoring | Do not count as Core Signal |
| Old case-study error | Wrong current stack | Source outside freshness window | Refresh/triangulate |
| Single-vendor rejection | Throws away valid accounts | No evidence core problem solved | Do not reject |
| AI-strategy false positive | No product relevance | No U1-U5 connection | Ignore |
| Job-posting overreach | False intent | Hiring only | Supporting Signal only |
| Parent/facility confusion | Wrong buyer later | Entity conflict | Resolve A0 |
| Same-name LinkedIn company mismatch | Unrelated company can enter the dataset under a similar name | LinkedIn page/domain/sector does not match researched entity | Resolve at Gate A11 before PASS |
| Protected-account leakage | Attribution conflict | Overlap not cleared | REVIEW/REJECT |
| Evidence stacking | Weak sources create false confidence | No direct evidence | Require direct/triangulated proof |
| Quota bias | Threshold drift | Decisions change near target | Keep volume out of qualification |

# 26. Worked Examples

All examples are fictional.

## Excellent company - PASS / A_PRIORITY

Regional system with 3 acute hospitals, current centralized monitoring, evidence of heterogeneous device environments, relevant clinical-engineering hiring, and no current comprehensive incumbent solving the same problem.

Primary use case: `U3_CENTRALIZED_MONITORING`
Secondary: `U2_DEVICE_EHR_INTEROPERABILITY`
Decision: PASS / A_PRIORITY

## Excellent small hospital - PASS / A_PRIORITY

Critical-access hospital with 24 beds, inpatient telemetry, and tele-ICU coverage.

Primary use case: `U4_REMOTE_SPECIALIST_TELE_ICU`
Decision: PASS

Bed count does not weaken the account because the operating problem is direct.

## Borderline company - REVIEW

Community acute hospital with telemetry confirmed but no verified Supporting Signal yet.

Decision: REVIEW
Next action: verify monitor-tech hiring, clinical-engineering environment, recent technology projects, or documentation workflow.

## False positive - REJECT

Outpatient specialty network with no inpatient operation.

Decision: `REJECT - R02_WRONG_ACCOUNT_TYPE`

## Famous but weak - REJECT

Large academic hospital with broad AI strategy and Epic but no specific monitoring, interoperability, tele-ICU, or centralized-monitoring use case.

Decision: `REJECT - R10_NO_CREDIBLE_USE_CASE`

## Incumbent conflict - REVIEW then REJECT

Regional system with relevant telemetry, but current evidence suggests recent enterprise-wide deployment of a comprehensive vendor-neutral monitoring and device-integration platform.

Verify scope first.
If it covers the same use case across relevant facilities: `REJECT - R04_CORE_PROBLEM_ALREADY_SOLVED`.

## Protected account - REJECT from new-business dataset

Excellent-fit community hospital already covered by an existing strategic relationship.

Decision: `REJECT - R05_PROTECTED_RELATIONSHIP`

# 27. AI Execution Contract

```text
You are executing SOP 1 - Account Research & Qualification for an inpatient hospital monitoring, interoperability, and clinical-workflow platform.

Your task is to qualify ACCOUNTS only.

Do not research decision-makers, emails, phone numbers, LinkedIn activity, or P1/P2/P3.

CURRENT GEOGRAPHY:
Only Indiana, Ohio, Kentucky, Texas, and Alabama are in scope.

ACTIVE-DISCOVERY ARCHETYPES:
COMMUNITY_ACUTE
REGIONAL_MULTI_SITE
CRITICAL_ACCESS
RURAL_ACUTE
LTACH_POST_ACUTE

ACADEMIC_TERTIARY is exception-only and may enter only when a specific current monitoring/interoperability/tele-ICU/central-monitoring use case is already visible.

QUALIFICATION STANDARD:
A PASS account requires:
1. correct entity;
2. approved geography;
3. approved account type;
4. verified inpatient operation;
5. at least one verified Core Signal;
6. at least one verified Supporting Signal;
7. exactly one evidence-backed primary use case U1-U5;
8. no hard exclusion;
9. relationship overlap cleared;
10. sufficient current evidence;
11. no unresolved decision-changing conflict;
12. final LinkedIn company-page validation completed;
13. linkedin_sector_status = SECTOR_PASS.

FINAL LINKEDIN COMPANY-SECTOR VALIDATION:
Run this after all preceding account-qualification gates and before the final PASS decision.

Capture:
linkedin_company_url
linkedin_company_name
linkedin_industry
linkedin_sector_status

Approved LinkedIn industries:
Hospitals and Health Care
Hospitals
Biotechnology
Biotechnology Research
Pharmaceutical Manufacturing
Medical Equipment Manufacturing
Medical Device

If the LinkedIn page belongs to another same-name/similar-name company:
set linkedin_sector_status = ENTITY_MISMATCH,
find the correct LinkedIn company page,
and rerun the gate.

If the LinkedIn page is confirmed as the correct entity but the industry is outside the approved list:
set linkedin_sector_status = SECTOR_MISMATCH
and REJECT with R11_LINKEDIN_SECTOR_MISMATCH.

Only SECTOR_PASS may proceed to final PASS and SOP 2.

CORE SIGNALS:
CS_TELEMETRY_CARDIAC_MONITORING
CS_CENTRAL_MONITORING
CS_TELE_ICU_VIRTUAL_CRITICAL_CARE
CS_DEVICE_EHR_INTEGRATION
CS_CLINICAL_ENGINEERING_MONITORING
CS_MULTI_VENDOR_INPATIENT_MONITORING
CS_MANUAL_MONITORING_DOCUMENTATION

SUPPORTING SIGNALS:
SS_MULTI_SITE
SS_MULTI_VENDOR_COMPLEXITY
SS_RELEVANT_HIRING
SS_RECENT_EXPANSION
SS_RECENT_ACQUISITION
SS_EHR_OR_INTEGRATION_CHANGE
SS_STAFFING_PRESSURE
SS_REMOTE_SPECIALIST_NEED
SS_ACTIVE_MONITORING_PROJECT
SS_VIRTUAL_CARE_PROGRAM
SS_DOCUMENTATION_AUTOMATION
SS_STANDARDISATION_NEED

PRIMARY USE CASES:
U1_DIGITAL_RHYTHM_WORKFLOW
U2_DEVICE_EHR_INTEROPERABILITY
U3_CENTRALIZED_MONITORING
U4_REMOTE_SPECIALIST_TELE_ICU
U5_AUTOMATED_DOCUMENTATION

DECISIONS:
PASS
REVIEW
REJECT

REVIEW is allowed only when a specific resolvable fact is missing. State:
- missing_fact
- why_it_matters
- best_verification_source
- exact_next_action

Never use "Needs more research" as a complete review reason.

REJECT when a hard exclusion or mandatory gate fails.

Do not lower standards because of desired dataset size.

For every material conclusion use:
FACT -> EVIDENCE -> INTERPRETATION -> DECISION IMPACT.

Facts must have traceable evidence.
Inference must be labelled.
Missing information must not be invented.

Use claim-specific source quality.
Prefer direct current evidence.
Discovery databases may discover accounts but should not independently prove material qualification claims when stronger verification is available.

For every likely PASS account, actively search for negative evidence that the core problem is already solved, the account is protected by an existing relationship, technology information is stale, entity identity changed, or the proposed use case is wrong.

Return one deterministic JSON object per account using the canonical schema.
Every PASS must include a reviewer-ready account card.
```

## Canonical AI Output JSON

```json
{
  "account_id": "",
  "canonical_account_name": "",
  "facility_name": "",
  "parent_system_name": "",
  "canonical_domain": "",
  "linkedin_company_url": "",
  "linkedin_company_name": "",
  "linkedin_industry": "",
  "linkedin_sector_status": "",
  "state": "",
  "city": "",
  "account_archetype": "",
  "bed_count": "UNKNOWN",
  "facility_count": "UNKNOWN",
  "acute_site_count": "UNKNOWN",
  "core_signals": [],
  "supporting_signals": [],
  "primary_use_case": "",
  "secondary_use_cases": [],
  "current_signal": "",
  "relationship_overlap_status": "",
  "hard_exclusion_code": "NONE",
  "negative_evidence_summary": "",
  "technology_context": {
    "telemetry_evidence_status": "UNKNOWN",
    "cardiac_monitoring_status": "UNKNOWN",
    "clinical_engineering_status": "UNKNOWN",
    "ehr_platform": "NOT_CHECKED",
    "monitoring_vendors_found": [],
    "central_monitoring_status": "UNKNOWN",
    "tele_icu_status": "UNKNOWN",
    "virtual_care_status": "UNKNOWN",
    "manual_documentation_status": "UNKNOWN",
    "interoperability_status": "UNKNOWN"
  },
  "evidence": [],
  "fact_evidence_interpretation_decisions": [],
  "conflict_status": "NONE",
  "missing_fact": null,
  "next_verification_action": null,
  "qualification_status": "",
  "priority_class": "",
  "review_reason_code": null,
  "reject_reason_code": null,
  "why_this_account": {
    "operating_environment": "",
    "likely_problem": "",
    "commercial_route": ""
  },
  "qa_status": "",
  "handoff_ready": false,
  "last_verified_at": ""
}
```

# Reviewer-Ready Account Card

Every PASS account must also produce:

```text
ACCOUNT:
PARENT SYSTEM:
LOCATION:
ARCHETYPE:
BEDS / SITES:

PRIMARY USE CASE:
SECONDARY USE CASES:

CORE SIGNAL:
SUPPORTING SIGNALS:

WHY THIS ACCOUNT:
Operating environment:
Likely problem:
Commercial route:

CURRENT SIGNAL:
KNOWN EHR: only if material
KNOWN DEVICE / MONITORING ENVIRONMENT: only if material

NEGATIVE EVIDENCE:
RELATIONSHIP OVERLAP:

LINKEDIN COMPANY PAGE:
LINKEDIN INDUSTRY:
LINKEDIN SECTOR STATUS:

TOP EVIDENCE:
1.
2.
3. if necessary

PRIORITY:
FINAL STATUS:
REVIEW GAP / REJECT REASON:
NEXT ACTION:
```

# FINAL SELF-QA CHECKLIST

Before PASS or handoff:

- [ ] Correct organisation/entity?
- [ ] State is IN/OH/KY/TX/AL?
- [ ] Approved archetype?
- [ ] Inpatient operation verified?
- [ ] At least one Core Signal directly supported?
- [ ] At least one Supporting Signal supported?
- [ ] Exactly one primary use case assigned?
- [ ] Hard exclusions checked?
- [ ] Existing/partner relationship checked?
- [ ] Official LinkedIn company page matched to the researched entity?
- [ ] LinkedIn industry captured?
- [ ] LinkedIn sector status = SECTOR_PASS?
- [ ] Negative evidence searched?
- [ ] Material evidence URLs stored?
- [ ] Source dates/access dates stored?
- [ ] Freshness checked?
- [ ] Conflicts resolved or explicitly recorded?
- [ ] Facts separated from inference?
- [ ] "Why this account" supported by evidence?
- [ ] PASS decision independent of any desired dataset size?
- [ ] No person/contact enrichment performed prematurely?

One NO on a mandatory condition means the account cannot PASS.
