# Runtime Orchestrator v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and report a minimal deterministic Runtime Orchestrator v1 that executes exactly five published workflows through the existing synthetic-only Controlled Harness and never performs external writes.

**Architecture:** `RuntimeOrchestrator` is a strict policy and routing layer above `ControlledOrchestrator`. It validates Runtime Contract 1.0 requests, maps a fixed workflow ID allowlist to repository-owned YAML, adapts the request into the Harness v0 payload, fixes the audit clock from `requested_at`, and stores request fingerprints plus deep-copied results in memory for idempotency.

**Tech Stack:** Python 3.12-compatible standard library, PyYAML 6.x through the existing harness loader, `unittest`, YAML fixtures, GitHub Actions.

## Global Constraints

- Runtime version is exactly `1.0`.
- Execute only the five workflow IDs published under `Schemas/Workflows/` on the Stage 8 branch base.
- Accept only synthetic data with `dry_run: true` and `allow_external_writes: false`.
- Fail closed for missing, invalid, ambiguous or unauthorized scope and approval declarations.
- Accept no user-selected filesystem paths, modules, commands, callables or executable code.
- Keep BUW and PC separate; reject shared/unknown brand scope in v1.
- Accept only `company: 汇沣电商`; reject 六合通 and every cross-company request.
- Preserve the existing Runtime Contract output and Controlled Harness behavior.
- `prepare_only` stops at `needs_approval`; `prohibited` never executes.
- Same `run_id` plus identical canonical request returns the stored result without rerun; changed content rejects as a collision.
- Use synthetic fixtures only and perform no external API, database, message, deployment, permission or business write.
- Work only in Stage 8 / RO-01 and Issue #16; do not start Stage 9 or Issue #13.
- Deliver through an independent Draft PR targeting `main`; never mark ready and never merge.
- Stop at Registry state `Reported` pending human Governance Thread review.

---

### Task 1: Register Stage 8 execution

**Files:**
- Modify: `Governance/AIOS-Stage-Registry.md`

**Interfaces:**
- Consumes: Issue #16 assignment and Execution Thread `019f88ca-9d63-7e13-b1e0-b4db3b6a65df`.
- Produces: the Stage Registry lifecycle source of truth at `Executing` before implementation begins.

- [ ] **Step 1: Replace the Stage 8 row**

Use this exact lifecycle evidence in the row:

```markdown
| 8 | RO-01 | Runtime Orchestrator（运行时编排器） | BUW AIOS Official Governance Thread | [Issue #16](https://github.com/tonybai0123456-png/hf-lht/issues/16) / Execution Thread `019f88ca-9d63-7e13-b1e0-b4db3b6a65df` / branch `feat/aios-runtime-orchestrator-v1` | Executing | Execution return pending | 方案 A authorized: minimal Runtime Orchestrator above the existing Controlled Harness; synthetic-only, dry-run and no-write boundary; stop at Reported. |
```

- [ ] **Step 2: Add the change-log record**

```markdown
| 2026-07-22 | 2.0 | Assigned Stage 8 / RO-01 through Issue #16 to the single dedicated Execution Thread `019f88ca-9d63-7e13-b1e0-b4db3b6a65df`; authorized branch `feat/aios-runtime-orchestrator-v1`; moved Stage 8 from Planned to Executing under approved 方案 A. | BUW AIOS Official Governance Thread authorization / RO-01 Execution Thread implementation |
```

- [ ] **Step 3: Verify the lifecycle edit**

Run:

```bash
rg -n "RO-01|Issue #16|019f88ca-9d63-7e13-b1e0-b4db3b6a65df|Executing" Governance/AIOS-Stage-Registry.md
git diff --check
```

Expected: the Stage 8 row names Issue #16, the one Execution Thread, authorized branch and `Executing`; no whitespace errors.

- [ ] **Step 4: Commit**

```bash
git add Governance/AIOS-Stage-Registry.md
git commit -m "governance: start Stage 8 Runtime Orchestrator"
```

