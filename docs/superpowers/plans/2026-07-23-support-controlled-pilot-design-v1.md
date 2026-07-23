# Support and Controlled Pilot Design v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Governance override for this plan:** Use only `superpowers:executing-plans` through inline execution in the same Execution Thread `019f8c92-e709-7a83-b06c-fa014cf0b216`. Do not use subagent-driven development, create a second execution task/thread, or dispatch any subagent unless the Governance Thread later changes this constraint explicitly.

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
- Governance execution constraint: the only permitted implementation mode is inline execution in this same Execution Thread `019f8c92-e709-7a83-b06c-fa014cf0b216`. Do not create a second execution task, thread or subagent. A different execution mode requires a later explicit Governance Thread decision.

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

- [ ] Replace the Task 2 validation skeleton with this complete closed-schema model validator:

```python
TOP_LEVEL_KEYS = (
    "model_version", "stage", "stage_id", "issue", "execution_thread",
    "synthetic_only", "repository_controlled_fixtures_only", "allowed_scope",
    "excluded_entities", "owner_state", "allowed_results", "authority",
    "id_prefixes", "human_gates", "support_requests", "support_cases",
    "pilot_candidates", "scopes", "entry_criteria", "exit_criteria",
    "stop_conditions", "withdrawal_conditions", "support_models",
    "escalation_paths", "success_metrics", "guardrail_metrics",
    "evidence_contract", "audit_contract", "decision_contract",
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
        "support_request_id", "SR-SYN-",
        {"support_request_id", "model_version", "synthetic", "pilot_candidate_id", "scope_id"},
    ),
    "support_cases": (
        "support_case_id", "SC-SYN-",
        {"support_case_id", "model_version", "synthetic", "support_request_id", "support_model_id", "escalation_path_id"},
    ),
    "pilot_candidates": (
        "pilot_candidate_id", "PCAN-SYN-",
        {"pilot_candidate_id", "model_version", "synthetic", "scope_id", "entry_criteria_ids", "exit_criteria_ids", "stop_condition_ids", "withdrawal_condition_ids"},
    ),
    "scopes": (
        "scope_id", "SCOPE-SYN-",
        {"scope_id", "model_version", "synthetic", "company", "brand", "workload_class", "duration_design_bound", "volume_design_bound", "permitted_actions", "excluded_actions"},
    ),
    "entry_criteria": (
        "criterion_id", "ENTRY-SYN-",
        {"criterion_id", "required_gate_ids", "real_world_satisfied"},
    ),
    "exit_criteria": (
        "criterion_id", "EXIT-SYN-",
        {"criterion_id", "required_evidence", "evaluator_may_close_real_pilot"},
    ),
    "stop_conditions": (
        "condition_id", "STOP-SYN-",
        {"condition_id", "triggers", "default_action"},
    ),
    "withdrawal_conditions": (
        "condition_id", "WITHDRAW-SYN-",
        {"condition_id", "required_capabilities", "real_roles_assigned"},
    ),
    "support_models": (
        "support_model_id", "SUP-SYN-",
        {"support_model_id", "owner_state", "required_elements"},
    ),
    "escalation_paths": (
        "escalation_path_id", "ESC-SYN-",
        {"escalation_path_id", "owner_state", "ordered_functions"},
    ),
    "success_metrics": (
        "metric_id", "SM-SYN-",
        {"metric_id", "definition", "unit", "direction", "source", "observation_window", "threshold_type", "threshold", "missing_data_behavior", "evidence_ref", "owner_state"},
    ),
    "guardrail_metrics": (
        "metric_id", "GM-SYN-",
        {"metric_id", "definition", "unit", "direction", "source", "observation_window", "threshold_type", "threshold", "missing_data_behavior", "evidence_ref", "owner_state"},
    ),
}

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
        or any(set(gate) != {"gate_id"} for gate in gates if isinstance(gate, dict))
        or [gate.get("gate_id") for gate in gates if isinstance(gate, dict)] != EXPECTED_GATES
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

    if model.get("support_requests", [{}])[0].get("pilot_candidate_id") != "PCAN-SYN-001":
        _append_once(errors, "support_request_candidate_ref_invalid")
    if model.get("support_requests", [{}])[0].get("scope_id") != "SCOPE-SYN-001":
        _append_once(errors, "support_request_scope_ref_invalid")
    if model.get("support_cases", [{}])[0].get("support_request_id") != "SR-SYN-001":
        _append_once(errors, "support_case_request_ref_invalid")
    if model.get("support_cases", [{}])[0].get("support_model_id") != "SUP-SYN-001":
        _append_once(errors, "support_case_model_ref_invalid")
    if model.get("support_cases", [{}])[0].get("escalation_path_id") != "ESC-SYN-001":
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
    if scope.get("excluded_actions") != ["external_read", "external_write", "real_pilot"]:
        _append_once(errors, "scope_excluded_actions_invalid")

    entry = model.get("entry_criteria", [{}])[0]
    if entry.get("required_gate_ids") != EXPECTED_GATES or entry.get("real_world_satisfied") is not False:
        _append_once(errors, "entry_human_gate_contract_invalid")
    if model.get("exit_criteria", [{}])[0].get("evaluator_may_close_real_pilot") is not False:
        _append_once(errors, "exit_authority_invalid")
    if model.get("withdrawal_conditions", [{}])[0].get("real_roles_assigned") is not False:
        _append_once(errors, "withdrawal_real_role_invalid")

    evidence_contract = model.get("evidence_contract")
    expected_evidence_keys = {
        "evidence_bundle_id_prefix", "version_format", "required_evidence_refs",
        "content_hash_required", "human_acceptance_inferred",
    }
    if not isinstance(evidence_contract, dict) or set(evidence_contract) != expected_evidence_keys:
        _append_once(errors, "evidence_contract_schema_invalid")
    elif (
        evidence_contract.get("evidence_bundle_id_prefix") != "EVB-SYN-"
        or evidence_contract.get("version_format") != "semantic_version"
        or evidence_contract.get("content_hash_required") is not True
        or evidence_contract.get("human_acceptance_inferred") is not False
    ):
        _append_once(errors, "evidence_contract_value_invalid")

    if model.get("audit_contract") != {
        "record_id": "AUD-SYN-001", "synthetic": True, "persistent_store": False,
    }:
        _append_once(errors, "audit_contract_invalid")
    if model.get("decision_contract") != {
        "record_id": "DEC-SYN-001", "synthetic": True,
        "human_decision": None, "pilot_authorized": False,
    }:
        _append_once(errors, "decision_contract_invalid")
    return errors
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

Wire the scanner into the evaluator with these exact functions and lines. The model copy exists only in memory and leaves the caller's input unchanged:

```python
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
    if not isinstance(decision_contract, dict) or decision_contract.get("pilot_authorized") is not False:
        _append_once(errors, "MODEL_DECISION_AUTHORITY_INVALID")
    scannable = {
        key: value
        for key, value in model.items()
        if key not in {"authority", "decision_contract"}
    }
    for error in _scan_forbidden(scannable, ("model",)):
        _append_once(errors, error)
    return errors

