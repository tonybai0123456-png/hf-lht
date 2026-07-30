# BUW AIOS Non-production Readiness Integration v1

## Document control

| Field | Value |
|---|---|
| Stage | Stage 15 / NR-01 |
| Company boundary | 汇沣电商 |
| Brand boundary | BUW only |
| Excluded entities | PC and 六合通 |
| Execution mode | Repository-controlled, local, synthetic and disposable |
| Maximum result | `needs_human_governance` |
| Production posture | Stage 10 remains `BLOCKED / NO-GO` |

## Business loop

Load one repository-controlled BUW synthetic package, validate it against the
closed model, evaluate it locally, record task-local evidence, and stop at
`needs_human_governance`. The loop performs no connector, network,
infrastructure, customer, store, order, employee, ticket, payment or production
action.

## Core objects

The core objects are the canonical model, environment manifest, simulated
principal, synthetic data contract, component result, task-local evidence
record, observation decision, rollback snapshot, recovery verification,
incident tabletop, support handoff, Stage 10–14 risk mapping, acceptance matrix
and normalized evaluator decision. Their identities and schemas are closed,
ordered and versioned.

## Data flow

Data flows only from four allowlisted repository YAML mappings into memory,
through validation and pure evaluation, to terminal output and disposable
task-local test evidence. No data leaves the process. Company is `汇沣电商`;
brand is `BUW`; `PC` and `六合通` are excluded. Inputs with aliases, merge keys,
unknown fields, external locators, real identifiers or non-synthetic provenance
are denied.

## Operators

The assigned implementation worker may edit only Stage 15 repository paths and
run local tests. The BUW AIOS Official Governance Thread separately approves
the plan, execution assignment, implementation evidence, named owners,
architecture and security, privacy and data, operations, each risk disposition,
pilot scope, pilot evidence, release, merge, publication and archive.

## AI and human judgment boundary

AI and deterministic code may validate syntax, types, identity, ordering,
evidence references, checksums, frozen boundaries and fail-closed behavior.
Humans alone may assign real owners, approve credentials or permissions, accept
risks, authorize a pilot, declare production readiness, approve release or
bypass a human gate. Silence is never approval.

## Proof of operation

A passing result proves only repository-contained local synthetic behavior,
deterministic denial of adversarial inputs, input immutability, evidence
consistency, synthetic recovery verification and absence of external actions.
It does not prove a live service, real environment, real connector, real data,
operational support, legal compliance, production readiness or deployment.

## Authority ceiling

The only evaluator results are `denied` and `needs_human_governance`. Stage 10
remains `BLOCKED / NO-GO`. `PR-RISK-001` through `PR-RISK-010` remain
`open_blocked_unaccepted`; owners remain
`unassigned / governance decision required`. The written specification,
implementation plan and dedicated execution assignment are recorded as
completed governance decisions. The evaluator cannot grant those decisions and
still requires implementation-evidence acceptance plus gates 5 through 12.
Risk acceptance, pilot authorization, production readiness and release
authorization remain exactly false.

## Component contracts

### Environment

The environment is local, synthetic and disposable. The canonical
`external_endpoints`, `connectors` and `credentials` declarations must be empty
lists. They are allowed only at their exact environment paths; non-empty or
misplaced capability fields are denied.

### Identity

Identity is simulated and scoped to one synthetic principal. Its permissions
allow only reading the committed fixture and writing disposable task-local
evidence. It cannot create, receive or use real credentials.

### Data

Data provenance is synthetic, classification is synthetic non-personal,
retention is task-local until cleanup, and deletion requires deterministic
cleanup evidence. No customer, employee, store, order or other business record
is permitted.

### Evidence and observation

Evidence is task-local append-only data with ordered identifiers and
deterministic checksums. Observation is a local decision only. Paging, ticket
creation and external delivery remain false.

### Recovery

Recovery snapshots only the named synthetic state. Restore is valid only when
pre- and post-restore checksums match and both restore and cleanup verification
are true. This is not a production rollback or RTO/RPO claim.

### Incident and support

Incident handling is tabletop-only, with no real incident declaration or
external communication. Support handoff routes to an abstract role, assigns no
real owner, creates no ticket and commits to no SLA.

## Risk mapping

`PR-RISK-001` through `PR-RISK-010` map to ordered local evidence identifiers.
Stages 11–14 remain Archived design evidence only. Mapping evidence is
remediation evidence, not risk acceptance, risk closure, pilot authority,
production authority or release authority.

## Stop and withdrawal

Stop immediately on unknown fields, malformed types, cycles, YAML aliases or
merge keys, reordered or duplicate identifiers, excluded entities, external
locators, credentials, connectors, authority-like values, changed checksums,
incomplete recovery, real owner names, external communication, non-empty
requested actions, or any attempt to exceed `needs_human_governance`.

Withdrawal removes only disposable task-local synthetic state and preserves the
Git/GitHub evidence trail. It performs no external rollback and must never
delete shared, business or production data.

## Lifecycle

Stage 15 starts `Planned`. After an approved plan and explicit execution
assignment, implementation may move only through `Executing` to `Reported` with
a Mandatory Return. `Reported` is not `Reviewed`. Review, merge, publication,
archive, Issue closure, real pilot, production, deployment, release and Stage 16
remain separate human Governance Thread decisions.
