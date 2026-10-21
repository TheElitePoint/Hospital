PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ---------- universe ----------
CREATE TABLE IF NOT EXISTS universe (
  ccn TEXT PRIMARY KEY,
  facility_name TEXT, address TEXT, city TEXT, state TEXT, zip TEXT, county TEXT,
  phone TEXT, hospital_type TEXT, hospital_ownership TEXT, emergency_services TEXT,
  bed_count TEXT DEFAULT 'UNKNOWN',
  source TEXT, loaded_at TEXT,
  dedupe_key TEXT,
  in_scope INTEGER DEFAULT 0,          -- passed A1/A3 pre-filter
  prefilter_reason TEXT,
  account_id TEXT
);
CREATE INDEX IF NOT EXISTS ix_universe_state ON universe(state);

-- ---------- accounts (SOP 1) ----------
CREATE TABLE IF NOT EXISTS accounts (
  account_id TEXT PRIMARY KEY,
  ccn TEXT,
  canonical_account_name TEXT,
  facility_name TEXT,
  parent_system_name TEXT DEFAULT 'NOT_APPLICABLE',
  canonical_domain TEXT,
  state TEXT, city TEXT,
  account_archetype TEXT,
  bed_count TEXT DEFAULT 'UNKNOWN',
  facility_count TEXT DEFAULT 'UNKNOWN',
  acute_site_count TEXT DEFAULT 'UNKNOWN',
  linkedin_company_url TEXT, linkedin_company_name TEXT,
  linkedin_industry TEXT, linkedin_sector_status TEXT,
  primary_use_case TEXT,
  secondary_use_cases TEXT,            -- json array
  current_signal TEXT,
  relationship_overlap_status TEXT DEFAULT 'UNKNOWN_REVIEW',
  qualification_status TEXT,           -- PASS | REVIEW | REJECT
  priority_class TEXT,
  hard_exclusion_code TEXT DEFAULT 'NONE',
  review_reason_code TEXT, reject_reason_code TEXT,
  missing_fact TEXT, why_it_matters TEXT,
  verification_source TEXT, next_verification_action TEXT,
  negative_evidence_summary TEXT,
  why_operating_environment TEXT, why_likely_problem TEXT, why_commercial_route TEXT,
  conflict_status TEXT DEFAULT 'NONE',
  qa_status TEXT DEFAULT 'PENDING', qa_reviewer_id TEXT,
  handoff_ready INTEGER DEFAULT 0,
  pipeline_stage TEXT DEFAULT 'SOP1', stage_status TEXT DEFAULT 'PENDING',
  gate_trace TEXT,                     -- json: gate -> verdict
  researcher_id TEXT, research_started_at TEXT, research_completed_at TEXT,
  last_verified_at TEXT,
  sop_version TEXT, prompt_version TEXT
);
CREATE INDEX IF NOT EXISTS ix_accounts_status ON accounts(qualification_status);

CREATE TABLE IF NOT EXISTS account_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id TEXT NOT NULL,
  signal_class TEXT NOT NULL,          -- CORE | SUPPORTING
  signal_code TEXT NOT NULL,
  UNIQUE(account_id, signal_class, signal_code)
);

CREATE TABLE IF NOT EXISTS account_tech (
  account_id TEXT NOT NULL,
  field_name TEXT NOT NULL,
  status TEXT NOT NULL,                -- CONFIRMED|NOT_FOUND|UNKNOWN|NOT_APPLICABLE|NOT_CHECKED
  PRIMARY KEY (account_id, field_name)
);

-- ---------- evidence (shared) ----------
CREATE TABLE IF NOT EXISTS evidence (
  evidence_id TEXT PRIMARY KEY,
  subject_type TEXT NOT NULL,          -- ACCOUNT | PERSON
  subject_id TEXT NOT NULL,
  claim_key TEXT, claim_type TEXT, claim_value TEXT,
  source_url TEXT, source_title TEXT, source_owner TEXT,
  source_tier TEXT,                    -- A1|A2|B|C
  source_date TEXT, accessed_at TEXT,
  evidence_excerpt TEXT,
  freshness_status TEXT, directness TEXT,
  conflict_status TEXT DEFAULT 'NONE',
  verbatim_verified INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_evidence_subject ON evidence(subject_type, subject_id);

CREATE TABLE IF NOT EXISTS claim_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject_id TEXT NOT NULL, claim_key TEXT NOT NULL, evidence_id TEXT NOT NULL,
  UNIQUE(subject_id, claim_key, evidence_id)
);

CREATE TABLE IF NOT EXISTS fed_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  account_id TEXT NOT NULL,
  fact TEXT, evidence_ids TEXT, interpretation TEXT,
  decision_impact TEXT, confidence TEXT
);