# Insert immediately after reasons: list[str] = [] in evaluate_eligibility.
for error in _scan_model_forbidden(model):
    _append_once(reasons, error)
for error in _scan_forbidden(request, ("request",)):
    _append_once(reasons, error)
for error in _scan_forbidden(evidence_bundle, ("evidence_bundle",)):
    _append_once(reasons, error)
```

The evaluator scans only supplied in-memory values, performs no sanitization and accesses no external source.

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

- [ ] Create `Governance/AIOS-Support-Controlled-Pilot-v1.md` with this complete policy text:

```markdown
# AIOS Support and Controlled Pilot Policy v1

## Purpose and authority

This policy implements the Stage 14 design rule: 设计先行、真实试点另行授权.
It governs repository-controlled synthetic evaluation for Issue #36 only.
The only allowed business pair is 汇沣电商 / BUW. PC is an independent brand
and excluded; 六合通 is a separate company and excluded. Every real owner
remains unassigned / governance decision required.

## Six system questions

### Business loop

A repository synthetic support request and pilot candidate are safely loaded,
validated as one versioned graph, evaluated in memory, and returned as denied
or needs_human_governance. No result starts or authorizes a pilot.

### Core objects

The controlled objects are Support request, Support case, Pilot candidate,
bounded scope, Entry criteria, Exit criteria, Stop conditions, Withdrawal
conditions, support model, Escalation path, Success metrics, Guardrail metrics,
Evidence bundle, Audit record, Decision record and Human gates.

### Data flow

Only allowlisted repository YAML enters the loader. Parsed mappings flow into
the pure evaluator. The decision stays in memory. No ticket, monitor, customer,
store, order, employee, infrastructure, connector, credential or external
system is read or written.

### Operators

Tests may be run only in the governed repository task. Abstract support and
review functions are not real operators. Only the Governance Thread can accept
evidence, name owners, decide risks or authorize a bounded real pilot.

### System and human judgment boundary

Code validates identity, version, order, completeness, provenance, boundary
and denial rules. Humans decide evidence acceptance, owner competence, legal
and business sufficiency, risk disposition and pilot authority.

### Proof of operation

Proof consists of deterministic positive and adversarial synthetic tests,
full repository regression, Workflow Schema validation, Python compilation,
frozen Stage 10–13 hashes and exact-head read-only CI. Passing proves only the
synthetic contract; it proves no real capability.

## Unified model and identity contract

The model version is support_controlled_pilot_eligibility/v1. IDs are
case-sensitive, prefix-constrained, unique and canonically ordered. Missing,
unknown, duplicate, reordered, wildcard, aliased, extra or mixed-version
identity denies the complete request.

## Support request and support case

A request references exactly one pilot candidate and scope. A case references
exactly one request, support model and escalation path. Both are synthetic and
perform no external action. A real ticket, person, owner or operational payload
denies.

## Pilot candidate and bounded scope

A candidate is a synthetic proposal, never permission. Its scope is exactly
汇沣电商 / BUW, one synthetic workload, one design duration and one design
volume. Scope expansion requires a new candidate and a later human decision.

## Entry, exit, stop and withdrawal

Entry requires all ten human gates and is never satisfied by the evaluator.
Exit requires scope, metric, case, evidence, data/access disposition and human
closure. Stop defaults to no further action pending human decision. Withdrawal
requires intake, acknowledgement, cessation, evidence preservation,
scope/data/access disposition and human closure. Missing any mechanism denies.

## Support model and escalation

The support model requires intake, taxonomy, severity, coverage design,
acknowledgement target, handoff, closure, training, runbook, retention and
service-target review. Escalation order is support triage, technical review,
triggered security/privacy review, triggered operational-resilience review,
then Governance Thread decision. Bypass, duplication or reordering denies.

## Success metrics and guardrail metrics

Every metric has immutable ID, definition, unit, direction, synthetic source,
observation window, threshold type/value, missing-data behavior, evidence
reference and unassigned owner. Missing data denies. Success cannot cancel a
guardrail breach, stop, withdrawal or unresolved risk.

## Evidence bundle, audit record and decision record

Evidence IDs, paths, versions, canonical order and synthetic-content SHA-256
values are exact. Human acceptance is always false in fixtures. Audit and
Decision records mirror request, candidate, scope, model, reasons, gates,
evidence and upstream risks, with external_actions_performed: [].

## Human gates and authority ceiling

