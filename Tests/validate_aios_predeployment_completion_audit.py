from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Predeployment-Completion-Audit-v1.yaml")
GUIDE_PATH = Path("Tests/AIOS-Predeployment-Completion-Audit-Validation.md")
CANDIDATE_PATH = Path(
    "Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml"
)
PROPOSALS_PATH = Path("Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml")
INTEGRATION_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
)
WORKFLOW_PATH = Path(
    ".github/workflows/validate-aios-support-controlled-pilot.yml"
)

REQUIREMENT_STATES = (
    "proven_complete",
    "proven_complete",
    "proven_complete",
    "pending_human_governance",
    "pending_human_governance",
    "pending_human_governance",
    "pending_human_governance",
    "pending_human_governance",
    "partial_pending_human_gates",
    "intentionally_withheld",
    "intentionally_excluded",
    "intentionally_excluded_or_withheld",
)
QUEUE_GATES = (
    "HG-PRIVACY-DATA",
    "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
    "HG-RISK-DISPOSITION",
    "HG-PILOT-SCOPE",
    "HG-PILOT-EVIDENCE",
)
QUEUE_ISSUES = ("#44", "#45", "#46", "#47", "#48")
QUEUE_STATES = (
    "proposed_awaiting_explicit_owner_approval",
    "blocked_by_prior_human_gate",
    "blocked_by_prior_human_gate",
    "blocked_by_prior_human_gate",
    "blocked_by_prior_human_gate",
)
QUEUE_APPROVERS = ("Tony", "Stone", "Tony", "Tony", "Stone")
QUEUE_TECHNICAL_OWNERS = (
    "Data Agent",
    "Developer Agent",
    "risk_treatment_evidence_by_mapped_agents",
    "Developer Agent",
    "Data Agent",
)
QUEUE_PREREQUISITES = (
    "HG-ARCH-SECURITY",
    "HG-PRIVACY-DATA",
    "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
    "HG-RISK-DISPOSITION",
    "HG-PILOT-SCOPE",
)
EVIDENCE_STATES = (
    "verified_external_capture",
    "verified",
    "verified",
    "verified",
    "verified",
    "incomplete_pending_human_gates",
    "verified_unapproved_treatment_mapping",
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


def load_completion_audit(root: Path = ROOT) -> dict[str, Any]:
    resolved_root = root.resolve()
    path = resolved_root / MODEL_PATH
    if path.resolve().parent != (resolved_root / "Governance").resolve():
        raise ValueError("completion audit path escapes repository")
    return _load_controlled_yaml(path)


def _validate_completion_audit_impl(model: Any) -> list[str]:
    keys = (
        "audit_version",
        "stage",
        "stage_id",
        "status",
        "allowed_scope",
        "excluded_entities",
        "audited_source_state",
        "requirement_ledger",
        "issue49_evidence_snapshot",
        "human_decision_queue",
        "completion_decision",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, keys, "$")
    if errors:
        return errors

    if model["audit_version"] != "predeployment_completion_audit/v1":
        errors.append(_error("$.audit_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["status"] != "incomplete_pending_ordered_human_governance":
        errors.append(_error("$.status", "must_remain_incomplete"))
    if model["allowed_scope"] != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.allowed_scope", "invalid"))
    if model["excluded_entities"] != ["PC", "六合通"]:
        errors.append(_error("$.excluded_entities", "invalid"))

    source = model["audited_source_state"]
    source_keys = (
        "baseline_commit",
        "baseline_tree",
        "reviewed_implementation_commit",
        "technical_receipt_source_commit",
        "technical_receipt_source_tree",
        "technical_receipt",
        "pull_request",
        "parent_issue",
        "release_boundary_issue",
        "audit_record_commit_state",
    )
    errors.extend(_exact_keys(source, source_keys, "$.audited_source_state"))
    expected_source = {
        "baseline_commit": "00ee3706f117df99cc89b64339659b4b497d7705",
        "baseline_tree": "58734f98a922cd8b15436312ff21911117052038",
        "reviewed_implementation_commit": (
            "b27614ba2ebebb772888c3a4b1ff3d829b47532e"
        ),
        "technical_receipt_source_commit": (
            "36716abc76373d053c75e68352f46589f4ddc8f1"
        ),
        "technical_receipt_source_tree": (
            "ec48f7c537162b32f6bc35947d9e49758e1b53bd"
        ),
        "technical_receipt": (
            "Governance/AIOS-Deployment-Free-Candidate-Receipt-v1.yaml"
        ),
        "pull_request": "#41 / Draft / open / unmerged",
        "parent_issue": "#40 / open",
        "release_boundary_issue": "#49 / open",
        "audit_record_commit_state": "external_capture_after_push",
    }
    if source != expected_source:
        errors.append(_error("$.audited_source_state", "exact_baseline_required"))

    ledger = model["requirement_ledger"]
    if not isinstance(ledger, list) or len(ledger) != 12:
        errors.append(_error("$.requirement_ledger", "exact_length_required"))
    else:
        for index, (record, expected_state) in enumerate(
            zip(ledger, REQUIREMENT_STATES), start=1
        ):
            path = f"$.requirement_ledger[{index - 1}]"
            errors.extend(
                _exact_keys(
                    record,
                    ("requirement_id", "requirement", "state", "evidence"),
                    path,
                )
            )
            if not isinstance(record, dict):
                continue
            if record.get("requirement_id") != f"PREDEP-{index:02d}":
                errors.append(_error(path, "ordered_requirement_id_required"))
            if (
                not isinstance(record.get("requirement"), str)
                or not record.get("requirement")
                or record.get("state") != expected_state
                or not isinstance(record.get("evidence"), list)
                or len(record.get("evidence")) < 2
                or not all(
                    isinstance(item, str) and item
                    for item in record.get("evidence", [])
                )
            ):
                errors.append(_error(path, "truthful_requirement_record_required"))

    snapshot = model["issue49_evidence_snapshot"]
    if not isinstance(snapshot, list) or len(snapshot) != 12:
        errors.append(
            _error("$.issue49_evidence_snapshot", "exact_length_required")
        )
    else:
        for index, (record, state) in enumerate(
            zip(snapshot, EVIDENCE_STATES), start=1
        ):
            if record != {"evidence_id": f"DFC-EV-{index:02d}", "state": state}:
                errors.append(
                    _error(
                        f"$.issue49_evidence_snapshot[{index - 1}]",
                        "truthful_snapshot_required",
                    )
                )

    queue = model["human_decision_queue"]
    if not isinstance(queue, list) or len(queue) != len(QUEUE_GATES):
        errors.append(_error("$.human_decision_queue", "exact_length_required"))
    else:
        expected = zip(
            QUEUE_GATES,
            QUEUE_ISSUES,
            QUEUE_STATES,
            QUEUE_APPROVERS,
            QUEUE_TECHNICAL_OWNERS,
            QUEUE_PREREQUISITES,
        )
        for index, (record, values) in enumerate(zip(queue, expected)):
            path = f"$.human_decision_queue[{index}]"
            errors.extend(
                _exact_keys(
                    record,
                    (
                        "gate_id",
                        "issue",
                        "accepted",
                        "state",
                        "human_approver",
                        "technical_owner",
                        "prerequisite",
                    ),
                    path,
                )
            )
            if not isinstance(record, dict):
                continue
            actual = (
                record.get("gate_id"),
                record.get("issue"),
                record.get("state"),
                record.get("human_approver"),
                record.get("technical_owner"),
                record.get("prerequisite"),
            )
            if actual != values or record.get("accepted") is not False:
                errors.append(_error(path, "unapproved_ordered_gate_required"))

    expected_decision = {
        "result": "not_complete_pending_human_governance",
        "remaining_requirements": list(QUEUE_GATES),
        "stage10": "BLOCKED / NO-GO",
        "release_gate_authorized": False,
        "deployment_free_evidence_only": True,
    }
    if model["completion_decision"] != expected_decision:
        errors.append(
            _error("$.completion_decision", "incomplete_decision_required")
        )
    if (
        not isinstance(model["claims"], dict)
        or model["claims"] != FALSE_CLAIMS
        or not all(type(value) is bool for value in model["claims"].values())
    ):
        errors.append(_error("$.claims", "exact_false_claims_required"))
    if model["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_completion_audit(model: Any) -> list[str]:
    return _fail_closed(_validate_completion_audit_impl, model, "$audit")


def evaluate_completion_audit(model: Any) -> dict[str, Any]:
    errors = validate_completion_audit(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "not_complete_pending_human_governance",
        "reason_codes": [*QUEUE_GATES, "FINAL-EXACT-HEAD-CAPTURE"],
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        model = load_completion_audit(root)
        candidate = _load_controlled_yaml(root / CANDIDATE_PATH)
        proposals = _load_controlled_yaml(root / PROPOSALS_PATH)
        integration = _load_controlled_yaml(root / INTEGRATION_PATH)
        guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
        workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
        workflow = yaml.safe_load(workflow_text)
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]

    errors = validate_completion_audit(model)
    candidate_gates = candidate.get("gate_ledger")
    candidate_gate_truth = (
        [gate.get("accepted") for gate in candidate_gates]
        if isinstance(candidate_gates, list)
        and all(isinstance(gate, dict) for gate in candidate_gates)
        else []
    )
    if (
        candidate.get("status")
        != "technical_evidence_verified_pending_human_gates"
        or candidate_gate_truth != [True] * 6 + [False] * 6
        or candidate.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.candidate", "alignment_required"))

    proposal_records = proposals.get("proposals")
    proposal_truth = (
        [
            (record.get("gate_id"), record.get("accepted"))
            for record in proposal_records
        ]
        if isinstance(proposal_records, list)
        and all(isinstance(record, dict) for record in proposal_records)
        else []
    )
    if (
        proposals.get("status")
        != "prepared_unapproved_ordered_human_gate_proposals"
        or proposals.get("sequencing", {}).get("next_gate") != QUEUE_GATES[0]
        or proposal_truth != list(zip(QUEUE_GATES, [False] * 5))
        or proposals.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.proposals", "alignment_required"))

    integration_gates = integration.get("human_gates")
    integration_truth = (
        [record.get("authorized") for record in integration_gates]
        if isinstance(integration_gates, list)
        and all(isinstance(record, dict) for record in integration_gates)
        else []
    )
    if (
        integration_truth != [True] * 6 + [False] * 6
        or integration.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.integration", "alignment_required"))

    guide_tokens = (
        "incomplete_pending_ordered_human_governance",
        "not_complete_pending_human_governance",
        "proven_complete",
        "pending_human_governance",
        "intentionally_withheld",
        "intentionally_excluded",
        "Gate 7–11",
        "Issue #44",
        "Issue #49",
        "Stage 10",
        "BLOCKED / NO-GO",
        "external_actions_performed=[]",
        "不得解释为",
    )
    for token in guide_tokens:
        if token not in guide:
            errors.append(_error("$repository.guide", f"missing_token:{token}"))

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
    for token in (
        "workflow_dispatch",
        "schedule:",
        "contents: write",
        "pull-requests: write",
        "persist-credentials: true",
    ):
        if token in workflow_text:
            errors.append(_error("$repository.workflow", f"forbidden_token:{token}"))
    for command in (
        "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
        "python3 -m compileall Tests",
    ):
        if command not in workflow_text:
            errors.append(_error("$repository.workflow", f"missing_command:{command}"))
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS predeployment completion audit validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_completion_audit(load_completion_audit(ROOT))
    print("AIOS predeployment completion audit validation PASSED")
    print(f"result={result['result']}")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
