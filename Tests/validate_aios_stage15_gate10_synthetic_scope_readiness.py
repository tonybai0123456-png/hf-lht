from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = Path(
    "Governance/AIOS-Stage15-Gate10-Synthetic-Rehearsal-Scope-Readiness-Audit-v1.yaml"
)
GATE9_PATH = Path(
    "Governance/AIOS-Stage15-Gate9-Risk-Treatment-Readiness-Audit-v1.yaml"
)
PROPOSALS_PATH = Path("Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml")
CANDIDATE_PATH = Path("Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml")
FIXTURE_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml"
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
RISK_IDS = tuple(f"PR-RISK-{number:03d}" for number in range(1, 11))
FALSE_CLAIMS = {
    "gate10_accepted": False,
    "real_pilot_performed": False,
    "pilot_authorized": False,
    "risk_accepted": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
}


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _fail_closed(
    validator: Callable[..., list[str]],
    *values: Any,
    path: str,
) -> list[str]:
    try:
        copied = [copy.deepcopy(value) for value in values]
        errors = validator(*copied)
        if not isinstance(errors, list) or not all(
            isinstance(error, str) for error in errors
        ):
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
                raise ValueError(f"{path}: YAML anchors and aliases are not allowed")
            if isinstance(token, ScalarToken) and token.value == "<<":
                raise ValueError(f"{path}: YAML merge keys are not allowed")
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{path}: controlled YAML must be a mapping")
    return loaded


def load_repository_assets(root: Path = ROOT) -> tuple[dict[str, Any], ...]:
    return (
        _load_controlled_yaml(root / AUDIT_PATH),
        _load_controlled_yaml(root / GATE9_PATH),
        _load_controlled_yaml(root / PROPOSALS_PATH),
        _load_controlled_yaml(root / CANDIDATE_PATH),
        _load_controlled_yaml(root / FIXTURE_PATH),
    )


