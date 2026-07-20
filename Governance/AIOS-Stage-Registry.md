# BUW AIOS Stage Registry

## Registry control

| Field | Value |
|---|---|
| Governance version | 1.0 |
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Source policy | `Governance/AIOS-Thread-Governance-v1.md` |
| Lifecycle | Planned → Executing → Reported → Archived |
| Last updated | 2026-07-20 |

This registry is the Single Source of Truth for current BUW AIOS Stage assignment and lifecycle status. Evidence links document execution; they do not replace the registry or grant archival authority.

## Registry rules

1. Every Stage has one stable Stage ID, one Parent Thread and no more than one active Execution Thread.
2. Only the Governance Thread may create, split, reassign, cancel or archive a Stage.
3. An Execution Thread may move its Stage from Executing to Reported only by submitting the Mandatory Return.
4. Reported does not mean Archived. Archived requires explicit Governance Thread confirmation and archive evidence.
5. A blocker is recorded in the Notes / next gate column without inventing another lifecycle status.
6. Historical links and pre-v1.0 exceptions are preserved rather than rewritten.

## Stage register

| Stage ID | Stage | Parent Thread | Single Execution Thread / evidence | Status | Return / archive evidence | Notes / next gate |
|---|---|---|---|---|---|---|
| AG-01 | Agent Governance（智能体治理） | BUW AIOS Official Governance Thread | [Issue #1](https://github.com/tonybai0123456-png/hf-lht/issues/1) / [PR #2](https://github.com/tonybai0123456-png/hf-lht/pull/2) | Archived | PR #2 merged to `main` | Historical Stage accepted before v1.0 freeze. |
| PL-01 | Prompt Library（提示词库） | BUW AIOS Official Governance Thread | [Issue #3](https://github.com/tonybai0123456-png/hf-lht/issues/3) / [Draft PR #4](https://github.com/tonybai0123456-png/hf-lht/pull/4) | Reported | Draft PR #4 contains scope and validation return | Governance Thread review and archive decision pending. |
| RC-01 | Runtime Contract（运行时契约） | BUW AIOS Official Governance Thread | [Issue #5](https://github.com/tonybai0123456-png/hf-lht/issues/5) / [Draft PR #6](https://github.com/tonybai0123456-png/hf-lht/pull/6) | Reported | Draft PR #6 contains scope and synthetic-validation return | Dependency and Governance Thread review pending. |
| WL-01 | Workflow Library（工作流库） | BUW AIOS Official Governance Thread | [Issue #7](https://github.com/tonybai0123456-png/hf-lht/issues/7) / [Draft PR #8](https://github.com/tonybai0123456-png/hf-lht/pull/8) | Reported | Draft PR #8 contains scope and validation return | Dependency and Governance Thread review pending. |
| WS-01 | Workflow Schema（工作流模式） | BUW AIOS Official Governance Thread | [Issue #9](https://github.com/tonybai0123456-png/hf-lht/issues/9) / [Draft PR #10](https://github.com/tonybai0123456-png/hf-lht/pull/10) | Reported | Draft PR #10 and its evidence comment record schema validation | Governance Thread review pending; PR #10 remains untouched by TG-01. |
| CH-01 | Controlled Harness（受控验证框架） | BUW AIOS Official Governance Thread | Historical combined execution in [Issue #9](https://github.com/tonybai0123456-png/hf-lht/issues/9) / [Draft PR #10](https://github.com/tonybai0123456-png/hf-lht/pull/10) | Reported | Draft PR #10 records synthetic-only harness evidence | Pre-freeze combined-execution exception; no new Stage may copy this pattern. |
| RO-01 | Runtime Orchestrator（运行时编排器） | BUW AIOS Official Governance Thread | Not assigned | Planned | No execution return yet | Governance Thread must create a dedicated Issue and assign one Execution Thread before Executing. |
| PR-01 | Production Readiness（生产就绪） | BUW AIOS Official Governance Thread | Not assigned | Planned | No execution return yet | Must remain Planned until prior governance gates, safety review and explicit human authorization are complete. |
| TG-01 | Thread Governance v1.0（线程治理第 1.0 版） | BUW AIOS Official Governance Thread | [Issue #11](https://github.com/tonybai0123456-png/hf-lht/issues/11) / branch `agent/aios-thread-governance-v1` / [Draft PR #12](https://github.com/tonybai0123456-png/hf-lht/pull/12) | Reported | Issue #11 and Draft PR #12 contain scope, safety boundary, validation and return evidence | Governance Thread must review the Mandatory Return and alone may confirm Archived. |

## Pre-freeze exception record

PR #10 contains both Workflow Schema and Controlled Harness work. This register preserves that historical fact without modifying PR #10. Under frozen v1.0 governance, every new Stage must have its own registered execution assignment; combined historical execution does not grant permission for future combined Stages.

## Mandatory Return template

### 本次完成

- Stage ID:
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
| 2026-07-20 | 1.0 | Initial Stage Registry created; historical stages mapped; TG-01 entered Executing. | BUW AIOS Official Governance Thread |
| 2026-07-20 | 1.0 | TG-01 linked to Draft PR #12 and moved from Executing to Reported after Mandatory Return evidence was assembled. | TG-01 Execution Thread |
