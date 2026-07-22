# BUW AIOS Project Registry

## Registry control

| Field | Value |
|---|---|
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Effective Thread Governance | `Governance/AIOS-Thread-Governance-v2.2.md` |
| Published Project policy | `Governance/AIOS-Project-Governance-Baseline-v1.md` (v1.0) |
| Canonical repository | `tonybai0123456-png/hf-lht` |
| Initial scope | Exactly one governed project: `BUW-AIOS` |
| Last updated | 2026-07-22 |

This registry is the controlled source for project identity and project status.
It does not replace `Governance/AIOS-Stage-Registry.md`, which controls Stage
assignment and Stage lifecycle. The published baseline, Thread Governance v2.2 and the Stage Registry form the
controlled project source chain.

## Registered projects

| Project ID | Project name | Company boundary | Brand boundary | Project owner | Governance Thread | Canonical repository | Policy / Stage Registry | Project status | Active Stage | Review date / evidence | Next gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BUW-AIOS | BUW AIOS | 汇沣电商; the company is not collapsed into this project; 六合通 is a separate company and excluded | BUW only; PC is an independent brand and excluded | Tony | BUW AIOS Official Governance Thread | `tonybai0123456-png/hf-lht` | `Governance/AIOS-Project-Governance-Baseline-v1.md` / `Governance/AIOS-Stage-Registry.md` | Active | No active Execution Stage; Stage 12 / DG-01 remains Planned and unassigned | 2026-07-22 / PR #26 merged at `7759b16`; all 15 files matched reviewed head; Stage 11 archived | Separate Governance Thread authorization is required to start Stage 12; production, real data, permissions, external writes, owner assignment, risk acceptance, pilot and release remain unauthorized |

## Registry rules

1. Project IDs are unique and immutable.
2. The Governance Thread alone may create, split, rename, suspend or archive an entry.
3. Every material field update requires a linked governance decision and evidence.
4. Missing or conflicting evidence must fail closed; preserve the truthful status.
5. Project status does not replace Stage status, and this registry does not
   authorize an Execution Thread.
6. BUW, PC, 汇沣电商 and 六合通 remain distinct at brand and company level.
7. GitHub artifacts and ChatGPT Projects are working context only unless promoted
   through the controlled governance path.

## Change log

| Date | Change | Authority / evidence |
|---|---|---|
| 2026-07-22 | Created the initial registry with exactly one `BUW-AIOS` entry for Stage 9 review; no additional project was inferred or registered. | Issue #13 / PG-01 Execution Thread; pending Governance Thread review |
| 2026-07-22 | Recorded Stage 9 as Reported after the independent Draft PR and both required CI workflows passed; project status remains Active and no publication or archival is inferred. | Draft PR #20 / PG-01 Mandatory Return |
| 2026-07-22 | Published Project Governance Baseline v1.0 through PR #20 at `62b2aaa`, archived Stage 9 after post-merge verification, and activated Stage 10 / PR-01 under Issue #21 with assessment-only boundaries. | BUW AIOS Official Governance Thread |
| 2026-07-22 | Recorded Stage 10 as Reported after Draft PR #23 and the required readiness and regression CI passed; retained the BLOCKED / NO-GO assessment recommendation and inferred no production or release authority. | PR-01 Mandatory Return |
| 2026-07-22 | Accepted the Stage 10 prepare-only assessment as Reviewed while preserving `BLOCKED / NO-GO`; no production, pilot, risk acceptance, release, merge or archive authority was granted. | BUW AIOS Official Governance Thread / PR #23 |
| 2026-07-22 | Published and archived Stage 10 without changing its `BLOCKED / NO-GO` conclusion; activated Stage 11 / AF-01 through Issue #24 under governance v2.2 while Stages 12–14 remain Planned. | BUW AIOS Official Governance Thread / PR #23 / Issue #24 |
| 2026-07-22 | Recorded Stage 11 as Reported after Draft PR #26 and its foundations and Runtime CI passed; retained design-only boundaries and inferred no review, production, risk acceptance, pilot, release, merge or archive authority. | AF-01 Mandatory Return / Draft PR #26 |
| 2026-07-22 | Accepted Stage 11 / AF-01 as Reviewed after independent content, boundary, targeted/full-test and four-workflow verification; preserved Draft/unmerged status and separate publication, archive and Stage 12 gates. | BUW AIOS Official Governance Thread / Draft PR #26 |
| 2026-07-22 | Published Stage 11 through PR #26 at `7759b16`, confirmed all 15 files matched the reviewed head, and archived AF-01; no active Execution Stage exists and Stage 12 remains Planned and unassigned. | BUW AIOS Official Governance Thread / PR #26 / Issue #24 |
