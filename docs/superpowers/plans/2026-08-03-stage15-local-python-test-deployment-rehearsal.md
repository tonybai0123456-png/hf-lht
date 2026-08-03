# Stage 15 Local Isolated Python Test-Deployment Rehearsal Implementation Plan

> **Preparation status:** Complete implementation plan only. Implementation and execution remain unauthorized until Tony records a separate explicit written decision in Issue #51.

> **Authority ceiling:** Local isolated Python, no network, no credentials, repository-controlled BUW synthetic data only. The maximum successful claim is `local_python_test_deployment_rehearsal_passed_not_cloud_proof`.

**Goal:** Implement a deterministic, fail-closed local runner that exports one exact Git commit/tree into a disposable directory, exercises the existing repository-controlled BUW synthetic workflow without network or credentials, validates the exact evidence contract, produces a closed machine-readable receipt, proves cleanup and stops for human review.

**Design baseline:** `docs/superpowers/specs/2026-08-03-stage15-local-python-test-deployment-rehearsal-design.md` at `9ac660b0694ee2ee18d3c9e5e8cbc3b45fb4b31f`.

**Governance entry point:** Issue #51. Parent governance Issue #40. Controlled Draft PR #41.

**Tech stack:** Python 3 standard library, locally available PyYAML declared by `requirements-dev.txt`, `unittest`, YAML, Markdown and existing pull-request CI. No new dependency, package download, container, cloud account or infrastructure.

## Global constraints

- Company is exactly `汇沣电商`; brand is exactly `BUW`.
- `PC`, `六合通`, aliases, wildcards, shared and mixed scope are denied.
- Inputs come only from the exact exported Git tree and committed synthetic fixtures.
- No real customer, employee, supplier, store, order, payment, account, support or operational data.
- No credentials, secrets, tokens, permissions, external endpoints, connectors or outbound messages.
- No DNS lookup, socket connection, listener, browser, daemon or online package installation.
- No cloud, container installation, staging, pilot, production, release or deployment action.
- PR #41 remains Draft/open/unmerged.
- Stage 10 remains `BLOCKED / NO-GO`.
- PR-RISK-001 through PR-RISK-010 remain `open_blocked_unaccepted`.
- `pilot_authorized`, `production_ready`, `release_authorized`, `deployment_authorized` and `risks_accepted` remain false.
- `external_actions_performed` remains exactly `[]`.
- Any ambiguity, malformed input, recursive structure, unsafe path, missing local dependency or required network operation fails closed into a recorded `denied` or `blocked` receipt.
- The implementation branch is the existing PR #41 branch; no second implementation branch or parallel execution task is permitted.
- Implementation stops at a Draft-PR evidence report. It must not mark the PR Ready, merge, publish, archive, close an Issue or infer additional authority.

## Files and single responsibilities

Create only after explicit implementation authorization:

- `Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml`
  - Closed source-of-truth contract for identity, environment, fixture, commands, results, risk states and authority ceiling.
- `Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml`
  - Closed receipt schema, exact keys and exact result/status enumerations.
- `Runtime/stage15_local_python_rehearsal.py`
  - Local-only orchestration, exact-tree export, preflight, guarded execution, receipt generation and contained cleanup.
- `Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml`
  - BUW-only deterministic rehearsal input referencing existing repository-controlled synthetic assets.
- `Tests/test_stage15_local_python_rehearsal.py`
  - Focused RED/GREEN unit and integration-contract tests.
- `Tests/validate_aios_stage15_local_python_rehearsal.py`
  - Cross-asset repository validator with no external I/O.
- `Tests/AIOS-Stage15-Local-Python-Rehearsal-Validation.md`
  - Reproducible local commands, expected outputs, claims and limitations.

Modify only when required by the completed implementation:

- `.github/workflows/validate-aios-nonproduction-readiness.yml`
  - Add focused read-only validation commands only; no installation or external service.
- `Tests/test_project_governance.py`
  - Pin required assets and authority ceiling without authorizing execution.
- `Governance/AIOS-Stage-Registry.md` and `Governance/AIOS-Project-Registry.md`
  - Record implementation evidence only after explicit execution authorization and completed Mandatory Return; do not change Stage 15 beyond its authorized lifecycle state.

Do not modify the approved design, Gate 12 decision, post-Gate12 reconciliation, risk register or historical audit to make the rehearsal pass.

## Public interfaces

