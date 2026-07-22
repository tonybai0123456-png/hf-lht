# Stage 9 / PG-01 Project Governance Baseline Design

## Decision and provenance

Issue #13 authorizes one documentation-only Project Governance Baseline on the
published Thread Governance v2.1 baseline. The historical branch
`agent/aios-project-governance-baseline-v1` was inspected as non-authoritative
prior work. Useful concepts were adapted, while its obsolete Stage 7, v1 and old
base assumptions were not cherry-picked or used to rewrite history.

The implementation branch is based on main commit
`dcc9b0990235b03b3a83f6e92d354fe2d5d0c7eb`, which already records Stage 9 as
Executing and Stage 10 as Planned.

## Design

The project layer contains two controlled documents:

1. `AIOS-Project-Governance-Baseline-v1.md` defines identity, authority,
   boundaries, lifecycle, artifact classes, change control and fail-closed rules.
2. `AIOS-Project-Registry.md` contains exactly one initial `BUW-AIOS` entry and
   records current project identity/status without replacing the Stage Registry.

The source hierarchy follows Thread Governance v2.1. The candidate baseline is
not frozen or published by execution. Its project lifecycle is deliberately
separate from the Stage lifecycle, and all high-risk actions retain human gates.

## Validation design

Standard-library unit tests read repository files and check positive invariants
and negative interpretations. CI has read-only repository permissions and no
credentials persistence. No synthetic payload is needed because the governed
objects are documentation and registry text; no real business data is accessed.

## Non-goals

No merge, publication, deployment, permission change, production access, real
data, external write, Stage 10 work, new runtime capability or architecture
expansion is included.
