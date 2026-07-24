# Non-production Readiness Remediation and Integration Implementation Plan

> **For agentic workers:** Execute this plan task-by-task only after independent human approval of the exact plan head, assignment of one dedicated Execution Task, and assignment of one implementation branch.

> **Governance override:** This document is review material. Stage 15 remains `Planned`; no implementation, real pilot, production, risk acceptance, owner assignment, permission change, external write, merge, publication, archive, Issue closure, or Stage 16 is authorized by this plan.

**Goal:** Build a repository-contained, local, synthetic, disposable proof for company `汇沣电商`, brand `BUW`, while excluding `PC` and `六合通`; map evidence to `PR-RISK-001` through `PR-RISK-010`; fail closed; and return at most `needs_human_governance`.

**Architecture:** Four allowlisted YAML mappings are loaded with `yaml.safe_load`. A closed validator checks identity, components, risks, gates, evidence, recovery, incident and support records. A pure evaluator performs no I/O and returns only `denied` or `needs_human_governance`. A repository validator cross-checks YAML, policy, validation guide and pull-request-only read-only CI.

**Tech Stack:** Python 3.12 standard library, PyYAML from `requirements-dev.txt`, `unittest`, YAML, Markdown and GitHub Actions.

## Global Constraints

- Company boundary: `汇沣电商`; brand boundary: `BUW`.
- Excluded: `PC`, `六合通`, aliases, wildcards, mixed scopes and unknown identities.
- Inputs are repository-controlled synthetic data only.
- Stage 10 remains `BLOCKED / NO-GO`; Stages 11–14 remain `Archived`.
- All ten risks remain `open_blocked_unaccepted`; owner remains `unassigned / governance decision required`.
- All twelve human gates remain unauthorized.
- Invalid input returns `denied`; valid synthetic input returns `needs_human_governance`.
- `risk_accepted`, `pilot_authorized`, `production_ready` and `release_authorized` are always false.
- `external_actions_performed` is always `[]`.
- The evaluator may not read files, write files, access network, environment, clock, randomness, subprocesses or connectors.
- Implementation stops at Draft PR + Stage 15 `Reported` + Mandatory Return.
- `Reported` does not mean `Reviewed`; `Reviewed` does not mean merged, published or `Archived`.

## Exact file structure and single responsibilities

Create:

- `Governance/AIOS-Nonproduction-Readiness-Integration-v1.md`
- `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml`
- `Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml`
- `Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml`
- `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`
- `Tests/validate_aios_nonproduction_readiness.py`
- `Tests/test_nonproduction_readiness.py`
- `Tests/AIOS-Nonproduction-Readiness-Validation.md`
- `.github/workflows/validate-aios-nonproduction-readiness.yml`

Modify only at implementation completion:

- `Governance/AIOS-Stage-Registry.md`
- `Governance/AIOS-Project-Registry.md`
- `Tests/test_project_governance.py`
- lifecycle compatibility tests only when their current assertions require the Stage 15 `Reported` transition.

## Exact public interfaces

```python
def load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]: ...
def validate_model(model: dict[str, Any]) -> list[str]: ...
def validate_fixture(fixture: dict[str, Any]) -> list[str]: ...
def evaluate_nonproduction_readiness(
    model: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]: ...
def validate_repository(root: Path) -> list[str]: ...
```

## Closed schemas and constants

The implementation must use these exact ordered identifiers:

```python
RISK_IDS = tuple(f"PR-RISK-{n:03d}" for n in range(1, 11))
COMPONENT_IDS = (
    "CMP-ENVIRONMENT", "CMP-IDENTITY", "CMP-DATA", "CMP-EVIDENCE",
    "CMP-OBSERVATION", "CMP-RECOVERY", "CMP-INCIDENT", "CMP-SUPPORT",
)
EVIDENCE_IDS = (
    "EV-ENVIRONMENT", "EV-IDENTITY", "EV-DATA", "EV-EVIDENCE",
    "EV-OBSERVATION", "EV-RECOVERY", "EV-INCIDENT", "EV-SUPPORT",
)
GATE_IDS = (
    "HG-SPEC-APPROVAL", "HG-PLAN-APPROVAL", "HG-EXECUTION-ASSIGNMENT",
    "HG-IMPLEMENTATION-EVIDENCE", "HG-NAMED-OWNER", "HG-ARCH-SECURITY",
    "HG-PRIVACY-DATA", "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
    "HG-RISK-DISPOSITION", "HG-PILOT-SCOPE", "HG-PILOT-EVIDENCE", "HG-RELEASE",
)
```

The model, fixture, mapping and matrix are closed records: exact keys only, exact types, exact ordered IDs, no aliases, no YAML merge keys, no additional fields, no truthy substitutes for booleans, and no authority-like values.

## Task 1: Pin execution provenance and create the failing test scaffold

**Files**

- Create: `Tests/test_nonproduction_readiness.py`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Loads `Tests/validate_aios_nonproduction_readiness.py` dynamically.
- Pins all public interfaces and exact paths.

- [ ] Record the separately approved execution assignment and clean starting tree.

```bash
test -n "$STAGE15_EXECUTION_TASK"
test -n "$STAGE15_IMPLEMENTATION_BRANCH"
test "$(git branch --show-current)" = "$STAGE15_IMPLEMENTATION_BRANCH"
git status --porcelain
git rev-parse HEAD
git rev-parse HEAD^{tree}
```

Expected: both assignment variables are non-empty, branch matches, status is empty, and exact head/tree are printed.

- [ ] Create the initial failing tests with complete imports and helpers.

```python
from __future__ import annotations
import ast
import copy
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "Tests/validate_aios_nonproduction_readiness.py"
MODEL = ROOT / "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
FIXTURE = ROOT / "Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml"

def load_validator():
    spec = importlib.util.spec_from_file_location("nr_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

class NonproductionReadinessTests(unittest.TestCase):
    def test_public_interfaces_exist(self):
        validator = load_validator()
        for name in (
            "load_repository_yaml", "validate_model", "validate_fixture",
            "evaluate_nonproduction_readiness", "validate_repository",
        ):
            self.assertTrue(callable(getattr(validator, name)))

    def test_model_and_fixture_are_valid(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        fixture = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_model(model))
        self.assertEqual([], validator.validate_fixture(fixture))
```

- [ ] Run RED and commit only the failing scaffold.

```bash
python3 -m unittest Tests.test_nonproduction_readiness -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): pin closed readiness interfaces"
```

Expected: tests fail because validator and controlled assets do not yet exist; commit contains only the test scaffold.

## Task 2: Implement the allowlisted loader and complete validator

**Files**

- Create: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Implements all five public functions.
- Produces stable ordered `path:code` errors.

- [ ] Create the complete validator below; do not leave prose-only helper steps.