An otherwise-valid candidate returns all gates:
HG-WRITTEN-SPEC-APPROVAL,
HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE,
HG-NAMED-OWNER-APPOINTMENT,
HG-REAL-SCOPE-AND-DATA-AUTHORIZATION,
HG-STAGE10-RISK-DISPOSITION,
HG-STAGE11-13-EVIDENCE-ACCEPTANCE,
HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE,
HG-METRIC-AND-EVIDENCE-ACCEPTANCE,
HG-BOUNDED-AUTHORITY-DEFINITION and
HG-REAL-PILOT-ENTRY-DECISION.
The evaluator cannot satisfy or remove a gate. pilot_authorized,
release_authorized and production_action_allowed remain false.

## Fail-closed error handling

Invalid input returns denied with stable ordered reasons. An otherwise-valid
input returns only needs_human_governance. approved, ready, released, eligible,
go, accepted, proceed, pilot_ready, production_ready and semantic equivalents
are forbidden. Exceptions never produce permission.

## Stage 10–13 frozen dependencies

Stage 10 BLOCKED / NO-GO remains controlling. PR-RISK-001 through
PR-RISK-008 remain blocked; PR-RISK-009 and PR-RISK-010 remain open; all are
unaccepted and owner-unassigned. Stage 11–13 remain Archived design evidence
only and are not real control acceptance.

## Testing and pull-request-only CI

CI triggers only on pull_request, grants contents: read, disables persisted
credentials, installs requirements-dev.txt and runs focused tests, repository
tests, Stage 14 validation, Workflow Schema and compilation. It performs no
push, deployment, publication or external write.

## Lifecycle and future real-pilot prerequisites

Implementation may stop only at Draft PR, Reported and Mandatory Return for
independent human review. A future real pilot requires a separate human
Governance Thread decision, named accountable owners, approved real scope and
data, accepted implementation and Stage 11–13 evidence, explicit Stage 10 risk
decisions, accepted support/stop/withdrawal capability, accepted metrics and
evidence, and clear bounded authority. Stage 14 evidence satisfies none of
those real-world gates. Merge, publication, archive and real pilot remain
separate decisions.
```

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
  - risk_id: PR-RISK-002
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: Stage 11 identity authorization and secret evidence required; no security control is provisioned or accepted
  - risk_id: PR-RISK-003
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: Stage 12 privacy purpose and data evidence required before any real data; Stage 14 remains synthetic only
  - risk_id: PR-RISK-004
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: exact source lineage quality and reconciliation evidence required; no source is connected
  - risk_id: PR-RISK-005
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: metric and evidence contracts are defined; no telemetry alert durable log or measured SLO exists
  - risk_id: PR-RISK-006
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: Stage 13 stop and recovery evidence plus withdrawal disposition proof required; no rollback is performed
  - risk_id: PR-RISK-007
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: Stage 13 escalation and human decision evidence required; no incident path is operated
  - risk_id: PR-RISK-008
    state: blocked
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: support model and synthetic handoff contract defined; no owner coverage or live support exists
  - risk_id: PR-RISK-009
    state: open
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: exact 汇沣电商 and BUW boundary required; PC 六合通 and ambiguity fail closed
  - risk_id: PR-RISK-010
    state: open
    accepted: false
    overridden_by_stage14: false
    owner_state: unassigned / governance decision required
    stage14_relationship: otherwise-valid evaluation stops at needs_human_governance; pilot and release authority remain false
upstream_evidence:
  - {stage: 11, lifecycle: Archived, evidence_class: architecture_and_security_design, design_only: true, accepted_for_real_pilot: false}
  - {stage: 12, lifecycle: Archived, evidence_class: privacy_and_data_governance_design, design_only: true, accepted_for_real_pilot: false}
  - {stage: 13, lifecycle: Archived, evidence_class: operational_resilience_design, design_only: true, accepted_for_real_pilot: false}
```

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

Insert these constants and this complete function immediately before `main`; Task 9 changes only `REQUIRED_PATHS` from `REQUIRED_PRE_CI_PATHS` to include `WORKFLOW_PATH` after creating the workflow:

