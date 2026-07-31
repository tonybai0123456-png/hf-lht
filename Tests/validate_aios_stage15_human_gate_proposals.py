from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml")
CANDIDATE_PATH = Path(
    "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml"
)
INTEGRATION_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
)
GUIDE_PATH = Path("Tests/AIOS-Stage15-Human-Gate-Proposals-Validation.md")
WORKFLOW_PATH = Path(
    ".github/workflows/validate-aios-support-controlled-pilot.yml"
)

GATE_ORDER = (
    "HG-SPEC-APPROVAL",
    "HG-PLAN-APPROVAL",
    "HG-EXECUTION-ASSIGNMENT",
    "HG-IMPLEMENTATION-EVIDENCE",
    "HG-NAMED-OWNER",
    "HG-ARCH-SECURITY",
    "HG-PRIVACY-DATA",
    "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
    "HG-RISK-DISPOSITION",
    "HG-PILOT-SCOPE",
    "HG-PILOT-EVIDENCE",
    "HG-RELEASE",
)
PROPOSAL_GATE_IDS = GATE_ORDER[6:11]
PROPOSAL_ISSUES = ("#44", "#45", "#46", "#47", "#48")
PROPOSAL_SCOPES = (
    "synthetic_privacy_data_only",
    "synthetic_operations_recovery_incident_support_only",
    "risk_treatment_direction_without_acceptance",
    "synthetic_rehearsal_only_no_real_pilot",
    "synthetic_rehearsal_evidence_only",
)
PROPOSAL_APPROVERS = ("Tony", "Stone", "Tony", "Tony", "Stone")
PROPOSAL_BACKUPS = ("Stone", "Tony", "Stone", "Stone", "Tony")
PROPOSAL_TECHNICAL_OWNERS = (
    "Data Agent",
    "Developer Agent",
    "risk_treatment_evidence_by_mapped_agents",
    "Developer Agent",
    "Data Agent",
)
PROPOSAL_CONTRIBUTORS = (
    ["Developer Agent"],
    ["CustomerService Agent", "Data Agent"],
    ["Developer Agent", "Data Agent", "CustomerService Agent", "CEO Agent"],
    ["CustomerService Agent", "Data Agent"],
    ["Developer Agent", "CustomerService Agent"],
)
PROPOSAL_APPROVAL_CONDITIONS = (
    "explicit_owner_approval_after_exact_contract_review",
    "gate7_accepted_then_explicit_owner_approval",
    "gates7_and_8_accepted_then_explicit_owner_approval",
    "gates7_through_9_accepted_then_explicit_zero_participant_scope_approval",
    "gate10_accepted_then_exact_head_synthetic_evidence_human_approval",
)
PROPOSAL_SPECIAL_KEYS = (
    ("allowed_scope_details", "prohibited_scope_details"),
    ("allowed_scope_details", "prohibited_scope_details", "design_targets"),
    ("risk_treatments", "required_evidence"),
    ("zero_participants", "entry_conditions", "stop_conditions"),
    ("truth_labels", "required_evidence", "unacceptable_evidence"),
)
FALSE_CLAIMS = {
    "risk_accepted": False,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
}
RISK_IDS = tuple(f"PR-RISK-{number:03d}" for number in range(1, 11))
RISK_HUMAN_OWNERS = (
    "Stone",
    "Stone",
    "Tony",
    "Tony",
    "Stone",
    "Stone",
    "Stone",
    "Stone",
    "Tony",
    "Tony",
)
RISK_TECHNICAL_SUPPORT = (
    ["Developer Agent"],
    ["Developer Agent"],
    ["Data Agent"],
    ["Data Agent"],
    ["Developer Agent", "Data Agent"],
    ["Developer Agent"],
    ["Developer Agent"],
    ["CustomerService Agent"],
    ["Data Agent", "CEO Agent"],
    ["CEO Agent"],
)


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [_error(path, "mapping_required")]
    if tuple(value.keys()) != expected:
        return [_error(path, "exact_keys_required")]
    return []


def _fail_closed(
    validator: Callable[[Any], list[str]],
    value: Any,
    path: str,
) -> list[str]:
    try:
        copied = copy.deepcopy(value)
        errors = validator(copied)
        if not isinstance(errors, list) or not all(
            isinstance(error, str) for error in errors
        ):
            return [_error(path, "validator_contract_error")]
        return errors
    except Exception as exc:
        return [_error(path, f"validation_exception:{type(exc).__name__}")]


