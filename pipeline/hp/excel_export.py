"""Export exactly two reader-facing sheets: People and Golden."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PIPELINE_ROOT.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "pipeline-dashboard" / "Hospital_People_Golden.xlsx"


PEOPLE_COLUMNS = [
    ("person_id", "Person ID"), ("full_name", "Name"), ("current_title", "Current Title"),
    ("current_company_display_name", "Hospital / System"), ("state", "State"),
    ("location_if_available", "Location"), ("linkedin_profile_url", "LinkedIn"),
    ("linkedin_identity_status", "LinkedIn Match"), ("person_status", "SOP2 Status"),
    ("validation_status", "SOP3 Status"), ("validated_priority", "Validated Priority"),
    ("validated_commercial_role", "Commercial Role"), ("validated_role_family", "Function"),
    ("role_scope", "Scope"), ("primary_use_case", "Use Case"),
    ("current_role_status", "Current Role"), ("employment_status", "Employment"),
    ("linkedin_activity_status", "LinkedIn Activity"), ("duplicate_status", "Duplicate Status"),
    ("account_id", "Account ID"), ("last_checked_at", "Last Checked"),
    ("missing_fact", "Missing Fact"), ("next_verification_action", "Next Action"),
]

GOLDEN_COLUMNS = [
    ("golden_rank", "Rank"), ("qualification_tier", "Validated?"),
    ("full_name", "Name"), ("validated_current_title", "Current Title"),
    ("account_name", "Hospital / System"), ("state", "State"), ("linkedin_profile_url", "LinkedIn"),
    ("validated_priority", "Priority"), ("validated_commercial_role", "Commercial Role"),
    ("validated_role_family", "Function"), ("role_scope", "Scope"), ("primary_use_case", "Use Case"),
    ("golden_priority_score", "Score"), ("account_quality_score", "Account"),
    ("use_case_strength_score", "Use Case Strength"), ("problem_ownership_score", "Ownership"),
    ("commercial_influence_score", "Influence"), ("validated_priority_score", "Priority Score"),
    ("current_signal_score", "Timing"), ("evidence_confidence_score", "Evidence"),
    ("linkedin_reachability_score", "Reachability"), ("golden_selection_reason", "Selection Reason"),
    ("canonical_person_id", "Person ID"), ("account_id", "Account ID"),
]


def _rows(con):
    people = [dict(row) for row in con.execute("""
        SELECT p.person_id,p.full_name,p.current_title,p.current_company_display_name,
               p.location_if_available,p.linkedin_profile_url,p.linkedin_identity_status,
               p.person_status,p.account_id,p.last_checked_at,p.primary_use_case,
               a.state, v.validation_status, v.validated_priority,
               v.validated_commercial_role, v.validated_role_family,
               COALESCE(v.role_scope,p.role_scope) role_scope,
               COALESCE(v.current_role_status,p.current_role_status) current_role_status,
               v.employment_status,
               COALESCE(v.linkedin_activity_status,p.linkedin_activity_status) linkedin_activity_status,
               COALESCE(v.duplicate_status,p.duplicate_status) duplicate_status,
               COALESCE(v.missing_fact,p.missing_fact) missing_fact,
               COALESCE(v.next_verification_action,p.next_verification_action) next_verification_action
        FROM people p
        LEFT JOIN accounts a ON a.account_id=p.account_id
        LEFT JOIN validations v ON v.person_id=p.person_id
        ORDER BY CASE COALESCE(v.validation_status,'') WHEN 'VALIDATED_PASS' THEN 0 WHEN 'VALIDATED_REVIEW' THEN 1 ELSE 2 END,
                 p.full_name, p.person_id
    """).fetchall()]
    # The DB unique index blocks canonical URL duplication. This final assertion also
    # protects exports created from manually altered databases.
    seen = set()
    unique_people = []
    for row in people:
        key = (row.get("linkedin_profile_url") or "").strip().lower().rstrip("/")
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        unique_people.append(row)
    golden = [dict(row) for row in con.execute("""
        SELECT g.*, a.canonical_account_name account_name, a.state
        FROM golden g LEFT JOIN accounts a ON a.account_id=g.account_id
        WHERE g.golden_status='GOLDEN_SELECTED'
        ORDER BY g.golden_rank, g.canonical_person_id
    """).fetchall()]
    return unique_people, golden


def export(con, output_path=None):
    output = Path(output_path or DEFAULT_OUTPUT).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    people, golden = _rows(con)
    payload = {
        "people": {"columns": PEOPLE_COLUMNS, "rows": people},
        "golden": {"columns": GOLDEN_COLUMNS, "rows": golden},
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }
    payload_path = PIPELINE_ROOT / "data" / "excel_export_payload.json"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False))
    node = os.environ.get("HP_NODE") or shutil.which("node") or "node"
    builder = PIPELINE_ROOT / "tools" / "build_excel.mjs"
    subprocess.run([node, str(builder), str(payload_path), str(output)], check=True, cwd=PIPELINE_ROOT)
    return {"path": str(output), "people": len(people), "golden": len(golden)}
