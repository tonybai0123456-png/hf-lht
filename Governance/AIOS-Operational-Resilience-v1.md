# BUW AIOS Operational Resilience v1

## Control statement

Stage 13 / OR-01 defines a synthetic, prepare-only resilience policy for BUW AIOS. Its purpose is to make continuity and recovery decisions reviewable before any pilot or release decision. It does not create operational capability.

Every service, dependency, signal and evidence item in this package is repository-controlled and synthetic. Real owners remain `unassigned / governance decision required`. Passing validation does not prove production readiness, an achieved SLA/SLO, a tested backup or restore, a working monitoring system, a real incident-response capability or authority to act.

## Business loop and six system questions

### 1. Business loop

Synthetic failure signal → classify the declared impact and severity → check the known dependency, continuity and recovery policy → stop at explicit human gates → emit deterministic synthetic evidence and a review outcome.

### 2. Core objects

The controlled objects are service, dependency, synthetic failure scenario, severity, impact, continuity tier, RTO/RPO design target, recovery evidence requirement, incident record, runbook, escalation, observability contract, recovery validation and audit record.

### 3. Data origin and destination

Input is one repository YAML fixture. The validator safely parses it and evaluates it in memory. Output is a deterministic dictionary held in memory. There is no monitoring, alerting, infrastructure, database, connector or business-system connection and no persistent incident record.

### 4. Operators

Only abstract roles are modeled: Incident Authority, Continuity Authority, Recovery Authority, Communications Authority, Governance Authority, Risk Authority and Release Authority. No person or real operating team is assigned.

### 5. System and human decisions

The validator may classify declared synthetic facts and prepare a recommendation. Humans alone decide incident declaration, failover, restoration, external communication, exceptions, risk acceptance and release. Silence or missing approval fails closed.

### 6. Proof

Evidence consists of deterministic positive/negative unit tests, the repository-wide suite, Workflow Schema validation, Python compilation and pull-request-only read-only CI. These prove package consistency only.

## Company and brand boundary

The allowed scope is 汇沣电商 / BUW. PC remains an independent brand and is excluded. 六合通 remains a separate company and is excluded. Wildcards, `shared`, unknown scopes and any cross-company or cross-brand reuse are denied. A combined view requires a separate Governance Thread decision and is not represented here.

## Service and dependency inventory

`aios_runtime_design` is a conceptual service boundary, not a deployment. Its two dependencies are `synthetic_policy_registry`, a repository fixture concept, and `synthetic_audit_store`, an in-memory evidence concept. Neither dependency is connected externally or provisioned. Unknown services and dependencies deny rather than inherit a default.

Trust-zone labels are proposed design labels only. They do not assert network segmentation, storage, identity, durability or operating controls.

## Failure, severity and impact taxonomy

The policy accepts only declared synthetic dependency degradation for the current fixture. Severity values are SEV-1 through SEV-4 and express review urgency, not a real incident declaration. Impact values are `critical`, `high`, `moderate` and `low`; they describe a hypothesis supplied by the fixture.

Unknown, empty, wildcarded or invented severity/impact values deny. Classification never pages a person, changes service state or authorizes containment.

## RTO/RPO design targets

Continuity tiers CT-1, CT-2 and CT-3 provide exact RTO/RPO design target pairs for policy evaluation. The current conceptual service uses CT-2: RTO 240 minutes and RPO 60 minutes. These numbers are design targets only. They are not achieved SLA/SLO commitments, contractual terms, measured performance or recovery promises.

Any different tier/value combination is unsupported and denies. Even a supported pair cannot authorize failover, restore, release or operational acceptance.

## Backup and recovery evidence requirements

The policy requires three design evidence references:

1. a human-reviewed backup scope and retention design;
2. a human-reviewed synthetic restoration verification plan;
3. declared integrity and reconciliation checks.

