# Non-production Readiness Remediation and Integration Implementation Plan

> **Execution record:** This plan was executed task-by-task only after the direct owner instruction dated 2026-07-30 assigned the bounded predeployment work to Codex goal `019fb137-f0bc-7e60-b8ad-efe1a8e250b1` on the existing Stage 15 branch.

> **Governance status:** Stage 15 is `Reported` and awaits independent human review. No real pilot, deployment, production, risk acceptance, owner assignment, permission change, external write, merge, publication, archive, Issue closure, or Stage 16 is authorized by this plan or its implementation evidence.

**Goal:** Build a repository-contained, local, synthetic, disposable proof for company `汇沣电商`, brand `BUW`, while excluding `PC` and `六合通`; map evidence to `PR-RISK-001` through `PR-RISK-010`; fail closed; and return at most `needs_human_governance`.

**Architecture:** Four allowlisted YAML mappings are loaded with `yaml.safe_load`. A closed validator checks identity, components, risks, gates, evidence, recovery, incident and support records. A pure evaluator performs no I/O and returns only `denied` or `needs_human_governance`. A repository validator cross-checks YAML, policy, validation guide and pull-request-only read-only CI.

**Tech Stack:** Python 3.12 standard library, PyYAML from `requirements-dev.txt`, `unittest`, YAML, Markdown and GitHub Actions.

## Global Constraints

- Company boundary: `汇沣电商`; brand boundary: `BUW`.
- Excluded entities: `PC`, `六合通`, aliases, wildcards, mixed scopes and unknown identities.
- Inputs are repository-controlled synthetic data only.
- Stage 10 remains `BLOCKED / NO-GO`; Stages 11–14 remain `Archived`.
- All ten risks remain `open_blocked_unaccepted`; owner remains `unassigned / governance decision required`.
- The written specification, implementation plan and dedicated execution assignment are recorded as authorized; implementation-evidence acceptance and gates 5–12 remain pending.
- Invalid or malformed input returns `denied`; valid synthetic input returns `needs_human_governance`.
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
- lifecycle compatibility tests only when current assertions require the Stage 15 `Reported` transition.

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
PENDING_GATE_IDS = GATE_IDS[3:]
FALSE_CLAIMS = {
    "risk_accepted": False,
    "pilot_authorized": False,
    "production_ready": False,
    "release_authorized": False,
}
```

The model, fixture, mapping and matrix are closed records: exact keys only, exact types, exact ordered IDs, no aliases, no YAML merge keys, no additional fields, no truthy substitutes for booleans, and no authority-like values.

## Capability-field and malformed-input correction contract

The valid fixture intentionally contains empty capability declarations at three exact paths. They are structure declarations, not authority grants. Only these exact empty lists are allowed:

```python
ALLOWED_EMPTY_CAPABILITY_PATHS = frozenset({
    "$.environment.external_endpoints",
    "$.environment.connectors",
    "$.environment.credentials",
})
FORBIDDEN_CAPABILITY_KEYS = frozenset({
    "credential", "credentials", "secret", "secrets", "password", "token",
    "api_key", "endpoint", "external_endpoints", "database", "connector",
    "connectors", "webhook",
})

