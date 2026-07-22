# BUW AIOS Stage Registry

## Registry control

| Field | Value |
|---|---|
| Governance version | 2.0 |
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Source policy | `Governance/AIOS-Thread-Governance-v2.md` |
| Historical policy | `Governance/AIOS-Thread-Governance-v1.md` (frozen v1.1; preserved unchanged) |
| Lifecycle | Planned → Executing → Reported → Reviewed → Archived |
| Roadmap | Stage 1 → Stage 9 |
| Publication status | Published through PR #12 on 2026-07-22 |
| Last updated | 2026-07-22 |

This registry is the Single Source of Truth for current BUW AIOS Stage assignment and lifecycle status. Evidence links document execution; they do not replace the registry or grant archival authority.

## Registry rules

1. Every Stage has one stable Stage ID, one Parent Thread and no more than one active Execution Thread.
2. Only the Governance Thread may create, split, reassign, cancel, renumber, review or archive a Stage.
3. After authorization, the Execution Thread works continuously within scope until completion, a governance stop condition or an unrecoverable blocker.
4. An Execution Thread may move its Stage from Executing to Reported only by submitting the Mandatory Return.
5. Reported does not mean Reviewed. Reviewed requires explicit human Governance Thread acceptance.
6. Reviewed does not mean merged, published or Archived. Archived requires a separate Governance Thread confirmation and archive evidence.
7. A blocker is recorded in the Notes / next gate column without inventing another lifecycle status.
8. Historical links and pre-v1.1 exceptions are preserved rather than rewritten.
9. Stage numbers 1 through 9 remain frozen under governance v2.0 and may be changed only by the Governance Thread.

## Frozen Stage roadmap

