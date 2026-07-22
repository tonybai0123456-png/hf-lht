# Stage 12 Privacy and Data Governance Validation

## Scope

This is deterministic, synthetic and read-only validation of the DG-01 policy package. It connects no source, processes no real data, performs no export, correction, retention, deletion or subject-request fulfillment, makes no legal conclusion and grants no production authority.

## Positive case

`SYN-DG-001` declares `synthetic: true`, company 汇沣电商, brand BUW, the registered synthetic contact asset and subject, one contact category, one synthetic email field, purpose `service_response`, basis record `BASIS-SYN-001`, abstract role `Data Steward`, read action, bounded rule `RET-SYN-030D` and lineage `synthetic_fixture` → `in_memory_validation`. It must return no denial reasons.

## Negative cases

| Mutation | Required denial |
|---|---|
| Missing or false synthetic marker | `real_or_unmarked_data` |
| PC, 六合通, wildcard or unknown boundary | `cross_boundary` |
| Unknown purpose | `unknown_purpose` |
| Missing or incompatible basis record | `missing_basis_decision` or `invalid_basis_decision` |
| Field outside the purpose allowlist | `excessive_fields` |
| Unlisted role, purpose, category or action | `unauthorized_access` |
| Missing required preference reference | `missing_consent_or_preference` |
| Unknown, unsafe or purpose-incompatible preference reference | `invalid_consent_or_preference` |
| Missing request ID, categories or fields | `missing_request_id`, `missing_categories` or `missing_fields` |
| Asset, category, field or action conflicts with the selected purpose | `asset_not_allowed_for_purpose`, `category_not_allowed_for_purpose`, `field_not_allowed_for_asset` or `action_not_allowed_for_purpose` |
| Delete, correct, export or fulfillment action | `human_approval_required` |
| Unknown, unbounded or auto-delete retention | `invalid_retention` |
| Missing or disallowed lineage | `missing_lineage` or `invalid_lineage` |
| Automatic real deletion claim | `automatic_real_deletion` |
| Legal, compliance, real-data or production authority claim | `production_or_legal_claim` |

Tests also reject invented owners, accepted Stage 10 risks, real-data authority and any CI trigger or permission that can write.

## Commands

```bash
python Tests/validate_aios_privacy_data_governance.py
python -m unittest Tests.test_privacy_data_governance -v
python -m unittest discover -s Tests -p 'test_*.py' -v
python Tests/validate_aios_workflow_schema.py
python -m compileall -q Runtime Tests
```

Passing proves only that the versioned policy package is internally complete and that declared synthetic requests fail closed. It is not legal approval, compliance certification, real-data authority, production readiness, deployment, pilot, release, Reviewed or Archived evidence.
