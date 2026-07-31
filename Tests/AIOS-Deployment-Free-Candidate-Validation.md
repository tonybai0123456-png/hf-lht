# AIOS Deployment-free Candidate Evidence Validation

## Purpose

This validation package records the truthful, deployment-free preparation
state for Stage 15 / NR-01. A successful schema validation means only that the
record is internally consistent. The current status is
`technical_evidence_verified_pending_human_gates`, and the only valid evaluation is
`not_ready_pending_human_governance`.

The result must not be interpreted as a merge, publication, archive, real
pilot, production-readiness, release, deployment, risk acceptance, or
permission decision（不得解释为上述任何授权）.

## Controlled scope and data boundary

- Company and brand: 汇沣电商 / BUW only.
- Excluded entities: PC and 六合通.
- Allowed data class: `synthetic_non_personal`.
- Narrowly allowed test class:
  `synthetic_personal_like_clearly_fictitious_non_routable`.
- Real customer, employee, business, payment, identifier, copied production,
  credential, connector, endpoint, and infrastructure-account material remain
  prohibited.
- Repository, local validation, and pull-request CI are the only execution
  surfaces. `external_actions_performed=[]`.

Gate 7 is accepted by the explicit owner decision recorded in Issue #44:

- Tony is the human approver.
- Stone is the backup and escalation contact.
- Data Agent is the technical validation owner.
- Developer Agent provides implementation support only.

This responsibility split grants only the stated synthetic-data boundary.
Gate 8 is separately accepted under Issue #45 for synthetic operations,
recovery, incident-tabletop and support-flow validation only. Stone is the
human approver, Tony is backup and escalation, Developer Agent is technical
owner, and CustomerService Agent plus Data Agent are evidence contributors.
It authorizes no real monitoring, alerting, ticketing, incident, failover,
restore, support operation or achieved RTO/RPO claim.

Gate 9–12 remain unaccepted. Issue #49 expressly withholds release while defining the
deployment-free evidence boundary.

## Evidence contract

The machine-readable record contains twelve evidence requirements:

1. Exact commit and tree.
2. Changed-file and asset manifest.
3. Clean-checkout reproducibility.
4. Local tests, validators, compile, and diff checks.
5. Exact-head CI.
6. Gate ledger for Gates 1–11.
7. Risk map and proposed treatment owners.
8. Synthetic control evidence.
9. Dependency manifest and install instructions.
10. Scan evidence for secrets, real data, connectors, and infrastructure
    material.
11. Explicitly withheld authorities.
12. Mandatory Return with `external_actions_performed=[]`.

The separate controlled receipt verifies the exact source commit/tree,
29-path manifest, clean-export replay, local tests and validators, exact-head
CI, synthetic controls, dependency resolution, scan and Mandatory Return.
Gate-ledger completion remains pending human governance. Risk treatment owners
are verified as a proposed mapping only and remain unapproved.

## Run locally

From the repository root:

```bash
python3 -m pip install --requirement requirements-dev.txt
python3 Tests/validate_aios_deployment_free_candidate.py
python3 -m unittest Tests.test_deployment_free_candidate -v
python3 -m unittest Tests.test_project_governance -v
```

Expected validator output:

```text
AIOS deployment-free candidate evidence validation PASSED
result=not_ready_pending_human_governance
external_actions_performed=[]
```

Any malformed structure, changed scope, elevated gate, real-data claim,
external action, or release-like state must fail closed.

Pull-request validation reuses the existing read-only
`.github/workflows/validate-aios-support-controlled-pilot.yml` workflow. Its
unfiltered `pull_request` trigger runs the full `Tests/test_*.py` discovery,
which includes this candidate package, and compiles the test tree. No workflow
permission or external write is added.
