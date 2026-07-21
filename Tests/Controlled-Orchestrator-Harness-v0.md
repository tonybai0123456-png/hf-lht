# Controlled Orchestrator Harness v0

## Purpose

Harness v0 proves that a split AIOS workflow can be loaded, interpreted and stopped at its safety boundary without invoking an Agent, external tool or production system.

It is intentionally not a production orchestrator. It only simulates control flow and creates reviewable artifacts.

## Safety boundary

Every accepted input must declare:

```yaml
metadata:
  data_classification: synthetic
  dry_run: true
  allow_external_writes: false
```

The runner rejects any other classification, any non-dry run and any request for external writes. It never sends messages, changes orders or inventory, modifies customer data, updates permissions, deploys code or performs a human decision.

## Controlled invocation

```bash
python -m pip install -r requirements-dev.txt
python Runtime/controlled_orchestrator.py \
  --workflow Schemas/Workflows/store-anomaly.yaml \
  --input Tests/Fixtures/store-anomaly-synthetic-input.yaml
```

Expected business result:

- the two initial `automatic_low_risk` steps are simulated;
- the Retail Agent to Data Agent handoff is recorded;
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
- missing required inputs becoming `blocked`;
- non-synthetic input rejection;
- external-write request rejection;
- idempotency duplicate rejection;
- prohibited steps never executing;
- approval, handoff and audit evidence generation.

The existing Schema validator remains a separate required check.
