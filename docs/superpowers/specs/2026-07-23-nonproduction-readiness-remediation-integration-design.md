# Stage 15 Non-production Readiness Remediation and Integration Validation Design

## Document control

| Field | Value |
|---|---|
| Stage | 15 / NR-01 |
| Status | Planned; governance-design gate only |
| Governance decision | 方案 B |
| Issue | [Issue #40](https://github.com/tonybai0123456-png/hf-lht/issues/40) |
| Draft PR | [PR #41](https://github.com/tonybai0123456-png/hf-lht/pull/41) |
| Governance-design branch | `gov/aios-stage15-nonproduction-readiness-design` |
| Main baseline | `403f97ea56678185398ee52fff2b35eeff7a700f` |
| Implementation assignment | dedicated Execution Task and implementation branch unassigned |
| Human review | required before an implementation plan or Executing transition |

## Purpose and authority

Stage 15 is designed to close the gap between design-only evidence and a
repeatable, repository-contained non-production integration proof. It does not
make BUW AIOS production-ready and does not authorize a real pilot.

The maximum positive result of any future Stage 15 evaluator is
`needs_human_governance`. Invalid, incomplete, cross-boundary or authority-like
inputs must fail closed as `denied`. Neither result accepts a risk, assigns a
real owner, authorizes a pilot or grants release authority.

This written specification is the only authorized deliverable in the current
gate. Functional implementation, an implementation plan and a dedicated
Execution Task require later, separate human decisions.

## Six system questions

### Business loop

A later, separately authorized Stage 15 implementation would assemble one
versioned local non-production package from repository-controlled code and
synthetic fixtures; validate its topology, simulated identity boundary,
synthetic data contract, durable local evidence, observation signals, rollback
snapshot, incident tabletop and support handoff; then stop at a human governance
decision. It performs no external action and cannot enter a real pilot.

### Core objects

The controlled objects are non-production package, environment manifest,
synthetic workload, simulated principal, policy decision, dependency, local
evidence store, telemetry event, audit record, rollback snapshot, recovery
verification, incident scenario, support handoff, readiness gap, Stage 10 risk,
human gate and governance decision.

### Data flow

Inputs are version-controlled policy, code and synthetic fixtures. Processing is
local and isolated. Outputs are deterministic validation results and
repository-contained synthetic evidence without credentials, personal data,
external endpoints or external writes. A later Draft PR may carry reviewed
evidence; no production, staging or business-system data flow is permitted.

### Operators

The Governance Thread approves the written specification, implementation plan,
dedicated Execution Task, evidence acceptance, risk disposition, pilot scope and
release as separate decisions. A future dedicated Execution Task may build and
test only the approved local package. Architecture, security, privacy/data,
operations, support and business owner roles remain
`unassigned / governance decision required`.

### AI and human judgment boundary

AI and deterministic tests may validate schemas, exact identifiers, evidence
completeness, local behavior, fail-closed decisions and frozen boundaries.
Humans alone approve the specification, plan, execution assignment, evidence,
real owners, credentials, permissions, real data, risk acceptance, pilot entry,
external action, production and release. Silence is never approval.

### Proof of operation

Future implementation proof requires reproducible commands, positive and
adversarial tests, repository-tree evidence, pull-request-only read-only CI and
an exact-head Mandatory Return. Passing this proof shows only that the bounded
local non-production package behaves as specified. It does not prove that any
real environment, connector, data source, operator, pilot or production service
exists.

## Business and authority boundaries

- Allowed company: 汇沣电商.
- Allowed brand: BUW.
- Excluded brand: PC, which remains independently governed.
- Excluded company: 六合通.
- Allowed data: synthetic fixtures committed to the repository.
- Allowed environment: local, isolated and disposable non-production execution.
- Allowed persistence: task-local synthetic evidence with deterministic cleanup
  and no shared external service.
- Prohibited: real data, production or staging systems, external infrastructure,
  network connectors, API calls, databases, credentials, secrets, permission
  changes, external messages, real owner assignment, risk acceptance, real pilot
  and release.
- Cross-company, cross-brand, wildcard, unknown or mixed scope defaults to deny.

## Design approaches and approved choice

### Approach A — documentation-only remediation

This would extend governance records without proving integrated behavior. It is
lower effort but leaves the design-to-execution gap open.

### Approach B — repository-contained non-production integration

This design specifies a local, synthetic and disposable integration package with
deterministic evidence and fail-closed governance. It is the approved approach
because it can test integration behavior without creating external authority.

### Approach C — real controlled-pilot preparation

This would require real owners, systems, data and operational authority. It is
outside Stage 15 and remains prohibited while Stage 10 is BLOCKED / NO-GO.

## Proposed component boundaries

The future implementation plan must keep these components independently
understandable and testable:

1. **Environment manifest** — declares exact local components, versions,
   dependencies and prohibited external endpoints.
2. **Simulated identity policy** — uses synthetic principals and deny-by-default
   permissions; it cannot create or read real credentials.
3. **Synthetic data contract** — enforces company, brand, classification,
   provenance, retention and deletion fields.
4. **Local evidence store** — records append-only synthetic audit events and
   deterministic identifiers inside the task-local package.
5. **Observation model** — generates local metrics and alert decisions without
   paging, monitoring connectors or external delivery.
6. **Rollback and recovery model** — snapshots only synthetic local state,
   restores it deterministically and verifies the restored checksum.
7. **Incident tabletop model** — evaluates synthetic scenarios and prepares an
   evidence bundle without declaring or operating a real incident.
8. **Support handoff model** — prepares a synthetic case and abstract role
   routing without creating a ticket or assigning a real owner.
9. **Readiness evaluator** — composes all controls using
   most-restrictive-wins and returns only `denied` or
   `needs_human_governance`.

No component may silently substitute an in-memory or local test result for
production evidence.

## Stage 10 risk remediation mapping

All risks remain unaccepted. Stage 15 may prepare remediation evidence only.

| Risk | Planned local control evidence | Authority retained by humans |
|---|---|---|
| PR-RISK-001 | Versioned environment manifest, dependency graph and local package startup/teardown proof | Architecture acceptance and any external environment |
| PR-RISK-002 | Simulated principal, deny-by-default policy and secret-free scan | Identity, credentials, permissions and security acceptance |
| PR-RISK-003 | Synthetic classification, minimization, retention and deletion validation | Real-data classification and privacy approval |
| PR-RISK-004 | Synthetic source contract, lineage, quality and reconciliation tests | Real source and metric approval |
| PR-RISK-005 | Local durable telemetry, audit retention and deterministic alert-decision tests | Real monitoring, alerts, paging and SLO acceptance |
| PR-RISK-006 | Synthetic snapshot, rollback trigger, restore and checksum verification | Real rollback authority, RTO/RPO and environment recovery |
| PR-RISK-007 | Synthetic severity, containment, escalation and evidence tabletop | Real incident authority and communications |
| PR-RISK-008 | Synthetic intake, handoff, service target and runbook exercise | Real support owner, coverage and SLA |
| PR-RISK-009 | Negative tests for BUW/PC and 汇沣电商/六合通 separation | Any combined view or cross-boundary exception |
| PR-RISK-010 | Exact lifecycle and authority-ceiling tests | Risk acceptance, pilot, release and production decisions |

The mapping does not close, downgrade or accept PR-RISK-001 through
PR-RISK-010. Each risk disposition remains a later Governance Thread decision.

## Decision contract

The future evaluator contract must be pure and side-effect free.

Allowed results:

- `denied` — evidence, identity, boundary, integrity or authority validation
  failed.
- `needs_human_governance` — every local synthetic validation passed, but every
  real-world authority remains withheld.

Required output fields:

- `result`;
- ordered unique `reason_codes`;
- ordered unique `evidence_refs`;
- ordered unique `required_human_gates`;
- `risk_states`, containing exactly PR-RISK-001 through PR-RISK-010;
- `external_actions_performed`, exactly an empty list;
- explicit false claims for risk acceptance, pilot authorization, production
  readiness and release authorization.

Forbidden results or claims include `ready`, `approved`, `accepted`, `go`,
`pilot_authorized`, `production_ready`, `released` and semantic equivalents.

## Human gates

The model must require these gates in order and treat every one as unauthorized
until an explicit decision is recorded:

1. written specification approval;
2. implementation plan approval;
3. dedicated Execution Task and branch assignment;
4. implementation evidence acceptance;
5. named owner appointment;
6. architecture and security acceptance;
7. privacy and data acceptance;
8. operations, recovery, incident and support acceptance;
9. individual Stage 10 risk disposition;
10. exact real-pilot scope decision;
11. pilot evidence acceptance;
12. release decision.

Stage 15 cannot satisfy gates 5 through 12 by itself.

## Stop, withdrawal and error handling

Execution must stop and return evidence when any of these conditions occurs:

- an input is not synthetic or its provenance is missing;
- a company, brand, owner, endpoint or requested action exceeds scope;
- credentials, secrets, external endpoints or real identifiers are detected;
- an evidence item is missing, duplicated, reordered, malformed or not
  reproducible;
- a required risk or gate is absent;
- a test attempts an external write, network action, paging, ticket creation,
  deployment or permission change;
- local cleanup, rollback or restored-state verification fails;
- the output contains an authority-like result or claim.

Withdrawal removes only disposable local synthetic state. Governance evidence in
Git and GitHub remains append-only and reviewable. No cleanup action may delete
shared, real or external data.

## Acceptance and adversarial cases

The later implementation plan must specify tests that prove:

- one exact valid synthetic package reaches `needs_human_governance`;
- PC, 六合通, shared brands, wildcard identity and unknown scope are denied;
- real or unclassified data is denied;
- credentials, external endpoints and connectors are denied;
- missing, duplicate, reordered or unknown risks, gates and evidence are denied;
- forged local evidence, changed checksums and incomplete rollback are denied;
- real owner names and authority claims are denied;
- external action collections must be exactly empty;
- risk states cannot be changed to accepted, closed or waived;
- every Stage 10 risk remains represented;
- Stages 11–14 remain archived design evidence and are not reinterpreted as
  operating capability;
- Stage 10 remains BLOCKED / NO-GO.

## Future deliverable set

If the written specification and a later implementation plan are separately
approved, the dedicated Execution Task may propose:

- one policy document;
- one machine-readable model;
- one Stage 10–14 evidence and risk mapping;
- one acceptance matrix;
- repository-controlled synthetic fixtures;
- one pure evaluator and repository validator;
- positive and adversarial tests;
- a validation guide;
- pull-request-only, read-only CI;
- truthful Stage and Project Registry updates.

This list defines reviewable deliverables but grants no implementation authority
in the current gate.

## Lifecycle and review gates

Current lifecycle is `Planned`. Issue #40 records governance design only.

The next permitted decision is independent human review of this exact written
specification. Approval of the specification may authorize preparation of an
implementation plan only. The Stage may move to `Executing` only after the plan
is independently approved and one dedicated Execution Task and implementation
branch are assigned.

Merge, publication, Mandatory Return, `Reported`, `Reviewed`, `Archived`, risk
acceptance, real pilot, production, release and Stage 16 each remain separate
governance decisions.