```python
from pathlib import Path
from typing import Any, Mapping, Sequence


def load_closed_yaml(path: Path) -> dict[str, Any]: ...

def validate_contract(contract: Any) -> list[str]: ...

def validate_fixture(fixture: Any) -> list[str]: ...

def validate_receipt(receipt: Any) -> list[str]: ...

def build_sanitized_environment(
    source: Mapping[str, str],
    *,
    temporary_root: Path,
    guard_path: Path,
) -> dict[str, str]: ...

def export_exact_candidate(
    *,
    repository_root: Path,
    source_commit: str,
    execution_root: Path,
) -> dict[str, Any]: ...

def run_guarded_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str],
    timeout_seconds: int,
) -> dict[str, Any]: ...

def normalize_smoke_output(output: Mapping[str, Any]) -> dict[str, Any]: ...

def run_rehearsal(
    *,
    repository_root: Path,
    source_commit: str,
    contract_path: Path,
    fixture_path: Path,
) -> dict[str, Any]: ...

def validate_repository(root: Path) -> list[str]: ...
```

All public entry points accept hostile or malformed Python/YAML shapes without leaking an uncaught exception. Stable errors use `path:reason_code` ordering.

## Closed result contract

The final receipt returns exactly one result:

```text
local_python_test_deployment_rehearsal_passed_not_cloud_proof
local_python_test_deployment_rehearsal_denied
local_python_test_deployment_rehearsal_blocked
```

Use `denied` for policy, identity, data, path, integrity, network, credential or authority violations. Use `blocked` for missing safe local prerequisites such as unavailable PyYAML, changed source head, unavailable exact candidate, cleanup verification failure or a test that requires network access.

Required receipt keys:

```yaml
schema_version: aios_stage15_local_python_rehearsal_receipt/v1
run_id: <non-secret identifier>
started_at_utc: <RFC3339 UTC>
finished_at_utc: <RFC3339 UTC>
company: 汇沣电商
brand: BUW
stage: Stage 15 / NR-01
mode: local_isolated_python_synthetic_only
result: <closed result enum>
source_commit: <40 lowercase hex>
source_tree: <40 lowercase hex>
file_inventory_sha256: <64 lowercase hex>
python_runtime:
  implementation: CPython
  version: <major.minor.patch>
  executable_label: approved_local_python
  user_site_enabled: false
  online_install_used: false
local_dependencies:
  PyYAML: <version or blocked>
fixture_ids: [NR-LOCAL-PYTHON-REHEARSAL-001]
fixture_checksums: {NR-LOCAL-PYTHON-REHEARSAL-001: <sha256>}
ordered_checks: []
smoke_result: {}
normalized_smoke_sha256: <sha256 or null>
network_guard:
  active: true
  attempted_operations: []
material_scan:
  credentials_found: false
  real_data_found: false
  external_endpoints_found: false
  nonempty_connectors_found: false
  infrastructure_material_found: false
cleanup:
  execution_directory_removed: true
  bytecode_directory_removed: true
  evidence_directory_preserved: false
  repository_unchanged: true
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
stage10_state: BLOCKED / NO-GO
pr41_state: draft_open_unmerged
cloud_capability_proven: false
pilot_authorized: false
production_ready: false
release_authorized: false
deployment_authorized: false
risks_accepted: false
external_actions_performed: []
reason_codes: []
evidence_refs: []
required_human_decisions: []
```

The schema allows no additional fields. The receipt must not contain absolute user-home paths, environment values, secret-like material, real-data content or unbounded command output.

## Stable reason codes

At minimum:

```python
REASON_CODES = (
    "SOURCE_COMMIT_INVALID",
    "SOURCE_HEAD_CHANGED",
    "SOURCE_TREE_MISMATCH",
    "SOURCE_WORKTREE_DIRTY",
    "ARCHIVE_MEMBER_UNSAFE",
    "FILE_INVENTORY_MISMATCH",
    "LOCAL_PYTHON_UNAVAILABLE",
    "LOCAL_DEPENDENCY_UNAVAILABLE",
    "CREDENTIAL_LIKE_ENVIRONMENT_PRESENT",
    "ENVIRONMENT_NOT_ALLOWLISTED",
    "NETWORK_OPERATION_ATTEMPTED",
    "COMMAND_NOT_ALLOWLISTED",
    "COMMAND_TIMEOUT",
    "COMPANY_SCOPE_DENIED",
    "BRAND_SCOPE_DENIED",
    "NON_SYNTHETIC_DATA_DENIED",
    "CAPABILITY_FIELD_NONEMPTY",
    "CAPABILITY_FIELD_MISPLACED",
    "SECRET_LIKE_MATERIAL_DENIED",
    "EXTERNAL_LOCATOR_DENIED",
    "AUTHORITY_CLAIM_DENIED",
    "SMOKE_OUTPUT_NONDETERMINISTIC",
    "RECEIPT_SCHEMA_INVALID",
    "CLEANUP_TARGET_UNSAFE",
    "CLEANUP_NOT_VERIFIED",
    "REPOSITORY_CHANGED",
    "MALFORMED_INPUT",
    "UNEXPECTED_RUNTIME_FAILURE",
)
```

