from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml")
FIXTURE_PATH = Path(
    "Tests/Fixtures/support-controlled-pilot/synthetic-support-pilot-candidate.yaml"
)
MAPPING_PATH = Path(
    "Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml"
)
MATRIX_PATH = Path(
    "Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml"
)
ALLOWED_YAML_PATHS = frozenset(
    {MODEL_PATH, FIXTURE_PATH, MAPPING_PATH, MATRIX_PATH}
)
MODEL_VERSION = "support_controlled_pilot_eligibility/v1"
OWNER_STATE = "unassigned / governance decision required"
ALLOWED_RESULTS = ["denied", "needs_human_governance"]
REQUEST_KEYS = {
    "model_version",
    "support_request_id",
    "support_case_id",
    "pilot_candidate_id",
    "scope_id",
    "company",
    "brand",
    "synthetic_workload_class",
    "owner_state",
    "external_actions_performed",
}
ID_RULES = {
    "support_request_id": re.compile(r"^SR-SYN-[A-Z0-9-]+$"),
    "support_case_id": re.compile(r"^SC-SYN-[A-Z0-9-]+$"),
    "pilot_candidate_id": re.compile(r"^PCAN-SYN-[A-Z0-9-]+$"),
    "scope_id": re.compile(r"^SCOPE-SYN-[A-Z0-9-]+$"),
}
EXPECTED_RISKS = {
    **{f"PR-RISK-{number:03d}": "blocked" for number in range(1, 9)},
    "PR-RISK-009": "open",
    "PR-RISK-010": "open",
}
FORBIDDEN_PERMISSION_TOKENS = frozenset(
    {
        "pilot_authorized",
        "approved",
        "ready",
        "released",
        "eligible",
        "go",
        "accepted",
        "proceed",
        "pilot_ready",
        "production_ready",
    }
)
FORBIDDEN_OPERATIONAL_KEYS = frozenset(
    {
        "ticket",
        "ticket_id",
        "monitor",
        "customer",
        "store",
        "order",
        "employee",
        "infrastructure",
        "database",
        "api",
        "connector",
        "credential",
        "secret",
        "pager",
        "alert",
        "external_url",
        "real_owner",
        "named_owner",
    }
)