```python
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any
import hashlib
import sys
import yaml

MODEL_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml")
MAPPING_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml")
MATRIX_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml")
FIXTURE_PATH = Path("Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml")
POLICY_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Integration-v1.md")
GUIDE_PATH = Path("Tests/AIOS-Nonproduction-Readiness-Validation.md")
WORKFLOW_PATH = Path(".github/workflows/validate-aios-nonproduction-readiness.yml")
ALLOWED_YAML_PATHS = frozenset({MODEL_PATH, MAPPING_PATH, MATRIX_PATH, FIXTURE_PATH})

RISK_IDS = tuple(f"PR-RISK-{n:03d}" for n in range(1, 11))
COMPONENT_IDS = (
    "CMP-ENVIRONMENT", "CMP-IDENTITY", "CMP-DATA", "CMP-EVIDENCE",
    "CMP-OBSERVATION", "CMP-RECOVERY", "CMP-INCIDENT", "CMP-SUPPORT",
)
EVIDENCE_IDS = (
    "EV-ENVIRONMENT", "EV-IDENTITY", "EV-DATA", "EV-EVIDENCE",
    "EV-OBSERVATION", "EV-RECOVERY", "EV-INCIDENT", "EV-SUPPORT",
)
GATE_IDS = (
    "HG-SPEC-APPROVAL", "HG-PLAN-APPROVAL", "HG-EXECUTION-ASSIGNMENT",
    "HG-IMPLEMENTATION-EVIDENCE", "HG-NAMED-OWNER", "HG-ARCH-SECURITY",
    "HG-PRIVACY-DATA", "HG-OPS-RECOVERY-INCIDENT-SUPPORT",
    "HG-RISK-DISPOSITION", "HG-PILOT-SCOPE", "HG-PILOT-EVIDENCE", "HG-RELEASE",
)
FALSE_CLAIMS = {
    "risk_accepted": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
}
FORBIDDEN_KEYS = frozenset({
    "credential", "secret", "secrets", "password", "token",
    "api_key", "endpoint", "database", "connector", "webhook",
})
FORBIDDEN_VALUES = frozenset({
    "ready", "approved", "accepted", "go", "eligible", "proceed",
    "pilot_ready", "pilot_authorized", "production_ready", "released",
})

def _error(path: str, code: str) -> str:
    return f"{path}:{code}"

def _exact_keys(value: Any, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(value, dict):
        return [_error(path, "mapping_required")]
    return [] if tuple(value.keys()) == expected else [_error(path, "exact_keys_required")]

def _ordered_ids(records: Any, key: str, expected: tuple[str, ...], path: str) -> list[str]:
    if not isinstance(records, list):
        return [_error(path, "list_required")]
    ids = [item.get(key) if isinstance(item, dict) else None for item in records]
    return [] if tuple(ids) == expected and len(set(ids)) == len(ids) else [_error(path, "ordered_unique_ids_required")]

def _is_exact_false(value: Any) -> bool:
    return type(value) is bool and value is False

def _scan_forbidden(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_KEYS:
                errors.append(_error(f"{path}.{key}", "forbidden_key"))
            errors.extend(_scan_forbidden(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_forbidden(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in FORBIDDEN_VALUES:
            errors.append(_error(path, "authority_like_value"))
        if normalized.startswith(("http://", "https://", "postgres://", "mysql://")):
            errors.append(_error(path, "external_locator"))
    return errors

def load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]:
    if relative_path.is_absolute() or relative_path not in ALLOWED_YAML_PATHS:
        raise ValueError("path is not allowlisted")
    root = root.resolve()
    candidate = root / relative_path
    if candidate.is_symlink():
        raise ValueError("symlink is not allowed")
    resolved = candidate.resolve()
    if root not in resolved.parents:
        raise ValueError("path escapes repository")
    loaded = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("controlled YAML must be a mapping")
    return loaded

def validate_model(model: dict[str, Any]) -> list[str]:
    errors = _exact_keys(model, (
        "model_version", "stage", "stage_id", "allowed_scope", "excluded_entities",
        "environment_mode", "allowed_results", "authority_ceiling", "real_owner",
        "stage10_posture", "components", "risks", "human_gates", "claims",
        "external_actions_performed",
    ), "$")
    if errors:
        return errors
    if model["model_version"] != "nonproduction_readiness_integration/v1": errors.append(_error("$.model_version", "invalid"))
    if model["stage"] != "15" or model["stage_id"] != "NR-01": errors.append(_error("$.stage", "invalid"))
    if model["allowed_scope"] != {"company": "汇沣电商", "brand": "BUW"}: errors.append(_error("$.allowed_scope", "invalid"))
    if model["excluded_entities"] != ["PC", "六合通"]: errors.append(_error("$.excluded_entities", "invalid"))
    if model["environment_mode"] != "local_synthetic_disposable": errors.append(_error("$.environment_mode", "invalid"))
    if model["allowed_results"] != ["denied", "needs_human_governance"]: errors.append(_error("$.allowed_results", "invalid"))
    if model["authority_ceiling"] != "needs_human_governance": errors.append(_error("$.authority_ceiling", "invalid"))
    if model["real_owner"] != "unassigned / governance decision required": errors.append(_error("$.real_owner", "invalid"))
    if model["stage10_posture"] != "BLOCKED / NO-GO": errors.append(_error("$.stage10_posture", "invalid"))
    errors += _ordered_ids(model["components"], "component_id", COMPONENT_IDS, "$.components")
    expected_pairs = list(zip(COMPONENT_IDS, EVIDENCE_IDS))
    actual_pairs = [(item.get("component_id"), item.get("evidence_id")) for item in model["components"] if isinstance(item, dict)]
    if actual_pairs != expected_pairs or any(tuple(item.keys()) != ("component_id", "evidence_id") for item in model["components"] if isinstance(item, dict)):
        errors.append(_error("$.components", "closed_component_records_required"))
    errors += _ordered_ids(model["risks"], "risk_id", RISK_IDS, "$.risks")
    for index, risk in enumerate(model["risks"]):
        if not isinstance(risk, dict) or tuple(risk.keys()) != ("risk_id", "state", "owner"):
            errors.append(_error(f"$.risks[{index}]", "closed_risk_record_required"))
        elif risk["state"] != "open_blocked_unaccepted" or risk["owner"] != "unassigned / governance decision required":
            errors.append(_error(f"$.risks[{index}]", "risk_must_remain_blocked"))
    errors += _ordered_ids(model["human_gates"], "gate_id", GATE_IDS, "$.human_gates")
    for index, gate in enumerate(model["human_gates"]):
        if not isinstance(gate, dict) or tuple(gate.keys()) != ("gate_id", "authorized") or not _is_exact_false(gate.get("authorized")):
            errors.append(_error(f"$.human_gates[{index}]", "unauthorized_gate_required"))
    if model["claims"] != FALSE_CLAIMS or any(type(value) is not bool for value in model["claims"].values()): errors.append(_error("$.claims", "exact_false_claims_required"))
    if model["external_actions_performed"] != []: errors.append(_error("$.external_actions_performed", "must_be_empty"))
    return [*errors, *_scan_forbidden(model)]

def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    errors = _exact_keys(fixture, (
        "fixture_version", "scenario_id", "scope", "environment", "identity",
        "data_contract", "component_results", "risk_states", "required_human_gates",
        "requested_external_actions", "claims", "evidence_store", "observation",
        "recovery", "incident_tabletop", "support_handoff",
    ), "$")
    if errors: return errors
    if fixture["fixture_version"] != "nonproduction_readiness_fixture/v1": errors.append(_error("$.fixture_version", "invalid"))
    if fixture["scenario_id"] != "NR-SYNTHETIC-LOCAL-001": errors.append(_error("$.scenario_id", "invalid"))
    if fixture["scope"] != {"company": "汇沣电商", "brand": "BUW"}: errors.append(_error("$.scope", "invalid"))
    if fixture["environment"] != {"mode": "local_synthetic_disposable", "external_endpoints": [], "connectors": [], "credentials": []}: errors.append(_error("$.environment", "invalid"))
    if fixture["identity"] != {"principal_id": "synthetic-principal-nr-001", "simulated": True, "permissions": ["read_synthetic_fixture", "write_task_local_evidence"]}: errors.append(_error("$.identity", "invalid"))
    if fixture["data_contract"] != {"provenance": "synthetic", "classification": "synthetic_non_personal", "retention": "task_local_until_cleanup", "deletion": "deterministic_cleanup_required"}: errors.append(_error("$.data_contract", "invalid"))
    errors += _ordered_ids(fixture["component_results"], "component_id", COMPONENT_IDS, "$.component_results")
    expected_pairs = list(zip(COMPONENT_IDS, EVIDENCE_IDS))
    actual_pairs = [(item.get("component_id"), item.get("evidence_id")) for item in fixture["component_results"] if isinstance(item, dict)]
    if actual_pairs != expected_pairs: errors.append(_error("$.component_results", "evidence_alignment_required"))
    if any(not isinstance(item, dict) or tuple(item.keys()) != ("component_id", "status", "evidence_id") or item.get("status") != "passed" for item in fixture["component_results"]): errors.append(_error("$.component_results", "closed_pass_records_required"))
    if tuple(fixture["risk_states"].keys()) != RISK_IDS or set(fixture["risk_states"].values()) != {"open_blocked_unaccepted"}: errors.append(_error("$.risk_states", "blocked_risks_required"))
    if tuple(fixture["required_human_gates"]) != GATE_IDS: errors.append(_error("$.required_human_gates", "ordered_gates_required"))
    if fixture["requested_external_actions"] != []: errors.append(_error("$.requested_external_actions", "must_be_empty"))
    if fixture["claims"] != FALSE_CLAIMS or any(type(value) is not bool for value in fixture["claims"].values()): errors.append(_error("$.claims", "exact_false_claims_required"))
    store = fixture["evidence_store"]
    if tuple(store.keys()) != ("mode", "records") or store["mode"] != "task_local_append_only": errors.append(_error("$.evidence_store", "invalid"))
    records = store.get("records", [])
    if [item.get("sequence") for item in records] != [1, 2, 3]: errors.append(_error("$.evidence_store.records", "append_only_sequence_required"))
    expected_payloads = ("environment", "evidence", "observation")
    expected_evidence = ("EV-ENVIRONMENT", "EV-EVIDENCE", "EV-OBSERVATION")
    for index, (record, payload, evidence_id) in enumerate(zip(records, expected_payloads, expected_evidence)):
        expected_checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if tuple(record.keys()) != ("sequence", "record_id", "evidence_id", "checksum"):
            errors.append(_error(f"$.evidence_store.records[{index}]", "closed_record_required"))
        elif record["record_id"] != f"AUDIT-{index + 1:03d}" or record["evidence_id"] != evidence_id or record["checksum"] != expected_checksum:
            errors.append(_error(f"$.evidence_store.records[{index}]", "invalid"))
    if fixture["observation"] != {"mode": "local_decision_only", "metric_ids": ["METRIC-LOCAL-VALIDATION", "METRIC-LOCAL-DENIAL"], "alert_decision": "synthetic_no_external_delivery", "paging": False, "ticket_created": False, "external_delivery": False}: errors.append(_error("$.observation", "invalid"))
    expected_state = hashlib.sha256(b"synthetic-state").hexdigest()
    recovery = fixture["recovery"]
    if tuple(recovery.keys()) != ("snapshot_id", "rollback_trigger", "pre_restore_checksum", "post_restore_checksum", "restore_verified", "cleanup_verified") or recovery != {"snapshot_id": "SYNTHETIC-SNAPSHOT-001", "rollback_trigger": "synthetic_validation_failure", "pre_restore_checksum": expected_state, "post_restore_checksum": expected_state, "restore_verified": True, "cleanup_verified": True}: errors.append(_error("$.recovery", "invalid"))
    if fixture["incident_tabletop"] != {"scenario_id": "SYNTHETIC-INCIDENT-001", "severity": "synthetic_sev2", "containment": "local_fixture_isolation", "communications": "none_external", "real_incident_declared": False}: errors.append(_error("$.incident_tabletop", "invalid"))
    if fixture["support_handoff"] != {"case_id": "SYNTHETIC-CASE-001", "owner": "unassigned / governance decision required", "route": "abstract_support_role", "ticket_created": False, "sla_committed": False}: errors.append(_error("$.support_handoff", "invalid"))
    return [*errors, *_scan_forbidden(fixture)]

def evaluate_nonproduction_readiness(model: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    errors = list(dict.fromkeys([*validate_model(deepcopy(model)), *validate_fixture(deepcopy(fixture))]))
    denied = bool(errors)
    return {
        "result": "denied" if denied else "needs_human_governance",
        "reason_codes": [f"VALIDATION_ERROR:{item}" for item in errors] if denied else ["LOCAL_SYNTHETIC_VALIDATION_PASSED", "HUMAN_GATES_REQUIRED"],
        "evidence_refs": [] if denied else list(EVIDENCE_IDS),
        "required_human_gates": list(GATE_IDS),
        "risk_states": {risk_id: "open_blocked_unaccepted" for risk_id in RISK_IDS},
        "external_actions_performed": [],
        "claims": dict(FALSE_CLAIMS),
    }

def _validate_mapping(mapping: dict[str, Any]) -> list[str]:
    errors = _exact_keys(mapping, ("mapping_version", "stage10_posture", "risk_mappings", "archived_dependencies"), "$mapping")
    if errors: return errors
    if mapping["mapping_version"] != "nonproduction_readiness_stage10_14_mapping/v1" or mapping["stage10_posture"] != "BLOCKED / NO-GO": errors.append(_error("$mapping", "header_invalid"))
    errors += _ordered_ids(mapping["risk_mappings"], "risk_id", RISK_IDS, "$mapping.risk_mappings")
    for item in mapping["risk_mappings"]:
        if tuple(item.keys()) != ("risk_id", "evidence_ids", "state") or item["state"] != "open_blocked_unaccepted": errors.append(_error("$mapping.risk_mappings", "closed_blocked_records_required"))
    expected = [{"stage": n, "status": "Archived", "interpretation": "design_evidence_only"} for n in range(11, 15)]
    if mapping["archived_dependencies"] != expected: errors.append(_error("$mapping.archived_dependencies", "invalid"))
    return errors

def _validate_matrix(matrix: dict[str, Any]) -> list[str]:
    errors = _exact_keys(matrix, ("matrix_version", "requirements", "authority_claims"), "$matrix")
    expected_ids = ("AC-ENVIRONMENT", "AC-IDENTITY", "AC-DATA", "AC-EVIDENCE", "AC-OBSERVATION", "AC-RECOVERY", "AC-INCIDENT", "AC-SUPPORT", "AC-RISK-MAPPING", "AC-AUTHORITY")
    if errors: return errors
    if matrix["matrix_version"] != "nonproduction_readiness_acceptance/v1": errors.append(_error("$matrix.matrix_version", "invalid"))
    errors += _ordered_ids(matrix["requirements"], "requirement_id", expected_ids, "$matrix.requirements")
    for item in matrix["requirements"]:
        if tuple(item.keys()) != ("requirement_id", "test_ids", "evidence_ids", "local_synthetic_proof", "real_world_authority"):
            errors.append(_error("$matrix.requirements", "closed_records_required"))
        elif type(item["local_synthetic_proof"]) is not bool or item["local_synthetic_proof"] is not True or not _is_exact_false(item["real_world_authority"]):
            errors.append(_error("$matrix.requirements", "authority_flags_invalid"))
    if matrix["authority_claims"] != FALSE_CLAIMS: errors.append(_error("$matrix.authority_claims", "exact_false_claims_required"))
    return errors

def validate_repository(root: Path) -> list[str]:
    model = load_repository_yaml(root, MODEL_PATH)
    fixture = load_repository_yaml(root, FIXTURE_PATH)
    mapping = load_repository_yaml(root, MAPPING_PATH)
    matrix = load_repository_yaml(root, MATRIX_PATH)
    errors = [*validate_model(model), *validate_fixture(fixture), *_validate_mapping(mapping), *_validate_matrix(matrix)]
    if tuple(item["risk_id"] for item in mapping["risk_mappings"]) != RISK_IDS: errors.append(_error("$cross.risks", "identity_mismatch"))
    if tuple(item["evidence_id"] for item in model["components"]) != EVIDENCE_IDS: errors.append(_error("$cross.model_evidence", "identity_mismatch"))
    if tuple(item["evidence_id"] for item in fixture["component_results"]) != EVIDENCE_IDS: errors.append(_error("$cross.fixture_evidence", "identity_mismatch"))
    policy = (root / POLICY_PATH).read_text(encoding="utf-8")
    guide = (root / GUIDE_PATH).read_text(encoding="utf-8")
    workflow = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
    for token in ("Business loop", "Core objects", "Data flow", "Operators", "AI and human judgment boundary", "Proof of operation", "Authority ceiling", "Component contracts", "Risk mapping", "Stop and withdrawal", "Lifecycle", "BLOCKED / NO-GO", "needs_human_governance", "汇沣电商", "BUW", "PC", "六合通"):
        if token not in policy: errors.append(_error("$policy", f"missing:{token}"))
    if "AIOS non-production readiness validation passed" not in guide: errors.append(_error("$guide", "success_text_missing"))
    for token in ("pull_request:", "contents: read", "persist-credentials: false", "python -m pip install --requirement requirements-dev.txt"):
        if token not in workflow: errors.append(_error("$workflow", f"missing:{token}"))
    for prohibited in ("push:", "contents: write", "pull-requests: write", "pip install pyyaml"):
        if prohibited in workflow: errors.append(_error("$workflow", f"prohibited:{prohibited}"))
    return errors

if __name__ == "__main__":
    found = validate_repository(Path(__file__).resolve().parents[1])
    if found:
        for item in found: print(item)
        sys.exit(1)
    print("AIOS non-production readiness validation passed")
```

