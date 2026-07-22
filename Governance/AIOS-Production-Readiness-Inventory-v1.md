# BUW AIOS Production Readiness Inventory v1.0

## Control and evidence basis

This inventory is a read-only snapshot of repository commit
`6cffaed4f4bc693aa897864396ae097b972bff80` for Stage 10 / PR-01. It describes
what exists and what is absent; it does not authorize filling any production gap.

## Architecture and dependency inventory

| Component | Current repository capability | Dependency | Production assessment | Evidence |
|---|---|---|---|---|
| Governance layer | Frozen Thread Governance v2.1, Project Governance v1.0 and Stage/Project registries | Human Governance Thread and GitHub history | Governed, but not a runtime control plane | `Governance/` |
| Agent layer | Eight documented Agent roles, prompts, RACI and runtime envelope | Markdown policy and human judgment | Design evidence only | `Agents/`, `Prompts/`, `AIOS/Agent-RACI.md` |
| Workflow layer | Five versioned workflow documents validated against Schema v1 | YAML and PyYAML | Deterministic repository artifacts, no scheduler/queue | `Schemas/`, `Workflows/` |
| Controlled Harness v0 | Simulates low-risk steps and stops at approval/prohibited actions | Python and PyYAML | Synthetic-only, in-memory, no external tools | `Runtime/controlled_orchestrator.py` |
| Runtime Orchestrator v1 | Validates exact requests, fixed workflow allowlist, boundaries, deterministic audit and replay | Python, PyYAML, Harness v0 | `mode=validate`; synthetic-only; no deployable service | `Runtime/runtime_orchestrator.py` |
| Fixtures and tests | Synthetic positive/negative company, brand, write, policy, idempotency and schema cases | Python unittest and PyYAML | Strong validation evidence, not production evidence | `Tests/` |
| CI | Pull-request checks with repository contents read permission | GitHub Actions, Python 3.12, PyYAML | Review-time validation only | `.github/workflows/` |
| Dependency manifest | `PyYAML>=6.0,<7.0` | Python package index during CI setup | Development validation dependency only | `requirements-dev.txt` |

No code change to Runtime, Harness, Schema, workflows, Agents or frozen governance
is required or authorized for this assessment.

## Operating-boundary inventory

| Boundary | Current enforcement | Stage 10 interpretation |
|---|---|---|
| Company | Runtime/Harness accept 汇沣电商 and reject 六合通/cross-company input. | Keep companies separate; no combined pilot. |
| Brand | Runtime accepts BUW or PC and rejects shared/unknown; Harness requires approval and breakdown for shared synthetic tests. | BUW and PC remain independent; no shared production scope is inferred. |
| Data | Runtime requires synthetic privacy classification and `synthetic://` evidence. | Real business/customer data remains prohibited. |
| Writes | Requests must prohibit external writes and set `allow_external_writes=false`. | No API, database, business or outbound write is authorized. |
| Actions | Automatic steps are simulated; prepare-only stops; prohibited steps reject. | No production action, human decision or release occurs. |
| Workflow selection | Fixed repository allowlist; no request-selected path, import or executable code. | Dynamic production routing is absent and not added. |
| State | Runtime idempotency and audit state are in memory. | No durable execution, queue, ledger or audit guarantee exists. |
| Approval | Runtime never treats input evidence or silence as approval. | Every future production-class gate remains human and not authorized. |

## Verified absences and limitations

The repository file inventory and current Runtime documentation show no:

- deployment manifest, service process, production environment or release pipeline;
- production API, database, message bus, scheduler, queue or connector;
- persistent state, distributed idempotency, backup or restore implementation;
- production authentication, authorization, identity or secrets integration;
- real-data classification, retention, deletion or source reconciliation implementation;
- durable logs, metrics, traces, SLOs, alerts or operational dashboards;
- deployment rollback automation, state recovery plan, RTO/RPO or drill;
- production incident-response or support/on-call runbook;
- approved pilot scope, risk acceptance or release authority.

These are assessment findings, not a mandate to implement them. Absence of a
connector or credential reduces current exposure but does not constitute a passed
production security, privacy, data or operations gate.

## Evidence limitations

- Evidence is repository-local and synthetic; no production system was inspected.
- Dynamic business facts, store/customer records and production configuration were
  intentionally not accessed.
- CI proves deterministic repository behavior only.
- Owner, threshold, SLO, RTO/RPO, support and incident decisions remain unassigned
  until the Governance Thread creates the appropriate authority and evidence path.
