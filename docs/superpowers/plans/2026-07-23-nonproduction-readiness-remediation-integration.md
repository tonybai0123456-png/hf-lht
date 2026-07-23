# Non-production Readiness Remediation and Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Governance override for this plan:** Do not begin implementation from this governance-design branch. Start only after independent human approval of this exact plan, creation or assignment of one dedicated Execution Task, and assignment of one implementation branch. Do not dispatch subagents or create another execution task unless the Governance Thread explicitly selects that execution mode.

**Goal:** Implement a repository-contained, local, synthetic and disposable Stage 15 integration proof that validates the exact BUW/汇沣电商 boundary, prepares evidence against PR-RISK-001 through PR-RISK-010, fails closed on malformed or authority-like input, and returns at most `needs_human_governance`.

**Architecture:** An exact allowlist loader reads four controlled YAML assets into memory. A pure evaluator validates one atomically versioned model and one synthetic fixture, applies most-restrictive-wins rules, and emits a normalized decision without filesystem, network, clock, environment, subprocess, connector or external-write access. A repository validator proves cross-file identity, risk, gate, evidence and lifecycle consistency. Markdown policy and validation guidance make the machine contract independently reviewable; pull-request-only read-only CI provides reproducible evidence without granting pilot or production authority.

**Tech Stack:** Python 3 standard library, PyYAML `safe_load`, `unittest`, YAML governance assets, Markdown policy and validation guide, GitHub Actions.

## Global Constraints

- This plan is review material only until the Governance Thread approves its exact head.
- Implementation requires one separately assigned dedicated Execution Task and one separately assigned implementation branch. The governance-design branch `gov/aios-stage15-nonproduction-readiness-design` is not the implementation branch.
- Before the first implementation edit, record the approved plan head, task identifier, branch and clean starting tree in Issue #40.
- The only allowed business scope is company `汇沣电商` and brand `BUW`. `PC`, `六合通`, combined scopes, aliases, wildcards and unknown identities fail closed.
- Every input and fixture is repository-controlled and synthetic. Do not access or represent real customers, stores, orders, employees, tickets, monitors, infrastructure resources, databases, APIs, connectors, credentials or secrets.
- Local persistence is confined to task-local disposable synthetic state. Tests may use `tempfile.TemporaryDirectory`; the evaluator itself must not read or write files.
- Stage 10 remains `BLOCKED / NO-GO`. PR-RISK-001 through PR-RISK-010 remain `open`, `blocked`, `unaccepted` and owner `unassigned / governance decision required`.
- Stages 11–14 remain archived design evidence. Their assets cannot be modified or reinterpreted as real operating capability.
- The evaluator has exactly two results: invalid input returns `denied`; an otherwise-valid local synthetic package returns `needs_human_governance`.
- Output claims `risk_accepted`, `pilot_authorized`, `production_ready` and `release_authorized` are always exactly `false`. `external_actions_performed` is always exactly `[]`.
- Reject permission-like results or fields, including `ready`, `approved`, `accepted`, `go`, `eligible`, `proceed`, `pilot_ready`, `pilot_authorized`, `production_ready`, `released` and semantic equivalents.
- Every human gate is unauthorized in the model and fixture. Passing tests never satisfies or bypasses a human gate.
- Each implementation task starts with a focused failing test, makes the smallest change that passes it, runs relevant regression tests, and ends with a dedicated commit.
- No task authorizes external infrastructure, credentials, permissions, real data, real owners, risk acceptance, deployment, real pilot, merge, publication, release, archive or Stage 16.
- Implementation completion may reach only Draft PR + Stage 15 `Reported` + Mandatory Return. `Reviewed`, merge, publication and archive remain later independent Governance Thread decisions.

## Plan authority and starting state

| Field | Exact value |
|---|---|
| Stage | `15 / NR-01` |
| Issue | `#40` |
| Governance-design branch | `gov/aios-stage15-nonproduction-readiness-design` |
| Draft PR | `#41` |
| Approved written-spec head | `6c6b028c1b21e6dc2826aa916e0725a3d0b4e0fa` |
| Lifecycle before implementation | Stage 15 `Planned`; implementation plan awaiting independent human review |
| Implementation assignment | dedicated Execution Task and implementation branch unassigned |
| Maximum implementation lifecycle | Draft PR + Stage 15 `Reported` + Mandatory Return |
| Real owner state | `unassigned / governance decision required` |
| Real pilot authority | none; a later exact-scope human governance decision is required |

