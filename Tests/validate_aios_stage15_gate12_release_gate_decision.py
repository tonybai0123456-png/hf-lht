from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Stage15-Gate12-Release-Gate-Decision-v1.yaml")
PACKET_PATH = Path("Governance/AIOS-Stage15-Gate12-Deployment-Free-Decision-Packet-v1.yaml")
GUIDE_PATH = Path("Tests/AIOS-Stage15-Gate12-Release-Gate-Decision-Validation.md")
REGISTRY_PATHS = (
    Path("Governance/AIOS-Stage-Registry.md"),
    Path("Governance/AIOS-Project-Registry.md"),
)

CANDIDATE_COMMIT = "9bc17fa2ef722f29a8fcf302ef275ef6fbdf3a49"
CANDIDATE_TREE = "bf82c13df03e86985d6c9bc190eea9cd2fc87830"
GOVERNANCE_RECORD_COMMIT = "68b6301bcd08316aa191ac5e1e8f69bce44ab7aa"
GOVERNANCE_RECORD_TREE = "fa5397b5fabf1eae6ddb8034da9b1d0f076f1bee"
RISK_IDS = tuple(f"PR-RISK-{index:03d}" for index in range(1, 11))

EXPECTED_BOUNDARY = {
    "gate_accepted": True,
    "governance_gate_only": True,
    "approval_state": "accepted",
    "mark_ready_for_review_authorized": False,
    "merge_authorized": False,
    "formal_publication_authorized": False,
    "archive_authorized": False,
    "issue_closure_authorized": False,
    "risk_acceptance_authorized": False,
    "risk_closure_authorized": False,
    "real_pilot_authorized": False,
    "real_participants_authorized": False,
    "real_data_authorized": False,
    "credentials_authorized": False,
    "permissions_authorized": False,
    "connectors_authorized": False,
    "infrastructure_authorized": False,
    "production_operations_authorized": False,
    "release_action_authorized": False,
    "deployment_authorized": False,
    "external_actions_allowed": False,
}

