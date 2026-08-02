from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(
    "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml"
)
GUIDE_PATH = Path("Tests/AIOS-Deployment-Free-Candidate-Validation.md")
WORKFLOW_PATH = Path(
    ".github/workflows/validate-aios-support-controlled-pilot.yml"
)
INTEGRATION_MODEL_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
)
RECEIPT_MODEL_PATH = Path(
    "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml"
)

GATE_IDS = (
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
GATE_STATES = (
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "accepted",
    "release_withheld_by_objective",
)
PENDING_GATE_IDS = GATE_IDS[11:]
REASON_CODES = (
    "HG-RELEASE-WITHHELD-BY-OBJECTIVE",
)
EVIDENCE_IDS = tuple(f"DFC-EV-{number:02d}" for number in range(1, 13))
EVIDENCE_REQUIREMENTS = (
    "exact_commit_and_tree",
    "changed_file_and_asset_manifest",
    "clean_checkout_reproducibility",
    "local_tests_validators_compile_and_diff",
    "exact_head_ci",
    "gate_ledger_1_through_11",
    "risk_map_and_treatment_owners",
    "synthetic_control_evidence",
    "dependency_manifest_and_install_instructions",
    "scan_for_secrets_real_data_connectors_and_infrastructure_material",
    "withheld_authorities",
    "mandatory_return_external_actions_empty",
)
EVIDENCE_STATUSES = (
    "verified_external_capture",
    "verified",
    "verified",
    "verified",
    "verified",
    "verified",
    "verified_authorized_treatment_mapping_risks_unaccepted",
    "verified_synthetic_only",
    "complete",
    "verified",
    "complete",
    "complete",
)
FALSE_CLAIMS = {
    "risk_accepted": False,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
    "real_data_used": False,
    "connector_used": False,
    "infrastructure_provisioned": False,
    "credentials_used": False,
}
EXPECTED_DATA_GOVERNANCE = {
    "status": "authorized_by_human_governance",
    "allowed_data_classes": [
        "synthetic_non_personal",
        "synthetic_personal_like_clearly_fictitious_non_routable",
    ],
    "disallowed_data": [
        "real_customer_employee_or_business_data",
        "copied_or_transformed_production_data",
        "live_identifiers_contact_details_or_payment_data",
        "secrets_credentials_tokens_or_permission_material",
        "live_connector_endpoint_or_infrastructure_account_material",
    ],
    "human_approver": "Tony",
    "backup_and_escalation_contact": "Stone",
    "technical_validation_owner": "Data Agent",
    "implementation_support": "Developer Agent",
    "real_data_authorized": False,
    "credentials_or_permission_material_authorized": False,
    "connectors_or_endpoints_authorized": False,
    "infrastructure_or_accounts_authorized": False,
    "pilot_authorized": False,
    "risk_accepted": False,
    "merge_publication_or_deployment_authorized": False,
    "external_actions_allowed": False,
    "decision_evidence": "Owner authorization / Issue #44",
}
EVALUATED_DATA_GOVERNANCE = {
    "status": "authorized_by_human_governance",
    "human_approver": "Tony",
    "backup_and_escalation_contact": "Stone",
    "technical_validation_owner": "Data Agent",
    "implementation_support": "Developer Agent",
    "external_actions_allowed": False,
}
EXPECTED_OPERATIONS_GOVERNANCE = {
    "status": "authorized_by_human_governance",
    "scope_type": "synthetic_operations_recovery_incident_support_only",
    "human_approver": "Stone",
    "backup_and_escalation_contact": "Tony",
    "technical_owner": "Developer Agent",
    "evidence_contributors": [
        "CustomerService Agent",
        "Data Agent",
    ],
    "design_targets": {
        "service_class": "CT-2",
        "rto_minutes": 240,
        "rpo_minutes": 60,
        "achieved_capability_claim": False,
        "sla_slo_committed": False,
    },
    "real_operations_authorized": False,
    "external_actions_allowed": False,
    "decision_evidence": "Owner authorization / Issue #45",
}
EXPECTED_RISK_TREATMENT_GOVERNANCE = {
    "status": "authorized_by_human_governance",
    "scope_type": "risk_treatment_direction_without_acceptance",
    "human_approver": "Tony",
    "overall_risk_owner": "Tony",
    "independent_reviewer_and_escalation_contact": "Stone",
    "technical_evidence_contributors": [
        "Developer Agent",
        "Data Agent",
        "CustomerService Agent",
        "CEO Agent",
    ],
    "disposition": "mitigate_and_remain_open_blocked_unaccepted",
    "treatment_ownership_authorized": True,
    "risk_acceptance": False,
    "risk_closure": False,
    "production_action_allowed": False,
    "external_actions_allowed": False,
    "decision_evidence": "Owner authorization / Issue #46",
}
EXPECTED_SYNTHETIC_REHEARSAL_SCOPE_GOVERNANCE = {
    "status": "authorized_by_human_governance",
    "scope_type": "synthetic_rehearsal_only_no_real_pilot",
    "human_approver": "Tony",
    "backup_and_escalation_contact": "Stone",
    "technical_owner": "Developer Agent",
    "evidence_contributors": ["CustomerService Agent", "Data Agent"],
    "zero_participants": {
        "real_customers": 0,
        "employees_or_real_operators": 0,
        "stores": 0,
        "production_or_staging_environments": 0,
        "real_cases_orders_accounts_or_messages": 0,
    },
    "real_pilot_authorized": False,
    "external_actions_allowed": False,
    "decision_evidence": "Owner authorization / Issue #47",
}


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


def load_candidate_evidence(root: Path = ROOT) -> dict[str, Any]:
    resolved_root = root.resolve()
    path = resolved_root / MODEL_PATH
    if path.resolve().parent != (resolved_root / "Governance").resolve():
        raise ValueError("candidate evidence path escapes repository")
    return _load_controlled_yaml(path)


def _validate_candidate_evidence_impl(model: Any) -> list[str]:
    expected_keys = (
        "candidate_evidence_version",
        "stage",
        "stage_id",
        "status",
        "allowed_scope",
        "excluded_entities",
        "source_state",
        "gate_ledger",
        "data_governance",
        "operations_governance",
        "risk_treatment_governance",
        "synthetic_rehearsal_scope_governance",
        "risk_posture",
        "evidence_requirements",
        "candidate_decision",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, expected_keys, "$")
    if errors:
        return errors

    if model["candidate_evidence_version"] != (
        "deployment_free_candidate_evidence/v1"
    ):
        errors.append(_error("$.candidate_evidence_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["status"] != "deployment_free_candidate_ready_for_gate12_decision":
        errors.append(_error("$.status", "gate12_candidate_state_required"))
    if model["allowed_scope"] != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.allowed_scope", "invalid"))
    if model["excluded_entities"] != ["PC", "六合通"]:
        errors.append(_error("$.excluded_entities", "invalid"))

    source_state = model["source_state"]
    source_keys = (
        "reviewed_commit",
        "reviewed_tree",
        "gate_record_commit",
        "gate_record_tree",
        "technical_evidence_commit",
        "technical_evidence_tree",
        "technical_evidence_receipt",
        "pull_request",
        "parent_issue",
        "candidate_commit_state",
    )
    errors.extend(_exact_keys(source_state, source_keys, "$.source_state"))
    if isinstance(source_state, dict):
        if source_state.get("reviewed_commit") != (
            "b27614ba2ebebb772888c3a4b1ff3d829b47532e"
        ):
            errors.append(_error("$.source_state.reviewed_commit", "invalid"))
        if source_state.get("reviewed_tree") != (
            "d3fec0a73e1f5b90d3c5829b387095da1e2ff5e4"
        ):
            errors.append(_error("$.source_state.reviewed_tree", "invalid"))
        if source_state.get("gate_record_commit") != (
            "204fbde1b23c49a00e07bef9cefce035f6b27cc4"
        ):
            errors.append(_error("$.source_state.gate_record_commit", "invalid"))
        if source_state.get("gate_record_tree") != (
            "71e6b82e407b626bb256d2459109ea88be018e8b"
        ):
            errors.append(_error("$.source_state.gate_record_tree", "invalid"))
        if source_state.get("technical_evidence_commit") != (
            "36716abc76373d053c75e68352f46589f4ddc8f1"
        ):
            errors.append(
                _error("$.source_state.technical_evidence_commit", "invalid")
            )
        if source_state.get("technical_evidence_tree") != (
            "ec48f7c537162b32f6bc35947d9e49758e1b53bd"
        ):
            errors.append(
                _error("$.source_state.technical_evidence_tree", "invalid")
            )
        if source_state.get("technical_evidence_receipt") != (
            "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml"
        ):
            errors.append(
                _error("$.source_state.technical_evidence_receipt", "invalid")
            )
        if source_state.get("pull_request") != "#41 / Draft / open / unmerged":
            errors.append(_error("$.source_state.pull_request", "invalid"))
        if source_state.get("parent_issue") != "#40 / open":
            errors.append(_error("$.source_state.parent_issue", "invalid"))
        if source_state.get("candidate_commit_state") != (
            "external_capture_verified_pending_human_gates"
        ):
            errors.append(
                _error("$.source_state.candidate_commit_state", "invalid")
            )

    gates = model["gate_ledger"]
    if not isinstance(gates, list) or len(gates) != len(GATE_IDS):
        errors.append(_error("$.gate_ledger", "exact_length_required"))
    else:
        for index, (gate, gate_id, state) in enumerate(
            zip(gates, GATE_IDS, GATE_STATES)
        ):
            path = f"$.gate_ledger[{index}]"
            errors.extend(
                _exact_keys(
                    gate,
                    ("gate_id", "accepted", "state", "decision_evidence"),
                    path,
                )
            )
            if not isinstance(gate, dict):
                continue
            expected_accepted = index < 11
            if (
                gate.get("gate_id") != gate_id
                or type(gate.get("accepted")) is not bool
                or gate.get("accepted") is not expected_accepted
                or gate.get("state") != state
                or not isinstance(gate.get("decision_evidence"), str)
                or not gate.get("decision_evidence")
            ):
                errors.append(_error(path, "recorded_gate_state_required"))

    if model["data_governance"] != EXPECTED_DATA_GOVERNANCE:
        errors.append(
            _error("$.data_governance", "controlled_proposal_required")
        )
    if model["operations_governance"] != EXPECTED_OPERATIONS_GOVERNANCE:
        errors.append(
            _error(
                "$.operations_governance",
                "controlled_synthetic_operations_approval_required",
            )
        )
    if model["risk_treatment_governance"] != EXPECTED_RISK_TREATMENT_GOVERNANCE:
        errors.append(
            _error(
                "$.risk_treatment_governance",
                "controlled_risk_treatment_approval_required",
            )
        )
    if (
        model["synthetic_rehearsal_scope_governance"]
        != EXPECTED_SYNTHETIC_REHEARSAL_SCOPE_GOVERNANCE
    ):
        errors.append(
            _error(
                "$.synthetic_rehearsal_scope_governance",
                "controlled_zero_participant_scope_approval_required",
            )
        )
    risk_posture = model["risk_posture"]
    expected_risk_posture = {
        "stage10": "BLOCKED / NO-GO",
        "risk_count": 10,
        "risk_state": "open_blocked_unaccepted",
        "treatment_ownership": "authorized_for_treatment_evidence_only",
        "risk_acceptance": False,
    }
    if risk_posture != expected_risk_posture:
        errors.append(_error("$.risk_posture", "blocked_unaccepted_required"))

    evidence = model["evidence_requirements"]
    if not isinstance(evidence, list) or len(evidence) != len(EVIDENCE_IDS):
        errors.append(
            _error("$.evidence_requirements", "exact_length_required")
        )
    else:
        for index, expected in enumerate(
            zip(EVIDENCE_IDS, EVIDENCE_REQUIREMENTS, EVIDENCE_STATUSES)
        ):
            record = evidence[index]
            path = f"$.evidence_requirements[{index}]"
            errors.extend(
                _exact_keys(
                    record,
                    ("evidence_id", "requirement", "status"),
                    path,
                )
            )
            if not isinstance(record, dict):
                continue
            actual = (
                record.get("evidence_id"),
                record.get("requirement"),
                record.get("status"),
            )
            if actual != expected:
                errors.append(_error(path, "truthful_evidence_state_required"))

    decision = model["candidate_decision"]
    expected_decision = {
        "result": "ready_for_gate12_decision_release_withheld",
        "reason_codes": list(REASON_CODES),
        "remaining_human_gates": list(PENDING_GATE_IDS),
        "deployment_free_evidence_only": True,
    }
    if decision != expected_decision:
        errors.append(_error("$.candidate_decision", "gate12_decision_boundary_required"))

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


def validate_candidate_evidence(model: Any) -> list[str]:
    return _fail_closed(_validate_candidate_evidence_impl, model, "$candidate")


def evaluate_candidate_evidence(model: Any) -> dict[str, Any]:
    errors = validate_candidate_evidence(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [
                f"VALIDATION_ERROR:{error}" for error in errors
            ],
            "remaining_human_gates": list(PENDING_GATE_IDS),
            "data_governance": dict(EVALUATED_DATA_GOVERNANCE),
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "ready_for_gate12_decision_release_withheld",
        "reason_codes": list(REASON_CODES),
        "remaining_human_gates": list(PENDING_GATE_IDS),
        "data_governance": dict(EVALUATED_DATA_GOVERNANCE),
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        model = load_candidate_evidence(root)
        integration = _load_controlled_yaml(root / INTEGRATION_MODEL_PATH)
        receipt = _load_controlled_yaml(root / RECEIPT_MODEL_PATH)
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
        workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_candidate_evidence(model)

    receipt_source = receipt.get("source_state")
    if (
        receipt.get("status")
        != "verified_technical_evidence_pending_human_gates"
        or not isinstance(receipt_source, dict)
        or receipt_source.get("candidate_commit")
        != model.get("source_state", {}).get("technical_evidence_commit")
        or receipt_source.get("candidate_tree")
        != model.get("source_state", {}).get("technical_evidence_tree")
        or receipt.get("external_actions_performed") != []
    ):
        errors.append(
            _error("$repository.receipt", "technical_evidence_alignment_required")
        )

    integration_gates = integration.get("human_gates")
    expected_gate_states = list(zip(GATE_IDS, [True] * 11 + [False]))
    actual_gate_states = (
        [
            (gate.get("gate_id"), gate.get("authorized"))
            if isinstance(gate, dict)
            else (None, None)
            for gate in integration_gates
        ]
        if isinstance(integration_gates, list)
        else []
    )
    if actual_gate_states != expected_gate_states:
        errors.append(
            _error(
                "$repository.integration_model.human_gates",
                "candidate_gate_alignment_required",
            )
        )
    integration_claims = integration.get("claims")
    if integration_claims != {
        "risk_accepted": False,
        "pilot_authorized": False,
        "production_ready": False,
        "release_authorized": False,
    }:
        errors.append(
            _error(
                "$repository.integration_model.claims",
                "false_claims_required",
            )
        )
    if integration.get("external_actions_performed") != []:
        errors.append(
            _error(
                "$repository.integration_model.external_actions_performed",
                "must_be_empty",
            )
        )

    guide_tokens = (
        "deployment_free_candidate_ready_for_gate12_decision",
        "ready_for_gate12_decision_release_withheld",
        "synthetic_non_personal",
        "synthetic_personal_like_clearly_fictitious_non_routable",
        "Tony",
        "Stone",
        "Data Agent",
        "Developer Agent",
        "Issue #44",
        "Issue #49",
        "Gate 12",
        "external_actions_performed=[]",
        "不得解释为",
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
    forbidden_workflow_tokens = (
        "workflow_dispatch",
        "schedule:",
        "contents: write",
        "pull-requests: write",
        "persist-credentials: true",
    )
    for token in forbidden_workflow_tokens:
        if token in workflow_text:
            errors.append(
                _error("$repository.workflow", f"forbidden_token:{token}")
            )
    required_commands = (
        "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
        "python3 -m compileall Tests",
    )
    for command in required_commands:
        if command not in workflow_text:
            errors.append(
                _error("$repository.workflow", f"missing_command:{command}")
            )
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS deployment-free candidate evidence validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_candidate_evidence(load_candidate_evidence(ROOT))
    print("AIOS deployment-free candidate evidence validation PASSED")
    print(f"result={result['result']}")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