- [ ] Run the validator import check and commit.

```bash
python3 -m py_compile Tests/validate_aios_nonproduction_readiness.py
python3 -c 'import importlib.util; p="Tests/validate_aios_nonproduction_readiness.py"; s=importlib.util.spec_from_file_location("v",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)'
git add Tests/validate_aios_nonproduction_readiness.py
git commit -m "feat(stage15): add closed readiness validator"
```

Expected: compilation/import pass; full tests remain RED until controlled assets are added.

## Task 3: Create the canonical model and synthetic fixture

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml`
- Create: `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Supplies the exact closed model and fixture consumed by the validator.

- [ ] Create the exact model.

```yaml
model_version: nonproduction_readiness_integration/v1
stage: "15"
stage_id: NR-01
allowed_scope: {company: 汇沣电商, brand: BUW}
excluded_entities: [PC, 六合通]
environment_mode: local_synthetic_disposable
allowed_results: [denied, needs_human_governance]
authority_ceiling: needs_human_governance
real_owner: unassigned / governance decision required
stage10_posture: BLOCKED / NO-GO
components:
  - {component_id: CMP-ENVIRONMENT, evidence_id: EV-ENVIRONMENT}
  - {component_id: CMP-IDENTITY, evidence_id: EV-IDENTITY}
  - {component_id: CMP-DATA, evidence_id: EV-DATA}
  - {component_id: CMP-EVIDENCE, evidence_id: EV-EVIDENCE}
  - {component_id: CMP-OBSERVATION, evidence_id: EV-OBSERVATION}
  - {component_id: CMP-RECOVERY, evidence_id: EV-RECOVERY}
  - {component_id: CMP-INCIDENT, evidence_id: EV-INCIDENT}
  - {component_id: CMP-SUPPORT, evidence_id: EV-SUPPORT}
risks:
  - {risk_id: PR-RISK-001, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-002, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-003, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-004, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-005, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-006, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-007, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-008, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-009, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
  - {risk_id: PR-RISK-010, state: open_blocked_unaccepted, owner: unassigned / governance decision required}
human_gates:
  - {gate_id: HG-SPEC-APPROVAL, authorized: false}
  - {gate_id: HG-PLAN-APPROVAL, authorized: false}
  - {gate_id: HG-EXECUTION-ASSIGNMENT, authorized: false}
  - {gate_id: HG-IMPLEMENTATION-EVIDENCE, authorized: false}
  - {gate_id: HG-NAMED-OWNER, authorized: false}
  - {gate_id: HG-ARCH-SECURITY, authorized: false}
  - {gate_id: HG-PRIVACY-DATA, authorized: false}
  - {gate_id: HG-OPS-RECOVERY-INCIDENT-SUPPORT, authorized: false}
  - {gate_id: HG-RISK-DISPOSITION, authorized: false}
  - {gate_id: HG-PILOT-SCOPE, authorized: false}
  - {gate_id: HG-PILOT-EVIDENCE, authorized: false}
  - {gate_id: HG-RELEASE, authorized: false}
claims: {risk_accepted: false, pilot_authorized: false, production_ready: false, release_authorized: false}
external_actions_performed: []
```

