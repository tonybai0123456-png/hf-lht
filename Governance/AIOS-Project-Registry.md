# BUW AIOS Project Registry

## Registry control

| Field | Value |
|---|---|
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Effective Thread Governance | `Governance/AIOS-Thread-Governance-v2.2.md` |
| Published Project policy | `Governance/AIOS-Project-Governance-Baseline-v1.md` (v1.0) |
| Canonical repository | `tonybai0123456-png/hf-lht` |
| Initial scope | Exactly one governed project: `BUW-AIOS` |
| Last updated | 2026-07-23 |

This registry is the controlled source for project identity and project status.
It does not replace `Governance/AIOS-Stage-Registry.md`, which controls Stage
assignment and Stage lifecycle. The published baseline, Thread Governance v2.2 and the Stage Registry form the
controlled project source chain.

## Registered projects

| Project ID | Project name | Company boundary | Brand boundary | Project owner | Governance Thread | Canonical repository | Policy / Stage Registry | Project status | Active Stage | Review date / evidence | Next gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BUW-AIOS | BUW AIOS | 汇沣电商; 六合通 is a separate company and excluded | BUW only; PC is an independent brand and excluded | Tony | BUW AIOS Official Governance Thread | `tonybai0123456-png/hf-lht` | `Governance/AIOS-Project-Governance-Baseline-v1.md` / `Governance/AIOS-Stage-Registry.md` | Active | Stage 13 Archived / Stage 14 Archived / no active execution Stage | 2026-07-23 / Issue #36 / exact reviewed implementation head `7184d91797128788decc734ef80f9d07114fcc84` / published through PR #37 at squash merge `142804f22396dc6f094327a0dffefb7da7593168` / publication alignment `8d6e2aff171e28e4a789454e677da234bc0f49fb` / 92 repository tests / post-merge validators and tree parity passed / `needs_human_governance` / Mandatory Return accepted | Human Governance Thread archive decision passed; all Stages 1–14 are Archived and no active execution Stage exists. Any future Stage or real pilot requires a separate governance decision; no pilot authority, real owner, real data/system/connector, external action, risk acceptance or release authority |

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
| 2026-07-22 | Activated Stage 12 / DG-01 under confirmed 方案 B through Issue #28, one Execution Thread and the authorized feature branch; implementation is synthetic/read-only and Stages 13–14 remain Planned. | BUW AIOS Official Governance Thread / Issue #28 |
| 2026-07-22 | Recorded Stage 12 as Reported after the synthetic policy model and deterministic verification passed; retained all legal, real-data, production, owner, risk, merge, archive and Stage 13 gates. | DG-01 Mandatory Return / Issue #28 |
| 2026-07-22 | Accepted the corrected Stage 12 / DG-01 result as Reviewed after independent finding replay, 14/14 content comparison, 11/11 targeted tests, 61/61 repository tests and five final-head workflows passed. | BUW AIOS Official Governance Thread / PR #29 / Issue #28 |
| 2026-07-22 | Published Stage 12 through PR #29 at `454a719`, passed post-merge validation and archived DG-01 through Issue #30; no active Execution Stage exists and Stage 13 remains Planned and unassigned. | BUW AIOS Official Governance Thread / PR #29 / Issues #28 and #30 |
| 2026-07-22 | Activated Stage 13 / OR-01 through Issue #32, one Execution Thread and the authorized feature branch; execution is synthetic, prepare-only and read-only, while Stage 14 remains Planned and unassigned. | BUW AIOS Official Governance Thread / Issue #32 |
| 2026-07-22 | Recorded Stage 13 as Reported after preparing the synthetic operational-resilience policy, model, risk/control mapping, fixture and deterministic validation; retained all production, operational action, owner, risk, merge, archive and Stage 14 gates. | OR-01 Mandatory Return / Issue #32 / Draft PR #33; exact final-head CI is recorded in the Issue return |
| 2026-07-22 | Human Governance final re-review passed Stage 13 at corrected head `327d9e9`; published the reviewed package through PR #33 at `7b16a5c`, passed post-merge validation and archived OR-01 through Issue #34; Stage 14 remains Planned and unassigned. | BUW AIOS Official Governance Thread / PR #33 / Issues #32 and #34 |
| 2026-07-23 | Activated the Stage 14 / PS-01 first design gate under 方案 A through Issue #36, one Execution Thread and the authorized branch; current work is limited to the written specification and awaits independent Governance Thread approval before any implementation plan. | BUW AIOS Official Governance Thread / Issue #36 |
| 2026-07-23 | Recorded independent approval of the Stage 14 written specification at exact head `c312db694afc40b5ec268f577c6c05a664b98eef` and opened the implementation-plan tranche only; Stage 14 remains Executing and the plan awaits independent human approval. | BUW AIOS Official Governance Thread / Issue #36 / Draft PR #37 |
| 2026-07-23 | Recorded independent review of implementation-plan head `e376726d51863e22324d164ddf8c8a33f84937cd`: CI and frozen boundaries passed, while actual-content corrections remained required; Stage 14 stays Executing and the corrected plan awaits independent human approval. | BUW AIOS Official Governance Thread / Issue #36 / Draft PR #37 |
| 2026-07-23 | Reported Stage 14 implementation evidence head `d0fac2e21266c6d9a815f121a409436bea166ebf` and submitted the Mandatory Return; retained Stage 13 Archived, Stage 10 BLOCKED / NO-GO and every real-pilot human gate. | PS-01 Execution Thread / Issue #36 / Draft PR #37 |
| 2026-07-23 | Human Governance Thread review passed Stage 14 / PS-01 at exact implementation head `7184d91797128788decc734ef80f9d07114fcc84`; accepted the Mandatory Return and its two narrow execution interpretations while preserving Draft/unmerged status and every real-pilot human gate. | BUW AIOS Official Governance Thread / Issue #36 / Draft PR #37 |
| 2026-07-23 | Published Stage 14 / PS-01 through authorized squash merge of PR #37 at `142804f`; post-merge tests, validators, compilation and tree parity passed. Stage 14 remains Reviewed and every archive and real-pilot gate remains separate. | BUW AIOS Official Governance Thread / PR #37 / Issue #36 |
| 2026-07-23 | Archived Stage 14 / PS-01 after verified review, publication and post-merge validation; all Stages 1–14 are Archived and no active execution Stage exists. Any future Stage or real pilot remains separately governed. | BUW AIOS Official Governance Thread / Issue #36 |