### Task 2: Add synthetic Runtime requests and RED contract tests

**Files:**
- Create: `Tests/Fixtures/runtime-orchestrator/agent-reports-to-ceo.yaml`
- Create: `Tests/Fixtures/runtime-orchestrator/customer-complaint.yaml`
- Create: `Tests/Fixtures/runtime-orchestrator/marketing-crm-campaign.yaml`
- Create: `Tests/Fixtures/runtime-orchestrator/shopify-developer.yaml`
- Create: `Tests/Fixtures/runtime-orchestrator/store-anomaly.yaml`
- Create: `Tests/test_runtime_orchestrator.py`
- Test: `Tests/test_runtime_orchestrator.py`

**Interfaces:**
- Consumes: Runtime Contract 1.0 fields and the five published workflow required-input lists.
- Produces: one complete synthetic Runtime request per workflow and executable expectations for `RuntimeOrchestrator.execute(request)`.

- [ ] **Step 1: Write the five fixtures**

Each fixture must contain exactly the Runtime envelope fields below, with the workflow-specific values shown in the matrix:

```yaml
runtime_version: "1.0"
run_id: "SYN-RO-UNIQUE-ID"
agent: "CANONICAL_AGENT"
mode: validate
requested_by: synthetic-test-suite
requested_at: "2026-07-22T08:00:00Z"
business_context:
  company: 汇沣电商
  brand: BUW
  scope_level: department
  department: "DOMAIN"
  decision_owner: Tony
  operating_owner: "CANONICAL_AGENT"
task:
  workflow_id: "PUBLISHED_WORKFLOW_ID"
  objective: "Validate the published workflow with synthetic evidence"
  requested_output: "Runtime Contract 1.0 result"
  acceptance_criteria: ["stop before the first prepare_only step"]
  deadline_or_review_date: "2026-07-23"
  requested_next_action: validate
  reporting_period: "2026-07-22"
  workflow_inputs: {}
evidence:
  - source_type: synthetic
    source_name: "Synthetic workflow fixture"
    source_link_or_id: "synthetic://runtime/PUBLISHED_WORKFLOW_ID/001"
    data_cutoff: "2026-07-22"
    owner: "CANONICAL_AGENT"
    confidence: high
    limitations: "Synthetic fixture only"
constraints:
  prohibited_actions: [external_write, production_execution, human_decision]
  privacy_classification: synthetic
  budget_limit_or_unknown: unknown
  time_limit: test-only
  known_business_rules: ["BUW and PC remain separate"]
  dry_run: true
  allow_external_writes: false
approval_context:
  risk_level: low
  approval_required: false
  approval_owner: null
  approval_status: not_required
  approval_evidence: []
```

| Fixture | Workflow ID | Agent/domain | Additional `workflow_inputs` |
|---|---|---|---|
| `agent-reports-to-ceo.yaml` | `agent_reports_to_ceo_decision_queue` | `CEO` / `Executive` | `situation`, `business_outcome`, `workflow_owner_agent`, `risk_level`, `data_cutoff`, `confidence`, `requested_decision` |
| `customer-complaint.yaml` | `customer_complaint_remediation` | `CustomerService` / `CustomerService` | `case_id`, `channel`, `customer_request`, `timeline` |
| `marketing-crm-campaign.yaml` | `marketing_crm_campaign` | `Marketing` / `Marketing` | `objective`, `audience`, `channel`, `market_scope`, `period`, `primary_business_outcome: acquisition_or_content`, `workflow_owner_agent: Marketing` |
| `shopify-developer.yaml` | `shopify_to_developer_draft_pr` | `Shopify` / `Shopify` | `business_goal`, `page_or_flow`, `current_state`, `desired_outcome`, `acceptance_criteria` |
| `store-anomaly.yaml` | `store_anomaly_investigation` | `Retail` / `Retail` | use `scope_level: store`, `store_code: G0011` in business context and inputs; add `period` and `anomaly_type` |

