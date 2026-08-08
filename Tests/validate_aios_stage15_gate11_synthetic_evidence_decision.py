from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = Path(
    "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Decision-v1.yaml"
)
READINESS_PATH = Path(
    "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Readiness-Audit-v1.yaml"
)
GATE10_PATH = Path(
    "Governance/AIOS-Stage15-Gate10-Synthetic-Rehearsal-Scope-Readiness-Audit-v1.yaml"
)
STAGE_REGISTRY_PATH = Path("Governance/AIOS-Stage-Registry.md")
PROJECT_REGISTRY_PATH = Path("Governance/AIOS-Project-Registry.md")

EVIDENCE_IDS = (
    "EV-ENVIRONMENT",
    "EV-IDENTITY",
    "EV-DATA",
    "EV-EVIDENCE",
    "EV-OBSERVATION",
    "EV-RECOVERY",
    "EV-INCIDENT",
    "EV-SUPPORT",
)
RISK_IDS = tuple(f"PR-RISK-{number:03d}" for number in range(1, 11))
CLAIMS = {
    "gate11_accepted": True,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "risk_accepted": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
}
DENIED_CLAIMS = dict(CLAIMS, gate11_accepted=False)


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
                raise ValueError(f"{path}: anchors and aliases are not allowed")
            if isinstance(token, ScalarToken) and token.value == "<<":
                raise ValueError(f"{path}: merge keys are not allowed")
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: controlled YAML must be a mapping")
    return loaded


def load_gate11_decision(root: Path = ROOT) -> dict[str, Any]:
    return _load_controlled_yaml(root.resolve() / DECISION_PATH)


