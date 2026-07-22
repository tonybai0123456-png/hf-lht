# BUW AIOS Architecture and Security Foundations v1

## Control statement

This Stage 11 / AF-01 package is a reviewable, non-production design derived from Issue #24 and main `45944a50ea33e61ad2683082441d2dac75812906`. It provisions nothing, creates no identity or secret, enables no connector, accepts no risk and grants no deployment, pilot, release or production authority. All unresolved ownership remains `unassigned / governance decision required`.

## Six system questions

1. **Business loop** — a future bounded BUW request may be admitted, validated, policy-checked, dry-run planned, human-approved where required, executed only through an explicitly authorized adapter, audited and reconciled. Stage 11 designs the controls but executes none of this loop against an external system.
2. **Core objects** — governed request, company/brand scope, workflow version, policy decision, approval record, run, idempotency key, audit event, connector command and reconciliation result.
3. **Data flow** — a synthetic request would cross ingress validation and policy checks into a stateless orchestrator; future durable state and audit stores would retain control evidence; a separately authorized connector boundary would be the only possible egress. No real data enters this Stage.
4. **Operators** — abstract roles only: Governance Approver, Security Reviewer, Platform Operator, Runtime Service Identity, Read-only Auditor and Connector Service Identity. No person is assigned.
5. **AI and human boundary** — deterministic controls validate envelopes, scope, allowlists, idempotency and policy. Humans alone authorize architecture acceptance, identities, secrets, connectors, risk acceptance, pilot and release. Silence is never approval.
6. **Proof** — deterministic validators and negative tests verify the design package, business separation, default-deny controls and absence of production authority. Future implementation and isolated non-production control tests require separate governance.

## Target topology and trust zones

```text
[Z0 Governance control] -> [Z1 Human access] -> [Z2 Ingress + policy]
                                                   |
                                                   v
                                       [Z3 Orchestration runtime]
                                          |                 |
                                          v                 v
                               [Z4 Durable control]   [Z5 Audit/observability]
                                          |
                                          v
                                  [Z6 Connector boundary] -X-> [Z7 External systems]
```

Every arrow is a proposed trust-boundary crossing, not an installed route. Z6→Z7 remains denied. The target components are an admission gateway, policy decision point, workflow registry, stateless orchestration worker, run/idempotency ledger, append-only audit sink and isolated connector adapter. Every component is proposed, unprovisioned and unassigned.

Company and brand claims are mandatory policy inputs. BUW and PC remain independent brands; 汇沣电商 is not collapsed into BUW; 六合通 is a separate company excluded from BUW AIOS. Unknown, shared or cross-boundary scope fails closed.

## Threat model

The threat model covers spoofed identities, privilege escalation, secret exposure, cross-brand/company mixing, replay/duplicate execution, connector egress, audit tampering and dependency compromise. Controls are design proposals: deny by default, workload-specific identities, explicit policy, short-lived secret retrieval, durable idempotency, append-only evidence, signed/version-pinned dependencies and isolated egress. Every threat remains not accepted; the full register is in `AIOS-Architecture-Security-Threat-Model-v1.yaml`.

## Identity and least privilege

Authentication is proposed through a future approved identity provider for humans and workload identity for services. Authorization is deny-by-default and scoped by environment, company, brand, workflow, action and resource. Governance Approver cannot operate runtime services; Platform Operator cannot accept risk; Read-only Auditor cannot alter evidence; Runtime Service Identity cannot reach external systems; Connector Service Identity is adapter-specific and cannot approve its own use. No accounts, roles, permissions or credentials are created here.

## Secrets lifecycle design

The proposed lifecycle is request → explicit approval → issue in a future approved secret manager → workload-bound retrieval → adapter-local use → rotation → revocation → audit. Secrets must not enter source control, workflow payloads, logs or human messages. Failure to retrieve, rotate or audit a secret stops execution. This is design only: there are no secret values, providers, credentials, tokens or configuration changes in this Stage.

## Persistence, idempotency, audit and connectors

- A future durable run ledger would store state transitions and immutable workflow/version references.
- A unique scoped idempotency key would be reserved before action; uncertain reservation or reconciliation stops execution.
- Audit events would be append-only, ordered, attributable to an abstract identity and include policy/approval references without secret material.
- Connector adapters would be isolated from orchestration, allowlisted per action/resource and disabled by default. No connector is implemented or enabled.
- External writes require a later, explicit governance decision and reversible operating design; Stage 11 permits none.

## Capacity and failure assumptions

No throughput, latency, availability, RTO or RPO has been measured, so none is claimed. A future bounded pilot is assumed small but its concurrency and workload remain unknown. Identity-provider, policy-store, ledger, audit-store or connector unavailability must fail closed. Duplicate, timeout, partial-result, stale-policy, cross-boundary and unknown-state conditions stop and require human review. Capacity tests, restoration drills and failure injection are downstream non-production evidence, not Stage 11 results.

## Stage 10 mapping

The foundations directly design responses to PR-RISK-001 and PR-RISK-002 and provide upstream controls relevant to observability, audit, business boundaries and release governance. Privacy/data governance, rollback, incident response and support remain downstream work. All ten Stage 10 risks stay open or blocked, not accepted and unassigned; see `AIOS-Architecture-Security-Stage10-Mapping-v1.yaml`.

## Non-production acceptance

Acceptance here means only that the design package is internally complete and reviewable. It does not mean implemented, security-approved, production-ready, deployed, piloted, released, Reviewed or Archived. The matrix requires exact governance metadata, six-question coverage, eight trust zones, least privilege, secrets design-only, durable control boundaries, ten-risk mapping, subject separation, negative tests and PR-only read-only CI. The Governance Thread must perform the human review.

## Mandatory boundaries

No infrastructure, environment, production/staging access, identity, credential, secret, permission, real data, connector, API/database/business write, outbound message, owner assignment, risk acceptance, pilot, deployment, merge or release is authorized by this package.