def _scan_forbidden(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            current_path = f"{path}.{key}"
            normalized = str(key).strip().lower()
            if current_path in ALLOWED_EMPTY_CAPABILITY_PATHS:
                if child != []:
                    errors.append(_error(current_path, "forbidden_capability_value"))
                continue
            if normalized in FORBIDDEN_CAPABILITY_KEYS:
                errors.append(_error(current_path, "forbidden_capability_key"))
            errors.extend(_scan_forbidden(child, current_path))
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
```

The validator entry points must fail closed for any Python/YAML shape, including scalars, lists, `None`, malformed nested records and unexpected mapping keys:

```python
def _fail_closed(callable_, value: Any, path: str) -> list[str]:
    try:
        return callable_(value)
    except (AttributeError, KeyError, TypeError, ValueError):
        return [_error(path, "malformed_input")]

def evaluate_nonproduction_readiness(model: Any, fixture: Any) -> dict[str, Any]:
    model_errors = _fail_closed(_validate_model_impl, deepcopy(model), "$model")
    fixture_errors = _fail_closed(_validate_fixture_impl, deepcopy(fixture), "$fixture")
    errors = list(dict.fromkeys([*model_errors, *fixture_errors]))
    return {
        "result": "denied" if errors else "needs_human_governance",
        "reason_codes": [f"VALIDATION_ERROR:{item}" for item in errors]
        if errors else ["LOCAL_SYNTHETIC_VALIDATION_PASSED", "HUMAN_GATES_REQUIRED"],
        "evidence_refs": [] if errors else list(EVIDENCE_IDS),
        "required_human_gates": list(PENDING_GATE_IDS),
        "risk_states": {risk_id: "open_blocked_unaccepted" for risk_id in RISK_IDS},
        "external_actions_performed": [],
        "claims": dict(FALSE_CLAIMS),
    }
```

`allowed_empty_capability` is the acceptance label for the three exact empty-list paths. `forbidden_capability_value` is the stable error code for a non-empty value at an allowed declaration path.

## Task 1: Pin execution provenance and create the failing test scaffold

**Files**

- Create: `Tests/test_nonproduction_readiness.py`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Loads `Tests/validate_aios_nonproduction_readiness.py` dynamically.
- Pins all public interfaces and exact paths.

- [ ] Record the separately approved execution assignment and create the initial RED tests.

```python
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "Tests/validate_aios_nonproduction_readiness.py"

def load_validator():
    spec = importlib.util.spec_from_file_location("nr_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
```

```bash
test -n "$STAGE15_EXECUTION_TASK"
test -n "$STAGE15_IMPLEMENTATION_BRANCH"
git status --porcelain
python3 -m unittest Tests.test_nonproduction_readiness -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): pin closed readiness interfaces"
```

Expected: the exact remote head and tree are recorded, the branch is clean, and tests fail only because controlled assets do not yet exist.

## Task 2: Implement the allowlisted loader and fail-closed validator

**Files**

- Create: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Implements all five public interfaces.
- Produces stable ordered `path:code` errors without exceptions.

- [ ] Implement the loader, closed record helpers, path-aware capability scanner and guarded validator entry points.

```python
from pathlib import Path
from typing import Any
import yaml

ALLOWED_YAML_PATHS = frozenset({
    Path("Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml"),
    Path("Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml"),
    Path("Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml"),
    Path("Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml"),
})

def load_repository_yaml(root: Path, relative_path: Path) -> dict[str, Any]:
    if relative_path.is_absolute() or relative_path not in ALLOWED_YAML_PATHS:
        raise ValueError("path is not allowlisted")
    candidate = root.resolve() / relative_path
    if candidate.is_symlink() or root.resolve() not in candidate.resolve().parents:
        raise ValueError("path boundary denied")
    loaded = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("controlled YAML must be a mapping")
    return loaded
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 Tests/validate_aios_nonproduction_readiness.py
git add Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "feat(stage15): add fail-closed readiness validator"
```

Expected: malformed top-level values return stable errors; valid structure advances to later missing-asset failures.

## Task 3: Add closed model and synthetic fixture

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml`
- Create: `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`

**Interfaces**

- Model defines risks, components, evidence, gates and authority ceiling.
- Fixture contains only local synthetic disposable facts.

- [ ] Create exact closed YAML records with the allowed empty capability declarations.

```yaml
fixture_version: nonproduction_readiness_fixture/v1
scenario_id: NR-SYNTHETIC-LOCAL-001
scope: {company: 汇沣电商, brand: BUW}
environment:
  mode: local_synthetic_disposable
  external_endpoints: []
  connectors: []
  credentials: []
requested_external_actions: []
claims:
  risk_accepted: false
  pilot_authorized: false
  production_ready: false
  release_authorized: false
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_model_and_fixture_are_valid -v
git add Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml
git commit -m "feat(stage15): add closed model and synthetic fixture"
```

Expected: valid model and fixture pass validation; environment capability fields are accepted only because all three exact-path values are empty lists.

## Task 4: Implement deterministic pure evaluation

**Files**

- Modify: `Tests/validate_aios_nonproduction_readiness.py`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Evaluator is deterministic, input-immutable and free of I/O.
- Result is exactly `denied` or `needs_human_governance`.

- [ ] Add positive, negative, determinism, mutation and AST side-effect tests.

```python
result = validator.evaluate_nonproduction_readiness(model, fixture)
self.assertEqual("needs_human_governance", result["result"])
self.assertEqual([], result["external_actions_performed"])
self.assertTrue(all(value is False for value in result["claims"].values()))

fixture["scope"]["brand"] = "PC"
result = validator.evaluate_nonproduction_readiness(model, fixture)
self.assertEqual("denied", result["result"])
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest Tests.test_nonproduction_readiness -v
git add Tests/validate_aios_nonproduction_readiness.py Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): prove pure bounded evaluation"
```

Expected: repeated runs are byte-for-byte stable, inputs remain unchanged, and no external action can be emitted.

## Task 5: Pin capability and malformed-input regressions

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: `Tests/validate_aios_nonproduction_readiness.py`

**Interfaces**

- Proves exact empty declarations are allowed.
- Proves non-empty, misplaced and malformed values are denied without exceptions.

- [ ] Add the three named regression tests required by governance.

```python
def test_empty_capability_fields_are_allowed(self):
    validator, model, fixture = self._assets()
    result = validator.evaluate_nonproduction_readiness(model, fixture)
    self.assertEqual("needs_human_governance", result["result"])

def test_nonempty_or_misplaced_capability_fields_are_denied(self):
    validator, model, baseline = self._assets()
    mutations = (
        lambda f: f["environment"]["external_endpoints"].append("https://example.invalid"),
        lambda f: f["environment"]["connectors"].append("shopify"),
        lambda f: f["environment"]["credentials"].append("token"),
        lambda f: f.__setitem__("connectors", []),
    )
    for mutate in mutations:
        fixture = copy.deepcopy(baseline)
        mutate(fixture)
        result = validator.evaluate_nonproduction_readiness(model, fixture)
        self.assertEqual("denied", result["result"])

def test_malformed_input_types_are_denied_without_exceptions(self):
    validator, model, fixture = self._assets()
    malformed_values = (None, True, 1, "text", [], [None], {"unexpected": []})
    for value in malformed_values:
        result = validator.evaluate_nonproduction_readiness(value, fixture)
        self.assertEqual("denied", result["result"])
        result = validator.evaluate_nonproduction_readiness(model, value)
        self.assertEqual("denied", result["result"])
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_empty_capability_fields_are_allowed -v
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_nonempty_or_misplaced_capability_fields_are_denied -v
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_malformed_input_types_are_denied_without_exceptions -v
git add Tests/test_nonproduction_readiness.py Tests/validate_aios_nonproduction_readiness.py
git commit -m "test(stage15): enforce capability and malformed input boundaries"
```

Expected: the positive package reaches human governance; every non-empty, misplaced or malformed case returns `denied` without raising.

## Task 6: Prove evidence and observation integrity

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: model, fixture and validator.

**Interfaces**

- Verifies append-only evidence sequence, deterministic checksums and no external delivery.
- Rejects gaps, duplicates and fabricated observation outcomes.

- [ ] Add table-driven evidence and observation mutations.

```python
mutations = (
    lambda f: f["evidence_store"]["records"][1].__setitem__("sequence", 3),
    lambda f: f["evidence_store"]["records"][1].__setitem__("record_id", "AUDIT-001"),
    lambda f: f["observation"].__setitem__("external_delivery", True),
)
for mutate in mutations:
    changed = copy.deepcopy(fixture)
    mutate(changed)
    self.assertEqual("denied", validator.evaluate_nonproduction_readiness(model, changed)["result"])
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_evidence_and_observation_integrity -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): prove local evidence integrity"
```

Expected: valid checksums pass; sequence gaps, duplicates and external-delivery claims are denied.

## Task 7: Prove recovery, incident and support boundaries

**Files**

- Modify/Test: `Tests/test_nonproduction_readiness.py`
- Verify: fixture and validator.

**Interfaces**

- Validates synthetic rollback and cleanup.
- Keeps incidents tabletop-only and support routing abstract.

- [ ] Add mutations for failed restore, real incident, named owner, live route, ticket and SLA.

```python
mutations = (
    lambda f: f["recovery"].__setitem__("restore_verified", False),
    lambda f: f["incident_tabletop"].__setitem__("real_incident_declared", True),
    lambda f: f["support_handoff"].__setitem__("owner", "Tony"),
    lambda f: f["support_handoff"].__setitem__("ticket_created", True),
)
for mutate in mutations:
    changed = copy.deepcopy(fixture)
    mutate(changed)
    self.assertEqual("denied", validator.evaluate_nonproduction_readiness(model, changed)["result"])
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness.NonproductionReadinessTests.test_recovery_incident_and_support_mutations_are_denied -v
git add Tests/test_nonproduction_readiness.py
git commit -m "test(stage15): enforce synthetic recovery and support boundaries"
```

Expected: all attempts to turn synthetic proof into real operations are denied.

## Task 8: Create Stage 10–14 mapping and acceptance matrix

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml`
- Create: `Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml`

**Interfaces**

- Maps all ten risks and archived design dependencies.
- Provides exact requirement-to-test-to-evidence traceability.

- [ ] Create the closed acceptance rows.

```yaml
requirements:
  - {requirement_id: AC-ENVIRONMENT, test_ids: [test_empty_capability_fields_are_allowed], evidence_ids: [EV-ENVIRONMENT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-IDENTITY, test_ids: [test_identity_boundary], evidence_ids: [EV-IDENTITY], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-DATA, test_ids: [test_data_contract], evidence_ids: [EV-DATA], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-EVIDENCE, test_ids: [test_evidence_and_observation_integrity], evidence_ids: [EV-EVIDENCE], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-OBSERVATION, test_ids: [test_evidence_and_observation_integrity], evidence_ids: [EV-OBSERVATION], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-RECOVERY, test_ids: [test_recovery_incident_and_support_mutations_are_denied], evidence_ids: [EV-RECOVERY], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-INCIDENT, test_ids: [test_recovery_incident_and_support_mutations_are_denied], evidence_ids: [EV-INCIDENT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-SUPPORT, test_ids: [test_recovery_incident_and_support_mutations_are_denied], evidence_ids: [EV-SUPPORT], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-RISK-MAPPING, test_ids: [test_risk_mapping], evidence_ids: [EV-EVIDENCE], local_synthetic_proof: true, real_world_authority: false}
  - {requirement_id: AC-AUTHORITY, test_ids: [test_valid_package_stops_at_human_governance], evidence_ids: [EV-EVIDENCE], local_synthetic_proof: true, real_world_authority: false}
```

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
git add Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml
git commit -m "feat(stage15): add risk mapping and acceptance matrix"
```

Expected: `PR-RISK-001` through `PR-RISK-010` remain blocked and every requirement maps to executable evidence.

## Task 9: Write the complete policy contract

**Files**

- Create: `Governance/AIOS-Nonproduction-Readiness-Integration-v1.md`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Defines operational meaning without granting operational authority.
- Separates local proof, risk disposition, pilot authority and release authority.

- [ ] Write all mandatory policy sections.

```markdown
## Business loop
## Core objects
## Data flow
## Operators
## AI and human judgment boundary
## Proof of operation
## Authority ceiling
## Component contracts
## Risk mapping
## Stop and withdrawal
## Lifecycle
```

```bash
python3 -m unittest Tests.test_nonproduction_readiness -v
git add Governance/AIOS-Nonproduction-Readiness-Integration-v1.md Tests/test_nonproduction_readiness.py
git commit -m "docs(stage15): define bounded nonproduction policy"
```

Expected: policy confirms the maximum result `needs_human_governance` and denies any interpretation as pilot, release or production approval.

## Task 10: Add the validation guide and reproducible local commands

**Files**

- Create: `Tests/AIOS-Nonproduction-Readiness-Validation.md`
- Modify/Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Documents clean installation, focused tests, full regression and negative cases.
- Uses repository-controlled development dependencies.

- [ ] Add exact commands and expected outcomes.

```markdown
python -m pip install -r requirements-dev.txt
python3 Tests/validate_aios_nonproduction_readiness.py
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest discover -s Tests -p "test_*.py" -v
```

```bash
python -m pip install -r requirements-dev.txt
python3 -m unittest Tests.test_nonproduction_readiness -v
git add Tests/AIOS-Nonproduction-Readiness-Validation.md Tests/test_nonproduction_readiness.py
git commit -m "docs(stage15): add reproducible validation guide"
```

Expected: a clean local clone can reproduce positive, negative and malformed-input results without credentials or network access.

## Task 11: Add pull-request-only read-only CI

**Files**

- Create: `.github/workflows/validate-aios-nonproduction-readiness.yml`
- Test: `Tests/test_nonproduction_readiness.py`

**Interfaces**

- Runs only for pull requests.
- Uses read-only contents permission and no persisted credentials.

- [ ] Add focused validation and full repository regression.

```yaml
name: Validate AIOS Nonproduction Readiness
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
      - run: python -m pip install -r requirements-dev.txt
      - run: python3 Tests/validate_aios_nonproduction_readiness.py
      - run: python3 -m unittest discover -s Tests -p "test_*.py" -v
```

```bash
python3 -m unittest Tests.test_project_governance -v
git add .github/workflows/validate-aios-nonproduction-readiness.yml Tests/test_nonproduction_readiness.py
git commit -m "ci(stage15): validate nonproduction readiness proof"
```

Expected: CI is pull-request-only, read-only, and every repository regression passes.

## Task 12: Complete lifecycle evidence and Mandatory Return

**Files**

- Modify: `Governance/AIOS-Stage-Registry.md`
- Modify: `Governance/AIOS-Project-Registry.md`
- Modify/Test: `Tests/test_project_governance.py`

**Interfaces**

- Moves Stage 15 only to `Reported`.
- Returns evidence to the Governance Thread without merging or granting authority.

- [ ] Record final evidence and stop.

```markdown
Mandatory Return:
- exact remote head and tree
- changed-file allowlist
- final-head CI links
- focused and full-regression results
- maximum result `needs_human_governance`
- risks remain open, blocked and unaccepted
- gates 1–3 are recorded governance decisions; gates 4–12 remain pending
- external actions performed: none
- merge, publication, archive, pilot and production: not authorized
```

```bash
python3 -m unittest Tests.test_project_governance -v
python3 -m unittest discover -s Tests -p "test_*.py" -v
git status --porcelain
git rev-parse HEAD
git rev-parse HEAD^{tree}
git add Governance/AIOS-Stage-Registry.md Governance/AIOS-Project-Registry.md Tests/test_project_governance.py
git commit -m "docs(stage15): report bounded implementation evidence"
```

Expected: Stage 15 is `Reported`, the changed-file allowlist is exact, final-head CI links are recorded, and work stops for independent human review.

## As-built executable closure

The direct owner instruction dated 2026-07-30 authorizes completion of all
pre-deployment repository work while continuing to prohibit deployment, real
data, real connectors, production credentials, production permissions and
business-data mutation. The dedicated execution assignment is Codex goal
`019fb137-f0bc-7e60-b8ad-efe1a8e250b1`; the implementation branch remains
`gov/aios-stage15-nonproduction-readiness-design`.

This section supersedes abbreviated examples earlier in the plan. The complete
executable definitions are the following repository-controlled source assets,
which are compiled, loaded and behavior-tested by
`test_stage15_as_built_closure_is_executable_not_token_only`:

- `Tests/validate_aios_nonproduction_readiness.py` contains complete definitions
  for `load_controlled_yaml_text`, `load_repository_yaml`, `_scan_capabilities`,
  `_fail_closed`, `validate_model`, `validate_fixture`,
  `evaluate_nonproduction_readiness` and `validate_repository`.
- `Tests/test_nonproduction_readiness.py` contains the positive, adversarial,
  malformed-type, cycle, alias, merge-key, purity, determinism, cross-file,
  CLI and read-only CI tests.
- `Governance/AIOS-Nonproduction-Readiness-Integration-Model-v1.yaml` and
  `Tests/Fixtures/nonproduction-readiness/synthetic-local-integration.yaml`
  contain the complete closed model and canonical synthetic fixture.
- `Governance/AIOS-Nonproduction-Readiness-Stage10-14-Mapping-v1.yaml` and
  `Governance/AIOS-Nonproduction-Readiness-Acceptance-Matrix-v1.yaml`
  contain all ten ordered risk mappings and all ten acceptance rows.
- `Governance/AIOS-Nonproduction-Readiness-Integration-v1.md`,
  `Tests/AIOS-Nonproduction-Readiness-Validation.md` and
  `.github/workflows/validate-aios-nonproduction-readiness.yml` contain the
  complete policy, reproducible validation contract and pull-request-only
  read-only CI.

The controlled loader rejects YAML anchors, aliases and merge keys before
construction by iterating `yaml.scan` tokens and denying `AnchorToken`,
`AliasToken` and a `ScalarToken` equal to `<<`. This prevents cyclic alias
graphs from entering `yaml.safe_load`.

The capability scanner is path- and value-aware:

```python
ALLOWED_EMPTY_CAPABILITY_PATHS = frozenset(
    {
        "$.environment.external_endpoints",
        "$.environment.connectors",
        "$.environment.credentials",
    }
)

def _scan_capabilities(
    value: Any,
    path: str = "$",
    active: set[int] | None = None,
) -> list[str]:
    """Allow only the three exact empty declarations and deny cycles."""
```

All public validation entry points place `copy.deepcopy` and the complete
validator call inside `_fail_closed`. Any malformed input exception, including
`RecursionError`, becomes a stable `validation_exception:<type>` denial.

```python
def _fail_closed(
    validator: Callable[[Any], list[str]],
    value: Any,
    path: str,
) -> list[str]:
    try:
        copied = copy.deepcopy(value)
        return validator(copied)
    except Exception as exc:
        return [_error(path, f"validation_exception:{type(exc).__name__}")]
```

The evaluator is a pure composition boundary. It performs no file, network,
environment, clock, randomness or process access and always returns false
authority claims plus an empty external-action list.

The acceptance matrix is also closed against exact test and evidence
identifiers. Replacing a requirement's test with a nonexistent test, or
reassigning evidence from another requirement, fails repository validation.

Run the exact closure evidence:

```bash
python3 Tests/validate_aios_nonproduction_readiness.py
python3 -m unittest Tests.test_nonproduction_readiness -v
python3 -m unittest Tests.test_project_governance -v
python3 -m unittest discover -s Tests -p 'test_*.py' -v
python3 Tests/validate_aios_workflow_schema.py
python3 Tests/validate_aios_operational_resilience.py
python3 Tests/validate_aios_support_controlled_pilot.py
python3 -m compileall -q Runtime Tests
git diff --check
git commit -m "feat(stage15): complete predeployment integration proof"
```

Expected: the canonical package returns `needs_human_governance`; every
adversarial or malformed case returns `denied`; all repository tests,
validators and compilation pass; Stage 10 remains `BLOCKED / NO-GO`; Stages
11–14 remain `Archived`; deployment and all real-world authority remain
withheld.

## Plan self-review checklist

- [ ] The written specification and this exact plan head have independent human approval.
- [ ] One dedicated Execution Task and one implementation branch are assigned before implementation.
- [ ] All new YAML files are closed mappings and contain no aliases or merge keys.
- [ ] The three exact empty capability paths are accepted only when values equal `[]`.
- [ ] Non-empty, misplaced, aliased and secret-bearing capability fields are denied.
- [ ] All validator entry points handle malformed types without exceptions.
- [ ] The positive fixture returns exactly `needs_human_governance`.
- [ ] Every negative fixture returns exactly `denied`.
- [ ] AC-ENVIRONMENT, AC-IDENTITY, AC-DATA, AC-EVIDENCE, AC-OBSERVATION, AC-RECOVERY, AC-INCIDENT, AC-SUPPORT, AC-RISK-MAPPING and AC-AUTHORITY are traceable.
- [ ] Policy contains Business loop, Core objects, Data flow, Operators, AI and human judgment boundary, Proof of operation, Authority ceiling, Component contracts, Risk mapping, Stop and withdrawal and Lifecycle.
- [ ] CI is pull-request-only and read-only.
- [ ] Stage 10 remains `BLOCKED / NO-GO`; Stages 11–14 remain `Archived`.
- [ ] Stage 15 stops at `Reported`; no merge, publication, archive, pilot or production is implied.
