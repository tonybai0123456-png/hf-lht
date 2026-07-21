# AIOS Workflow Schema v1 Validation

## Result

The executable validator passed against `Schemas/AIOS-Workflow-Schema-v1.yaml`.

```text
AIOS Workflow Schema v1 validation PASSED
- parsed documents: 6
- validated workflows: 5
- synthetic negative cases: 4
```

## Run

```bash
python3 -m pip install -r requirements-dev.txt
python3 Tests/validate_aios_workflow_schema.py
```

## Coverage

The validator checks the contract and all five workflow instances for:

- one non-empty accountable agent;
- required input declarations;
- valid Runtime Contract 1.0 statuses and action classes;
- explicit transition conditions;
- approval-package output for approval gates;
- handoff, evidence, completion and audit fields;
- retry, timeout, stale, idempotency and audit contract settings;
- Retail dynamic supervisor dispatch by 李涛 and escalation to Stone.

Four synthetic negative cases confirm that missing ownership, missing required
inputs, invalid approval output and invalid transition state are rejected.

This validation uses repository-only synthetic structures. It does not access
production systems or real business records.