Reason codes are de-duplicated while preserving first-observed order.

## Command allowlist

The runner constructs argv arrays directly and never invokes a shell. The only permitted command families are:

1. `git rev-parse --verify <source_commit>^{commit}`
2. `git rev-parse <source_commit>^{tree}`
3. `git status --porcelain --untracked-files=all`
4. `git archive --format=tar <source_commit>`
5. the already selected local Python executable with:
   - `-m unittest ...`
   - repository validator script paths under the exported tree;
   - `-m compileall -q` against approved repository directories;
   - the controlled orchestrator smoke entry point.

Prohibited command tokens include package managers, network tools, shells, interpreters other than the selected Python, service managers, browsers, container tools and infrastructure clients. Any unknown command is denied before subprocess creation.

## Network denial design

Create a task-local `sitecustomize.py` injected into every child Python process through the sanitized `PYTHONPATH`. It replaces these APIs with a recorder that raises `NetworkOperationDenied` before any network activity:

- `socket.socket.connect`
- `socket.socket.connect_ex`
- `socket.create_connection`
- `socket.getaddrinfo`
- `socket.gethostbyname`
- `socket.gethostbyname_ex`
- `socket.gethostbyaddr`

The recorder stores only operation name and a redacted destination category, never payloads, credentials or full addresses. Tests must attempt each guarded API and prove deterministic denial.

The runner itself does not execute Git fetch/pull/clone, package installation or any command that can require a remote. A missing local object returns `blocked`; it never triggers remote retrieval.

## Environment contract

The selected Python executable is resolved before sanitization and represented in receipts only as `approved_local_python`.

Parent environment names are inspected without recording values. Presence of a credential-like name fails closed, including case-insensitive fragments:

```text
TOKEN, SECRET, PASSWORD, PASSWD, API_KEY, APIKEY, CREDENTIAL,
AUTH, COOKIE, SESSION, DATABASE_URL, DB_URL, WEBHOOK,
AWS_, AZURE_, GOOGLE_APPLICATION_CREDENTIALS, GITHUB_TOKEN,
OPENAI_, SHOPIFY_, META_, FACEBOOK_, SLACK_
```

The child environment is rebuilt from an allowlist and contains only values required for local execution:

```text
PATH
LANG
LC_ALL
TMPDIR
PYTHONNOUSERSITE=1
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=<task-local network guard>
```

No inherited proxy variable, cloud configuration, home directory, user-site path, token or connector setting is passed to child processes.

## Exact candidate export and safe extraction

- Require a clean repository before export.
- Resolve the source commit and tree locally; do not fetch.
- Run `git archive --format=tar <source_commit>` with captured bytes.
- Parse with Python `tarfile`; do not invoke a shell tar command.
- Reject absolute names, `..` traversal, device files, FIFOs, hard links and symbolic links.
- Extract only regular files and directories under a newly created execution root.
- Inventory relative POSIX paths, sizes and SHA-256 checksums in sorted order.
- Hash the canonical inventory JSON to produce `file_inventory_sha256`.
- Verify every executed file path resolves under the execution root.

## Cleanup containment

The runner creates one top-level temporary root with a random opaque name and a marker file containing the run ID. Execution, bytecode and ephemeral evidence directories are children of that root.

Before removal, all conditions must be true:

- target resolves strictly beneath the top-level temporary root;
- top-level root resolves beneath the operating-system temporary directory;
- marker exists and matches the current run ID;
- target is not the repository root, user home, filesystem root or a parent of any of them;
- target was created by the current process and recorded before execution.

Use `shutil.rmtree` only after containment validation. If containment or removal verification fails, return `blocked`; never broaden the deletion target. The final receipt records boolean cleanup outcomes, not absolute paths.

## Determinism boundary

