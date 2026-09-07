#!/usr/bin/env python3
"""Validate the fail-closed Issue #55 human execution-disposition contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = Path("Governance/AIOS-Stage15-Rehearsal-Execution-Disposition-Contract-v1.yaml")
LEDGER_PATH = Path("Governance/AIOS-Stage15-Local-Python-Rehearsal-Execution-Ledger-v1.yaml")

EXPECTED_RUN_IDS = [
    "STAGE15-LOCAL-ad8373c2401e",
    "STAGE15-LOCAL-33e2216976b7",
]
EXPECTED_AUTH_TREATMENTS = {
    "within_original_one_run_authorization",
    "outside_documented_authorization",
    "separately_ratified_bounded_governance_exception",
}
EXPECTED_EVIDENCE_TREATMENTS = {
    "eligible_for_issue52_evidence_review",
    "ineligible_for_issue52_evidence_review",
    "superseded_for_issue52_evidence_only_execution_history_preserved",
}
EXPECTED_INVALID_SUBSTITUTES = {
    "recurring_or_general_continue_instruction",
    "machine_authored_packet_or_recommendation",
    "green_tests_validators_or_actions",
    "pull_request_mergeability_or_draft_state",
    "issue_assignment_label_reaction_or_elapsed_time",
    "silence_or_failure_to_object",
    "a_decision_for_a_different_issue_pr_head_or_execution_set",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: mapping required")
    return loaded


def validate_repository(root: Path = ROOT) -> list[str]:
    resolved = Path(root).resolve()
    errors: list[str] = []
    for path in (CONTRACT_PATH, LEDGER_PATH):
        if not (resolved / path).is_file():
            errors.append(f"missing:{path.as_posix()}")
    if errors:
        return errors

    contract = _load_yaml(resolved / CONTRACT_PATH)
    ledger = _load_yaml(resolved / LEDGER_PATH)

    if contract.get("contract_version") != "aios_stage15_rehearsal_execution_disposition_contract/v1":
        errors.append("contract:version_drift")
    if contract.get("status") != "awaiting_explicit_tony_disposition":
        errors.append("contract:must_remain_awaiting_explicit_tony_disposition")

    target = contract.get("controlled_target")
    if not isinstance(target, dict):
        errors.append("contract:controlled_target_mapping_required")
        target = {}
    expected_target = {
        "reconciliation_issue": 55,
        "authorization_issue": 51,
        "evidence_acceptance_issue": 52,
        "lifecycle_issue": 53,
        "controlled_pr": 41,
        "controlled_pr_head": "8f73e1c54fe9bffb67c0c07600420aab4924c329",
        "execution_ledger": "Governance/AIOS-Stage15-Local-Python-Rehearsal-Execution-Ledger-v1.yaml",
    }
    for key, expected in expected_target.items():
        if target.get(key) != expected:
            errors.append(f"contract:controlled_target_drift:{key}")

    required_run_ids = contract.get("required_execution_ids")
    if required_run_ids != EXPECTED_RUN_IDS:
        errors.append("contract:required_execution_ids_drift")
    ledger_rows = ledger.get("recorded_executions")
    if not isinstance(ledger_rows, list):
        errors.append("ledger:recorded_executions_list_required")
        ledger_rows = []
    ledger_run_ids = [row.get("run_id") for row in ledger_rows if isinstance(row, dict)]
    if ledger_run_ids != EXPECTED_RUN_IDS:
        errors.append("contract:execution_set_must_match_append_only_ledger")

    boundary = contract.get("original_authorization_boundary")
    if not isinstance(boundary, dict):
        errors.append("contract:original_authorization_boundary_mapping_required")
        boundary = {}
    if boundary.get("owner") != "Tony":
        errors.append("contract:owner_must_be_tony")
    if boundary.get("authorized_execution_count") != 1:
        errors.append("contract:original_authorized_execution_count_must_be_one")
    if boundary.get("source_issue") != 51 or boundary.get("source_comment_id") != 5211821955:
        errors.append("contract:authorization_source_drift")
    if boundary.get("rule") != "one_bounded_local_isolated_python_rehearsal_only":
        errors.append("contract:authorization_rule_drift")

    requirements = contract.get("human_decision_requirements")
    if not isinstance(requirements, dict):
        errors.append("contract:human_decision_requirements_mapping_required")
        requirements = {}
    for key in (
        "decision_must_name_exact_pr_head",
        "decision_must_cover_every_required_execution_id",
        "execution_occurred_must_be_explicit",
        "authorization_treatment_must_be_explicit",
        "evidence_eligibility_for_issue52_must_be_explicit",
        "rationale_required_per_execution",
        "generic_continue_instruction_is_not_a_decision",
    ):
        if requirements.get(key) is not True:
            errors.append(f"contract:decision_requirement_must_be_true:{key}")
    if requirements.get("actor_must_be") != "Tony" or requirements.get("issue_must_be") != 55:
        errors.append("contract:human_decision_actor_or_issue_drift")

    if set(contract.get("allowed_authorization_treatments", [])) != EXPECTED_AUTH_TREATMENTS:
        errors.append("contract:authorization_treatment_enum_drift")
    if set(contract.get("allowed_evidence_eligibility_treatments", [])) != EXPECTED_EVIDENCE_TREATMENTS:
        errors.append("contract:evidence_treatment_enum_drift")

    constraints = contract.get("ratification_constraints", {}).get(
        "separately_ratified_bounded_governance_exception"
    )
    if not isinstance(constraints, dict):
        errors.append("contract:ratification_constraints_mapping_required")
        constraints = {}
    for key in (
        "historical_execution_record_must_be_preserved",
        "does_not_rewrite_original_one_run_authorization",
        "does_not_authorize_another_rehearsal",
        "does_not_authorize_ready_for_review",
        "does_not_authorize_merge",
        "does_not_authorize_risk_acceptance",
        "does_not_authorize_real_pilot_or_real_data",
        "does_not_authorize_permissions_connectors_infrastructure",
        "does_not_authorize_production_release_or_deployment",
    ):
        if constraints.get(key) is not True:
            errors.append(f"contract:ratification_constraint_must_be_true:{key}")

    if set(contract.get("anti_replay_invalid_substitutes", [])) != EXPECTED_INVALID_SUBSTITUTES:
        errors.append("contract:anti_replay_invalid_substitutes_drift")

    resolution = contract.get("resolution_rule")
    if not isinstance(resolution, dict):
        errors.append("contract:resolution_rule_mapping_required")
        resolution = {}
    for key in (
        "unresolved_until_one_explicit_tony_record_covers_both_required_execution_ids",
        "machine_must_not_infer_which_run_consumed_original_authorization",
        "machine_must_not_retroactively_invalidate_a_recorded_execution",
        "no_new_rehearsal_as_repair_mechanism",
    ):
        if resolution.get(key) is not True:
            errors.append(f"contract:resolution_rule_must_be_true:{key}")

    decision = contract.get("current_decision_record")
    if not isinstance(decision, dict):
        errors.append("contract:current_decision_record_mapping_required")
        decision = {}
    if decision.get("recorded") is not False:
        errors.append("contract:machine_must_not_record_human_disposition")
    if decision.get("record_url") is not None or decision.get("actor") is not None:
        errors.append("contract:human_decision_reference_must_be_empty_while_unresolved")
    if decision.get("per_execution_disposition") != []:
        errors.append("contract:per_execution_disposition_must_be_empty_while_unresolved")

    downstream = contract.get("downstream_authority")
    if not isinstance(downstream, dict) or not downstream:
        errors.append("contract:downstream_authority_mapping_required")
    elif any(value is not False for value in downstream.values()):
        errors.append("contract:downstream_authority_escalation")
    if contract.get("external_actions_performed") != []:
        errors.append("contract:external_actions_present")

    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 rehearsal execution disposition contract validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIOS Stage 15 rehearsal execution disposition contract validation PASSED")
    print("decision_state=awaiting_explicit_tony_disposition")
    print("required_execution_count=2")
    print("generic_continue_instruction_valid=false")
    print("downstream_authority_granted=false")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
