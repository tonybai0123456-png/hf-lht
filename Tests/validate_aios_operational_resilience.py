#!/usr/bin/env python3
"""Read-only validator for Stage 13 Operational Resilience."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = Path("Governance/AIOS-Operational-Resilience-Model-v1.yaml")
POLICY = Path("Governance/AIOS-Operational-Resilience-v1.md")
MAPPING = Path("Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml")
ACCEPTANCE = Path("Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml")
FIXTURE = Path("Tests/Fixtures/operational-resilience/synthetic-service-degradation.yaml")
VALIDATION = Path("Tests/AIOS-Operational-Resilience-Validation.md")
TESTS = Path("Tests/test_operational_resilience.py")
WORKFLOW = Path(".github/workflows/validate-aios-operational-resilience.yml")
SPEC = Path("docs/superpowers/specs/2026-07-22-operational-resilience-v1-design.md")
PLAN = Path("docs/superpowers/plans/2026-07-22-operational-resilience-v1.md")
STAGE_REGISTRY = Path("Governance/AIOS-Stage-Registry.md")
PROJECT_REGISTRY = Path("Governance/AIOS-Project-Registry.md")
UNASSIGNED = "unassigned / governance decision required"
STAGE10_RISKS = {f"PR-RISK-{number:03d}" for number in range(1, 11)}
REQUIRED_GATES = [
    "incident_declaration",
    "failover",
    "restoration",
    "external_communication",
    "exception",
    "risk_acceptance",
    "release",
]
AUTHORITY_FLAGS = (
    "incident_authority_granted",
    "failover_authorized",
    "restoration_authorized",
    "external_communication_authorized",
    "exception_authorized",
    "risk_acceptance_granted",
    "pilot_authorized",
    "release_authorized",
    "production_ready",
    "sla_slo_achieved",
    "backup_restore_tested",
    "real_incident_capability",
)
AUTHORIZED_PREPARE_ACTIONS = [
    "classify_synthetic_signal",
    "evaluate_resilience_policy",
    "prepare_recovery_recommendation",
]
PROHIBITED_REAL_ACTIONS = [
    "declare_incident",
    "perform_failover",
    "perform_restore",
    "send_external_communication",
    "grant_exception",
    "accept_risk",
    "approve_release",
    "page_on_call",
    "modify_infrastructure",
]
REQUIRED_CLAIMS = {
    "sla_achieved",
    "slo_achieved",
    "backup_tested",
    "restore_tested",
    "real_incident_capability",
}
INCIDENT_RECORD_FIELDS = [
    "scenario_id",
    "policy_version",
    "synthetic",
    "company",
    "brand",
    "service_id",
    "dependency_ids",
    "signal_type",
    "severity",
    "impact",
    "decision",
    "reason_codes",
    "human_gates",
    "evidence_refs",
]
EXPECTED_INCIDENT_RECORD_CONTRACT = {
    "required_fields": INCIDENT_RECORD_FIELDS,
    "synthetic_only": True,
    "persistent_store_provisioned": False,
    "real_incident_id_allowed": False,
    "raw_alert_payload_allowed": False,
    "owner_state": UNASSIGNED,
}
EXPECTED_INCIDENT_LIFECYCLE = {
    "states": [
        "signal_received",
        "classified",
        "policy_evaluated",
        "human_decision_required",
        "synthetic_evidence_ready",
    ],
    "terminal_state": "human_decision_required",
    "incident_declaration_automatic": False,
    "containment_automatic": False,
    "recovery_automatic": False,
    "closure_automatic": False,
    "owner_state": UNASSIGNED,
}
EXPECTED_RUNBOOK_CONTRACT = {
    "required_sections": [
        "scope",
        "prerequisites",
        "stop_conditions",
        "decision_gates",
        "evidence",
        "validation",
        "escalation",
    ],
    "execution_mode": "prepare_only",
    "real_commands_allowed": False,
    "owner_state": UNASSIGNED,
}
EXPECTED_ESCALATION_CONTRACT = {
    "severity_to_abstract_role": {
        "SEV-1": "Incident Authority",
        "SEV-2": "Incident Authority",
        "SEV-3": "Governance Authority",
        "SEV-4": "Governance Authority",
    },
    "paging_enabled": False,
    "external_communication_enabled": False,
    "owner_state": UNASSIGNED,
}
EXPECTED_OBSERVABILITY_CONTRACT = {
    "design_signals": [
        "synthetic_availability",
        "synthetic_dependency_health",
        "synthetic_data_integrity",
    ],
    "alert_delivery_enabled": False,
    "monitoring_connector_enabled": False,
    "durable_telemetry_claimed": False,
    "owner_state": UNASSIGNED,
}
EXPECTED_AUDIT_CONTRACT = {
    "required_fields": [
        "scenario_id",
        "policy_version",
        "service_id",
        "severity",
        "impact",
        "decision",
        "reason_codes",
        "evidence_refs",
    ],
    "append_only_design": True,
    "persistent_store_provisioned": False,
    "raw_personal_content_allowed": False,
    "credentials_allowed": False,
    "owner_state": UNASSIGNED,
}


def _yaml(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing required file: {path.as_posix()}")
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"could not parse {path.as_posix()}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.as_posix()} must contain a mapping")
        return {}
    return value


def _text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required file: {path.as_posix()}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"could not read {path.as_posix()}: {exc}")
        return ""


def _items_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        str(item.get("id")): item
        for item in items
        if isinstance(item, dict) and item.get("id")
    }


def _append_once(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _has_unique_non_empty_ids(items: Any) -> bool:
    if not isinstance(items, list) or not items:
        return False
    ids = [
        item.get("id") if isinstance(item, dict) else None
        for item in items
    ]
    return (
        all(isinstance(item_id, str) and item_id.strip() for item_id in ids)
        and len(ids) == len(set(ids))
    )


def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = model.get("metadata", {})
    expected_metadata = {
        "stage": 13,
        "stage_id": "OR-01",
        "issue": 32,
        "governance_version": "2.2",
        "main_baseline": "c5dde2171c65e75b595c411854cba0016f3623f7",
        "execution_thread": "019f8a35-6d4e-7c60-b35a-79de8626d4e3",
        "branch": "feat/aios-operational-resilience-v1",
        "mode": "synthetic_tabletop_validation",
        "stage_status": "Archived",
        "owner_state": UNASSIGNED,
    }
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            errors.append(f"metadata.{key} must equal {expected!r}")

    questions = model.get("six_system_questions", {})
    required_questions = {
        "business_loop",
        "core_objects",
        "data_flow",
        "operators",
        "ai_human_boundary",
        "proof",
    }
    if set(questions) != required_questions or any(
        not str(value).strip() for value in questions.values()
    ):
        errors.append("six_system_questions must contain six non-empty answers")

    boundaries = model.get("business_boundaries", {})
    expected_boundaries = {
        "allowed_company": "汇沣电商",
        "allowed_brand": "BUW",
        "excluded_brand": "PC",
        "excluded_company": "六合通",
        "cross_boundary_default": "deny",
    }
    for key, expected in expected_boundaries.items():
        if boundaries.get(key) != expected:
            errors.append(f"business_boundaries.{key} must equal {expected!r}")

    for section in ("services", "dependencies"):
        items = model.get(section, [])
        if not isinstance(items, list) or not items:
            errors.append(f"{section} must be a non-empty list")
            continue
        if not _has_unique_non_empty_ids(items):
            errors.append(f"{section} must contain unique non-empty ids")
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{section}[{index}] must be a mapping")
                continue
            if item.get("owner_state") != UNASSIGNED:
                errors.append(f"{section}[{index}].owner_state must remain unassigned")
            if item.get("synthetic_only") is not True:
                errors.append(f"{section}[{index}].synthetic_only must be true")
            if section == "services" and item.get("deployed") is not False:
                errors.append(f"{section}[{index}].deployed must be false")
            if section == "dependencies" and item.get("external_connection") is not False:
                errors.append(f"{section}[{index}].external_connection must be false")

    for section in (
        "continuity_tiers",
        "severity_levels",
        "impact_classes",
        "failure_modes",
    ):
        if not _has_unique_non_empty_ids(model.get(section)):
            errors.append(f"{section} must contain unique non-empty ids")

    failure_modes = model.get("failure_modes", [])
    if not isinstance(failure_modes, list) or not failure_modes:
        errors.append("failure_modes must be a non-empty list")
    else:
        for index, failure_mode in enumerate(failure_modes):
            if failure_mode.get("real_signal_source") is not False:
                errors.append(f"failure_modes[{index}].real_signal_source must be false")
            if failure_mode.get("automatic_incident_declaration") is not False:
                errors.append(
                    f"failure_modes[{index}].automatic_incident_declaration must be false"
                )

    services = _items_by_id(model.get("services"))
    dependencies = _items_by_id(model.get("dependencies"))
    tiers = _items_by_id(model.get("continuity_tiers"))
    for service_id, service in services.items():
        if service.get("company") != "汇沣电商" or service.get("brand") != "BUW":
            errors.append(f"services.{service_id} must remain in 汇沣电商 / BUW")
        if service.get("continuity_tier_id") not in tiers:
            errors.append(f"services.{service_id} has unknown continuity tier")
        unknown = set(service.get("dependency_ids", [])) - set(dependencies)
        if unknown:
            errors.append(f"services.{service_id} has unknown dependencies: {sorted(unknown)}")

    for index, tier in enumerate(model.get("continuity_tiers", [])):
        if tier.get("claim_state") != "design_target_only":
            errors.append(
                f"continuity_tiers[{index}].claim_state must be design_target_only"
            )
        if not isinstance(tier.get("rto_minutes"), int) or tier["rto_minutes"] <= 0:
            errors.append(f"continuity_tiers[{index}].rto_minutes must be positive")
        if not isinstance(tier.get("rpo_minutes"), int) or tier["rpo_minutes"] < 0:
            errors.append(f"continuity_tiers[{index}].rpo_minutes must be non-negative")
        if tier.get("human_approval_required") is not True:
            errors.append(f"continuity_tiers[{index}] must require human approval")

    evidence = model.get("recovery_evidence_requirements", [])
    if not isinstance(evidence, list) or len(evidence) < 3:
        errors.append("recovery_evidence_requirements must contain at least three items")
    if not _has_unique_non_empty_ids(evidence):
        errors.append(
            "recovery_evidence_requirements must contain unique non-empty ids"
        )
    for index, requirement in enumerate(evidence):
        if requirement.get("claim_state") != "design_requirement_only":
            errors.append(
                f"recovery_evidence_requirements[{index}].claim_state must be design_requirement_only"
            )
        if requirement.get("owner_state") != UNASSIGNED:
            errors.append(
                f"recovery_evidence_requirements[{index}].owner_state must remain unassigned"
            )

    gates = model.get("human_gates", [])
    if [gate.get("id") for gate in gates if isinstance(gate, dict)] != REQUIRED_GATES:
        errors.append("human_gates must contain the seven required gates in order")
    for index, gate in enumerate(gates):
        if gate.get("required") is not True or gate.get("owner_state") != UNASSIGNED:
            errors.append(f"human_gates[{index}] must be required and unassigned")

    if model.get("incident_record_contract") != EXPECTED_INCIDENT_RECORD_CONTRACT:
        errors.append(
            "incident_record_contract must require synthetic fields and prohibit persistence"
        )

    if model.get("incident_lifecycle") != EXPECTED_INCIDENT_LIFECYCLE:
        errors.append("incident_lifecycle must be exact, manual, and unassigned")
    if model.get("runbook_contract") != EXPECTED_RUNBOOK_CONTRACT:
        errors.append("runbook_contract must be exact, prepare-only, and unassigned")
    if model.get("escalation_contract") != EXPECTED_ESCALATION_CONTRACT:
        errors.append("escalation_contract must be exact, non-operational, and unassigned")
    if model.get("observability_contract") != EXPECTED_OBSERVABILITY_CONTRACT:
        errors.append("observability_contract must be exact, disconnected, and unassigned")
    if model.get("audit_contract") != EXPECTED_AUDIT_CONTRACT:
        errors.append("audit_contract must be exact, non-persistent, and unassigned")
    if model.get("allowed_prepare_actions") != AUTHORIZED_PREPARE_ACTIONS:
        errors.append(
            "allowed_prepare_actions must equal the authorized prepare-only actions"
        )
    if model.get("prohibited_real_actions") != PROHIBITED_REAL_ACTIONS:
        errors.append(
            "prohibited_real_actions must equal the authorized real-action denials"
        )

    decision = model.get("decision", {})
    if decision.get("result") != "resilience_review_candidate":
        errors.append("decision.result must be resilience_review_candidate")
    if set(decision) != {"result", *AUTHORITY_FLAGS}:
        errors.append("decision must contain only the authorized result and denial flags")
    for flag in AUTHORITY_FLAGS:
        if decision.get(flag) is not False:
            errors.append(f"decision.{flag} must be false")
    return errors


def evaluate_scenario(model: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    """Evaluate declared synthetic facts without performing any external action."""

    reasons: list[str] = []
    boundaries = model.get("business_boundaries", {})
    services = _items_by_id(model.get("services"))
    dependencies = _items_by_id(model.get("dependencies"))
    severities = _items_by_id(model.get("severity_levels"))
    impacts = _items_by_id(model.get("impact_classes"))
    failure_modes = _items_by_id(model.get("failure_modes"))
    tiers = _items_by_id(model.get("continuity_tiers"))
    requirements = _items_by_id(model.get("recovery_evidence_requirements"))

    scenario_id_value = scenario.get("scenario_id")
    scenario_id = (
        scenario_id_value.strip() if isinstance(scenario_id_value, str) else ""
    )
    if not scenario_id:
        _append_once(reasons, "missing_scenario_id")

    if scenario.get("synthetic") is not True:
        _append_once(reasons, "real_or_unmarked_signal")
    if (
        scenario.get("company") != boundaries.get("allowed_company")
        or scenario.get("brand") != boundaries.get("allowed_brand")
    ):
        _append_once(reasons, "cross_boundary")

    service = services.get(str(scenario.get("service_id")))
    if not service:
        _append_once(reasons, "unknown_service")

    supplied_dependency_ids = scenario.get("dependency_ids")
    dependency_ids = (
        supplied_dependency_ids.copy()
        if isinstance(supplied_dependency_ids, list)
        else []
    )
    dependency_ids_are_strings = all(
        isinstance(item, str) for item in dependency_ids
    )
    duplicate_dependencies = (
        dependency_ids_are_strings
        and len(dependency_ids) != len(set(dependency_ids))
    )
    dependencies_known = bool(dependency_ids) and dependency_ids_are_strings and all(
        item in dependencies for item in dependency_ids
    )
    if not dependencies_known:
        _append_once(reasons, "unknown_dependency")
    if duplicate_dependencies:
        _append_once(reasons, "duplicate_dependency")
    if (
        service
        and dependencies_known
        and not duplicate_dependencies
        and dependency_ids != service.get("dependency_ids", [])
    ):
        _append_once(reasons, "dependency_contract_mismatch")

    if str(scenario.get("severity")) not in severities:
        _append_once(reasons, "invalid_severity")
    if str(scenario.get("impact")) not in impacts:
        _append_once(reasons, "invalid_impact")
    if str(scenario.get("signal_type")) not in failure_modes:
        _append_once(reasons, "unknown_failure_mode")

    target = scenario.get("continuity_target")
    if not isinstance(target, dict):
        _append_once(reasons, "unsupported_rto_rpo")
    else:
        tier = tiers.get(str(target.get("tier_id")))
        if (
            not tier
            or target.get("rto_minutes") != tier.get("rto_minutes")
            or target.get("rpo_minutes") != tier.get("rpo_minutes")
            or (service and target.get("tier_id") != service.get("continuity_tier_id"))
        ):
            _append_once(reasons, "unsupported_rto_rpo")

    supplied_evidence = scenario.get("recovery_evidence")
    required_evidence_ids = list(requirements)
    if not isinstance(supplied_evidence, list) or not supplied_evidence:
        _append_once(reasons, "missing_recovery_evidence")
    else:
        entries_are_valid = all(
            isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and bool(item["id"].strip())
            for item in supplied_evidence
        )
        if not entries_are_valid:
            _append_once(reasons, "recovery_evidence_contract_mismatch")
        else:
            supplied_evidence_ids = [item["id"] for item in supplied_evidence]
            if len(supplied_evidence_ids) != len(set(supplied_evidence_ids)):
                _append_once(reasons, "duplicate_recovery_evidence")
            if (
                len(supplied_evidence) != len(required_evidence_ids)
                or supplied_evidence_ids != required_evidence_ids
            ):
                _append_once(reasons, "recovery_evidence_contract_mismatch")
            if set(supplied_evidence_ids) != set(required_evidence_ids):
                _append_once(reasons, "missing_recovery_evidence")

    valid_evidence_entries = (
        supplied_evidence
        if isinstance(supplied_evidence, list)
        else []
    )
    for supplied in valid_evidence_entries:
        if not isinstance(supplied, dict):
            continue
        evidence_id = supplied.get("id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            continue
        if evidence_id not in requirements:
            _append_once(reasons, "missing_recovery_evidence")
        if supplied.get("state") != "design_requirement_only":
            _append_once(reasons, "invalid_recovery_evidence_state")
            _append_once(reasons, "achievement_claim")

    supplied_gates = scenario.get("human_gates")
    if not isinstance(supplied_gates, list) or not supplied_gates:
        _append_once(reasons, "missing_human_gate")
    else:
        gates_are_strings = all(isinstance(gate, str) for gate in supplied_gates)
        if gates_are_strings and len(supplied_gates) != len(set(supplied_gates)):
            _append_once(reasons, "duplicate_human_gate")
        if not gates_are_strings or supplied_gates != REQUIRED_GATES:
            _append_once(reasons, "human_gate_contract_mismatch")

    if (
        scenario.get("requested_action") not in AUTHORIZED_PREPARE_ACTIONS
        or scenario.get("requested_action") in PROHIBITED_REAL_ACTIONS
        or scenario.get("external_actions_performed") is not False
    ):
        _append_once(reasons, "unsafe_continuity_action")

    claims = scenario.get("claims")
    claims_are_exact_false = (
        isinstance(claims, dict)
        and set(claims) == REQUIRED_CLAIMS
        and all(value is False for value in claims.values())
    )
    if not claims_are_exact_false:
        _append_once(reasons, "invalid_claim_contract")
    if isinstance(claims, dict) and any(value is True for value in claims.values()):
        _append_once(reasons, "achievement_claim")

    evidence_refs = [
        requirement.get("evidence_path")
        for requirement in requirements.values()
        if requirement.get("evidence_path")
    ]
    result = "denied" if reasons else "needs_human_approval"
    incident_record = {
        "scenario_id": scenario_id,
        "policy_version": str(model.get("metadata", {}).get("governance_version", "")),
        "synthetic": scenario.get("synthetic") is True,
        "company": scenario.get("company"),
        "brand": scenario.get("brand"),
        "service_id": scenario.get("service_id"),
        "dependency_ids": dependency_ids,
        "signal_type": scenario.get("signal_type"),
        "severity": scenario.get("severity"),
        "impact": scenario.get("impact"),
        "decision": result,
        "reason_codes": reasons.copy(),
        "human_gates": REQUIRED_GATES.copy(),
        "evidence_refs": evidence_refs.copy(),
    }
    return {
        "result": result,
        "reason_codes": reasons,
        "required_human_gates": REQUIRED_GATES.copy(),
        "evidence_refs": evidence_refs,
        "external_actions_performed": False,
        "incident_record": incident_record,
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    required_paths = (
        MODEL,
        POLICY,
        MAPPING,
        ACCEPTANCE,
        FIXTURE,
        VALIDATION,
        TESTS,
        WORKFLOW,
        SPEC,
        PLAN,
        STAGE_REGISTRY,
        PROJECT_REGISTRY,
    )
    for relative in required_paths:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative.as_posix()}")

    model = _yaml(root / MODEL, errors)
    errors.extend(validate_model(model))
    fixture = _yaml(root / FIXTURE, errors)
    result = evaluate_scenario(model, fixture)
    if result.get("result") != "needs_human_approval" or result.get("reason_codes"):
        errors.append("positive fixture must stop at needs_human_approval")
    incident_record = result.get("incident_record", {})
    if (
        not isinstance(incident_record, dict)
        or list(incident_record) != INCIDENT_RECORD_FIELDS
        or incident_record.get("scenario_id") != fixture.get("scenario_id")
        or incident_record.get("decision") != "needs_human_approval"
    ):
        errors.append("positive fixture must emit the complete synthetic incident record")

    mapping = _yaml(root / MAPPING, errors)
    entries = mapping.get("mappings", [])
    if {entry.get("stage10_risk_id") for entry in entries if isinstance(entry, dict)} != STAGE10_RISKS:
        errors.append("mapping must cover exactly PR-RISK-001 through PR-RISK-010")
    for index, entry in enumerate(entries):
        if entry.get("residual_status") not in {"open", "blocked"}:
            errors.append(f"mappings[{index}].residual_status must remain open or blocked")
        if entry.get("risk_accepted") is not False:
            errors.append(f"mappings[{index}].risk_accepted must be false")
        if entry.get("production_action_allowed") is not False:
            errors.append(f"mappings[{index}].production_action_allowed must be false")
        if entry.get("owner_state") != UNASSIGNED:
            errors.append(f"mappings[{index}].owner_state must remain unassigned")

    acceptance = _yaml(root / ACCEPTANCE, errors)
    criteria = acceptance.get("criteria", [])
    if not isinstance(criteria, list) or len(criteria) < 10:
        errors.append("acceptance matrix must contain at least ten criteria")
    for index, criterion in enumerate(criteria):
        if criterion.get("design_only") is not True or criterion.get("expected") != "pass":
            errors.append(f"criteria[{index}] must be design-only and expect pass")
        for evidence_path in criterion.get("evidence_paths", []):
            if not isinstance(evidence_path, str) or Path(evidence_path).is_absolute() or not (root / evidence_path).is_file():
                errors.append(f"criteria[{index}] has invalid evidence path: {evidence_path!r}")
    for flag, value in acceptance.get("authority_boundary", {}).items():
        if value is not False:
            errors.append(f"acceptance authority boundary {flag} must be false")

    policy = _text(root / POLICY, errors)
    for required in (
        "Business loop and six system questions",
        "Service and dependency inventory",
        "RTO/RPO design targets",
        "Human decision gates",
        "BUW",
        "PC",
        "汇沣电商",
        "六合通",
        "design target",
        "unassigned / governance decision required",
    ):
        if required not in policy:
            errors.append(f"policy missing required statement: {required}")

    workflow = _text(root / WORKFLOW, errors)
    if "pull_request:" not in workflow or "permissions:\n  contents: read" not in workflow:
        errors.append("workflow must be pull-request-only with contents read")
    for prohibited in ("push:", "workflow_dispatch:", "contents: write", "git push", "curl ", "wget "):
        if prohibited in workflow:
            errors.append(f"workflow contains prohibited token: {prohibited}")

    stage_registry = _text(root / STAGE_REGISTRY, errors)
    project_registry = _text(root / PROJECT_REGISTRY, errors)
    errors.extend(validate_current_registry_lifecycle(stage_registry, project_registry))
    return errors


def validate_current_registry_lifecycle(
    stage_registry: str,
    project_registry: str,
) -> list[str]:
    """Validate Stage 13 archive evidence and the Stage 14 Reported ceiling."""
    errors: list[str] = []
    stage13 = next((line for line in stage_registry.splitlines() if line.startswith("| 13 |")), "")
    stage14 = next((line for line in stage_registry.splitlines() if line.startswith("| 14 |")), "")
    project = next((line for line in project_registry.splitlines() if line.startswith("| BUW-AIOS |")), "")

    stage13_required = (
        "Issue #32", "Issue #34", "019f8a35-6d4e-7c60-b35a-79de8626d4e3",
        "feat/aios-operational-resilience-v1", "327d9e9", "7b16a5c",
        "19/19", "80/80", "| Archived |",
    )
    if not all(token in stage13 for token in stage13_required):
        errors.append("Stage 13 registry row must preserve exact reviewed published archive evidence")

    stage14_required = (
        "Issue #36", "019f8c92-e709-7a83-b06c-fa014cf0b216",
        "feat/aios-support-controlled-pilot-design-v1", "PR #37",
        "| Reported |", "Implementation evidence head", "Mandatory Return",
        "needs_human_governance", "independently approved plan", "no pilot authority",
    )
    if not all(token in stage14 for token in stage14_required):
        errors.append("Stage 14 must record evidence-backed Reported status under independently approved plan")

    for forbidden in (
        "| Reviewed |", "| Archived |", "pilot authority granted", "pilot authorized",
        "pilot_authorized: true", "release authorized", "released", "ready for pilot",
        "self-approved plan", "named owner", "real data connected", "connector enabled",
    ):
        if forbidden in stage14:
            errors.append(f"Stage 14 exceeds Reported authority: {forbidden}")

    project_required = (
        "Stage 13 Archived / Stage 14 Reported", "Issue #36",
        "implementation evidence head", "Draft PR #37", "Mandatory Return",
        "needs_human_governance", "Awaiting independent human review", "no pilot authority",
    )
    if not all(token in project for token in project_required):
        errors.append("Project Registry must record Stage 14 Reported awaiting independent human review")

    for forbidden in (
        "Stage 14 Reviewed", "Stage 14 Archived", "pilot authority granted",
        "pilot authorized", "pilot_authorized: true", "release authorized",
        "self-approved", "ready for pilot",
    ):
        if forbidden in project:
            errors.append(f"Project Registry exceeds Reported authority: {forbidden}")
    return errors


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Operational Resilience validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    fixture = yaml.safe_load((ROOT / FIXTURE).read_text(encoding="utf-8"))
    model = yaml.safe_load((ROOT / MODEL).read_text(encoding="utf-8"))
    result = evaluate_scenario(model, fixture)
    print("AIOS Operational Resilience validation PASSED")
    print(f"- deterministic fixture outcome: {result['result']}")
    print(f"- required human gates: {len(result['required_human_gates'])}")
    print("- external actions performed: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