Their only permitted state is `design_requirement_only`. Missing evidence denies. A state such as `tested`, `passed`, `restored` or `achieved` is rejected as an unsupported capability claim. This Stage does not create, inspect, copy, delete, restore or test a backup.

## Incident lifecycle and event record

The synthetic lifecycle is `signal_received → classified → policy_evaluated → human_decision_required → synthetic_evidence_ready`. `human_decision_required` is the operational stop. The last label means only that review evidence can be assembled after a human decision; it does not close or resolve an event.

A synthetic incident record contains scenario ID, service/dependencies, declared severity/impact, policy version, decision, reason codes, evidence references and required gates. It contains no personal content, credentials, secrets, real alert payload or real incident identifier.

## Runbook contract

A future runbook must state scope, prerequisites, stop conditions, decision gates, required evidence, recovery validation and escalation. Stage 13 runbooks are prepare-only. They contain no executable infrastructure command and cannot authorize real operation.

The runbook must stop on unknown dependency state, missing evidence, unsupported target, unresolved company/brand scope or missing human approval.

## Escalation and communication

SEV-1 and SEV-2 route conceptually to the abstract Incident Authority; SEV-3 and SEV-4 route conceptually to the abstract Governance Authority. This is a decision matrix only. Paging and external communication are disabled. Recipient selection, timing, content and transmission require separate human authority and operational implementation outside this Stage.

## Observability and alert contract design

The design signal names are synthetic availability, synthetic dependency health and synthetic data integrity. They define future evidence questions, not telemetry. There is no monitor, alert rule, pager, SLO calculation, connector, dashboard or durable log. A future Stage must separately authorize and verify any such capability.

## Continuity and failover decision matrix

| Declared condition | Validator result | Required next decision |
|---|---|---|
| Known synthetic service/dependencies, supported target and complete design evidence | `needs_human_approval` | Humans decide whether any incident declaration or later action is appropriate |
| Unknown service/dependency or cross-boundary scope | `denied` | Governance corrects the design; no action |
| Unsupported RTO/RPO or missing recovery evidence | `denied` | Continuity/Recovery authorities review; no action |
| Requested failover, restoration, page or communication | `denied` | Separate explicit human and operational authority is required |
| Claim of achieved SLA/SLO, tested restore or real capability | `denied` | Remove the unsupported claim and provide separately governed evidence |

No row performs failover or recovery.

## Human decision gates

The model requires all seven gates in every otherwise-valid scenario:

- incident declaration;
- failover;
- restoration;
- external communication;
- exception;
- risk acceptance;
- release.

The validator records that these gates are required. It cannot satisfy them. Exceptions and risk acceptance cannot be inferred from a passing test or an approved document.

## Recovery validation and audit

Recovery validation is a future evidence requirement: integrity checks, reconciliation, dependency health, target comparison and human sign-off. Stage 13 does not execute these checks against a system.

The audit contract is append-only by design but has no provisioned persistent store. It forbids personal content, credentials and secrets. Current evidence is only the fixture, deterministic output, tests, commit, Draft PR and CI result.

## Stage 10/11/12 traceability

The mapping file covers every Stage 10 risk and cites Stage 11 architecture/security plus Stage 12 privacy/data-governance evidence. OR-01 directly elaborates observability, rollback/recovery and incident-response design while reinforcing business separation and release governance.

All mapped risks remain `open` or `blocked`, unaccepted and unassigned. Stage 11 and Stage 12 are Archived dependencies; Stage 13 does not rewrite them or turn their design evidence into production capability.

## Mandatory authority boundary

Stage 13 does not authorize production/staging access, infrastructure, monitoring, alerting, paging, backup, restore, failover, chaos testing, incident operations, credentials, permissions, real data, external messages, real owners, legal conclusions, exceptions, risk acceptance, pilot, release, merge, publication, archive or Stage 14.

The maximum lifecycle state the Execution Thread may record is `Reported`. Independent human governance must review the exact remote head. Stage 14 remains `Planned` and unassigned.
