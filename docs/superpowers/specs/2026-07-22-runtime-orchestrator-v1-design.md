# Runtime Orchestrator v1 Design

## 1. Decision and purpose

Stage 8 / RO-01 implements approved 方案 A: a minimal `RuntimeOrchestrator` layer above the published Workflow Schema v1 files and the existing `ControlledOrchestrator`. It converts one strict Runtime Contract 1.0 request into the existing harness payload, invokes only the fixed synthetic dry-run boundary, and returns the complete Runtime output envelope.

This stage proves deterministic selection, validation, approval-stop, auditability and idempotency. It does not turn Harness v0 into a production executor and does not expand Stage 6 architecture.

## 2. Business loop and the six system questions

1. **Business loop:** a caller submits a Runtime Contract request for one published workflow; the orchestrator validates company, brand, authorization and safety policy; the controlled harness simulates low-risk steps; the run stops at approval or rejection and returns review evidence.
2. **Core objects:** Runtime request, published workflow, canonical request fingerprint, run record, Runtime result, approval package and audit entry.
3. **Data flow:** synthetic YAML fixture or in-memory request → strict Runtime validation → fixed workflow allowlist → adapter-generated Harness payload → `ControlledOrchestrator` → Runtime-compatible in-memory result. No business output is written to disk or an external system.
4. **Operator and scenario:** a developer or reviewer runs local tests or read-only GitHub Actions against synthetic fixtures. There is no production operator path in v1.
5. **System versus human judgment:** the system validates policy, selects the fixed workflow, simulates `automatic_low_risk` steps, detects prohibited steps and stops at `prepare_only`. A named human reviews any approval package; silence is never approval.
6. **Proof:** all five published workflow IDs pass positive synthetic tests; negative tests cover policy, scope, paths, code, approval, action class and idempotency; deterministic equality and complete Runtime output fields are asserted; CI uses `contents: read` only.

## 3. Scope

### Included

- `Runtime/runtime_orchestrator.py` with Runtime version `1.0`.
- A fixed allowlist for exactly these published workflow IDs:
  - `agent_reports_to_ceo_decision_queue`
  - `customer_complaint_remediation`
  - `marketing_crm_campaign`
  - `shopify_to_developer_draft_pr`
  - `store_anomaly_investigation`
- Strict Runtime Contract request validation and deterministic adaptation to Harness v0.
- Synthetic fixtures for all five workflows.
- Focused automated tests, operator documentation and read-only pull-request CI.
- In-memory idempotency for the life of one `RuntimeOrchestrator` instance.

### Excluded

- Deployment, merge, production or real data, external APIs, databases, outbound messages or business writes.
- Permission, credential, pricing, payment, customer, order, inventory or financial changes.
- User-selected workflow paths, plugin/module names, commands, expressions or executable code.
- Persistence, queues, schedulers, connectors, distributed locks, retries or production observability.
- Changes to Workflow Schema v1, Runtime Contract 1.0, `ControlledOrchestrator`, Stage 6 architecture, Stage 9 or Issue #13.

## 4. Public interface

```python
class RuntimePolicyError(ValueError):
    pass


class RunIdCollisionError(RuntimePolicyError):
    pass


class RuntimeOrchestrator:
    def execute(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate and execute one deterministic synthetic dry-run."""
```

The request uses the published Runtime Contract 1.0 top-level envelope and adds only the Stage 8 routing fields needed inside existing objects:

```yaml
runtime_version: "1.0"
run_id: "SYN-RO-STORE-001"
agent: Retail
mode: validate
requested_by: "synthetic-test-suite"
requested_at: "2026-07-22T08:00:00Z"
business_context:
  company: 汇沣电商
  brand: BUW
  scope_level: store
  store_code: G0011
  department: Retail
  decision_owner: 李涛
  operating_owner: Retail
task:
  workflow_id: store_anomaly_investigation
  objective: "Validate synthetic store anomaly control flow"
  requested_output: "Runtime Contract 1.0 result"
  acceptance_criteria: ["stop before approval-required action"]
  deadline_or_review_date: "2026-07-23"
  requested_next_action: "validate"
  reporting_period: "2026-07-22"
  workflow_inputs:
    store_code: G0011
    period: "2026-07-22"
    anomaly_type: synthetic_anomaly
evidence:
  - source_type: synthetic
    source_name: "synthetic store alert"
    source_link_or_id: "synthetic://store/G0011/alert/001"
    data_cutoff: "2026-07-22"
    owner: Retail
    confidence: high
    limitations: "Synthetic fixture only"
constraints:
  prohibited_actions: [external_write, production_execution, human_decision]
  privacy_classification: synthetic
  budget_limit_or_unknown: unknown
  time_limit: "test-only"
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

`task.workflow_inputs` supplies only domain inputs. `brand` is always sourced from `business_context`; `evidence_links` is always derived from the validated evidence items. A caller may not override either field in `workflow_inputs`.

## 5. Fail-closed validation

Validation happens before workflow execution. Any missing, empty, malformed, ambiguous or unauthorized field raises `RuntimePolicyError`; a reused `run_id` with different canonical content raises `RunIdCollisionError`.

The following policy is fixed for v1:

- Top-level fields must exactly match the Runtime Contract 1.0 envelope.
- `runtime_version` must be `"1.0"`; `mode` must be `validate`.
- `workflow_id` must be in the five-item fixed allowlist. No path, filename, module, command, callable or code field is accepted.
- `company` must be exactly `汇沣电商`. `六合通` and all other companies are rejected.
- `brand` must be exactly `BUW` or `PC`. `shared`, `unknown` and all cross-brand requests are rejected in v1; a future shared view requires a separate authorized design.
- `store_code` is required for `scope_level: store`, and any duplicate `workflow_inputs.store_code` must match it.
- Every evidence item must contain all Runtime Contract fields, use `source_type: synthetic`, use a `synthetic://` identifier and a valid confidence value.
- `privacy_classification` must be `synthetic`, `dry_run` must be `true`, and `allow_external_writes` must be `false`.
- `prohibited_actions` must explicitly include `external_write`, `production_execution` and `human_decision`.
- Approval status may only be `not_required` or `pending`. It must agree with `approval_required`; pending approval requires a named owner, and input approval evidence must be empty. Runtime v1 never consumes or invents an approval.
- All required workflow inputs must be non-empty after the adapter adds brand and evidence links.