| Stage | Stage ID | Name | Parent Thread | Single Execution Thread / evidence | Status | Return / archive evidence | Notes / next gate |
|---:|---|---|---|---|---|---|---|
| 1 | AG-01 | Agent Governance（智能体治理） | BUW AIOS Official Governance Thread | [Issue #1](https://github.com/tonybai0123456-png/hf-lht/issues/1) / [PR #2](https://github.com/tonybai0123456-png/hf-lht/pull/2) | Archived | PR #2 merged to `main` | Historical Stage accepted before v1.1 freeze. |
| 2 | PL-01 | Prompt Library（提示词库） | BUW AIOS Official Governance Thread | [Issue #3](https://github.com/tonybai0123456-png/hf-lht/issues/3) / [PR #4](https://github.com/tonybai0123456-png/hf-lht/pull/4) | Archived | Published through PR #4 on 2026-07-22; validation return and human governance review passed on 2026-07-21. | Archived by the Governance Thread on 2026-07-22 under [Issue #14](https://github.com/tonybai0123456-png/hf-lht/issues/14) after verified publication and completed review; reopen only through a new Stage or approved governance-version change. |
| 3 | RC-01 | Runtime Contract（运行时契约） | BUW AIOS Official Governance Thread | [Issue #5](https://github.com/tonybai0123456-png/hf-lht/issues/5) / [PR #6](https://github.com/tonybai0123456-png/hf-lht/pull/6) | Archived | Published through PR #6 on 2026-07-22; synthetic-validation return and human governance review passed on 2026-07-21. | Archived by the Governance Thread on 2026-07-22 under [Issue #14](https://github.com/tonybai0123456-png/hf-lht/issues/14) after verified publication and completed review; reopen only through a new Stage or approved governance-version change. |
| 4 | WL-01 | Workflow Library（工作流库） | BUW AIOS Official Governance Thread | [Issue #7](https://github.com/tonybai0123456-png/hf-lht/issues/7) / [PR #8](https://github.com/tonybai0123456-png/hf-lht/pull/8) | Archived | Published through PR #8 on 2026-07-22; validation return and human governance re-review passed on 2026-07-22. | Archived by the Governance Thread on 2026-07-22 under [Issue #14](https://github.com/tonybai0123456-png/hf-lht/issues/14) after verified publication and completed re-review; reopen only through a new Stage or approved governance-version change. |
| 5 | WS-01 | Workflow Schema（工作流模式） | BUW AIOS Official Governance Thread | [Issue #9](https://github.com/tonybai0123456-png/hf-lht/issues/9) / [PR #10](https://github.com/tonybai0123456-png/hf-lht/pull/10) | Archived | Published through PR #10 on 2026-07-22; schema validation and human governance review passed. | Archived by the Governance Thread on 2026-07-22 under [Issue #14](https://github.com/tonybai0123456-png/hf-lht/issues/14) after verified publication and completed review; reopen only through a new Stage or approved governance-version change. |
| 6 | CH-01 | Controlled Harness（受控验证框架） | BUW AIOS Official Governance Thread | Historical combined execution in [Issue #9](https://github.com/tonybai0123456-png/hf-lht/issues/9) / [PR #10](https://github.com/tonybai0123456-png/hf-lht/pull/10) | Archived | Published through PR #10 on 2026-07-22; synthetic-only harness evidence and human governance review passed. | Archived by the Governance Thread on 2026-07-22 under [Issue #14](https://github.com/tonybai0123456-png/hf-lht/issues/14); the pre-freeze combined-execution exception is historical and must not be reused. |
| 7 | TG-01 | Thread Governance v2.0（线程治理第 2.0 版） | BUW AIOS Official Governance Thread | [Issue #11](https://github.com/tonybai0123456-png/hf-lht/issues/11) / branch `agent/aios-thread-governance-v1` / [Draft PR #12](https://github.com/tonybai0123456-png/hf-lht/pull/12) | Archived | Governance Thread accepted the Stage 7 technical result and approved the v2.0 migration update. | Archived by the Governance Thread on 2026-07-22 under [Issue #14](https://github.com/tonybai0123456-png/hf-lht/issues/14). Project Governance Baseline remains an unassigned backlog item in [Issue #13](https://github.com/tonybai0123456-png/hf-lht/issues/13) and is not part of TG-01. Stage 8 remains Planned. |
| 8 | RO-01 | Runtime Orchestrator（运行时编排器） | BUW AIOS Official Governance Thread | [Issue #16](https://github.com/tonybai0123456-png/hf-lht/issues/16) / Execution Thread `019f88ca-9d63-7e13-b1e0-b4db3b6a65df` / branch `feat/aios-runtime-orchestrator-v1` / [Draft PR #17](https://github.com/tonybai0123456-png/hf-lht/pull/17) | Reported | [Runtime CI run #1](https://github.com/tonybai0123456-png/hf-lht/actions/runs/29902843242) and [Schema CI run #30](https://github.com/tonybai0123456-png/hf-lht/actions/runs/29902843339) passed on the initial Draft PR head. | Mandatory Return assembled with no implementation blocker; Draft PR remains unmerged. Next gate: human Governance Thread review for Reviewed or scoped follow-up. |
| 9 | PR-01 | Production Readiness（生产就绪） | BUW AIOS Official Governance Thread | Not assigned | Planned | No execution return yet | Must remain Planned until prior governance gates, safety review and explicit human authorization are complete. |

## Pre-freeze exception record

PR #10 contains both Workflow Schema and Controlled Harness work. This register preserves that historical fact without modifying PR #10. Under governance v2.0, every new Stage must have its own registered execution assignment; combined historical execution does not grant permission for future combined Stages.

## Governance Dashboard minimum fields

The Governance Thread dashboard must maintain at least:

- current Stage and lifecycle status;
- active Execution Thread;
- Issue, PR and CI evidence;
- blockers and risks;
- human approvals pending;
- next governance action.

The dashboard is a governance summary. It does not replace this registry or GitHub execution evidence.

## Mandatory Return template

### 本次完成

- Stage number / Stage ID:
- Current status: Reported (the Execution Thread may not self-declare Reviewed)
- Completed scope:

### 证据链接

- Issue:
- Branch / commit:
- Draft PR:
- Files / checks:

### 阻塞项

- None, or list the exact decision, dependency or risk.

### 下一步

- Governance Thread reviews the return and either confirms Reviewed or sends the Stage back for scoped follow-up. Archival is a later, separate decision.

## Registry change log

| Date | Governance version | Change | Authority |
|---|---|---|---|
| 2026-07-20 | 1.0 draft | Initial Stage Registry created; historical Stages mapped; TG-01 entered Executing. | TG-01 Execution Thread |
| 2026-07-20 | 1.0 draft | TG-01 linked to Draft PR #12 and moved from Executing to Reported after Mandatory Return evidence was assembled. | TG-01 Execution Thread |
| 2026-07-20 | 1.1 | Aligned repository governance with the approved dual-thread model, continuous execution rule, Governance Dashboard and frozen Stage 1–9 roadmap; Stage 7 remains Reported pending governance acceptance. | BUW AIOS Official Governance Thread authorization / TG-01 Execution Thread implementation |
| 2026-07-22 | 2.0 upgrade draft | Added Reviewed to the lifecycle; recorded Stages 2–7 as Reviewed under explicit Governance Thread decisions; preserved Stage 1 as Archived and Stages 8–9 as Planned. | BUW AIOS Official Governance Thread authorization / TG-01 Execution Thread implementation |
| 2026-07-22 | 2.0 upgrade draft | Clarified frozen Stage 7 as TG-01 Thread Governance v2.0 only; removed the misleading combined Project Governance name and recorded Issue #13 as unassigned backlog pending a separate Stage decision. | BUW AIOS Official Governance Thread human review |
| 2026-07-22 | 2.0 | Published Governance v2.0 through authorized PR #12; Stage 7 remains Reviewed and is not Archived; Stage 8 remains Planned. | BUW AIOS Official Governance Thread authorization / TG-01 Execution Thread publication |
| 2026-07-22 | 2.0 | Published Stage 2 Prompt Library through authorized PR #4; Stage 2 remains Reviewed and is not Archived; PRs #6, #8 and #10 remain Draft and Stage 8 remains Planned. | BUW AIOS Official Governance Thread authorization / PL-01 Execution Thread publication |
| 2026-07-22 | 2.0 | Published Stage 3 Runtime Contract through authorized PR #6; Stage 3 remains Reviewed and is not Archived; PRs #8 and #10 remain Draft and Stage 8 remains Planned. | BUW AIOS Official Governance Thread authorization / RC-01 Execution Thread publication |
| 2026-07-22 | 2.0 | Published Stage 4 Workflow Library through authorized PR #8; Stage 4 remains Reviewed and is not Archived; PR #10 remains Draft and Stage 8 remains Planned. | BUW AIOS Official Governance Thread authorization / WL-01 Execution Thread publication |
| 2026-07-22 | 2.0 | Published Stages 5 and 6 Workflow Schema and Controlled Harness through authorized PR #10; both Stages remain Reviewed and are not Archived; the historical combined-execution exception is preserved and Stage 8 remains Planned. | BUW AIOS Official Governance Thread authorization / WS-01 and CH-01 Execution Thread publication |
| 2026-07-22 | 2.0 | Archived Stages 2–7 after verified publication, completed human review and separate Governance Thread authorization; accepted the bundled publication authorization as covering non-destructive synchronization, retargeting to `main` and revalidation; kept Stages 8–9 Planned and Issue #13 open and unassigned. | BUW AIOS Official Governance Thread |
| 2026-07-22 | 2.0 | Assigned Stage 8 / RO-01 through Issue #16 to the single dedicated Execution Thread `019f88ca-9d63-7e13-b1e0-b4db3b6a65df`; authorized branch `feat/aios-runtime-orchestrator-v1`; moved Stage 8 from Planned to Executing under approved 方案 A. | BUW AIOS Official Governance Thread authorization / RO-01 Execution Thread implementation |
| 2026-07-22 | 2.0 | Submitted the Stage 8 / RO-01 Mandatory Return through Draft PR #17 after the Runtime and Schema CI checks passed; moved Stage 8 from Executing to Reported without self-declaring Reviewed. | RO-01 Execution Thread |
