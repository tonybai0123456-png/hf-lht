from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Post-Gate12-Reconciliation-v1.yaml")
AUDIT_PATH = Path("Governance/AIOS-Predeployment-Completion-Audit-v1.yaml")
DECISION_PATH = Path("Governance/AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml")
REGISTRY_PATH = Path("Governance/AIOS-Stage-Registry.md")
GUIDE_PATH = Path("Tests/AIOS-Stage15-Post-Gate12-Reconciliation-Validation.md")

ACTIONS = (
    "ready_for_review",
    "merge",
    "formal_publication",
    "archive",
    "issue_closure",
    "risk_acceptance_or_closure",
    "real_pilot_or_participants",
    "real_data_or_credentials",
    "permissions_connectors_or_infrastructure",
    "production_operations",
    "release_action",
    "deployment",
)
FALSE_AUTHORITIES = {action: False for action in ACTIONS}
FALSE_CLAIMS = {
    "ready_for_review_authorized": False,
    "merge_authorized": False,
    "archive_authorized": False,
    "issue_closure_authorized": False,
    "risk_accepted": False,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_action_authorized": False,
    "deployment_authorized": False,
    "real_data_used": False,
    "connector_used": False,
    "infrastructure_provisioned": False,
    "credentials_used": False,
}
RISK_IDS = tuple(f"PR-RISK-{index:03d}" for index in range(1, 11))


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [_error(path, "mapping_required")]
    if tuple(value.keys()) != expected:
        return [_error(path, "exact_keys_required")]
    return []


def _fail_closed(
    validator: Callable[[Any], list[str]], value: Any, path: str
) -> list[str]:
    try:
        copied = copy.deepcopy(value)
        errors = validator(copied)
        if not isinstance(errors, list) or not all(isinstance(item, str) for item in errors):
            return [_error(path, "validator_contract_error")]
        return list(dict.fromkeys(errors))
    except Exception as exc:
        return [_error(path, f"validation_exception:{type(exc).__name__}")]


def _load_controlled_yaml(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"{path}: symlink is not allowed")
    text = path.read_text(encoding="utf-8")
    try:
        for token in yaml.scan(text):
            if isinstance(token, (AnchorToken, AliasToken)):
                raise ValueError(f"{path}: anchors and aliases are not allowed")
            if isinstance(token, ScalarToken) and token.value == "<<":
                raise ValueError(f"{path}: merge keys are not allowed")
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: controlled YAML must be a mapping")
    return loaded


def load_reconciliation(root: Path = ROOT) -> dict[str, Any]:
    resolved_root = root.resolve()
    path = resolved_root / MODEL_PATH
    if path.resolve().parent != (resolved_root / "Governance").resolve():
        raise ValueError("reconciliation path escapes repository")
    return _load_controlled_yaml(path)


def _validate_reconciliation_impl(model: Any) -> list[str]:
    root_keys = (
        "record_version",
        "stage",
        "stage_id",
        "status",
        "scope",
        "source_records",
        "controlled_state",
        "lifecycle_handoff_queue",
        "reconciliation",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, root_keys, "$")
    if errors:
        return errors

    if model.get("record_version") != "stage15_post_gate12_reconciliation/v1":
        errors.append(_error("$.record_version", "invalid"))
    if model.get("stage") != "15" or model.get("stage_id") != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model.get("status") != "lifecycle_handoff_ready_actions_withheld":
        errors.append(_error("$.status", "invalid"))
    if model.get("scope") != {
        "company": "汇沣电商",
        "brand": "BUW",
        "excluded_entities": ["PC", "六合通"],
    }:
        errors.append(_error("$.scope", "exact_scope_required"))

    sources = model.get("source_records")
    expected_sources = {
        "historical_predeployment_audit": {
            "path": "Governance/AIOS-Predeployment-Completion-Audit-v1.yaml",
            "recorded_status": "deployment_free_work_complete_gate12_decision_pending",
            "interpretation": "preserved_historical_snapshot_not_current_authority",
        },
        "gate12_decision": {
            "path": "Governance/AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml",
            "decision_record_commit": "d386414791daa17bc572c237acabb79551a2aad2",
            "decision_record_tree": "9aedd318620f5c05591386c19665773837d1f148",
            "recorded_status": "accepted_governance_gate_only_release_actions_withheld",
            "accepted_scope": "gate12_governance_gate_only",
        },
        "approved_candidate": {
            "commit": "9bc17fa2ef722f29a8fcf302ef275ef6fbdf3a49",
            "tree": "bf82c13df03e86985d6c9bc190eea9cd2fc87830",
            "governance_record_commit": "68b6301bcd08316aa191ac5e1e8f69bce44ab7aa",
        },
    }
    if sources != expected_sources:
        errors.append(_error("$.source_records", "exact_source_records_required"))

    state = model.get("controlled_state")
    state_keys = (
        "lifecycle_status",
        "pull_request",
        "parent_issue",
        "release_boundary_issue",
        "reconciliation_issue",
        "stage10",
        "gate12_accepted",
        "governance_gate_only",
        "risks",
        "downstream_authorities",
    )
    errors.extend(_exact_keys(state, state_keys, "$.controlled_state"))
    if isinstance(state, dict):
        expected_scalars = {
            "lifecycle_status": "Reviewed",
            "parent_issue": 40,
            "release_boundary_issue": 49,
            "reconciliation_issue": 50,
            "stage10": "BLOCKED / NO-GO",
            "gate12_accepted": True,
            "governance_gate_only": True,
        }
        for key, expected in expected_scalars.items():
            if state.get(key) != expected:
                errors.append(_error(f"$.controlled_state.{key}", "invalid"))
        if state.get("pull_request") != {
            "number": 41,
            "state": "open",
            "draft": True,
            "merged": False,
        }:
            errors.append(_error("$.controlled_state.pull_request", "draft_open_unmerged_required"))
        expected_risks = [
            {"risk_id": risk_id, "state": "open_blocked_unaccepted"}
            for risk_id in RISK_IDS
        ]
        if state.get("risks") != expected_risks:
            errors.append(_error("$.controlled_state.risks", "exact_open_risks_required"))
        authorities = state.get("downstream_authorities")
        if authorities != FALSE_AUTHORITIES or not isinstance(authorities, dict):
            errors.append(_error("$.controlled_state.downstream_authorities", "all_false_required"))
        elif not all(type(value) is bool for value in authorities.values()):
            errors.append(_error("$.controlled_state.downstream_authorities", "booleans_required"))

    expected_queue = [
        {
            "action": action,
            "authorized": False,
            "prerequisite": "separate_explicit_governance_authorization",
        }
        for action in ACTIONS
    ]
    if model.get("lifecycle_handoff_queue") != expected_queue:
        errors.append(_error("$.lifecycle_handoff_queue", "exact_ordered_queue_required"))

    if model.get("reconciliation") != {
        "historical_snapshot_preserved": True,
        "current_authority_source": "Governance/AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml",
        "current_result": "lifecycle_handoff_ready_actions_withheld",
        "next_governance_action": "separate_explicit_lifecycle_authorization_or_hold",
        "stage16_authorized": False,
    }:
        errors.append(_error("$.reconciliation", "invalid"))
    claims = model.get("claims")
    if claims != FALSE_CLAIMS or not isinstance(claims, dict):
        errors.append(_error("$.claims", "exact_false_claims_required"))
    elif not all(type(value) is bool for value in claims.values()):
        errors.append(_error("$.claims", "booleans_required"))
    if model.get("external_actions_performed") != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_reconciliation(model: Any) -> list[str]:
    return _fail_closed(_validate_reconciliation_impl, model, "$reconciliation")