TOP_LEVEL_KEYS = (
    "model_version",
    "stage",
    "stage_id",
    "issue",
    "execution_thread",
    "synthetic_only",
    "repository_controlled_fixtures_only",
    "allowed_scope",
    "excluded_entities",
    "owner_state",
    "allowed_results",
    "authority",
    "id_prefixes",
    "human_gates",
    "support_requests",
    "support_cases",
    "pilot_candidates",
    "scopes",
    "entry_criteria",
    "exit_criteria",
    "stop_conditions",
    "withdrawal_conditions",
    "support_models",
    "escalation_paths",
    "success_metrics",
    "guardrail_metrics",
    "evidence_contract",
    "audit_contract",
    "decision_contract",
)
EXPECTED_GATES = [
    "HG-WRITTEN-SPEC-APPROVAL",
    "HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE",
    "HG-NAMED-OWNER-APPOINTMENT",
    "HG-REAL-SCOPE-AND-DATA-AUTHORIZATION",
    "HG-STAGE10-RISK-DISPOSITION",
    "HG-STAGE11-13-EVIDENCE-ACCEPTANCE",
    "HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE",
    "HG-METRIC-AND-EVIDENCE-ACCEPTANCE",
    "HG-BOUNDED-AUTHORITY-DEFINITION",
    "HG-REAL-PILOT-ENTRY-DECISION",
]
COLLECTION_CONTRACTS = {
    "support_requests": (
        "support_request_id",
        "SR-SYN-",
        {
            "support_request_id",
            "model_version",
            "synthetic",
            "pilot_candidate_id",
            "scope_id",
        },
    ),
    "support_cases": (
        "support_case_id",
        "SC-SYN-",
        {
            "support_case_id",
            "model_version",
            "synthetic",
            "support_request_id",
            "support_model_id",
            "escalation_path_id",
        },
    ),
    "pilot_candidates": (
        "pilot_candidate_id",
        "PCAN-SYN-",
        {
            "pilot_candidate_id",
            "model_version",
            "synthetic",
            "scope_id",
            "entry_criteria_ids",
            "exit_criteria_ids",
            "stop_condition_ids",
            "withdrawal_condition_ids",
        },
    ),
    "scopes": (
        "scope_id",
        "SCOPE-SYN-",
        {
            "scope_id",
            "model_version",
            "synthetic",
            "company",
            "brand",
            "workload_class",
            "duration_design_bound",
            "volume_design_bound",
            "permitted_actions",
            "excluded_actions",
        },
    ),
    "entry_criteria": (
        "criterion_id",
        "ENTRY-SYN-",
        {"criterion_id", "required_gate_ids", "real_world_satisfied"},
    ),
    "exit_criteria": (
        "criterion_id",
        "EXIT-SYN-",
        {"criterion_id", "required_evidence", "evaluator_may_close_real_pilot"},
    ),
    "stop_conditions": (
        "condition_id",
        "STOP-SYN-",
        {"condition_id", "triggers", "default_action"},
    ),
    "withdrawal_conditions": (
        "condition_id",
        "WITHDRAW-SYN-",
        {"condition_id", "required_capabilities", "real_roles_assigned"},
    ),
    "support_models": (
        "support_model_id",
        "SUP-SYN-",
        {"support_model_id", "owner_state", "required_elements"},
    ),
    "escalation_paths": (
        "escalation_path_id",
        "ESC-SYN-",
        {"escalation_path_id", "owner_state", "ordered_functions"},
    ),
    "success_metrics": (
        "metric_id",
        "SM-SYN-",
        {
            "metric_id",
            "definition",
            "unit",
            "direction",
            "source",
            "observation_window",
            "threshold_type",
            "threshold",
            "missing_data_behavior",
            "evidence_ref",
            "owner_state",
        },
    ),
    "guardrail_metrics": (
        "metric_id",
        "GM-SYN-",
        {
            "metric_id",
            "definition",
            "unit",
            "direction",
            "source",
            "observation_window",
            "threshold_type",
            "threshold",
            "missing_data_behavior",
            "evidence_ref",
            "owner_state",
        },
    ),
}