---

## Exact file structure and single responsibilities

### Create

- `Governance/AIOS-Nonproduction-Readiness-Integration-v1.md` — normative policy for the local synthetic business loop, authority ceiling, stop rules and lifecycle.
- `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml` — canonical identity, component, evidence, human-gate, result and authority contract.
- `Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml` — exact PR-RISK-001 through PR-RISK-010 mapping to local evidence while preserving all blocked/unaccepted states.
- `Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml` — requirement-to-test-to-evidence trace with all real-world authority flags false.
- `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml` — sole otherwise-valid synthetic package.
- `Tests/validate_aios_nonproduction_readiness.py` — allowlisted loader, model/fixture validators, pure evaluator and repository validator.
- `Tests/test_nonproduction_readiness.py` — structural, positive, deterministic, immutability and adversarial tests.
- `Tests/AIOS-Nonproduction-Readiness-Validation.md` — reproducible commands and the bounded meaning of a pass.
- `.github/workflows/validate-aios-nonproduction-readiness.yml` — pull-request-only, read-only validation.

### Modify only at implementation completion

- `Governance/AIOS-Stage-Registry.md` — move Stage 15 only from `Planned` to `Reported`, link the assigned Execution Task/branch and Mandatory Return, and preserve every higher gate.
- `Governance/AIOS-Project-Registry.md` — synchronize Stage 15 `Reported` and independent-review next gate.
- `Tests/test_project_governance.py` — assert exact Reported evidence and reject Reviewed/Archived/pilot authority.
- `Tests/validate_aios_operational_resilience.py` — update only a current-registry forward-lifecycle assertion if it explicitly caps the roadmap before Stage 15.
- `Tests/test_operational_resilience.py` — regress frozen Stage 13 evidence and the authorized Stage 15 Reported transition.
- `Tests/validate_aios_support_controlled_pilot.py` — update only a current-registry forward-lifecycle assertion if required.
- `Tests/test_support_controlled_pilot.py` — regress frozen Stage 14 evidence and reject reinterpretation as real pilot capability.

### Consume without modification

- `docs/superpowers/specs/2026-07-23-nonproduction-readiness-remediation-integration-design.md` — approved normative specification.
- Stage 10 Production Readiness assets — source of exact risk identities and `BLOCKED / NO-GO`.
- Stage 11 Architecture and Security, Stage 12 Privacy and Data Governance, Stage 13 Operational Resilience and Stage 14 Support and Controlled Pilot assets — archived evidence and frozen authority limits.
- `.github/workflows/validate-aios-workflow-schema.yml` and `Tests/validate_aios_workflow_schema.py` — workflow-schema contract.

## Exact public interfaces

```python
def load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]:
    """Safely load one exact allowlisted YAML mapping below root."""

def validate_model(model: dict[str, Any]) -> list[str]:
    """Return stable ordered validation errors for the canonical model."""

def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    """Return stable ordered validation errors for one synthetic package."""

def evaluate_nonproduction_readiness(
    model: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    """Purely evaluate already-loaded mappings and return a normalized decision."""

def validate_repository(root: Path) -> list[str]:
    """Validate the allowlisted assets and their cross-file identities."""
```

The evaluator result has this exact shape:

```python
{
    "result": "denied" | "needs_human_governance",
    "reason_codes": list[str],
    "evidence_refs": list[str],
    "required_human_gates": list[str],
    "risk_states": {
        "PR-RISK-001": "open_blocked_unaccepted",
        "PR-RISK-002": "open_blocked_unaccepted",
        "PR-RISK-003": "open_blocked_unaccepted",
        "PR-RISK-004": "open_blocked_unaccepted",
        "PR-RISK-005": "open_blocked_unaccepted",
        "PR-RISK-006": "open_blocked_unaccepted",
        "PR-RISK-007": "open_blocked_unaccepted",
        "PR-RISK-008": "open_blocked_unaccepted",
        "PR-RISK-009": "open_blocked_unaccepted",
        "PR-RISK-010": "open_blocked_unaccepted",
    },
    "external_actions_performed": [],
    "claims": {
        "risk_accepted": False,
        "pilot_authorized": False,
        "production_ready": False,
        "release_authorized": False,
    },
}
```