def _load_controlled_yaml(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"{path}: symlink is not allowed")
    text = path.read_text(encoding="utf-8")
    try:
        for token in yaml.scan(text):
            if isinstance(token, (AnchorToken, AliasToken)):
                raise ValueError(f"{path}: YAML anchors and aliases are not allowed")
            if isinstance(token, ScalarToken) and token.value == "<<":
                raise ValueError(f"{path}: YAML merge keys are not allowed")
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: controlled YAML must be a mapping")
    return loaded


def load_proposals(root: Path = ROOT) -> dict[str, Any]:
    resolved_root = root.resolve()
    path = resolved_root / MODEL_PATH
    if path.resolve().parent != (resolved_root / "Governance").resolve():
        raise ValueError("proposal path escapes repository")
    return _load_controlled_yaml(path)


def _validate_common_proposal(
    proposal: Any,
    index: int,
) -> list[str]:
    path = f"$.proposals[{index}]"
    if not isinstance(proposal, dict):
        return [_error(path, "mapping_required")]
    expected_keys = (
        "gate_id",
        "issue",
        "accepted",
        "state",
        "prerequisite_gates",
        "scope_type",
        "human_approver",
        "backup_and_escalation_contact",
        "technical_owner",
        "contributors",
        *PROPOSAL_SPECIAL_KEYS[index],
        "approval_condition",
        "authority_ceiling",
        "external_actions_allowed",
    )
    errors = _exact_keys(proposal, expected_keys, path)
    expected_common = {
        "gate_id": PROPOSAL_GATE_IDS[index],
        "issue": PROPOSAL_ISSUES[index],
        "accepted": False,
        "state": "proposed_awaiting_explicit_owner_approval",
        "prerequisite_gates": list(GATE_ORDER[: 6 + index]),
        "scope_type": PROPOSAL_SCOPES[index],
        "human_approver": PROPOSAL_APPROVERS[index],
        "backup_and_escalation_contact": PROPOSAL_BACKUPS[index],
        "technical_owner": PROPOSAL_TECHNICAL_OWNERS[index],
        "contributors": PROPOSAL_CONTRIBUTORS[index],
        "approval_condition": PROPOSAL_APPROVAL_CONDITIONS[index],
        "authority_ceiling": "needs_human_governance",
        "external_actions_allowed": False,
    }
    for key, expected in expected_common.items():
        actual = proposal.get(key)
        if key in {"accepted", "external_actions_allowed"}:
            if type(actual) is not bool or actual is not expected:
                errors.append(_error(f"{path}.{key}", "exact_false_required"))
        elif actual != expected:
            errors.append(_error(f"{path}.{key}", "invalid"))
    return errors


