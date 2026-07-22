# BUW AIOS Thread Governance v2.0

## 1. Document control

| Field | Value |
|---|---|
| Governance version | 2.0 |
| Status | Frozen and published |
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Repository | `tonybai0123456-png/hf-lht` |
| Stage control surface | `Governance/AIOS-Stage-Registry.md` |
| Supersedes on publication | `Governance/AIOS-Thread-Governance-v1.md` (frozen v1.1) |
| Effective scope | BUW AIOS Stage planning, execution-thread assignment, continuous execution, review, return reporting and archival |
| Upgrade approved on | 2026-07-22 |
| Published on | 2026-07-22 via PR #12 |

The Governance Thread approved this major-version upgrade so the lifecycle can distinguish technical review from archival. Version 2.0 was published through the authorized merge of PR #12 on 2026-07-22 and is the repository's current frozen governance authority. Frozen v1.1 remains readable as historical evidence.

This document governs work coordination. It does not authorize merge, deployment, production access, permission changes, real-business-data access, external writes or any other high-risk action.

## 2. Governance precedes tools（治理先于工具）

No tool, Agent, ChatGPT Project, Issue, branch, pull request, workflow, harness, orchestrator or automation may define its own governance authority.

Before work starts, governance must establish:

1. the Stage and intended business outcome;
2. the Governance Thread and required Parent Thread;
3. the one permitted Execution Thread;
4. scope, exclusions, approval boundary, acceptance evidence and return format;
5. the initial Stage status in the Stage Registry.

Tools execute approved work. They do not create policy, expand scope, approve risk, declare review or archival, or replace human governance judgment.

## 3. Single Governance Authority（唯一治理权威）

The **BUW AIOS Official Governance Thread** is the Single Governance Authority for this governance version. Only that Governance Thread may:

- create, split, sequence, suspend or cancel a Stage;
- assign or replace a Stage's Execution Thread;
- confirm a Stage moving from Reported to Reviewed;
- approve a Stage moving from Reviewed to Archived;
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
- lifecycle confirmation from Reported to Reviewed and from Reviewed to Archived.

The Governance Thread does not perform routine implementation, code changes, tests, CI maintenance or PR implementation work.

### 4.2 Execution Thread（执行线程）

The Execution Thread owns **how to implement and validate** one authorized Stage. Its responsibilities are:

- repository implementation and documentation;
- tests and CI;
- Issue and Draft PR maintenance;
- evidence capture;
- correction of ordinary technical defects;
- Mandatory Return at completion or escalation.

The Execution Thread must not change governance rules, expand Stage scope, approve high-risk actions, self-declare Reviewed or Archived, merge without authorization, deploy to production or use real business data outside an explicitly approved boundary.

### 4.3 Parent Thread Required（必须指定父线程）

Every Execution Thread must identify its Parent Governance Thread before entering Executing. The parent must be recorded in the Stage Registry and repeated in the related GitHub Issue or PR description.

If the Parent Thread is absent, ambiguous or points to an unapproved authority, the Stage must not enter Executing. Ordinary work notes, Projects and tool sessions are not substitutes for the required parent relationship.

### 4.4 One Stage, one Execution Thread

At any time, one Stage may have only one active Execution Thread. Parallel Agents or tools may work inside that thread's authorized scope, but they do not become independent execution authorities.

A second Execution Thread may be assigned only after the Governance Thread records the reason, closes or supersedes the prior assignment and updates the Stage Registry. Splitting work requires separate Stage IDs and separate execution assignments.

The Workflow Schema and Controlled Harness work recorded under PR #10 is a pre-freeze combined-execution exception. It is preserved as historical evidence and must not be treated as a reusable precedent under v2.0.

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

**Planned（已计划） → Executing（执行中） → Reported（已汇报） → Reviewed（已评审） → Archived（已归档）**

| Status | Meaning | Entry requirement | Exit authority |
|---|---|---|---|
| Planned | Stage is defined but execution has not started. | Stage ID, scope, Parent Thread, acceptance evidence and intended execution assignment are registered. | Governance Thread authorizes Executing. |
| Executing | The one assigned Execution Thread is working continuously within scope. | Execution Thread and evidence location are registered; safety and approval boundaries are explicit. | Execution Thread submits Mandatory Return and marks Reported. |
| Reported | Execution has returned its result and evidence; human governance review is pending. | Mandatory Return is complete and evidence links are accessible. | Governance Thread confirms Reviewed or returns the Stage for scoped follow-up. |
| Reviewed | Human governance review has accepted the technical result, while merge, publication, sequencing or final closure may remain pending. | The Governance Thread records the review decision and evidence; any Draft PR remains Draft unless separately authorized. | Governance Thread alone confirms Archived after required closure evidence exists. |
| Archived | Governance has accepted final closure and closed the Stage. | Review, required publication or disposition, and archive evidence are recorded in the Stage Registry. | A new Stage or approved governance-version change is required to reopen work. |

Status movement must be recorded in the Stage Registry. `Reviewed` does not mean merged, deployed, published or archived. A blocker does not create an extra lifecycle state: record the blocker in the Stage row and keep the truthful current status. Statuses may not be skipped, backdated or inferred from tool activity alone.

## 6. Mandatory Return（强制回归汇报）