---

## Task 1: Pin the closed model contract with failing structural tests

**Files**

- Create: `Tests/test_nonproduction_readiness.py`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Consumes the future model path.
- Pins `validate_model(model: dict[str, Any]) -> list[str]`.

- [ ] Record the separately approved execution starting state:

```bash
git rev-parse HEAD
git branch --show-current
git status --short
test ! -e Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml
test ! -e Tests/validate_aios_nonproduction_readiness.py
```

Expected: approved plan head and assigned implementation branch are printed, status is clean, both absence checks exit `0`.

- [ ] Create a test loader and the first exact test:

```python
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_nonproduction_readiness.py"

def load_validator():
    spec = importlib.util.spec_from_file_location("nr_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

class NonproductionReadinessTests(unittest.TestCase):
    def test_model_has_exact_scope_results_risks_and_gates(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_model(model))
        self.assertEqual("nonproduction_readiness_integration/v1", model["model_version"])
        self.assertEqual({"company": "汇沣电商", "brand": "BUW"}, model["allowed_scope"])
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])
        self.assertEqual(["denied", "needs_human_governance"], model["allowed_results"])
        self.assertEqual(
            [f"PR-RISK-{number:03d}" for number in range(1, 11)],
            [risk["risk_id"] for risk in model["risks"]],
        )
        self.assertEqual(
            [
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
            ],
            [gate["gate_id"] for gate in model["human_gates"]],
        )
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_model_has_exact_scope_results_risks_and_gates -v
```

Expected: `ERROR` because the validator/model is absent.

- [ ] Commit only the failing test:

```bash
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): pin nonproduction readiness contract"
```

## Task 2: Implement the allowlisted loader and canonical model

**Files**

- Create: `Tests/validate_aios_nonproduction_readiness.py`
- Create: `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Implements `load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]`.
- Implements `validate_model(model: dict[str, Any]) -> list[str]`.

- [ ] Add RED cases that reject absolute paths, `..`, symlinks, non-allowlisted paths, non-mapping YAML and duplicate/missing/reordered IDs.

```python
    def test_loader_rejects_paths_outside_exact_allowlist(self):
        validator = load_validator()
        for path in (
            Path("/tmp/input.yaml"),
            Path("../input.yaml"),
            Path("Governance/uncontrolled.yaml"),
        ):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    validator.load_repository_yaml(ROOT, path)
```

- [ ] Run the new test and confirm RED due to the missing implementation.

- [ ] Implement exact constants and safe loading:

```python
MODEL_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml")
MAPPING_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml")
MATRIX_PATH = Path("Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml")
FIXTURE_PATH = Path("Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml")
ALLOWED_PATHS = frozenset({MODEL_PATH, MAPPING_PATH, MATRIX_PATH, FIXTURE_PATH})
RISK_IDS = tuple(f"PR-RISK-{number:03d}" for number in range(1, 11))
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

def load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]:
    if relative_path.is_absolute() or relative_path not in ALLOWED_PATHS:
        raise ValueError("path is not allowlisted")
    root_resolved = root.resolve()
    candidate = root_resolved / relative_path
    if candidate.is_symlink() or candidate.resolve().parent not in {
        (root_resolved / path).parent.resolve() for path in ALLOWED_PATHS
    }:
        raise ValueError("path escapes its controlled directory")
    loaded = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("controlled YAML must be a mapping")
    return loaded
```

- [ ] Create the canonical model with these exact top-level keys:

```yaml
model_version: nonproduction_readiness_integration/v1
stage: "15"
stage_id: NR-01
allowed_scope:
  company: 汇沣电商
  brand: BUW
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
claims:
  risk_accepted: false
  pilot_authorized: false
  production_ready: false
  release_authorized: false