- [ ] **Step 2: Write the output and five-workflow tests**

Create `Tests/test_runtime_orchestrator.py` with:

```python
FIXTURE_EXPECTATIONS = {
    "agent-reports-to-ceo.yaml": ("agent_reports_to_ceo_decision_queue", "CEO", 3),
    "customer-complaint.yaml": ("customer_complaint_remediation", "CustomerService", 3),
    "marketing-crm-campaign.yaml": ("marketing_crm_campaign", "Marketing", 3),
    "shopify-developer.yaml": ("shopify_to_developer_draft_pr", "Shopify", 5),
    "store-anomaly.yaml": ("store_anomaly_investigation", "Retail", 2),
}

def test_all_published_workflows_stop_at_approval(self):
    for fixture_name, (workflow_id, agent, completed_count) in FIXTURE_EXPECTATIONS.items():
        result = RuntimeOrchestrator().execute(load_request(FIXTURE_ROOT / fixture_name))
        self.assertEqual(result["status"], "needs_approval")
        self.assertEqual(result["agent"], agent)
        self.assertEqual(result["domain_payload"]["workflow_id"], workflow_id)
        self.assertEqual(len(result["domain_payload"]["completed_steps"]), completed_count)
        self.assertFalse(result["domain_payload"]["external_writes_performed"])
```

Also assert exact Runtime output fields, `runtime_orchestrator_version`, 64-character fingerprint, fixed repository-relative workflow source, deterministic equality across fresh instances and identical audit timestamps.

- [ ] **Step 3: Write policy and idempotency tests**

For copies of the store fixture, test these exact mutations and expected exceptions:

```python
POLICY_MUTATIONS = [
    (("runtime_version",), "2.0"),
    (("business_context", "company"), "六合通"),
    (("business_context", "brand"), "shared"),
    (("constraints", "privacy_classification"), "production"),
    (("constraints", "dry_run"), False),
    (("constraints", "allow_external_writes"), True),
    (("approval_context", "approval_status"), "approved"),
    (("task", "workflow_id"), "unknown_workflow"),
]
```

Add separate tests that an unknown top-level `workflow_path`, task-level `code`, missing required workflow input and conflicting store code raise `RuntimePolicyError`; wrong content under an existing `run_id` raises `RunIdCollisionError`; identical replay returns equal but separately copied results and calls `_execute_once` exactly once.

- [ ] **Step 4: Write prohibited and no-write tests**

Patch the fixed loader to return a copy of a published workflow whose first step has `action_class: prohibited`, then assert `status: rejected`, no completed steps and `external_writes_performed: false`.

During all five fixture executions, patch these effect surfaces to raise if called:

```python
Path.write_text
subprocess.run
subprocess.Popen
socket.create_connection
urllib.request.urlopen
```

The test succeeds only when none is invoked.

- [ ] **Step 5: Run RED and confirm the expected failure**

Run:

```bash
.venv/bin/python -m unittest Tests.test_runtime_orchestrator -v
```

Expected: FAIL during import because `Runtime.runtime_orchestrator` does not exist. Fix only test syntax or fixture parsing errors until the failure is specifically the missing production module.

### Task 3: Implement the minimal Runtime Orchestrator

**Files:**
- Create: `Runtime/runtime_orchestrator.py`
- Test: `Tests/test_runtime_orchestrator.py`

**Interfaces:**
- Consumes: a JSON-compatible `dict[str, Any]` Runtime request and fixed workflow documents.
- Produces: `RuntimeOrchestrator.execute(request) -> dict[str, Any]`, `RuntimePolicyError`, and `RunIdCollisionError`; fixture path loading remains test-only.

- [ ] **Step 1: Define locked constants and errors**

