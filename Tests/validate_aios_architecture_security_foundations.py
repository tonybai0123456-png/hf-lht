#!/usr/bin/env python3
"""Read-only validator for Stage 11 Architecture and Security Foundations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS = Path("Governance/AIOS-Architecture-Security-Foundations-v1.md")
MODEL = Path("Governance/AIOS-Architecture-Security-Model-v1.yaml")
THREATS = Path("Governance/AIOS-Architecture-Security-Threat-Model-v1.yaml")
MAPPING = Path("Governance/AIOS-Architecture-Security-Stage10-Mapping-v1.yaml")
ACCEPTANCE = Path("Governance/AIOS-Architecture-Security-Acceptance-Matrix-v1.yaml")
STAGE_REGISTRY = Path("Governance/AIOS-Stage-Registry.md")
WORKFLOW = Path(".github/workflows/validate-aios-architecture-security-foundations.yml")
UNASSIGNED = "unassigned / governance decision required"
QUESTIONS = {"business_loop", "core_objects", "data_flow", "operators", "ai_human_boundary", "proof"}
BOUNDARIES = {"BUW", "PC", "汇沣电商", "六合通"}
ZONES = {"governance_control", "human_access", "ingress_policy", "orchestration_runtime", "durable_control_state", "audit_observability", "connector_boundary", "external_business_systems"}
STAGE10_RISKS = {f"PR-RISK-{number:03d}" for number in range(1, 11)}


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
    return path.read_text(encoding="utf-8")


def _evidence(paths: Any, root: Path, errors: list[str], label: str) -> None:
    if not isinstance(paths, list) or not paths:
        errors.append(f"{label} must be a non-empty list")
        return
    for item in paths:
        path = Path(str(item))
        if path.is_absolute() or ".." in path.parts or not (root / path).is_file():
            errors.append(f"{label} evidence does not exist or is unsafe: {item}")


def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = model.get("metadata", {})
    expected = {
        "stage": 11, "stage_id": "AF-01", "issue": 24, "governance_version": "2.2",
        "main_baseline": "45944a50ea33e61ad2683082441d2dac75812906",
        "execution_thread": "019f89ac-e3b7-7b90-ad27-286708c407e0",
        "branch": "feat/aios-architecture-security-foundations-v1", "mode": "design_only",
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            errors.append(f"model.metadata.{key} must equal {value!r}")
    if metadata.get("stage_status") not in {"Executing", "Reported", "Reviewed"}:
        errors.append("model.metadata.stage_status must be Executing, Reported or Reviewed")
    if set(model.get("six_system_questions", {})) != QUESTIONS:
        errors.append("model must answer exactly the six system questions")
    elif any(not str(value).strip() for value in model["six_system_questions"].values()):
        errors.append("six system question answers must be non-empty")
    boundaries = model.get("business_boundaries", {})
    if not BOUNDARIES.issubset(boundaries) or boundaries.get("cross_boundary_default") != "deny":
        errors.append("business boundaries must separate BUW, PC, 汇沣电商 and 六合通 with default deny")
    zones = model.get("trust_zones", [])
    if {zone.get("id") for zone in zones if isinstance(zone, dict)} != ZONES:
        errors.append("trust zones must contain exactly the required zones")
    for index, zone in enumerate(zones):
        if zone.get("provisioned") is not False:
            errors.append(f"trust_zones[{index}].provisioned must be false")
        if zone.get("owner_state") != UNASSIGNED:
            errors.append(f"trust_zones[{index}].owner_state must remain unassigned")
    for index, component in enumerate(model.get("target_components", [])):
        if component.get("provisioned") is not False:
            errors.append(f"target_components[{index}].provisioned must be false")
        if component.get("owner_state") != UNASSIGNED:
            errors.append(f"target_components[{index}].owner_state must remain unassigned")
    identity = model.get("identity_and_access", {})
    if identity.get("least_privilege_default") != "deny" or identity.get("identities_created") is not False:
        errors.append("identity design must deny by default and create no identities")
    secrets = model.get("secrets_lifecycle", {})
    if secrets.get("design_only") is not True or secrets.get("secrets_created") is not False:
        errors.append("secrets lifecycle must remain design-only and create no secrets")
    forbidden_secret_fields = {"value", "secret", "credential", "token", "password", "private_key"}
    if forbidden_secret_fields.intersection(secrets):
        errors.append("secrets lifecycle must not contain secret material fields")
    connectors = model.get("connector_boundary", {})
    if connectors.get("default") != "deny" or connectors.get("enabled_connectors") != [] or connectors.get("external_writes_allowed") is not False:
        errors.append("connector boundary must deny by default with no enabled connector or external write")
    decision = model.get("decision", {})
    for key in ("production_ready", "deployment_authorized", "pilot_authorized", "release_authorized", "risk_acceptance_granted"):
        if decision.get(key) is not False:
            errors.append(f"decision.{key} must be false")
    return errors


def validate_threats(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    threats = data.get("threats", [])
    required = {"identity", "secrets", "data_boundary", "connector", "execution", "audit", "supply_chain"}
    if not required.issubset({item.get("category") for item in threats if isinstance(item, dict)}):
        errors.append("threat model is missing required categories")
    for index, threat in enumerate(threats):
        if threat.get("owner_state") != UNASSIGNED:
            errors.append(f"threats[{index}].owner_state must remain unassigned")
        if threat.get("acceptance_status") != "not_accepted" or threat.get("production_action_allowed") is not False:
            errors.append(f"threats[{index}] must remain unaccepted and deny production action")
        _evidence(threat.get("evidence_paths"), root, errors, f"threats[{index}].evidence_paths")
    return errors


def validate_mapping(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    mappings = data.get("mappings", [])
    ids = {item.get("stage10_risk_id") for item in mappings if isinstance(item, dict)}
    if ids != STAGE10_RISKS:
        errors.append("Stage 10 mapping must cover exactly PR-RISK-001 through PR-RISK-010")
    for index, item in enumerate(mappings):
        if item.get("owner_state") != UNASSIGNED:
            errors.append(f"mappings[{index}].owner_state must remain unassigned")
        if item.get("residual_status") not in {"open", "blocked"}:
            errors.append(f"mappings[{index}].residual_status must remain open or blocked")
        if item.get("risk_accepted") is not False or item.get("production_action_allowed") is not False:
            errors.append(f"mappings[{index}] must not accept risk or allow production action")
        _evidence(item.get("evidence_paths"), root, errors, f"mappings[{index}].evidence_paths")
    return errors


def validate_acceptance(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    decision = data.get("overall_decision", {})
    if decision.get("result") != "design_review_candidate":
        errors.append("acceptance result must be design_review_candidate")
    for key in ("production_ready", "deployment_authorized", "pilot_authorized", "release_authorized"):
        if decision.get(key) is not False:
            errors.append(f"acceptance overall_decision.{key} must be false")
    for index, criterion in enumerate(data.get("criteria", [])):
        if criterion.get("owner_state") != UNASSIGNED:
            errors.append(f"criteria[{index}].owner_state must remain unassigned")
        if criterion.get("production_action_allowed") is not False:
            errors.append(f"criteria[{index}] must deny production action")
        _evidence(criterion.get("evidence_paths"), root, errors, f"criteria[{index}].evidence_paths")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    foundations = _text(root / FOUNDATIONS, errors)
    registry = _text(root / STAGE_REGISTRY, errors)
    workflow = _text(root / WORKFLOW, errors)
    model = _yaml(root / MODEL, errors)
    threats = _yaml(root / THREATS, errors)
    mapping = _yaml(root / MAPPING, errors)
    acceptance = _yaml(root / ACCEPTANCE, errors)
    if model:
        errors.extend(validate_model(model))
    if threats:
        errors.extend(validate_threats(threats, root))
    if mapping:
        errors.extend(validate_mapping(mapping, root))
    if acceptance:
        errors.extend(validate_acceptance(acceptance, root))
    for heading in ("## Six system questions", "## Target topology and trust zones", "## Threat model", "## Identity and least privilege", "## Secrets lifecycle design", "## Persistence, idempotency, audit and connectors", "## Capacity and failure assumptions", "## Stage 10 mapping", "## Non-production acceptance"):
        if heading not in foundations:
            errors.append(f"foundations document missing heading: {heading}")
    status = model.get("metadata", {}).get("stage_status")
    marker = f"| 11 | AF-01 |"
    row = next((line for line in registry.splitlines() if line.startswith(marker)), "")
    if not row or f"| {status} |" not in row:
        errors.append("Stage Registry status must match the model")
    if "pull_request:" not in workflow or "contents: read" not in workflow or "persist-credentials: false" not in workflow:
        errors.append("CI must be pull-request-only and read-only")
    for forbidden in ("push:", "workflow_dispatch:", "contents: write", "pull-requests: write"):
        if forbidden in workflow:
            errors.append(f"CI contains forbidden trigger or permission: {forbidden}")
    return errors


if __name__ == "__main__":
    problems = validate_repository()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)
    print("Stage 11 Architecture and Security Foundations validation passed.")