external_actions_performed: []
```

- [ ] Make `validate_model` enforce exact top-level keys, exact ordering, unique non-empty string IDs, exact false booleans, exact empty action list, exact risk state/owner and no extra fields in closed records.

- [ ] Run GREEN and regression:

```bash
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest discover -s Tests -p 'test_*.py'
```

Expected: all Stage 15 tests and all repository tests pass.

- [ ] Commit:

```bash
git add Tests/validate_aios_nonproduction_readiness.py Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): add closed readiness model"
```

## Task 3: Add the synthetic package and strict fixture validation

**Files**

- Create: `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Implements `validate_fixture(fixture: dict[str, Any]) -> list[str]`.
- Consumes one closed synthetic object graph.

- [ ] Add RED tests for the valid fixture and mutations covering cross-brand/company, wildcard scope, non-synthetic provenance, real-looking owner, credential/secret fields, external endpoints, connector requests, missing/reordered/duplicate component IDs, evidence IDs, risk IDs and gate IDs.

```python
    def test_valid_fixture_is_exactly_local_synthetic_and_complete(self):
        validator = load_validator()
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        self.assertEqual([], validator.validate_fixture(fixture))
        self.assertEqual({"company": "汇沣电商", "brand": "BUW"}, fixture["scope"])
        self.assertEqual("synthetic", fixture["data_contract"]["provenance"])
        self.assertEqual([], fixture["requested_external_actions"])
```

- [ ] Create the fixture with exact identity and complete component evidence:

```yaml
fixture_version: nonproduction_readiness_fixture/v1
scenario_id: NR-SYNTHETIC-LOCAL-001
scope: {company: 汇沣电商, brand: BUW}
environment:
  mode: local_synthetic_disposable
  external_endpoints: []
  connectors: []
  credentials: []
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
  - HG-SPEC-APPROVAL
  - HG-PLAN-APPROVAL
  - HG-EXECUTION-ASSIGNMENT
  - HG-IMPLEMENTATION-EVIDENCE
  - HG-NAMED-OWNER
  - HG-ARCH-SECURITY
  - HG-PRIVACY-DATA
  - HG-OPS-RECOVERY-INCIDENT-SUPPORT
  - HG-RISK-DISPOSITION
  - HG-PILOT-SCOPE
  - HG-PILOT-EVIDENCE
  - HG-RELEASE
requested_external_actions: []
claims: {risk_accepted: false, pilot_authorized: false, production_ready: false, release_authorized: false}
```

- [ ] Implement closed-record validation. Reject unknown keys, Python truthy substitutes for booleans, empty IDs, duplicates, reordering and any semantic authority token.

- [ ] Run focused adversarial tests, then the repository suite; expect all pass.

- [ ] Commit:

```bash
git add Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): validate synthetic integration package"
```

## Task 4: Implement the pure deterministic evaluator

**Files**

- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Implements `evaluate_nonproduction_readiness(model, fixture) -> dict[str, Any]`.
- Performs no I/O and mutates neither input.

- [ ] Add RED tests for the exact valid output, invalid `denied` output, repeated-call equality and deep-copy immutability.

```python
    def test_valid_package_stops_at_human_governance(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        result = validator.evaluate_nonproduction_readiness(model, fixture)
        self.assertEqual("needs_human_governance", result["result"])
        self.assertEqual(["LOCAL_SYNTHETIC_VALIDATION_PASSED", "HUMAN_GATES_REQUIRED"], result["reason_codes"])
        self.assertEqual([], result["external_actions_performed"])
        self.assertEqual(
            {"risk_accepted": False, "pilot_authorized": False, "production_ready": False, "release_authorized": False},
            result["claims"],
        )
```

- [ ] Implement stable helpers and evaluator:

```python
def _ordered_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))

def evaluate_nonproduction_readiness(model, fixture):
    model_errors = validate_model(model)
    fixture_errors = validate_fixture(fixture)
    errors = _ordered_unique([*model_errors, *fixture_errors])
    denied = bool(errors)
    return {
        "result": "denied" if denied else "needs_human_governance",
        "reason_codes": (
            [f"VALIDATION_ERROR:{error}" for error in errors]
            if denied
            else ["LOCAL_SYNTHETIC_VALIDATION_PASSED", "HUMAN_GATES_REQUIRED"]
        ),
        "evidence_refs": (
            [] if denied else [item["evidence_id"] for item in fixture["component_results"]]
        ),
        "required_human_gates": list(GATE_IDS),
        "risk_states": {risk_id: "open_blocked_unaccepted" for risk_id in RISK_IDS},
        "external_actions_performed": [],
        "claims": {
            "risk_accepted": False,
            "pilot_authorized": False,
            "production_ready": False,
            "release_authorized": False,
        },
    }
```