-- ---------- people (SOP 2) ----------
CREATE TABLE IF NOT EXISTS people (
  person_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  full_name TEXT,
  linkedin_profile_url TEXT,
  linkedin_canonical_key TEXT,
  normalized_name TEXT,
  normalized_title TEXT,
  linkedin_identity_status TEXT,
  linkedin_activity_status TEXT DEFAULT 'NOT_CHECKED',
  current_company_display_name TEXT,
  current_title TEXT, department TEXT,
  role_family TEXT, seniority_level TEXT, role_scope TEXT,
  location_if_available TEXT,
  primary_use_case TEXT,
  person_use_case_relevance TEXT,
  problem_ownership_level TEXT,
  evaluation_influence TEXT, commercial_influence TEXT, technical_influence TEXT,
  internal_routing_value TEXT,
  current_role_status TEXT, profile_identity_confidence TEXT,
  initial_priority TEXT,
  better_person_json TEXT,
  duplicate_status TEXT DEFAULT 'UNIQUE',
  person_status TEXT,                  -- PERSON_PASS | REVIEW | REJECT
  review_reason TEXT, reject_reason_code TEXT,
  missing_fact TEXT, next_verification_action TEXT,
  pipeline_stage TEXT DEFAULT 'SOP2', stage_status TEXT DEFAULT 'PENDING',
  last_checked_at TEXT, prompt_version TEXT
);
CREATE INDEX IF NOT EXISTS ix_people_account ON people(account_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_people_li ON people(linkedin_profile_url)
  WHERE linkedin_profile_url IS NOT NULL AND linkedin_profile_url <> '';
CREATE TABLE IF NOT EXISTS duplicate_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id TEXT NOT NULL,
  candidate_person_id TEXT NOT NULL,
  key_type TEXT NOT NULL,              -- LINKEDIN|NAME_ACCOUNT|TITLE_ACCOUNT|CROSS_ACCOUNT
  key_value TEXT NOT NULL,
  resolution_status TEXT DEFAULT 'UNRESOLVED', -- UNRESOLVED|CONFIRMED_DUPLICATE|DISTINCT_PEOPLE
  detected_at TEXT NOT NULL,
  resolved_at TEXT,
  resolved_by TEXT,
  UNIQUE(person_id,candidate_person_id,key_type)
);

-- ---------- validation (SOP 3) ----------
CREATE TABLE IF NOT EXISTS validations (
  person_id TEXT PRIMARY KEY,
  canonical_person_id TEXT,
  account_id TEXT,
  linkedin_identity_status TEXT, identity_confidence TEXT,
  current_employer TEXT, account_entity_match TEXT, role_scope TEXT,
  validated_current_title TEXT, validated_department TEXT, validated_role_family TEXT,
  current_role_status TEXT, employment_status TEXT,
  primary_use_case TEXT, validated_commercial_role TEXT,
  problem_ownership_level TEXT, evaluation_influence TEXT, commercial_influence TEXT,
  technical_influence TEXT, clinical_influence TEXT, internal_routing_value TEXT,
  original_priority TEXT, validated_priority TEXT,
  priority_change_status TEXT DEFAULT 'UNCHANGED', priority_change_reason TEXT,
  better_person_gap_found INTEGER DEFAULT 0, better_function TEXT,
  better_person_name_if_known TEXT, return_to_sop2_required INTEGER DEFAULT 0,
  duplicate_status TEXT DEFAULT 'UNIQUE', duplicate_of_person_id TEXT,
  linkedin_activity_status TEXT, last_visible_reaction_date TEXT,
  linkedin_activity_checked_at TEXT, linkedin_activity_source TEXT,
  activity_run_status TEXT,            -- raw actor outcome, audits the UNKNOWN rule
  evidence_confidence TEXT,
  conflict_status TEXT DEFAULT 'NONE',
  missing_fact TEXT, why_it_matters TEXT,
  best_verification_source TEXT, next_verification_action TEXT,
  validation_status TEXT,              -- VALIDATED_PASS | VALIDATED_REVIEW | VALIDATED_REJECT
  workflow_status TEXT,                -- RETURN_TO_SOP1 | RETURN_TO_SOP2 | NULL
  reject_reason_code TEXT,
  validator_id TEXT, validated_at TEXT,
  qa_status TEXT DEFAULT 'PENDING', handoff_ready INTEGER DEFAULT 0,
  review_value_score REAL DEFAULT 0    -- drives the 30% review-queue slice
);

CREATE TABLE IF NOT EXISTS person_accounts (
  canonical_person_id TEXT NOT NULL,
  account_id TEXT NOT NULL,
  PRIMARY KEY (canonical_person_id, account_id)
);

CREATE TABLE IF NOT EXISTS correction_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject_type TEXT, subject_id TEXT,
  field_name TEXT, old_value TEXT, new_value TEXT,
  change_type TEXT,                    -- CORRECTION|PROMOTION|DEMOTION|SCOPE_CHANGE|ENTITY_CORRECTION|DUPLICATE_MERGE
  reason TEXT, evidence_ids TEXT, changed_at TEXT, changed_by TEXT
);