```python
import hashlib

POLICY_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-v1.md")
MAPPING_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-Stage10-13-Mapping-v1.yaml")
MATRIX_PATH = Path("Governance/AIOS-Support-Controlled-Pilot-Acceptance-Matrix-v1.yaml")
GUIDE_PATH = Path("Tests/AIOS-Support-Controlled-Pilot-Validation.md")
WORKFLOW_PATH = Path(".github/workflows/validate-aios-support-controlled-pilot.yml")
STAGE_REGISTRY_PATH = Path("Governance/AIOS-Stage-Registry.md")
PROJECT_REGISTRY_PATH = Path("Governance/AIOS-Project-Registry.md")
REQUIRED_PRE_CI_PATHS = (
    MODEL_PATH, FIXTURE_PATH, POLICY_PATH, MAPPING_PATH, MATRIX_PATH, GUIDE_PATH,
    STAGE_REGISTRY_PATH, PROJECT_REGISTRY_PATH,
)
REQUIRED_PATHS = REQUIRED_PRE_CI_PATHS
REQUIRED_POLICY_TOKENS = (
    "Purpose and authority", "Business loop", "Core objects", "Data flow",
    "Operators", "System and human judgment boundary", "Proof of operation",
    "Support request", "Support case", "Pilot candidate", "Entry", "Exit",
    "Stop", "Withdrawal", "Escalation", "Success metrics", "Guardrail metrics",
    "Evidence bundle", "Audit record", "Decision record", "Human gates",
    "needs_human_governance", "Stage 10 BLOCKED / NO-GO", "Stage 11–13",
    "汇沣电商", "BUW", "PC", "六合通",
    "unassigned / governance decision required", "设计先行、真实试点另行授权",
)
REQUIRED_WORKFLOW_COMMANDS = (
    "python3 -m pip install -r requirements-dev.txt",
    "python3 -m unittest Tests.test_support_controlled_pilot -v",
    "python3 Tests/validate_aios_support_controlled_pilot.py",
    "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
    "python3 Tests/validate_aios_workflow_schema.py",
    "python3 -m compileall Tests",
)
PROHIBITED_WORKFLOW_TOKENS = (
    "push:", "workflow_dispatch:", "contents: write", "pull-requests: write",
    "issues: write", "git push", "curl ", "wget ", "secrets.", "environment:",
    "pip install pyyaml",
)
FROZEN_STAGE10_13_SHA256 = {
    "Governance/AIOS-Production-Readiness-v1.md": "d2129cd26e05a44b3d44cf7cfd291fa52668f56d75f7fd65aba604352c69e7ef",
    "Governance/AIOS-Production-Readiness-Inventory-v1.md": "de2a9a988a86e8fda9a853eb8659f14a320d69016f04b1f8d4ab73099e8cc190",
    "Governance/AIOS-Production-Readiness-Matrix-v1.yaml": "da865bc3dc902780c0951aa9a34f0344a5cf62eabd940066e8b7ee54aaff16ea",
    "Governance/AIOS-Production-Readiness-Risk-Register-v1.yaml": "b05eb30b90101047f244ed99170d70dc5e35497e1ac122d63d0c2dee3602acf9",
    "Governance/AIOS-Architecture-Security-Foundations-v1.md": "85615d5084460f68d0b629d3d891bd327e7cbecf902cc285d64ce5d5425c11e3",
    "Governance/AIOS-Architecture-Security-Model-v1.yaml": "bccfcaf000d076caa5ba1ec0929096ade47d2c03f3ddb0bbb932a0150d164564",
    "Governance/AIOS-Architecture-Security-Threat-Model-v1.yaml": "0cffa47748ac2b60aa5f36c7f8cbbc829cdfa15bf66369c3ce1a0cac50029566",
    "Governance/AIOS-Architecture-Security-Acceptance-Matrix-v1.yaml": "cca2d46dd27291a354644d47a4019244d81a0cb8398a5cc086f90fcee72c9247",
    "Governance/AIOS-Architecture-Security-Stage10-Mapping-v1.yaml": "1e71bb2a9f0209b24795663e2e9269271ccd89053e2d59e0d2ec31d4d89063f1",
    "Governance/AIOS-Privacy-Data-Governance-v1.md": "7c4ddcf8cb7cdb5e56a63688cae15701c26eb9061bd7fd9bfa3b10229b4593bf",
    "Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml": "cb9fa07b0a4c969f7620743858eeeb189d813bc12e0cf4653b8008add1c44450",
    "Governance/AIOS-Privacy-Data-Governance-Acceptance-Matrix-v1.yaml": "bcb2bb058ae8162a99651128fae9921fc67f44cacb5595f5f823cd393696ded9",
    "Governance/AIOS-Privacy-Data-Governance-Stage10-Mapping-v1.yaml": "30291db4ba05fec1c5fa9891c6537207b544ef9e2e4772c7eab054cdfc40e246",
    "Governance/AIOS-Operational-Resilience-v1.md": "e453f6b13a1ce0f12c2867208fcc45163580dd20fe24853789bbf00ede4f8d96",
    "Governance/AIOS-Operational-Resilience-Model-v1.yaml": "fc3c42dab820a1a38b05dfa5e81829b779e9c0802dd72527cb9fc1053c51e35e",
    "Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml": "ff961770e395629f4ea14bd6099c10e107160e1b49241cf1dd57248d55b16406",
    "Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml": "8a8b62fafac828ef560766c07da427695f1758d6bc65f714d2e4db1f822da7bb",
}

def _read_required_text(root: Path, path: Path, errors: list[str]) -> str:
    absolute = root / path
    if not absolute.is_file():
        errors.append(f"missing_required_path:{path.as_posix()}")
        return ""
    return absolute.read_text(encoding="utf-8")

def _load_required_yaml(root: Path, path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        return load_repository_yaml(root, path)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"yaml_load_failed:{path.as_posix()}:{type(exc).__name__}")
        return {}

def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_PATHS:
        if not (root / path).is_file():
            errors.append(f"missing_required_path:{path.as_posix()}")

    model = _load_required_yaml(root, MODEL_PATH, errors)
    fixture = _load_required_yaml(root, FIXTURE_PATH, errors)
    mapping = _load_required_yaml(root, MAPPING_PATH, errors)
    matrix = _load_required_yaml(root, MATRIX_PATH, errors)
    policy = _read_required_text(root, POLICY_PATH, errors)
    stage_registry = _read_required_text(root, STAGE_REGISTRY_PATH, errors)
    project_registry = _read_required_text(root, PROJECT_REGISTRY_PATH, errors)

    for model_error in validate_model(model):
        errors.append(f"model:{model_error}")

    if fixture.get("synthetic") is not True or fixture.get("repository_controlled") is not True:
        errors.append("fixture:synthetic_repository_controlled_required")
    request = fixture.get("request")
    evidence = fixture.get("evidence_bundle")
    if not isinstance(request, dict):
        errors.append("fixture:request_mapping_required")
    if not isinstance(evidence, dict):
        errors.append("fixture:evidence_bundle_mapping_required")
    if isinstance(request, dict) and isinstance(evidence, dict):
        decision = evaluate_eligibility(model, request, evidence)
        if decision.get("result") != "needs_human_governance":
            errors.append("fixture:otherwise_valid_result_invalid")
        if decision.get("external_actions_performed") != []:
            errors.append("fixture:external_actions_must_be_empty")
        if decision.get("required_human_gates") != [gate["gate_id"] for gate in model.get("human_gates", [])]:
            errors.append("fixture:human_gate_order_invalid")

    expected_risk_ids = [f"PR-RISK-{number:03d}" for number in range(1, 11)]
    risk_rows = mapping.get("stage10_risks")
    if not isinstance(risk_rows, list) or [row.get("risk_id") for row in risk_rows] != expected_risk_ids:
        errors.append("mapping:stage10_risk_order_invalid")
    else:
        expected_states = ["blocked"] * 8 + ["open", "open"]
        if [row.get("state") for row in risk_rows] != expected_states:
            errors.append("mapping:stage10_state_invalid")
        if any(row.get("accepted") is not False for row in risk_rows):
            errors.append("mapping:stage10_acceptance_forbidden")
        if any(row.get("overridden_by_stage14") is not False for row in risk_rows):
            errors.append("mapping:stage10_override_forbidden")
        if any(row.get("owner_state") != OWNER_STATE for row in risk_rows):
            errors.append("mapping:stage10_owner_invalid")
        if any(not isinstance(row.get("stage14_relationship"), str) or not row["stage14_relationship"].strip() for row in risk_rows):
            errors.append("mapping:stage14_relationship_required")
    if mapping.get("stage10_conclusion") != "BLOCKED / NO-GO":
        errors.append("mapping:stage10_conclusion_invalid")
    upstream = mapping.get("upstream_evidence")
    if not isinstance(upstream, list) or [row.get("stage") for row in upstream] != [11, 12, 13]:
        errors.append("mapping:stage11_13_order_invalid")
    elif any(
        row.get("lifecycle") != "Archived"
        or row.get("design_only") is not True
        or row.get("accepted_for_real_pilot") is not False
        for row in upstream
    ):
        errors.append("mapping:stage11_13_boundary_invalid")

    requirements = matrix.get("requirements")
    expected_requirement_ids = [
        "identity_version_order", "business_scope", "synthetic_provenance",
        "owner_state", "support_request_case", "candidate_scope", "entry", "exit",
        "stop", "withdrawal", "support_model", "escalation", "success_metrics",
        "guardrail_metrics", "evidence_bundle", "audit_decision", "human_gates",
        "stage10_risks", "stage11_13_evidence", "pure_evaluation", "read_only_ci",
    ]
    if not isinstance(requirements, list) or [row.get("requirement_id") for row in requirements] != expected_requirement_ids:
        errors.append("matrix:requirement_order_invalid")
    elif any(
        row.get("synthetic_evidence_required") is not True
        or row.get("human_acceptance_required") is not True
        for row in requirements
    ):
        errors.append("matrix:human_acceptance_contract_invalid")
    if matrix.get("authority_ceiling") != {
        "pilot_authorized": False,
        "release_authorized": False,
        "production_action_allowed": False,
    }:
        errors.append("matrix:authority_ceiling_invalid")

    for token in REQUIRED_POLICY_TOKENS:
        if token not in policy:
            errors.append(f"policy:missing_token:{token}")

    stage13 = next((line for line in stage_registry.splitlines() if line.startswith("| 13 |")), "")
    stage14 = next((line for line in stage_registry.splitlines() if line.startswith("| 14 |")), "")
    project = next((line for line in project_registry.splitlines() if line.startswith("| BUW-AIOS |")), "")
    for token in ("Issue #32", "Issue #34", "327d9e9", "7b16a5c", "19/19", "80/80", "| Archived |"):
        if token not in stage13:
            errors.append(f"registry:stage13_missing:{token}")
    for token in ("Issue #36", "019f8c92-e709-7a83-b06c-fa014cf0b216", "feat/aios-support-controlled-pilot-design-v1", "no pilot authority"):
        if token not in stage14:
            errors.append(f"registry:stage14_missing:{token}")
    if not any(status in stage14 for status in ("| Executing |", "| Reported |")):
        errors.append("registry:stage14_lifecycle_invalid")
    if any(token in stage14 for token in ("| Reviewed |", "| Archived |", "pilot authority granted", "pilot_authorized: true")):
        errors.append("registry:stage14_authority_exceeded")
    if "Stage 13 Archived / Stage 14 " not in project:
        errors.append("registry:project_stage_pair_missing")

    for relative, expected_hash in FROZEN_STAGE10_13_SHA256.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"frozen:missing:{relative}")
            continue
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"frozen:changed:{relative}")

    if (root / WORKFLOW_PATH).is_file():
        workflow = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
        if "pull_request:" not in workflow or "permissions:\n  contents: read" not in workflow:
            errors.append("workflow:trigger_or_permission_invalid")
        if "persist-credentials: false" not in workflow:
            errors.append("workflow:persist_credentials_not_false")
        for command in REQUIRED_WORKFLOW_COMMANDS:
            if command not in workflow:
                errors.append(f"workflow:missing_command:{command}")
        for token in PROHIBITED_WORKFLOW_TOKENS:
            if token in workflow:
                errors.append(f"workflow:prohibited_token:{token}")
    return errors
```

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
        validator = load_validator()
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        expected_commands = (
            "python3 -m pip install -r requirements-dev.txt",
            "python3 -m unittest Tests.test_support_controlled_pilot -v",
            "python3 Tests/validate_aios_support_controlled_pilot.py",
            "python3 -m unittest discover -s Tests -p 'test_*.py' -v",
            "python3 Tests/validate_aios_workflow_schema.py",
            "python3 -m compileall Tests",
        )
        for command in expected_commands:
            self.assertIn(command, workflow)
        for prohibited in (
            "contents: write", "pull-requests: write", "issues: write", "git push",
            "curl ", "wget ", "secrets.", "environment:", "pip install pyyaml",
        ):
            self.assertNotIn(prohibited, workflow)
        self.assertEqual([], validator.validate_repository(ROOT))
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
      - run: python3 -m pip install -r requirements-dev.txt
      - run: python3 -m unittest Tests.test_support_controlled_pilot -v
      - run: python3 Tests/validate_aios_support_controlled_pilot.py
      - run: python3 -m unittest discover -s Tests -p 'test_*.py' -v
      - run: python3 Tests/validate_aios_workflow_schema.py
      - run: python3 -m compileall Tests