```python
RUNTIME_VERSION = "1.0"
PUBLISHED_WORKFLOWS = {
    "agent_reports_to_ceo_decision_queue": "Schemas/Workflows/agent-report-ceo-decision-queue.yaml",
    "customer_complaint_remediation": "Schemas/Workflows/customer-complaint-remediation.yaml",
    "marketing_crm_campaign": "Schemas/Workflows/marketing-crm-campaign.yaml",
    "shopify_to_developer_draft_pr": "Schemas/Workflows/shopify-developer-draft-pr.yaml",
    "store_anomaly_investigation": "Schemas/Workflows/store-anomaly.yaml",
}

class RuntimePolicyError(ValueError):
    """Raised when a Runtime request fails the Stage 8 safety policy."""

class RunIdCollisionError(RuntimePolicyError):
    """Raised when a run_id is reused with different canonical content."""
```

Resolve workflow paths only as `REPOSITORY_ROOT / PUBLISHED_WORKFLOWS[workflow_id]`; never accept a path from the request.

- [ ] **Step 2: Implement canonicalization and idempotency**

```python
def execute(self, request: dict[str, Any]) -> dict[str, Any]:
    canonical_request = self._canonical_request(request)
    fingerprint = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    normalized = json.loads(canonical_request)
    run_id = normalized["run_id"]
    previous = self._runs.get(run_id)
    if previous is not None:
        previous_fingerprint, previous_result = previous
        if previous_fingerprint != fingerprint:
            raise RunIdCollisionError("run_id already exists with different canonical request")
        return copy.deepcopy(previous_result)
    self._validate_request(normalized)
    result = self._execute_once(normalized, fingerprint)
    self._runs[run_id] = (fingerprint, copy.deepcopy(result))
    return copy.deepcopy(result)
```

`_canonical_request` requires a mapping and non-empty string `run_id`, then uses `json.dumps(..., ensure_ascii=False, sort_keys=True, separators=(",", ":"))`; serialization failures become `RuntimePolicyError`.

- [ ] **Step 3: Implement exact Runtime validation**

Use exact allowed-key sets for the top level, business context, task, evidence item, constraints and approval context. Require all Runtime Contract fields plus `task.workflow_id`, `task.reporting_period`, `task.workflow_inputs`, `constraints.dry_run` and `constraints.allow_external_writes`.

Apply these checks before Harness execution:

```python
request["runtime_version"] == "1.0"
request["mode"] == "validate"
request["business_context"]["company"] == "汇沣电商"
request["business_context"]["brand"] in {"BUW", "PC"}
request["constraints"]["privacy_classification"] == "synthetic"
request["constraints"]["dry_run"] is True
request["constraints"]["allow_external_writes"] is False
{"external_write", "production_execution", "human_decision"}.issubset(
    request["constraints"]["prohibited_actions"]
)
request["approval_context"]["approval_status"] in {"not_required", "pending"}
request["approval_context"]["approval_evidence"] == []
```

Validate non-empty strings/lists, timezone-aware `requested_at`, evidence field completeness with `source_type: synthetic` and `synthetic://` IDs, approval flag/status agreement, workflow allowlist membership, no `brand` or `evidence_links` override in `workflow_inputs`, store-code consistency, all adapted workflow required inputs and the request `agent` against the workflow's fixed or runtime-selected accountable agent.

- [ ] **Step 4: Implement deterministic Harness adaptation**

Build the Harness payload using only validated Runtime values:

```python
payload = {
    "metadata": {
        "run_id": request["run_id"],
        "company": context["company"],
        "data_classification": constraints["privacy_classification"],
        "dry_run": constraints["dry_run"],
        "allow_external_writes": constraints["allow_external_writes"],
        "trigger_event_id": request["run_id"],
        "business_entity": business_entity,
        "period": task["reporting_period"],
    },
    "inputs": {
        **task["workflow_inputs"],
        "brand": context["brand"],
        "evidence_links": [item["source_link_or_id"] for item in request["evidence"]],
    },
}
```

