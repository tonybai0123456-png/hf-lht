from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(
    "Governance/AIOS-Stage15-Gate12-Deployment-Free-Decision-Packet-v1.yaml"
)
GUIDE_PATH = Path("Tests/AIOS-Stage15-Gate12-Decision-Packet-Validation.md")
CANDIDATE_PATH = Path("Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml")
AUDIT_PATH = Path("Governance/AIOS-Predeployment-Completion-Audit-v1.yaml")

CANDIDATE_COMMIT = "9bc17fa2ef722f29a8fcf302ef275ef6fbdf3a49"
CANDIDATE_TREE = "bf82c13df03e86985d6c9bc190eea9cd2fc87830"
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
FALSE_CLAIMS = {
    "gate12_accepted": False,
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


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _fail_closed(
    validator: Callable[[Any], list[str]], value: Any, path: str
) -> list[str]:
    try:
        copied = copy.deepcopy(value)
        errors = validator(copied)
        if not isinstance(errors, list) or not all(isinstance(item, str) for item in errors):
            return [_error(path, "validator_contract_error")]
        return errors
    except Exception as exc:
        return [_error(path, f"validation_exception:{type(exc).__name__}")]


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


def load_decision_packet(root: Path = ROOT) -> dict[str, Any]:
    return _load_yaml(root / MODEL_PATH)


def _validate_packet_impl(model: Any) -> list[str]:
    if not isinstance(model, dict):
        return [_error("$", "mapping_required")]
    errors: list[str] = []
    if model.get("packet_version") != "stage15_gate12_deployment_free_decision_packet/v1":
        errors.append(_error("$.packet_version", "invalid"))
    if model.get("stage") != "15" or model.get("stage_id") != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model.get("status") != "ready_for_gate12_decision_release_withheld":
        errors.append(_error("$.status", "gate12_boundary_required"))
    if model.get("allowed_scope") != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.allowed_scope", "buw_only_required"))
    if model.get("excluded_entities") != ["PC", "六合通"]:
        errors.append(_error("$.excluded_entities", "exact_exclusion_required"))

    source = model.get("candidate_source")
    if not isinstance(source, dict):
        errors.append(_error("$.candidate_source", "mapping_required"))
    else:
        if source.get("candidate_commit") != CANDIDATE_COMMIT:
            errors.append(_error("$.candidate_source.candidate_commit", "exact_required"))
        if source.get("candidate_tree") != CANDIDATE_TREE:
            errors.append(_error("$.candidate_source.candidate_tree", "exact_required"))
        if source.get("pull_request") != "#41 / Draft / open / unmerged":
            errors.append(_error("$.candidate_source.pull_request", "draft_required"))
        if source.get("candidate_changed_paths") != 46:
            errors.append(_error("$.candidate_source.candidate_changed_paths", "exact_required"))

    manifest = model.get("changed_file_manifest")
    paths = manifest.get("paths") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("count") != 46
        or not isinstance(paths, list)
        or len(paths) != 46
        or len(set(paths)) != 46
        or paths != sorted(paths)
    ):
        errors.append(_error("$.changed_file_manifest", "exact_sorted_manifest_required"))

    verification = model.get("verification")
    if not isinstance(verification, dict):
        errors.append(_error("$.verification", "mapping_required"))
    else:
        expected = {
            "repository_tests": {"passed": 161, "total": 161},
            "controlled_validators": {"passed": 15, "total": 15},
            "python_compilation": "passed",
            "diff_check": "passed",
        }
        for key, value in expected.items():
            if verification.get(key) != value:
                errors.append(_error(f"$.verification.{key}", "exact_pass_required"))
        scans = verification.get("material_scans")
        if not isinstance(scans, dict) or set(scans.values()) != {"passed_no_material"}:
            errors.append(_error("$.verification.material_scans", "no_material_required"))

    ci = model.get("exact_head_ci")
    if (
        not isinstance(ci, list)
        or len(ci) != 9
        or len({item.get("workflow") for item in ci if isinstance(item, dict)}) != 9
        or any(not isinstance(item, dict) or item.get("conclusion") != "success" for item in ci)
    ):
        errors.append(_error("$.exact_head_ci", "nine_unique_successes_required"))

    gates = model.get("gate_ledger")
    expected_gates = [
        {"gate_id": gate_id, "accepted": index < 11}
        for index, gate_id in enumerate(GATE_IDS)
    ]
    if gates != expected_gates:
        errors.append(_error("$.gate_ledger", "gates1_through_11_only_required"))

    risks = model.get("risk_evidence_mapping")
    if (
        not isinstance(risks, list)
        or [item.get("risk_id") for item in risks if isinstance(item, dict)]
        != [f"PR-RISK-{number:03d}" for number in range(1, 11)]
    ):
        errors.append(_error("$.risk_evidence_mapping", "ordered_ten_risks_required"))
    if model.get("risk_state") != {
        "count": 10,
        "disposition": "mitigate_and_remain_open_blocked_unaccepted",
        "state": "open_blocked_unaccepted",
        "accepted": False,
        "closed": False,
    }:
        errors.append(_error("$.risk_state", "open_blocked_unaccepted_required"))

    repo = model.get("repository_state")
    if not isinstance(repo, dict) or repo.get("stage10") != "BLOCKED / NO-GO":
        errors.append(_error("$.repository_state", "blocked_no_go_required"))
    decision = model.get("gate12_decision_material")
    if (
        not isinstance(decision, dict)
        or decision.get("decision_required") != "HG-RELEASE"
        or decision.get("current_state") != "unapproved"
    ):
        errors.append(_error("$.gate12_decision_material", "unapproved_release_gate_required"))
    mandatory = model.get("mandatory_return")
    if (
        not isinstance(mandatory, dict)
        or mandatory.get("result") != "deployment_free_work_complete_gate12_decision_pending"
        or mandatory.get("external_actions_performed") != []
        or mandatory.get("gate12_pending") is not True
    ):
        errors.append(_error("$.mandatory_return", "exact_return_required"))
    if model.get("claims") != FALSE_CLAIMS:
        errors.append(_error("$.claims", "all_false_claims_required"))
    if model.get("external_actions_performed") != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_decision_packet(model: Any) -> list[str]:
    return _fail_closed(_validate_packet_impl, model, "$packet")


