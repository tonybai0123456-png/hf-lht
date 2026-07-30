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
  `b27614ba2ebebb772888c3a4b1ff3d829b47532e`; the remaining eight human gates
  stay required and unauthorized.
- Evaluation is deterministic, does not mutate inputs and performs no external
  action.
- All repository regression tests and validators exit zero.

A pass proves only repository-contained local synthetic behavior. It does not authorize deployment,
accept a risk, assign a real owner, authorize a pilot, declare production
readiness, authorize release, permit merge, publish or archive Stage 15, close
Issue #40 or start Stage 16.
