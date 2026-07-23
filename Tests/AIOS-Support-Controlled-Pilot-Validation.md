# AIOS Support Controlled Pilot Validation

Run from repository root:

    python3 -m unittest Tests.test_support_controlled_pilot -v
    python3 Tests/validate_aios_support_controlled_pilot.py
    python3 -m unittest discover -s Tests -p 'test_*.py' -v
    python3 -m unittest Tests.test_project_governance -v
    python3 Tests/validate_aios_operational_resilience.py
    python3 Tests/validate_aios_workflow_schema.py
    python3 -m compileall Tests
    git diff --check

Expected focused result: every adversarial case is denied; the sole otherwise-valid
fixture returns needs_human_governance; external_actions_performed is empty.

Expected repository result: every command exits 0. Compare the Stage 10–13 canonical
assets against the approved starting head and require an empty diff. A pass proves
only deterministic repository-controlled synthetic contract behavior.
needs_human_governance proves no pilot authority. It proves no real support
capability, risk acceptance, owner appointment, release or pilot readiness.
