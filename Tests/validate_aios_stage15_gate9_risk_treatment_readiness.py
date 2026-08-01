from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = Path(
    "Governance/AIOS-Stage15-Gate9-Risk-Treatment-Readiness-Audit-v1.yaml"
)
RISK_REGISTER_PATH = Path(
    "Governance/AIOS-Production-Readiness-Risk-Register-v1.yaml"
)
PROPOSALS_PATH = Path("Governance/AIOS-Stage15-Human-Gate-Proposals-v1.yaml")
CANDIDATE_PATH = Path("Governance/AIOS-Deployment-Free-Candidate-Evidence-v1.yaml")

RISK_IDS = tuple(f"PR-RISK-{number:03d}" for number in range(1, 11))
RISK_CATEGORIES = (
    "architecture",
    "security",
    "privacy",
    "data",
    "observability",
    "rollback",
    "incident_response",
    "support",
    "business_boundary",
    "release_governance",
)
RISK_SEVERITIES = (
    "critical",
    "critical",
    "critical",
    "high",
    "high",
    "critical",
    "high",
    "high",
    "critical",
    "critical",
)
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
FALSE_CLAIMS = {
    "gate9_accepted": False,
    "risk_accepted": False,
    "risk_closed": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
    "deployment_authorized": False,
}
ACCEPTED_CLAIMS = {
    **FALSE_CLAIMS,
    "gate9_accepted": True,
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
        _load_controlled_yaml(root / RISK_REGISTER_PATH),
        _load_controlled_yaml(root / PROPOSALS_PATH),
        _load_controlled_yaml(root / CANDIDATE_PATH),
    )