- [ ] Add an AST regression test proving the evaluator does not call `open`, `Path.read_text`, `Path.write_text`, `requests`, `socket`, `subprocess`, `os.environ`, clock or random APIs.

- [ ] Run focused tests twice and compare output; run the full repository suite.

- [ ] Commit:

```bash
git add Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): add pure fail-closed evaluator"
```

## Task 5: Prove environment, identity and data boundaries adversarially

**Files**

- Modify: `Tests/test_nonproduction_readiness.py`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`

**Interfaces**

- Strengthens `validate_fixture`.
- Produces stable denial reason codes for PR-RISK-001 through PR-RISK-004 and PR-RISK-009.

- [ ] Add table-driven RED mutations for:
  - environment mode `staging`, `production`, `shared` or empty;
  - HTTP/HTTPS endpoints, databases and connector names;
  - credential, token, password, key and secret fields at any depth;
  - non-simulated or wildcard principal;
  - permissions beyond the two exact synthetic permissions;
  - company `六合通`, brand `PC`, multiple brands, unknown or wildcard scope;
  - provenance other than exact `synthetic`;
  - personal/real/unclassified data;
  - retention or deletion policy changes.

```python
    def test_environment_identity_and_data_mutations_are_denied(self):
        mutations = (
            ("external endpoint", ("environment", "external_endpoints"), ["https://example.invalid"]),
            ("real credential", ("environment", "credentials"), ["token"]),
            ("PC boundary", ("scope", "brand"), "PC"),
            ("real provenance", ("data_contract", "provenance"), "real"),
        )
        for label, path, value in mutations:
            with self.subTest(label=label):
                fixture = self.valid_fixture_copy()
                self.set_path(fixture, path, value)
                self.assertEqual("denied", self.evaluate(fixture)["result"])
```

- [ ] Implement deterministic recursive forbidden-key/value scans with an exact lowercase token set and no fuzzy network lookup.

- [ ] Assert every denial retains all false claims and an empty external-action list.

- [ ] Run focused and repository suites; expect all pass.

- [ ] Commit:

```bash
git add Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): enforce synthetic scope boundaries"
```

## Task 6: Model local evidence, observation and audit integrity

**Files**

- Modify: `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml`
- Modify: `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Adds exact `evidence_store`, `observation` and `audit_records` closed mappings.
- Keeps all records synthetic and local.

- [ ] Add RED tests requiring:
  - append-only sequence numbers `[1, 2, 3]`;
  - non-empty unique deterministic record IDs;
  - exact SHA-256 lowercase checksums;
  - observation delivery `local_decision_only`;
  - paging, ticketing and external delivery all false;
  - evidence IDs matching the model and component results exactly.

- [ ] Add the exact fixture structures:

```yaml
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
```

The three values are the deterministic SHA-256 digests of the canonical UTF-8 payloads `environment`, `evidence` and `observation`; tests must recompute rather than merely compare copied strings.

- [ ] Reject gaps, duplicates, reordering, malformed checksums, forged evidence IDs, external delivery and non-boolean values.

- [ ] Run focused and full tests; expect all pass.

- [ ] Commit:

```bash
git add Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): validate local evidence integrity"
```

## Task 7: Model rollback, recovery, incident tabletop and support handoff

**Files**

- Modify: `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml`
- Modify: `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Adds four closed synthetic result mappings.
- Prepares evidence only; performs no rollback, incident or support action outside disposable local state.

- [ ] Add RED cases for incomplete cleanup, pre/post checksum mismatch, absent restore verification, real incident wording, real owner, real communications, created tickets and SLA/coverage claims.

- [ ] Add exact fixture records:

```yaml
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

Both recovery values are the deterministic SHA-256 digest of the canonical UTF-8 payload `synthetic-state`; tests must recompute the digest and require equality.

