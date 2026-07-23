# Support and Controlled Pilot Design v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a repository-only, synthetic Support + Controlled Pilot Eligibility Model whose deterministic evaluator denies malformed or unsafe inputs and returns only `needs_human_governance` for an otherwise-valid BUW/汇沣电商 candidate.

**Architecture:** A safe repository loader parses an exact allowlist of YAML assets, then passes in-memory mappings into a pure evaluator. The evaluator validates one atomically versioned object graph, applies most-restrictive-wins rules, and emits a normalized decision without filesystem, network, clock, environment, subprocess, connector or external-write access. Policy, Stage 10–13 mapping and an acceptance matrix make the machine contract independently reviewable; PR-only read-only CI proves synthetic behavior but grants no pilot authority.

**Tech Stack:** Python 3 standard library, PyYAML `safe_load`, `unittest`, YAML governance assets, Markdown policy and validation guide, GitHub Actions.

## Global Constraints

- Start only after the Governance Thread independently approves this plan in Issue #36 and Draft PR #37.
- Work only from the approved plan head on `feat/aios-support-controlled-pilot-design-v1`; record the exact starting head before editing.
- The only business pair is company `汇沣电商` and brand `BUW`. `PC`, `六合通`, combined scopes, aliases and wildcards fail closed.
- All inputs and fixtures are repository-controlled and synthetic. Never access or represent a real customer, store, order, employee, owner, support ticket, monitor, infrastructure resource, database, API, connector, credential or external action.
- Every real-owner field is exactly `unassigned / governance decision required`.
- Stage 10 remains `BLOCKED / NO-GO`; its risks remain blocked/open and unaccepted. Stage 11–13 assets and design-only boundaries remain frozen.
- The evaluator has exactly two results: invalid inputs return `denied`; an otherwise-valid input returns `needs_human_governance`.
- Reject permission-like results or fields, including `pilot_authorized`, `approved`, `ready`, `released`, `eligible`, `go`, `accepted`, `proceed`, `pilot_ready`, `production_ready` and semantic equivalents.
- No task authorizes a real pilot, named owner, risk acceptance, merge, publication, release or archive.
- Each task begins with an exact failing test, makes the smallest implementation needed for that test, proves the pass, and ends with its own commit.
- Implementation completion may reach only Draft PR + Stage 14 `Reported` + Mandatory Return. Governance alone may review, merge, publish, archive or authorize any real pilot later.

## Plan authority and starting state

| Field | Exact value |
|---|---|
| Issue | `#36` |
| Execution Thread | `019f8c92-e709-7a83-b06c-fa014cf0b216` |
| Branch | `feat/aios-support-controlled-pilot-design-v1` |
| Draft PR | `#37` |
| Approved written-spec head | `c312db694afc40b5ec268f577c6c05a664b98eef` |
| Lifecycle before implementation | Stage 14 `Executing`; implementation plan awaiting independent human approval |
| Maximum implementation lifecycle | Draft PR + Stage 14 `Reported` + Mandatory Return |
| Real owner state | `unassigned / governance decision required` |
| Real pilot authority | none; a separate bounded human Governance Thread decision is required |

---

## Exact file structure and single responsibilities

### Create

- `Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml` — single canonical versioned contract for identity, order, scope, authority, objects, gates and outcomes.
- `Governance/AIOS-Support-Controlled-Pilot-v1.md` — policy for the business loop, authority boundaries, failure rules and lifecycle.
- `Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml` — immutable trace from each Stage 10 risk and Stage 11–13 dependency to Stage 14 without accepting or closing them.
- `Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml` — requirement-to-evidence matrix with every pilot/release authority flag false.
- `Tests/Fixtures/support-controlled-pilot/synthetic-support-pilot-candidate.yaml` — sole otherwise-valid synthetic input bundle.
- `Tests/validate_aios_support_controlled_pilot.py` — safe loader, exact model validation, pure evaluator and repository validator.
- `Tests/test_support_controlled_pilot.py` — positive, determinism, immutability and adversarial tests.
- `Tests/AIOS-Support-Controlled-Pilot-Validation.md` — reproducible commands and bounded meaning of pass.
- `.github/workflows/validate-aios-support-controlled-pilot.yml` — pull-request-only, read-only CI.

### Modify only at implementation completion

- `Governance/AIOS-Stage-Registry.md` — record Stage 14 `Reported`, exact evidence and Mandatory Return without changing Stage 10–13.
- `Governance/AIOS-Project-Registry.md` — synchronize lifecycle and independent review gate.
- `Tests/validate_aios_operational_resilience.py` — update only the current-registry forward lifecycle assertion.
- `Tests/test_operational_resilience.py` — regress the authorized Reported transition and reject Reviewed/Archived/pilot authority.
- `Tests/test_project_governance.py` — assert exact Stage 13 archive and Stage 14 Reported evidence.

### Consume without modification

- `docs/superpowers/specs/2026-07-23-support-controlled-pilot-design-v1.md` — approved normative specification.
- Stage 10 production-readiness risk register — risk identities and `BLOCKED / NO-GO`.
- Stage 11 architecture/security, Stage 12 privacy/data-governance and Stage 13 operational-resilience assets — archived design evidence and frozen authority limits.
- `.github/workflows/validate-aios-workflow-schema.yml` and `Tests/validate_aios_workflow_schema.py` — workflow-schema contract.

---

## Task 1: Pin the model contract with failing structural tests

**Files**

- Create: `Tests/test_support_controlled_pilot.py`
- Test: `Tests/test_support_controlled_pilot.py`

**Interfaces**

- Consumes: approved specification and future canonical model path.
- Produces: executable expectations for `validate_model(model: dict[str, Any]) -> list[str]`.

- [ ] Record the approved start and absence of implementation assets:

```bash
git rev-parse HEAD
git status --short
test ! -e Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml
test ! -e Tests/validate_aios_support_controlled_pilot.py
```

Expected: approved plan head printed, clean status, both absence checks exit `0`.

- [ ] Write the first exact failing test:

```python
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml"
VALIDATOR = ROOT / "Tests/validate_aios_support_controlled_pilot.py"

def load_validator():
    spec = importlib.util.spec_from_file_location("support_pilot_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

class SupportControlledPilotTests(unittest.TestCase):
    def test_model_has_exact_identity_boundary_outcomes_and_gate_order(self):
        validator = load_validator()
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        self.assertEqual([], validator.validate_model(model))
        self.assertEqual("support_controlled_pilot_eligibility/v1", model["model_version"])
        self.assertEqual({"company": "汇沣电商", "brand": "BUW"}, model["allowed_scope"])
        self.assertEqual(["PC", "六合通"], model["excluded_entities"])
        self.assertEqual(["denied", "needs_human_governance"], model["allowed_results"])
        self.assertEqual(
            [
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
            ],
            [gate["gate_id"] for gate in model["human_gates"]],
        )
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_model_has_exact_identity_boundary_outcomes_and_gate_order -v
```

Expected: `ERROR` because validator/model is absent.

- [ ] Commit the failing test:

```bash
git add Tests/test_support_controlled_pilot.py
git commit -m "test(stage14): pin support pilot model contract"
```

Expected: one commit with only the test.

## Task 2: Implement the safe loader and canonical YAML model

**Files**

- Create: `Tests/validate_aios_support_controlled_pilot.py`
- Create: `Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml`
- Modify/Test: `Tests/test_support_controlled_pilot.py`

**Interfaces**

- Consumes: repository root and exact allowlisted repository-relative `Path`.
- Produces: `load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]`; `validate_model(model: dict[str, Any]) -> list[str]`.