def load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]:
    if relative_path.is_absolute() or relative_path not in ALLOWED_YAML_PATHS:
        raise ValueError("path_not_allowlisted")
    resolved_root = root.resolve()
    resolved_path = (resolved_root / relative_path).resolve()
    if resolved_root not in resolved_path.parents:
        raise ValueError("path_outside_repository")
    value = yaml.safe_load(resolved_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("yaml_root_must_be_mapping")
    return value


def _append_once(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _valid_ids(items: Any, id_key: str, prefix: str) -> bool:
    if not isinstance(items, list) or not items:
        return False
    ids = [item.get(id_key) for item in items if isinstance(item, dict)]
    return (
        len(ids) == len(items)
        and all(
            isinstance(value, str)
            and value.startswith(prefix)
            and value != prefix
            and "*" not in value
            and value.upper() == value
            for value in ids
        )
        and len(ids) == len(set(ids))
    )


def _scan_forbidden(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_OPERATIONAL_KEYS:
                _append_once(
                    errors,
                    "FORBIDDEN_OPERATIONAL_FIELD:" + ".".join((*path, str(key))),
                )
            if normalized in FORBIDDEN_PERMISSION_TOKENS and child not in (
                False,
                None,
            ):
                _append_once(
                    errors,
                    "FORBIDDEN_PERMISSION_FIELD:" + ".".join((*path, str(key))),
                )
            for error in _scan_forbidden(child, (*path, str(key))):
                _append_once(errors, error)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            for error in _scan_forbidden(child, (*path, str(index))):
                _append_once(errors, error)
    elif (
        isinstance(value, str)
        and value.strip().lower() in FORBIDDEN_PERMISSION_TOKENS
    ):
        _append_once(errors, "FORBIDDEN_PERMISSION_VALUE:" + ".".join(path))
    return errors


def _scan_model_forbidden(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_authority = {
        "pilot_authorized": False,
        "release_authorized": False,
        "production_action_allowed": False,
        "staging_action_allowed": False,
        "external_action_allowed": False,
    }
    if model.get("authority") != expected_authority:
        _append_once(errors, "MODEL_AUTHORITY_INVALID")
    decision_contract = model.get("decision_contract")
    if (
        not isinstance(decision_contract, dict)
        or decision_contract.get("pilot_authorized") is not False
    ):
        _append_once(errors, "MODEL_DECISION_AUTHORITY_INVALID")
    scannable = {
        key: value
        for key, value in model.items()
        if key not in {"authority", "decision_contract"}
    }
    for error in _scan_forbidden(scannable, ("model",)):
        _append_once(errors, error)
    return errors


def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if tuple(model) != TOP_LEVEL_KEYS:
        _append_once(errors, "top_level_keys_or_order_invalid")
    exact_scalars = {
        "model_version": MODEL_VERSION,
        "stage": 14,
        "stage_id": "PS-01",
        "issue": 36,
        "execution_thread": "019f8c92-e709-7a83-b06c-fa014cf0b216",
        "synthetic_only": True,
        "repository_controlled_fixtures_only": True,
        "allowed_scope": {"company": "汇沣电商", "brand": "BUW"},
        "excluded_entities": ["PC", "六合通"],
        "owner_state": OWNER_STATE,
        "allowed_results": ["denied", "needs_human_governance"],
    }
    for key, expected in exact_scalars.items():
        if model.get(key) != expected:
            _append_once(errors, f"{key}_invalid")

    expected_authority = {
        "pilot_authorized": False,
        "release_authorized": False,
        "production_action_allowed": False,
        "staging_action_allowed": False,
        "external_action_allowed": False,
    }
    if model.get("authority") != expected_authority:
        _append_once(errors, "authority_invalid")

    gates = model.get("human_gates")
    if (
        not isinstance(gates, list)
        or any(
            set(gate) != {"gate_id"} for gate in gates if isinstance(gate, dict)
        )
        or [gate.get("gate_id") for gate in gates if isinstance(gate, dict)]
        != EXPECTED_GATES
    ):
        _append_once(errors, "human_gate_order_invalid")

    for collection, (id_key, prefix, exact_keys) in COLLECTION_CONTRACTS.items():
        items = model.get(collection)
        if not _valid_ids(items, id_key, prefix):
            _append_once(errors, f"{collection}_ids_invalid")
            continue
        for item in items:
            if set(item) != exact_keys:
                _append_once(errors, f"{collection}_schema_invalid")
            if item.get("owner_state", OWNER_STATE) != OWNER_STATE:
                _append_once(errors, f"{collection}_owner_invalid")

    if (
        model.get("support_requests", [{}])[0].get("pilot_candidate_id")
        != "PCAN-SYN-001"
    ):
        _append_once(errors, "support_request_candidate_ref_invalid")
    if model.get("support_requests", [{}])[0].get("scope_id") != "SCOPE-SYN-001":
        _append_once(errors, "support_request_scope_ref_invalid")
    if (
        model.get("support_cases", [{}])[0].get("support_request_id")
        != "SR-SYN-001"
    ):
        _append_once(errors, "support_case_request_ref_invalid")
    if (
        model.get("support_cases", [{}])[0].get("support_model_id")
        != "SUP-SYN-001"
    ):
        _append_once(errors, "support_case_model_ref_invalid")
    if (
        model.get("support_cases", [{}])[0].get("escalation_path_id")
        != "ESC-SYN-001"
    ):
        _append_once(errors, "support_case_escalation_ref_invalid")

    candidate = model.get("pilot_candidates", [{}])[0]
    expected_candidate_refs = {
        "scope_id": "SCOPE-SYN-001",
        "entry_criteria_ids": ["ENTRY-SYN-001"],
        "exit_criteria_ids": ["EXIT-SYN-001"],
        "stop_condition_ids": ["STOP-SYN-001"],
        "withdrawal_condition_ids": ["WITHDRAW-SYN-001"],
    }
    for key, expected in expected_candidate_refs.items():
        if candidate.get(key) != expected:
            _append_once(errors, f"pilot_candidate_{key}_invalid")

    scope = model.get("scopes", [{}])[0]
    if (scope.get("company"), scope.get("brand")) != ("汇沣电商", "BUW"):
        _append_once(errors, "scope_business_boundary_invalid")
    if scope.get("permitted_actions") != ["in_memory_evaluation"]:
        _append_once(errors, "scope_permitted_actions_invalid")
    if scope.get("excluded_actions") != [
        "external_read",
        "external_write",
        "real_pilot",
    ]:
        _append_once(errors, "scope_excluded_actions_invalid")

    entry = model.get("entry_criteria", [{}])[0]
    if (
        entry.get("required_gate_ids") != EXPECTED_GATES
        or entry.get("real_world_satisfied") is not False
    ):
        _append_once(errors, "entry_human_gate_contract_invalid")
    if (
        model.get("exit_criteria", [{}])[0].get("evaluator_may_close_real_pilot")
        is not False
    ):
        _append_once(errors, "exit_authority_invalid")
    if (
        model.get("withdrawal_conditions", [{}])[0].get("real_roles_assigned")
        is not False
    ):
        _append_once(errors, "withdrawal_real_role_invalid")

    evidence_contract = model.get("evidence_contract")
    expected_evidence_keys = {
        "evidence_bundle_id_prefix",
        "version_format",
        "required_evidence_refs",
        "content_hash_required",
        "human_acceptance_inferred",
    }
    if (
        not isinstance(evidence_contract, dict)
        or set(evidence_contract) != expected_evidence_keys
    ):
        _append_once(errors, "evidence_contract_schema_invalid")
    elif (
        evidence_contract.get("evidence_bundle_id_prefix") != "EVB-SYN-"
        or evidence_contract.get("version_format") != "semantic_version"
        or evidence_contract.get("content_hash_required") is not True
        or evidence_contract.get("human_acceptance_inferred") is not False
    ):
        _append_once(errors, "evidence_contract_value_invalid")

    if model.get("audit_contract") != {
        "record_id": "AUD-SYN-001",
        "synthetic": True,
        "persistent_store": False,
    }:
        _append_once(errors, "audit_contract_invalid")
    if model.get("decision_contract") != {
        "record_id": "DEC-SYN-001",
        "synthetic": True,
        "human_decision": None,
        "pilot_authorized": False,
    }:
        _append_once(errors, "decision_contract_invalid")
    return errors


def evaluate_eligibility(
    model: dict[str, Any],
    request: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    for error in _scan_model_forbidden(model):
        _append_once(reasons, error)
    for error in _scan_forbidden(request, ("request",)):
        _append_once(reasons, error)
    for error in _scan_forbidden(evidence_bundle, ("evidence_bundle",)):
        _append_once(reasons, error)
    for error in validate_model(model):
        _append_once(reasons, f"MODEL_{error.upper()}")
    if (
        request.get("model_version") != MODEL_VERSION
        or evidence_bundle.get("model_version") != MODEL_VERSION
    ):
        _append_once(reasons, "VERSION_MISMATCH")
    if (
        request.get("company") != "汇沣电商"
        or request.get("brand") != "BUW"
    ):
        _append_once(reasons, "BUSINESS_BOUNDARY_INVALID")
    if request.get("owner_state") != OWNER_STATE:
        _append_once(reasons, "REAL_OWNER_FORBIDDEN")
    if (
        evidence_bundle.get("synthetic") is not True
        or evidence_bundle.get("repository_controlled") is not True
    ):
        _append_once(reasons, "SYNTHETIC_PROVENANCE_INVALID")
    if evidence_bundle.get("upstream_risk_states") != EXPECTED_RISKS:
        _append_once(reasons, "UPSTREAM_RISK_STATE_INVALID")
    if (
        request.get("external_actions_performed") != []
        or evidence_bundle.get("external_actions_performed") != []
    ):
        _append_once(reasons, "EXTERNAL_ACTION_FORBIDDEN")
    if set(request) != REQUEST_KEYS:
        _append_once(reasons, "REQUEST_SCHEMA_INVALID")
    for field, rule in ID_RULES.items():
        if not isinstance(request.get(field), str) or not rule.fullmatch(
            request[field]
        ):
            _append_once(reasons, f"{field.upper()}_INVALID")
    if (
        evidence_bundle.get("evidence_refs")
        != model["evidence_contract"]["required_evidence_refs"]
    ):
        _append_once(reasons, "EVIDENCE_ORDER_OR_CONTENT_INVALID")
    items = evidence_bundle.get("evidence_items")
    if (
        not isinstance(items, list)
        or [item.get("evidence_id") for item in items]
        != evidence_bundle.get("evidence_refs")
    ):
        _append_once(reasons, "EVIDENCE_ITEM_ORDER_INVALID")
    else:
        for item in items:
            content = item.get("synthetic_content")
            digest = (
                hashlib.sha256(content.encode("utf-8")).hexdigest()
                if isinstance(content, str)
                else None
            )
            if (
                item.get("hash_basis") != "synthetic_content_utf8"
                or item.get("content_sha256") != digest
            ):
                _append_once(reasons, "EVIDENCE_HASH_INVALID")
            if item.get("human_accepted") is not False:
                _append_once(reasons, "HUMAN_ACCEPTANCE_INFERENCE_FORBIDDEN")
    result = "denied" if reasons else "needs_human_governance"
    gates = [] if reasons else [gate["gate_id"] for gate in model["human_gates"]]
    core = {
        "result": result,
        "model_version": MODEL_VERSION,
        "support_request_id": request.get("support_request_id"),
        "support_case_id": request.get("support_case_id"),
        "pilot_candidate_id": request.get("pilot_candidate_id"),
        "scope_id": request.get("scope_id"),
        "reason_codes": reasons,
        "required_human_gates": gates,
        "evidence_refs": list(evidence_bundle.get("evidence_refs", [])),
        "upstream_risk_states": dict(
            evidence_bundle.get("upstream_risk_states", {})
        ),
        "external_actions_performed": [],
    }
    audit = {**core, "record_id": "AUD-SYN-001", "synthetic": True}
    decision = {
        **core,
        "record_id": "DEC-SYN-001",
        "synthetic": True,
        "human_decision": None,
    }
    return {**core, "audit_record": audit, "decision_record": decision}


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    model = load_repository_yaml(root, MODEL_PATH)
    for error in validate_model(model):
        _append_once(errors, error)
    mapping = load_repository_yaml(root, MAPPING_PATH)
    matrix = load_repository_yaml(root, MATRIX_PATH)
    if [item.get("risk_id") for item in mapping.get("stage10_risks", [])] != [
        f"PR-RISK-{n:03d}" for n in range(1, 11)
    ]:
        _append_once(errors, "stage10_risk_order_invalid")
    expected_states = ["blocked"] * 8 + ["open", "open"]
    if [item.get("state") for item in mapping.get("stage10_risks", [])] != expected_states:
        _append_once(errors, "stage10_risk_state_invalid")
    if any(
        item.get("accepted") is not False
        or item.get("overridden_by_stage14") is not False
        or item.get("owner_state") != OWNER_STATE
        for item in mapping.get("stage10_risks", [])
    ):
        _append_once(errors, "stage10_risk_authority_invalid")
    if matrix.get("authority_ceiling") != {
        "pilot_authorized": False,
        "release_authorized": False,
        "production_action_allowed": False,
    }:
        _append_once(errors, "acceptance_authority_ceiling_invalid")
    requirements = matrix.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        _append_once(errors, "acceptance_requirements_invalid")
    elif any(
        row.get("synthetic_evidence_required") is not True
        or row.get("human_acceptance_required") is not True
        for row in requirements
    ):
        _append_once(errors, "acceptance_requirement_authority_invalid")
    return errors
