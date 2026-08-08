# Stage 15 Local Isolated Python Rehearsal Validation

## Scope

This guide validates one BUW-only, repository-controlled, local isolated
Python rehearsal. It uses no network during the rehearsal, no credentials,
no online dependency installation, no real data, no real participants, no
connectors and no infrastructure.

The maximum positive result is:

`local_python_test_deployment_rehearsal_passed_not_cloud_proof`

That result is local technical evidence only. It does not prove cloud,
staging, pilot, production, release or formal deployment capability.

## Authorization evidence

- Plan commit: `2d3d186d1930d18bfd0a8d604240694f11e1af6c`
- Plan tree: `6b26f4f67907dcba68698949c6c303a4b8d9e5f0`
- Issue #51 owner decision:
  `https://github.com/tonybai0123456-png/hf-lht/issues/51#issuecomment-5211821955`
- Branch: `gov/aios-stage15-nonproduction-readiness-design`
- Pull request: PR #41, which remains Draft / open / unmerged.

## TDD evidence

The focused public-interface test was run before implementation and failed
with one expected assertion: the rehearsal runner did not exist. This is the
recorded RED state. The GREEN sequence must use the already available isolated
repository Python environment and must not install a package.

## Local commands

From the repository root, with the existing local isolated interpreter:

```bash
.venv/bin/python -m unittest Tests.test_stage15_local_python_rehearsal -v
.venv/bin/python Tests/validate_aios_stage15_local_python_rehearsal.py
.venv/bin/python -m unittest Tests.test_project_governance -v
.venv/bin/python -m unittest discover -s Tests -p 'test_*.py' -v
.venv/bin/python -X pycache_prefix=/private/tmp/buw-stage15-pycache -m compileall -q Runtime Tests
git diff --check
```

If PyYAML is unavailable, return
`local_python_test_deployment_rehearsal_blocked` with reason
`LOCAL_DEPENDENCY_UNAVAILABLE`. Do not download it and do not modify system
Python.

## One clean-export rehearsal

The exact candidate must first be committed and the repository must be clean.
Invoke the runner with a minimal outer environment that contains no token,
secret, credential, proxy, cloud or connector variable:

```bash
env -i PATH="$PATH" LANG="C.UTF-8" LC_ALL="C.UTF-8" \
  .venv/bin/python Runtime/stage15_local_python_rehearsal.py \
  --repository "$PWD" --commit "<exact-40-character-local-commit>"
```

The runner exports only the local Git object, activates a task-local socket
guard, executes the controlled synthetic workflow twice, compares normalized
output, validates the closed receipt and removes only its marked temporary
directories.

The accepted implementation must also:

- lock every Git and Python command to an exact argument shape, including
  denial of `git archive --remote` and additional status arguments;
- write operation-category-only network attempts to a task-local append-only
  log and deny the run even when child code catches the network exception;
- compute the receipt material scan from the exact contract, fixture,
  dedicated workflow, dedicated input and runtime assets;
- use only `SYNTHETIC-ROLE-*` and `SYNTHETIC-STORE-*` operational identifiers.

The pre-acceptance candidate `e87f7fdc7ae235d365afc8f44816c5854877f1b2`
was stopped by Stone and is not valid rehearsal evidence because it did not
yet satisfy these four requirements. It must not be cited as a passed run.

## Executed run evidence

- Run ID: `STAGE15-LOCAL-33e2216976b7`
- Source commit: `33e2216976b73ebaff4368ca8b8d5dc206ebf894`
- Source tree: `eff75180da120fa7deffdd15b1daa2a13bcb8ab5`
- Result: `local_python_test_deployment_rehearsal_passed_not_cloud_proof`
- Receipt: `Governance/AIOS-Stage15-Local-Python-Rehearsal-Receipt-v1.json`
- Receipt SHA-256:
  `2dae30bc8444d5ffb2b4b59e5df0c419921b40a5b4385d577c333c964f66b261`
- Candidate inventory SHA-256:
  `bfabad910aa9efe738732650dc7486de6ce35af37a2a00efa559a11b96a07c67`
- Normalized smoke SHA-256:
  `b6eed5c9d6c8e388bc4921a390a80d51d5702bf1f0ab57e326573b8afd1c1df6`
- Fixture SHA-256:
  `4e4d00d15ead4a45e5dd1c1c6a56dba7a62f5053d431f962ae1842878e1bcaec`
- Computed material findings: all false.
- Recorded network attempts: `[]`.
- External actions performed: `[]`.
- Cleanup: execution and bytecode directories removed; repository unchanged.

The run used CPython 3.9.6 and the already-present PyYAML 6.0.3. No package
installation was performed. This is local technical evidence only, not cloud,
staging, real-pilot, release, production or deployment proof.

## Required readback

- Receipt validates with no additional fields.
- Company is exactly 汇沣电商 and brand exactly BUW.
- PC and 六合通 remain excluded.
- Stage 10 remains `BLOCKED / NO-GO`.
- PR-RISK-001 through PR-RISK-010 remain `open_blocked_unaccepted`.
- PR #41 remains Draft / open / unmerged.
- All pilot, production, release, deployment and risk-acceptance flags are
  false.
- `external_actions_performed=[]`.
- Cleanup booleans are verified true except
  `evidence_directory_preserved=false`.

Passing this validation must never be interpreted as permission to mark the
PR Ready, merge, publish, archive, close an Issue, accept risk, start a real
pilot, create infrastructure, release or deploy.