- [ ] Create the exact fixture; checksums are SHA-256 of `environment`, `evidence`, `observation` and `synthetic-state`.

```yaml
fixture_version: nonproduction_readiness_fixture/v1
scenario_id: NR-SYNTHETIC-LOCAL-001
scope: {company: 汇沣电商, brand: BUW}
environment: {mode: local_synthetic_disposable, external_endpoints: [], connectors: [], credentials: []}
identity:
  principal_id: synthetic-principal-nr-001
  simulated: true
  permissions: [read_synthetic_fixture, write_task_local_evidence]
data_contract:
  provenance: synthetic
  classification: synthetic_non_personal
  retention: task_local_until_cleanup
  deletion: deterministic_cleanup_required
component_results:
  - {component_id: CMP-ENVIRONMENT, status: passed, evidence_id: EV-ENVIRONMENT}
  - {component_id: CMP-IDENTITY, status: passed, evidence_id: EV-IDENTITY}
  - {component_id: CMP-DATA, status: passed, evidence_id: EV-DATA}
  - {component_id: CMP-EVIDENCE, status: passed, evidence_id: EV-EVIDENCE}
  - {component_id: CMP-OBSERVATION, status: passed, evidence_id: EV-OBSERVATION}
  - {component_id: CMP-RECOVERY, status: passed, evidence_id: EV-RECOVERY}
  - {component_id: CMP-INCIDENT, status: passed, evidence_id: EV-INCIDENT}
  - {component_id: CMP-SUPPORT, status: passed, evidence_id: EV-SUPPORT}
risk_states:
  PR-RISK-001: open_blocked_unaccepted
  PR-RISK-002: open_blocked_unaccepted
  PR-RISK-003: open_blocked_unaccepted
  PR-RISK-004: open_blocked_unaccepted
  PR-RISK-005: open_blocked_unaccepted
  PR-RISK-006: open_blocked_unaccepted
  PR-RISK-007: open_blocked_unaccepted
  PR-RISK-008: open_blocked_unaccepted
  PR-RISK-009: open_blocked_unaccepted
  PR-RISK-010: open_blocked_unaccepted
required_human_gates:
  [HG-SPEC-APPROVAL, HG-PLAN-APPROVAL, HG-EXECUTION-ASSIGNMENT, HG-IMPLEMENTATION-EVIDENCE,
   HG-NAMED-OWNER, HG-ARCH-SECURITY, HG-PRIVACY-DATA, HG-OPS-RECOVERY-INCIDENT-SUPPORT,
   HG-RISK-DISPOSITION, HG-PILOT-SCOPE, HG-PILOT-EVIDENCE, HG-RELEASE]
requested_external_actions: []
claims: {risk_accepted: false, pilot_authorized: false, production_ready: false, release_authorized: false}
evidence_store:
  mode: task_local_append_only
  records:
    - {sequence: 1, record_id: AUDIT-001, evidence_id: EV-ENVIRONMENT, checksum: ba5285161ba6eed0085fb13784ce5c92f70ebc268b94fd66aa1d68a32884204d}
    - {sequence: 2, record_id: AUDIT-002, evidence_id: EV-EVIDENCE, checksum: ee8250fb76e094b34b471f13a73dbbe51d1ae142e9df59d7c0d31ec20f0a0a8e}
    - {sequence: 3, record_id: AUDIT-003, evidence_id: EV-OBSERVATION, checksum: 772c6953848bf5b19aedf9a34ccb066f31eacca29bdbfcb1b9821765f1060149}
observation:
  mode: local_decision_only
  metric_ids: [METRIC-LOCAL-VALIDATION, METRIC-LOCAL-DENIAL]
  alert_decision: synthetic_no_external_delivery
  paging: false
  ticket_created: false
  external_delivery: false
recovery:
  snapshot_id: SYNTHETIC-SNAPSHOT-001
  rollback_trigger: synthetic_validation_failure
  pre_restore_checksum: b88066f8d3d5af004ad275383907fc900bdda75f6ef21e32864eddcc01c4dc18
  post_restore_checksum: b88066f8d3d5af004ad275383907fc900bdda75f6ef21e32864eddcc01c4dc18
  restore_verified: true
  cleanup_verified: true
incident_tabletop:
  scenario_id: SYNTHETIC-INCIDENT-001
  severity: synthetic_sev2
  containment: local_fixture_isolation
  communications: none_external
  real_incident_declared: false
support_handoff:
  case_id: SYNTHETIC-CASE-001
  owner: unassigned / governance decision required
  route: abstract_support_role
  ticket_created: false
  sla_committed: false
```

