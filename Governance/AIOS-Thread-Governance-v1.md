# BUW AIOS Thread Governance v1.1

## 1. Document control

| Field | Value |
|---|---|
| Governance version | 1.1 |
| Status | Frozen |
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Repository | `tonybai0123456-png/hf-lht` |
| Stage control surface | `Governance/AIOS-Stage-Registry.md` |
| Effective scope | BUW AIOS Stage planning, execution-thread assignment, continuous execution, return reporting and archival |
| Approved on | 2026-07-20 |

This document governs work coordination. It does not authorize deployment, production access, permission changes, real-business-data access, external writes or any other high-risk action.

## 2. Governance precedes tools（治理先于工具）

No tool, Agent, ChatGPT Project, Issue, branch, pull request, workflow, harness, orchestrator or automation may define its own governance authority.

Before work starts, governance must establish:

1. the Stage and intended business outcome;
2. the Governance Thread and required Parent Thread;
3. the one permitted Execution Thread;
4. scope, exclusions, approval boundary, acceptance evidence and return format;
5. the initial Stage status in the Stage Registry.

Tools execute approved work. They do not create policy, expand scope, approve risk, declare archival or replace human governance judgment.

## 3. Single Governance Authority（唯一治理权威）

The **BUW AIOS Official Governance Thread** is the Single Governance Authority for this governance version. Only that Governance Thread may:

- create, split, sequence, suspend or cancel a Stage;
- assign or replace a Stage's Execution Thread;
- approve a Stage moving from Reported to Archived;
- resolve conflicts between execution evidence and governance records;
- freeze a governance version or authorize a version upgrade;
- authorize entry into a new Stage.

An Execution Thread, GitHub Issue, Draft PR, Agent, Project, automation or tool output may supply evidence and recommendations, but none of them may self-declare governance authority.

## 4. Dual-thread operating model（双线程工作模式）

### 4.1 Governance Thread（治理线程）

The Governance Thread owns **what, why and whether to approve**. Its responsibilities are:

- governance rules and versioning;
- architecture and roadmap decisions;
- Stage definition, sequencing and authorization;
- risk, exception and human-approval decisions;
- review of Execution Reports;
- Governance Dashboard maintenance;
- lifecycle confirmation from Reported to Archived.

The Governance Thread does not perform routine implementation, code changes, tests, CI maintenance or PR implementation work.

### 4.2 Execution Thread（执行线程）

The Execution Thread owns **how to implement and validate** one authorized Stage. Its responsibilities are:

- repository implementation and documentation;
- tests and CI;
- Issue and Draft PR maintenance;
- evidence capture;
- correction of ordinary technical defects;
- Mandatory Return at completion or escalation.

The Execution Thread must not change governance rules, expand Stage scope, approve high-risk actions, merge without authorization, deploy to production or use real business data outside an explicitly approved boundary.

### 4.3 Parent Thread Required（必须指定父线程）

Every Execution Thread must identify its Parent Governance Thread before entering Executing. The parent must be recorded in the Stage Registry and repeated in the related GitHub Issue or PR description.

If the Parent Thread is absent, ambiguous or points to an unapproved authority, the Stage must not enter Executing. Ordinary work notes, Projects and tool sessions are not substitutes for the required parent relationship.

### 4.4 One Stage, one Execution Thread

At any time, one Stage may have only one active Execution Thread. Parallel Agents or tools may work inside that thread's authorized scope, but they do not become independent execution authorities.

A second Execution Thread may be assigned only after the Governance Thread records the reason, closes or supersedes the prior assignment and updates the Stage Registry. Splitting work requires separate Stage IDs and separate execution assignments.

The Workflow Schema and Controlled Harness work recorded under PR #10 is a pre-freeze combined-execution exception. It is preserved as historical evidence and must not be treated as a reusable precedent after v1.1 is frozen.

### 4.5 Continuous execution rule（持续执行规则）

After a Stage is authorized, its Execution Thread continues working within scope without requesting permission for each ordinary implementation step.

The Execution Thread pauses and returns to governance only when one of these conditions occurs:

1. human approval is required;
2. a material architecture conflict is found;
3. the approved scope must expand;
4. production data, external writes, deployment, permissions, payments, deletion or large-scale outbound communication would be involved;
5. an unrecoverable blocker is reached;
6. the Stage is complete.

Ordinary test failures, reversible defects and routine implementation choices are handled inside the Execution Thread.

## 5. Stage lifecycle

The only governance lifecycle is:

**Planned（已计划） → Executing（执行中） → Reported（已汇报） → Archived（已归档）**