def _validate_gate7(proposal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if proposal.get("allowed_scope_details") != [
        "synthetic_non_personal",
        "synthetic_personal_like_clearly_fictitious_non_routable",
    ]:
        errors.append(_error("$.proposals[0].allowed_scope_details", "invalid"))
    if proposal.get("prohibited_scope_details") != [
        "real_customer_employee_or_business_data",
        "copied_or_transformed_production_data",
        "live_identifiers_contact_details_or_payment_data",
        "secrets_credentials_tokens_or_permission_material",
        "live_connector_endpoint_or_infrastructure_account_material",
    ]:
        errors.append(
            _error("$.proposals[0].prohibited_scope_details", "invalid")
        )
    return errors


def _validate_gate8(proposal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if proposal.get("allowed_scope_details") != [
        "deterministic_stage13_prepare_only_runbook_validation",
        "synthetic_dependency_degradation_and_incident_tabletop",
        "task_local_snapshot_checksum_restore_cleanup_evidence",
        "synthetic_support_intake_triage_handoff_stop_withdrawal_closure",
        "exact_ordered_escalation_functions_no_external_delivery",
    ]:
        errors.append(_error("$.proposals[1].allowed_scope_details", "invalid"))
    if proposal.get("prohibited_scope_details") != [
        "real_monitoring_alerting_paging_ticket_or_external_message",
        "infrastructure_failover_backup_restore_or_rollback",
        "real_incident_support_case_or_sla_slo_claim",
        "production_staging_cloud_credential_connector_or_real_data",
    ]:
        errors.append(
            _error("$.proposals[1].prohibited_scope_details", "invalid")
        )
    if proposal.get("design_targets") != {
        "service_class": "CT-2",
        "rto_minutes": 240,
        "rpo_minutes": 60,
        "achieved_capability_claim": False,
        "sla_slo_committed": False,
    }:
        errors.append(_error("$.proposals[1].design_targets", "invalid"))
    return errors


def _validate_gate9(proposal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    risks = proposal.get("risk_treatments")
    if not isinstance(risks, list) or len(risks) != 10:
        return [_error("$.proposals[2].risk_treatments", "exact_length_required")]
    for index, (risk, risk_id, human_owner, technical_support) in enumerate(
        zip(risks, RISK_IDS, RISK_HUMAN_OWNERS, RISK_TECHNICAL_SUPPORT)
    ):
        path = f"$.proposals[2].risk_treatments[{index}]"
        expected = {
            "risk_id": risk_id,
            "human_treatment_owner": human_owner,
            "technical_support_agents": technical_support,
            "disposition": "mitigate_and_remain_open_blocked_unaccepted",
            "production_action_allowed": False,
        }
        if (
            not isinstance(risk, dict)
            or risk != expected
            or type(risk.get("production_action_allowed")) is not bool
        ):
            errors.append(_error(path, "closed_unaccepted_treatment_required"))
    if proposal.get("required_evidence") != [
        "gates6_through_8_exact_head_evidence",
        "exact_risk_to_evidence_mapping",
        "named_human_treatment_owner_per_risk",
        "residual_state_open_blocked_unaccepted",
        "risk_acceptance_false",
    ]:
        errors.append(_error("$.proposals[2].required_evidence", "invalid"))
    return errors


def _validate_gate10(proposal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if proposal.get("zero_participants") != {
        "real_customers": 0,
        "employees_or_real_operators": 0,
        "stores": 0,
        "production_or_staging_environments": 0,
        "real_cases_orders_accounts_or_messages": 0,
    }:
        errors.append(_error("$.proposals[3].zero_participants", "invalid"))
    if proposal.get("entry_conditions") != [
        "gates1_through_9_separately_accepted_and_verified",
        "all_risks_have_treatment_dispositions_but_remain_unaccepted",
        "stage10_remains_blocked_no_go",
        "external_actions_performed_empty",
    ]:
        errors.append(_error("$.proposals[3].entry_conditions", "invalid"))
    if proposal.get("stop_conditions") != [
        "real_or_unmarked_data",
        "cross_boundary_scope",
        "missing_evidence_or_owner",
        "requested_external_action",
        "support_recovery_or_metric_failure",
        "representation_as_real_pilot",
    ]:
        errors.append(_error("$.proposals[3].stop_conditions", "invalid"))
    return errors


def _validate_gate11(proposal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if proposal.get("truth_labels") != {
        "evidence_type": "synthetic_rehearsal_only",
        "real_pilot_performed": False,
        "pilot_authorized": False,
        "risk_accepted": False,
        "production_ready": False,
        "release_authorized": False,
    }:
        errors.append(_error("$.proposals[4].truth_labels", "invalid"))
    if proposal.get("required_evidence") != [
        "exact_commit_test_ci_and_evidence_identifiers",
        "synthetic_scope_and_company_brand_reconciliation",
        "environment_identity_data_evidence_observation_recovery_incident_support_results",
        "risk_to_evidence_mapping_pr_risk_001_through_010",
        "synthetic_support_case_human_closure",
        "external_actions_performed_empty",
    ]:
        errors.append(_error("$.proposals[4].required_evidence", "invalid"))
    if proposal.get("unacceptable_evidence") != [
        "narrative_or_screenshot_without_source_identifiers",
        "different_commit_or_incomplete_ci",
        "real_customer_employee_store_order_account_support_or_incident_data",
        "external_message_ticket_page_alert_or_connector_record",
        "invented_missing_duplicated_or_reordered_evidence_identifier",
        "real_pilot_production_rto_rpo_sla_slo_or_risk_acceptance_claim",
    ]:
        errors.append(_error("$.proposals[4].unacceptable_evidence", "invalid"))
    return errors


def _validate_proposals_impl(model: Any) -> list[str]:
    expected_keys = (
        "proposal_version",
        "stage",
        "stage_id",
        "status",
        "allowed_scope",
        "excluded_entities",
        "sequencing",
        "proposals",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, expected_keys, "$")
    if errors:
        return errors
    if model["proposal_version"] != "stage15_human_gate_proposals/v1":
        errors.append(_error("$.proposal_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["status"] != "prepared_unapproved_ordered_human_gate_proposals":
        errors.append(_error("$.status", "must_remain_unapproved"))
    if model["allowed_scope"] != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.allowed_scope", "invalid"))
    if model["excluded_entities"] != ["PC", "六合通"]:
        errors.append(_error("$.excluded_entities", "invalid"))
    if model["sequencing"] != {
        "accepted_gates": list(GATE_ORDER[:6]),
        "gate_order": list(GATE_ORDER),
        "next_gate": "HG-PRIVACY-DATA",
        "strict_dependency_order": True,
        "release_gate_accepted": False,
    }:
        errors.append(_error("$.sequencing", "strict_order_required"))

    proposals = model["proposals"]
    if not isinstance(proposals, list) or len(proposals) != 5:
        errors.append(_error("$.proposals", "exact_length_required"))
    else:
        special_validators = (
            _validate_gate7,
            _validate_gate8,
            _validate_gate9,
            _validate_gate10,
            _validate_gate11,
        )
        for index, (proposal, special_validator) in enumerate(
            zip(proposals, special_validators)
        ):
            errors.extend(_validate_common_proposal(proposal, index))
            if isinstance(proposal, dict):
                errors.extend(special_validator(proposal))

    claims = model["claims"]
    if (
        not isinstance(claims, dict)
        or claims != FALSE_CLAIMS
        or not all(type(value) is bool for value in claims.values())
    ):
        errors.append(_error("$.claims", "exact_false_claims_required"))
    if model["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_proposals(model: Any) -> list[str]:
    return _fail_closed(_validate_proposals_impl, model, "$proposals")


def evaluate_proposals(model: Any) -> dict[str, Any]:
    errors = validate_proposals(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "next_gate": "HG-PRIVACY-DATA",
            "accepted_proposal_gates": [],
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "not_ready_pending_human_governance",
        "reason_codes": list(PROPOSAL_GATE_IDS),
        "next_gate": "HG-PRIVACY-DATA",
        "accepted_proposal_gates": [],
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        proposals = load_proposals(root)
        candidate = _load_controlled_yaml(root / CANDIDATE_PATH)
        integration = _load_controlled_yaml(root / INTEGRATION_PATH)
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
        workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_proposals(proposals)

    candidate_gates = candidate.get("gate_ledger")
    candidate_pending = (
        candidate_gates[6:11] if isinstance(candidate_gates, list) else []
    )
    expected_candidate = list(
        zip(PROPOSAL_GATE_IDS, PROPOSAL_ISSUES)
    )
    actual_candidate = [
        (
            gate.get("gate_id"),
            gate.get("decision_evidence"),
        )
        if isinstance(gate, dict) and gate.get("accepted") is False
        else (None, None)
        for gate in candidate_pending
    ]
    if actual_candidate != [
        (gate_id, f"Issue {issue}") for gate_id, issue in expected_candidate
    ]:
        errors.append(
            _error(
                "$repository.candidate.gate_ledger",
                "unapproved_proposal_alignment_required",
            )
        )

    integration_gates = integration.get("human_gates")
    integration_pending = (
        integration_gates[6:11] if isinstance(integration_gates, list) else []
    )
    actual_integration = [
        gate.get("gate_id")
        if isinstance(gate, dict) and gate.get("authorized") is False
        else None
        for gate in integration_pending
    ]
    if actual_integration != list(PROPOSAL_GATE_IDS):
        errors.append(
            _error(
                "$repository.integration.human_gates",
                "unauthorized_alignment_required",
            )
        )

    guide_tokens = (
        "prepared_unapproved_ordered_human_gate_proposals",
        "not_ready_pending_human_governance",
        *PROPOSAL_GATE_IDS,
        "Issue #44",
        "Issue #45",
        "Issue #46",
        "Issue #47",
        "Issue #48",
        "Tony",
        "Stone",
        "Developer Agent",
        "Data Agent",
        "CustomerService Agent",
        "CEO Agent",
        "mitigate_and_remain_open_blocked_unaccepted",
        "synthetic_rehearsal_only_no_real_pilot",
        "synthetic_rehearsal_evidence_only",
        "Gate 12",
        "release expressly withheld",
        "accepted_proposal_gates=[]",
        "external_actions_performed=[]",
    )
    for token in guide_tokens:
        if token not in guide:
            errors.append(
                _error("$repository.guide", f"missing_token:{token}")
            )

    if not isinstance(workflow, dict) or workflow.get(True) != {
        "pull_request": None
    }:
        errors.append(
            _error("$repository.workflow.trigger", "pull_request_only_required")
        )
    if (
        not isinstance(workflow, dict)
        or workflow.get("permissions") != {"contents": "read"}
    ):
        errors.append(
            _error("$repository.workflow.permissions", "read_only_required")
        )
    if (
        "python3 -m unittest discover -s Tests -p 'test_*.py' -v"
        not in workflow_text
    ):
        errors.append(
            _error("$repository.workflow", "full_test_discovery_required")
        )
    for token in (
        "workflow_dispatch",
        "schedule:",
        "contents: write",
        "pull-requests: write",
        "persist-credentials: true",
    ):
        if token in workflow_text:
            errors.append(
                _error("$repository.workflow", f"forbidden_token:{token}")
            )
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 human-gate proposal validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_proposals(load_proposals(ROOT))
    print("AIOS Stage 15 human-gate proposal validation PASSED")
    print(f"result={result['result']}")
    print(f"next_gate={result['next_gate']}")
    print("accepted_proposal_gates=[]")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