- [ ] Run focused validation and commit.

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_model_and_fixture_are_valid -v
git add Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml
git commit -m "feat(stage15): add closed model and synthetic fixture"
```

Expected: model/fixture validation passes; repository validation remains RED until mapping, matrix, policy, guide and workflow exist.

## Task 4: Add exact evaluator, determinism, immutability and AST side-effect tests

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: `Tests/validate_aios_nonproduction_readiness.py`

**Interfaces**

- Verifies `evaluate_nonproduction_readiness` is pure and stable.

- [ ] Append these complete tests inside `NonproductionReadinessTests`.

```python
    def _assets(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        fixture = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
        return validator, model, fixture

    def test_valid_package_stops_at_human_governance(self):
        validator, model, fixture = self._assets()
        before_model, before_fixture = copy.deepcopy(model), copy.deepcopy(fixture)
        first = validator.evaluate_nonproduction_readiness(model, fixture)
        second = validator.evaluate_nonproduction_readiness(model, fixture)
        self.assertEqual(first, second)
        self.assertEqual("needs_human_governance", first["result"])
        self.assertEqual([], first["external_actions_performed"])
        self.assertEqual({"risk_accepted": False, "pilot_authorized": False, "production_ready": False, "release_authorized": False}, first["claims"])
        first["claims"]["risk_accepted"] = True
        self.assertFalse(second["claims"]["risk_accepted"])
        self.assertEqual(before_model, model)
        self.assertEqual(before_fixture, fixture)

    def test_invalid_package_is_denied(self):
        validator, model, fixture = self._assets()
        fixture["scope"]["brand"] = "PC"
        result = validator.evaluate_nonproduction_readiness(model, fixture)
        self.assertEqual("denied", result["result"])
        self.assertEqual([], result["external_actions_performed"])
        self.assertTrue(all(value is False for value in result["claims"].values()))

    def test_evaluator_ast_has_no_side_effect_apis(self):
        source = VALIDATOR.read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "evaluate_nonproduction_readiness")
        text = ast.unparse(function)
        for forbidden in ("open(", "read_text(", "write_text(", "requests", "socket", "subprocess", "os.environ", "time.", "datetime.", "random."):
            self.assertNotIn(forbidden, text)
```

- [ ] Run twice and compare serialized output.

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_valid_package_stops_at_human_governance -v
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_valid_package_stops_at_human_governance -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): prove pure fail-closed evaluation"
```

Expected: both runs pass identically; input and prior-output mutation do not affect later results.

## Task 5: Add recursive boundary and authority-smuggling adversarial tests

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: `Tests/validate_aios_nonproduction_readiness.py`

**Interfaces**

- Exercises recursive forbidden-key/value scanning and exact scope checks.

- [ ] Append the complete table-driven mutation test.

```python
    def test_environment_identity_data_and_authority_mutations_are_denied(self):
        validator, model, baseline = self._assets()
        mutations = (
            ("brand", lambda f: f["scope"].__setitem__("brand", "PC")),
            ("company", lambda f: f["scope"].__setitem__("company", "六合通")),
            ("wildcard", lambda f: f["scope"].__setitem__("brand", "*")),
            ("endpoint", lambda f: f["environment"]["external_endpoints"].append("https://example.invalid")),
            ("connector", lambda f: f["environment"]["connectors"].append("shopify")),
            ("credential", lambda f: f["environment"]["credentials"].append("token")),
            ("principal", lambda f: f["identity"].__setitem__("simulated", False)),
            ("permission", lambda f: f["identity"]["permissions"].append("write_production")),
            ("provenance", lambda f: f["data_contract"].__setitem__("provenance", "real")),
            ("classification", lambda f: f["data_contract"].__setitem__("classification", "personal")),
            ("authority", lambda f: f.__setitem__("decision", "approved")),
            ("external action", lambda f: f["requested_external_actions"].append("send")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                fixture = copy.deepcopy(baseline)
                mutate(fixture)
                result = validator.evaluate_nonproduction_readiness(model, fixture)
                self.assertEqual("denied", result["result"])
                self.assertEqual([], result["external_actions_performed"])
                self.assertTrue(all(value is False for value in result["claims"].values()))
```

- [ ] Add YAML source checks against aliases and merge keys.

```python
    def test_controlled_yaml_uses_no_aliases_or_merge_keys(self):
        for path in (MODEL, FIXTURE, ROOT / "Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml", ROOT / "Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml"):
            if path.exists():
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"(?m)^\s*<<:")
                self.assertNotRegex(text, r"(?<!\w)[&*][A-Za-z0-9_-]+")
```

