# BUW AIOS Privacy and Data Governance v1

## Control statement

This Stage 12 / DG-01 package implements confirmed 方案 B as policy, machine-readable controls and synthetic/read-only verification. It is based on Issue #28 and main `e4ad42068b72ea107bf0c57aba11c6dd86e3cf0c`. It connects no source, processes no real data, fulfills no data-subject request, makes no legal conclusion and grants no production, pilot, release or risk-acceptance authority. Every unresolved owner remains `unassigned / governance decision required`.

## Six system questions

1. **Business loop** — a synthetic request declares company, brand, asset, subject, categories, fields, purpose, basis decision, role, action, retention and lineage. Deterministic controls either allow the exact bounded request in memory or deny it with stable reasons for human review.
2. **Core objects** — data asset, subject type, category, classification, purpose, basis decision, consent or preference reference, access policy, retention rule, subject request, lineage record, policy decision and audit event.
3. **Data flow** — repository-owned synthetic fixtures flow into a read-only Python validator, which loads versioned YAML and returns in-memory results. No source, destination, connector or external system is reached.
4. **Operators** — abstract Governance Approver, Privacy Reviewer, Legal Reviewer, Data Steward, Security Reviewer, Read-only Auditor and Runtime Service Identity. No real person is assigned.
5. **System and human boundary** — deterministic checks validate declared facts and fail closed. Humans alone approve purpose and basis records, exceptions, real-data access, retention, subject-request fulfillment, legal interpretation, risk and release.
6. **Proof** — one exact positive fixture and independent negative mutations prove package consistency, minimization, separation and denial behavior. They do not prove legal compliance or production operation.

## Business and data boundaries

BUW and PC remain independent United States brands. 汇沣电商 is the company boundary containing separate BUW and PC scopes and is not identical to BUW. 六合通 is a separate international freight-forwarding company excluded from BUW AIOS. Every request must declare exactly 汇沣电商 and BUW; unknown, shared, wildcard or cross-boundary values fail closed.

Every Stage 12 sample is synthetic and marked `synthetic: true`. Real customer, employee, vendor, payment, credential, authentication or free-text operational data is prohibited.

## Governance object model

The machine-readable model separates data assets, purposes, basis-decision references, access policies, retention rules, subject-request states, lineage rules and decision authority. Stable identifiers allow deterministic validation while keeping legal and operational decisions with humans.

## Purpose and processing-basis records

A request must reference a registered purpose and a compatible human-reviewed basis-decision record. Every basis record must explicitly retain `legal_conclusion: false` and `real_data_authorized: false`. The record proves only that a synthetic design decision was documented; it is not a legal conclusion. Missing, unknown, unsafe or purpose-incompatible references deny the request. Silence never becomes permission.

## Classification and minimization

Each synthetic asset declares a subject type, categories, fields, classification and `synthetic_only: true`. Every purpose has an exact field and category allowlist. A request for any additional field, including synthetic free text, is denied as excessive. Stage 12 does not infer new categories or collect content.

## Access control

Access is deny by default and must match the exact abstract role, purpose, category and action. The bounded positive fixture permits a Data Steward to read one synthetic email field for `service_response`. Runtime identities, wildcard roles, unlisted actions and cross-purpose access are rejected. The policy assigns no real account or permission.

## Retention and disposition

The only sample rule retains a synthetic fixture for 30 days from synthetic request creation, requires human review and forbids automatic real deletion. Unknown, zero, null or indefinite retention is rejected. Holds, exceptions and any future disposition require named human governance decisions outside this Stage.

## Data-subject and preference flow

Access, correction, deletion and opt-out are represented only as a synthetic state design: intake → identity verification required → scope review → human approval required → synthetic evidence ready → closed. Automatic fulfillment and real action are false. A purpose that requires consent or preference evidence must reference a registered synthetic record whose purpose and human-review state are compatible; arbitrary or unknown identifiers are denied. The validator neither collects consent nor decides when law requires it.

## Lineage and audit

The allowed synthetic path is `synthetic_fixture` → `in_memory_validation`. Missing or different lineage is denied. Future lineage must retain company, brand, purpose, policy version and evidence references without raw personal content. Audit evidence records request ID, abstract actor, decision and reason codes only.

## Stage 10/11 mapping

DG-01 directly supplies design evidence for PR-RISK-003 and PR-RISK-004 and adds privacy/data controls relevant to all ten Stage 10 risks. It cannot close or accept any risk. Stage 11 remains Archived; its unprovisioned architecture, identity, secret, audit and connector controls remain unchanged.

## Synthetic acceptance

Acceptance means the policy package is complete and deterministically testable. The positive case must match the exact BUW synthetic allowlist. Negative tests must reject real or unmarked data, PC or other boundary values, unknown purpose, missing basis, excessive fields, unauthorized roles, invalid retention, missing lineage, automatic real deletion and production or legal claims. Pull-request-only read-only CI repeats these checks.

## Mandatory boundaries

No real data, source connection, export, correction, retention action, deletion, subject-request fulfillment, legal advice, compliance certification, infrastructure, deployment, production/staging access, credential, permission, connector, external write, outbound message, owner assignment, exception, risk acceptance, pilot, release, merge, publication, archive or Stage 13 execution is authorized.