```

- [ ] Replace the pre-CI required-path assignment with this exact final assignment; the complete `validate_repository` function from Task 8 then makes workflow absence, command drift, write permission and prohibited tokens repository errors:

```python
REQUIRED_PATHS = (*REQUIRED_PRE_CI_PATHS, WORKFLOW_PATH)
```

Run this negative probe against an isolated copy to prove the validator rejects an unbounded dependency command without editing the working tree:

```bash
probe_root=$(mktemp -d)
cp -R . "$probe_root/repo"
sed -i.bak 's#python3 -m pip install -r requirements-dev.txt#pip install pyyaml#' "$probe_root/repo/.github/workflows/validate-aios-support-controlled-pilot.yml"
python3 -c 'from pathlib import Path; import importlib.util,sys; root=Path(sys.argv[1]); p=root/"Tests/validate_aios_support_controlled_pilot.py"; s=importlib.util.spec_from_file_location("v",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); errors=m.validate_repository(root); assert "workflow:missing_command:python3 -m pip install -r requirements-dev.txt" in errors; assert "workflow:prohibited_token:pip install pyyaml" in errors' "$probe_root/repo"
```

Expected: exit `0`; both exact workflow errors are present in the in-memory list. The temporary directory is outside the repository and contains no real data.

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

- [ ] Replace the Stage 14 portions of the two existing Registry test methods and replace the lifecycle escalation method with these complete methods:

```python
# Tests/test_operational_resilience.py
import hashlib