- [ ] Run and commit.

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_environment_identity_data_and_authority_mutations_are_denied -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): reject boundary and authority smuggling"
```

Expected: every mutation returns `denied` with false claims and no external actions.

## Task 6: Prove local evidence and observation integrity

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: model, fixture and validator.

**Interfaces**

- Verifies append-only sequence, record IDs, evidence IDs, checksums and no external delivery.

- [ ] Append complete evidence mutation tests.

```python
    def test_evidence_and_observation_integrity(self):
        validator, model, baseline = self._assets()
        for label, mutate in (
            ("sequence gap", lambda f: f["evidence_store"]["records"][1].__setitem__("sequence", 3)),
            ("record duplicate", lambda f: f["evidence_store"]["records"][1].__setitem__("record_id", "AUDIT-001")),
            ("checksum", lambda f: f["evidence_store"]["records"][0].__setitem__("checksum", "0" * 64)),
            ("evidence id", lambda f: f["evidence_store"]["records"][0].__setitem__("evidence_id", "EV-UNKNOWN")),
            ("paging", lambda f: f["observation"].__setitem__("paging", True)),
            ("ticket", lambda f: f["observation"].__setitem__("ticket_created", True)),
            ("delivery", lambda f: f["observation"].__setitem__("external_delivery", True)),
        ):
            with self.subTest(label=label):
                fixture = copy.deepcopy(baseline)
                mutate(fixture)
                self.assertEqual("denied", validator.evaluate_nonproduction_readiness(model, fixture)["result"])
```

- [ ] Verify deterministic checksums directly.

```bash
python3 - <<'PY'
import hashlib
for value in ("environment", "evidence", "observation", "synthetic-state"):
    print(value, hashlib.sha256(value.encode("utf-8")).hexdigest())
PY
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_evidence_and_observation_integrity -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): prove local evidence integrity"
```

Expected: printed hashes match fixture values; every mutation is denied.

## Task 7: Prove recovery, incident tabletop and support handoff boundaries

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: fixture and validator.

**Interfaces**

- Verifies synthetic recovery and abstract support evidence without real operations.

- [ ] Append complete recovery/incident/support tests.

```python
    def test_recovery_incident_and_support_mutations_are_denied(self):
        validator, model, baseline = self._assets()
        for label, mutate in (
            ("restore", lambda f: f["recovery"].__setitem__("restore_verified", False)),
            ("cleanup", lambda f: f["recovery"].__setitem__("cleanup_verified", False)),
            ("post checksum", lambda f: f["recovery"].__setitem__("post_restore_checksum", "0" * 64)),
            ("real incident", lambda f: f["incident_tabletop"].__setitem__("real_incident_declared", True)),
            ("communications", lambda f: f["incident_tabletop"].__setitem__("communications", "email_sent")),
            ("real owner", lambda f: f["support_handoff"].__setitem__("owner", "Tony")),
            ("real route", lambda f: f["support_handoff"].__setitem__("route", "live_support_queue")),
            ("ticket", lambda f: f["support_handoff"].__setitem__("ticket_created", True)),
            ("sla", lambda f: f["support_handoff"].__setitem__("sla_committed", True)),
        ):
            with self.subTest(label=label):
                fixture = copy.deepcopy(baseline)
                mutate(fixture)
                self.assertEqual("denied", validator.evaluate_nonproduction_readiness(model, fixture)["result"])
```

- [ ] Run and commit.

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_recovery_incident_and_support_mutations_are_denied -v
python3 -m unittest Tests.test_nonproduction_readiness -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): enforce synthetic recovery and support boundaries"
```

Expected: every invalid underlying fact is denied even when component status remains `passed`.

## Task 8: Create the complete Stage 10–14 mapping and acceptance matrix

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml`
- Create: `Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Supplies exact cross-file risk/evidence and requirement/test/evidence mappings.

- [ ] Create the complete mapping.

```yaml
mapping_version: nonproduction_readiness_stage10_14_mapping/v1
stage10_posture: BLOCKED / NO-GO
risk_mappings:
  - {risk_id: PR-RISK-001, evidence_ids: [EV-ENVIRONMENT], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-002, evidence_ids: [EV-IDENTITY], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-003, evidence_ids: [EV-DATA], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-004, evidence_ids: [EV-DATA, EV-EVIDENCE], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-005, evidence_ids: [EV-OBSERVATION, EV-EVIDENCE], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-006, evidence_ids: [EV-RECOVERY], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-007, evidence_ids: [EV-INCIDENT], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-008, evidence_ids: [EV-SUPPORT], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-009, evidence_ids: [EV-IDENTITY, EV-DATA], state: open_blocked_unaccepted}
  - {risk_id: PR-RISK-010, evidence_ids: [EV-ENVIRONMENT, EV-EVIDENCE], state: open_blocked_unaccepted}
archived_dependencies:
  - {stage: 11, status: Archived, interpretation: design_evidence_only}
  - {stage: 12, status: Archived, interpretation: design_evidence_only}
  - {stage: 13, status: Archived, interpretation: design_evidence_only}
  - {stage: 14, status: Archived, interpretation: design_evidence_only}
```

- [ ] Create all ten acceptance rows; no row may be deferred to the implementer.

```yaml
matrix_version: nonproduction_readiness_acceptance/v1
requirements:
  - {requirement_id: AC-ENVIRONMENT, test_ids: [test_environment_identity_data_and_authority_mutations_are_denied], evidence_ids: [EV-ENVIRONMENT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-IDENTITY, test_ids: [test_environment_identity_data_and_authority_mutations_are_denied], evidence_ids: [EV-IDENTITY], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-DATA, test_ids: [test_environment_identity_data_and_authority_mutations_are_denied], evidence_ids: [EV-DATA], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-EVIDENCE, test_ids: [test_evidence_and_observation_integrity], evidence_ids: [EV-EVIDENCE], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-OBSERVATION, test_ids: [test_evidence_and_observation_integrity], evidence_ids: [EV-OBSERVATION], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-RECOVERY, test_ids: [test_recovery_incident_and_support_mutations_are_denied], evidence_ids: [EV-RECOVERY], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-INCIDENT, test_ids: [test_recovery_incident_and_support_mutations_are_denied], evidence_ids: [EV-INCIDENT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-SUPPORT, test_ids: [test_recovery_incident_and_support_mutations_are_denied], evidence_ids: [EV-SUPPORT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-RISK-MAPPING, test_ids: [test_repository_cross_file_contract], evidence_ids: [EV-ENVIRONMENT, EV-IDENTITY, EV-DATA, EV-EVIDENCE, EV-OBSERVATION, EV-RECOVERY, EV-INCIDENT, EV-SUPPORT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-AUTHORITY, test_ids: [test_valid_package_stops_at_human_governance, test_invalid_package_is_denied], evidence_ids: [], local_synthetic_proof: true, real_world_authority: false}
authority_claims: {risk_accepted: false, pilot_authorized: false, production_ready: false, release_authorized: false}
```

- [ ] Add and run the repository cross-file test.

```python
    def test_repository_cross_file_contract(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_repository_cross_file_contract -v
git add Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): trace blocked risks to complete acceptance evidence"
```

Expected: test remains RED only because policy, guide and workflow are not yet present.

## Task 9: Create the complete policy and validation guide

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Integration-v1.md`
- Create: `Tests/AIOS-Nonproduction-Readiness-Validation.md`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Makes the machine contract independently reviewable.
- Answers all system questions without granting real authority.

- [ ] Create the policy with this complete normative body.

```markdown
# AIOS Non-production Readiness Integration v1

## Business loop
Load one repository-controlled BUW synthetic package, validate it against the closed model, evaluate it locally, record task-local evidence, and stop at `needs_human_governance`. The loop performs no connector, network, infrastructure, customer, store, order, employee, ticket, payment or production action.

## Core objects
The core objects are the canonical model, synthetic fixture, Stage 10–14 risk mapping, acceptance matrix, normalized evaluator decision and local audit evidence. Their identities and schemas are closed and versioned.

## Data flow
Data flows only from allowlisted repository YAML into memory, through validation and pure evaluation, to terminal output and disposable task-local test evidence. No data leaves the process. Company is `汇沣电商`; brand is `BUW`; `PC` and `六合通` are excluded.