def _validate_impl(
    audit: Any,
    risk_register: Any,
    proposals: Any,
    candidate: Any,
) -> list[str]:
    errors: list[str] = []
    if not all(isinstance(value, dict) for value in (audit, risk_register, proposals, candidate)):
        return [_error("$", "all_assets_must_be_mappings")]

    expected_audit_keys = (
        "audit_version",
        "stage",
        "stage_id",
        "status",
        "next_gate",
        "source_assets",
        "prerequisites",
        "gate9_decision_boundary",
        "risk_treatment_readiness",
        "required_truth",
        "claims",
        "external_actions_performed",
    )
    if tuple(audit.keys()) != expected_audit_keys:
        errors.append(_error("$audit", "exact_keys_required"))
    if audit.get("audit_version") != "stage15_gate9_risk_treatment_readiness/v1":
        errors.append(_error("$audit.audit_version", "invalid"))
    if audit.get("stage") != "15" or audit.get("stage_id") != "NR-01":
        errors.append(_error("$audit.stage", "invalid"))
    if audit.get("status") != (
        "accepted_treatment_direction_risks_remain_open_blocked_unaccepted"
    ):
        errors.append(_error("$audit.status", "accepted_treatment_direction_required"))
    if audit.get("next_gate") != "HG-PILOT-SCOPE":
        errors.append(_error("$audit.next_gate", "gate10_required"))
    if audit.get("source_assets") != {
        "risk_register": str(RISK_REGISTER_PATH),
        "gate_proposals": str(PROPOSALS_PATH),
        "candidate_evidence": str(CANDIDATE_PATH),
    }:
        errors.append(_error("$audit.source_assets", "exact_sources_required"))
    if audit.get("prerequisites") != {
        "HG-PRIVACY-DATA": "accepted",
        "HG-OPS-RECOVERY-INCIDENT-SUPPORT": "accepted",
    }:
        errors.append(_error("$audit.prerequisites", "gates7_and_8_required"))
    if audit.get("gate9_decision_boundary") != {
        "human_approver": "Tony",
        "overall_risk_owner": "Tony",
        "independent_reviewer_and_escalation_contact": "Stone",
        "gate_accepted": True,
        "approval_state": "accepted",
        "disposition": "mitigate_and_remain_open_blocked_unaccepted",
        "risk_acceptance": False,
        "risk_closure": False,
        "production_action_allowed": False,
        "decision_evidence": "Owner authorization / Issue #46",
    }:
        errors.append(_error("$audit.gate9_decision_boundary", "exact_boundary_required"))

    register_metadata = risk_register.get("metadata")
    register_risks = risk_register.get("risks")
    if not isinstance(register_metadata, dict):
        errors.append(_error("$risk_register.metadata", "mapping_required"))
    else:
        if register_metadata.get("stage") != 10 or register_metadata.get("stage_id") != "PR-01":
            errors.append(_error("$risk_register.metadata", "stage10_required"))
        if register_metadata.get("owner_rule") != "unassigned / governance decision required":
            errors.append(_error("$risk_register.metadata.owner_rule", "must_remain_unassigned"))
    if not isinstance(register_risks, list) or len(register_risks) != 10:
        errors.append(_error("$risk_register.risks", "exact_ten_required"))
        register_risks = []

    proposal_list = proposals.get("proposals")
    gate9 = proposal_list[2] if isinstance(proposal_list, list) and len(proposal_list) > 2 else None
    if not isinstance(gate9, dict):
        errors.append(_error("$proposals.gate9", "mapping_required"))
        gate9_treatments: list[Any] = []
    else:
        expected_gate9_common = {
            "gate_id": "HG-RISK-DISPOSITION",
            "issue": "#46",
            "accepted": True,
            "state": "accepted",
            "scope_type": "risk_treatment_direction_without_acceptance",
            "human_approver": "Tony",
            "overall_risk_owner": "Tony",
            "independent_reviewer_and_escalation_contact": "Stone",
            "decision_evidence": "Owner authorization / Issue #46",
            "authority_ceiling": "needs_human_governance",
            "external_actions_allowed": False,
        }
        for key, expected in expected_gate9_common.items():
            if gate9.get(key) != expected or (
                isinstance(expected, bool) and type(gate9.get(key)) is not bool
            ):
                errors.append(_error(f"$proposals.gate9.{key}", "invalid"))
        gate9_treatments = gate9.get("risk_treatments")
        if not isinstance(gate9_treatments, list) or len(gate9_treatments) != 10:
            errors.append(_error("$proposals.gate9.risk_treatments", "exact_ten_required"))
            gate9_treatments = []

    audit_treatments = audit.get("risk_treatment_readiness")
    if not isinstance(audit_treatments, list) or len(audit_treatments) != 10:
        errors.append(_error("$audit.risk_treatment_readiness", "exact_ten_required"))
        audit_treatments = []

    if len(register_risks) == len(gate9_treatments) == len(audit_treatments) == 10:
        for index, (
            risk_id,
            category,
            severity,
            human_owner,
            technical_support,
        ) in enumerate(
            zip(
                RISK_IDS,
                RISK_CATEGORIES,
                RISK_SEVERITIES,
                RISK_HUMAN_OWNERS,
                RISK_TECHNICAL_SUPPORT,
            )
        ):
            register_risk = register_risks[index]
            proposal_risk = gate9_treatments[index]
            audit_risk = audit_treatments[index]
            path = f"$risks[{index}]"
            if not all(isinstance(value, dict) for value in (register_risk, proposal_risk, audit_risk)):
                errors.append(_error(path, "mapping_required"))
                continue
            if register_risk.get("id") != risk_id:
                errors.append(_error(f"{path}.register.id", "ordered_id_required"))
            if register_risk.get("category") != category:
                errors.append(_error(f"{path}.register.category", "invalid"))
            if register_risk.get("severity") != severity:
                errors.append(_error(f"{path}.register.severity", "invalid"))
            if register_risk.get("owner_state") != "unassigned / governance decision required":
                errors.append(_error(f"{path}.register.owner_state", "must_remain_unassigned"))
            if register_risk.get("acceptance_status") != "not_accepted":
                errors.append(_error(f"{path}.register.acceptance_status", "must_remain_not_accepted"))
            if register_risk.get("production_action_allowed") is not False:
                errors.append(_error(f"{path}.register.production_action_allowed", "must_be_false"))
            expected_proposal = {
                "risk_id": risk_id,
                "human_treatment_owner": human_owner,
                "technical_support_agents": technical_support,
                "disposition": "mitigate_and_remain_open_blocked_unaccepted",
                "production_action_allowed": False,
            }
            if proposal_risk != expected_proposal:
                errors.append(_error(f"{path}.proposal", "exact_treatment_required"))
            expected_audit = {
                "risk_id": risk_id,
                "category": category,
                "severity": severity,
                "human_treatment_owner": human_owner,
                "technical_support_agents": technical_support,
                "disposition": "mitigate_and_remain_open_blocked_unaccepted",
                "treatment_authorized": True,
                "risk_accepted": False,
                "production_action_allowed": False,
            }
            if audit_risk != expected_audit:
                errors.append(_error(f"{path}.audit", "exact_mapping_required"))

    candidate_gates = candidate.get("gate_ledger")
    if not isinstance(candidate_gates, list) or len(candidate_gates) != 12:
        errors.append(_error("$candidate.gate_ledger", "exact_twelve_required"))
    else:
        for index in (6, 7):
            gate = candidate_gates[index]
            if not isinstance(gate, dict) or gate.get("accepted") is not True:
                errors.append(_error(f"$candidate.gate_ledger[{index}]", "accepted_prerequisite_required"))
        gate9_candidate = candidate_gates[8]
        if (
            not isinstance(gate9_candidate, dict)
            or gate9_candidate.get("gate_id") != "HG-RISK-DISPOSITION"
            or gate9_candidate.get("accepted") is not True
            or gate9_candidate.get("state") != "accepted"
        ):
            errors.append(_error("$candidate.gate_ledger[8]", "gate9_must_be_accepted"))
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
        remaining = candidate_decision.get("remaining_human_gates")
        if not isinstance(remaining, list) or remaining != [
            "HG-PILOT-SCOPE",
            "HG-PILOT-EVIDENCE",
            "HG-RELEASE",
        ]:
            errors.append(_error("$candidate.candidate_decision.remaining_human_gates", "gate10_first_required"))

    if audit.get("required_truth") != {
        "risk_count": 10,
        "every_risk_open_blocked_unaccepted": True,
        "every_risk_not_accepted": True,
        "every_production_action_disallowed": True,
        "treatment_ownership_authorized_for_evidence_only": True,
        "stage10_posture": "BLOCKED / NO-GO",
    }:
        errors.append(_error("$audit.required_truth", "exact_truth_required"))
    claims = audit.get("claims")
    if (
        not isinstance(claims, dict)
        or claims != ACCEPTED_CLAIMS
        or not all(type(value) is bool for value in claims.values())
    ):
        errors.append(_error("$audit.claims", "exact_false_claims_required"))
    if audit.get("external_actions_performed") != []:
        errors.append(_error("$audit.external_actions_performed", "must_be_empty"))
    return errors


