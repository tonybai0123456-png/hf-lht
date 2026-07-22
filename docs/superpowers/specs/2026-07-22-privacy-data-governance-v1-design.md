# BUW AIOS Privacy and Data Governance v1 — Design

## Document control

| Field | Value |
|---|---|
| Stage | 12 / DG-01 |
| Issue | #28 |
| Governance version | 2.2 |
| Main baseline | `e4ad42068b72ea107bf0c57aba11c6dd86e3cf0c` |
| Execution Thread | `019f8762-4b8c-7452-addb-ba9510988798` |
| Branch | `feat/aios-privacy-data-governance-v1` |
| Mode | Policy + machine-readable controls + synthetic/read-only verification |
| Decision | Confirmed 方案 B |

## Purpose

Stage 12 defines a reviewable privacy and data-governance control package for a future bounded BUW AIOS workload. It converts the Stage 11 architecture boundary into explicit data-policy objects and deterministic denial rules. It does not connect a source, process real data, execute a data-subject request, make a legal conclusion, or authorize production.

## Six system questions

1. **Business loop** — a synthetic data-processing request enters with company, brand, data category, purpose, processing-basis reference, requested fields, actor role and retention rule. Deterministic controls validate scope, minimize fields, check access and retention, and emit a synthetic decision and audit evidence. Missing or conflicting evidence is denied and returned for human governance review.
2. **Core objects** — data asset, data subject type, data category, classification, processing purpose, processing-basis decision record, consent/preference record, actor role, access policy, retention rule, deletion request, lineage record, policy decision and audit event.
3. **Data flow** — repository-owned synthetic fixtures flow into a read-only validator. The validator loads versioned YAML policy, produces in-memory allow/deny results and writes nothing externally. Future real sources and destinations remain unconnected.
4. **Operators** — abstract roles only: Governance Approver, Privacy Reviewer, Legal Reviewer, Data Steward, Security Reviewer, Read-only Auditor and Runtime Service Identity. Every real owner remains `unassigned / governance decision required`.
5. **System and human boundary** — deterministic code validates declared facts and fails closed. Humans alone approve processing purposes and bases, retention periods, exceptions, real-data access, data-subject fulfillment, legal interpretation, risk acceptance and release.
6. **Proof** — positive fixtures prove a narrowly complete request can be evaluated; negative fixtures prove cross-boundary, unknown-purpose, missing-basis, excessive-field, unauthorized-role, indefinite-retention, automatic-deletion and real-data claims are rejected. Full repository regression and PR-only read-only CI provide repeatable evidence.

## Business and data boundaries

- BUW and PC remain independent United States brands.
- 汇沣电商 is the company boundary containing separate BUW and PC scopes; it is not identical to BUW.
- 六合通 is a separate international freight-forwarding company and is excluded from BUW AIOS.
- Every request must declare one company and one brand. Unknown, shared, wildcard or cross-company/brand scope is denied.
- All fixtures are synthetic and visibly marked `synthetic: true`.
- No customer, employee, vendor, payment, authentication or free-text content from real operations is allowed in Stage 12.

## Policy architecture

The package has six independently testable layers:

1. **Data catalog** — declares allowed synthetic asset types, subject types, fields, categories and classification.
2. **Purpose and basis register** — declares bounded purposes and references a human-approved processing-basis decision state. The model records whether a basis decision exists; it does not decide law.
3. **Minimization matrix** — maps each purpose to an exact allowed field set. Supersets fail closed.
4. **Access matrix** — maps abstract roles to allowed purpose/category actions. Silence and wildcard access are denied.
5. **Retention and disposition register** — requires bounded durations, review gates and a human-approved disposition path. Indefinite retention and autonomous real deletion are prohibited.
6. **Lineage and audit contract** — requires source class, destination class, policy version, decision, reasons and evidence references without storing personal content.

Each layer uses a focused YAML file or section with stable identifiers. The validator composes them without mutating the repository or any external system.

## Request and decision contract

A synthetic evaluation request must contain:

- request ID and `synthetic: true`;
- company and brand;
- asset ID and subject type;
- data categories and requested fields;
- purpose ID and processing-basis decision reference;
- actor role and requested action;
- retention rule ID;
- lineage source and proposed destination;
- consent/preference reference when the declared purpose requires it.