EXPECTED_CLAIMS = {
    "gate12_accepted": True,
    "ready_for_review_authorized": False,
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


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _fail_closed(validator: Callable[[Any], list[str]], value: Any) -> list[str]:
    try:
        copied = copy.deepcopy(value)
        errors = validator(copied)
        if not isinstance(errors, list) or not all(isinstance(item, str) for item in errors):
            return [_error("$", "validator_contract_error")]
        return errors
    except Exception as exc:
        return [_error("$", f"validation_exception:{type(exc).__name__}")]


def _load_yaml(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError("symlink is not allowed")
    text = path.read_text(encoding="utf-8")
    for token in yaml.scan(text):
        if isinstance(token, (AnchorToken, AliasToken)):
            raise ValueError("anchors and aliases are not allowed")
        if isinstance(token, ScalarToken) and token.value == "<<":
            raise ValueError("merge keys are not allowed")
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError("mapping required")
    return loaded


def load_gate12_decision(root: Path = ROOT) -> dict[str, Any]:
    return _load_yaml(root / MODEL_PATH)


def _validate_gate12_decision_impl(model: Any) -> list[str]:
    if not isinstance(model, dict):
        return [_error("$", "mapping_required")]
    errors: list[str] = []
    if model.get("decision_version") != "stage15_gate12_hg_release_decision/v1":
        errors.append(_error("$.decision_version", "invalid"))
    if model.get("stage") != "15" or model.get("stage_id") != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model.get("status") != "accepted_governance_gate_only_release_actions_withheld":
        errors.append(_error("$.status", "governance_gate_only_required"))

    material = model.get("approved_decision_material")
    expected_material = {
        "candidate_commit": CANDIDATE_COMMIT,
        "candidate_tree": CANDIDATE_TREE,
        "governance_record_commit": GOVERNANCE_RECORD_COMMIT,
        "governance_record_tree": GOVERNANCE_RECORD_TREE,
        "decision_packet": str(PACKET_PATH),
        "pull_request": "#41 / Draft / open / unmerged",
    }
    if material != expected_material:
        errors.append(_error("$.approved_decision_material", "exact_material_required"))

    approval = model.get("approval_record")
    if not isinstance(approval, dict):
        errors.append(_error("$.approval_record", "mapping_required"))
    else:
        expected_approval = {
            "decision_date": "2026-08-02",
            "decision_evidence": "Owner authorization / Issue #49 / BUW AIOS Official Governance Thread",
            "accepted_gate": "HG-RELEASE",
            "accepted_scope": "gate12_governance_gate_only",
            "exact_material_required": True,
            "authority_expansion": False,
        }
        if approval != expected_approval:
            errors.append(_error("$.approval_record", "exact_approval_required"))

    if model.get("gate12_decision_boundary") != EXPECTED_BOUNDARY:
        errors.append(_error("$.gate12_decision_boundary", "withheld_actions_required"))
    if model.get("scope_reconciliation") != {
        "company": "汇沣电商",
        "brand": "BUW",
        "excluded_entities": ["PC", "六合通"],
        "evidence_scope": "synthetic_and_isolated_nonproduction_only",
        "stage10": "BLOCKED / NO-GO",
    }:
        errors.append(_error("$.scope_reconciliation", "exact_scope_required"))

    repository = model.get("repository_state")
    if repository != {
        "pull_request": {"number": 41, "state": "open", "draft": True, "merged": False},
        "open_issues": [40, 44, 45, 46, 47, 48, 49],
        "closed_issues": [],
    }:
        errors.append(_error("$.repository_state", "draft_open_state_required"))

    risks = model.get("risk_reconciliation")
    if not isinstance(risks, list) or len(risks) != 10:
        errors.append(_error("$.risk_reconciliation", "ten_risks_required"))
    else:
        if tuple(item.get("risk_id") for item in risks if isinstance(item, dict)) != RISK_IDS:
            errors.append(_error("$.risk_reconciliation", "ordered_risk_ids_required"))
        for index, item in enumerate(risks):
            if not isinstance(item, dict) or item != {
                "risk_id": RISK_IDS[index],
                "state": "open_blocked_unaccepted",
                "risk_accepted": False,
                "risk_closed": False,
            }:
                errors.append(_error(f"$.risk_reconciliation[{index}]", "open_unaccepted_required"))

    next_auth = model.get("next_required_authorization")
    expected_actions = [
        "mark_ready_for_review",
        "merge",
        "formal_publication",
        "archive",
        "issue_closure",
        "risk_acceptance_or_closure",
        "real_pilot",
        "real_data_or_credentials",
        "permissions_connectors_or_infrastructure",
        "production_operations",
        "release_action",
        "deployment",
    ]
    if next_auth != {
        "state": "separate_explicit_authorization_required",
        "actions": expected_actions,
    }:
        errors.append(_error("$.next_required_authorization", "separate_authority_required"))
    if model.get("claims") != EXPECTED_CLAIMS:
        errors.append(_error("$.claims", "exact_claims_required"))
    if model.get("external_actions_performed") != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return errors


def validate_gate12_decision(model: Any) -> list[str]:
    return _fail_closed(_validate_gate12_decision_impl, model)


def evaluate_gate12_decision(model: Any) -> dict[str, Any]:
    errors = validate_gate12_decision(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": errors,
            "gate12_accepted": False,
            "release_action_authorized": False,
            "deployment_authorized": False,
            "external_actions_performed": [],
        }
    return {
        "result": "accepted_governance_gate_only_release_actions_withheld",
        "reason_codes": [],
        "gate12_accepted": True,
        "release_action_authorized": False,
        "deployment_authorized": False,
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        model = load_gate12_decision(root)
    except Exception as exc:
        return [_error(str(MODEL_PATH), f"load_failed:{type(exc).__name__}")]
    errors.extend(validate_gate12_decision(model))

    for required in (root / PACKET_PATH, root / GUIDE_PATH):
        if not required.is_file() or required.is_symlink():
            errors.append(_error(str(required.relative_to(root)), "regular_file_required"))

    if (root / PACKET_PATH).is_file():
        try:
            packet = _load_yaml(root / PACKET_PATH)
            source = packet.get("candidate_source", {})
            if (
                source.get("candidate_commit") != CANDIDATE_COMMIT
                or source.get("candidate_tree") != CANDIDATE_TREE
            ):
                errors.append(_error(str(PACKET_PATH), "approved_candidate_mismatch"))
        except Exception as exc:
            errors.append(_error(str(PACKET_PATH), f"load_failed:{type(exc).__name__}"))

    registry_tokens = (
        "Gate 12 accepted",
        str(MODEL_PATH),
        "accepted_governance_gate_only_release_actions_withheld",
        CANDIDATE_COMMIT,
        GOVERNANCE_RECORD_COMMIT,
        "PR #41 remains Draft/open/unmerged",
        "all ten risks remain open, blocked and unaccepted",
        "separate explicit authorization",
    )
    for relative in REGISTRY_PATHS:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            errors.append(_error(str(relative), "regular_file_required"))
            continue
        text = path.read_text(encoding="utf-8")
        try:
            current = (
                text.split("## Current Stage 15 decision overlay", 1)[1]
                .split("## Pre-freeze exception record", 1)[0]
                .split("## Registry rules", 1)[0]
            )
        except IndexError:
            errors.append(_error(str(relative), "current_overlay_required"))
            continue
        for token in registry_tokens:
            if token not in current:
                errors.append(_error(str(relative), f"missing_current_token:{token}"))
    return errors


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 Gate 12 decision validation FAILED")
        for error in errors:
            print(error)
        return 1
    result = evaluate_gate12_decision(load_gate12_decision(ROOT))
    print("AIOS Stage 15 Gate 12 decision validation PASSED")
    print(f"result={result['result']}")
    print("gate12_accepted=true")
    print("release_action_authorized=false")
    print("deployment_authorized=false")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
