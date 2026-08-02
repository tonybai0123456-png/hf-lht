from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = Path(
    "Governance/AIOS-Stage15-Gate11-Synthetic-Rehearsal-Evidence-Readiness-Audit-v1.yaml"
)
PROPOSALS_PATH = Path("Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml")
GATE10_PATH = Path(
    "Governance/AIOS-Stage15-Gate10-Synthetic-Rehearsal-Scope-Readiness-Audit-v1.yaml"
)
CANDIDATE_PATH = Path("Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml")
FIXTURE_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml"
)

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
CI_RECORDS = (
    ("Validate AIOS Workflow Schema", 72, 30730693193, "success"),
    ("Validate AIOS Privacy and Data Governance", 64, 30730693183, "success"),
    ("Validate AIOS Operational Resilience", 57, 30730693190, "success"),
    ("Validate Runtime Orchestrator v1", 94, 30730693169, "success"),
    ("Validate AIOS Non-production Readiness", 23, 30730693180, "success"),
    (
        "Validate AIOS Architecture and Security Foundations",
        73,
        30730693191,
        "success",
    ),
    ("Validate AIOS Project Governance", 85, 30730693174, "success"),
    ("Validate AIOS Support Controlled Pilot", 40, 30730693184, "success"),
    (
        "Validate AIOS Production Readiness Assessment",
        81,
        30730693182,
        "success",
    ),
)
FALSE_CLAIMS = {
    "gate11_accepted": False,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "risk_accepted": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
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


def load_gate11_audit(root: Path = ROOT) -> dict[str, Any]:
    return _load_controlled_yaml(root.resolve() / AUDIT_PATH)


def _validate_gate11_audit_impl(model: Any) -> list[str]:
    keys = (
        "audit_version",
        "stage",
        "stage_id",
        "status",
        "next_gate",
        "source_evidence",
        "gate11_decision_boundary",
        "scope_reconciliation",
        "synthetic_evidence_results",
        "risk_evidence_reconciliation",
        "synthetic_support_case_closure",
        "metric_and_guardrail_reconciliation",
        "withheld_authorities",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, keys, "$")
    if errors:
        return errors
    if model["audit_version"] != (
        "stage15_gate11_synthetic_rehearsal_evidence_readiness/v1"
    ):
        errors.append(_error("$.audit_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["status"] != "ready_for_stone_human_evidence_decision_not_approved":
        errors.append(_error("$.status", "human_approval_must_remain_pending"))
    if model["next_gate"] != "HG-PILOT-EVIDENCE":
        errors.append(_error("$.next_gate", "gate11_required"))

    expected_source = {
        "source_commit": "d757768e3a06d5443cafec1934011711cb039766",
        "source_tree": "9fe8f4b199ca0c4c4d888e3fa7d910504e53eeef",
        "pull_request": "#41 / Draft / open / unmerged",
        "changed_paths": 39,
        "commits": 36,
        "local_verification": {
            "tests_passed": 152,
            "tests_total": 152,
            "validators_passed": 13,
            "validators_total": 13,
            "compilation": "passed",
            "diff_check": "passed",
        },
        "exact_head_ci": [
            {
                "workflow": workflow,
                "run_number": run_number,
                "run_id": run_id,
                "conclusion": conclusion,
            }
            for workflow, run_number, run_id, conclusion in CI_RECORDS
        ],
    }
    if model["source_evidence"] != expected_source:
        errors.append(_error("$.source_evidence", "exact_source_evidence_required"))

    expected_boundary = {
        "human_approver": "Stone",
        "backup_and_escalation_contact": "Tony",
        "technical_owner": "Data Agent",
        "contributors": ["Developer Agent", "CustomerService Agent"],
        "gate_accepted": False,
        "approval_state": "awaiting_explicit_stone_human_evidence_approval",
        "scope_type": "synthetic_rehearsal_evidence_only",
        "evidence_type": "synthetic_rehearsal_only",
        "authority_ceiling": "needs_human_governance",
        "external_actions_allowed": False,
    }
    if model["gate11_decision_boundary"] != expected_boundary:
        errors.append(_error("$.gate11_decision_boundary", "exact_pending_boundary_required"))

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

    evidence = model["synthetic_evidence_results"]
    expected_evidence = [
        {"evidence_id": evidence_id, "result": "verified_synthetic"}
        for evidence_id in EVIDENCE_IDS
    ]
    if evidence != expected_evidence:
        errors.append(_error("$.synthetic_evidence_results", "ordered_evidence_required"))

    risks = model["risk_evidence_reconciliation"]
    expected_risks = [
        {
            "risk_id": risk_id,
            "state": "open_blocked_unaccepted",
            "risk_accepted": False,
        }
        for risk_id in RISK_IDS
    ]
    if risks != expected_risks:
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

    if model["metric_and_guardrail_reconciliation"] != {
        "deterministic_results": True,
        "stop_and_withdrawal_checks_passed": True,
        "evidence_identifiers_complete_and_ordered": True,
        "support_closure_is_synthetic_only": True,
        "external_delivery_performed": False,
    }:
        errors.append(_error("$.metric_and_guardrail_reconciliation", "exact_guardrails_required"))

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
    if model["claims"] != FALSE_CLAIMS or not all(
        type(value) is bool for value in model["claims"].values()
    ):
        errors.append(_error("$.claims", "exact_false_claims_required"))
    if model["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return list(dict.fromkeys(errors))


def validate_gate11_audit(model: Any) -> list[str]:
    return _fail_closed(_validate_gate11_audit_impl, model, "$gate11")


def evaluate_gate11_readiness(model: Any) -> dict[str, Any]:
    errors = validate_gate11_audit(model)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "next_gate": "HG-PILOT-EVIDENCE",
            "gate11_accepted": False,
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "ready_for_stone_human_evidence_decision_not_approved",
        "reason_codes": ["STONE_EXPLICIT_HUMAN_EVIDENCE_APPROVAL_REQUIRED"],
        "next_gate": "HG-PILOT-EVIDENCE",
        "gate11_accepted": False,
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        audit = load_gate11_audit(root)
        proposals = _load_controlled_yaml(root / PROPOSALS_PATH)
        gate10 = _load_controlled_yaml(root / GATE10_PATH)
        candidate = _load_controlled_yaml(root / CANDIDATE_PATH)
        fixture = _load_controlled_yaml(root / FIXTURE_PATH)
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    errors = validate_gate11_audit(audit)

    proposal_records = proposals.get("proposals")
    gate11 = proposal_records[4] if isinstance(proposal_records, list) and len(proposal_records) == 5 else None
    if (
        proposals.get("status") != "gates7_through_10_accepted_gate11_pending"
        or proposals.get("sequencing", {}).get("next_gate") != "HG-PILOT-EVIDENCE"
        or not isinstance(gate11, dict)
        or gate11.get("gate_id") != "HG-PILOT-EVIDENCE"
        or gate11.get("accepted") is not False
        or gate11.get("human_approver") != "Stone"
        or gate11.get("scope_type") != "synthetic_rehearsal_evidence_only"
        or gate11.get("external_actions_allowed") is not False
    ):
        errors.append(_error("$repository.proposals", "gate11_pending_alignment_required"))

    if (
        gate10.get("status")
        != "accepted_zero_participant_synthetic_rehearsal_scope_no_real_pilot"
        or gate10.get("next_gate") != "HG-PILOT-EVIDENCE"
        or gate10.get("claims", {}).get("gate10_accepted") is not True
        or gate10.get("claims", {}).get("pilot_authorized") is not False
    ):
        errors.append(_error("$repository.gate10", "accepted_prerequisite_required"))

    ledger = candidate.get("gate_ledger")
    if (
        not isinstance(ledger, list)
        or len(ledger) != 12
        or ledger[9].get("accepted") is not True
        or ledger[10].get("accepted") is not False
        or candidate.get("candidate_decision", {}).get("remaining_human_gates")
        != ["HG-PILOT-EVIDENCE", "HG-RELEASE"]
        or candidate.get("external_actions_performed") != []
    ):
        errors.append(_error("$repository.candidate", "gate11_pending_alignment_required"))

    if (
        fixture.get("required_human_gates")
        != ["HG-PILOT-EVIDENCE", "HG-RELEASE"]
        or fixture.get("support_handoff", {}).get("case_id")
        != "SYNTHETIC-CASE-001"
        or fixture.get("support_handoff", {}).get("ticket_created") is not False
        or fixture.get("requested_external_actions") != []
    ):
        errors.append(_error("$repository.fixture", "synthetic_fixture_alignment_required"))
    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Stage 15 Gate 11 synthetic-evidence readiness validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_gate11_readiness(load_gate11_audit(ROOT))
    print("AIOS Stage 15 Gate 11 synthetic-evidence readiness validation PASSED")
    print(f"result={result['result']}")
    print("next_gate=HG-PILOT-EVIDENCE")
    print("gate11_accepted=false")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
