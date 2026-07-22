#!/usr/bin/env python3
"""Deterministic, read-only validation for Stage 10 Production Readiness evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT = Path("Governance/AIOS-Production-Readiness-v1.md")
MATRIX = Path("Governance/AIOS-Production-Readiness-Matrix-v1.yaml")
INVENTORY = Path("Governance/AIOS-Production-Readiness-Inventory-v1.md")
RISKS = Path("Governance/AIOS-Production-Readiness-Risk-Register-v1.yaml")
STAGE_REGISTRY = Path("Governance/AIOS-Stage-Registry.md")
WORKFLOW = Path(".github/workflows/validate-aios-production-readiness.yml")

REQUIRED_QUESTIONS = {
    "business_loop",
    "core_objects",
    "data_flow",
    "operators",
    "ai_human_boundary",
    "proof",
}
REQUIRED_DIMENSIONS = {
    "architecture_dependencies",
    "operating_boundary",
    "security",
    "privacy",
    "data",
    "observability",
    "rollback",
    "incident_response",
    "support",
    "audit_governance",
}
REQUIRED_APPROVAL_GATES = {
    "architecture",
    "security",
    "privacy_data",
    "operations",
    "pilot",
    "release",
}
ALLOWED_GATE_STATUSES = {"pass", "gap", "blocked", "not_applicable"}
UNASSIGNED = "unassigned / governance decision required"


def _load_yaml(path: Path, errors: list[str]) -> dict[str, Any]:
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


def _read_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required file: {path.as_posix()}")
        return ""
    return path.read_text(encoding="utf-8")


def _check_evidence_paths(items: list[Any], root: Path, errors: list[str], label: str) -> None:
    for index, item in enumerate(items):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}[{index}] must be a non-empty repository path")
            continue
        path = Path(item)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"{label}[{index}] must be repository-relative")
            continue
        if not (root / path).is_file():
            errors.append(f"{label}[{index}] evidence does not exist: {item}")


def validate_matrix(matrix: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    metadata = matrix.get("metadata")
    if not isinstance(metadata, dict):
        return ["matrix.metadata must be a mapping"]
    expected = {
        "stage": 10,
        "stage_id": "PR-01",
        "issue": 21,
        "governance_version": "2.1",
        "main_baseline": "6cffaed4f4bc693aa897864396ae097b972bff80",
        "execution_thread": "019f8937-ac22-71a2-bb35-d8f6d2e0f55f",
        "branch": "feat/aios-production-readiness-v1",
        "mode": "prepare_only",
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            errors.append(f"matrix.metadata.{field} must equal {value!r}")
    if metadata.get("stage_status") not in {"Executing", "Reported", "Reviewed"}:
        errors.append("matrix.metadata.stage_status must be Executing, Reported or Reviewed")

    questions = matrix.get("six_system_questions")
    if not isinstance(questions, dict) or set(questions) != REQUIRED_QUESTIONS:
        errors.append("matrix.six_system_questions must contain exactly the six required questions")
    elif any(not isinstance(value, str) or not value.strip() for value in questions.values()):
        errors.append("every six-system-question answer must be non-empty")

    decision = matrix.get("assessment_decision")
    if not isinstance(decision, dict):
        errors.append("matrix.assessment_decision must be a mapping")
    else:
        if decision.get("recommendation") != "blocked":
            errors.append("assessment recommendation must remain blocked")
        if decision.get("production_ready") is not False:
            errors.append("production_ready must be false")
        if decision.get("release_authorized") is not False:
            errors.append("release_authorized must be false")
        if decision.get("decision_authority") != "BUW AIOS Official Governance Thread":
            errors.append("decision authority must remain the Governance Thread")

    boundaries = matrix.get("business_boundaries")
    if not isinstance(boundaries, dict):
        errors.append("matrix.business_boundaries must be a mapping")
    else:
        for key in ("BUW", "PC", "汇沣电商", "六合通"):
            if key not in boundaries or not isinstance(boundaries[key], str):
                errors.append(f"business boundary missing: {key}")
        if boundaries.get("cross_boundary_default") != "deny":
            errors.append("cross-boundary default must be deny")

    gates = matrix.get("readiness_gates")
    if not isinstance(gates, list) or not gates:
        errors.append("matrix.readiness_gates must be a non-empty list")
    else:
        dimensions: set[str] = set()
        blocked_count = 0
        ids: set[str] = set()
        for index, gate in enumerate(gates):
            label = f"readiness_gates[{index}]"
            if not isinstance(gate, dict):
                errors.append(f"{label} must be a mapping")
                continue
            gate_id = gate.get("id")
            if not isinstance(gate_id, str) or not gate_id:
                errors.append(f"{label}.id must be non-empty")
            elif gate_id in ids:
                errors.append(f"duplicate readiness gate id: {gate_id}")
            else:
                ids.add(gate_id)
            dimension = gate.get("dimension")
            if isinstance(dimension, str):
                dimensions.add(dimension)
            status = gate.get("status")
            if status not in ALLOWED_GATE_STATUSES:
                errors.append(f"{label}.status is invalid")
            if status == "blocked":
                blocked_count += 1
            if gate.get("production_action_allowed") is not False:
                errors.append(f"{label} must deny production action")
            if status in {"gap", "blocked"} and gate.get("owner_state") != UNASSIGNED:
                errors.append(f"{label}.owner_state must remain unassigned")
            for field in ("criterion", "current_evidence", "gap", "human_gate"):
                if not gate.get(field):
                    errors.append(f"{label}.{field} must be non-empty")
            evidence = gate.get("evidence_paths")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{label}.evidence_paths must be non-empty")
            else:
                _check_evidence_paths(evidence, root, errors, f"{label}.evidence_paths")
        missing_dimensions = sorted(REQUIRED_DIMENSIONS - dimensions)
        if missing_dimensions:
            errors.append(f"missing readiness dimensions: {missing_dimensions}")
        if blocked_count == 0:
            errors.append("at least one readiness gate must be blocked")

    approvals = matrix.get("human_approval_gates")
    if not isinstance(approvals, list):
        errors.append("matrix.human_approval_gates must be a list")
    else:
        kinds: set[str] = set()
        for index, gate in enumerate(approvals):
            label = f"human_approval_gates[{index}]"
            if not isinstance(gate, dict):
                errors.append(f"{label} must be a mapping")
                continue
            kinds.add(str(gate.get("type")))
            if gate.get("approval_mode") != "explicit_human":
                errors.append(f"{label} must require explicit human approval")
            if gate.get("status") != "not_authorized":
                errors.append(f"{label} must remain not_authorized")
            if gate.get("silence_is_approval") is not False:
                errors.append(f"{label} must reject silence as approval")
        missing = sorted(REQUIRED_APPROVAL_GATES - kinds)
        if missing:
            errors.append(f"missing human approval gate types: {missing}")
    return errors


def validate_risks(risks: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    entries = risks.get("risks")
    if not isinstance(entries, list) or not entries:
        return ["risk register must contain a non-empty risks list"]
    ids: set[str] = set()
    for index, risk in enumerate(entries):
        label = f"risks[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{label} must be a mapping")
            continue
        risk_id = risk.get("id")
        if not isinstance(risk_id, str) or not risk_id:
            errors.append(f"{label}.id must be non-empty")
        elif risk_id in ids:
            errors.append(f"duplicate risk id: {risk_id}")
        else:
            ids.add(risk_id)
        if risk.get("owner_state") != UNASSIGNED:
            errors.append(f"{label}.owner_state must remain unassigned")
        if risk.get("acceptance_status") != "not_accepted":
            errors.append(f"{label}.acceptance_status must be not_accepted")
        if risk.get("acceptance_authority") != "BUW AIOS Official Governance Thread":
            errors.append(f"{label}.acceptance_authority is invalid")
        if risk.get("production_action_allowed") is not False:
            errors.append(f"{label} must deny production action")
        for field in ("category", "risk", "impact", "mitigation", "next_evidence"):
            if not risk.get(field):
                errors.append(f"{label}.{field} must be non-empty")
        evidence = risk.get("evidence_paths")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}.evidence_paths must be non-empty")
        else:
            _check_evidence_paths(evidence, root, errors, f"{label}.evidence_paths")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    assessment = _read_text(root / ASSESSMENT, errors)
    inventory = _read_text(root / INVENTORY, errors)
    stage_registry = _read_text(root / STAGE_REGISTRY, errors)
    workflow = _read_text(root / WORKFLOW, errors)
    matrix = _load_yaml(root / MATRIX, errors)
    risks = _load_yaml(root / RISKS, errors)

    if matrix:
        errors.extend(validate_matrix(matrix, root))
    if risks:
        errors.extend(validate_risks(risks, root))

    for heading in (
        "## Six system questions",
        "## Readiness decision matrix",
        "## Security, privacy and data",
        "## Observability, rollback and support",
        "## Human approval gates",
        "## Assessment conclusion",
    ):
        if heading not in assessment:
            errors.append(f"assessment missing heading: {heading}")
    for heading in (
        "## Architecture and dependency inventory",
        "## Operating-boundary inventory",
        "## Verified absences and limitations",
    ):
        if heading not in inventory:
            errors.append(f"inventory missing heading: {heading}")

    stage10 = next((line for line in stage_registry.splitlines() if line.startswith("| 10 |")), "")
    matrix_status = matrix.get("metadata", {}).get("stage_status") if matrix else None
    if matrix_status and f"| {matrix_status} |" not in stage10:
        errors.append("Stage Registry status must match matrix.metadata.stage_status")
    for required in (
        "Issue #21",
        "019f8937-ac22-71a2-bb35-d8f6d2e0f55f",
        "feat/aios-production-readiness-v1",
    ):
        if required not in stage10:
            errors.append(f"Stage 10 registry row missing: {required}")

    if workflow:
        for required in (
            "pull_request:",
            "permissions:\n  contents: read",
            "persist-credentials: false",
            "python Tests/validate_aios_production_readiness.py",
        ):
            if required not in workflow:
                errors.append(f"readiness CI missing: {required}")
        for prohibited in ("push:", "contents: write", "pull-requests: write", "git push"):
            if prohibited in workflow:
                errors.append(f"readiness CI contains prohibited capability: {prohibited}")
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("AIOS Production Readiness validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AIOS Production Readiness validation PASSED")
    print("- prepare-only assessment: validated")
    print("- readiness gates and human approvals: validated")
    print("- risk owners and acceptance: fail-closed")
    print("- repository evidence paths: readable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