def test_registry_records_archived_stage13_and_reported_stage14(self):
    stage_registry = STAGE_REGISTRY.read_text(encoding="utf-8")
    project_registry = PROJECT_REGISTRY.read_text(encoding="utf-8")
    stage13 = next(line for line in stage_registry.splitlines() if line.startswith("| 13 |"))
    stage14 = next(line for line in stage_registry.splitlines() if line.startswith("| 14 |"))
    for token in (
        "Issue #32", "Issue #34", "019f8a35-6d4e-7c60-b35a-79de8626d4e3",
        "feat/aios-operational-resilience-v1", "327d9e9", "7b16a5c",
        "19/19", "80/80", "| Archived |", "no production/staging",
        "risk acceptance", "pilot", "release",
    ):
        self.assertIn(token, stage13)
    frozen_stage13 = {
        ROOT / "Governance/AIOS-Operational-Resilience-v1.md": "e453f6b13a1ce0f12c2867208fcc45163580dd20fe24853789bbf00ede4f8d96",
        ROOT / "Governance/AIOS-Operational-Resilience-Model-v1.yaml": "fc3c42dab820a1a38b05dfa5e81829b779e9c0802dd72527cb9fc1053c51e35e",
        ROOT / "Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml": "ff961770e395629f4ea14bd6099c10e107160e1b49241cf1dd57248d55b16406",
        ROOT / "Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml": "8a8b62fafac828ef560766c07da427695f1758d6bc65f714d2e4db1f822da7bb",
    }
    for path, expected_sha256 in frozen_stage13.items():
        self.assertEqual(expected_sha256, hashlib.sha256(path.read_bytes()).hexdigest())
    stage13_model = yaml.safe_load(
        (ROOT / "Governance/AIOS-Operational-Resilience-Model-v1.yaml").read_text(encoding="utf-8")
    )
    self.assertFalse(stage13_model["decision"]["risk_acceptance_granted"])
    self.assertFalse(stage13_model["decision"]["production_ready"])
    for token in (
        "Issue #36", "019f8c92-e709-7a83-b06c-fa014cf0b216",
        "feat/aios-support-controlled-pilot-design-v1", "PR #37",
        "| Reported |", "Mandatory Return", "needs_human_governance",
        "independently approved plan", "no pilot authority",
    ):
        self.assertIn(token, stage14)
    self.assertIn("Stage 13 Archived / Stage 14 Reported", project_registry)

def test_stage14_reported_lifecycle_and_authority_escalation_fail_closed(self):
    stage_registry = STAGE_REGISTRY.read_text(encoding="utf-8")
    project_registry = PROJECT_REGISTRY.read_text(encoding="utf-8")
    self.assertEqual([], validate_current_registry_lifecycle(stage_registry, project_registry))

    for status in ("Reviewed", "Archived"):
        with self.subTest(stage_status=status):
            mutated = stage_registry.replace("| Reported |", f"| {status} |")
            errors = validate_current_registry_lifecycle(mutated, project_registry)
            self.assertTrue(any("exceeds Reported authority" in error for error in errors), errors)

    mutations = {
        "pilot": stage_registry.replace("no pilot authority", "pilot authority granted"),
        "self_approval": stage_registry.replace("independently approved plan", "self-approved plan"),
        "released": stage_registry.replace("no pilot authority", "release authorized"),
    }
    for name, mutated in mutations.items():
        with self.subTest(stage_mutation=name):
            errors = validate_current_registry_lifecycle(mutated, project_registry)
            self.assertTrue(any("exceeds Reported authority" in error for error in errors), errors)

    for status in ("Reviewed", "Archived"):
        with self.subTest(project_status=status):
            mutated = project_registry.replace(
                "Stage 13 Archived / Stage 14 Reported",
                f"Stage 13 Archived / Stage 14 {status}",
            )
            errors = validate_current_registry_lifecycle(stage_registry, mutated)
            self.assertTrue(any("Project Registry exceeds Reported authority" in error for error in errors), errors)

    mutated_project = project_registry.replace(
        "awaiting independent human review",
        "self-approved and ready for pilot",
    )
    errors = validate_current_registry_lifecycle(stage_registry, mutated_project)
    self.assertTrue(any("Project Registry exceeds Reported authority" in error for error in errors), errors)

