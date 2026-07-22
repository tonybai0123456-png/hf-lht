# Stage 13 Operational Resilience v1 Design

## Purpose and authority

Stage 13 / OR-01 converts synthetic failure signals into reviewable continuity and recovery decisions without operating any real system. It is authorized by Issue #32 for Execution Thread `019f8a35-6d4e-7c60-b35a-79de8626d4e3` on branch `feat/aios-operational-resilience-v1`, based on `main` commit `c5dde2171c65e75b595c411854cba0016f3623f7`.

The package is design and validation evidence only. It cannot declare a real incident, trigger failover or restoration, contact anyone, accept risk, assign an owner, publish a release, or claim that an RTO, RPO, SLA, SLO, backup, restore, runbook, alert or incident capability exists in production.

## Business loop and six system questions

1. **Business loop:** synthetic failure signal → classify declared impact and severity → check known dependencies, continuity target and recovery evidence requirements → stop at an explicit human gate → emit deterministic synthetic evidence.
2. **Core objects:** service, dependency, synthetic scenario, impact, severity, continuity tier, RTO/RPO design target, recovery evidence requirement, incident record, runbook, escalation, observability contract, recovery validation and audit record.
3. **Data flow:** repository-controlled YAML fixture → safe in-memory parse → pure deterministic evaluation → in-memory decision; no monitoring, infrastructure, database, connector or business-system access.
4. **Operators:** abstract roles only. Every real operational owner remains `unassigned / governance decision required`.
5. **System and human boundary:** the validator checks only declared synthetic facts. Humans alone may declare an incident, approve failover, approve restoration, authorize external communication, grant an exception, accept risk or approve pilot/release.
6. **Proof:** deterministic positive and negative tests, repository regression, Workflow Schema validation, Python compilation and pull-request-only read-only CI.

## Considered approaches

### Selected: one versioned model and one pure validator

A single YAML model holds the resilience contract and stable identifiers. One external synthetic fixture represents a tabletop request. A pure Python validator checks repository completeness and evaluates the fixture without side effects. This is the smallest design that keeps cross-object consistency directly testable.

### Rejected: executable incident state machine

An executable state machine would make the design look operational and increase the chance that prepare-only recommendations are mistaken for real incident authority. Stage 13 does not need runtime orchestration.

### Rejected: separate model file per control domain

Splitting service inventory, continuity targets, incident controls and evidence requirements into many YAML files would create unnecessary reference complexity for a single synthetic service scenario. The Stage 10/11/12 mapping and acceptance matrix remain separate because they have distinct review purposes.

## Model architecture

The machine-readable model contains:

- exact Stage metadata, BUW-only company/brand boundaries and all owner/authority denials;
- known services and dependencies with trust zones and synthetic-only declarations;
- severity and impact taxonomies;
- bounded continuity tiers whose RTO/RPO values are explicitly labeled design targets;
- recovery evidence requirements whose allowed state is `design_requirement_only`;
- incident lifecycle, runbook, escalation, observability and audit contracts;
- allowed prepare-only actions and prohibited real actions;
- explicit human gates for incident declaration, failover, restoration, communication, exception, risk acceptance and release;
- a decision block that grants no operational authority.

The Stage 10/11/12 mapping covers all ten Stage 10 risk IDs. It cites Stage 11 and Stage 12 controls where applicable, keeps owners unassigned, retains `open` or `blocked`, and sets risk acceptance and production action to false.

## Evaluation contract

`evaluate_scenario(model, scenario)` returns a deterministic dictionary with `result`, ordered unique `reason_codes`, `required_human_gates`, `evidence_refs`, `external_actions_performed` and one complete in-memory `incident_record`. The record contains exactly the machine-readable contract fields and mirrors the final decision, reasons, gates and evidence references; it creates no real incident or persistent audit entry.

A valid synthetic scenario returns `needs_human_approval`, never `recovered` or `executed`. Invalid scenarios return `denied`. Stable denial reasons include:

- `real_or_unmarked_signal`;
- `missing_scenario_id`;
- `cross_boundary`;
- `unknown_service`, `unknown_dependency`, `duplicate_dependency` and `dependency_contract_mismatch`;
- `invalid_severity` and `invalid_impact`;
- `unsupported_rto_rpo`;
- `missing_recovery_evidence`, `duplicate_recovery_evidence`, `recovery_evidence_contract_mismatch` and `invalid_recovery_evidence_state`;
- `missing_human_gate`, `duplicate_human_gate` and `human_gate_contract_mismatch`;
- `unsafe_continuity_action`;
- `invalid_claim_contract` and `achievement_claim`.

Unknown, missing, duplicated, reordered, wildcarded or internally inconsistent values always deny. Claim keys must exactly match the authorized set and every claim value must be the boolean `false`. Model validation exact-matches lifecycle, runbook, escalation, observability, audit and allowed/prohibited action contracts, including every unassigned owner and disabled operational capability.

## Synthetic fixture

The positive fixture describes one synthetic degradation of the conceptual `aios_runtime_design` service for 汇沣电商 / BUW. It references only declared synthetic dependencies, a supported design target and repository evidence requirements. Its requested action is `prepare_recovery_recommendation`, and it names every required human gate while asserting that no external action was performed.

Negative tests deep-copy and mutate this fixture in memory. No test generates alerts, pages, backups, restores, failovers, incidents, messages, credentials or infrastructure changes.

## Human-readable policy and evidence

The policy explains business meaning, service/dependency boundaries, classification, continuity targets, evidence requirements, incident lifecycle, runbook and escalation contracts, observability design, recovery verification and mandatory human decisions. The acceptance matrix provides binary review criteria with repository-relative evidence paths. The validation guide states exactly what a pass does and does not prove.

## CI and lifecycle

The Stage 13 workflow runs only on `pull_request`, has `contents: read`, checks out without persisted credentials and performs only parsing, tests, schema validation and compilation. It has no push trigger, write permission, artifact publication or external operation.

After local and final-head CI evidence passes, the branch records Stage 13 as `Reported` and publishes a Mandatory Return on Issue #32. `Reported` is not `Reviewed` or `Archived`. Stage 14 remains `Planned` and unassigned.

## Deliverables

- `Governance/AIOS-Operational-Resilience-v1.md`
- `Governance/AIOS-Operational-Resilience-Model-v1.yaml`
- `Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml`
- `Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml`
- `Tests/Fixtures/operational-resilience/synthetic-service-degradation.yaml`
- `Tests/validate_aios_operational_resilience.py`
- `Tests/test_operational_resilience.py`
- `Tests/AIOS-Operational-Resilience-Validation.md`
- `.github/workflows/validate-aios-operational-resilience.yml`
- Stage Registry and Project Registry lifecycle updates
- this specification and the implementation plan

## Self-review

The design contains no placeholder, real owner, operational connector, production claim, risk acceptance, merge authority, Stage 14 activation or ambiguous positive outcome. The package boundary matches Issue #32 and all required fail-closed cases have stable reason codes.