## Operators
An assigned implementation worker may edit only plan-authorized repository paths and run local tests. A human Governance Thread separately approves the plan, execution assignment, implementation evidence, risk disposition, pilot scope, release, merge, publication and archive.

## AI and human judgment boundary
AI may validate deterministic syntax, identity, ordering, evidence references and fail-closed behavior. AI may not assign real owners, accept risks, authorize a pilot, declare production readiness, approve release or bypass any human gate.

## Proof of operation
A passing result proves only repository-contained local synthetic behavior, deterministic denial of adversarial inputs, immutability, evidence consistency and no external actions. It does not prove a live service, real pilot, production readiness, operational support or legal compliance.

## Authority ceiling
The only evaluator results are `denied` and `needs_human_governance`. Stage 10 remains `BLOCKED / NO-GO`. All risks remain open, blocked and unaccepted. All authority claims remain false.

## Component contracts
Environment is local and disposable. Identity is simulated. Data is synthetic and non-personal. Evidence is task-local append-only. Observation is local decision only. Recovery is synthetic checksum equality and cleanup proof. Incident handling is tabletop only. Support handoff uses an abstract role without ticket or SLA commitment.

## Risk mapping
`PR-RISK-001` through `PR-RISK-010` map to local evidence IDs only. Mapping evidence is remediation evidence, not risk acceptance, risk closure, pilot authority, production authority or release authority.

## Stop and withdrawal
Stop immediately on unknown fields, malformed types, reordered or duplicate IDs, excluded entities, external locators, credentials, connectors, authority-like values, changed checksums, incomplete recovery, real owner names, external communication, non-empty requested actions, or any attempt to exceed `needs_human_governance`. Withdrawal requires deleting disposable task-local evidence and recording the denial; no external rollback is performed.

## Lifecycle
Stage 15 begins `Planned`. After a separately approved plan, one dedicated Execution Task and one implementation branch may execute. Implementation may return only Stage 15 `Reported` plus a Mandatory Return. `Reviewed`, merge, publication, `Archived`, a real pilot and Stage 16 require separate human Governance Thread decisions.
```

- [ ] Create the validation guide with exact commands and interpretation.

```markdown
# AIOS Non-production Readiness Validation

Run from repository root:

    python -m pip install --requirement requirements-dev.txt
    python3 Tests/validate_aios_nonproduction_readiness.py
    python3 -m unittest Tests.test_nonproduction_readiness -v
    python3 -m unittest Tests.test_project_governance -v
    python3 -m unittest discover -s Tests -p 'test_*.py'
    python3 Tests/validate_aios_workflow_schema.py
    python3 -m compileall -q Tests
    git diff --check

Expected validator success text: `AIOS non-production readiness validation passed`.

A pass proves only repository-contained local synthetic behavior. It does not accept any risk, assign a real owner, authorize a pilot, declare production readiness, permit release, merge, publication, archive or Stage 16.
```

- [ ] Run repository validation and commit.

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
git add Governance/AIOS-Nonproduction-Readiness-Integration-v1.md Tests/AIOS-Nonproduction-Readiness-Validation.md
git commit -m "docs(stage15): add complete bounded integration policy"
```

Expected: repository validation remains RED only because the workflow is not yet present.

## Task 10: Add pull-request-only read-only CI using the repository dependency contract

**Files**

- Create: `.github/workflows/validate-aios-nonproduction-readiness.yml`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Runs on pull requests only.
- Uses `requirements-dev.txt`.
- Grants `contents: read` only.

- [ ] Create the exact workflow.

```yaml
name: Validate AIOS Non-production Readiness
on:
  pull_request:
permissions:
  contents: read
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install --requirement requirements-dev.txt
      - run: python3 Tests/validate_aios_nonproduction_readiness.py
      - run: python3 -m unittest Tests.test_nonproduction_readiness -v
      - run: python3 -m unittest Tests.test_project_governance -v
      - run: python3 -m unittest discover -s Tests -p 'test_*.py'
      - run: python3 Tests/validate_aios_workflow_schema.py
      - run: python3 -m compileall -q Tests
```

- [ ] Append the exact CI regression.

```python
    def test_ci_is_pull_request_only_read_only_and_constrained(self):
        workflow = (ROOT / ".github/workflows/validate-aios-nonproduction-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("python -m pip install --requirement requirements-dev.txt", workflow)
        for denied in ("contents: write", "pull-requests: write", "issues: write", "pip install pyyaml", "git push", "deployment"):
            self.assertNotIn(denied, workflow)
```

- [ ] Run all targeted checks and commit.

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 Tests/validate_aios_workflow_schema.py
git add .github/workflows/validate-aios-nonproduction-readiness.yml Tests/test_nonproduction_readiness.py
git commit -m "ci(stage15): validate local proof with constrained dependencies"
```

Expected: targeted validator and tests pass; workflow remains read-only and pull-request-only.

## Task 11: Complete adversarial, cross-directory and frozen-boundary regression

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: `Tests/validate_aios_nonproduction_readiness.py`
- Consume without modification: Stage 10–14 policy assets.

**Interfaces**

- Proves stable denial, working-directory independence and frozen prior-stage evidence.

- [ ] Append complete cross-directory and stable-error tests.

```python
    def test_cli_is_independent_of_current_directory(self):
        for cwd in (ROOT, ROOT / "Tests"):
            result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=cwd, text=True, capture_output=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("AIOS non-production readiness validation passed\n", result.stdout)

    def test_errors_are_stable_and_inputs_are_not_mutated(self):
        validator, model, fixture = self._assets()
        fixture["scope"]["brand"] = "PC"
        first = validator.evaluate_nonproduction_readiness(model, fixture)
        second = validator.evaluate_nonproduction_readiness(copy.deepcopy(model), copy.deepcopy(fixture))
        self.assertEqual(first, second)
        self.assertEqual(list(dict.fromkeys(first["reason_codes"])), first["reason_codes"])
```

- [ ] Compare frozen Stage 10–14 paths to the independently approved plan head.

```bash
test -n "$STAGE15_APPROVED_PLAN_HEAD"
git cat-file -e "$STAGE15_APPROVED_PLAN_HEAD^{commit}"
git diff --exit-code "$STAGE15_APPROVED_PLAN_HEAD"...HEAD -- \
  Governance/AIOS-Production-Readiness-v1.md \
  Governance/AIOS-Architecture-Security-Foundations-v1.md \
  Governance/AIOS-Privacy-Data-Governance-v1.md \
  Governance/AIOS-Operational-Resilience-v1.md \
  Governance/AIOS-Support-Controlled-Pilot-v1.md
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest discover -s Tests -p 'test_*.py'
git diff --check
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): harden deterministic frozen-boundary validation"
```

Expected: frozen diff is empty; targeted/full tests and diff check pass.

## Task 12: Move only to Reported and submit the exact Mandatory Return

**Files**

- Modify: `Governance/AIOS-Stage-Registry.md`
- Modify: `Governance/AIOS-Project-Registry.md`
- Modify/Test: `Tests/test_project_governance.py`
- Modify lifecycle compatibility tests only if current assertions require it.

**Interfaces**

- Moves Stage 15 only from `Planned` to `Reported`.
- Generates exact remote replay evidence and Mandatory Return.
- Does not self-approve.

- [ ] Require exact assignment and evidence variables, then update only the Stage 15 row and append-only change logs.

```python
from pathlib import Path
import os
import re

