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

- canonical IDs for all Agent ownership fields;
- one accountable Agent per workflow run, including the Marketing/CRM runtime selector;
- required input declarations;
- Runtime Contract 1.0 status and action enums;
- the complete Runtime output envelope and 14-field handoff contract;
- explicit transition conditions;
- approval-package output for approval gates;
- handoff, evidence, completion and audit fields;
- retry, timeout, stale, idempotency and audit contract settings;
- exactly five unique workflow IDs;
- schema-version consistency across split files;
- exact semantic equality between embedded and split instances;
- Retail ownership of supervisor-response preparation, 李涛 human approval and escalation to Stone;
- separation of BUW/PC, explicit approval for shared-brand views and prohibition on mixing 汇沣电商 with 六合通.

Four schema mutation cases confirm rejection of missing ownership, missing required inputs, invalid approval output and invalid transition state. Harness behavior tests separately cover runtime ownership, handoff, approval and company/brand boundaries.

The GitHub Actions workflow runs the same validator on relevant pull-request and branch changes. This validation uses repository-only synthetic structures and does not access production systems or real business records.