def evaluate_reconciliation(model: Any) -> dict[str, Any]:
    errors = validate_reconciliation(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "lifecycle_handoff_ready_actions_withheld",
        "reason_codes": ["GATE12-GOVERNANCE-ONLY", "SEPARATE-AUTHORIZATION-REQUIRED"],
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        model = load_reconciliation(root)
        audit = _load_controlled_yaml(root / AUDIT_PATH)
        decision = _load_controlled_yaml(root / DECISION_PATH)
        registry = (root / REGISTRY_PATH).read_text(encoding="utf-8")
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]

    errors = validate_reconciliation(model)
    if (
        audit.get("status") != "deployment_free_work_complete_gate12_decision_pending"
        or audit.get("completion_decision", {}).get("result")
        != "deployment_free_work_complete_gate12_decision_pending"
        or audit.get("completion_decision", {}).get("release_gate_authorized") is not False
        or audit.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.historical_audit", "preserved_snapshot_required"))

    boundary = decision.get("gate12_decision_boundary")
    false_boundary_keys = (
        "mark_ready_for_review_authorized",
        "merge_authorized",
        "formal_publication_authorized",
        "archive_authorized",
        "issue_closure_authorized",
        "risk_acceptance_authorized",
        "risk_closure_authorized",
        "real_pilot_authorized",
        "real_participants_authorized",
        "real_data_authorized",
        "credentials_authorized",
        "permissions_authorized",
        "connectors_authorized",
        "infrastructure_authorized",
        "production_operations_authorized",
        "release_action_authorized",
        "deployment_authorized",
        "external_actions_allowed",
    )
    if (
        decision.get("status") != "accepted_governance_gate_only_release_actions_withheld"
        or not isinstance(boundary, dict)
        or boundary.get("gate_accepted") is not True
        or boundary.get("governance_gate_only") is not True
        or boundary.get("approval_state") != "accepted"
        or any(boundary.get(key) is not False for key in false_boundary_keys)
        or decision.get("repository_state", {}).get("pull_request")
        != {"number": 41, "state": "open", "draft": True, "merged": False}
        or decision.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.gate12_decision", "governance_only_boundary_required"))

    expected_decision_risks = [
        {
            "risk_id": risk_id,
            "state": "open_blocked_unaccepted",
            "risk_accepted": False,
            "risk_closed": False,
        }
        for risk_id in RISK_IDS
    ]
    if decision.get("risk_reconciliation") != expected_decision_risks:
        errors.append(_error("$repository.gate12_decision.risks", "exact_open_risks_required"))

    registry_tokens = (
        "Stage 15 is Reviewed",
        "Gate 12 is now accepted",
        "governance gate",
        "accepted_governance_gate_only_release_actions_withheld",
        "deployment_free_work_complete_gate12_governance_gate_accepted_actions_withheld",
        "PR #41 remains Draft/open/unmerged",
        "Stage 10 remains",
        "BLOCKED / NO-GO",
    )
    for token in registry_tokens:
        if token not in registry:
            errors.append(_error("$repository.stage_registry", f"missing_token:{token}"))

    guide_tokens = (
        "append-only",
        "historical snapshot",
        "Gate 12",
        "governance gate only",
        "lifecycle_handoff_ready_actions_withheld",
        "open_blocked_unaccepted",
        "BLOCKED / NO-GO",
        "external_actions_performed=[]",
    )
    for token in guide_tokens:
        if token not in guide:
            errors.append(_error("$repository.guide", f"missing_token:{token}"))
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository()
    if errors:
        print("Stage 15 post-Gate12 reconciliation: DENIED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_reconciliation(load_reconciliation())
    print(f"Stage 15 post-Gate12 reconciliation: {result['result']}")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
