# AIOS Operational Resilience v1 Validation

## Scope

This evidence validates the Stage 13 / OR-01 repository package only. It uses a synthetic fixture and deterministic in-memory evaluation. It does not connect to or operate monitoring, infrastructure, databases, alerts, paging, backups, restores, failover, communications or incidents.

## Positive case

`Tests/Fixtures/operational-resilience/synthetic-service-degradation.yaml` declares 汇沣电商 / BUW, one known conceptual service, two known synthetic dependencies, SEV-2/high impact, the exact CT-2 design target, three design-only recovery evidence records, a prepare-only requested action and all seven human gates.

Expected result: `needs_human_approval`, no reason codes and `external_actions_performed: false`. The result also contains a complete in-memory `incident_record` with exactly the model contract fields, policy version `2.2`, the fixture identity and the same decision, reason codes, required gates and evidence references as the outer result.

## Negative cases

The targeted test suite independently verifies denial of:

- missing, empty or whitespace-only scenario identity;
- unmarked or non-synthetic signal;
- PC, 六合通, wildcard, shared or unknown company/brand scope;
- unknown service or dependency, duplicate model IDs, and non-exact or duplicated dependency IDs;
- invalid severity or impact;
- unsupported RTO/RPO tier/value combinations;
- missing, reordered or duplicated recovery evidence IDs, or a state claiming a tested restore;
- missing, reordered or duplicated human gates;
- requested or reported real continuity action;
- missing, empty, unknown, non-boolean or truthy capability-claim fields;
- mutations enabling automatic incident/containment/recovery/closure, executable runbooks, paging, external communication, alert delivery, monitoring connectors, durable telemetry, persistent/mutable audit, personal content or credentials;
- mutations to the authorized prepare-only or prohibited-real action sets;
- invented owner, production authority, risk acceptance, release or pilot authority;
- Stage 10 risk closure/acceptance and Stage 14 activation;
- push-enabled or write-capable CI.

## Commands

```text
python Tests/validate_aios_operational_resilience.py
python -m unittest Tests.test_operational_resilience -v
python -m unittest discover -s Tests -p 'test_*.py' -v
python Tests/validate_aios_workflow_schema.py
python -m compileall -q Runtime Tests
```

Compilation uses a task-local or temporary `PYTHONPYCACHEPREFIX` when the host's default cache path is restricted.

## Meaning of PASS

PASS proves that the committed documents, model, fixture, mappings, validator, tests, registries and CI contract are mutually consistent on the tested head. It proves deterministic denial behavior for the declared synthetic mutations and complete generation of the tested in-memory synthetic incident record.

PASS does not prove production readiness, an achieved RTO/RPO/SLA/SLO, a tested backup or restore, monitor/alert coverage, incident response, owner readiness, legal compliance, risk acceptance, pilot readiness or release authority. Human review, merge, publication and archive remain separate governance decisions.
