# Runtime Orchestrator v1

## Purpose

Runtime Orchestrator v1 is the Stage 8 / RO-01 policy and routing layer above the existing Controlled Orchestrator Harness v0. It proves that a Runtime Contract 1.0 request can select one published workflow, fail closed at the BUW AIOS boundary, produce deterministic audit evidence and stop before a human approval without external or business effects.

It is a synthetic validation component, not a production orchestrator.
It performs no external writes.

## Business loop

1. A caller constructs one complete Runtime Contract 1.0 request in memory.
2. Runtime v1 validates the exact envelope, company, brand, evidence, approval and no-write declarations.
3. A fixed workflow ID selects a repository-owned Workflow Schema v1 document.
4. Runtime v1 derives the Controlled Harness payload and fixes its audit clock from `requested_at`.
5. Harness v0 simulates only `automatic_low_risk` steps, stops before `prepare_only`, and rejects `prohibited` steps.
6. Runtime v1 returns the complete Runtime output with deterministic Stage 8 evidence under `domain_payload`.

## Fixed workflow allowlist

- `agent_reports_to_ceo_decision_queue`
- `customer_complaint_remediation`
- `marketing_crm_campaign`
- `shopify_to_developer_draft_pr`
- `store_anomaly_investigation`

The request supplies a workflow ID, never a path. Runtime v1 contains no dynamic import, module, callable, command, expression or code execution field. It has no CLI workflow-path argument.

## Required safety boundary

Every accepted request must declare:

```yaml
runtime_version: "1.0"
mode: validate
business_context:
  company: 汇沣电商
  brand: BUW  # or PC
constraints:
  prohibited_actions: [external_write, production_execution, human_decision]
  privacy_classification: synthetic
  dry_run: true
  allow_external_writes: false
approval_context:
  approval_required: false
  approval_owner: null
  approval_status: not_required
  approval_evidence: []
```

Every evidence item must be explicitly synthetic and use a `synthetic://` identifier. `brand` is limited to BUW or PC; `shared` and `unknown` fail closed in v1. `company` is limited to 汇沣电商; 六合通 or any cross-company request fails closed. Brand and evidence links are derived from the Runtime envelope and cannot be overridden in workflow inputs.

## Complete request and in-memory invocation

The repository contains one complete request for each published workflow under `Tests/Fixtures/runtime-orchestrator/`. The API accepts a mapping already loaded in memory:

```python
from pathlib import Path
import yaml

from Runtime.runtime_orchestrator import RuntimeOrchestrator

fixture = Path("Tests/Fixtures/runtime-orchestrator/store-anomaly.yaml")
request = yaml.safe_load(fixture.read_text(encoding="utf-8"))
result = RuntimeOrchestrator().execute(request)

assert result["status"] == "needs_approval"
assert result["domain_payload"]["external_writes_performed"] is False
```

Fixture loading belongs to test code only. The production Runtime module exposes no path-based request loader. Workflow selection remains a fixed in-code allowlist and no request field can select a filesystem path.

The returned top-level object exactly matches the Runtime Contract 1.0 standard output. `domain_payload` also contains:

- `runtime_orchestrator_version: "1.0"`;
- the SHA-256 `request_fingerprint`;
- the fixed repository-relative `workflow_source`;
- deterministic Harness audit entries;
- `external_writes_performed: false`.

## Approval and prohibited behavior

- `automatic_low_risk`: simulated in memory and added to completed-step evidence.
- `prepare_only`: not executed; result becomes `needs_approval` with an approval package.
- `prohibited`: not executed; result becomes `rejected` and no later step runs.

Runtime v1 never interprets silence as approval and never accepts input approval evidence as authority.

## Idempotency

One `RuntimeOrchestrator` instance keeps an in-memory ledger:

- first valid `run_id`: execute once and retain a deep copy;
- same `run_id` plus identical canonical request: return a fresh copy of the retained result without reloading or rerunning;
- same `run_id` plus changed canonical request: raise `RunIdCollisionError` before execution;
- rejected preflight policy requests are not retained.

The ledger is intentionally not persistent or distributed in Stage 8.

## Verification

```bash
python -m pip install --requirement requirements-dev.txt
python Tests/validate_aios_workflow_schema.py
python -m unittest Tests.test_controlled_orchestrator -v
python -m unittest Tests.test_runtime_orchestrator -v
```

The Runtime suite covers all five workflows, Runtime output compatibility, deterministic audit, idempotent replay, run collision, wrong version, non-synthetic data, write requests, company/brand mixing, unknown workflows, arbitrary routing/code fields, missing inputs, accountability mismatch, prohibited steps and guarded write/process/network surfaces.

GitHub Actions runs the same checks on pull requests with `contents: read` only and does not persist checkout credentials.

## Explicit exclusions

Runtime v1 has no external API, database, production connector, message sender, business write, deployment, merge, permission change, real data, persistent queue or scheduler. Stage 9 and Issue #13 are outside RO-01. The Stage 8 Execution Thread stops at `Reported` for human Governance Thread review.
