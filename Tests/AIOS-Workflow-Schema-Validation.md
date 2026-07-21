# AIOS Workflow Schema v1 Validation

## Result

The executable validator covers both the embedded multi-document schema and the five parser-friendly split workflow files.

Expected successful output:

```text
AIOS Workflow Schema v1 validation PASSED
- parsed embedded documents: 6
- validated embedded workflows: 5
- validated split workflow files: 5
- cross-file consistency: PASS
- synthetic negative cases: 4
```

## Run

```bash
python3 -m pip install -r requirements-dev.txt
python3 Tests/validate_aios_workflow_schema.py
```

## Coverage

The validator checks:

- one non-empty accountable agent per workflow;
- required input declarations;
- Runtime Contract 1.0 status and action enums;
- explicit transition conditions;
- approval-package output for approval gates;
- handoff, evidence, completion and audit fields;
- retry, timeout, stale, idempotency and audit contract settings;
- exactly five unique workflow IDs;
- schema-version consistency across split files;
- exact semantic equality between embedded and split instances;
- Retail dynamic supervisor dispatch by 李涛 and escalation to Stone.

Four synthetic negative cases confirm rejection of missing ownership, missing required inputs, invalid approval output and invalid transition state.

The GitHub Actions workflow runs the same validator on relevant pull-request and branch changes. This validation uses repository-only synthetic structures and does not access production systems or real business records.