-- ---------- golden (SOP 4) ----------
CREATE TABLE IF NOT EXISTS golden (
  canonical_person_id TEXT PRIMARY KEY,
  person_id TEXT, account_id TEXT,
  full_name TEXT, linkedin_profile_url TEXT,
  validated_current_title TEXT, validated_department TEXT, validated_role_family TEXT,
  role_scope TEXT, validated_commercial_role TEXT, validated_priority TEXT,
  account_priority TEXT, account_archetype TEXT, primary_use_case TEXT, current_signal TEXT,
  linkedin_activity_status TEXT, last_visible_reaction_date TEXT,
  account_quality_score REAL, use_case_strength_score REAL, problem_ownership_score REAL,
  commercial_influence_score REAL, validated_priority_score REAL, current_signal_score REAL,
  evidence_confidence_score REAL, linkedin_reachability_score REAL,
  golden_priority_score REAL,
  incremental_value TEXT, role_family_already_represented INTEGER DEFAULT 0,
  distinct_scope_value TEXT, buying_group_contribution TEXT,
  golden_eligible INTEGER DEFAULT 0, golden_ineligible_reason TEXT,
  golden_rank INTEGER, golden_status TEXT,
  golden_selection_reason TEXT, golden_exclusion_reason TEXT,
  selection_cycle TEXT, golden_locked_at TEXT
);

CREATE TABLE IF NOT EXISTS golden_cycles (
  selection_cycle TEXT PRIMARY KEY,
  validated_input_unique_people INTEGER, golden_eligible_unique_people INTEGER,
  golden_selected_unique_people INTEGER, shortage_status TEXT, shortage_reasons TEXT,
  return_to_sop3_count INTEGER, locked_at TEXT, qa_status TEXT
);

CREATE TABLE IF NOT EXISTS golden_replacements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  selection_cycle TEXT, removed_person_id TEXT, added_person_id TEXT,
  reason TEXT, replaced_at TEXT
);

-- ---------- infrastructure ----------
CREATE TABLE IF NOT EXISTS api_cache (
  cache_key TEXT PRIMARY KEY,
  provider TEXT, request TEXT, payload TEXT,
  fetched_at TEXT, ttl_days INTEGER, http_status INTEGER
);

CREATE TABLE IF NOT EXISTS api_keys (
  key_id TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  secret TEXT NOT NULL,
  label TEXT,
  state TEXT DEFAULT 'ACTIVE',         -- ACTIVE | EXHAUSTED | INVALID | DISABLED
  added_at TEXT, last_used_at TEXT,
  cooldown_until TEXT,
  calls INTEGER DEFAULT 0, failures INTEGER DEFAULT 0,
  last_error TEXT, exhausted_at TEXT
);

-- A submitted Apify run is recorded before polling.  If the dashboard or laptop
-- restarts, the same logical request resumes that run instead of paying twice.
CREATE TABLE IF NOT EXISTS apify_runs (
  request_key TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL,
  run_id TEXT,
  dataset_id TEXT,
  status TEXT NOT NULL,                -- SUBMITTED|RUNNING|SUCCEEDED|FAILED|UNCERTAIN
  max_charge_usd REAL,
  submitted_at TEXT,
  updated_at TEXT,
  error TEXT
);

CREATE TABLE IF NOT EXISTS run_log (
  run_id TEXT PRIMARY KEY,
  sop TEXT, subject_type TEXT, subject_id TEXT,
  provider TEXT, model TEXT, prompt_version TEXT, key_id TEXT,
  tokens_in INTEGER, tokens_out INTEGER, cost_usd REAL,
  status TEXT, error TEXT,
  started_at TEXT, finished_at TEXT
);

CREATE TABLE IF NOT EXISTS human_input (
  subject_type TEXT, subject_id TEXT,
  qa_decision TEXT, qa_reviewer_id TEXT, qa_notes TEXT,
  manual_override_status TEXT, override_reason TEXT,
  synced_at TEXT,
  PRIMARY KEY (subject_type, subject_id)
);

-- ---------- local web control plane ----------
CREATE TABLE IF NOT EXISTS pipeline_jobs (
  job_id TEXT PRIMARY KEY,
  target_golden INTEGER NOT NULL,
  starting_golden INTEGER DEFAULT 0,
  status TEXT NOT NULL,                -- QUEUED|RUNNING|NEEDS_KEY|COMPLETE|SHORTAGE|FAILED|CANCELLED
  current_stage TEXT,
  required_provider TEXT,
  command TEXT,
  checkpoint_path TEXT,
  workbook_path TEXT,
  researched_people INTEGER DEFAULT 0,
  validated_people INTEGER DEFAULT 0,
  golden_people INTEGER DEFAULT 0,
  review_people INTEGER DEFAULT 0,
  rejected_people INTEGER DEFAULT 0,
  duplicate_people INTEGER DEFAULT 0,
  error TEXT,
  created_at TEXT,
  started_at TEXT,
  finished_at TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_pipeline_jobs_created ON pipeline_jobs(created_at DESC);

CREATE TABLE IF NOT EXISTS dashboard_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT,
  level TEXT NOT NULL,
  stage TEXT,
  message TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_dashboard_events_job ON dashboard_events(job_id, id);