def evaluate_decision_packet(model: Any) -> dict[str, Any]:
    errors = validate_decision_packet(model)
    return {
        "result": "denied" if errors else "ready_for_gate12_decision_release_withheld",
        "reason_codes": [f"VALIDATION_ERROR:{item}" for item in errors]
        if errors
        else ["HG-RELEASE-WITHHELD-BY-OBJECTIVE"],
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        model = load_decision_packet(root)
        candidate = _load_yaml(root / CANDIDATE_PATH)
        audit = _load_yaml(root / AUDIT_PATH)
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_decision_packet(model)
    manifest = model.get("changed_file_manifest", {}).get("paths", [])
    if any(not (root / path).is_file() for path in manifest):
        errors.append(_error("$repository.manifest", "path_missing"))
    if candidate.get("candidate_decision", {}).get("result") != model.get("status"):
        errors.append(_error("$repository.candidate", "status_alignment_required"))
    if audit.get("completion_decision", {}).get("result") != (
        "deployment_free_work_complete_gate12_decision_pending"
    ):
        errors.append(_error("$repository.audit", "completion_alignment_required"))
    for token in (
        CANDIDATE_COMMIT,
        CANDIDATE_TREE,
        "161/161",
        "15/15",
        "9/9",
        "BLOCKED / NO-GO",
        "external_actions_performed=[]",
        "不得解释为",
    ):
        if token not in guide:
            errors.append(_error("$repository.guide", f"missing_token:{token}"))
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 Gate 12 deployment-free decision packet validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIOS Stage 15 Gate 12 deployment-free decision packet validation PASSED")
    print("result=ready_for_gate12_decision_release_withheld")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