- [ ] Add loader escape/allowlist RED test:

```python
    def test_loader_accepts_only_allowlisted_repository_yaml(self):
        validator = load_validator()
        loaded = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        self.assertEqual("support_controlled_pilot_eligibility/v1", loaded["model_version"])
        for unsafe in (
            Path("../outside.yaml"),
            Path("Governance/AIOS-Stage-Registry.md"),
            Path("/tmp/input.yaml"),
        ):
            with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                validator.load_repository_yaml(ROOT, unsafe)
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_loader_accepts_only_allowlisted_repository_yaml -v
```

Expected: `ERROR` because the loader is absent.

- [ ] Implement safe loading and validation skeleton:

```python
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml")
FIXTURE_PATH = Path("Tests/Fixtures/support-controlled-pilot/synthetic-support-pilot-candidate.yaml")
ALLOWED_YAML_PATHS = frozenset({MODEL_PATH, FIXTURE_PATH})
MODEL_VERSION = "support_controlled_pilot_eligibility/v1"
OWNER_STATE = "unassigned / governance decision required"
ALLOWED_RESULTS = ["denied", "needs_human_governance"]

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

def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if model.get("model_version") != MODEL_VERSION:
        errors.append("invalid_model_version")
    if model.get("allowed_scope") != {"company": "汇沣电商", "brand": "BUW"}:
        errors.append("invalid_allowed_scope")
    if model.get("excluded_entities") != ["PC", "六合通"]:
        errors.append("invalid_excluded_entities")
    if model.get("allowed_results") != ALLOWED_RESULTS:
        errors.append("invalid_allowed_results")
    return errors
```

- [ ] Create canonical YAML with exact key/order/authority:

```yaml
model_version: support_controlled_pilot_eligibility/v1
stage: 14
stage_id: PS-01
issue: 36
execution_thread: 019f8c92-e709-7a83-b06c-fa014cf0b216
synthetic_only: true
repository_controlled_fixtures_only: true
allowed_scope: {company: 汇沣电商, brand: BUW}
excluded_entities: [PC, 六合通]
owner_state: unassigned / governance decision required
allowed_results: [denied, needs_human_governance]
authority:
  pilot_authorized: false
  release_authorized: false
  production_action_allowed: false
  staging_action_allowed: false
  external_action_allowed: false
id_prefixes:
  support_request: SR-SYN-
  support_case: SC-SYN-
  pilot_candidate: PCAN-SYN-
  scope: SCOPE-SYN-
  success_metric: SM-SYN-
  guardrail_metric: GM-SYN-
  evidence_bundle: EVB-SYN-
  audit_record: AUD-SYN-
  decision_record: DEC-SYN-
  human_gate: HG-
human_gates:
  - {gate_id: HG-WRITTEN-SPEC-APPROVAL}
  - {gate_id: HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE}
  - {gate_id: HG-NAMED-OWNER-APPOINTMENT}
  - {gate_id: HG-REAL-SCOPE-AND-DATA-AUTHORIZATION}
  - {gate_id: HG-STAGE10-RISK-DISPOSITION}
  - {gate_id: HG-STAGE11-13-EVIDENCE-ACCEPTANCE}
  - {gate_id: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {gate_id: HG-METRIC-AND-EVIDENCE-ACCEPTANCE}
  - {gate_id: HG-BOUNDED-AUTHORITY-DEFINITION}
  - {gate_id: HG-REAL-PILOT-ENTRY-DECISION}
```

Append these exact ordered contracts to the same YAML file; the validator treats every shown key and list order as closed:

```yaml
support_requests:
  - support_request_id: SR-SYN-001
    model_version: support_controlled_pilot_eligibility/v1
    synthetic: true
    pilot_candidate_id: PCAN-SYN-001
    scope_id: SCOPE-SYN-001
support_cases:
  - support_case_id: SC-SYN-001
    model_version: support_controlled_pilot_eligibility/v1
    synthetic: true
    support_request_id: SR-SYN-001
    support_model_id: SUP-SYN-001
    escalation_path_id: ESC-SYN-001
pilot_candidates:
  - pilot_candidate_id: PCAN-SYN-001
    model_version: support_controlled_pilot_eligibility/v1
    synthetic: true
    scope_id: SCOPE-SYN-001
    entry_criteria_ids: [ENTRY-SYN-001]
    exit_criteria_ids: [EXIT-SYN-001]
    stop_condition_ids: [STOP-SYN-001]
    withdrawal_condition_ids: [WITHDRAW-SYN-001]
scopes:
  - scope_id: SCOPE-SYN-001
    model_version: support_controlled_pilot_eligibility/v1
    synthetic: true
    company: 汇沣电商
    brand: BUW
    workload_class: SYNTHETIC-SUPPORT-EVALUATION
    duration_design_bound: one synthetic evaluation
    volume_design_bound: one synthetic candidate
    permitted_actions: [in_memory_evaluation]
    excluded_actions: [external_read, external_write, real_pilot]
entry_criteria:
  - criterion_id: ENTRY-SYN-001
    required_gate_ids: [HG-WRITTEN-SPEC-APPROVAL, HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE, HG-NAMED-OWNER-APPOINTMENT, HG-REAL-SCOPE-AND-DATA-AUTHORIZATION, HG-STAGE10-RISK-DISPOSITION, HG-STAGE11-13-EVIDENCE-ACCEPTANCE, HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE, HG-METRIC-AND-EVIDENCE-ACCEPTANCE, HG-BOUNDED-AUTHORITY-DEFINITION, HG-REAL-PILOT-ENTRY-DECISION]
    real_world_satisfied: false
exit_criteria:
  - criterion_id: EXIT-SYN-001
    required_evidence: [scope_reconciliation, metric_reconciliation, case_disposition, data_access_disposition, human_closure]
    evaluator_may_close_real_pilot: false
stop_conditions:
  - condition_id: STOP-SYN-001
    triggers: [unknown_state, identity_mismatch, suspected_real_data, cross_boundary, unresolved_stage10_risk, missing_stage11_13_evidence, support_gap, escalation_gap, guardrail_breach, metric_source_failure, audit_gap, authority_loss, external_action]
    default_action: no_further_action_pending_human_decision
withdrawal_conditions:
  - condition_id: WITHDRAW-SYN-001
    required_capabilities: [intake, acknowledgement, stop_further_activity, preserve_evidence, dispose_scope_data_access, human_closure]
    real_roles_assigned: false
support_models:
  - support_model_id: SUP-SYN-001
    owner_state: unassigned / governance decision required
    required_elements: [intake, taxonomy, severity, coverage_design, acknowledgement_target, investigation_handoff, closure, training, runbook, evidence_retention, service_target_review]
escalation_paths:
  - escalation_path_id: ESC-SYN-001
    owner_state: unassigned / governance decision required
    ordered_functions: [support_triage, technical_review, security_privacy_review_when_triggered, operational_resilience_review_when_triggered, governance_thread_decision]
success_metrics:
  - metric_id: SM-SYN-001
    definition: synthetic support intake completeness
    unit: ratio
    direction: higher_is_better
    source: repository_synthetic_fixture
    observation_window: one synthetic evaluation
    threshold_type: exact
    threshold: 1.0
    missing_data_behavior: deny
    evidence_ref: EVID-SYN-METRICS-AUDIT
    owner_state: unassigned / governance decision required
  - {metric_id: SM-SYN-002, definition: bounded synthetic task quality, unit: ratio, direction: higher_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: minimum, threshold: 1.0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
guardrail_metrics:
  - {metric_id: GM-SYN-001, definition: acknowledgement evidence completeness, unit: ratio, direction: higher_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: exact, threshold: 1.0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-002, definition: unresolved synthetic support cases, unit: count, direction: lower_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: maximum, threshold: 0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-003, definition: escalation timeliness evidence completeness, unit: ratio, direction: higher_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: exact, threshold: 1.0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-004, definition: synthetic errors and exceptions, unit: count, direction: lower_is_better, source: evaluator_decision, observation_window: one synthetic evaluation, threshold_type: maximum, threshold: 0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-005, definition: cross-boundary events, unit: count, direction: lower_is_better, source: evaluator_decision, observation_window: one synthetic evaluation, threshold_type: maximum, threshold: 0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-006, definition: external write attempts, unit: count, direction: lower_is_better, source: evaluator_decision, observation_window: one synthetic evaluation, threshold_type: maximum, threshold: 0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-007, definition: stop responsiveness evidence completeness, unit: ratio, direction: higher_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: exact, threshold: 1.0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-008, definition: withdrawal completion evidence, unit: ratio, direction: higher_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: exact, threshold: 1.0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
  - {metric_id: GM-SYN-009, definition: evidence bundle completeness, unit: ratio, direction: higher_is_better, source: repository_synthetic_fixture, observation_window: one synthetic evaluation, threshold_type: exact, threshold: 1.0, missing_data_behavior: deny, evidence_ref: EVID-SYN-METRICS-AUDIT, owner_state: unassigned / governance decision required}
evidence_contract:
  evidence_bundle_id_prefix: EVB-SYN-
  version_format: semantic_version
  required_evidence_refs: [EVID-SYN-STAGE10-RISK-REGISTER, EVID-SYN-STAGE11-ARCHITECTURE-SECURITY, EVID-SYN-STAGE12-PRIVACY-DATA, EVID-SYN-STAGE13-OPERATIONAL-RESILIENCE, EVID-SYN-SUPPORT-STOP-WITHDRAWAL, EVID-SYN-METRICS-AUDIT]
  content_hash_required: true
  human_acceptance_inferred: false
audit_contract:
  record_id: AUD-SYN-001
  synthetic: true
  persistent_store: false
decision_contract:
  record_id: DEC-SYN-001
  synthetic: true
  human_decision: null
  pilot_authorized: false
```