- [ ] Validate exact keys/types/values and fail closed on unknown action fields.

- [ ] Prove the evaluator distrusts a fixture-supplied `status: passed` when underlying recovery, incident or support facts are invalid.

- [ ] Run focused and repository suites; expect all pass.

- [ ] Commit:

```bash
git add Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): add synthetic recovery and handoff evidence"
```

## Task 8: Add exact Stage 10–14 mapping and acceptance matrix

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml`
- Create: `Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Extends `validate_repository(root: Path) -> list[str]`.
- Cross-checks exact risk/evidence/gate identities across all controlled assets.

- [ ] Add RED tests requiring mapping risk order PR-RISK-001 through PR-RISK-010, exact states, exact evidence references and archived Stage 11–14 design-only dependencies.

- [ ] Create mapping records with these exact risk/evidence assignments:

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

- [ ] Create one acceptance row per requirement category with exact keys:

```yaml
matrix_version: nonproduction_readiness_acceptance/v1
requirements:
  - requirement_id: AC-IDENTITY
    test_ids: [test_environment_identity_and_data_mutations_are_denied]
    evidence_ids: [EV-IDENTITY]
    local_synthetic_proof: true
    real_world_authority: false
authority_claims:
  risk_accepted: false
  pilot_authorized: false
  production_ready: false
  release_authorized: false
```

Add rows `AC-ENVIRONMENT`, `AC-DATA`, `AC-EVIDENCE`, `AC-OBSERVATION`, `AC-RECOVERY`, `AC-INCIDENT`, `AC-SUPPORT`, `AC-RISK-MAPPING` and `AC-AUTHORITY` with their exact test/evidence references.

- [ ] Implement cross-file set, count, order and uniqueness comparisons. Never trust counts declared inside YAML.

- [ ] Add frozen-source tests reading Stage 10–14 registries/assets and asserting no implementation commit modifies them.

- [ ] Export `STAGE15_APPROVED_PLAN_HEAD` from the exact immutable approval recorded in Issue #40, validate it with `git cat-file -e "$STAGE15_APPROVED_PLAN_HEAD^{commit}"`, run `git diff --name-only "$STAGE15_APPROVED_PLAN_HEAD"...HEAD`, and reject any path outside the plan allowlist.

- [ ] Run focused/full tests and commit:

```bash
git add Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): trace blocked risks to local evidence"
```

## Task 9: Add policy and reproducible validation guidance

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Integration-v1.md`
- Create: `Tests/AIOS-Nonproduction-Readiness-Validation.md`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- `validate_repository` checks required policy/guide tokens and asset presence.
- Documents the bounded meaning of test evidence.

- [ ] Add RED tests requiring the policy to answer all six system questions and explicitly state:
  - BUW/汇沣电商 only;
  - PC/六合通 excluded;
  - local synthetic disposable boundary;
  - Stage 10 `BLOCKED / NO-GO`;
  - exact two-result ceiling;
  - twelve ordered human gates;
  - stop/withdrawal conditions;
  - no external actions;
  - passing does not prove real pilot or production readiness.

- [ ] Write the policy with sections:
  `Business loop`, `Core objects`, `Data flow`, `Operators`,
  `AI and human judgment boundary`, `Proof of operation`,
  `Authority ceiling`, `Component contracts`, `Risk mapping`,
  `Stop and withdrawal`, `Lifecycle`.

- [ ] Write the validation guide with exact commands:

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest discover -s Tests -p 'test_*.py'
python3 Tests/validate_aios_workflow_schema.py
python3 -m compileall -q Tests
git diff --check
```

The guide must state expected success text `AIOS non-production readiness validation passed` and explain that success proves repository-contained synthetic behavior only.

- [ ] Make the validator CLI call `validate_repository(Path(__file__).resolve().parents[1])`, print stable errors one per line, exit `1` on errors and print the exact success text on exit `0`.

- [ ] Run every documented command; expect all pass.

- [ ] Commit:

```bash
git add Governance/AIOS-Nonproduction-Readiness-Integration-v1.md Tests/AIOS-Nonproduction-Readiness-Validation.md Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "docs(stage15): add bounded integration policy"
```

