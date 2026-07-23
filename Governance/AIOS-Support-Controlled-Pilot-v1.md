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
