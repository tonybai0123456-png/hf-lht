# Stage 12 Privacy and Data Governance v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reviewable Stage 12 / DG-01 privacy and data-governance package with machine-readable controls, deterministic synthetic validation, regression tests, read-only CI and a Draft PR Mandatory Return.

**Architecture:** Versioned YAML contains the governance model, Stage 10 mapping and acceptance criteria. A focused Python validator loads those artifacts, validates evidence and fail-closed boundaries, and exposes pure functions used by negative tests. Markdown records the human-readable design and validation contract.

**Tech Stack:** Markdown, YAML, Python 3, PyYAML, unittest, GitHub Actions.

## Global Constraints

- Use Issue #28, branch `feat/aios-privacy-data-governance-v1`, baseline `e4ad42068b72ea107bf0c57aba11c6dd86e3cf0c` and Execution Thread `019f8762-4b8c-7452-addb-ba9510988798`.
- All example requests must set `synthetic: true`; real business, customer, employee or vendor data is prohibited.
- BUW and PC remain independent brands; 汇沣电商 and 六合通 remain separate companies.
- Unknown or conflicting company, brand, purpose, basis, field, role, retention or lineage state must deny.
- All human owners remain `unassigned / governance decision required`.
- Do not make a legal conclusion or claim compliance certification, production readiness, deployment, pilot, release or risk acceptance.
- CI is pull-request-only, uses `contents: read`, disables credential persistence and performs no external write.
- Stage 12 may stop only at Reported. Merge, publication, Archived and Stage 13 require separate authority.

---

### Task 1: Write the Stage 12 contract tests

**Files:**
- Create: `Tests/test_privacy_data_governance.py`
- Read: `docs/superpowers/specs/2026-07-22-privacy-data-governance-v1-design.md`

**Interfaces:**
- Consumes: `validate_model(model: dict) -> list[str]`, `evaluate_request(model: dict, request: dict) -> list[str]`, and `validate_repository(root: Path) -> list[str]`.
- Produces: executable positive and negative expectations for all later tasks.

- [ ] **Step 1: Create failing tests for package completeness and one allowed synthetic request**

Use `unittest`; load `Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml`; assert `validate_repository(ROOT) == []`; evaluate this exact request:

```python
VALID_REQUEST = {
    "request_id": "SYN-DG-001",
    "synthetic": True,
    "company": "汇沣电商",
    "brand": "BUW",
    "asset_id": "synthetic_customer_contact",
    "subject_type": "synthetic_customer",
    "categories": ["contact"],
    "fields": ["synthetic_email"],
    "purpose_id": "service_response",
    "basis_decision_id": "BASIS-SYN-001",
    "actor_role": "Data Steward",
    "action": "read",
    "retention_rule_id": "RET-SYN-030D",
    "lineage": {"source": "synthetic_fixture", "destination": "in_memory_validation"},
}
```

Assert `evaluate_request(MODEL, VALID_REQUEST) == []`.

- [ ] **Step 2: Add table-driven negative mutations**

For each mutation, assert its expected stable reason code:

```python
CASES = [
    ({"synthetic": False}, "real_or_unmarked_data"),
    ({"brand": "PC"}, "cross_boundary"),
    ({"purpose_id": "unknown"}, "unknown_purpose"),
    ({"basis_decision_id": ""}, "missing_basis_decision"),
    ({"fields": ["synthetic_email", "synthetic_free_text"]}, "excessive_fields"),
    ({"actor_role": "Runtime Service Identity"}, "unauthorized_access"),
    ({"retention_rule_id": "RET-FOREVER"}, "invalid_retention"),
]
```

Also test missing lineage, automatic deletion and a production/legal claim.

- [ ] **Step 3: Run the tests and confirm the red state**

Run: `python -m unittest Tests.test_privacy_data_governance -v`

Expected: FAIL because the validator and model do not exist.

- [ ] **Step 4: Commit the red tests**

Commit message: `test: define Stage 12 privacy governance contract`

### Task 2: Create the machine-readable governance model

**Files:**
- Create: `Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml`
- Test: `Tests/test_privacy_data_governance.py`

**Interfaces:**
- Produces: top-level mappings `metadata`, `business_boundaries`, `data_assets`, `purposes`, `basis_decisions`, `access_policies`, `retention_rules`, `subject_request_flow`, `lineage_policy`, `sample_requests`, and `decision`.

- [ ] **Step 1: Define exact metadata and boundaries**

Include:

