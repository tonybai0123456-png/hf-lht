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
| Gate 5 accountable owner | Tony; Stone is backup and escalation contact; [Issue #42](https://github.com/tonybai0123456-png/hf-lht/issues/42) |
| Gate 6 architecture and security | Platform-neutral, synthetic and isolated non-production; Stone is the human approver and Developer Agent owns the technical solution and validation; [Issue #43](https://github.com/tonybai0123456-png/hf-lht/issues/43) |

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
Gate 5 assigns Tony as the single accountable Stage 15 owner and Stone as the
backup and escalation contact. This owner contract coordinates the gate ledger
and evidence; it grants no automatic merge, credential, permission, risk
acceptance, pilot, release or deployment authority.
Gate 6 authorizes only the repository-controlled, platform-neutral architecture
and security design and its synthetic validation in isolated non-production.
Stone is the human architecture and security approver; Developer Agent is
accountable and responsible for the technical solution and validation. This
does not authorize cloud resources, infrastructure, credentials, permissions,
real data, connectors, pilot, merge, publication, release or deployment.

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
`open_blocked_unaccepted`; their treatment owners remain
`unassigned / governance decision required`. The written specification,
implementation plan and dedicated execution assignment are recorded as
completed governance decisions. The Human Governance Thread accepted the exact
implementation evidence at reviewed target
`b27614ba2ebebb772888c3a4b1ff3d829b47532e`; the evaluator cannot grant or
revoke that decision. The owner authorization recorded through Issue #42
accepts Gate 5 for Tony, with Stone as backup and escalation contact;
gates 6 through 12 remain unauthorized.
The separate architecture and security authorization recorded through Issue
#43 accepts Gate 6 only. It uses a platform-neutral, synthetic and isolated
non-production boundary, with Stone as human approver and Developer Agent as
technical accountable and responsible owner; gates 7 through 12 remain
unauthorized. No cloud resource, credential, real-data, connector, pilot,
merge, publication, release or deployment authority is granted.
Risk acceptance, pilot authorization, production readiness and release
authorization remain exactly false.

## Component contracts

### Environment

The environment is local, synthetic and disposable. The canonical
`external_endpoints`, `connectors` and `credentials` declarations must be empty
lists. They are allowed only at their exact environment paths; non-empty or
misplaced capability fields are denied.

### Architecture and security

The approved design remains platform-neutral and repository-controlled. Its
only executable proof is deterministic synthetic validation in isolated
non-production local or pull-request CI contexts. No resource is provisioned,
no external network access is enabled, and no real credential, permission,
connector or data is used. Passing this proof is not production security
acceptance or risk acceptance.

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
real operational support owner, creates no ticket and commits to no SLA. The
Gate 5 governance owner is not an operational support assignment.

## Risk mapping

`PR-RISK-001` through `PR-RISK-010` map to ordered local evidence identifiers.
Stages 11–14 remain Archived design evidence only. Mapping evidence is
remediation evidence, not risk acceptance, risk closure, pilot authority,
production authority or release authority.

## Stop and withdrawal

Stop immediately on unknown fields, malformed types, cycles, YAML aliases or
merge keys, reordered or duplicate identifiers, excluded entities, external
locators, credentials, connectors, authority-like values, changed checksums,
incomplete recovery, unapproved operational owner names, external
communication, non-empty requested actions, or any attempt to exceed
`needs_human_governance`.

Withdrawal removes only disposable task-local synthetic state and preserves the
Git/GitHub evidence trail. It performs no external rollback and must never
delete shared, business or production data.

## Lifecycle

Stage 15 starts `Planned`. After an approved plan and explicit execution
assignment, implementation may move only through `Executing` to `Reported` with
a Mandatory Return. The Human Governance Thread accepted the exact reported
evidence at `b27614ba2ebebb772888c3a4b1ff3d829b47532e` and moved Stage 15 to
`Reviewed`. Reviewed does not authorize merge, publication, archive, Issue
closure, real pilot, production, deployment, release or Stage 16; each remains
a separate human Governance Thread decision. Gate 5 was separately accepted
through Issue #42 with Tony as the single accountable owner and Stone as backup
and escalation contact; at that decision point, gates 6 through 12 remained
unauthorized. Gate 6 was separately accepted through Issue #43 for the
platform-neutral, synthetic and isolated non-production architecture and
security design. Stone is the human approver and Developer Agent owns the
technical solution and validation; gates 7 through 12 remain unauthorized.
No cloud resource, credential, real-data, connector, pilot, merge, publication,
release or deployment authority is granted.

### Gate 7 privacy and data approval

Gate 7 was separately accepted through Issue #44 on 2026-07-31. Only
`synthetic_non_personal` and
`synthetic_personal_like_clearly_fictitious_non_routable` are authorized.
Tony is the human approver, Stone is backup and escalation contact, Data Agent
is technical validation owner, and Developer Agent provides implementation
support.

This approval does not authorize real customer, employee, business, payment or
production-derived data; live identifiers or contact details; credentials,
secrets or permission material; connectors, endpoints, infrastructure or
accounts; pilot, risk acceptance, merge, publication, release or deployment.
Gates 8 through 12 remain unauthorized, and Gate 8 is the only valid next
decision.