The orchestrator never accepts arbitrary filesystem paths. Workflow IDs map to repository-owned constants resolved relative to the Runtime module. YAML loading remains in the existing `load_workflow` helper; code evaluation and dynamic imports are absent.

## 6. Deterministic execution and output

The canonical request is JSON encoded with sorted keys, stable separators and UTF-8 characters preserved, then hashed with SHA-256. `requested_at` must be timezone-aware ISO-8601 and becomes the fixed UTC clock passed to `ControlledOrchestrator`; every audit entry in one run therefore has the same deterministic timestamp.

The adapter creates Harness metadata as follows:

| Harness field | Runtime source |
|---|---|
| `run_id` | top-level `run_id` |
| `company` | `business_context.company` |
| `data_classification` | `constraints.privacy_classification` |
| `dry_run` | `constraints.dry_run` |
| `allow_external_writes` | `constraints.allow_external_writes` |
| `trigger_event_id` | top-level `run_id` |
| `business_entity` | `brand` plus optional `store_code` |
| `period` | `task.reporting_period` |

The result retains every top-level field required by the Runtime Contract standard output. Stage 8 evidence is additive only under `domain_payload`:

- `runtime_orchestrator_version: "1.0"`
- `request_fingerprint: <sha256>`
- `workflow_source: <fixed repository-relative path>`

The existing Harness behavior remains authoritative for step simulation, handoffs, `prepare_only` approval stops and `prohibited` rejection. `external_writes_performed` must remain `false` in every returned result.

## 7. Idempotency

The orchestrator stores `run_id → (request_fingerprint, deep-copied result)` in memory only.

- First valid request: execute once and store the result.
- Same `run_id` and same canonical request: return a fresh deep copy of the stored result, with no workflow reload or Harness rerun and no new audit event.
- Same `run_id` and different canonical request: raise `RunIdCollisionError` before validation or execution of the changed request.
- Policy failures before execution are not cached.

This intentionally differs from Harness v0's legacy duplicate-key rejection: Runtime v1 owns request-level idempotency above the Harness boundary while leaving Harness v0 unchanged.

## 8. Safety and governance properties

- **Locked allowlist:** only five repository-owned workflow documents can be selected.
- **Most restrictive wins:** any missing or conflicting company, brand, approval or safety declaration rejects the request.
- **Approval stop:** `prepare_only` returns `needs_approval`; no subsequent step runs.
- **Prohibited stop:** a `prohibited` action returns `rejected`; the prohibited step and all later steps do not run.
- **No external effects:** Runtime v1 has no connector, write, subprocess, network or messaging interface.
- **Explicit entities:** company and brand are independently validated and are included in the adapted business entity.
- **Audit:** deterministic Harness audit plus request fingerprint and fixed workflow source make each accepted result reproducible.

## 9. Test and CI design

Focused tests must demonstrate:

1. all five fixed workflow IDs execute from synthetic fixtures and stop at their published approval gate;
2. complete Runtime output fields and Stage 8 domain evidence;
3. deterministic results and audit logs across fresh orchestrator instances;
4. same-request idempotent replay without invoking `_execute_once` again;
5. changed-request `run_id` collision rejection;
6. non-synthetic, external-write, non-dry-run, wrong-version, wrong-company, shared-brand, unknown-workflow, arbitrary-path/code keys, malformed approval and missing-input rejection;
7. a published workflow containing a prohibited first step is rejected without completion or external writes;
8. no filesystem business write, subprocess or network connection is attempted during fixture runs;
9. the existing schema validator and Controlled Harness tests remain green.

GitHub Actions runs only on pull requests affecting Runtime Orchestrator files and declares `permissions: contents: read`. It installs `requirements-dev.txt` and runs the schema validator, existing Harness suite and new Runtime suite. It performs no upload, comment, deployment, mutation or secret-dependent step.

## 10. Delivery and rollback

Delivery is an independent Draft PR from `feat/aios-runtime-orchestrator-v1` to `main`. Stage 8 may move only from `Executing` to `Reported`; human Governance Thread review is required for `Reviewed`. The Execution Thread never marks the PR ready and never merges it.

Rollback before merge is to close the Draft PR or abandon the branch. No production or business state exists to reverse.
