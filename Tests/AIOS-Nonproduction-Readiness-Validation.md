# AIOS Non-production Readiness Validation

Run from the repository root in a clean Python environment:

    python -m pip install --requirement requirements-dev.txt
    python3 Tests/validate_aios_nonproduction_readiness.py
    python3 -m unittest Tests.test_nonproduction_readiness -v
    python3 -m unittest Tests.test_project_governance -v
    python3 -m unittest discover -s Tests -p 'test_*.py' -v
    python3 Tests/validate_aios_workflow_schema.py
    python3 Tests/validate_aios_operational_resilience.py
    python3 Tests/validate_aios_support_controlled_pilot.py
    python3 -m compileall -q Runtime Tests
    git diff --check

Expected validator output:

    AIOS non-production readiness validation PASSED
    result=needs_human_governance
    external_actions_performed=[]

Expected behavior:

- The canonical BUW synthetic package returns `needs_human_governance`.
- PC, 六合通, wildcard, unknown, real-data and authority-like inputs are denied.
- Empty capability declarations are allowed only at the three canonical
  environment paths; non-empty or misplaced declarations are denied.
- YAML anchors, aliases, merge keys, cyclic structures and malformed types fail
  closed without escaping exceptions.
- Acceptance requirements use exact test and evidence links; nonexistent test
  names and cross-requirement evidence substitutions are denied.
- The exact implementation-evidence gate is recorded as accepted only by the
  Human Governance Thread decision on reviewed target
  `b27614ba2ebebb772888c3a4b1ff3d829b47532e`.
- Gate 5 is recorded as accepted only by the owner authorization in Issue #42:
  Tony is the single accountable owner and Stone is the backup and escalation
  contact; gates 6 through 12 remain unauthorized.
- Gate 6 is recorded as accepted only by the architecture and security
  authorization in Issue #43: the design is platform-neutral, uses synthetic
  data and runs only in isolated non-production; Stone is the human approver
  and Developer Agent owns the technical solution and validation;
  gates 7 through 12 remain unauthorized.
- Gate 6 validation provisions no cloud resource, enables no external network
  access and uses no real credential, permission, connector or data.
- Gate 7 is recorded as accepted only by the owner authorization in Issue #44:
  `synthetic_non_personal` and
  `synthetic_personal_like_clearly_fictitious_non_routable` are the only
  allowed data classes; Tony is human approver, Stone is backup and escalation,
  Data Agent is technical validation owner and Developer Agent is
  implementation support. Gates 8 through 12 remain unauthorized.
- Gate 7 authorizes no real data, credential, permission, connector, endpoint,
  infrastructure, account, pilot, risk acceptance, merge, publication, release
  or deployment.
- Gate 8 is recorded as accepted only by the owner authorization in Issue #45:
  Stone is the human approver, Tony is backup and escalation, Developer Agent
  is technical owner, and CustomerService Agent plus Data Agent contribute
  evidence. Only deterministic synthetic runbook, degradation, recovery,
  incident-tabletop and support-flow validation is in scope. Gates 9 through 12
  remain unauthorized.
- Gate 8 authorizes no real monitoring, alerting, ticketing, incident,
  failover, backup/restore, support commitment, cloud resource, real data,
  credential, connector, pilot, risk acceptance, merge, publication, release
  or deployment. CT-2 RTO 240 minutes and RPO 60 minutes are design targets
  only.
- Evaluation is deterministic, does not mutate inputs and performs no external
  action.
- All repository regression tests and validators exit zero.

A pass proves only repository-contained local synthetic behavior. It does not authorize deployment,
accept a risk, assign an operational, support or risk-treatment owner, authorize
a pilot, declare production readiness, authorize release, permit merge, publish
or archive Stage 15, close Issue #40 or start Stage 16. The Gate 5 governance
owner contract grants no automatic merge, credential, permission, risk
acceptance, pilot, release or deployment authority.
The Gate 6 architecture and security record grants no cloud resource,
credential, real-data, connector, pilot, merge, publication, release or
deployment authority and is not production security acceptance or risk
acceptance.
The Gate 7 privacy and data record grants only the two named synthetic data
classes and performs no external action.
The Gate 8 operations record grants only the named synthetic validation scope
and performs no external action.
