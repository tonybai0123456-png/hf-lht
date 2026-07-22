# Stage 13 Operational Resilience v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reviewable Stage 13 / OR-01 operational-resilience package with deterministic fail-closed synthetic validation, read-only CI and a Draft PR Mandatory Return.

**Architecture:** One versioned YAML model defines services, dependencies, classification, continuity targets, evidence requirements and human gates. One repository fixture is evaluated by a pure Python validator; separate mapping and acceptance files support governance review without creating runtime capability.

**Tech Stack:** Markdown, YAML, Python 3, PyYAML, unittest and GitHub Actions.

## Global Constraints

- Use Issue #32, branch `feat/aios-operational-resilience-v1`, baseline `c5dde2171c65e75b595c411854cba0016f3623f7` and Execution Thread `019f8a35-6d4e-7c60-b35a-79de8626d4e3`.
- Use repository-controlled synthetic fixtures and deterministic in-memory validation only.
- BUW and PC remain independent brands; 汇沣电商 and 六合通 remain separate companies.
- All real owners remain `unassigned / governance decision required`.
- Unknown service/dependency, invalid severity/impact, unsafe action, missing gate, unsupported RTO/RPO, missing recovery evidence, cross-boundary use and achievement claims must deny.
- RTO/RPO are design targets only; no SLA/SLO, backup/restore test or real incident capability may be claimed.
- CI is pull-request-only, read-only and performs no external operation.
- Stage 13 may stop only at Reported. Stage 14 remains Planned and unassigned.

---

### Task 1: Define the RED contract

**Files:**
- Create: `Tests/test_operational_resilience.py`

**Interfaces:**
- Consumes: `validate_model`, `evaluate_scenario` and `validate_repository` from the future validator.
- Produces: positive fixture outcome and stable denial-code expectations.

- [ ] Write a test that requires the complete repository package and a valid fixture result of `needs_human_approval` with no external actions.
- [ ] Add table-driven mutations for every required fail-closed condition and authority claim.
- [ ] Add mapping, acceptance, registry and PR-only CI restrictions.
- [ ] Run `python -m unittest Tests.test_operational_resilience -v` and confirm it fails because the validator is absent.

### Task 2: Build the machine-readable contract and pure validator

**Files:**
- Create: `Governance/AIOS-Operational-Resilience-Model-v1.yaml`
- Create: `Tests/Fixtures/operational-resilience/synthetic-service-degradation.yaml`
- Create: `Tests/validate_aios_operational_resilience.py`
- Test: `Tests/test_operational_resilience.py`

**Interfaces:**
- `validate_model(model: dict) -> list[str]` checks metadata, links, owners, design-only states and authority flags.
- `evaluate_scenario(model: dict, scenario: dict) -> dict` returns `denied` or `needs_human_approval` with ordered stable reason codes.
- `validate_repository(root: Path = ROOT) -> list[str]` checks every required artifact, mapping, acceptance item, workflow and registry state.

- [ ] Define exact metadata, business boundaries and the six system questions.
- [ ] Define one conceptual service, two synthetic dependencies, four severity levels, three continuity tiers, evidence requirements and seven mandatory human gates.
- [ ] Create one valid synthetic fixture with only prepare-only action and design-only evidence.
- [ ] Implement safe loaders and fail-closed model validation.
- [ ] Implement ordered scenario evaluation for all required denial cases.
- [ ] Run the targeted tests until GREEN, changing implementation rather than weakening tests.

### Task 3: Add policy, mappings and acceptance evidence

**Files:**
- Create: `Governance/AIOS-Operational-Resilience-v1.md`
- Create: `Governance/AIOS-Operational-Resilience-Stage10-12-Mapping-v1.yaml`
- Create: `Governance/AIOS-Operational-Resilience-Acceptance-Matrix-v1.yaml`
- Create: `Tests/AIOS-Operational-Resilience-Validation.md`

**Interfaces:**
- The mapping covers exactly `PR-RISK-001` through `PR-RISK-010` and cites Stage 11/12 evidence.
- Each acceptance item has a stable ID, objective criterion, repository-relative evidence and `design_only: true`.

- [ ] Document the business loop, core objects, data flow, roles, human/system boundary and proof.
- [ ] Document service/dependency inventory, severity/impact, continuity, recovery evidence, incident lifecycle, runbooks, escalation, observability and audit.
- [ ] Map all ten Stage 10 risks while preserving blocked/open, unassigned ownership and no acceptance.
- [ ] Define acceptance criteria for boundaries, fail-closed behavior, human gates, no-claim controls, mapping and deterministic CI.
- [ ] Document positive and negative commands and the limited meaning of PASS.
- [ ] Run targeted tests to GREEN.

### Task 4: Add lifecycle evidence and PR-only CI

**Files:**
- Create: `.github/workflows/validate-aios-operational-resilience.yml`
- Modify: `Governance/AIOS-Stage-Registry.md`
- Modify: `Governance/AIOS-Project-Registry.md`
- Modify: `Tests/test_project_governance.py`

**Interfaces:**
- Workflow runs validator, targeted tests, repository regression, Workflow Schema validation and compilation.
- Stage 13 row records Issue #32, the exact Execution Thread, branch and `Reported`; Stage 14 stays Planned/unassigned.

- [ ] Create a `pull_request`-only workflow with `contents: read` and `persist-credentials: false`.
- [ ] Move Stage 13 from Planned through its authorized assignment to Reported and append lifecycle evidence.
- [ ] Update Project Registry active-stage text and history without changing project boundaries.
- [ ] Update governance tests for Stage 13 Reported and Stage 14 Planned.
- [ ] Run targeted and full tests to GREEN.

### Task 5: Verify, publish and return

**Files:** all authorized Stage 13 files above plus Issue #32 and an independent Draft PR.

- [ ] Run `python Tests/validate_aios_operational_resilience.py`.
- [ ] Run `python -m unittest Tests.test_operational_resilience -v`.
- [ ] Run `python -m unittest discover -s Tests -p 'test_*.py' -v`.
- [ ] Run `python Tests/validate_aios_workflow_schema.py` and Python compilation with a task-local cache.
- [ ] Inspect the complete diff for real data, real owners, unsafe action, false capability claims, Stage 14 changes and workflow writes.
- [ ] Commit intended files, push the exact authorized branch and open a Draft PR to `main`.
- [ ] Wait for final-head PR CI, require every run to succeed and verify remote filenames/content against the tested local head.
- [ ] Post Issue #32 Mandatory Return with 本次完成、证据链接、阻塞项、下一步, exact remote head, file/test counts, CI and boundary statement.

## Plan self-review

Every Issue #32 deliverable and denial case maps to a task. Interfaces use the same validator names throughout. No placeholder, production operation, named owner, merge, archive or Stage 14 action is present.