```yaml
metadata:
  stage: 12
  stage_id: DG-01
  issue: 28
  governance_version: "2.2"
  main_baseline: e4ad42068b72ea107bf0c57aba11c6dd86e3cf0c
  execution_thread: 019f8762-4b8c-7452-addb-ba9510988798
  branch: feat/aios-privacy-data-governance-v1
  mode: synthetic_policy_validation
  stage_status: Executing
business_boundaries:
  allowed_company: 汇沣电商
  allowed_brand: BUW
  excluded_brand: PC
  excluded_company: 六合通
  cross_boundary_default: deny
```

- [ ] **Step 2: Define the minimum data catalog and purpose controls**

Create one asset `synthetic_customer_contact` with subject `synthetic_customer`, category `contact`, field `synthetic_email`, classification `synthetic_personal_like` and `synthetic_only: true`. Define purpose `service_response` with exact field/category/action allowlists and basis reference `BASIS-SYN-001`.

- [ ] **Step 3: Define access, retention, subject request and lineage controls**

Allow only `Data Steward` to read for `service_response`. Define `RET-SYN-030D` as 30 days from synthetic request creation with human review and no automatic real deletion. Define subject-request states `intake`, `identity_verification_required`, `scope_review`, `human_approval_required`, `synthetic_evidence_ready`, `closed`. Require lineage source `synthetic_fixture` and destination `in_memory_validation`.

- [ ] **Step 4: Set all authority flags false**

```yaml
decision:
  result: policy_review_candidate
  legal_approval_granted: false
  real_data_authorized: false
  production_ready: false
  deployment_authorized: false
  pilot_authorized: false
  release_authorized: false
  risk_acceptance_granted: false
```

- [ ] **Step 5: Commit the model**

Commit message: `feat: add Stage 12 machine-readable governance model`

### Task 3: Implement the fail-closed validator

**Files:**
- Create: `Tests/validate_aios_privacy_data_governance.py`
- Test: `Tests/test_privacy_data_governance.py`

**Interfaces:**
- Produces: `validate_model(model: dict[str, Any]) -> list[str]`, `evaluate_request(model: dict[str, Any], request: dict[str, Any]) -> list[str]`, and `validate_repository(root: Path = ROOT) -> list[str]`.
- Reason codes are stable snake_case strings.

- [ ] **Step 1: Add safe YAML and text loaders**

Implement `_yaml(path, errors)` and `_text(path, errors)`; missing, unsafe or unparsable evidence adds an error and never allows a request.

- [ ] **Step 2: Implement metadata, boundary and authority validation**

Require the exact Stage metadata, exact four entity boundaries, `cross_boundary_default: deny`, `synthetic_only: true`, all owners unassigned and every decision authority flag false.

- [ ] **Step 3: Implement request evaluation**

Return an ordered unique list of reason codes. Validate in this order: synthetic marker, boundary, asset/subject/category, purpose, basis reference, field minimization, access, consent/preference when required, retention, lineage, deletion/production/legal claims.

- [ ] **Step 4: Implement repository evidence validation**

Require the human-readable policy, model, Stage 10 mapping, acceptance matrix, validation document, tests, workflow, Stage Registry and Project Registry. Check every evidence path is repository-relative and exists. Require Stage Registry status to match model metadata.

- [ ] **Step 5: Run targeted tests to green**

Run: `python -m unittest Tests.test_privacy_data_governance -v`

Expected: all Stage 12 tests PASS.

- [ ] **Step 6: Commit the validator**

Commit message: `feat: validate Stage 12 privacy governance controls`

### Task 4: Add human-readable policy, risk mapping and acceptance evidence

**Files:**
- Create: `Governance/AIOS-Privacy-Data-Governance-v1.md`
- Create: `Governance/AIOS-Privacy-Data-Governance-Stage10-Mapping-v1.yaml`
- Create: `Governance/AIOS-Privacy-Data-Governance-Acceptance-Matrix-v1.yaml`
- Test: `Tests/test_privacy_data_governance.py`

**Interfaces:**
- The mapping covers exactly `PR-RISK-001` through `PR-RISK-010`.
- Every mapping keeps `risk_accepted: false`, `production_action_allowed: false`, owner unassigned and residual status `open` or `blocked`.

- [ ] **Step 1: Write the policy document**

Use these headings: Control statement, Six system questions, Business and data boundaries, Governance object model, Purpose and processing-basis records, Classification and minimization, Access control, Retention and disposition, Data-subject and preference flow, Lineage and audit, Stage 10/11 mapping, Synthetic acceptance, Mandatory boundaries.

- [ ] **Step 2: Create the ten-risk mapping**

