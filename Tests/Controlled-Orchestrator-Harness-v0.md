# Controlled Orchestrator Harness v0

## Purpose

Harness v0 proves that a split AIOS workflow can be loaded, interpreted and stopped at its safety boundary without invoking an Agent, external tool or production system.

It is intentionally not a production orchestrator. It only simulates control flow and creates reviewable artifacts.

## Safety boundary

Every accepted input must declare:

```yaml
metadata:
  run_id: unique-synthetic-run-id
  company: 汇沣电商
  data_classification: synthetic
  dry_run: true
  allow_external_writes: false
```

The runner rejects any other company or classification, any non-dry run and any request for external writes. `brand` must be BUW or PC; `shared` additionally requires explicit approval metadata and separate BUW/PC breakdown. It never sends messages, changes orders or inventory, modifies customer data, updates permissions, deploys code or performs a human decision.

Every result uses the complete Runtime Contract 1.0 output envelope. Workflow-specific Harness evidence remains under `domain_payload`; Runtime `status` remains separate from Green/Yellow/Red `executive_status`.

## Controlled invocation

```bash
python -m pip install -r requirements-dev.txt
python Runtime/controlled_orchestrator.py \
  --workflow Schemas/Workflows/store-anomaly.yaml \
  --input Tests/Fixtures/store-anomaly-synthetic-input.yaml
```

Expected business result:

- the two initial `automatic_low_risk` steps are simulated;
- canonical Agent handoffs `Retail` → `Data` → `Retail` are recorded with all 14 Runtime fields;
- the runner stops before `assign_supervisor_response` because it is `prepare_only`;
- an approval package is prepared for 李涛;
- status is `needs_approval`;
- no external write is performed.

This preserves the confirmed operating rule: 李涛 decides whether and which supervisor to dispatch; the system does not bind 梁其乐, Jenny or 小田 to a store or dispatch them automatically.

## Test coverage

```bash
python -m unittest Tests/test_controlled_orchestrator.py
```

The tests cover:

- the repository fixture end-to-end run;
- complete Runtime output and 14-field handoff envelopes;
- canonical Agent IDs and separation of Agent responsibility from human approval;
- missing required inputs becoming `blocked`;
- non-synthetic input rejection;
- external-write request rejection;
- cross-company and unauthorized shared-brand rejection;
- idempotency duplicate rejection;
- prohibited steps never executing;
- Marketing/CRM runtime selection of exactly one A/R from the primary business outcome;
- Tony/Stone fallback when approval authority is not declared;
- approval, handoff and audit evidence generation.

The existing Schema validator remains a separate required check.
