#!/usr/bin/env python3
"""Read-only validator for Stage 12 Privacy and Data Governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = Path("Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml")
POLICY = Path("Governance/AIOS-Privacy-Data-Governance-v1.md")
MAPPING = Path("Governance/AIOS-Privacy-Data-Governance-Stage10-Mapping-v1.yaml")
ACCEPTANCE = Path("Governance/AIOS-Privacy-Data-Governance-Acceptance-Matrix-v1.yaml")
VALIDATION = Path("Tests/AIOS-Privacy-Data-Governance-Validation.md")
TESTS = Path("Tests/test_privacy_data_governance.py")
WORKFLOW = Path(".github/workflows/validate-aios-privacy-data-governance.yml")
STAGE_REGISTRY = Path("Governance/AIOS-Stage-Registry.md")
PROJECT_REGISTRY = Path("Governance/AIOS-Project-Registry.md")
UNASSIGNED = "unassigned / governance decision required"
STAGE10_RISKS = {f"PR-RISK-{number:03d}" for number in range(1, 11)}
AUTHORITY_FLAGS = (
    "legal_approval_granted",
    "real_data_authorized",
    "production_ready",
    "deployment_authorized",
    "pilot_authorized",
    "release_authorized",
    "risk_acceptance_granted",
)


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


def _append_once(errors: list[str], code: str) -> None:
    if code not in errors:
        errors.append(code)


def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = model.get("metadata", {})
    expected = {
        "stage": 12,
        "stage_id": "DG-01",
        "issue": 28,
        "governance_version": "2.2",
        "main_baseline": "e4ad42068b72ea107bf0c57aba11c6dd86e3cf0c",
        "execution_thread": "019f8762-4b8c-7452-addb-ba9510988798",
        "branch": "feat/aios-privacy-data-governance-v1",
        "mode": "synthetic_policy_validation",
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            errors.append(f"metadata.{key} must equal {value!r}")
    if metadata.get("stage_status") not in {"Executing", "Reported", "Reviewed", "Archived"}:
        errors.append("metadata.stage_status must be Executing, Reported, Reviewed or Archived")
    if metadata.get("owner_state") != UNASSIGNED:
        errors.append("metadata.owner_state must remain unassigned")

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
    for key, value in expected_boundaries.items():
        if boundaries.get(key) != value:
            errors.append(f"business_boundaries.{key} must equal {value!r}")

    for section in (
        "data_assets",
        "purposes",
        "basis_decisions",
        "consent_or_preference_records",
        "access_policies",
        "retention_rules",
    ):
        items = model.get(section, [])
        if not isinstance(items, list) or not items:
            errors.append(f"{section} must be a non-empty list")
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict) or item.get("owner_state") != UNASSIGNED:
                errors.append(f"{section}[{index}].owner_state must remain unassigned")

    for index, asset in enumerate(model.get("data_assets", [])):
        if asset.get("synthetic_only") is not True:
            errors.append(f"data_assets[{index}].synthetic_only must be true")

    for index, basis in enumerate(model.get("basis_decisions", [])):
        if basis.get("status") != "human_review_recorded_for_synthetic_design":
            errors.append(
                f"basis_decisions[{index}].status must be synthetic-design review only"
            )
        if basis.get("legal_conclusion") is not False:
            errors.append(f"basis_decisions[{index}].legal_conclusion must be false")
        if basis.get("real_data_authorized") is not False:
            errors.append(f"basis_decisions[{index}].real_data_authorized must be false")

    for index, record in enumerate(model.get("consent_or_preference_records", [])):
        if record.get("synthetic_only") is not True:
            errors.append(
                f"consent_or_preference_records[{index}].synthetic_only must be true"
            )
        if record.get("human_review_state") != "human_review_recorded_for_synthetic_design":
            errors.append(
                f"consent_or_preference_records[{index}].human_review_state must be synthetic-design review only"
            )
        if not isinstance(record.get("purpose_ids"), list) or not record["purpose_ids"]:
            errors.append(
                f"consent_or_preference_records[{index}].purpose_ids must be non-empty"
            )

    subject_flow = model.get("subject_request_flow", {})
    lineage = model.get("lineage_policy", {})
    if subject_flow.get("owner_state") != UNASSIGNED:
        errors.append("subject_request_flow.owner_state must remain unassigned")
    if subject_flow.get("automatic_fulfillment") is not False or subject_flow.get("real_action_allowed") is not False:
        errors.append("subject_request_flow must deny automatic and real fulfillment")
    if lineage.get("owner_state") != UNASSIGNED:
        errors.append("lineage_policy.owner_state must remain unassigned")
    if lineage.get("cross_boundary_allowed") is not False or lineage.get("raw_personal_content_allowed") is not False:
        errors.append("lineage_policy must deny cross-boundary and raw personal content")

    decision = model.get("decision", {})
    if decision.get("result") != "policy_review_candidate":
        errors.append("decision.result must be policy_review_candidate")
    for key in AUTHORITY_FLAGS:
        if decision.get(key) is not False:
            errors.append(f"decision.{key} must be false")
    return errors


def evaluate_request(model: dict[str, Any], request: dict[str, Any]) -> list[str]:
    """Return deterministic denial reason codes; an empty list is allowed."""

    reasons: list[str] = []
    boundaries = model.get("business_boundaries", {})
    assets = _items_by_id(model.get("data_assets"))
    purposes = _items_by_id(model.get("purposes"))
    bases = _items_by_id(model.get("basis_decisions"))
    preferences = _items_by_id(model.get("consent_or_preference_records"))
    retention = _items_by_id(model.get("retention_rules"))
    categories = request.get("categories")
    fields = request.get("fields")
    category_set = set(categories) if isinstance(categories, list) else set()
    field_set = set(fields) if isinstance(fields, list) else set()

    if not isinstance(request.get("request_id"), str) or not request["request_id"].strip():
        _append_once(reasons, "missing_request_id")
    if request.get("synthetic") is not True:
        _append_once(reasons, "real_or_unmarked_data")
    if (
        request.get("company") != boundaries.get("allowed_company")
        or request.get("brand") != boundaries.get("allowed_brand")
    ):
        _append_once(reasons, "cross_boundary")
    if not isinstance(categories, list) or not categories:
        _append_once(reasons, "missing_categories")
    if not isinstance(fields, list) or not fields:
        _append_once(reasons, "missing_fields")

    asset = assets.get(str(request.get("asset_id")))
    if not asset or request.get("subject_type") != asset.get("subject_type"):
        _append_once(reasons, "unknown_asset_or_subject")
    else:
        if not category_set.issubset(set(asset.get("categories", []))):
            _append_once(reasons, "unknown_category")
        if not field_set.issubset(set(asset.get("fields", []))):
            _append_once(reasons, "field_not_allowed_for_asset")

    purpose = purposes.get(str(request.get("purpose_id")))
    if not purpose:
        _append_once(reasons, "unknown_purpose")
    else:
        if request.get("asset_id") not in purpose.get("allowed_assets", []):
            _append_once(reasons, "asset_not_allowed_for_purpose")
        if not category_set.issubset(set(purpose.get("allowed_categories", []))):
            _append_once(reasons, "category_not_allowed_for_purpose")
        if request.get("action") not in purpose.get("allowed_actions", []):
            _append_once(reasons, "action_not_allowed_for_purpose")
        basis_id = request.get("basis_decision_id")
        if not basis_id:
            _append_once(reasons, "missing_basis_decision")
        elif (
            basis_id not in bases
            or basis_id not in purpose.get("basis_decision_ids", [])
            or bases[basis_id].get("status")
            != "human_review_recorded_for_synthetic_design"
            or bases[basis_id].get("legal_conclusion") is not False
            or bases[basis_id].get("real_data_authorized") is not False
        ):
            _append_once(reasons, "invalid_basis_decision")
        if not field_set.issubset(set(purpose.get("allowed_fields", []))):
            _append_once(reasons, "excessive_fields")
        if purpose.get("consent_or_preference_required") is True:
            preference_id = request.get("consent_or_preference_id")
            if not preference_id:
                _append_once(reasons, "missing_consent_or_preference")
            else:
                preference = preferences.get(str(preference_id))
                if (
                    not preference
                    or request.get("purpose_id") not in preference.get("purpose_ids", [])
                    or preference.get("synthetic_only") is not True
                    or preference.get("human_review_state")
                    != "human_review_recorded_for_synthetic_design"
                ):
                    _append_once(reasons, "invalid_consent_or_preference")

    action = request.get("action")
    if action in {"delete", "correct", "export", "fulfill_subject_request"}:
        _append_once(reasons, "human_approval_required")
    access_allowed = any(
        isinstance(policy, dict)
        and policy.get("role") == request.get("actor_role")
        and request.get("purpose_id") in policy.get("purpose_ids", [])
        and action in policy.get("actions", [])
        and category_set.issubset(set(policy.get("categories", [])))
        for policy in model.get("access_policies", [])
    )
    if not access_allowed:
        _append_once(reasons, "unauthorized_access")

    rule = retention.get(str(request.get("retention_rule_id")))
    if (
        not rule
        or not isinstance(rule.get("duration_days"), int)
        or rule.get("duration_days", 0) <= 0
        or rule.get("review_required") is not True
        or rule.get("automatic_real_deletion") is not False
    ):
        _append_once(reasons, "invalid_retention")

    lineage = request.get("lineage")
    lineage_policy = model.get("lineage_policy", {})
    if not isinstance(lineage, dict) or not lineage.get("source") or not lineage.get("destination"):
        _append_once(reasons, "missing_lineage")
    elif (
        lineage.get("source") not in lineage_policy.get("allowed_sources", [])
        or lineage.get("destination") not in lineage_policy.get("allowed_destinations", [])
    ):
        _append_once(reasons, "invalid_lineage")

    if request.get("automatic_real_deletion") is True:
        _append_once(reasons, "automatic_real_deletion")
    if any(
        request.get(key) is True
        for key in (
            "production_authorized",
            "legal_approval_granted",
            "compliance_certified",
            "real_data_authorized",
        )
    ):
        _append_once(reasons, "production_or_legal_claim")
    return reasons


def _validate_evidence_paths(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    for section in ("mappings", "criteria"):
        for index, item in enumerate(data.get(section, [])):
            paths = item.get("evidence_paths") if isinstance(item, dict) else None
            if not isinstance(paths, list) or not paths:
                errors.append(f"{section}[{index}].evidence_paths must be non-empty")
                continue
            for raw in paths:
                path = Path(str(raw))
                if path.is_absolute() or ".." in path.parts or not (root / path).is_file():
                    errors.append(f"{section}[{index}] evidence path is missing or unsafe: {raw}")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    model = _yaml(root / MODEL, errors)
    mapping = _yaml(root / MAPPING, errors)
    acceptance = _yaml(root / ACCEPTANCE, errors)
    policy = _text(root / POLICY, errors)
    _text(root / VALIDATION, errors)
    _text(root / TESTS, errors)
    workflow = _text(root / WORKFLOW, errors)
    stage_registry = _text(root / STAGE_REGISTRY, errors)
    project_registry = _text(root / PROJECT_REGISTRY, errors)
    if model:
        errors.extend(validate_model(model))
        for request in model.get("sample_requests", []):
            for reason in evaluate_request(model, request):
                errors.append(f"sample request denied: {reason}")

    if mapping:
        ids = {
            item.get("stage10_risk_id")
            for item in mapping.get("mappings", [])
            if isinstance(item, dict)
        }
        if ids != STAGE10_RISKS:
            errors.append("Stage 10 mapping must cover exactly PR-RISK-001 through PR-RISK-010")
        for index, item in enumerate(mapping.get("mappings", [])):
            if item.get("owner_state") != UNASSIGNED:
                errors.append(f"mappings[{index}].owner_state must remain unassigned")
            if item.get("risk_accepted") is not False or item.get("production_action_allowed") is not False:
                errors.append(f"mappings[{index}] must deny risk acceptance and production action")
            if item.get("residual_status") not in {"open", "blocked"}:
                errors.append(f"mappings[{index}].residual_status must remain open or blocked")
        errors.extend(_validate_evidence_paths(mapping, root))

    if acceptance:
        decision = acceptance.get("overall_decision", {})
        if decision.get("result") != "policy_review_candidate":
            errors.append("acceptance result must be policy_review_candidate")
        for key in ("legal_approval_granted", "real_data_authorized", "production_ready", "deployment_authorized", "pilot_authorized", "release_authorized"):
            if decision.get(key) is not False:
                errors.append(f"acceptance overall_decision.{key} must be false")
        errors.extend(_validate_evidence_paths(acceptance, root))

    required_headings = (
        "## Six system questions",
        "## Business and data boundaries",
        "## Governance object model",
        "## Classification and minimization",
        "## Retention and disposition",
        "## Lineage and audit",
        "## Mandatory boundaries",
    )
    for heading in required_headings:
        if heading not in policy:
            errors.append(f"policy document missing heading: {heading}")

    status = model.get("metadata", {}).get("stage_status") if model else None
    stage_row = next(
        (line for line in stage_registry.splitlines() if line.startswith("| 12 | DG-01 |")),
        "",
    )
    if not stage_row or f"| {status} |" not in stage_row:
        errors.append("Stage Registry status must match the Stage 12 model")
    if "Stage 12 / DG-01" not in project_registry or str(status) not in project_registry:
        errors.append("Project Registry must identify the current Stage 12 status")

    required_workflow = ("pull_request:", "contents: read", "persist-credentials: false")
    for token in required_workflow:
        if token not in workflow:
            errors.append(f"CI missing required read-only control: {token}")
    for forbidden in ("push:", "workflow_dispatch:", "contents: write", "pull-requests: write", "git push"):
        if forbidden in workflow:
            errors.append(f"CI contains forbidden trigger, permission or command: {forbidden}")
    return errors


if __name__ == "__main__":
    problems = validate_repository()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)
    print("Stage 12 Privacy and Data Governance validation passed.")