def _validate_gate11_decision_impl(model: Any) -> list[str]:
    keys = (
        "decision_version",
        "stage",
        "stage_id",
        "status",
        "next_gate",
        "approved_evidence_package",
        "approval_record",
        "gate11_decision_boundary",
        "scope_reconciliation",
        "synthetic_evidence_results",
        "risk_evidence_reconciliation",
        "synthetic_support_case_closure",
        "withheld_authorities",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, keys, "$")
    if errors:
        return errors
    if model["decision_version"] != (
        "stage15_gate11_synthetic_rehearsal_evidence_decision/v1"
    ):
        errors.append(_error("$.decision_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["status"] != (
        "accepted_synthetic_rehearsal_evidence_only_no_release_authority"
    ):
        errors.append(_error("$.status", "exact_accepted_scope_required"))
    if model["next_gate"] != "HG-RELEASE":
        errors.append(_error("$.next_gate", "release_gate_required"))

    if model["approved_evidence_package"] != {
        "commit": "247ffe84f49517fbf74b4e2878f30ad594540cb0",
        "tree": "19ef0e6d7d51e020c264f70e3c261373cbe115e5",
        "readiness_asset": (
            "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-"
            "Evidence-Readiness-Audit-v1.yaml"
        ),
        "source_evidence_commit": "d757768e3a06d5443cafec1934011711cb039766",
        "source_evidence_tree": "9fe8f4b199ca0c4c4d888e3fa7d910504e53eeef",
        "tests_passed": 155,
        "tests_total": 155,
        "validators_passed": 14,
        "validators_total": 14,
        "exact_head_ci_passed": 9,
        "exact_head_ci_total": 9,
        "pull_request": "#41 / Draft / open / unmerged",
    }:
        errors.append(_error("$.approved_evidence_package", "exact_package_required"))

    if model["approval_record"] != {
        "decision_date": "2026-08-02",
        "decision_evidence": (
            "Owner authorization / Issue #48 / BUW AIOS Official Governance Thread"
        ),
        "accepted_scope": "synthetic_rehearsal_evidence_only",
        "exact_commit_required": True,
        "authority_expansion": False,
    }:
        errors.append(_error("$.approval_record", "exact_decision_required"))

    if model["gate11_decision_boundary"] != {
        "human_approver": "Stone",
        "backup_and_escalation_contact": "Tony",
        "technical_owner": "Data Agent",
        "contributors": ["Developer Agent", "CustomerService Agent"],
        "gate_accepted": True,
        "approval_state": "accepted",
        "scope_type": "synthetic_rehearsal_evidence_only",
        "evidence_type": "synthetic_rehearsal_only",
        "authority_ceiling": "needs_human_governance",
        "release_authorized": False,
        "external_actions_allowed": False,
    }:
        errors.append(_error("$.gate11_decision_boundary", "exact_boundary_required"))

    if model["scope_reconciliation"] != {
        "company": "汇沣电商",
        "brand": "BUW",
        "excluded_entities": ["PC", "六合通"],
        "gate10_scope": "synthetic_rehearsal_only_no_real_pilot",
        "real_participant_count": 0,
        "production_or_staging_environment_count": 0,
        "real_case_order_account_or_message_count": 0,
    }:
        errors.append(_error("$.scope_reconciliation", "synthetic_scope_required"))

    if model["synthetic_evidence_results"] != [
        {"evidence_id": evidence_id, "result": "verified_synthetic"}
        for evidence_id in EVIDENCE_IDS
    ]:
        errors.append(_error("$.synthetic_evidence_results", "ordered_evidence_required"))
    if model["risk_evidence_reconciliation"] != [
        {
            "risk_id": risk_id,
            "state": "open_blocked_unaccepted",
            "risk_accepted": False,
        }
        for risk_id in RISK_IDS
    ]:
        errors.append(_error("$.risk_evidence_reconciliation", "unaccepted_risks_required"))
    if model["synthetic_support_case_closure"] != {
        "case_id": "SYNTHETIC-CASE-001",
        "record_type": "synthetic_role_simulation_no_real_participant",
        "synthetic_actor_id": "SYNTHETIC-HUMAN-ROLE-CS-001",
        "actor_is_real_person": False,
        "case_disposition": "stopped_withdrawn_and_closed",
        "ticket_created": False,
        "external_message_sent": False,
        "human_closure_record_complete": True,
    }:
        errors.append(_error("$.synthetic_support_case_closure", "synthetic_closure_required"))

    if model["withheld_authorities"] != [
        "real_pilot",
        "real_participants",
        "real_data",
        "credentials_and_permissions",
        "connectors",
        "external_infrastructure_and_accounts",
        "risk_acceptance",
        "merge",
        "publication",
        "archive",
        "release",
        "deployment",
    ]:
        errors.append(_error("$.withheld_authorities", "exact_withholding_required"))
    if model["claims"] != CLAIMS or not all(
        type(value) is bool for value in model["claims"].values()
    ):
        errors.append(_error("$.claims", "exact_claims_required"))
    if model["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_gate11_decision(model: Any) -> list[str]:
    return _fail_closed(_validate_gate11_decision_impl, model, "$gate11_decision")


def evaluate_gate11_decision(model: Any) -> dict[str, Any]:
    errors = validate_gate11_decision(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "next_gate": "HG-PILOT-EVIDENCE",
            "gate11_accepted": False,
            "release_authorized": False,
            "claims": dict(DENIED_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "accepted_synthetic_rehearsal_evidence_only_no_release_authority",
        "reason_codes": ["EXACT_GATE11_PACKAGE_ACCEPTED", "HG_RELEASE_STILL_REQUIRED"],
        "next_gate": "HG-RELEASE",
        "gate11_accepted": True,
        "release_authorized": False,
        "claims": dict(CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        decision = load_gate11_decision(root)
        readiness = _load_controlled_yaml(root.resolve() / READINESS_PATH)
        gate10 = _load_controlled_yaml(root.resolve() / GATE10_PATH)
        registries = [
            (root.resolve() / STAGE_REGISTRY_PATH).read_text(encoding="utf-8"),
            (root.resolve() / PROJECT_REGISTRY_PATH).read_text(encoding="utf-8"),
        ]
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_gate11_decision(decision)
    if (
        readiness.get("status")
        != "ready_for_stone_human_evidence_decision_not_approved"
        or readiness.get("claims", {}).get("gate11_accepted") is not False
        or readiness.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.readiness", "immutable_readiness_snapshot_required"))
    if (
        gate10.get("status")
        != "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot"
        or gate10.get("claims", {}).get("gate10_accepted") is not True
        or gate10.get("claims", {}).get("pilot_authorized") is not False
    ):
        errors.append(_error("$repository.gate10", "accepted_prerequisite_required"))
    tokens = (
        "Gate 11 accepted",
        "AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Decision-v1.yaml",
        "247ffe84f49517fbf74b4e2878f30ad594540cb0",
        "gates7_through_11_accepted_release_gate_withheld",
        "Gate 12 is the only valid next governance decision",
        "Gate 12 remains expressly withheld",
    )
    for index, registry in enumerate(registries):
        for token in tokens:
            if token not in registry:
                errors.append(_error(f"$repository.registries[{index}]", f"missing:{token}"))
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 Gate 11 synthetic-evidence decision validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_gate11_decision(load_gate11_decision(ROOT))
    print("AIOS Stage 15 Gate 11 synthetic-evidence decision validation PASSED")
    print(f"result={result['result']}")
    print("gate11_accepted=true")
    print("next_gate=HG-RELEASE")
    print("release_authorized=false")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