Parse `requested_at`, normalize it to UTC, and instantiate `ControlledOrchestrator(now=lambda: fixed_time)`. After `run`, require the complete Runtime output field set and `external_writes_performed is False`, then add orchestrator version, fingerprint and fixed workflow source under `domain_payload`.

- [ ] **Step 5: Run GREEN and the existing suites**

Run:

```bash
.venv/bin/python -m unittest Tests.test_runtime_orchestrator -v
.venv/bin/python Tests/validate_aios_workflow_schema.py
.venv/bin/python -m unittest Tests.test_controlled_orchestrator -v
```

Expected: every command exits 0 with no failed test.

- [ ] **Step 6: Commit**

```bash
git add Runtime/runtime_orchestrator.py Tests/test_runtime_orchestrator.py Tests/Fixtures/runtime-orchestrator
git commit -m "feat: add synthetic Runtime Orchestrator v1"
```

### Task 4: Add focused operating documentation and read-only CI

**Files:**
- Create: `Tests/Runtime-Orchestrator-v1.md`
- Create: `.github/workflows/validate-runtime-orchestrator.yml`
- Modify: `Tests/test_runtime_orchestrator.py`

**Interfaces:**
- Consumes: the tested Runtime API and repository verification commands.
- Produces: reviewer-readable invocation/safety guidance and a pull-request-only CI gate with `contents: read`.

- [ ] **Step 1: Add failing repository-contract tests**

Add tests that parse the workflow text and documentation:

```python
workflow_text = (ROOT / ".github/workflows/validate-runtime-orchestrator.yml").read_text()
self.assertIn("permissions:\n  contents: read", workflow_text)
self.assertIn("pull_request:", workflow_text)
self.assertNotIn("push:", workflow_text)
self.assertNotIn("write", workflow_text.lower().replace("external_writes", ""))
self.assertTrue((ROOT / "Tests" / "Runtime-Orchestrator-v1.md").is_file())
```

Run the new tests and confirm they fail because the two files do not exist.

- [ ] **Step 2: Write the focused documentation**

Document the business loop, fixed workflow IDs, complete request shape, in-memory API invocation, expected `needs_approval`, idempotent replay/collision behavior, no-write guarantees, test commands and explicit exclusions. State that v1 has no CLI path argument and no production connector.

- [ ] **Step 3: Create the read-only workflow**

```yaml
name: Validate Runtime Orchestrator v1

on:
  pull_request:
    paths:
      - "Runtime/**"
      - "Schemas/**"
      - "Tests/**"
      - "requirements-dev.txt"
      - ".github/workflows/validate-runtime-orchestrator.yml"

permissions:
  contents: read

concurrency:
  group: runtime-orchestrator-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-dev.txt
      - run: python -m pip install --requirement requirements-dev.txt
      - run: python Tests/validate_aios_workflow_schema.py
      - run: python -m unittest Tests.test_controlled_orchestrator -v
      - run: python -m unittest Tests.test_runtime_orchestrator -v
```

- [ ] **Step 4: Verify and commit**

Run:

```bash
.venv/bin/python -m unittest discover -s Tests -p 'test_*.py' -v
.venv/bin/python Tests/validate_aios_workflow_schema.py
git diff --check
```

Expected: all tests pass, schema validation passes and the diff is clean.

Commit:

```bash
git add Tests/Runtime-Orchestrator-v1.md Tests/test_runtime_orchestrator.py .github/workflows/validate-runtime-orchestrator.yml
git commit -m "ci: validate Runtime Orchestrator without writes"
```

### Task 5: Verify, review, push and create the Draft PR

**Files:**
- Inspect: all changes from `origin/main...HEAD`

**Interfaces:**
- Consumes: committed Stage 8 implementation and all local evidence.
- Produces: pushed branch and an independent Draft PR targeting `main`.

- [ ] **Step 1: Run fresh complete verification**

```bash
.venv/bin/python Tests/validate_aios_workflow_schema.py
.venv/bin/python -m unittest discover -s Tests -p 'test_*.py' -v
git diff --check origin/main...HEAD
git status --short --branch
```

