# BUW AIOS Stage Registry

## Registry control

| Field | Value |
|---|---|
| Governance version | 1.1 |
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Source policy | `Governance/AIOS-Thread-Governance-v1.md` |
| Lifecycle | Planned → Executing → Reported → Archived |
| Roadmap | Stage 1 → Stage 9 |
| Last updated | 2026-07-20 |

This registry is the Single Source of Truth for current BUW AIOS Stage assignment and lifecycle status. Evidence links document execution; they do not replace the registry or grant archival authority.

## Registry rules

1. Every Stage has one stable Stage ID, one Parent Thread and no more than one active Execution Thread.
2. Only the Governance Thread may create, split, reassign, cancel, renumber or archive a Stage.
3. After authorization, the Execution Thread works continuously within scope until completion, a governance stop condition or an unrecoverable blocker.
4. An Execution Thread may move its Stage from Executing to Reported only by submitting the Mandatory Return.
5. Reported does not mean Archived. Archived requires explicit Governance Thread confirmation and archive evidence.
6. A blocker is recorded in the Notes / next gate column without inventing another lifecycle status.
7. Historical links and pre-v1.1 exceptions are preserved rather than rewritten.
8. Stage numbers 1 through 9 are frozen under governance v1.1 and may be changed only by the Governance Thread.

## Frozen Stage roadmap

| Stage | Stage ID | Name | Parent Thread | Single Execution Thread / evidence | Status | Return / archive evidence | Notes / next gate |
|---:|---|---|---|---|---|---|---|
| 1 | AG-01 | Agent Governance（智能体治理） | BUW AIOS Official Governance Thread | [Issue #1](https://github.com/tonybai0123456-png/hf-lht/issues/1) / [PR #2](https://github.com/tonybai0123456-png/hf-lht/pull/2) | Archived | PR #2 merged to `main` | Historical Stage accepted before v1.1 freeze. |
| 2 | PL-01 | Prompt Library（提示词库） | BUW AIOS Official Governance Thread | [Issue #3](https://github.com/tonybai0123456-png/hf-lht/issues/3) / [Draft PR #4](https://github.com/tonybai0123456-png/hf-lht/pull/4) | Reported | Draft PR #4 contains scope and validation return | Governance Thread review and archive decision pending. |
| 3 | RC-01 | Runtime Contract（运行时契约） | BUW AIOS Official Governance Thread | [Issue #5](https://github.com/tonybai0123456-png/hf-lht/issues/5) / [Draft PR #6](https://github.com/tonybai0123456-png/hf-lht/pull/6) | Reported | Draft PR #6 contains scope and synthetic-validation return | Dependency and Governance Thread review pending. |
| 4 | WL-01 | Workflow Library（工作流库） | BUW AIOS Official Governance Thread | [Issue #7](https://github.com/tonybai0123456-png/hf-lht/issues/7) / [Draft PR #8](https://github.com/tonybai0123456-png/hf-lht/pull/8) | Reported | Draft PR #8 contains scope and validation return | Dependency and Governance Thread review pending. |
| 5 | WS-01 | Workflow Schema（工作流模式） | BUW AIOS Official Governance Thread | [Issue #9](https://github.com/tonybai0123456-png/hf-lht/issues/9) / [Draft PR #10](https://github.com/tonybai0123456-png/hf-lht/pull/10) | Reported | Draft PR #10 and its evidence comment record schema validation | Governance Thread review pending; PR #10 remains untouched by Stage 7. |
| 6 | CH-01 | Controlled Harness（受控验证框架） | BUW AIOS Official Governance Thread | Historical combined execution in [Issue #9](https://github.com/tonybai0123456-png/hf-lht/issues/9) / [Draft PR #10](https://github.com/tonybai0123456-png/hf-lht/pull/10) | Reported | Draft PR #10 records synthetic-only harness evidence | Pre-freeze combined-execution exception; no new Stage may copy this pattern. |
| 7 | TG-01 | Project Governance Baseline / Thread Governance v1.1（项目治理基线／线程治理第 1.1 版） | BUW AIOS Official Governance Thread | [Issue #11](https://github.com/tonybai0123456-png/hf-lht/issues/11) / branch `agent/aios-thread-governance-v1` / [Draft PR #12](https://github.com/tonybai0123456-png/hf-lht/pull/12) | Reported | Issue #11, Draft PR #12 and governance files contain scope, safety boundary, validation and Mandatory Return evidence | Governance Thread must review the v1.1-aligned return and alone may confirm Archived. |
| 8 | RO-01 | Runtime Orchestrator（运行时编排器） | BUW AIOS Official Governance Thread | Not assigned | Planned | No execution return yet | Must not enter Executing until Stage 7 is accepted and a dedicated Issue and Execution Thread are assigned. |
| 9 | PR-01 | Production Readiness（生产就绪） | BUW AIOS Official Governance Thread | Not assigned | Planned | No execution return yet | Must remain Planned until prior governance gates, safety review and explicit human authorization are complete. |

## Pre-freeze exception record

PR #10 contains both Workflow Schema and Controlled Harness work. This register preserves that historical fact without modifying PR #10. Under frozen v1.1 governance, every new Stage must have its own registered execution assignment; combined historical execution does not grant permission for future combined Stages.

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
- Current status: Reported
- Completed scope:

### 证据链接

- Issue:
- Branch / commit:
- Draft PR:
- Files / checks:

### 阻塞项

- None, or list the exact decision, dependency or risk.

### 下一步

- Governance Thread reviews the return and either confirms Archived or sends the Stage back for scoped follow-up.

## Registry change log

| Date | Governance version | Change | Authority |
|---|---|---|---|
| 2026-07-20 | 1.0 draft | Initial Stage Registry created; historical Stages mapped; TG-01 entered Executing. | TG-01 Execution Thread |
| 2026-07-20 | 1.0 draft | TG-01 linked to Draft PR #12 and moved from Executing to Reported after Mandatory Return evidence was assembled. | TG-01 Execution Thread |
| 2026-07-20 | 1.1 | Aligned repository governance with the approved dual-thread model, continuous execution rule, Governance Dashboard and frozen Stage 1–9 roadmap; Stage 7 remains Reported pending governance acceptance. | BUW AIOS Official Governance Thread authorization / TG-01 Execution Thread implementation |