## Task 10: Add pull-request-only read-only CI

**Files**

- Create: `.github/workflows/validate-aios-nonproduction-readiness.yml`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Runs validation only for pull requests.
- Grants only `contents: read`.

- [ ] Add a RED workflow test requiring:

```python
    def test_ci_is_pull_request_only_and_read_only(self):
        workflow = (ROOT / ".github/workflows/validate-aios-nonproduction-readiness.yml").read_text()
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        for denied in ("contents: write", "pull-requests: write", "issues: write", "git push", "deployment"):
            self.assertNotIn(denied, workflow)
```

- [ ] Create the exact workflow:

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
      - run: pip install pyyaml
      - run: python3 Tests/validate_aios_nonproduction_readiness.py
      - run: python3 -m unittest Tests.test_nonproduction_readiness -v
      - run: python3 -m unittest discover -s Tests -p 'test_*.py'
      - run: python3 Tests/validate_aios_workflow_schema.py
      - run: python3 -m compileall -q Tests
```

- [ ] Validate the workflow through the repository Workflow Schema validator and full tests.

- [ ] Commit:

```bash
git add .github/workflows/validate-aios-nonproduction-readiness.yml Tests/test_nonproduction_readiness.py
git commit -m "ci(stage15): validate local integration proof"
```

## Task 11: Complete adversarial, determinism and frozen-boundary regression

**Files**

- Modify: `Tests/test_nonproduction_readiness.py`
- Modify: `Tests/validate_aios_nonproduction_readiness.py`

**Interfaces**

- Finalizes negative coverage and stable error ordering.
- Proves archived controls and authority boundaries remain unchanged.

- [ ] Add RED cases for every specified attack class:
  - missing, duplicate, reordered and unknown risk/gate/evidence IDs;
  - mapping counts that disagree with actual entries;
  - YAML booleans replaced by strings or integers;
  - aliases, merge keys and unknown fields used to smuggle authority;
  - fixture `status: passed` with invalid underlying facts;
  - changed checksums and incomplete cleanup/rollback;
  - real owner names and non-abstract routes;
  - non-empty external-action lists;
  - accepted/closed/waived risk states;
  - `ready`, `approved`, `accepted`, `go`, `eligible`, `proceed`, `pilot_ready`,
    `pilot_authorized`, `production_ready` or `released` anywhere in decision fields;
  - mutation attempts against evaluator inputs and prior returned output;
  - repeated execution under different current directories.

- [ ] Normalize every error through stable path-prefixed codes, sort only where the contract declares order irrelevant, and preserve declared order elsewhere.

- [ ] Verify:

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest discover -s Tests -p 'test_*.py'
python3 Tests/validate_aios_workflow_schema.py
python3 -m compileall -q Tests
git diff --check
git status --short
```

Expected: validators/tests/compilation/diff pass; status contains only planned implementation paths.

- [ ] Independently compare frozen Stage 10–14 paths against the approved plan head:

```bash
test -n "$STAGE15_APPROVED_PLAN_HEAD"
git cat-file -e "$STAGE15_APPROVED_PLAN_HEAD^{commit}"
git diff --exit-code "$STAGE15_APPROVED_PLAN_HEAD"...HEAD -- Governance/AIOS-Production-Readiness-v1.md Governance/AIOS-Architecture-Security-Foundations-v1.md Governance/AIOS-Privacy-Data-Governance-v1.md Governance/AIOS-Operational-Resilience-v1.md Governance/AIOS-Support-Controlled-Pilot-v1.md
```

Expected: the recorded commit resolves; the frozen-path comparison has no output and exits `0`. Do not derive this value from a moving branch name.

- [ ] Commit:

```bash
git add Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): harden readiness validation"
```

## Task 12: Report exact implementation evidence without self-approval

**Files**

- Modify: `Governance/AIOS-Stage-Registry.md`
- Modify: `Governance/AIOS-Project-Registry.md`
- Modify: `Tests/test_project_governance.py`
- Modify only if current-lifecycle assertions require it:
  - `Tests/validate_aios_operational_resilience.py`
  - `Tests/test_operational_resilience.py`
  - `Tests/validate_aios_support_controlled_pilot.py`
  - `Tests/test_support_controlled_pilot.py`