The decision contains `allow` or `deny`, deterministic reason codes, policy version and evidence paths. It contains no personal content and grants no operational authority.

## Fail-closed rules

The validator denies when:

- company or brand is missing, unknown, shared, wildcarded or cross-boundary;
- `synthetic` is not exactly true;
- a data asset, subject type, category, purpose, basis decision, role, action or retention rule is unknown;
- requested fields exceed the purpose-specific allowlist;
- a required consent/preference reference is absent;
- access is not explicitly granted for the exact role, purpose, category and action;
- retention is unbounded, lacks a review gate or claims automatic real deletion;
- lineage is missing, self-contradictory or crosses an excluded boundary;
- policy versions or evidence references are missing;
- any artifact claims legal approval, compliance certification, production readiness or real-data authority.

Unknown states never fall back to allow.

## Data-subject and consent design

Stage 12 models intake, identity-verification requirement, scope discovery, human approval, response evidence and closure for access, correction, deletion and opt-out requests. All instances are synthetic state-machine examples. The validator forbids automatic fulfillment and requires a human gate before any future export, correction or deletion.

Consent and preference records are modeled only as referenced governance objects. The package does not collect consent, contact a person or decide whether consent is legally required.

## Retention and deletion design

Every governed asset has a bounded retention rule with:

- duration and start event;
- review frequency;
- hold/exception state;
- disposition proposal;
- required human approver;
- evidence required before closure.

The design rejects `forever`, null or zero-control retention. It also rejects any claim that Stage 12 deleted real data. Synthetic deletion-request transitions may be evaluated in memory only.

## Lineage, provenance and audit

A lineage record identifies synthetic source class, transformation purpose, destination class, policy version and evidence path. Cross-company or cross-brand movement is denied. Audit events record request ID, actor role, policy version, decision, reason codes and evidence references, but never raw personal content, credentials or secrets.

## Stage 10 and Stage 11 relationship

Stage 12 provides design responses to privacy/data-governance and source-contract gaps, especially Stage 10 risks PR-RISK-003 and PR-RISK-004. It may refine mitigation evidence but cannot close or accept any Stage 10 risk. Stage 11 architecture and security controls remain unchanged and Archived; Stage 12 adds policy objects without provisioning its proposed stores, identities or connectors.

## Deliverables

- `Governance/AIOS-Privacy-Data-Governance-v1.md`
- `Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml`
- `Governance/AIOS-Privacy-Data-Governance-Stage10-Mapping-v1.yaml`
- `Governance/AIOS-Privacy-Data-Governance-Acceptance-Matrix-v1.yaml`
- `Tests/validate_aios_privacy_data_governance.py`
- `Tests/test_privacy_data_governance.py`
- `Tests/AIOS-Privacy-Data-Governance-Validation.md`
- `.github/workflows/validate-aios-privacy-data-governance.yml`
- Stage and Project Registry updates
- implementation plan, Draft PR and Mandatory Return

## Verification strategy

Positive tests cover one strictly bounded synthetic BUW request with an exact field allowlist, explicit purpose/basis reference, authorized abstract role, bounded retention and valid lineage.

Negative tests independently mutate company, brand, synthetic flag, purpose, basis, fields, role, consent reference, retention, disposition authority, lineage and production/legal claims. The validator also checks evidence paths, stable IDs, business separation, unassigned owners and PR-only read-only CI.

The full repository suite, Workflow Schema validation and Python compilation must pass before the Mandatory Return.

## Lifecycle and stop point

The Stage moves Planned → Executing through Issue #28 and this confirmed design. The Execution Thread may implement continuously and submit a Draft PR. After all required checks pass it may record Reported through the Mandatory Return. It cannot self-declare Reviewed, merge, publication or Archived.

## Non-goals and authority boundary

Stage 12 does not authorize or perform:

- real-data access, source connection, migration, export, correction, retention or deletion;
- legal advice, statutory interpretation, compliance certification or regulator communication;
- infrastructure, deployment, production/staging access, credentials or permissions;
- connectors, API/database/business writes or outbound messages;
- real owner assignment, exception approval, risk acceptance, pilot or release;
- merge, publication, archive or Stage 13 execution.