def _validate_impl(
    audit: Any,
    gate9: Any,
    proposals: Any,
    candidate: Any,
    fixture: Any,
) -> list[str]:
    errors: list[str] = []
    if not all(
        isinstance(value, dict)
        for value in (audit, gate9, proposals, candidate, fixture)
    ):
        return [_error("$", "all_assets_must_be_mappings")]

    expected_audit_keys = (
        "audit_version",
        "stage",
        "stage_id",
        "status",
        "next_gate",
        "source_assets",
        "prerequisites",
        "gate10_decision_boundary",
        "zero_participant_boundary",
        "allowed_rehearsal_scope",
        "stop_conditions",
        "required_truth",
        "claims",
        "external_actions_performed",
    )
    if tuple(audit.keys()) != expected_audit_keys:
        errors.append(_error("$audit", "exact_keys_required"))
    if audit.get("audit_version") != (
        "stage15_gate10_synthetic_rehearsal_scope_readiness/v1"
    ):
        errors.append(_error("$audit.audit_version", "invalid"))
    if audit.get("stage") != "15" or audit.get("stage_id") != "NR-01":
        errors.append(_error("$audit.stage", "invalid"))
    if audit.get("status") != (
        "ready_for_explicit_zero_participant_scope_decision_not_approved"
    ):
        errors.append(_error("$audit.status", "decision_ready_not_approved_required"))
    if audit.get("next_gate") != "HG-PILOT-SCOPE":
        errors.append(_error("$audit.next_gate", "gate10_required"))
    if audit.get("source_assets") != {
        "gate9_readiness": str(GATE9_PATH),
        "gate_proposals": str(PROPOSALS_PATH),
        "candidate_evidence": str(CANDIDATE_PATH),
        "synthetic_fixture": str(FIXTURE_PATH),
    }:
        errors.append(_error("$audit.source_assets", "exact_sources_required"))
    if audit.get("prerequisites") != {
        "gates1_through_9_accepted_and_verified": True,
        "HG-RISK-DISPOSITION": "accepted",
        "every_risk_open_blocked_unaccepted": True,
        "stage10_posture": "BLOCKED / NO-GO",
    }:
        errors.append(_error("$audit.prerequisites", "exact_prerequisites_required"))

    expected_boundary = {
        "human_approver": "Tony",
        "backup_and_escalation_contact": "Stone",
        "technical_owner": "Developer Agent",
        "contributors": ["CustomerService Agent", "Data Agent"],
        "gate_accepted": False,
        "approval_state": "proposed_awaiting_explicit_owner_approval",
        "scope_type": "synthetic_rehearsal_only_no_real_pilot",
        "decision_evidence": "Issue #47",
        "real_pilot_authorized": False,
        "external_actions_allowed": False,
    }
    if audit.get("gate10_decision_boundary") != expected_boundary:
        errors.append(_error("$audit.gate10_decision_boundary", "exact_boundary_required"))

    expected_zero_boundary = {
        "real_customers": 0,
        "employees_or_real_operators": 0,
        "stores": 0,
        "production_or_staging_environments": 0,
        "real_cases_orders_accounts_or_messages": 0,
    }
    if audit.get("zero_participant_boundary") != expected_zero_boundary:
        errors.append(_error("$audit.zero_participant_boundary", "all_counts_must_be_zero"))
    if audit.get("allowed_rehearsal_scope") != [
        "repository_controlled_buw_synthetic_fixtures",
        "local_or_pull_request_ci_execution",
        "deterministic_evaluator_and_fail_closed_controls",
        "synthetic_support_incident_recovery_and_evidence_records",
        "maximum_result_needs_human_governance",
    ]:
        errors.append(_error("$audit.allowed_rehearsal_scope", "exact_scope_required"))
    if audit.get("stop_conditions") != [
        "real_or_unmarked_data",
        "cross_boundary_scope",
        "missing_evidence_or_owner",
        "requested_external_action",
        "support_recovery_or_metric_failure",
        "representation_as_real_pilot",
    ]:
        errors.append(_error("$audit.stop_conditions", "exact_stop_conditions_required"))

    if gate9.get("status") != (
        "accepted_treatment_direction_risks_remain_open_blocked_unaccepted"
    ):
        errors.append(_error("$gate9.status", "accepted_gate9_required"))
    if gate9.get("next_gate") != "HG-PILOT-SCOPE":
        errors.append(_error("$gate9.next_gate", "gate10_required"))
    gate9_boundary = gate9.get("gate9_decision_boundary")
    if not isinstance(gate9_boundary, dict):
        errors.append(_error("$gate9.gate9_decision_boundary", "mapping_required"))
    else:
        if gate9_boundary.get("gate_accepted") is not True:
            errors.append(_error("$gate9.gate9_decision_boundary.gate_accepted", "true_required"))
        if gate9_boundary.get("risk_acceptance") is not False:
            errors.append(_error("$gate9.gate9_decision_boundary.risk_acceptance", "false_required"))
        if gate9_boundary.get("production_action_allowed") is not False:
            errors.append(_error("$gate9.gate9_decision_boundary.production_action_allowed", "false_required"))
    gate9_treatments = gate9.get("risk_treatment_readiness")
    if not isinstance(gate9_treatments, list) or len(gate9_treatments) != 10:
        errors.append(_error("$gate9.risk_treatment_readiness", "exact_ten_required"))
    else:
        for index, (risk_id, treatment) in enumerate(zip(RISK_IDS, gate9_treatments)):
            if not isinstance(treatment, dict):
                errors.append(_error(f"$gate9.risk_treatment_readiness[{index}]", "mapping_required"))
                continue
            if treatment.get("risk_id") != risk_id:
                errors.append(_error(f"$gate9.risk_treatment_readiness[{index}].risk_id", "ordered_id_required"))
            if treatment.get("treatment_authorized") is not True:
                errors.append(_error(f"$gate9.risk_treatment_readiness[{index}].treatment_authorized", "true_required"))
            if treatment.get("risk_accepted") is not False:
                errors.append(_error(f"$gate9.risk_treatment_readiness[{index}].risk_accepted", "false_required"))
            if treatment.get("production_action_allowed") is not False:
                errors.append(_error(f"$gate9.risk_treatment_readiness[{index}].production_action_allowed", "false_required"))

    sequencing = proposals.get("sequencing")
    proposal_list = proposals.get("proposals")
    if not isinstance(sequencing, dict):
        errors.append(_error("$proposals.sequencing", "mapping_required"))
    else:
        if sequencing.get("accepted_gates") != list(GATE_ORDER[:9]):
            errors.append(_error("$proposals.sequencing.accepted_gates", "gates1_through_9_required"))
        if sequencing.get("gate_order") != list(GATE_ORDER):
            errors.append(_error("$proposals.sequencing.gate_order", "exact_order_required"))
        if sequencing.get("next_gate") != "HG-PILOT-SCOPE":
            errors.append(_error("$proposals.sequencing.next_gate", "gate10_required"))
        if sequencing.get("release_gate_accepted") is not False:
            errors.append(_error("$proposals.sequencing.release_gate_accepted", "false_required"))
    gate10 = proposal_list[3] if isinstance(proposal_list, list) and len(proposal_list) > 3 else None
    if not isinstance(gate10, dict):
        errors.append(_error("$proposals.gate10", "mapping_required"))
    else:
        expected_gate10 = {
            "gate_id": "HG-PILOT-SCOPE",
            "issue": "#47",
            "accepted": False,
            "state": "proposed_awaiting_explicit_owner_approval",
            "prerequisite_gates": list(GATE_ORDER[:9]),
            "scope_type": "synthetic_rehearsal_only_no_real_pilot",
            "human_approver": "Tony",
            "backup_and_escalation_contact": "Stone",
            "technical_owner": "Developer Agent",
            "contributors": ["CustomerService Agent", "Data Agent"],
            "zero_participants": expected_zero_boundary,
            "entry_conditions": [
                "gates1_through_9_separately_accepted_and_verified",
                "all_risks_have_treatment_dispositions_but_remain_unaccepted",
                "stage10_remains_blocked_no_go",
                "external_actions_performed_empty",
            ],
            "stop_conditions": [
                "real_or_unmarked_data",
                "cross_boundary_scope",
                "missing_evidence_or_owner",
                "requested_external_action",
                "support_recovery_or_metric_failure",
                "representation_as_real_pilot",
            ],
            "approval_condition": "gates7_through_9_accepted_then_explicit_zero_participant_scope_approval",
            "authority_ceiling": "needs_human_governance",
            "external_actions_allowed": False,
        }
        if gate10 != expected_gate10:
            errors.append(_error("$proposals.gate10", "exact_pending_scope_required"))

    candidate_gates = candidate.get("gate_ledger")
    if not isinstance(candidate_gates, list) or len(candidate_gates) != 12:
        errors.append(_error("$candidate.gate_ledger", "exact_twelve_required"))
    else:
        for index, gate_id in enumerate(GATE_ORDER):
            gate = candidate_gates[index]
            if not isinstance(gate, dict) or gate.get("gate_id") != gate_id:
                errors.append(_error(f"$candidate.gate_ledger[{index}]", "ordered_gate_required"))
                continue
            if index < 9 and (gate.get("accepted") is not True or gate.get("state") != "accepted"):
                errors.append(_error(f"$candidate.gate_ledger[{index}]", "accepted_prerequisite_required"))
            if index == 9 and (
                gate.get("accepted") is not False
                or gate.get("state") != "proposed_awaiting_explicit_owner_approval"
            ):
                errors.append(_error("$candidate.gate_ledger[9]", "gate10_must_remain_pending"))
            if index > 9 and gate.get("accepted") is not False:
                errors.append(_error(f"$candidate.gate_ledger[{index}]", "later_gate_must_remain_unaccepted"))
    if candidate.get("risk_posture") != {
        "stage10": "BLOCKED / NO-GO",
        "risk_count": 10,
        "risk_state": "open_blocked_unaccepted",
        "treatment_ownership": "authorized_for_treatment_evidence_only",
        "risk_acceptance": False,
    }:
        errors.append(_error("$candidate.risk_posture", "blocked_unaccepted_required"))
    candidate_decision = candidate.get("candidate_decision")
    if not isinstance(candidate_decision, dict):
        errors.append(_error("$candidate.candidate_decision", "mapping_required"))
    else:
        if candidate_decision.get("result") != "not_ready_pending_human_governance":
            errors.append(_error("$candidate.candidate_decision.result", "pending_required"))
        if candidate_decision.get("remaining_human_gates") != [
            "HG-PILOT-SCOPE",
            "HG-PILOT-EVIDENCE",
            "HG-RELEASE",
        ]:
            errors.append(_error("$candidate.candidate_decision.remaining_human_gates", "gate10_first_required"))

    if fixture.get("scope") != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$fixture.scope", "buw_only_required"))
    environment = fixture.get("environment")
    if not isinstance(environment, dict):
        errors.append(_error("$fixture.environment", "mapping_required"))
    else:
        if environment.get("mode") != "local_synthetic_disposable":
            errors.append(_error("$fixture.environment.mode", "local_synthetic_required"))
        for field in ("external_endpoints", "connectors", "credentials"):
            if environment.get(field) != []:
                errors.append(_error(f"$fixture.environment.{field}", "must_be_empty"))
    data_contract = fixture.get("data_contract")
    if not isinstance(data_contract, dict):
        errors.append(_error("$fixture.data_contract", "mapping_required"))
    else:
        if data_contract.get("provenance") != "synthetic":
            errors.append(_error("$fixture.data_contract.provenance", "synthetic_required"))
        if data_contract.get("classification") != "synthetic_non_personal":
            errors.append(_error("$fixture.data_contract.classification", "synthetic_non_personal_required"))
    risk_states = fixture.get("risk_states")
    if not isinstance(risk_states, dict) or tuple(risk_states.keys()) != RISK_IDS:
        errors.append(_error("$fixture.risk_states", "ordered_ten_risks_required"))
    elif any(value != "open_blocked_unaccepted" for value in risk_states.values()):
        errors.append(_error("$fixture.risk_states", "all_must_remain_open_blocked_unaccepted"))
    if fixture.get("required_human_gates") != [
        "HG-PILOT-SCOPE",
        "HG-PILOT-EVIDENCE",
        "HG-RELEASE",
    ]:
        errors.append(_error("$fixture.required_human_gates", "gate10_first_required"))
    if fixture.get("requested_external_actions") != []:
        errors.append(_error("$fixture.requested_external_actions", "must_be_empty"))
    fixture_claims = fixture.get("claims")
    if fixture_claims != {
        "risk_accepted": False,
        "pilot_authorized": False,
        "production_ready": False,
        "release_authorized": False,
    } or not all(type(value) is bool for value in fixture_claims.values()):
        errors.append(_error("$fixture.claims", "all_false_required"))
    observation = fixture.get("observation")
    if not isinstance(observation, dict) or any(
        observation.get(field) is not False
        for field in ("paging", "ticket_created", "external_delivery")
    ):
        errors.append(_error("$fixture.observation", "no_external_delivery_required"))
    incident = fixture.get("incident_tabletop")
    if not isinstance(incident, dict) or incident.get("real_incident_declared") is not False:
        errors.append(_error("$fixture.incident_tabletop", "synthetic_only_required"))
    support = fixture.get("support_handoff")
    if not isinstance(support, dict) or support.get("ticket_created") is not False:
        errors.append(_error("$fixture.support_handoff", "no_real_ticket_required"))

    if audit.get("required_truth") != {
        "company": "汇沣电商",
        "brand": "BUW",
        "excluded_entities": ["PC", "六合通"],
        "synthetic_fixture_validated": True,
        "external_endpoints_empty": True,
        "connectors_empty": True,
        "credentials_empty": True,
        "requested_external_actions_empty": True,
        "real_data_used": False,
        "real_pilot_performed": False,
        "pilot_authorized": False,
        "risk_accepted": False,
        "production_ready": False,
        "release_authorized": False,
    }:
        errors.append(_error("$audit.required_truth", "exact_truth_required"))
    claims = audit.get("claims")
    if (
        not isinstance(claims, dict)
        or claims != FALSE_CLAIMS
        or not all(type(value) is bool for value in claims.values())
    ):
        errors.append(_error("$audit.claims", "exact_false_claims_required"))
    if audit.get("external_actions_performed") != []:
        errors.append(_error("$audit.external_actions_performed", "must_be_empty"))
    return errors