def validate_assets(
    audit: Any,
    risk_register: Any,
    proposals: Any,
    candidate: Any,
) -> list[str]:
    return _fail_closed(
        _validate_impl,
        audit,
        risk_register,
        proposals,
        candidate,
        path="$gate9_readiness",
    )


def evaluate_assets(
    audit: Any,
    risk_register: Any,
    proposals: Any,
    candidate: Any,
) -> dict[str, Any]:
    errors = validate_assets(audit, risk_register, proposals, candidate)
    if errors:
        return {
            "result": "denied",
            "reason_codes": [f"VALIDATION_ERROR:{error}" for error in errors],
            "next_gate": "HG-PILOT-SCOPE",
            "gate9_accepted": False,
            "claims": dict(FALSE_CLAIMS),
            "external_actions_performed": [],
        }
    return {
        "result": (
            "accepted_treatment_direction_risks_remain_open_blocked_unaccepted"
        ),
        "reason_codes": ["GATE9_ACCEPTED_RISKS_REMAIN_UNACCEPTED"],
        "next_gate": "HG-PILOT-SCOPE",
        "gate9_accepted": True,
        "claims": dict(ACCEPTED_CLAIMS),
        "external_actions_performed": [],
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    try:
        assets = load_repository_assets(root)
    except (OSError, ValueError) as exc:
        return [_error("$repository", f"load_error:{type(exc).__name__}")]
    return validate_assets(*assets)


def main() -> int:
    try:
        assets = load_repository_assets(ROOT)
    except (OSError, ValueError) as exc:
        print("AIOS Stage 15 Gate 9 risk-treatment readiness validation FAILED")
        print(f"- $repository:load_error:{type(exc).__name__}")
        return 1
    errors = validate_assets(*assets)
    if errors:
        print("AIOS Stage 15 Gate 9 risk-treatment readiness validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    result = evaluate_assets(*assets)
    print("AIOS Stage 15 Gate 9 risk-treatment readiness validation PASSED")
    print(f"result={result['result']}")
    print(f"next_gate={result['next_gate']}")
    print(f"gate9_accepted={str(result['gate9_accepted']).lower()}")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