`validate_model` defines the exact top-level key tuple from this document, compares `list(model)` to that tuple, applies the ID-prefix rules to every collection, verifies all references, and rejects every extension key.

- [ ] Add exact prefix, uniqueness, canonical-order, false-authority and owner checks:

```python
def _append_once(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)

def _ids_are_unique_and_prefixed(
    items: list[dict[str, Any]], key: str, prefix: str
) -> bool:
    ids = [item.get(key) for item in items]
    return (
        all(isinstance(value, str) and value.startswith(prefix) for value in ids)
        and len(ids) == len(set(ids))
    )
```

- [ ] Run GREEN:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
```

Expected: current tests all `OK`.

- [ ] Commit:

```bash
git add Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml Tests/validate_aios_support_controlled_pilot.py Tests/test_support_controlled_pilot.py
git commit -m "feat(stage14): add canonical eligibility model and safe loader"
```

## Task 3: Drive the pure evaluator with one synthetic fixture

**Files**

- Create: `Tests/Fixtures/support-controlled-pilot/synthetic-support-pilot-candidate.yaml`
- Modify/Test: `Tests/test_support_controlled_pilot.py`
- Modify: `Tests/validate_aios_support_controlled_pilot.py`

**Interfaces**

- Consumes: validated model, request mapping, evidence-bundle mapping.
- Produces: `evaluate_eligibility(model: dict[str, Any], request: dict[str, Any], evidence_bundle: dict[str, Any]) -> dict[str, Any]`.

- [ ] Add RED test for result shape, determinism and immutability:

```python
import copy

    def test_valid_fixture_needs_human_governance_without_side_effects(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        before = copy.deepcopy((model, fixture))
        first = validator.evaluate_eligibility(model, fixture["request"], fixture["evidence_bundle"])
        second = validator.evaluate_eligibility(model, fixture["request"], fixture["evidence_bundle"])
        self.assertEqual(first, second)
        self.assertEqual(before, (model, fixture))
        self.assertEqual("needs_human_governance", first["result"])
        self.assertEqual([], first["reason_codes"])
        self.assertEqual([g["gate_id"] for g in model["human_gates"]], first["required_human_gates"])
        self.assertEqual([], first["external_actions_performed"])
        self.assertEqual(
            {
                "result", "model_version", "support_request_id", "support_case_id",
                "pilot_candidate_id", "scope_id", "reason_codes", "required_human_gates",
                "evidence_refs", "upstream_risk_states", "audit_record", "decision_record",
                "external_actions_performed",
            },
            set(first),
        )
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_valid_fixture_needs_human_governance_without_side_effects -v
```

Expected: `ERROR` because fixture/evaluator is absent.

- [ ] Create exact synthetic fixture:

```yaml
fixture_version: support_controlled_pilot_fixture/v1
synthetic: true
repository_controlled: true
request:
  model_version: support_controlled_pilot_eligibility/v1
  support_request_id: SR-SYN-001
  support_case_id: SC-SYN-001
  pilot_candidate_id: PCAN-SYN-001
  scope_id: SCOPE-SYN-001
  company: 汇沣电商
  brand: BUW
  synthetic_workload_class: SYNTHETIC-SUPPORT-EVALUATION
  owner_state: unassigned / governance decision required
  external_actions_performed: []
evidence_bundle:
  model_version: support_controlled_pilot_eligibility/v1
  evidence_bundle_id: EVB-SYN-001
  evidence_bundle_version: 1.0.0
  synthetic: true
  repository_controlled: true
  evidence_refs:
    - EVID-SYN-STAGE10-RISK-REGISTER
    - EVID-SYN-STAGE11-ARCHITECTURE-SECURITY
    - EVID-SYN-STAGE12-PRIVACY-DATA
    - EVID-SYN-STAGE13-OPERATIONAL-RESILIENCE
    - EVID-SYN-SUPPORT-STOP-WITHDRAWAL
    - EVID-SYN-METRICS-AUDIT
  evidence_items:
    - {evidence_id: EVID-SYN-STAGE10-RISK-REGISTER, synthetic_content: EVID-SYN-STAGE10-RISK-REGISTER, hash_basis: synthetic_content_utf8, repository_path: Governance/AIOS-Production-Readiness-Risk-Register-v1.yaml, content_sha256: 3d7f83dce1b454e06bf6c5c66637abc88e990fd73ad715fdfbfa3685cf22ede4, human_accepted: false}
    - {evidence_id: EVID-SYN-STAGE11-ARCHITECTURE-SECURITY, synthetic_content: EVID-SYN-STAGE11-ARCHITECTURE-SECURITY, hash_basis: synthetic_content_utf8, repository_path: Governance/AIOS-Architecture-Security-Model-v1.yaml, content_sha256: 3484042600c1186c2ef2901a34a15f530d75e5e79a5fda34ecf86c1a2d10aea9, human_accepted: false}
    - {evidence_id: EVID-SYN-STAGE12-PRIVACY-DATA, synthetic_content: EVID-SYN-STAGE12-PRIVACY-DATA, hash_basis: synthetic_content_utf8, repository_path: Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml, content_sha256: a82f13e3fa739b020bd2ee7d46c3519093bcdf23aae2edf5cc30813a8da50899, human_accepted: false}
    - {evidence_id: EVID-SYN-STAGE13-OPERATIONAL-RESILIENCE, synthetic_content: EVID-SYN-STAGE13-OPERATIONAL-RESILIENCE, hash_basis: synthetic_content_utf8, repository_path: Governance/AIOS-Operational-Resilience-Model-v1.yaml, content_sha256: 7e25b112c97b0c1b932308c44f56f363a0c0ae61158f3818bb878c7413759cbc, human_accepted: false}
    - {evidence_id: EVID-SYN-SUPPORT-STOP-WITHDRAWAL, synthetic_content: EVID-SYN-SUPPORT-STOP-WITHDRAWAL, hash_basis: synthetic_content_utf8, repository_path: Governance/AIOS-Support-Controlled-Pilot-Model-v1.yaml, content_sha256: 9890de682c5b9a8ab0a8b93907e291ab25d9f568f8a4f74ee57a1771c8127a76, human_accepted: false}
    - {evidence_id: EVID-SYN-METRICS-AUDIT, synthetic_content: EVID-SYN-METRICS-AUDIT, hash_basis: synthetic_content_utf8, repository_path: Tests/Fixtures/support-controlled-pilot/synthetic-support-pilot-candidate.yaml, content_sha256: 0058fa48f1a5c7d87a8867b7c966fc2255200d4074b120563f912ae497fc4fd6, human_accepted: false}
  upstream_risk_states:
    PR-RISK-001: blocked
    PR-RISK-002: blocked
    PR-RISK-003: blocked
    PR-RISK-004: blocked
    PR-RISK-005: blocked
    PR-RISK-006: blocked
    PR-RISK-007: blocked
    PR-RISK-008: blocked
    PR-RISK-009: open
    PR-RISK-010: open
  external_actions_performed: []
```

- [ ] Implement a total pure evaluator using new output mappings:

```python
def evaluate_eligibility(
    model: dict[str, Any],
    request: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    for error in validate_model(model):
        _append_once(reasons, f"MODEL_{error.upper()}")
    if request.get("model_version") != MODEL_VERSION or evidence_bundle.get("model_version") != MODEL_VERSION:
        _append_once(reasons, "VERSION_MISMATCH")
    if (request.get("company"), request.get("brand")) != ("汇沣电商", "BUW"):
        _append_once(reasons, "BUSINESS_BOUNDARY_INVALID")
    if request.get("owner_state") != OWNER_STATE:
        _append_once(reasons, "REAL_OWNER_FORBIDDEN")
    if request.get("external_actions_performed") != [] or evidence_bundle.get("external_actions_performed") != []:
        _append_once(reasons, "EXTERNAL_ACTION_FORBIDDEN")
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
        "upstream_risk_states": dict(evidence_bundle.get("upstream_risk_states", {})),
        "external_actions_performed": [],
    }
    audit = {**core, "record_id": "AUD-SYN-001", "synthetic": True}
    decision = {**core, "record_id": "DEC-SYN-001", "synthetic": True, "human_decision": None}
    return {**core, "audit_record": audit, "decision_record": decision}
```

- [ ] Run GREEN twice:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
python3 Tests/validate_aios_support_controlled_pilot.py
```

Expected: tests `OK`; validator prints `PASSED`, `result=needs_human_governance`, `external_actions_performed=[]`.

- [ ] Commit:

```bash
git add Tests/Fixtures/support-controlled-pilot/synthetic-support-pilot-candidate.yaml Tests/test_support_controlled_pilot.py Tests/validate_aios_support_controlled_pilot.py
git commit -m "feat(stage14): add pure synthetic eligibility evaluation"
```

## Task 4: Fail closed on identity, order, version and schema attacks

**Files**

- Modify/Test: `Tests/test_support_controlled_pilot.py`
- Modify: `Tests/validate_aios_support_controlled_pilot.py`

**Interfaces**

- Consumes: adversarial in-memory mutations.
- Produces: stable ordered denial reasons, never repaired inputs.

- [ ] Add table-driven RED test:

```python
    def test_identity_version_order_and_schema_attacks_deny(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        cases = {
            "missing_id": lambda r, e: r.pop("support_request_id"),
            "wildcard_id": lambda r, e: r.__setitem__("scope_id", "SCOPE-SYN-*"),
            "wrong_prefix": lambda r, e: r.__setitem__("pilot_candidate_id", "SR-SYN-001"),
            "mixed_version": lambda r, e: e.__setitem__("model_version", "support_controlled_pilot_eligibility/v2"),
            "duplicate_evidence": lambda r, e: e["evidence_refs"].append(e["evidence_refs"][0]),
            "reordered_evidence": lambda r, e: e["evidence_refs"].reverse(),
            "unknown_field": lambda r, e: r.__setitem__("extension", True),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                request = copy.deepcopy(fixture["request"])
                evidence = copy.deepcopy(fixture["evidence_bundle"])
                mutate(request, evidence)
                decision = validator.evaluate_eligibility(model, request, evidence)
                self.assertEqual("denied", decision["result"])
                self.assertTrue(decision["reason_codes"])
                self.assertEqual([], decision["required_human_gates"])
                self.assertEqual([], decision["external_actions_performed"])
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_identity_version_order_and_schema_attacks_deny -v
```

Expected: failures for unimplemented denial cases.

- [ ] Add exact schemas, regexes, order and duplicate checks:

```python
import re
import hashlib

REQUEST_KEYS = {
    "model_version", "support_request_id", "support_case_id", "pilot_candidate_id",
    "scope_id", "company", "brand", "synthetic_workload_class", "owner_state",
    "external_actions_performed",
}
ID_RULES = {
    "support_request_id": re.compile(r"^SR-SYN-[A-Z0-9-]+$"),
    "support_case_id": re.compile(r"^SC-SYN-[A-Z0-9-]+$"),
    "pilot_candidate_id": re.compile(r"^PCAN-SYN-[A-Z0-9-]+$"),
    "scope_id": re.compile(r"^SCOPE-SYN-[A-Z0-9-]+$"),
}
if set(request) != REQUEST_KEYS:
    _append_once(reasons, "REQUEST_SCHEMA_INVALID")
for field, rule in ID_RULES.items():
    if not isinstance(request.get(field), str) or not rule.fullmatch(request[field]):
        _append_once(reasons, f"{field.upper()}_INVALID")
if evidence_bundle.get("evidence_refs") != model["evidence_contract"]["required_evidence_refs"]:
    _append_once(reasons, "EVIDENCE_ORDER_OR_CONTENT_INVALID")
items = evidence_bundle.get("evidence_items")
if not isinstance(items, list) or [item.get("evidence_id") for item in items] != evidence_bundle.get("evidence_refs"):
    _append_once(reasons, "EVIDENCE_ITEM_ORDER_INVALID")
else:
    for item in items:
        content = item.get("synthetic_content")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest() if isinstance(content, str) else None
        if item.get("hash_basis") != "synthetic_content_utf8" or item.get("content_sha256") != digest:
            _append_once(reasons, "EVIDENCE_HASH_INVALID")
        if item.get("human_accepted") is not False:
            _append_once(reasons, "HUMAN_ACCEPTANCE_INFERENCE_FORBIDDEN")
```

- [ ] Run GREEN and commit:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
git add Tests/test_support_controlled_pilot.py Tests/validate_aios_support_controlled_pilot.py
git commit -m "test(stage14): deny malformed identity and ordering inputs"
```

Expected: all Stage 14 tests `OK`; one independent commit.

## Task 5: Fail closed on business, data, owner, authority and upstream attacks

**Files**

- Modify/Test: `Tests/test_support_controlled_pilot.py`
- Modify: `Tests/validate_aios_support_controlled_pilot.py`

**Interfaces**

- Consumes: boundary, provenance, owner, mechanism, metric, evidence and authority mutations.
- Produces: deterministic `denied`, preserving Stage 10 and Stage 11–13 boundaries.

- [ ] Add exact RED cases:

```python
    def test_business_authority_and_control_attacks_deny(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        fixture = validator.load_repository_yaml(ROOT, validator.FIXTURE_PATH)
        mutations = {
            "pc": lambda r, e: r.__setitem__("brand", "PC"),
            "lht": lambda r, e: r.__setitem__("company", "六合通"),
            "cross_brand": lambda r, e: r.__setitem__("brand", "BUW|PC"),
            "real_owner": lambda r, e: r.__setitem__("owner_state", "Named Operator"),
            "real_data": lambda r, e: e.__setitem__("synthetic", False),
            "connector": lambda r, e: e.__setitem__("connector", "ticket-api"),
            "external_action": lambda r, e: r["external_actions_performed"].append("ticket-created"),
            "stage10_closed": lambda r, e: e["upstream_risk_states"].__setitem__("PR-RISK-001", "closed"),
            "stage11_missing": lambda r, e: e["evidence_refs"].remove("EVID-SYN-STAGE11-ARCHITECTURE-SECURITY"),
            "support_missing": lambda r, e: e["evidence_refs"].remove("EVID-SYN-SUPPORT-STOP-WITHDRAWAL"),
            "metrics_missing": lambda r, e: e["evidence_refs"].remove("EVID-SYN-METRICS-AUDIT"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                request = copy.deepcopy(fixture["request"])
                evidence = copy.deepcopy(fixture["evidence_bundle"])
                mutate(request, evidence)
                self.assertEqual("denied", validator.evaluate_eligibility(model, request, evidence)["result"])

    def test_permission_like_results_and_fields_are_rejected(self):
        validator = load_validator()
        model = validator.load_repository_yaml(ROOT, validator.MODEL_PATH)
        forbidden = [
            "pilot_authorized", "approved", "ready", "released", "eligible", "go",
            "accepted", "proceed", "pilot_ready", "production_ready",
        ]
        for token in forbidden:
            with self.subTest(token=token):
                mutated = copy.deepcopy(model)
                mutated["allowed_results"] = ["denied", token]
                self.assertTrue(validator.validate_model(mutated))
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_business_authority_and_control_attacks_deny Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_permission_like_results_and_fields_are_rejected -v
```

Expected: at least one failure until every boundary is enforced.

- [ ] Add exact risk and permission constants:

```python
EXPECTED_RISKS = {
    **{f"PR-RISK-{number:03d}": "blocked" for number in range(1, 9)},
    "PR-RISK-009": "open",
    "PR-RISK-010": "open",
}
FORBIDDEN_PERMISSION_TOKENS = frozenset({
    "pilot_authorized", "approved", "ready", "released", "eligible", "go",
    "accepted", "proceed", "pilot_ready", "production_ready",
})
if request.get("company") != "汇沣电商" or request.get("brand") != "BUW":
    _append_once(reasons, "BUSINESS_BOUNDARY_INVALID")
if evidence_bundle.get("synthetic") is not True or evidence_bundle.get("repository_controlled") is not True:
    _append_once(reasons, "SYNTHETIC_PROVENANCE_INVALID")
if evidence_bundle.get("upstream_risk_states") != EXPECTED_RISKS:
    _append_once(reasons, "UPSTREAM_RISK_STATE_INVALID")
```

Add this recursive scanner and call it on model, request and evidence before eligibility calculation:

```python
FORBIDDEN_OPERATIONAL_KEYS = frozenset({
    "ticket", "ticket_id", "monitor", "customer", "store", "order", "employee",
    "infrastructure", "database", "api", "connector", "credential", "secret",
    "pager", "alert", "external_url", "real_owner", "named_owner",
})

def _scan_forbidden(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_OPERATIONAL_KEYS:
                _append_once(errors, "FORBIDDEN_OPERATIONAL_FIELD:" + ".".join((*path, str(key))))
            if normalized in FORBIDDEN_PERMISSION_TOKENS and child not in (False, None):
                _append_once(errors, "FORBIDDEN_PERMISSION_FIELD:" + ".".join((*path, str(key))))
            for error in _scan_forbidden(child, (*path, str(key))):
                _append_once(errors, error)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            for error in _scan_forbidden(child, (*path, str(index))):
                _append_once(errors, error)
    elif isinstance(value, str) and value.strip().lower() in FORBIDDEN_PERMISSION_TOKENS:
        _append_once(errors, "FORBIDDEN_PERMISSION_VALUE:" + ".".join(path))
    return errors
```

The only permitted permission-like keys are the exact false-valued keys in `model["authority"]` and `decision_contract`; validate those blocks first, remove neither key nor value, and scan all other paths. The scanner does not sanitize input or access an external source.

- [ ] Run GREEN and commit:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
python3 Tests/validate_aios_support_controlled_pilot.py
git add Tests/test_support_controlled_pilot.py Tests/validate_aios_support_controlled_pilot.py
git commit -m "feat(stage14): enforce fail-closed governance boundaries"
```

Expected: canonical result `needs_human_governance`; all mutations `denied`; commit succeeds.

## Task 6: Add policy and prove specification coverage

**Files**

- Create: `Governance/AIOS-Support-Controlled-Pilot-v1.md`
- Modify/Test: `Tests/test_support_controlled_pilot.py`

**Interfaces**

- Consumes: approved specification and model identities.
- Produces: independently reviewable policy mapped to evaluator behavior.

- [ ] Add RED coverage test:

```python
POLICY = ROOT / "Governance/AIOS-Support-Controlled-Pilot-v1.md"

    def test_policy_covers_business_loop_objects_authority_and_lifecycle(self):
        policy = POLICY.read_text(encoding="utf-8")
        required = [
            "Purpose and authority", "Business loop", "Core objects", "Data flow",
            "Operators", "System and human judgment boundary", "Proof of operation",
            "Support request", "Support case", "Pilot candidate", "Entry", "Exit",
            "Stop", "Withdrawal", "Escalation", "Success metrics", "Guardrail metrics",
            "Evidence bundle", "Audit record", "Decision record", "Human gates",
            "needs_human_governance", "Stage 10 BLOCKED / NO-GO", "Stage 11–13",
            "汇沣电商", "BUW", "PC", "六合通",
            "unassigned / governance decision required",
            "设计先行、真实试点另行授权",
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, policy)
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_policy_covers_business_loop_objects_authority_and_lifecycle -v
```

Expected: `ERROR` because policy is absent.

- [ ] Write exact policy structure:

```markdown
# AIOS Support and Controlled Pilot Policy v1
## Purpose and authority
## Six system questions
### Business loop
### Core objects
### Data flow
### Operators
### System and human judgment boundary
### Proof of operation
## Unified model and identity contract
## Support request and support case
## Pilot candidate and bounded scope
## Entry, exit, stop and withdrawal
## Support model and escalation
## Success metrics and guardrail metrics
## Evidence bundle, audit record and decision record
## Human gates and authority ceiling
## Fail-closed error handling
## Stage 10–13 frozen dependencies
## Testing and pull-request-only CI
## Lifecycle and future real-pilot prerequisites
```

The final section must require a separate human governance decision, named owners, approved real scope/data, accepted evidence, risk decisions, support/stop/withdrawal capability and bounded authority. State that Stage 14 evidence satisfies none of those gates.

- [ ] Run GREEN and commit:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
git add Governance/AIOS-Support-Controlled-Pilot-v1.md Tests/test_support_controlled_pilot.py
git commit -m "docs(stage14): define controlled pilot governance policy"
```

Expected: all tests `OK`; policy-only implementation commit.

## Task 7: Add Stage 10–13 mapping and acceptance matrix

**Files**

- Create: `Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml`
- Create: `Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml`
- Modify/Test: `Tests/test_support_controlled_pilot.py`
- Modify: `Tests/validate_aios_support_controlled_pilot.py`

**Interfaces**

- Consumes: exact Stage 10 risk IDs/states and Stage 11–13 archived evidence.
- Produces: complete mappings with no closure, acceptance or authority.

- [ ] Add RED tests:

```python
MAPPING = ROOT / "Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml"
MATRIX = ROOT / "Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml"

    def test_upstream_mapping_freezes_risks_and_design_boundaries(self):
        mapping = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
        self.assertEqual(
            [f"PR-RISK-{number:03d}" for number in range(1, 11)],
            [item["risk_id"] for item in mapping["stage10_risks"]],
        )
        self.assertEqual(["blocked"] * 8 + ["open", "open"], [i["state"] for i in mapping["stage10_risks"]])
        self.assertTrue(all(i["accepted"] is False for i in mapping["stage10_risks"]))
        self.assertTrue(all(i["owner_state"] == "unassigned / governance decision required" for i in mapping["stage10_risks"]))
        self.assertEqual([11, 12, 13], [i["stage"] for i in mapping["upstream_evidence"]])
        self.assertTrue(all(i["design_only"] is True and i["accepted_for_real_pilot"] is False for i in mapping["upstream_evidence"]))

    def test_acceptance_matrix_never_grants_authority(self):
        matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
        self.assertTrue(all(row["synthetic_evidence_required"] for row in matrix["requirements"]))
        self.assertTrue(all(row["human_acceptance_required"] for row in matrix["requirements"]))
        self.assertEqual(
            {"pilot_authorized": False, "release_authorized": False, "production_action_allowed": False},
            matrix["authority_ceiling"],
        )
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_upstream_mapping_freezes_risks_and_design_boundaries Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_acceptance_matrix_never_grants_authority -v
```

Expected: `ERROR` because mappings are absent.

- [ ] Create explicit mapping, with all ten rows written out:

```yaml
mapping_version: support_controlled_pilot_stage10_13_mapping/v1
stage10_conclusion: BLOCKED / NO-GO
stage10_risks:
  - risk_id: PR-RISK-001
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: architecture evidence required; no deployable capability inferred
upstream_evidence:
  - {stage: 11, lifecycle: Archived, evidence_class: architecture_and_security_design, design_only: true, accepted_for_real_pilot: false}
  - {stage: 12, lifecycle: Archived, evidence_class: privacy_and_data_governance_design, design_only: true, accepted_for_real_pilot: false}
  - {stage: 13, lifecycle: Archived, evidence_class: operational_resilience_design, design_only: true, accepted_for_real_pilot: false}
```

Write explicit entries PR-RISK-002 through PR-RISK-010; 001–008 remain `blocked`, 009–010 remain `open`; every row remains unaccepted, unoverridden and owner-unassigned. Do not use YAML anchors or generated implicit rows.

- [ ] Create the exact ordered acceptance matrix; each row names its model field, test method, evidence and human gate:

```yaml
matrix_version: support_controlled_pilot_acceptance_matrix/v1
requirements:
  - {requirement_id: identity_version_order, model_field: id_prefixes, test_method: test_identity_version_order_and_schema_attacks_deny, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE}
  - {requirement_id: business_scope, model_field: allowed_scope, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-REAL-SCOPE-AND-DATA-AUTHORIZATION}
  - {requirement_id: synthetic_provenance, model_field: synthetic_only, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-REAL-SCOPE-AND-DATA-AUTHORIZATION}
  - {requirement_id: owner_state, model_field: owner_state, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-NAMED-OWNER-APPOINTMENT}
  - {requirement_id: support_request_case, model_field: support_requests, test_method: test_model_has_exact_identity_boundary_outcomes_and_gate_order, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {requirement_id: candidate_scope, model_field: pilot_candidates, test_method: test_valid_fixture_needs_human_governance_without_side_effects, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-BOUNDED-AUTHORITY-DEFINITION}
  - {requirement_id: entry, model_field: entry_criteria, test_method: test_valid_fixture_needs_human_governance_without_side_effects, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-REAL-PILOT-ENTRY-DECISION}
  - {requirement_id: exit, model_field: exit_criteria, test_method: test_model_has_exact_identity_boundary_outcomes_and_gate_order, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {requirement_id: stop, model_field: stop_conditions, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-SUPPORT-STOP-WITHDRAWAL, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {requirement_id: withdrawal, model_field: withdrawal_conditions, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-SUPPORT-STOP-WITHDRAWAL, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {requirement_id: support_model, model_field: support_models, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-SUPPORT-STOP-WITHDRAWAL, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {requirement_id: escalation, model_field: escalation_paths, test_method: test_identity_version_order_and_schema_attacks_deny, synthetic_evidence: EVB-SYN-SUPPORT-STOP-WITHDRAWAL, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE}
  - {requirement_id: success_metrics, model_field: success_metrics, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-METRICS-AUDIT, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-METRIC-AND-EVIDENCE-ACCEPTANCE}
  - {requirement_id: guardrail_metrics, model_field: guardrail_metrics, test_method: test_business_authority_and_control_attacks_deny, synthetic_evidence: EVB-SYN-METRICS-AUDIT, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-METRIC-AND-EVIDENCE-ACCEPTANCE}
  - {requirement_id: evidence_bundle, model_field: evidence_contract, test_method: test_identity_version_order_and_schema_attacks_deny, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-METRIC-AND-EVIDENCE-ACCEPTANCE}
  - {requirement_id: audit_decision, model_field: audit_contract, test_method: test_valid_fixture_needs_human_governance_without_side_effects, synthetic_evidence: EVB-SYN-METRICS-AUDIT, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE}
  - {requirement_id: human_gates, model_field: human_gates, test_method: test_valid_fixture_needs_human_governance_without_side_effects, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-REAL-PILOT-ENTRY-DECISION}
  - {requirement_id: stage10_risks, model_field: upstream_risk_states, test_method: test_upstream_mapping_freezes_risks_and_design_boundaries, synthetic_evidence: EVID-SYN-STAGE10-RISK-REGISTER, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-STAGE10-RISK-DISPOSITION}
  - {requirement_id: stage11_13_evidence, model_field: evidence_contract, test_method: test_upstream_mapping_freezes_risks_and_design_boundaries, synthetic_evidence: EVID-SYN-STAGE11-13, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-STAGE11-13-EVIDENCE-ACCEPTANCE}
  - {requirement_id: pure_evaluation, model_field: allowed_results, test_method: test_valid_fixture_needs_human_governance_without_side_effects, synthetic_evidence: EVB-SYN-001, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE}
  - {requirement_id: read_only_ci, model_field: authority, test_method: test_workflow_is_pull_request_only_and_read_only, synthetic_evidence: CI-EXACT-HEAD, synthetic_evidence_required: true, human_acceptance_required: true, human_gate: HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE}
authority_ceiling: {pilot_authorized: false, release_authorized: false, production_action_allowed: false}
```

- [ ] Extend the loader allowlist, then make `validate_repository(root: Path = ROOT) -> list[str]` use only this loader for YAML, validate row order/equality, and reject any true authority:

```python
MAPPING_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml")
MATRIX_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml")
ALLOWED_YAML_PATHS = frozenset({MODEL_PATH, FIXTURE_PATH, MAPPING_PATH, MATRIX_PATH})

mapping = load_repository_yaml(root, MAPPING_PATH)
matrix = load_repository_yaml(root, MATRIX_PATH)
if [item.get("risk_id") for item in mapping.get("stage10_risks", [])] != [f"PR-RISK-{n:03d}" for n in range(1, 11)]:
    errors.append("stage10_risk_order_invalid")
if matrix.get("authority_ceiling") != {
    "pilot_authorized": False,
    "release_authorized": False,
    "production_action_allowed": False,
}:
    errors.append("acceptance_authority_ceiling_invalid")
```

- [ ] Run GREEN and commit:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
python3 Tests/validate_aios_support_controlled_pilot.py
git add Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml Tests/test_support_controlled_pilot.py Tests/validate_aios_support_controlled_pilot.py
git commit -m "docs(stage14): map frozen upstream controls and acceptance"
```

Expected: tests/validator pass; traceability commit succeeds.

## Task 8: Add validation guide and complete repository validator

**Files**

- Create: `Tests/AIOS-Support-Controlled-Pilot-Validation.md`
- Modify/Test: `Tests/test_support_controlled_pilot.py`
- Modify: `Tests/validate_aios_support_controlled_pilot.py`

**Interfaces**

- Consumes: every Stage 14 asset and frozen Stage 10–13 paths.
- Produces: `validate_repository(root: Path = ROOT) -> list[str]`, CLI exit `0/1`, reproducible guide.

- [ ] Add RED test:

```python
VALIDATION_GUIDE = ROOT / "Tests/AIOS-Support-Controlled-Pilot-Validation.md"

    def test_repository_validator_and_guide_cover_all_deliverables(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_repository(ROOT))
        guide = VALIDATION_GUIDE.read_text(encoding="utf-8")
        for command in (
            "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
            "python3 -m unittest Tests.test_project_governance -v",
            "python3 Tests/validate_aios_operational_resilience.py",
            "python3 Tests/validate_aios_support_controlled_pilot.py",
            "python3 Tests/validate_aios_workflow_schema.py",
            "python3 -m compileall Tests",
        ):
            self.assertIn(command, guide)
        self.assertIn("needs_human_governance proves no pilot authority", guide)
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_repository_validator_and_guide_cover_all_deliverables -v
```

Expected: failure because guide/repository checks are incomplete.

- [ ] Complete CLI:

```python
def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        print("AIOS Support Controlled Pilot validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    model = load_repository_yaml(ROOT, MODEL_PATH)
    fixture = load_repository_yaml(ROOT, FIXTURE_PATH)
    result = evaluate_eligibility(model, fixture["request"], fixture["evidence_bundle"])
    print("AIOS Support Controlled Pilot validation PASSED")
    print(f"result={result['result']}")
    print("external_actions_performed=[]")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

`validate_repository` checks every required file, exact model/fixture/mapping/matrix, policy coverage, owner states, permission-like outcome positions, Stage 10 conclusion, Stage 11–13 evidence, workflow once created and current registries. Accumulate errors in stable order.

- [ ] Write the guide using this executable command block and interpretation text:

```markdown
# AIOS Support Controlled Pilot Validation

Run from repository root:

    python3 -m unittest Tests.test_support_controlled_pilot -v
    python3 Tests/validate_aios_support_controlled_pilot.py
    python3 -m unittest discover -s Tests -p 'test_*.py' -v
    python3 -m unittest Tests.test_project_governance -v
    python3 Tests/validate_aios_operational_resilience.py
    python3 Tests/validate_aios_workflow_schema.py
    python3 -m compileall Tests
    git diff --check

Expected focused result: every adversarial case is denied; the sole otherwise-valid
fixture returns needs_human_governance; external_actions_performed is empty.

Expected repository result: every command exits 0. Compare the Stage 10–13 canonical
assets against the approved starting head and require an empty diff. A pass proves
only deterministic repository-controlled synthetic contract behavior.
needs_human_governance proves no pilot authority. It proves no real support
capability, risk acceptance, owner appointment, release or pilot readiness.
```

- [ ] Run GREEN and commit:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
python3 Tests/validate_aios_support_controlled_pilot.py
python3 Tests/validate_aios_operational_resilience.py
python3 -m unittest Tests.test_project_governance -v
git add Tests/AIOS-Support-Controlled-Pilot-Validation.md Tests/test_support_controlled_pilot.py Tests/validate_aios_support_controlled_pilot.py
git commit -m "test(stage14): complete repository validation guide"
```

Expected: all commands exit `0`; validator result remains `needs_human_governance`.

## Task 9: Add pull-request-only read-only CI

**Files**

- Create: `.github/workflows/validate-aios-support-controlled-pilot.yml`
- Modify/Test: `Tests/test_support_controlled_pilot.py`
- Modify: `Tests/validate_aios_support_controlled_pilot.py`

**Interfaces**

- Consumes: pull-request head checkout.
- Produces: read-only CI for focused/full validation, schema and compilation.

- [ ] Add RED workflow test:

```python
WORKFLOW = ROOT / ".github/workflows/validate-aios-support-controlled-pilot.yml"

    def test_workflow_is_pull_request_only_and_read_only(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        for prohibited in (
            "contents: write", "pull-requests: write", "issues: write", "git push",
            "curl ", "wget ", "secrets.", "environment:",
        ):
            self.assertNotIn(prohibited, workflow)
```

- [ ] Run RED:

```bash
python3 -m unittest Tests.test_support_controlled_pilot.SupportControlledPilotTests.test_workflow_is_pull_request_only_and_read_only -v
```

Expected: `ERROR` because workflow is absent.

- [ ] Create workflow:

```yaml
name: Validate AIOS Support Controlled Pilot
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
      - run: python3 -m unittest Tests.test_support_controlled_pilot -v
      - run: python3 Tests/validate_aios_support_controlled_pilot.py
      - run: python3 -m unittest discover -s Tests -p 'test_*.py' -v
      - run: python3 Tests/validate_aios_workflow_schema.py
      - run: python3 -m compileall Tests
```

- [ ] Extend repository validation to require exact trigger, read permission, disabled checkout credentials and command set.

- [ ] Run GREEN and commit:

```bash
python3 -m unittest Tests.test_support_controlled_pilot -v
python3 Tests/validate_aios_support_controlled_pilot.py
python3 Tests/validate_aios_workflow_schema.py
git add .github/workflows/validate-aios-support-controlled-pilot.yml Tests/test_support_controlled_pilot.py Tests/validate_aios_support_controlled_pilot.py
git commit -m "ci(stage14): validate synthetic support pilot design"
```

Expected: all commands exit `0`; CI commit succeeds.

## Task 10: Verify implementation, report without escalation, publish Mandatory Return

**Files**

- Modify: `Governance/AIOS-Stage-Registry.md`
- Modify: `Governance/AIOS-Project-Registry.md`
- Modify: `Tests/validate_aios_operational_resilience.py`
- Modify/Test: `Tests/test_operational_resilience.py`
- Modify/Test: `Tests/test_project_governance.py`
- Test: full `Tests/` suite and every governance validator.

**Interfaces**

- Consumes: complete local evidence, exact remote head, exact-head CI URLs.
- Produces: Stage 14 `Reported`, one Mandatory Return on Issue #36, Draft PR #37 evidence; never Reviewed/Archived/pilot authority.

- [ ] Run full gate before lifecycle change:

```bash
python3 -m unittest discover -s Tests -p 'test_*.py' -v
python3 -m unittest Tests.test_project_governance -v
python3 Tests/validate_aios_operational_resilience.py
python3 Tests/validate_aios_support_controlled_pilot.py
python3 Tests/validate_aios_workflow_schema.py
python3 -m compileall Tests
git diff --check
git status --short
```

Expected: all exit `0`; all tests pass; compilation succeeds; diff check silent; only authorized files exist.

- [ ] Prove all canonical Stage 10–13 control assets are frozen:

```bash
git diff --exit-code c312db694afc40b5ec268f577c6c05a664b98eef -- Governance/AIOS-Production-Readiness-v1.md Governance/AIOS-Production-Readiness-Inventory-v1.md Governance/AIOS-Production-Readiness-Matrix-v1.yaml Governance/AIOS-Production-Readiness-Risk-Register-v1.yaml Governance/AIOS-Architecture-Security-Foundations-v1.md Governance/AIOS-Architecture-Security-Model-v1.yaml Governance/AIOS-Architecture-Security-Threat-Model-v1.yaml Governance/AIOS-Architecture-Security-Acceptance-Matrix-v1.yaml Governance/AIOS-Architecture-Security-Stage10-Mapping-v1.yaml Governance/AIOS-Privacy-Data-Governance-v1.md Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml Governance/AIOS-Privacy-Data-Governance-Acceptance-Matrix-v1.yaml Governance/AIOS-Privacy-Data-Governance-Stage10-Mapping-v1.yaml Governance/AIOS-Operational-Resilience-v1.md Governance/AIOS-Operational-Resilience-Model-v1.yaml Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml
```

Expected: exit `0`, no output; every listed canonical asset remains byte-identical to the approved plan baseline.

- [ ] Add RED lifecycle expectations:

```python
self.assertIn("| Reported |", stage14)
self.assertIn("Mandatory Return", stage14)
self.assertIn("needs_human_governance", stage14)
self.assertIn("no pilot authority", stage14)
```

Also mutate `Reported` to `Reviewed` and `Archived`, and `no pilot authority` to `pilot authority granted`; each mutation must fail. Preserve exact Stage 13 assertions for Archived, Issues #32/#34, reviewed head `327d9e9`, published commit `7b16a5c`, `19/19`, `80/80`, model, policy, risk conclusion and design-only boundary.

- [ ] Run lifecycle RED:

```bash
python3 -m unittest Tests.test_operational_resilience.OperationalResilienceTests.test_registry_records_archived_stage13_and_separately_authorized_stage14_design Tests.test_project_governance.ProjectGovernanceValidation.test_stages_10_through_13_are_archived_stage14_design_is_separately_authorized -v
```

Expected: failures because Stage 14 is still `Executing`.

- [ ] Update both Registry rows to `Reported` only after all implementation evidence exists. Record Issue #36, Execution Thread, branch, exact head, Draft PR #37, test counts and `needs_human_governance`; state Mandatory Return awaits independent review and grants no pilot authority. Keep Stage 13 unchanged.

- [ ] Change only current-registry lifecycle validation from plan-awaiting `Executing` to evidence-backed `Reported`. Continue rejecting Reviewed, Archived, pilot/release authority, named owner, real data/system claims and Stage 13 changes.

- [ ] Run full GREEN gate:

```bash
python3 -m unittest discover -s Tests -p 'test_*.py' -v
python3 -m unittest Tests.test_project_governance -v
python3 Tests/validate_aios_operational_resilience.py
python3 Tests/validate_aios_support_controlled_pilot.py
python3 Tests/validate_aios_workflow_schema.py
python3 -m compileall Tests
git diff --check
```

Expected: all exit `0`; capture exact test count for Mandatory Return.

- [ ] Run plan conformance checks without creating false token matches:

```bash
python3 -c 'from pathlib import Path; p=Path("docs/superpowers/plans/2026-07-23-support-controlled-pilot-design-v1.md").read_text(); bad=["T"+"BD","T"+"ODO","place"+"holder"]; found=[x for x in bad if x in p]; raise SystemExit(f"unresolved markers: {found}" if found else 0)'
python3 -c 'from pathlib import Path; p=Path("docs/superpowers/plans/2026-07-23-support-controlled-pilot-design-v1.md").read_text(); required=["evaluate_eligibility(model: dict[str, Any], request: dict[str, Any], evidence_bundle: dict[str, Any]) -> dict[str, Any]","load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]","validate_model(model: dict[str, Any]) -> list[str]","validate_repository(root: Path = ROOT) -> list[str]"]; missing=[x for x in required if x not in p]; raise SystemExit(f"signature mismatch: {missing}" if missing else 0)'
```

Expected: both exit `0`, no output. Manually map every approved specification heading to a model field, policy section, test and acceptance row; record coverage in the PR comment.

- [ ] Commit Reported transition independently:

```bash
git add Governance/AIOS-Stage-Registry.md Governance/AIOS-Project-Registry.md Tests/validate_aios_operational_resilience.py Tests/test_operational_resilience.py Tests/test_project_governance.py
git commit -m "gov(stage14): report synthetic implementation evidence"
```

- [ ] Push and verify Draft status:

```bash
git push origin feat/aios-support-controlled-pilot-design-v1
gh pr view 37 --json isDraft,state,headRefOid,mergeStateStatus,url
```

Expected: `isDraft=true`, `state=OPEN`, head equals `git rev-parse HEAD`. Never mark ready or merge.

- [ ] Wait for exact-head CI:

```bash
gh pr checks 37 --watch
gh pr view 37 --json headRefOid,statusCheckRollup
```

Expected: every required check succeeds for exact head. If not, record failure honestly; fix only an in-scope defect through a new test-first commit and wait for the new head.

- [ ] Compare local and remote:

```bash
git diff --name-only c312db694afc40b5ec268f577c6c05a664b98eef..HEAD
git diff --exit-code HEAD origin/feat/aios-support-controlled-pilot-design-v1 --
```

Expected: only authorized files listed; remote comparison exits `0`.

- [ ] Post one Mandatory Return to Issue #36 with exact base/head, commits, files, test counts, validator output, CI URLs, `needs_human_governance`, `external_actions_performed: []`, frozen-boundary proof, Draft PR and exclusions. Add the same evidence summary to Draft PR #37 without requesting readiness.

- [ ] Stop at `Reported`. Do not merge, publish, archive, assign owners, accept risk, connect a real system or execute a real pilot.

---

## Plan self-review gate

Before submitting this plan for independent approval, verify:

- Every normative specification area maps to at least one future file, test and validation step.
- These signatures are identical everywhere:
  - `load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]`
  - `validate_model(model: dict[str, Any]) -> list[str]`
  - `evaluate_eligibility(model: dict[str, Any], request: dict[str, Any], evidence_bundle: dict[str, Any]) -> dict[str, Any]`
  - `validate_repository(root: Path = ROOT) -> list[str]`
- Every task has exact paths, Consumes/Produces, RED command/expected failure, minimal implementation, GREEN command/expected pass and independent commit.
- Every data row, function body and authority statement required for execution is explicit.
- Stage 10–13 controls are consumed as frozen evidence and never modified.
- Maximum lifecycle is Draft PR + `Reported` + Mandatory Return; no merge, publication, archive or real pilot step exists.