Before an Execution Thread stops, hands off or requests review, it must return to the Parent Governance Thread with these four headings:

1. **本次完成** — exact scope completed and current Stage status;
2. **证据链接** — Issue, branch, Draft PR, files, checks and other reviewable evidence;
3. **阻塞项** — unresolved dependency, decision, risk or `无`;
4. **下一步** — the single next governance action and its owner.

The Execution Thread must set the Stage to Reported after this return. It must not claim Reviewed or Archived. Missing evidence, inaccessible links, unexplained scope drift or an incomplete return prevents review and archival.

After human review, the Governance Thread records Reviewed. Reviewed work stays open until the Governance Thread separately confirms its required merge, publication, disposition or archival conditions.

## 7. Single Source of Truth（唯一事实源）

The authoritative control chain is:

1. the latest effective frozen governance document approved and published by the Governance Thread;
2. `Governance/AIOS-Stage-Registry.md` for current Stage assignment and lifecycle status;
3. explicit Governance Thread decisions awaiting repository publication;
4. linked GitHub Issues, branches, commits and PRs for execution evidence;
5. ChatGPT Projects and other tools as working context only.

If sources conflict, the Governance Thread resolves the conflict and updates the authoritative document or registry. Chat messages that are not explicit governance decisions, local notes, branch names, PR descriptions, tool state and automation output must not silently override the frozen governance document or the Stage Registry.

## 8. Governance Freeze and version upgrades（治理冻结与版本升级）

Version 2.0 is frozen as of its repository publication through PR #12 on 2026-07-22. Frozen means the rules cannot be silently edited, reinterpreted through tool behavior or bypassed by starting another thread.

Every proposed governance change requires:

1. a decision in the Governance Thread;
2. a dedicated Stage Registry entry;
3. an independent GitHub Issue and Draft PR;
4. an explicit change log, compatibility impact and migration rule;
5. review before merge and publication.

Version numbering follows these rules:

- **Patch (`2.0.x`)**: wording or citation corrections with no change to authority, lifecycle, controls or obligations.
- **Minor (`2.x`)**: backward-compatible governance additions or clarifications that add a controlled capability.
- **Major (`3.0`)**: changes to governance authority, lifecycle, Parent Thread rules, execution exclusivity, source-of-truth hierarchy or archival rights.

A future approved upgrade draft does not silently become published authority. A new version becomes the repository's published authority only after governance-approved merge and publication. Version 2.0 became published authority through the authorized merge of PR #12; historical frozen versions and their evidence remain readable.

## 9. ChatGPT Project transition strategy（ChatGPT 项目过渡策略）

ChatGPT Projects may continue as temporary intake, context and collaboration containers during transition, but a Project is not a Governance Thread and is not a source of governance authority merely because it contains related chats or files.

Transition rules:

1. Map every active Project task to a Stage ID, Parent Governance Thread and one Execution Thread.
2. Register the mapping before the task advances to Executing.
3. Preserve old Project chats as read-only evidence; do not rewrite history to simulate compliance.
4. Start new governed work through the Stage Registry and a linked GitHub Issue.
5. Move decisions and completion evidence back to the Governance Thread through Mandatory Return.
6. Record human review as Reviewed without treating it as merge or archival authorization.
7. Retire duplicated Project control lists only after the Governance Thread confirms their registered Stages are Archived.

The transition is administrative only. It does not authorize deployment, production access, permission changes, external communication or real-business-data use.

## 10. Compliance gate

A Stage is non-compliant and must not advance when any of the following is missing or contradictory:

- one recognized Governance Authority;
- a registered Parent Thread;
- one and only one active Execution Thread;
- an allowed lifecycle status;
- explicit scope and safety boundary;
- reviewable evidence and Mandatory Return;
- Governance Thread confirmation for Reviewed and Archived.

When non-compliance is found, preserve the evidence, record the issue in the Stage Registry and return it to the Governance Thread for decision.

## 11. v2.0 change log, compatibility and migration

### 11.1 Change log

- Added Reviewed（已评审） between Reported and Archived.
- Separated technical acceptance from merge, publication and final archival.
- Clarified that an Execution Thread reports work but cannot self-declare Reviewed.
- Clarified the repository-publication boundary for governance upgrades.

### 11.2 Compatibility impact

The Single Governance Authority, Governance Thread, Execution Thread, Parent Thread requirement, one-Stage/one-Execution-Thread rule, Mandatory Return, Single Source of Truth, Governance Freeze and ChatGPT Project transition controls remain compatible with v1.1. The lifecycle and archival gate change is intentionally not backward-compatible and therefore requires this Major version.

### 11.3 Migration rule

With v2.0 publication through PR #12:

1. preserve `Governance/AIOS-Thread-Governance-v1.md` unchanged as the frozen v1.1 historical version;
2. use `Governance/AIOS-Thread-Governance-v2.md` for new governance decisions;
3. migrate Stages 2 through 7 from Reported to Reviewed because the Governance Thread explicitly accepted their technical results;
4. keep Stage 1 Archived without reopening it;
5. keep Stages 8 and 9 Planned without creating an execution authorization;
6. keep PRs #4, #6, #8, #10 and #12 Draft and unmerged until separate governance decisions authorize their disposition;
7. retain the fixed review order `#4 → #6 → #8 → #10 → #12` as historical review evidence, not merge authorization.