# Tests/test_project_governance.py
def test_stages_10_through_13_are_archived_stage14_is_reported(self):
    stage10 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 10 |"))
    stage11 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 11 |"))
    stage12 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 12 |"))
    stage13 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 13 |"))
    stage14 = next(line for line in self.stage_registry.splitlines() if line.startswith("| 14 |"))
    self.assertIn("BLOCKED / NO-GO", stage10)
    self.assertIn("| Archived |", stage10)
    self.assertIn("PR #26", stage11)
    self.assertIn("| Archived |", stage11)
    self.assertIn("PR #29", stage12)
    self.assertIn("454a719", stage12)
    self.assertIn("| Archived |", stage12)
    for token in ("Issue #32", "Issue #34", "327d9e9", "7b16a5c", "19/19", "80/80", "| Archived |"):
        self.assertIn(token, stage13)
    for token in (
        "Issue #36", "019f8c92-e709-7a83-b06c-fa014cf0b216",
        "feat/aios-support-controlled-pilot-design-v1", "PR #37",
        "| Reported |", "Mandatory Return", "needs_human_governance",
        "no pilot authority",
    ):
        self.assertIn(token, stage14)
    self.assertIn("Stage 13 Archived / Stage 14 Reported", self.project_registry)
```

- [ ] Run lifecycle RED:

```bash
python3 -m unittest Tests.test_operational_resilience.OperationalResilienceTests.test_registry_records_archived_stage13_and_reported_stage14 Tests.test_operational_resilience.OperationalResilienceTests.test_stage14_reported_lifecycle_and_authority_escalation_fail_closed Tests.test_project_governance.ProjectGovernanceValidation.test_stages_10_through_13_are_archived_stage14_is_reported -v
```

Expected: three failures because the registries still record Stage 14 `Executing`.

- [ ] Capture the exact verified implementation evidence in environment variables; every value comes from a command that exits successfully:

```bash
export AIOS_IMPL_EVIDENCE_HEAD="$(git rev-parse HEAD)"
export AIOS_FOCUSED_TEST_COUNT="$(python3 -m unittest Tests.test_support_controlled_pilot -v 2>&1 | awk '/^Ran [0-9]+ tests/{print $2}')"
export AIOS_FULL_TEST_COUNT="$(python3 -m unittest discover -s Tests -p 'test_*.py' -v 2>&1 | awk '/^Ran [0-9]+ tests/{print $2}')"
export AIOS_PROJECT_TEST_COUNT="$(python3 -m unittest Tests.test_project_governance -v 2>&1 | awk '/^Ran [0-9]+ tests/{print $2}')"
export AIOS_CI_URLS="$(gh run list --commit "$AIOS_IMPL_EVIDENCE_HEAD" --json conclusion,url --jq '[.[] | select(.conclusion == "success") | .url] | join(", ")')"
test -n "$AIOS_IMPL_EVIDENCE_HEAD"
test -n "$AIOS_FOCUSED_TEST_COUNT"
test -n "$AIOS_FULL_TEST_COUNT"
test -n "$AIOS_PROJECT_TEST_COUNT"
test -n "$AIOS_CI_URLS"
```

Expected: all five non-empty checks exit `0`; CI URLs refer only to successful runs for `AIOS_IMPL_EVIDENCE_HEAD`.

- [ ] Run this complete Registry update program. It replaces only the Stage 14 row, the BUW-AIOS project row and the current publication-status line, then appends one idempotent change-log row to each registry:

```python
from __future__ import annotations
import os
from pathlib import Path

stage_path = Path("Governance/AIOS-Stage-Registry.md")
project_path = Path("Governance/AIOS-Project-Registry.md")
head = os.environ["AIOS_IMPL_EVIDENCE_HEAD"]
focused = os.environ["AIOS_FOCUSED_TEST_COUNT"]
full = os.environ["AIOS_FULL_TEST_COUNT"]
project_tests = os.environ["AIOS_PROJECT_TEST_COUNT"]
ci_urls = os.environ["AIOS_CI_URLS"]

stage_text = stage_path.read_text(encoding="utf-8")
stage_lines = stage_text.splitlines()
stage_row = (
    "| 14 | PS-01 | Support and Controlled Pilot Design（支持与受控试点设计） "
    "| BUW AIOS Official Governance Thread "
    "| [Issue #36](https://github.com/tonybai0123456-png/hf-lht/issues/36) / "
    "Execution Thread `019f8c92-e709-7a83-b06c-fa014cf0b216` / branch "
    "`feat/aios-support-controlled-pilot-design-v1` / "
    "[Draft PR #37](https://github.com/tonybai0123456-png/hf-lht/pull/37) "
    f"| Reported | Implementation evidence head `{head}`; {focused} focused tests, "
    f"{full} repository tests, {project_tests} Project Governance tests; exact-head CI: "
    f"{ci_urls}; otherwise-valid result `needs_human_governance`; Mandatory Return submitted. "
    "| Reported for independent human review under independently approved plan; no pilot authority. "
    "No real owner, real data/system/connector, external action, risk acceptance, release, merge, "
    "publication or archive authority. |"
)
stage_lines = [stage_row if line.startswith("| 14 |") else line for line in stage_lines]
stage_lines = [
    (
        "| Publication status | Governance v2.2 published; Stages 1–13 archived; "
        "Stage 14 is Reported under Issue #36 with a Mandatory Return awaiting independent human review |"
    )
    if line.startswith("| Publication status |") else line
    for line in stage_lines
]
stage_log = (
    f"| 2026-07-23 | 2.2 | Reported Stage 14 implementation evidence head `{head}` "
    f"with {focused} focused, {full} repository and {project_tests} Project Governance tests; "
    "submitted the Mandatory Return while retaining all human gates and no pilot authority. "
    "| PS-01 Execution Thread / Issue #36 / Draft PR #37 |"
)
if stage_log not in stage_lines:
    stage_lines.append(stage_log)
stage_path.write_text("\n".join(stage_lines) + "\n", encoding="utf-8")