| Status | Meaning | Entry requirement | Exit authority |
|---|---|---|---|
| Planned | Stage is defined but execution has not started. | Stage ID, scope, Parent Thread, acceptance evidence and intended execution assignment are registered. | Governance Thread authorizes Executing. |
| Executing | The one assigned Execution Thread is working continuously within scope. | Execution Thread and evidence location are registered; safety and approval boundaries are explicit. | Execution Thread submits Mandatory Return and marks Reported. |
| Reported | Execution has returned its result and evidence; governance acceptance is pending. | Mandatory Return is complete and evidence links are accessible. | Governance Thread alone confirms Archived or returns the Stage for further work. |
| Archived | Governance has accepted the return and closed the Stage. | Governance decision and archive evidence are recorded in the Stage Registry. | A new Stage or approved governance-version change is required to reopen work. |

Status movement must be recorded in the Stage Registry. A blocker does not create an extra lifecycle state: record the blocker in the Stage row and keep the truthful current status. Statuses may not be skipped, backdated or inferred from tool activity alone.

## 6. Mandatory Return（强制回归汇报）

Before an Execution Thread stops, hands off or requests archival, it must return to the Parent Governance Thread with these four headings:

1. **本次完成** — exact scope completed and current Stage status;
2. **证据链接** — Issue, branch, Draft PR, files, checks and other reviewable evidence;
3. **阻塞项** — unresolved dependency, decision, risk or `无`;
4. **下一步** — the single next governance action and its owner.

The Execution Thread must set the Stage to Reported after this return. It must not claim Archived. Missing evidence, inaccessible links, unexplained scope drift or an incomplete return prevents archival.

## 7. Single Source of Truth（唯一事实源）

The authoritative control chain is:

1. the latest effective frozen governance document approved by the Governance Thread;
2. `Governance/AIOS-Stage-Registry.md` for current Stage assignment and lifecycle status;
3. linked GitHub Issues, branches, commits and PRs for execution evidence;
4. ChatGPT Projects and other tools as working context only.

If sources conflict, the Governance Thread resolves the conflict and updates the authoritative document or registry. Chat messages, local notes, branch names, PR descriptions, tool state and automation output must not silently override the frozen governance document or the Stage Registry.

## 8. Governance Freeze and version upgrades（治理冻结与版本升级）

Version 1.1 is frozen. Frozen means the rules cannot be silently edited, reinterpreted through tool behavior or bypassed by starting another thread.

Every proposed governance change requires:

1. a decision in the Governance Thread;
2. a dedicated Stage Registry entry;
3. an independent GitHub Issue and Draft PR;
4. an explicit change log, compatibility impact and migration rule;
5. review before merge and publication.

Version numbering follows these rules:

- **Patch (`1.1.x`)**: wording or citation corrections with no change to authority, lifecycle, controls or obligations.
- **Minor (`1.x`)**: backward-compatible governance additions or clarifications that add a controlled capability.
- **Major (`2.0`)**: changes to governance authority, lifecycle, Parent Thread rules, execution exclusivity, source-of-truth hierarchy or archival rights.

The new version becomes the repository's published authority only after governance approval and merge. Existing Stages remain governed by the version recorded at their creation unless the Governance Thread explicitly records a migration. Historical frozen versions and their evidence remain readable.

## 9. ChatGPT Project transition strategy（ChatGPT 项目过渡策略）

ChatGPT Projects may continue as temporary intake, context and collaboration containers during transition, but a Project is not a Governance Thread and is not a source of governance authority merely because it contains related chats or files.

Transition rules:

1. Map every active Project task to a Stage ID, Parent Governance Thread and one Execution Thread.
2. Register the mapping before the task advances to Executing.
3. Preserve old Project chats as read-only evidence; do not rewrite history to simulate compliance.
4. Start new governed work through the Stage Registry and a linked GitHub Issue.
5. Move decisions and completion evidence back to the Governance Thread through Mandatory Return.
6. Retire duplicated Project control lists only after the Governance Thread confirms their registered Stages are Archived.

The transition is administrative only. It does not authorize deployment, production access, permission changes, external communication or real-business-data use.

## 10. Compliance gate

A Stage is non-compliant and must not advance when any of the following is missing or contradictory:

- one recognized Governance Authority;
- a registered Parent Thread;
- one and only one active Execution Thread;
- an allowed lifecycle status;
- explicit scope and safety boundary;
- reviewable evidence and Mandatory Return;
- Governance Thread confirmation for Archived.

When non-compliance is found, preserve the evidence, record the issue in the Stage Registry and return it to the Governance Thread for decision.

## 11. v1.1 compatibility note

Version 1.1 preserves the authority model, lifecycle, Parent Thread requirement, one-Stage/one-Execution-Thread rule and archival rights established in the initial draft. It adds the explicitly approved dual-thread responsibility boundary, continuous execution rule, fixed nine-Stage roadmap and Governance Dashboard operating model. No production or external-action authority is added.