Expected: schema passes, all tests pass, no whitespace errors and no uncommitted tracked changes.

- [ ] **Step 2: Perform single-thread code review**

Because Issue #16 authorizes exactly one Execution Thread, do not dispatch a review agent. Review `git diff --stat origin/main...HEAD` and `git diff origin/main...HEAD` against every Issue #16 acceptance criterion, classify findings as Critical/Important/Minor, fix every Critical or Important finding with a regression test, and rerun Step 1.

- [ ] **Step 3: Push the authorized branch**

```bash
git push -u origin feat/aios-runtime-orchestrator-v1
```

- [ ] **Step 4: Create an independent Draft PR**

Create a Draft PR with base `main`, head `feat/aios-runtime-orchestrator-v1`, link Issue #16, summarize the locked allowlist and no-write boundary, list local commands/results, mark risk as low, and explicitly state: no deployment, no production/real data, no external writes, no Stage 9, no Issue #13, never ready and never merged by this Execution Thread.

### Task 6: Wait for CI and report Stage 8

**Files:**
- Modify: `Governance/AIOS-Stage-Registry.md`

**Interfaces:**
- Consumes: Draft PR URL, head commit and successful GitHub Actions evidence.
- Produces: Registry state `Reported` and the Mandatory Return posted to the Draft PR.

- [ ] **Step 1: Wait for all Draft PR checks**

Poll the workflow runs for the Draft PR head commit until each applicable check reaches a terminal state. If an in-scope test or CI configuration fails, reproduce locally, add a failing regression test where applicable, implement the smallest fix, rerun complete verification, commit and push. Do not fix unrelated repository or infrastructure failures by widening scope.

- [ ] **Step 2: Change only Stage 8 to Reported**

Replace `Executing` with `Reported`, link the Draft PR and CI evidence in the Stage 8 row, keep the same Issue, thread and branch, and set the next gate to human Governance Thread review. Add a change-log record that the Execution Thread submitted the Mandatory Return and did not self-declare `Reviewed`.

- [ ] **Step 3: Verify, commit and push the Registry return**

```bash
rg -n "RO-01|Reported|Draft PR|CI|human Governance Thread review" Governance/AIOS-Stage-Registry.md
git diff --check
git add Governance/AIOS-Stage-Registry.md
git commit -m "governance: report Stage 8 Runtime Orchestrator"
git push
```

- [ ] **Step 4: Re-wait for CI on the final Registry commit**

Wait until the Draft PR head commit containing the Reported Registry update has successful applicable checks. Record exact run/check URLs.

- [ ] **Step 5: Post the Chinese Execution Report**

Post this structure to the Draft PR conversation:

```markdown
## 本次完成

- Stage number / Stage ID: Stage 8 / RO-01
- Current status: Reported（Execution Thread 不自行声明 Reviewed）
- Completed scope: Runtime Orchestrator v1、五个 published workflow synthetic dry-run、fail-closed policy、审批停止、prohibited rejection、内存幂等、确定性审计、Runtime 输出契约、无写入测试、只读 CI。

## 证据链接

- Issue: #16
- Branch / commit: `feat/aios-runtime-orchestrator-v1` / final head commit
- Draft PR: current Draft PR
- Files / checks: design、plan、Runtime implementation、fixtures、tests、documentation、successful CI runs

## 阻塞项

- 无实施阻塞。等待人工 Governance Thread 审查；本线程不合并、不发布、不进入 Stage 9。

## 下一步

- Governance Thread 审查本次 return，并决定确认 Reviewed 或退回范围内修订。Archived、merge、publication 和 Stage 9 均需后续独立决定。
```

- [ ] **Step 6: Stop at Reported**

Confirm the PR remains Draft and unmerged, the final branch is clean and synchronized, the Registry says `Reported`, and return the Issue, Draft PR, commit and CI links. Do not mark ready, merge, deploy, change permissions, start Stage 9 or execute Issue #13.