required = ("STAGE15_EXECUTION_TASK", "STAGE15_IMPLEMENTATION_BRANCH", "STAGE15_REMOTE_HEAD", "STAGE15_REMOTE_TREE", "STAGE15_TARGETED_COUNT", "STAGE15_REPOSITORY_COUNT", "STAGE15_PROJECT_COUNT", "STAGE15_CI_URLS")
missing = [name for name in required if not os.environ.get(name)]
if missing:
    raise SystemExit("missing exact evidence variables: " + ", ".join(missing))

stage_path = Path("Governance/AIOS-Stage-Registry.md")
stage = stage_path.read_text(encoding="utf-8")
rows = [line for line in stage.splitlines() if line.startswith("| 15 |")]
if len(rows) != 1 or "| Planned |" not in rows[0]:
    raise SystemExit("expected exactly one Planned Stage 15 row")
replacement = rows[0].replace("| Planned |", "| Reported |")
replacement = re.sub(r"corrected implementation plan awaits independent human review.*$", f"implementation evidence at `{os.environ['STAGE15_REMOTE_HEAD']}` / tree `{os.environ['STAGE15_REMOTE_TREE']}` submitted through {os.environ['STAGE15_EXECUTION_TASK']} on branch `{os.environ['STAGE15_IMPLEMENTATION_BRANCH']}`; Mandatory Return submitted; implementation evidence awaits independent human review; maximum result `needs_human_governance`; no real pilot or production authority. |", replacement)
stage_path.write_text(stage.replace(rows[0], replacement), encoding="utf-8")

project_path = Path("Governance/AIOS-Project-Registry.md")
project = project_path.read_text(encoding="utf-8")
project = project.replace("Stage 14 Archived / Stage 15 Planned", "Stage 14 Archived / Stage 15 Reported")
project = project.replace("corrected implementation plan awaits independent human review", "implementation evidence awaits independent human review; Mandatory Return submitted; maximum result `needs_human_governance`")
project_path.write_text(project, encoding="utf-8")
```

- [ ] Run the complete evidence bundle, push the assigned branch, and perform fresh remote replay.

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest Tests.test_project_governance -v
python3 -m unittest discover -s Tests -p 'test_*.py'
python3 Tests/validate_aios_workflow_schema.py
python3 Tests/validate_aios_operational_resilience.py
python3 Tests/validate_aios_support_controlled_pilot.py
python3 -m compileall -q Tests
git diff --check
git status --short
git add Governance/AIOS-Stage-Registry.md Governance/AIOS-Project-Registry.md Tests/test_project_governance.py
git commit -m "docs(stage15): report nonproduction readiness evidence"
git push origin "$STAGE15_IMPLEMENTATION_BRANCH"
git rev-parse HEAD
git rev-parse HEAD^{tree}
gh pr view 41 --json isDraft,state,mergeStateStatus,headRefOid,url
gh pr checks 41
```

Expected: all commands pass; PR remains Draft/open/unmerged; local/remote head matches; Stage 15 is `Reported`, not `Reviewed` or `Archived`.

- [ ] Clone the exact remote branch into a new temporary directory and repeat the complete evidence bundle.

```bash
REMOTE_HEAD="$(git rev-parse HEAD)"
REMOTE_TREE="$(git rev-parse HEAD^{tree})"
TMPDIR="$(mktemp -d)"
git clone --branch "$STAGE15_IMPLEMENTATION_BRANCH" --single-branch "$(git remote get-url origin)" "$TMPDIR/replay"
test "$(git -C "$TMPDIR/replay" rev-parse HEAD)" = "$REMOTE_HEAD"
test "$(git -C "$TMPDIR/replay" rev-parse HEAD^{tree})" = "$REMOTE_TREE"
(
  cd "$TMPDIR/replay"
  python -m pip install --requirement requirements-dev.txt
  python3 Tests/validate_aios_nonproduction_readiness.py
  python3 -m unittest discover -s Tests -p 'test_*.py'
  python3 -m compileall -q Tests
  git diff --check
  test -z "$(git status --porcelain)"
)
```

Expected: exact head/tree parity, clean checkout and all replay checks pass.

- [ ] Generate and post the Mandatory Return with exact values; do not self-approve.

```bash
cat > /tmp/stage15-mandatory-return.md <<EOF
## Stage 15 / NR-01 Mandatory Return

- exact remote head and tree: \`$(git rev-parse HEAD)\` / \`$(git rev-parse HEAD^{tree})\`
- assigned Execution Task: \`${STAGE15_EXECUTION_TASK}\`
- implementation branch: \`${STAGE15_IMPLEMENTATION_BRANCH}\`
- Draft PR: #41
- changed-file allowlist: $(git diff --name-only "$STAGE15_APPROVED_PLAN_HEAD"...HEAD | tr '\n' ' ')
- targeted/full/Project Governance counts: ${STAGE15_TARGETED_COUNT} / ${STAGE15_REPOSITORY_COUNT} / ${STAGE15_PROJECT_COUNT}
- final-head CI links: ${STAGE15_CI_URLS}
- lifecycle: \`Reported\`
- maximum result \`needs_human_governance\`
- frozen boundary: Stage 10 remains \`BLOCKED / NO-GO\`; Stages 11–14 remain \`Archived\`
- authority confirmation: no external actions, real data, credentials, permissions, real owners, risk acceptance, pilot, production, release, merge, publication, archive, Issue closure or Stage 16
- next gate: independent human review of this exact remote head and Mandatory Return
EOF
gh issue comment 40 --body-file /tmp/stage15-mandatory-return.md
```

- [ ] Stop.

```bash
git status --short
gh pr view 41 --json isDraft,state,headRefOid,url
```

Expected: no further edits; do not mark `Reviewed`, merge, publish, archive, close Issue #40, start a real pilot or start Stage 16.

## Plan self-review checklist

- [ ] Every deliverable has an exact path and responsible task.
- [ ] All component boundaries are covered: environment, identity, data, evidence, observation, recovery, incident, support and evaluator.
- [ ] `PR-RISK-001` through `PR-RISK-010` remain ordered and `open_blocked_unaccepted`.
- [ ] All twelve human gates remain ordered and unauthorized.
- [ ] `AC-ENVIRONMENT`, `AC-IDENTITY`, `AC-DATA`, `AC-EVIDENCE`, `AC-OBSERVATION`, `AC-RECOVERY`, `AC-INCIDENT`, `AC-SUPPORT`, `AC-RISK-MAPPING` and `AC-AUTHORITY` are complete.
- [ ] Policy sections are complete: Business loop, Core objects, Data flow, Operators, AI and human judgment boundary, Proof of operation, Authority ceiling, Component contracts, Risk mapping, Stop and withdrawal, Lifecycle.
- [ ] CI uses `python -m pip install --requirement requirements-dev.txt`.
- [ ] Positive, adversarial, determinism, immutability, recursive scanning, cross-file, CLI and frozen-boundary tests contain executable bodies.
- [ ] Lifecycle update and Mandatory Return contain exact commands and evidence fields.
- [ ] The plan does not assign an Execution Task, implementation branch, real owner or real-world authority.
- [ ] Implementation stops at Stage 15 `Reported` + Mandatory Return.

## Human decisions still required after this plan

1. Independently approve or return this exact corrected implementation-plan head.
2. Assign exactly one dedicated Execution Task and one implementation branch.
3. Independently review the exact implementation head and Mandatory Return.
4. Decide merge and publication separately.
5. Decide archive and Issue #40 closure separately.
6. Decide any real pilot scope, owners, data, systems, risk dispositions, release and Stage 16 separately.
