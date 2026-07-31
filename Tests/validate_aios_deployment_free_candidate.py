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
    "proposed_awaiting_explicit_owner_approval",
    "proposed_awaiting_explicit_owner_approval",
    "proposed_awaiting_explicit_owner_approval",
    "proposed_awaiting_explicit_owner_approval",
    "proposed_awaiting_explicit_owner_approval",
    "release_withheld_by_objective",
)
PENDING_GATE_IDS = GATE_IDS[6:]
REASON_CODES = (
    "HG-PRIVACY-DATA",
    "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
    "HG-RISK-DISPOSITION",
    "HG-PILOT-SCOPE",
    "HG-PILOT-EVIDENCE",
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
    "pending_final_capture",
    "pending_final_capture",
    "baseline_only",
    "baseline_only",
    "pending_final_capture",
    "incomplete_pending_human_gates",
    "incomplete_pending_human_gate",
    "baseline_only",
    "complete",
    "pending_final_capture",
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
    "status": "proposed_awaiting_explicit_owner_approval",
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
    "external_actions_allowed": False,
    "decision_evidence": "Issue #44 proposal; explicit owner approval pending",
}
EVALUATED_DATA_GOVERNANCE = {
    "status": "proposed_awaiting_explicit_owner_approval",
    "human_approver": "Tony",
    "backup_and_escalation_contact": "Stone",
    "technical_validation_owner": "Data Agent",
    "implementation_support": "Developer Agent",
    "external_actions_allowed": False,
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
    if model["status"] != "preparation_incomplete_pending_human_gates":
        errors.append(_error("$.status", "must_remain_incomplete"))
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
        if source_state.get("pull_request") != "#41 / Draft / open / unmerged":
            errors.append(_error("$.source_state.pull_request", "invalid"))
        if source_state.get("parent_issue") != "#40 / open":
            errors.append(_error("$.source_state.parent_issue", "invalid"))
        if source_state.get("candidate_commit_state") != "pending_final_capture":
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
            expected_accepted = index < 6
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
    risk_posture = model["risk_posture"]
    expected_risk_posture = {
        "stage10": "BLOCKED / NO-GO",
        "risk_count": 10,
        "risk_state": "open_blocked_unaccepted",
        "treatment_ownership": "proposed_not_authorized",
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
        "result": "not_ready_pending_human_governance",
        "reason_codes": list(REASON_CODES),
        "remaining_human_gates": list(PENDING_GATE_IDS),
        "deployment_free_evidence_only": True,
    }
    if decision != expected_decision:
        errors.append(_error("$.candidate_decision", "incomplete_decision_required"))

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
        "result": "not_ready_pending_human_governance",
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
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
        workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_candidate_evidence(model)

    integration_gates = integration.get("human_gates")
    expected_gate_states = list(zip(GATE_IDS, [True] * 6 + [False] * 6))
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
        "preparation_incomplete_pending_human_gates",
        "not_ready_pending_human_governance",
        "synthetic_non_personal",
        "synthetic_personal_like_clearly_fictitious_non_routable",
        "Tony",
        "Stone",
        "Data Agent",
        "Developer Agent",
        "Issue #44",
        "Issue #49",
        "Gate 7–12",
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
