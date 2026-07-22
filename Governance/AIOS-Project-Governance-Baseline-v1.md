# BUW AIOS Project Governance Baseline v1.0

## 1. Document control

| Field | Value |
|---|---|
| Project ID | `BUW-AIOS` |
| Project name | BUW AIOS |
| Project-governance version | 1.0 (frozen published version) |
| Publication status | Published through PR #20 / squash merge `62b2aaa` on 2026-07-22 |
| Stage | Stage 9 / PG-01 |
| Issue | [Issue #13](https://github.com/tonybai0123456-png/hf-lht/issues/13) |
| Parent Governance Thread | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Single Execution Thread | `019f7da6-da0c-7310-ad7c-2b4bc15a9906` |
| Canonical repository | `tonybai0123456-png/hf-lht` |
| Project Registry | `Governance/AIOS-Project-Registry.md` |
| Stage Registry | `Governance/AIOS-Stage-Registry.md` |
| Effective governance dependency | `Governance/AIOS-Thread-Governance-v2.1.md` |

This frozen published baseline defines project identity, authority, controlled
artifacts, change flow, evidence and project lifecycle for `BUW-AIOS`. It was
human-reviewed and published through PR #20 at merge `62b2aaa`.

It authorizes no deployment, permission change, production access, real business
data, customer data or external writes. Stage 10 / PR-01 is separately authorized
through Issue #21 for assessment and prepare-only evidence, not production.

## 2. Why this baseline exists

Thread Governance controls how Stages and threads are authorized. This baseline
adds the missing project-level control: it gives BUW AIOS one stable identity,
one accountable authority, explicit business boundaries, a Project Registry and
a repeatable evidence path. The Project Registry and Stage Registry remain
separate so project identity cannot be inferred from a temporary Stage or tool.

Governance precedes tools. Tools execute authorized work; they do not create
policy, expand scope, approve risk, freeze a version or archive a project.

## 3. Project identity and business boundary

`BUW-AIOS` is the governed AI operating-system project for the BUW brand.

- **BUW** is the project brand boundary.
- **PC** is an independent brand and is outside this project's identity.
- **汇沣电商** is the company boundary; the company is not collapsed into this
  BUW brand project.
- **六合通** is a separate company and is outside this project.

A cross-brand, cross-company or whole-company control surface requires a new
project ID or an explicit Governance Thread decision and controlled registry
change. A repository, ChatGPT Project, folder, Issue, branch, PR or tool session
cannot silently widen the boundary.

## 4. Single Project Governance Authority

The **BUW AIOS Official Governance Thread** is the Single Project Governance
Authority. Only it may:

- create, rename, split, suspend, reactivate or archive the project;
- change the project owner, company/brand boundary or canonical repository;
- approve Project Registry entries and project-governance versions;
- authorize Stages and resolve conflicts between project records;
- approve exceptions to this baseline;
- confirm project-status transitions and publication.

An Execution Thread, GitHub Issue, Draft PR, Agent, ChatGPT Project, workflow or
tool may produce evidence. None is an independent governance authority and none
may self-approve, self-freeze or self-archive.

## 5. Operating model and the six system questions

| Question | Controlled answer |
|---|---|
| Business loop | Governance authorizes a bounded Stage; execution implements and validates it; Mandatory Return supplies evidence; human governance reviews and later archives. |
| Core objects | Project, project policy, Project Registry entry, Stage, Governance Thread, Execution Thread, Issue, branch, Draft PR and evidence. |
| Data flow | Governance decisions and synthetic/read-only validation evidence enter GitHub; controlled policy and registries settle in the canonical repository. |
| Operators | The Governance Thread decides what/why/whether; the single Execution Thread implements and validates how; human owners approve gated transitions. |
| AI vs human judgment | Agents and tools check structure and consistency; humans alone decide authority, scope, exceptions, review, publication and archival. |
| Proof | Linked Issue, branch, commit, Draft PR, deterministic validation, CI result, registry transition and Mandatory Return. |

## 6. Core roles and separation of registries

| Object or role | Controls | Cannot do alone |
|---|---|---|
| Project `BUW-AIOS` | Groups governed BUW AIOS policies, Stages and evidence. | Expand into PC, all of 汇沣电商 or 六合通. |
| Governance Thread | Owns project policy, authorization, exceptions, review and archive decisions. | Treat missing evidence as approval. |
| Project Registry | Records current project identity, boundary, owner, repository, project status and policy references. | Create authority or replace Stage assignment. |
| Stage Registry | Records Stage assignment, one Execution Thread and Stage lifecycle. | Replace project identity or project status. |
| Execution Thread | Implements one authorized Stage and submits Mandatory Return. | Change governance, self-approve or self-archive. |
| Canonical repository | Preserves controlled artifacts and evidence. | Approve or merge its own changes. |
| ChatGPT Project | Supplies intake and working context. | Become policy, a registry or Governance Thread. |
| Agents and tools | Draft, inspect and validate within authorization. | Make irreversible, permission, production or governance decisions. |

The Project Registry controls **project identity and project status**. The Stage
Registry controls **Stage assignment and Stage lifecycle**. Each does not replace
the other, and a status in one cannot be inferred as a status in the other.

## 7. Single Source of Truth

The authoritative project control chain is:

1. the latest effective frozen governance document published by the Governance
   Thread, currently `Governance/AIOS-Thread-Governance-v2.1.md`;
2. `Governance/AIOS-Stage-Registry.md` for current Stage assignment and lifecycle;
3. explicit Governance Thread decisions awaiting repository publication;
4. the latest published Project Governance Baseline;
5. `Governance/AIOS-Project-Registry.md` for current governed-project identity,
   boundary, owner, repository, project status and policy references;
6. linked Issues, branches, commits, PRs, validation and CI as execution evidence;
7. ChatGPT Projects, chats, local drafts and tools as working context only.

Thread Governance v2.1 and the Stage Registry remain authoritative.
If records conflict, the Governance Thread resolves and publishes the correction.
Safety controls use the most restrictive rule. Missing or ambiguous authority,
boundary or evidence must fail closed: the affected transition stops.

## 8. Project lifecycle

The project-status lifecycle is distinct from the Stage lifecycle:

**Registered → Active → Suspended → Archived**

| Project status | Meaning | Transition authority |
|---|---|---|
| Registered | Identity exists but governed execution is not yet active. | Governance Thread |
| Active | One or more authorized Stages may be governed; every Stage still has only one active Execution Thread. | Governance Thread |
| Suspended | New execution is paused while evidence and records are preserved. | Governance Thread |
| Archived | Project closure is accepted after evidence, disposition and publication requirements are complete. | Governance Thread only |

Suspension is not deletion. Archived is not inferred from a merged PR or an
Archived Stage. Stage lifecycle remains **Planned → Executing → Reported →
Reviewed → Archived**. Reported does not mean Reviewed. Reviewed does not mean
Archived. The Execution Thread may set only its authorized Stage to Reported by
submitting Mandatory Return.

Reviewed does not mean Archived; each transition requires its own recorded human
governance decision.

## 9. Controlled artifact classes

| Class | Examples | Control |
|---|---|---|
| Normative policy | Effective Thread Governance and a published Project Governance Baseline | Requires Governance Thread approval and controlled publication. |
| Operational registry | Project Registry and Stage Registry | Current controlled state; changes require correct authority and evidence. |
| Execution evidence | Issue, branch, commit, Draft PR, tests, CI and Execution Report | Proves work but creates no governance authority. |
| Working context | ChatGPT Project files, chats, local drafts and tool output | Non-authoritative until promoted through the controlled process. |

Working context must never be cited as published policy without a linked human
decision and repository publication evidence.

## 10. Project operating loop

1. Governance confirms the project and authorizes a Stage.
2. The Project Registry supplies identity, boundary, owner, repository and policy.
3. The Stage Registry records the Parent Thread and exactly one Execution Thread.
4. Execution uses the dedicated Issue, authorized branch and independent Draft PR.
5. Read-only validation checks scope, consistency, safety and evidence.
6. The Execution Thread submits Mandatory Return and moves its Stage to Reported.
7. The Governance Thread may confirm Reviewed or return scoped corrections.
8. Publication and Archived each require separate governance authority.

Tool activity, file existence, a passing test or an open PR does not advance a
governance lifecycle by itself.

## 11. Change control and human approval

Documentation drafting, Project Registry proposals and read-only validation may
proceed in an authorized prepare-only Stage. They remain Draft PR work until
human review.

Changes to project identity, owner, business boundary, authority, source
hierarchy, lifecycle, registry schema, freeze rules or approval gates require a
dedicated Stage, Issue, Draft PR, compatibility note and Governance Thread approval.

Explicit human approval is required before:

- merging or deploying;
- changing permissions, credentials, security settings or branch protection;
- production access, real business data or customer data access;
- any external writes or irreversible business action;
- changing company, brand, store or customer ownership boundaries;
- publishing a new governance version or marking a project Archived.

Inherited tool access is never equivalent to human approval.

## 12. Project Registry rules

Every registered project must have a stable ID, name, business boundary, owner,
Governance Thread, canonical repository, policy paths, project status, active
Stage reference, review date and evidence.

1. Project IDs are unique and immutable.
2. Only the Governance Thread may create, split, rename or archive an entry.
3. Every material field change requires a linked decision and evidence.
4. Missing evidence fails closed; the current truthful status remains.
5. Corrections append a dated change record and preserve prior evidence.
6. Project status does not replace Stage status.
7. A project may contain several Stages, but a Stage may never have multiple
   active Execution Threads.

## 13. ChatGPT Project transition strategy

A ChatGPT Project is not a Governance Thread, Project Registry, Stage Registry or
project authority. It is working context only.

1. Map active work to `BUW-AIOS`, a registered Stage and a Parent Thread.
2. Record exactly one Execution Thread before the Stage enters Executing.
3. Preserve old Project chats and synced files as read-only historical evidence.
4. Promote policy only through Issue, branch, Draft PR, human review and publication.
5. Return decisions and evidence through Mandatory Return.
6. Retire duplicate Project control lists only after governance reconciliation.

This transition grants no production, permission, real-data or external-write authority.

## 14. Evidence and Mandatory Return

Every Stage preserves its Parent Thread, Stage ID, Issue, single Execution Thread,
branch, commit, Draft PR, changed-file scope, checks, CI, approvals, exceptions,
unresolved blockers and lifecycle transitions.

Mandatory Return uses exactly:

1. **本次完成**;
2. **证据链接**;
3. **阻塞项**;
4. **下一步**.

The execution return may report the Stage but may not declare Reviewed or Archived.

## 15. Fail-closed boundaries and negative cases

| Condition | Required response |
|---|---|
| Missing or ambiguous Governance Thread | Do not start or advance. |
| Duplicate project ID | Reject the duplicate and return the conflict. |
| multiple active Execution Threads for one Stage | Stop new execution and require governance resolution. |
| Conflicting project records | Preserve evidence and apply the authority chain. |
| Missing evidence or inaccessible link | Keep the truthful status; do not claim completion. |
| Scope drift or architecture expansion | Stop the out-of-scope action and return for adjudication. |
| Production, permission, real business data or external writes | Stop and require explicit human approval; Stage 9 grants none. |
| Historical non-compliance | Preserve history; do not rewrite it to simulate compliance. |

This baseline must never be interpreted to mean that a ChatGPT Project owns
governance; an Issue, PR, Agent or tool may self-approve; a Stage may use multiple
active Execution Threads; BUW automatically includes PC, all of 汇沣电商 or
六合通; documentation authorizes production or real business data; or Reported
means Archived.

## 16. Governance Freeze and version upgrades

This v1.0 baseline is frozen after Governance Thread approval and controlled
publication through PR #20. An Execution Thread cannot alter or re-freeze it.

- Patch `1.0.x`: non-semantic wording or citation correction.
- Minor `1.x`: backward-compatible project-governance addition.
- Major `2.0`: authority, identity, boundary, hierarchy, lifecycle or approval change.

Every upgrade requires an explicit governance decision, dedicated Stage, Issue,
Draft PR, change log, compatibility impact, migration rule, review and publication.
Frozen historical versions remain readable and must not be silently modified.

## 17. Stage 9 compliance gate

PG-01 passed human review, was published through PR #20 and was archived only
after post-merge verification. Stage 10 / PR-01 is separately authorized through
Issue #21 for assessment, documentation, synthetic/read-only validation, CI,
Draft PR and Execution Report only; production execution remains unauthorized.
