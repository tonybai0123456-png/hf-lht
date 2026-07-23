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
ALLOWED_YAML_PATHS = frozenset({MODEL_PATH, FIXTURE_PATH})
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
    for error in validate_model(model):
        _append_once(reasons, f"MODEL_{error.upper()}")
    if (
        request.get("model_version") != MODEL_VERSION
        or evidence_bundle.get("model_version") != MODEL_VERSION
    ):
        _append_once(reasons, "VERSION_MISMATCH")
    if (request.get("company"), request.get("brand")) != ("汇沣电商", "BUW"):
        _append_once(reasons, "BUSINESS_BOUNDARY_INVALID")
    if request.get("owner_state") != OWNER_STATE:
        _append_once(reasons, "REAL_OWNER_FORBIDDEN")
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