def validate_assets(
    audit: Any,
    gate9: Any,
    proposals: Any,
    candidate: Any,
    fixture: Any,
) -> list[str]:
    return _fail_closed(
        _validate_impl,
        audit,
        gate9,
        proposals,
        candidate,
        fixture,
        path="$gate10_scope_readiness",
    )


def evaluate_assets(
    audit: Any,
    gate9: Any,
    proposals: Any,
    candidate: Any,
    fixture: Any,
) -> dict[str, Any]:
    errors = validate_assets(audit, gate9, proposals, candidate, fixture)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "next_gate": "HG-PILOT-SCOPE",
            "gate10_accepted": False,
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": "ready_for_explicit_owner_decision_not_approved",
        "reason_codes": ["EXPLICIT_ZERO_PARTICIPANT_SCOPE_APPROVAL_REQUIRED"],
        "next_gate": "HG-PILOT-SCOPE",
        "gate10_accepted": False,
        "claims": dict(FALSE_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        assets = load_repository_assets(root)
    except Exception as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    return validate_assets(*assets)


def main() -> int:
    try:
        assets = load_repository_assets(ROOT)
    except Exception as exc:
        print(
            "AIOS Stage 15 Gate 10 synthetic-scope readiness validation FAILED "
            f"load_error={type(exc).__name__}"
        )
        return 1
    result = evaluate_assets(*assets)
    if result["result"] == "denied":
        print("AIOS Stage 15 Gate 10 synthetic-scope readiness validation FAILED")
        for reason in result["reason_codes"]:
            print(reason)
        return 1
    print("AIOS Stage 15 Gate 10 synthetic-scope readiness validation PASSED")
    print(f"result={result['result']}")
    print(f"next_gate={result['next_gate']}")
    print("gate10_accepted=false")
    print("pilot_authorized=false")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