Give PR-RISK-003 and PR-RISK-004 direct DG-01 design controls. Keep all ten risks open or blocked and explicitly state design evidence cannot close or accept them.

- [ ] **Step 3: Create eight acceptance criteria**

Cover six questions, boundaries, catalog/purpose/basis, minimization/access, retention/subject requests, lineage/audit, ten-risk preservation and deterministic PR-only CI. Use repository-relative evidence paths.

- [ ] **Step 4: Add tests for exact mapping and acceptance requirements**

Assert IDs, owners, authority flags and evidence paths.

- [ ] **Step 5: Run targeted tests**

Run: `python -m unittest Tests.test_privacy_data_governance -v`

Expected: PASS.

- [ ] **Step 6: Commit policy evidence**

Commit message: `docs: add Stage 12 privacy governance evidence`

### Task 5: Add validation guide and pull-request-only CI

**Files:**
- Create: `Tests/AIOS-Privacy-Data-Governance-Validation.md`
- Create: `.github/workflows/validate-aios-privacy-data-governance.yml`
- Modify: `Tests/test_privacy_data_governance.py`

**Interfaces:**
- Workflow invokes `python Tests/validate_aios_privacy_data_governance.py`, targeted unittest, full unittest discovery, Workflow Schema validation and Python compilation.

- [ ] **Step 1: Write positive and negative validation cases**

Document the exact synthetic allow case and every required denial mutation. State that a pass proves policy-package consistency only.

- [ ] **Step 2: Add read-only CI**

Use only `pull_request:`; set `permissions: contents: read`; use checkout with `persist-credentials: false`; install PyYAML; run deterministic commands. Do not add `push`, `workflow_dispatch`, write permissions or artifact publication.

- [ ] **Step 3: Test workflow restrictions**

Assert required tokens and reject `push:`, `workflow_dispatch:`, `contents: write`, `pull-requests: write` and `git push`.

- [ ] **Step 4: Run targeted and full tests**

Run:
- `python Tests/validate_aios_privacy_data_governance.py`
- `python -m unittest Tests.test_privacy_data_governance -v`
- `python -m unittest discover -s Tests -p 'test_*.py' -v`

Expected: validator and all tests PASS.

- [ ] **Step 5: Commit CI and validation**

Commit message: `ci: validate Stage 12 privacy governance package`

### Task 6: Register Stage 12 execution and produce the Mandatory Return

**Files:**
- Modify: `Governance/AIOS-Stage-Registry.md`
- Modify: `Governance/AIOS-Project-Registry.md`
- Modify: `Tests/test_project_governance.py`
- Modify: `Tests/AIOS-Project-Governance-Baseline-Validation.md`
- Modify: `Governance/AIOS-Privacy-Data-Governance-Model-v1.yaml`
- Modify: Issue #28
- Create: Draft PR

**Interfaces:**
- Stage 12 row moves Planned → Executing when registered, then Executing → Reported only after evidence passes.
- Stages 13–14 remain Planned and unassigned.

- [ ] **Step 1: Register the exact assignment**

Update Stage 12 with Issue #28, Execution Thread, branch and Executing status. Update Project Registry Active Stage. Append dated governance evidence. Update governance tests.

- [ ] **Step 2: Run pre-return verification**

Run:
- Stage 12 validator;
- targeted Stage 12 tests;
- full repository test discovery;
- Workflow Schema validation through `Tests/validate_aios_workflow_schema.py`;
- Python compilation;
- diff review for real data, production authority, owner assignment and protected-scope changes.

Expected: all checks PASS and only authorized files changed.

- [ ] **Step 3: Move Stage 12 to Reported**

After green evidence, update model, Stage Registry, Project Registry and Issue #28 from Executing to Reported. Do not use Reviewed or Archived.

- [ ] **Step 4: Open a Draft PR**

Title: `Stage 12 / DG-01: Privacy and Data Governance v1`. Include scope, checks, exact head SHA and all authority boundaries.

- [ ] **Step 5: Wait for required CI and correct ordinary defects**

Required final workflows: Stage 12 Privacy/Data Governance, Project Governance, Production Readiness regression and Runtime regression. All must succeed on the final head.

- [ ] **Step 6: Post the Mandatory Return**

Use headings 本次完成, 证据链接, 阻塞项 and 下一步. State Stage 12 is Reported only. Human review, merge/publication, legal approval, real-data use, archive and Stage 13 remain separate decisions.

- [ ] **Step 7: Commit final governance evidence**

Commit message: `governance: report Stage 12 privacy data governance result`