- Inject a fixed clock and fixed run ID in tests.
- Real rehearsal timestamps may vary, but the normalized smoke object excludes timestamps, run IDs, temporary paths, Python executable paths and unordered mappings.
- Serialize normalized output with UTF-8 canonical JSON: sorted keys, compact separators, `ensure_ascii=False`.
- Execute the focused smoke twice in fresh process state and require identical normalized bytes and SHA-256.
- The controlled orchestrator must stop at its existing human-approval boundary and must report no external writes.

## Task 0: Governance and provenance preflight

**Do not perform this task until Issue #51 contains an explicit owner authorization for the exact plan and execution assignment.**

- [ ] Record the authorizing Issue comment URL, timestamp, owner, exact plan commit and existing branch.
- [ ] Confirm PR #41 is Draft/open/unmerged.
- [ ] Confirm Stage 10 and all risk states are unchanged.
- [ ] Confirm the working tree is clean and source objects are local.
- [ ] Record `external_actions_performed=[]`.

Stop with no implementation if any authority is ambiguous.

## Task 1: Create RED tests and pin interfaces

**Files**

- Create: `Tests/test_stage15_local_python_rehearsal.py`

**RED tests**

- public interfaces exist;
- closed result and reason-code enums are exact;
- exact commit/tree export succeeds only for a local object;
- unsafe archive members are denied;
- secret-like environment names are denied without exposing values;
- network APIs are denied and recorded;
- BUW synthetic fixture passes while PC, 六合通, wildcard and mixed scope fail;
- exact empty `external_endpoints`, `connectors`, `credentials` pass only at approved paths;
- non-empty or misplaced capability fields fail;
- authority-like outputs fail;
- repeated smoke output is deterministic;
- cleanup cannot target outside the task root;
- malformed, recursive and type-polluted inputs produce a receipt;
- additional receipt keys fail the schema.

Run the focused tests and record the expected RED result before implementation.

## Task 2: Add closed contract and receipt schema

**Files**

- Create: `Governance/AIOS-Stage15-Local-Python-Rehearsal-Contract-v1.yaml`
- Create: `Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-Schema-v1.yaml`

The contract pins:

- exact company, brand, stage and mode;
- exact allowed file and command families;
- exact environment names and forbidden fragments;
- exact fixture IDs and approved capability paths;
- exact result states and reason codes;
- exact ten-risk state map;
- exact false authority flags;
- maximum claim and required human decisions.

The receipt schema uses exact mappings, exact scalar types, exact ordered risk IDs and `additional_properties: false` semantics implemented by the validator.

## Task 3: Add the rehearsal fixture

**Files**

- Create: `Tests/Fixtures/nonproduction-readiness/local-python-rehearsal-synthetic.yaml`

The fixture references, but does not mutate, `synthetic-local-integration.yaml`. It must include:

- scenario ID `NR-LOCAL-PYTHON-REHEARSAL-001`;
- company `汇沣电商`, brand `BUW`;
- committed synthetic provenance;
- exact controlled workflow and input paths;
- empty capability fields at approved paths;
- no free-form imported business text;
- no external locator, connector, credential or requested external action;
- expected controlled orchestrator stop state and expected normalized output fields.

## Task 4: Implement closed loading and validation helpers

**Files**

- Create: `Runtime/stage15_local_python_rehearsal.py`
- Extend: `Tests/test_stage15_local_python_rehearsal.py`

Implement exact-key, exact-type validators and a cycle-safe traversal using object identity tracking. YAML anchors, aliases and merge keys are rejected before semantic validation. `deepcopy`, traversal and normalization occur inside the fail-closed boundary.

No validator reads environment, network, clock, randomness or external state.

## Task 5: Implement exact-tree export and inventory

Implement local object resolution, clean-tree check, `git archive`, safe extraction and canonical inventory hashing. Add negative tests for traversal, links, device members, commit mismatch, tree mismatch and dirty-source substitution.

## Task 6: Implement environment isolation and network guard

Implement parent environment-name inspection, child allowlist construction, task-local `sitecustomize.py`, socket-denial recording and explicit command allowlisting. Add tests for every guarded socket API, proxy/cloud/token variables and unknown commands.

Do not call a package manager. Check PyYAML by import and `importlib.metadata.version`; return `blocked` when unavailable.

## Task 7: Implement deterministic controlled-orchestrator smoke

Run the existing controlled orchestrator from the exported tree with the approved synthetic fixture. Use an injected fixed clock for tests. Verify:

