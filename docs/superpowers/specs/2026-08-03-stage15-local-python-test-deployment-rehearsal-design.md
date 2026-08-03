# Stage 15 Local Isolated Python Test Deployment Rehearsal Design

## Document control

| Field | Value |
|---|---|
| Company | 汇沣电商 |
| Brand | BUW |
| Stage | Stage 15 / NR-01 |
| Gate state | Gate 12 approved; all downstream lifecycle actions withheld |
| Design status | Approved target; implementation not yet authorized by this document |
| Approved approach | A — local isolated Python test environment |
| Approval date | 2026-08-03 |
| Draft PR | [PR #41](https://github.com/tonybai0123456-png/hf-lht/pull/41) |
| Governance issue | [Issue #40](https://github.com/tonybai0123456-png/hf-lht/issues/40) |
| Reconciliation issue | [Issue #50](https://github.com/tonybai0123456-png/hf-lht/issues/50) |
| Remote branch | `gov/aios-stage15-nonproduction-readiness-design` |
| Reviewed source baseline | `89f308c2a3ae76ed67c8b6f957f4ed31dea3011a` |
| Reviewed source tree | `222d49e8d3ba9ca1321088b7694229b18b2101fb` |
| Maximum claim | Local deployment rehearsal only; not cloud, pilot or production proof |

## Why this rehearsal is needed

Stage 15 already has repository-contained governance and synthetic validation
evidence, but that evidence does not yet prove that one exact candidate can be
unpacked into a clean local directory, executed by an isolated Python runtime,
validated without external access, and cleaned up with a complete receipt.

This design closes that narrow evidence gap. It deliberately does not create a
cloud environment, use a real connector, contact a participant, process real
data or exercise production operations. A passing result proves only that the
exact repository candidate can complete the bounded local rehearsal described
here.

## Authority ceiling

The 2026-08-03 decision authorizes the design target as:

> Local isolated Python test environment; no network, no credentials and pure
> synthetic data. Work may proceed continuously. The result is a deployment
> rehearsal and does not prove cloud capability.

The decision does not authorize any of the following:

- marking PR #41 Ready for Review;
- merging, formally publishing, archiving or closing an Issue;
- accepting, downgrading or closing PR-RISK-001 through PR-RISK-010;
- a real participant, real pilot or real business workflow;
- real, personal, customer, employee, order or operational data;
- credentials, secrets, permissions or identity-provider changes;
- network access, external endpoints, connectors or outbound messages;
- cloud accounts, infrastructure, containers requiring installation, staging,
  production, release or deployment;
- any BUW/PC combined view or any action for PC or 六合通.

Silence, a passing test, a green CI check or a successful rehearsal must never
be interpreted as additional authority.

## Six system questions

### 1. What business loop is being proved?

An exact Git candidate is identified, exported into a disposable local working
directory, checked against the environment and data boundaries, exercised with
synthetic inputs, validated, recorded in a machine-readable receipt and cleaned
up. The loop ends at human review of that receipt. It does not continue into a
pilot, release or production action.

### 2. What are the core objects?

The controlled objects are:

1. **Candidate identity** — exact commit, tree and changed-file inventory.
2. **Environment contract** — interpreter, dependency and isolation rules.
3. **Synthetic fixture set** — repository-controlled BUW-only non-personal and
   explicitly fictional, non-contactable and non-routable data.
4. **Rehearsal run** — deterministic commands executed against the export.
5. **Run receipt** — results, versions, checksums, reason codes and evidence.
6. **Cleanup receipt** — proof that the disposable export was removed without
   deleting repository or user data.
7. **Authority record** — explicit false values for every withheld downstream
   action and an empty `external_actions_performed` list.

### 3. Where does data come from and where does it settle?

Source material comes only from the exact Git tree and its committed synthetic
fixtures. The candidate is exported with `git archive` into a newly created
temporary directory. Validation runs locally and writes only task-local,
non-secret evidence into a separate temporary evidence directory. The final
receipt may be copied into the repository only when it contains no absolute
home paths, credentials, secrets or personal data. Temporary execution material
is then removed and the cleanup result is recorded.

No data is read from or written to a cloud service, database, connector, user
account, customer system, shared filesystem or external endpoint.

### 4. Who operates and reviews it?

| Responsibility | Role |
|---|---|
| Scope owner and human governance approver | Tony |
| Independent review, stop and escalation | Stone |
| Technical design, implementation and execution | Developer Agent |
| Technical evidence verification | Data Agent |
| Synthetic support-evidence contribution only | CustomerService Agent |

These roles do not grant credentials, infrastructure authority, real-data
access, pilot authority, release authority or risk acceptance.

### 5. What does the system decide and what remains human?

Deterministic code may decide whether the exact candidate, environment,
fixtures, tests, output schema, material scans and cleanup evidence satisfy this
design. It must fail closed on ambiguity or boundary violations.

Humans alone decide any later Ready-for-Review transition, merge, risk
disposition, real environment, credential, connector, pilot, release,
production or deployment action.

### 6. How is successful operation proved?

A valid receipt must bind all results to the exact commit and tree and include:

- Python executable identity and version;
- locally available dependency versions and their source;
- proof that online dependency installation was not used;
- synthetic fixture identifiers and checksums;
- focused tests, full tests, validators and compile results;
- deterministic runtime smoke result;
- secret, credential, real-data, connector and infrastructure scan results;
- network-prohibition controls and detected network attempts;
- working-tree difference check;
- temporary-directory cleanup result;
- `external_actions_performed: []`;
- explicit statements that cloud, pilot and production capabilities were not
  tested or proven.

## Options considered

### A — local isolated Python runner (selected)

This is immediately achievable with existing repository assets and a local
Python interpreter. It requires no new software, account, network or
infrastructure. Its limitation is equally explicit: it does not demonstrate
cloud packaging, networking, managed identity, observability or production
operations.

### B — local container rehearsal

A container would improve packaging parity, but Docker or Podman is not part of
the verified local baseline. Installing or configuring it would add software
and authority outside the current decision.

### C — isolated cloud test environment

This would provide stronger environmental evidence but requires a provider,
account, budget, credentials, permissions, network and infrastructure scope.
All remain separately governed and are outside this design.

## Rehearsal architecture

```text
exact Git commit/tree
        |
        v
git archive -> new disposable directory
        |
        v
boundary preflight
  - BUW only
  - synthetic only
  - no endpoints/connectors/credentials
  - local Python and local dependencies only
        |
        v
deterministic local execution
  - runtime smoke
  - focused and full tests
  - validators and compile
  - material and difference scans
        |
        v
machine-readable receipt -> independent evidence review
        |
        v
disposable directory cleanup -> cleanup receipt -> stop
```

The runner must not open a listening service, start a background daemon, use a
browser, perform DNS resolution, make a socket connection or invoke a package
manager in online mode.

## Environment contract

### Interpreter

- Use a pre-existing local Python 3 interpreter recorded in the receipt.
- Prefer a repository-local virtual environment when already present and
  verified; otherwise use an isolated temporary virtual environment populated
  only from an already available local package cache.
- Set `PYTHONNOUSERSITE=1` to avoid user-site dependency leakage.
- Route bytecode to a disposable path with `-X pycache_prefix=<temporary path>`
  or disable bytecode writes when compilation evidence is collected separately.
- Do not modify the system Python installation.

### Dependencies

- `requirements-dev.txt` is the declared dependency input.
- No dependency may be downloaded during the rehearsal.
- If a required dependency such as PyYAML is not already available from the
  approved interpreter or a verified local cache, return a blocked result with
  evidence; do not enable network access.
- Record the exact package versions actually imported.
- Do not add a dependency solely to make the rehearsal pass without a separate
  reviewed repository change.

### Process and environment isolation

- Create execution and evidence directories with unique temporary paths.
- Start with a minimal allowlist of environment variables required to locate
  the interpreter, temporary directory and locale.
- Reject credential-like or connector-like environment variables rather than
  recording their values.
- Do not inherit proxy variables, cloud-provider settings, API tokens, database
  URLs or service credentials.
- Use repository files from the exported exact tree, not mutable files from the
  developer's working tree.

### Network prohibition

The implementation plan must provide a deterministic control that makes Python
socket connection attempts fail locally and records attempted use without
capturing payloads. The rehearsal must also scan commands and configuration for
external URLs, endpoints or connector requests. A required network operation is
a blocked result, not permission to request or use network access.

## Synthetic data contract

Every exercised record must satisfy all of these rules:

- company is exactly `汇沣电商`;
- brand is exactly `BUW`;
- provenance explicitly identifies a committed synthetic fixture;
- no real identifier, address, phone number, email, order, payment, employee,
  customer or free-form imported business text is present;
- any person-like record is explicitly fictional, non-contactable and
  non-routable;
- `external_endpoints`, `connectors` and `credentials` are present only at their
  approved schema paths and are exactly empty lists;
- retention and cleanup behavior applies only to temporary synthetic evidence;
- cross-company, cross-brand, wildcard, unknown or mixed scope is denied.

The runner must not accept a command-line path outside the exported candidate
and its temporary evidence directory as a fixture input.

## Execution phases

### Phase 1 — exact-candidate preflight

1. Resolve the approved remote head and exact tree.
2. Confirm the local working tree is clean before starting.
3. Export the exact commit with `git archive` into a fresh temporary directory.
4. Inventory and checksum the exported files.
5. Verify that the export matches the recorded tree and contains no uncommitted
   developer files.

### Phase 2 — environment and material preflight

1. Record interpreter and local dependency versions.
2. Verify the minimal environment allowlist.
3. Validate every selected fixture against the synthetic data contract.
4. Scan for credentials, secrets, non-empty connectors, external endpoints,
   infrastructure definitions and real-data indicators.
5. Stop before runtime execution if any preflight check fails.

### Phase 3 — deterministic execution

1. Run the focused rehearsal contract tests.
2. Execute the existing controlled orchestrator with the approved synthetic
   local-integration fixture.
3. Verify the exact deterministic result and the authority ceiling.
4. Run repository validators, full test suite and Python compilation.
5. Repeat the focused run and compare normalized outputs to prove determinism.

### Phase 4 — evidence and cleanup

1. Generate a schema-validated machine-readable run receipt.
2. Confirm no external action, background process or listener was created.
3. Remove only the exact temporary execution and bytecode directories created
   for this rehearsal.
4. Verify their absence and record cleanup evidence.
5. Recheck the repository working tree and stop for human evidence review.

## Required result contract

The machine-readable receipt must return exactly one of:

- `local_python_test_deployment_rehearsal_passed_not_cloud_proof`;
- `local_python_test_deployment_rehearsal_denied`;
- `local_python_test_deployment_rehearsal_blocked`.

`passed_not_cloud_proof` is allowed only when every required check passes,
cleanup succeeds and all downstream authority flags remain false.

The receipt must contain at least:

- `schema_version`;
- `run_id` and UTC timestamps;
- `company`, `brand`, `stage` and `mode`;
- `source_commit`, `source_tree` and file-inventory checksum;
- `python_runtime` and imported dependency versions;
- `fixture_ids` and fixture checksums;
- ordered test and validator results;
- deterministic smoke outputs and normalized output checksum;
- material-scan and network-prohibition results;
- cleanup result;
- `risk_states` for exactly PR-RISK-001 through PR-RISK-010;
- `stage10_state: BLOCKED / NO-GO`;
- `pr41_state: draft_open_unmerged`;
- `cloud_capability_proven: false`;
- `pilot_authorized: false`;
- `production_ready: false`;
- `release_authorized: false`;
- `deployment_authorized: false`;
- `risks_accepted: false`;
- `external_actions_performed: []`;
- ordered reason codes, evidence references and required human decisions.

The receipt must never contain an environment-variable value, secret-like
material, absolute user-home path or real-data content.

## Fail-closed and stop conditions

Return `denied` when there is a boundary or integrity violation, including:

- company or brand mismatch;
- non-synthetic, ambiguous or externally sourced fixture content;
- non-empty or misplaced endpoint, connector or credential fields;
- secret-like material or credential-like environment variables;
- an external address, socket attempt, listener or background process request;
- an unapproved input or output path;
- candidate commit/tree mismatch or dirty-source substitution;
- a runtime output that claims approval, readiness, risk acceptance, pilot,
  release, production or deployment authority;
- cleanup targeting anything other than the exact task-created temporary paths.

Return `blocked` when the rehearsal cannot safely proceed without new authority
or a missing local prerequisite, including:

- the remote head changed after candidate selection;
- the required local Python version or dependency is unavailable;
- a validator or test cannot run without network access;
- cleanup cannot be verified;
- the exact candidate or evidence schema is unavailable.

Exceptions, malformed YAML, aliases, recursive structures, type pollution and
unexpected process failures must be converted into deterministic denied or
blocked receipts. They must not escape as an unrecorded partial run.

## Acceptance criteria

The implementation is acceptable only when all of the following are proven by
automated tests and a complete receipt:

1. The exact commit and tree are exported and independently verified.
2. The execution directory contains only files from that exact tree.
3. No online installation, DNS lookup, socket connection or external write is
   performed.
4. No credential or secret value is used, emitted or persisted.
5. All executed data is BUW-only and satisfies the synthetic data contract.
6. Empty approved capability fields pass; non-empty or misplaced capability
   fields fail closed.
7. Focused positive, negative, malformed-input and network-attempt tests pass.
8. Full repository tests, validators and compilation pass from the export.
9. Repeated normalized smoke output is byte-for-byte deterministic.
10. The run receipt validates against a closed schema.
11. Cleanup removes only task-created temporary paths and is verified.
12. The repository working tree remains unchanged by the rehearsal.
13. All ten risks remain open, blocked and unaccepted.
14. Stage 10 remains `BLOCKED / NO-GO`.
15. PR #41 remains Draft, open and unmerged.
16. Every downstream authority flag is false and
    `external_actions_performed` is exactly an empty list.
17. The final report explicitly states that cloud, real-pilot and production
    capability remain untested and unproven.

## Test strategy

The implementation plan must start with failing tests for:

- exact-commit/tree export verification;
- environment allowlisting and credential-like variable rejection;
- network-attempt denial;
- synthetic fixture boundary validation;
- non-empty and misplaced capability denial;
- exact output schema and forbidden authority claims;
- deterministic repeated execution;
- cleanup-path containment and verified cleanup;
- malformed inputs and unexpected runtime errors producing receipts rather
  than uncaught exceptions.

Only after those tests are observed failing may the smallest runner, validator,
schema and synthetic receipt fixture be implemented. Focused tests must be made
green before the full suite and clean-export rehearsal are run.

## Evidence review and governance outcome

Developer Agent may implement and execute the approved local rehearsal after a
separate implementation authorization. Data Agent verifies receipt integrity
and evidence completeness. Stone independently reviews boundary preservation
and may stop or escalate. Tony retains the human decision on any later action.

The maximum successful conclusion is:

`local_python_test_deployment_rehearsal_passed_not_cloud_proof`

That conclusion means only that the exact candidate passed the local,
no-network, no-credential, synthetic rehearsal. It does not change Stage 10,
the ten risk states, PR #41 lifecycle state or any downstream authorization.

## Mandatory Return for the future implementation

The implementation return must include:

1. exact remote commit and tree;
2. changed-file inventory;
3. interpreter and local dependency versions;
4. focused, full, validator, compile and deterministic-smoke results;
5. machine-readable receipt path and checksum;
6. material, environment and network-prohibition scan results;
7. cleanup verification;
8. exact GitHub Actions results for the pushed head;
9. PR-RISK-001 through PR-RISK-010 states;
10. current PR and Issue states;
11. unperformed external actions, with
    `external_actions_performed: []`;
12. explicit statement that cloud and production capability remain unproven;
13. one consolidated instruction for the next human decision.