**Interfaces**

- Moves only Stage 15 `Planned` to `Reported`.
- Prepares the Mandatory Return at the exact remote head.

- [ ] Add lifecycle RED tests requiring:
  - exactly one Stage 15 row;
  - assigned Execution Task and implementation branch;
  - `| Reported |`;
  - Issue #40 and Draft PR #41;
  - exact test/CI evidence;
  - `needs_human_governance`;
  - `implementation evidence awaits independent human review`;
  - no `Reviewed`, `Archived`, pilot authorization, production readiness or risk acceptance;
  - Stage 10 remains `BLOCKED / NO-GO`;
  - Stages 11–14 remain `Archived`.

- [ ] Update only current lifecycle text and append-only change logs. Do not rewrite archived evidence.

- [ ] Run the complete evidence bundle:

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
```

Expected: all commands pass; only plan-authorized paths differ from the approved plan head.

- [ ] Commit the Reported transition:

```bash
git add Governance/AIOS-Stage-Registry.md Governance/AIOS-Project-Registry.md Tests/test_project_governance.py Tests/validate_aios_operational_resilience.py Tests/test_operational_resilience.py Tests/validate_aios_support_controlled_pilot.py Tests/test_support_controlled_pilot.py
git commit -m "docs(stage15): report nonproduction readiness evidence"
```

Stage only the lifecycle compatibility files that actually changed.

- [ ] Push the assigned implementation branch to Draft PR #41 or a separately authorized implementation PR, then record:

```bash
git rev-parse HEAD
git branch --show-current
git ls-remote origin "refs/heads/$(git branch --show-current)"
gh pr view --json isDraft,state,mergeStateStatus,headRefOid,url
gh pr checks
```

Expected: local and remote heads match; PR is Draft/open/unmerged; every required final-head check succeeds.

- [ ] Clone the exact remote branch into a fresh temporary directory and repeat the complete evidence bundle. Compare every changed remote file against the tested local file.

- [ ] Post the Mandatory Return to Issue #40 with:
  - exact remote head and tree;
  - assigned Execution Task, branch and Draft PR;
  - changed-file allowlist and file-count parity;
  - targeted/full/Project Governance test counts;
  - validator, compilation, diff and frozen-boundary results;
  - final-head CI links;
  - lifecycle `Reported`;
  - maximum result `needs_human_governance`;
  - explicit confirmation of no external actions, real data, credentials, permissions, owners, risk acceptance, pilot, production, release, merge, archive or Stage 16.

- [ ] Stop. Do not mark Stage 15 `Reviewed`, merge, publish, archive, close Issue #40, start a real pilot or start Stage 16.

---

## Plan self-review checklist

- [ ] Every future deliverable in the approved specification has one exact path and one responsible task.
- [ ] All nine component boundaries are covered: environment, identity, data, evidence, observation, recovery, incident, support and evaluator.
- [ ] PR-RISK-001 through PR-RISK-010 appear exactly once in canonical ordered collections and remain `open_blocked_unaccepted`.
- [ ] All twelve human gates appear in exact order and remain unauthorized.
- [ ] The valid result cannot exceed `needs_human_governance`; invalid input is `denied`.
- [ ] Output authority claims are exact booleans and always false; external actions are exactly empty.
- [ ] Positive, adversarial, determinism, immutability and frozen-boundary tests are explicit.
- [ ] Every task contains exact files, interfaces, RED, GREEN, verification and commit steps.
- [ ] No unresolved planning markers or symbolic target values remain in the executable steps.
- [ ] The plan does not assign an Execution Task, implementation branch, real owner or real-world authority.
- [ ] Implementation stops at Stage 15 `Reported` + Mandatory Return.

## Human decisions still required after this plan

1. Independently approve or return this exact implementation-plan head.
2. Assign exactly one dedicated Execution Task and one implementation branch.
3. Select an implementation execution mode; no subagent dispatch is authorized by this plan.
4. Independently review the exact implementation head and Mandatory Return.
5. Decide merge/publication separately.
6. Decide archival and Issue #40 closure separately after post-publication validation.
7. Decide any real pilot scope, owners, data, systems, risk dispositions and release separately.