project_text = project_path.read_text(encoding="utf-8")
project_lines = project_text.splitlines()
project_row = (
    "| BUW-AIOS | BUW AIOS | 汇沣电商; 六合通 is a separate company and excluded "
    "| BUW only; PC is an independent brand and excluded | Tony "
    "| BUW AIOS Official Governance Thread | `tonybai0123456-png/hf-lht` "
    "| `Governance/AIOS-Project-Governance-Baseline-v1.md` / `Governance/AIOS-Stage-Registry.md` "
    "| Active | Stage 13 Archived / Stage 14 Reported "
    f"| 2026-07-23 / Issue #36 / implementation evidence head `{head}` / Draft PR #37 / "
    f"{focused} focused / {full} repository / {project_tests} Project Governance tests / "
    "`needs_human_governance` / Mandatory Return "
    "| Awaiting independent human review; no pilot authority, merge, publication, release or archive authority |"
)
project_lines = [project_row if line.startswith("| BUW-AIOS |") else line for line in project_lines]
project_log = (
    f"| 2026-07-23 | Reported Stage 14 implementation evidence head `{head}` and submitted "
    "the Mandatory Return; retained Stage 13 Archived, Stage 10 BLOCKED / NO-GO and every "
    "real-pilot human gate. | PS-01 Execution Thread / Issue #36 / Draft PR #37 |"
)
if project_log not in project_lines:
    project_lines.append(project_log)
project_path.write_text("\n".join(project_lines) + "\n", encoding="utf-8")
```

Expected: only the two registry files change; Stage 13 rows remain byte-for-byte identical.

- [ ] Replace `validate_current_registry_lifecycle` in `Tests/validate_aios_operational_resilience.py` with this exact Reported-phase function:

```python
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
```

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

- [ ] Capture the final verified values and write this fixed Mandatory Return body. Every shell expansion is populated from the named verification command; there are no manually entered evidence values:

```bash
export AIOS_FINAL_HEAD="$(git rev-parse HEAD)"
export AIOS_COMMIT_LIST="$(git log --format='%H %s' c312db694afc40b5ec268f577c6c05a664b98eef..HEAD)"
export AIOS_CHANGED_FILES="$(git diff --name-only c312db694afc40b5ec268f577c6c05a664b98eef..HEAD)"
export AIOS_FINAL_CI_URLS="$(gh run list --commit "$AIOS_FINAL_HEAD" --json conclusion,url --jq '[.[] | select(.conclusion == "success") | .url] | join(", ")')"
test -n "$AIOS_FINAL_HEAD"
test -n "$AIOS_COMMIT_LIST"
test -n "$AIOS_CHANGED_FILES"
test -n "$AIOS_FINAL_CI_URLS"

cat > /private/tmp/aios-stage14-mandatory-return.md <<EOF
## Stage Mandatory Return — Stage 14 / PS-01

### Identity and authority
- Issue: #36
- Execution Thread: 019f8c92-e709-7a83-b06c-fa014cf0b216
- Branch: feat/aios-support-controlled-pilot-design-v1
- Draft PR: https://github.com/tonybai0123456-png/hf-lht/pull/37
- Approved written-spec head: c312db694afc40b5ec268f577c6c05a664b98eef
- Implementation evidence head before Reported transition: $AIOS_IMPL_EVIDENCE_HEAD
- Exact final remote head: $AIOS_FINAL_HEAD
- Lifecycle requested: Reported only; awaiting independent human review

### Commit evidence
$AIOS_COMMIT_LIST

### Changed files
$AIOS_CHANGED_FILES

### Deterministic validation
- Stage 14 focused tests: $AIOS_FOCUSED_TEST_COUNT passed
- Repository tests: $AIOS_FULL_TEST_COUNT passed
- Project Governance tests: $AIOS_PROJECT_TEST_COUNT passed
- Operational Resilience validator: PASS
- Support Controlled Pilot validator: PASS
- Workflow Schema validator: PASS
- Python compilation: PASS
- git diff --check: PASS
- Stage 10–13 frozen SHA-256 boundary: 17/17 PASS
- Local/remote file parity: PASS

### Evaluator evidence
- otherwise-valid result: needs_human_governance
- invalid result: denied
- external_actions_performed: []
- required human gates:
  1. HG-WRITTEN-SPEC-APPROVAL
  2. HG-IMPLEMENTATION-EVIDENCE-ACCEPTANCE
  3. HG-NAMED-OWNER-APPOINTMENT
  4. HG-REAL-SCOPE-AND-DATA-AUTHORIZATION
  5. HG-STAGE10-RISK-DISPOSITION
  6. HG-STAGE11-13-EVIDENCE-ACCEPTANCE
  7. HG-SUPPORT-STOP-WITHDRAWAL-ACCEPTANCE
  8. HG-METRIC-AND-EVIDENCE-ACCEPTANCE
  9. HG-BOUNDED-AUTHORITY-DEFINITION
  10. HG-REAL-PILOT-ENTRY-DECISION

### Exact-head CI
$AIOS_FINAL_CI_URLS

### Frozen upstream boundary
- Stage 10 remains BLOCKED / NO-GO.
- PR-RISK-001 through PR-RISK-008 remain blocked and unaccepted.
- PR-RISK-009 and PR-RISK-010 remain open and unaccepted.
- Stage 11–13 remain Archived design evidence only.
- All real owners remain unassigned / governance decision required.

### Explicit exclusions
No real pilot, real owner, real data, customer, store, order, employee, ticket,
monitor, alert, infrastructure, database, API, connector, credential, external
write, risk acceptance, release, merge, publication, Reviewed transition or
Archived transition is claimed or authorized.

### Requested governance action
Independently review the exact final head. This Mandatory Return does not
self-approve implementation evidence and does not authorize a pilot.
EOF

gh issue comment 36 --body-file /private/tmp/aios-stage14-mandatory-return.md
gh pr comment 37 --body-file /private/tmp/aios-stage14-mandatory-return.md
```

Expected: both GitHub commands return comment URLs; Issue #36 receives exactly one Mandatory Return and Draft PR #37 receives the same evidence without changing review readiness.

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