- company/brand/synthetic/dry-run boundaries;
- no external write;
- stop at the existing human-approval gate;
- exact accountable/handoff behavior required by the selected workflow;
- no authority-like claim;
- identical normalized output from two fresh runs.

## Task 8: Implement receipt assembly and closed validation

Every code path, including unexpected exceptions, produces a schema-valid receipt. Error receipts redact command output and never include environment values or absolute home paths. A `passed_not_cloud_proof` result is impossible unless every ordered check, deterministic comparison and cleanup check passes.

## Task 9: Implement contained cleanup

Add marker-based path containment, removal and absence verification. Tests use temporary directories only and prove repository, parent, home and filesystem-root targets are denied. Cleanup failure returns `blocked` with evidence; it never retries against a broader path.

## Task 10: Add repository validator and validation guide

**Files**

- Create: `Tests/validate_aios_stage15_local_python_rehearsal.py`
- Create: `Tests/AIOS-Stage15-Local-Python-Rehearsal-Validation.md`

The validator cross-checks contract, schema, fixture, runner, tests, approved design, Stage Registry, risk register, Gate 12 decision and post-Gate12 reconciliation. It denies drift in company/brand, risk states, Stage 10 state, PR lifecycle or downstream authority flags.

The guide records exact local commands, expected RED/GREEN sequence, local dependency behavior, evidence limitations and the no-cloud/no-pilot/no-production claim.

## Task 11: Restore GREEN and run repository validation

Run in this order with the already available local interpreter/isolated environment:

1. focused rehearsal tests;
2. rehearsal repository validator;
3. Project Governance tests;
4. all repository unit tests;
5. existing repository validators;
6. Python compilation;
7. whitespace/diff checks.

No dependency download is allowed. If PyYAML is unavailable in the selected local interpreter, record a blocked result and stop.

## Task 12: Execute one clean-export rehearsal

Only after Tasks 1–11 are green and Issue #51 explicitly authorizes execution:

- select and record the exact remote head and tree;
- run from a clean repository;
- export the exact candidate;
- execute all four phases in disposable directories;
- produce one closed receipt;
- verify cleanup and unchanged repository;
- verify `external_actions_performed=[]`;
- stop for independent evidence review.

Do not repeat a failed run after changing code without producing a new exact commit and new evidence identity.

## Task 13: Exact-head CI and Mandatory Return

Push the implementation evidence to the existing Stage 15 branch. Wait for every required exact-head PR workflow. The Mandatory Return must include:

- exact commit and tree;
- changed-file manifest;
- focused and full test counts;
- validator and compilation outcomes;
- exact-head workflow links and outcomes;
- rehearsal result and receipt checksum;
- cleanup proof;
- risk states and Stage 10 state;
- all false authority flags;
- limitations: no cloud, real pilot or production capability tested;
- `external_actions_performed=[]`.

Stop at human review. Do not mark PR #41 Ready, merge, publish, archive, close an Issue, accept risk, start a real pilot, create infrastructure or deploy.

## Implementation acceptance criteria

The implementation may be reported complete only when:

1. Issue #51 contains explicit authorization for this exact plan, branch and execution assignment.
2. The RED result was recorded before implementation.
3. All seven required assets exist with closed schemas and single responsibilities.
4. Exact local commit/tree export and safe extraction are proven.
5. No online installation, DNS lookup, socket connection or external write occurred.
6. No credential or secret value was used, emitted or persisted.
7. All executed data is BUW-only, committed and synthetic.
8. Empty approved capability fields pass; non-empty or misplaced fields deny.
9. Malformed, recursive and unexpected inputs return a valid receipt.
10. Repeated normalized smoke output is byte-for-byte deterministic.
11. The complete receipt validates with no additional fields.
12. Cleanup removes only task-created paths and is independently verified.
13. The repository remains unchanged by the rehearsal itself.
14. Focused, full, governance, validator and compilation checks pass.
15. All exact-head GitHub Actions pass.
16. All ten risks remain `open_blocked_unaccepted`.
17. Stage 10 remains `BLOCKED / NO-GO`.
18. PR #41 remains Draft/open/unmerged.
19. Every downstream authority flag remains false.
20. The final report states `external_actions_performed=[]` and explicitly says cloud, real-pilot and production capability remain untested and unproven.

## Current stop state

This plan is now ready for independent governance review. It does not authorize Task 0 or any implementation/execution task. The next valid action is a separate explicit owner decision in Issue #51 approving or rejecting the exact plan and, if approved, assigning the Developer Agent to the existing Stage 15 branch.