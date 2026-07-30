from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any, Callable

import yaml
from yaml.tokens import AliasToken, AnchorToken, ScalarToken


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
)
MAPPING_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml"
)
MATRIX_PATH = Path(
    "Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml"
)
FIXTURE_PATH = Path(
    "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml"
)
POLICY_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Integration-v1.md")
GUIDE_PATH = Path("Tests/AIOS-Nonproduction-Readiness-Validation.md")
WORKFLOW_PATH = Path(".github/workflows/validate-aios-nonproduction-readiness.yml")
STAGE_REGISTRY_PATH = Path("Governance/AIOS-Stage-Registry.md")
PROJECT_REGISTRY_PATH = Path("Governance/AIOS-Project-Registry.md")

ALLOWED_YAML_PATHS = frozenset(
    {MODEL_PATH, MAPPING_PATH, MATRIX_PATH, FIXTURE_PATH}
)
RISK_IDS = tuple(f"PR-RISK-{number:03d}" for number in range(1, 11))
COMPONENT_IDS = (
    "CMP-ENVIRONMENT",
    "CMP-IDENTITY",
    "CMP-DATA",
    "CMP-EVIDENCE",
    "CMP-OBSERVATION",
    "CMP-RECOVERY",
    "CMP-INCIDENT",
    "CMP-SUPPORT",
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
GATE_IDS = (
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
ACCEPTANCE_IDS = (
    "AC-ENVIRONMENT",
    "AC-IDENTITY",
    "AC-DATA",
    "AC-EVIDENCE",
    "AC-OBSERVATION",
    "AC-RECOVERY",
    "AC-INCIDENT",
    "AC-SUPPORT",
    "AC-RISK-MAPPING",
    "AC-AUTHORITY",
)
FALSE_CLAIMS = {
    "risk_accepted": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
}
ALLOWED_EMPTY_CAPABILITY_PATHS = frozenset(
    {
        "$.environment.external_endpoints",
        "$.environment.connectors",
        "$.environment.credentials",
    }
)
CAPABILITY_KEYS = frozenset(
    {
        "api_key",
        "api_keys",
        "connector",
        "connectors",
        "credential",
        "credentials",
        "database",
        "databases",
        "endpoint",
        "endpoints",
        "external_endpoint",
        "external_endpoints",
        "password",
        "passwords",
        "secret",
        "secrets",
        "token",
        "tokens",
        "webhook",
        "webhooks",
    }
)
AUTHORITY_LIKE_VALUES = frozenset(
    {
        "accepted",
        "approved",
        "eligible",
        "go",
        "pilot_authorized",
        "pilot_ready",
        "proceed",
        "production_ready",
        "ready",
        "released",
    }
)


def _error(path: str, code: str) -> str:
    return f"{path}:{code}"


def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [_error(path, "mapping_required")]
    if tuple(value.keys()) != expected:
        return [_error(path, "exact_keys_required")]
    return []


def _ordered_ids(
    records: Any,
    key: str,
    expected: tuple[str, ...],
    path: str,
) -> list[str]:
    if not isinstance(records, list):
        return [_error(path, "list_required")]
    identifiers = [
        record.get(key) if isinstance(record, dict) else None for record in records
    ]
    if tuple(identifiers) != expected or len(set(identifiers)) != len(identifiers):
        return [_error(path, "ordered_unique_ids_required")]
    return []


def _is_exact_bool(value: Any, expected: bool) -> bool:
    return type(value) is bool and value is expected


def _scan_capabilities(
    value: Any,
    path: str = "$",
    active: set[int] | None = None,
) -> list[str]:
    active = set() if active is None else active
    if isinstance(value, (dict, list)):
        identity = id(value)
        if identity in active:
            return [_error(path, "cyclic_structure")]
        active.add(identity)

    errors: list[str] = []
    try:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                child_path = f"{path}.{key_text}"
                normalized = key_text.strip().lower()
                if normalized in CAPABILITY_KEYS:
                    if (
                        child_path in ALLOWED_EMPTY_CAPABILITY_PATHS
                        and type(child) is list
                        and child == []
                    ):
                        continue
                    errors.append(_error(child_path, "forbidden_capability"))
                errors.extend(_scan_capabilities(child, child_path, active))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                errors.extend(
                    _scan_capabilities(child, f"{path}[{index}]", active)
                )
        elif isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in AUTHORITY_LIKE_VALUES:
                errors.append(_error(path, "authority_like_value"))
            if normalized.startswith(
                (
                    "http://",
                    "https://",
                    "mysql://",
                    "postgres://",
                    "redis://",
                )
            ):
                errors.append(_error(path, "external_locator"))
    finally:
        if isinstance(value, (dict, list)):
            active.discard(id(value))
    return errors


def load_controlled_yaml_text(path: Path, text: str) -> dict[str, Any]:
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


def load_repository_yaml(
    root: Path,
    relative_path: Path,
) -> dict[str, Any]:
    if relative_path.is_absolute() or relative_path not in ALLOWED_YAML_PATHS:
        raise ValueError("path is not allowlisted")
    resolved_root = root.resolve()
    candidate = resolved_root / relative_path
    if candidate.is_symlink():
        raise ValueError("symlink is not allowed")
    resolved = candidate.resolve()
    if resolved_root not in resolved.parents:
        raise ValueError("path escapes repository")
    text = candidate.read_text(encoding="utf-8")
    return load_controlled_yaml_text(relative_path, text)


def _validate_model_impl(model: Any) -> list[str]:
    expected_keys = (
        "model_version",
        "stage",
        "stage_id",
        "allowed_scope",
        "excluded_entities",
        "environment_mode",
        "allowed_results",
        "authority_ceiling",
        "real_owner",
        "stage10_posture",
        "components",
        "risks",
        "human_gates",
        "claims",
        "external_actions_performed",
    )
    errors = _exact_keys(model, expected_keys, "$")
    if errors:
        return errors

    if model["model_version"] != "nonproduction_readiness_integration/v1":
        errors.append(_error("$.model_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01":
        errors.append(_error("$.stage", "invalid"))
    if model["allowed_scope"] != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.allowed_scope", "invalid"))
    if model["excluded_entities"] != ["PC", "六合通"]:
        errors.append(_error("$.excluded_entities", "invalid"))
    if model["environment_mode"] != "local_synthetic_disposable":
        errors.append(_error("$.environment_mode", "invalid"))
    if model["allowed_results"] != ["denied", "needs_human_governance"]:
        errors.append(_error("$.allowed_results", "invalid"))
    if model["authority_ceiling"] != "needs_human_governance":
        errors.append(_error("$.authority_ceiling", "invalid"))
    if model["real_owner"] != "unassigned / governance decision required":
        errors.append(_error("$.real_owner", "invalid"))
    if model["stage10_posture"] != "BLOCKED / NO-GO":
        errors.append(_error("$.stage10_posture", "invalid"))

    components = model["components"]
    errors.extend(
        _ordered_ids(components, "component_id", COMPONENT_IDS, "$.components")
    )
    if isinstance(components, list):
        expected_pairs = list(zip(COMPONENT_IDS, EVIDENCE_IDS))
        actual_pairs = [
            (
                record.get("component_id"),
                record.get("evidence_id"),
            )
            if isinstance(record, dict)
            else (None, None)
            for record in components
        ]
        if actual_pairs != expected_pairs:
            errors.append(_error("$.components", "evidence_alignment_required"))
        for index, record in enumerate(components):
            if (
                not isinstance(record, dict)
                or tuple(record.keys()) != ("component_id", "evidence_id")
            ):
                errors.append(
                    _error(
                        f"$.components[{index}]",
                        "closed_component_record_required",
                    )
                )

    risks = model["risks"]
    errors.extend(_ordered_ids(risks, "risk_id", RISK_IDS, "$.risks"))
    if isinstance(risks, list):
        for index, risk in enumerate(risks):
            if (
                not isinstance(risk, dict)
                or tuple(risk.keys()) != ("risk_id", "state", "owner")
            ):
                errors.append(
                    _error(f"$.risks[{index}]", "closed_risk_record_required")
                )
            elif (
                risk["state"] != "open_blocked_unaccepted"
                or risk["owner"] != "unassigned / governance decision required"
            ):
                errors.append(
                    _error(f"$.risks[{index}]", "risk_must_remain_blocked")
                )

    gates = model["human_gates"]
    errors.extend(_ordered_ids(gates, "gate_id", GATE_IDS, "$.human_gates"))
    if isinstance(gates, list):
        for index, gate in enumerate(gates):
            if (
                not isinstance(gate, dict)
                or tuple(gate.keys()) != ("gate_id", "authorized")
                or not _is_exact_bool(gate.get("authorized"), False)
            ):
                errors.append(
                    _error(
                        f"$.human_gates[{index}]",
                        "unauthorized_gate_required",
                    )
                )

    claims = model["claims"]
    if claims != FALSE_CLAIMS or not all(
        type(value) is bool for value in claims.values()
    ):
        errors.append(_error("$.claims", "exact_false_claims_required"))
    if model["external_actions_performed"] != []:
        errors.append(_error("$.external_actions_performed", "must_be_empty"))
    errors.extend(_scan_capabilities(model))
    return list(dict.fromkeys(errors))


def _validate_fixture_impl(fixture: Any) -> list[str]:
    expected_keys = (
        "fixture_version",
        "scenario_id",
        "scope",
        "environment",
        "identity",
        "data_contract",
        "component_results",
        "risk_states",
        "required_human_gates",
        "requested_external_actions",
        "claims",
        "evidence_store",
        "observation",
        "recovery",
        "incident_tabletop",
        "support_handoff",
    )
    errors = _exact_keys(fixture, expected_keys, "$")
    if errors:
        return errors

    if fixture["fixture_version"] != "nonproduction_readiness_fixture/v1":
        errors.append(_error("$.fixture_version", "invalid"))
    if fixture["scenario_id"] != "NR-SYNTHETIC-LOCAL-001":
        errors.append(_error("$.scenario_id", "invalid"))
    if fixture["scope"] != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append(_error("$.scope", "invalid"))
    if fixture["environment"] != {
        "mode": "local_synthetic_disposable",
        "external_endpoints": [],
        "connectors": [],
        "credentials": [],
    }:
        errors.append(_error("$.environment", "invalid"))
    if fixture["identity"] != {
        "principal_id": "synthetic-principal-nr-001",
        "simulated": True,
        "permissions": [
            "read_synthetic_fixture",
            "write_task_local_evidence",
        ],
    }:
        errors.append(_error("$.identity", "invalid"))
    if fixture["data_contract"] != {
        "provenance": "synthetic",
        "classification": "synthetic_non_personal",
        "retention": "task_local_until_cleanup",
        "deletion": "deterministic_cleanup_required",
    }:
        errors.append(_error("$.data_contract", "invalid"))

    component_results = fixture["component_results"]
    errors.extend(
        _ordered_ids(
            component_results,
            "component_id",
            COMPONENT_IDS,
            "$.component_results",
        )
    )
    if isinstance(component_results, list):
        expected_pairs = list(zip(COMPONENT_IDS, EVIDENCE_IDS))
        actual_pairs = [
            (
                record.get("component_id"),
                record.get("evidence_id"),
            )
            if isinstance(record, dict)
            else (None, None)
            for record in component_results
        ]
        if actual_pairs != expected_pairs:
            errors.append(
                _error("$.component_results", "evidence_alignment_required")
            )
        for index, record in enumerate(component_results):
            if (
                not isinstance(record, dict)
                or tuple(record.keys())
                != ("component_id", "status", "evidence_id")
                or record.get("status") != "passed"
            ):
                errors.append(
                    _error(
                        f"$.component_results[{index}]",
                        "closed_pass_record_required",
                    )
                )

    risk_states = fixture["risk_states"]
    if (
        not isinstance(risk_states, dict)
        or tuple(risk_states.keys()) != RISK_IDS
        or tuple(risk_states.values())
        != tuple("open_blocked_unaccepted" for _ in RISK_IDS)
    ):
        errors.append(_error("$.risk_states", "blocked_risks_required"))
    if fixture["required_human_gates"] != list(GATE_IDS):
        errors.append(_error("$.required_human_gates", "ordered_gates_required"))
    if fixture["requested_external_actions"] != []:
        errors.append(_error("$.requested_external_actions", "must_be_empty"))
    claims = fixture["claims"]
    if (
        not isinstance(claims, dict)
        or claims != FALSE_CLAIMS
        or not all(type(value) is bool for value in claims.values())
    ):
        errors.append(_error("$.claims", "exact_false_claims_required"))

    store = fixture["evidence_store"]
    if (
        not isinstance(store, dict)
        or tuple(store.keys()) != ("mode", "records")
        or store.get("mode") != "task_local_append_only"
    ):
        errors.append(_error("$.evidence_store", "invalid"))
    else:
        records = store.get("records")
        if not isinstance(records, list):
            errors.append(_error("$.evidence_store.records", "list_required"))
        else:
            expected_payloads = ("environment", "evidence", "observation")
            expected_record_ids = ("AUDIT-001", "AUDIT-002", "AUDIT-003")
            expected_evidence = (
                "EV-ENVIRONMENT",
                "EV-EVIDENCE",
                "EV-OBSERVATION",
            )
            if [record.get("sequence") if isinstance(record, dict) else None
                for record in records] != [1, 2, 3]:
                errors.append(
                    _error(
                        "$.evidence_store.records",
                        "append_only_sequence_required",
                    )
                )
            for index, payload in enumerate(expected_payloads):
                if index >= len(records) or not isinstance(records[index], dict):
                    errors.append(
                        _error(
                            f"$.evidence_store.records[{index}]",
                            "closed_record_required",
                        )
                    )
                    continue
                record = records[index]
                expected_checksum = hashlib.sha256(
                    payload.encode("utf-8")
                ).hexdigest()
                if (
                    tuple(record.keys())
                    != ("sequence", "record_id", "evidence_id", "checksum")
                    or record["record_id"] != expected_record_ids[index]
                    or record["evidence_id"] != expected_evidence[index]
                    or record["checksum"] != expected_checksum
                ):
                    errors.append(
                        _error(
                            f"$.evidence_store.records[{index}]",
                            "invalid",
                        )
                    )
            if len(records) != 3:
                errors.append(
                    _error("$.evidence_store.records", "exact_length_required")
                )

    if fixture["observation"] != {
        "mode": "local_decision_only",
        "metric_ids": [
            "METRIC-LOCAL-VALIDATION",
            "METRIC-LOCAL-DENIAL",
        ],
        "alert_decision": "synthetic_no_external_delivery",
        "paging": False,
        "ticket_created": False,
        "external_delivery": False,
    }:
        errors.append(_error("$.observation", "invalid"))

    expected_state = hashlib.sha256(b"synthetic-state").hexdigest()
    if fixture["recovery"] != {
        "snapshot_id": "SYNTHETIC-SNAPSHOT-001",
        "rollback_trigger": "synthetic_validation_failure",
        "pre_restore_checksum": expected_state,
        "post_restore_checksum": expected_state,
        "restore_verified": True,
        "cleanup_verified": True,
    }:
        errors.append(_error("$.recovery", "invalid"))
    if fixture["incident_tabletop"] != {
        "scenario_id": "SYNTHETIC-INCIDENT-001",
        "severity": "synthetic_sev2",
        "containment": "local_fixture_isolation",
        "communications": "none_external",
        "real_incident_declared": False,
    }:
        errors.append(_error("$.incident_tabletop", "invalid"))
    if fixture["support_handoff"] != {
        "case_id": "SYNTHETIC-CASE-001",
        "owner": "unassigned / governance decision required",
        "route": "abstract_support_role",
        "ticket_created": False,
        "sla_committed": False,
    }:
        errors.append(_error("$.support_handoff", "invalid"))
    errors.extend(_scan_capabilities(fixture))
    return list(dict.fromkeys(errors))


def _fail_closed(
    validator: Callable[[Any], list[str]],
    value: Any,
    path: str,
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


def validate_model(model: Any) -> list[str]:
    return _fail_closed(_validate_model_impl, model, "$model")


def validate_fixture(fixture: Any) -> list[str]:
    return _fail_closed(_validate_fixture_impl, fixture, "$fixture")


def evaluate_nonproduction_readiness(
    model: Any,
    fixture: Any,
) -> dict[str, Any]:
    errors = list(
        dict.fromkeys(
            [
                *validate_model(model),
                *validate_fixture(fixture),
            ]
        )
    )
    denied = bool(errors)
    return {
        "result": "denied" if denied else "needs_human_governance",
        "reason_codes": (
            [f"VALIDATION_ERROR:{error}" for error in errors] if denied else []
        ),
        "evidence_refs": [] if denied else list(EVIDENCE_IDS),
        "required_human_gates": list(GATE_IDS),
        "risk_states": {
            risk_id: "open_blocked_unaccepted" for risk_id in RISK_IDS
        },
        "external_actions_performed": [],
        "claims": dict(FALSE_CLAIMS),
    }


def _validate_mapping(mapping: Any) -> list[str]:
    errors = _exact_keys(
        mapping,
        (
            "mapping_version",
            "stage10_posture",
            "risk_mappings",
            "archived_dependencies",
        ),
        "$mapping",
    )
    if errors:
        return errors
    if (
        mapping["mapping_version"]
        != "nonproduction_readiness_stage10_14_mapping/v1"
        or mapping["stage10_posture"] != "BLOCKED / NO-GO"
    ):
        errors.append(_error("$mapping", "header_invalid"))
    risk_mappings = mapping["risk_mappings"]
    errors.extend(
        _ordered_ids(
            risk_mappings,
            "risk_id",
            RISK_IDS,
            "$mapping.risk_mappings",
        )
    )
    if isinstance(risk_mappings, list):
        for index, record in enumerate(risk_mappings):
            if (
                not isinstance(record, dict)
                or tuple(record.keys()) != ("risk_id", "evidence_ids", "state")
                or record.get("state") != "open_blocked_unaccepted"
                or not isinstance(record.get("evidence_ids"), list)
                or not record.get("evidence_ids")
                or any(
                    evidence_id not in EVIDENCE_IDS
                    for evidence_id in record.get("evidence_ids", [])
                )
            ):
                errors.append(
                    _error(
                        f"$mapping.risk_mappings[{index}]",
                        "closed_blocked_record_required",
                    )
                )
    expected_dependencies = [
        {
            "stage": number,
            "status": "Archived",
            "interpretation": "design_evidence_only",
        }
        for number in range(11, 15)
    ]
    if mapping["archived_dependencies"] != expected_dependencies:
        errors.append(_error("$mapping.archived_dependencies", "invalid"))
    errors.extend(_scan_capabilities(mapping, "$mapping"))
    return list(dict.fromkeys(errors))


def _validate_matrix(matrix: Any) -> list[str]:
    errors = _exact_keys(
        matrix,
        ("matrix_version", "requirements", "authority_claims"),
        "$matrix",
    )
    if errors:
        return errors
    if matrix["matrix_version"] != "nonproduction_readiness_acceptance/v1":
        errors.append(_error("$matrix.matrix_version", "invalid"))
    requirements = matrix["requirements"]
    errors.extend(
        _ordered_ids(
            requirements,
            "requirement_id",
            ACCEPTANCE_IDS,
            "$matrix.requirements",
        )
    )
    if isinstance(requirements, list):
        for index, record in enumerate(requirements):
            if (
                not isinstance(record, dict)
                or tuple(record.keys())
                != (
                    "requirement_id",
                    "test_ids",
                    "evidence_ids",
                    "local_synthetic_proof",
                    "real_world_authority",
                )
                or not isinstance(record.get("test_ids"), list)
                or not record.get("test_ids")
                or not isinstance(record.get("evidence_ids"), list)
                or not _is_exact_bool(record.get("local_synthetic_proof"), True)
                or not _is_exact_bool(record.get("real_world_authority"), False)
                or any(
                    evidence_id not in EVIDENCE_IDS
                    for evidence_id in record.get("evidence_ids", [])
                )
            ):
                errors.append(
                    _error(
                        f"$matrix.requirements[{index}]",
                        "closed_requirement_record_required",
                    )
                )
    if matrix["authority_claims"] != FALSE_CLAIMS:
        errors.append(
            _error("$matrix.authority_claims", "exact_false_claims_required")
        )
    errors.extend(_scan_capabilities(matrix, "$matrix"))
    return list(dict.fromkeys(errors))


def _load_repository_asset(
    root: Path,
    relative_path: Path,
    label: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        return load_repository_yaml(root, relative_path), []
    except Exception as exc:
        return None, [_error(label, f"load_error:{type(exc).__name__}")]


def validate_repository(root: Path) -> list[str]:
    model, model_load_errors = _load_repository_asset(
        root, MODEL_PATH, "$repository.model"
    )
    fixture, fixture_load_errors = _load_repository_asset(
        root, FIXTURE_PATH, "$repository.fixture"
    )
    mapping, mapping_load_errors = _load_repository_asset(
        root, MAPPING_PATH, "$repository.mapping"
    )
    matrix, matrix_load_errors = _load_repository_asset(
        root, MATRIX_PATH, "$repository.matrix"
    )
    errors = [
        *model_load_errors,
        *fixture_load_errors,
        *mapping_load_errors,
        *matrix_load_errors,
    ]
    if model is not None:
        errors.extend(validate_model(model))
    if fixture is not None:
        errors.extend(validate_fixture(fixture))
    if mapping is not None:
        errors.extend(_fail_closed(_validate_mapping, mapping, "$mapping"))
    if matrix is not None:
        errors.extend(_fail_closed(_validate_matrix, matrix, "$matrix"))

    if model is not None and fixture is not None:
        model_evidence = [
            record.get("evidence_id")
            for record in model.get("components", [])
            if isinstance(record, dict)
        ]
        fixture_evidence = [
            record.get("evidence_id")
            for record in fixture.get("component_results", [])
            if isinstance(record, dict)
        ]
        if tuple(model_evidence) != EVIDENCE_IDS:
            errors.append(_error("$cross.model_evidence", "identity_mismatch"))
        if tuple(fixture_evidence) != EVIDENCE_IDS:
            errors.append(_error("$cross.fixture_evidence", "identity_mismatch"))
    if mapping is not None:
        mapping_risks = [
            record.get("risk_id")
            for record in mapping.get("risk_mappings", [])
            if isinstance(record, dict)
        ]
        if tuple(mapping_risks) != RISK_IDS:
            errors.append(_error("$cross.risks", "identity_mismatch"))

    text_assets = {
        "$policy": (
            POLICY_PATH,
            (
                "Business loop",
                "Core objects",
                "Data flow",
                "Operators",
                "AI and human judgment boundary",
                "Proof of operation",
                "Authority ceiling",
                "Component contracts",
                "Risk mapping",
                "Stop and withdrawal",
                "Lifecycle",
                "BLOCKED / NO-GO",
                "needs_human_governance",
                "汇沣电商",
                "BUW",
                "PC",
                "六合通",
            ),
        ),
        "$guide": (
            GUIDE_PATH,
            (
                "AIOS non-production readiness validation PASSED",
                "python -m pip install --requirement requirements-dev.txt",
                "python3 Tests/validate_aios_nonproduction_readiness.py",
                "python3 -m unittest Tests.test_nonproduction_readiness -v",
                "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
                "does not authorize deployment",
            ),
        ),
        "$workflow": (
            WORKFLOW_PATH,
            (
                "pull_request:",
                "permissions:\n  contents: read",
                "persist-credentials: false",
                "python -m pip install --requirement requirements-dev.txt",
                "python3 Tests/validate_aios_nonproduction_readiness.py",
                "python3 -m unittest Tests.test_nonproduction_readiness -v",
                "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
                "python3 Tests/validate_aios_workflow_schema.py",
                "python3 -m compileall -q Runtime Tests",
            ),
        ),
    }
    for label, (relative_path, tokens) in text_assets.items():
        try:
            content = (root / relative_path).read_text(encoding="utf-8")
        except Exception as exc:
            errors.append(_error(label, f"load_error:{type(exc).__name__}"))
            continue
        for token in tokens:
            if token not in content:
                errors.append(_error(label, f"missing:{token}"))
        if label == "$workflow":
            for forbidden in (
                "push:",
                "workflow_dispatch:",
                "contents: write",
                "pull-requests: write",
                "issues: write",
                "git push",
                "curl ",
                "wget ",
                "secrets.",
                "deployment",
            ):
                if forbidden in content:
                    errors.append(_error(label, f"forbidden:{forbidden}"))

    try:
        stage_registry = (root / STAGE_REGISTRY_PATH).read_text(encoding="utf-8")
        stage10 = next(
            (
                line
                for line in stage_registry.splitlines()
                if line.startswith("| 10 |")
            ),
            "",
        )
        stage15 = next(
            (
                line
                for line in stage_registry.splitlines()
                if line.startswith("| 15 |")
            ),
            "",
        )
        if "BLOCKED / NO-GO" not in stage10:
            errors.append(_error("$registry.stage10", "posture_not_frozen"))
        if not stage15:
            errors.append(_error("$registry.stage15", "missing"))
        if "| Reviewed |" in stage15 or "| Archived |" in stage15:
            errors.append(_error("$registry.stage15", "authority_exceeded"))
    except Exception as exc:
        errors.append(
            _error("$registry.stage", f"load_error:{type(exc).__name__}")
        )

    return list(dict.fromkeys(errors))


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS non-production readiness validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    model = load_repository_yaml(ROOT, MODEL_PATH)
    fixture = load_repository_yaml(ROOT, FIXTURE_PATH)
    decision = evaluate_nonproduction_readiness(model, fixture)
    if decision["result"] != "needs_human_governance":
        print("AIOS non-production readiness validation FAILED")
        print(f"- $decision:unexpected_result:{decision['result']}")
        return 1
    print("AIOS non-production readiness validation PASSED")
    print(f"result={decision['result']}")
    print("external_actions_performed=[]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
