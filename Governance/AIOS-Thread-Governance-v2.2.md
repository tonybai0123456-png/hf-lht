# BUW AIOS Thread Governance v2.2

## 1. Document control

| Field | Value |
|---|---|
| Governance version | 2.2 |
| Status | Frozen and published |
| Governance authority | BUW AIOS Official Governance Thread（BUW AIOS 官方治理主线程） |
| Repository | `tonybai0123456-png/hf-lht` |
| Stage control surface | `Governance/AIOS-Stage-Registry.md` |
| Supersedes on publication | `Governance/AIOS-Thread-Governance-v2.1.md` (frozen v2.1) |
| Effective scope | BUW AIOS Stage planning, execution-thread assignment, continuous execution, review, publication and archival |
| Upgrade approved on | 2026-07-22 |

Version 2.2 preserves the v2.1 authority, lifecycle, safety boundaries and historical evidence. It records Stage 10 publication and archival, preserves its `BLOCKED / NO-GO` production decision, and extends the frozen roadmap through Stage 14 so remediation work can proceed in controlled, evidence-first stages.

This policy does not authorize deployment, production or staging access, permission or credential changes, real-business-data access, connector writes, risk acceptance, a pilot, release or external communication.

## 2. Governance authority and operating model

The **BUW AIOS Official Governance Thread** is the single authority for Stage creation, sequencing, assignment, review, publication and archival. Tools, Agents, Issues, branches, pull requests, CI and execution tasks provide evidence but cannot expand scope or grant authority.

Each Stage must have:

1. one stable Stage ID and business outcome;
2. this Governance Thread as Parent Thread;
3. no more than one active Execution Thread;
4. explicit scope, exclusions, safety boundary and acceptance evidence;
5. a truthful status in `Governance/AIOS-Stage-Registry.md`.

The Governance Thread owns what, why and whether to approve. The Execution Thread owns implementation, documentation, tests, CI, Draft PR maintenance, evidence and Mandatory Return for one authorized Stage. It may not self-declare review, publication or archival.

## 3. Continuous execution and stop conditions

After authorization, the assigned Execution Thread continues ordinary work within scope. It pauses and returns when human approval is required, a material architecture conflict or scope expansion appears, production or staging access would be involved, permissions or credentials would change, real data or external writes would be used, risk acceptance or pilot authority is needed, an unrecoverable blocker occurs, or the Stage is complete.

Routine defects, tests and reversible documentation or synthetic implementation choices remain inside the authorized execution scope.

## 4. Lifecycle and Mandatory Return

The only lifecycle is:

**Planned → Executing → Reported → Reviewed → Archived**

| Status | Meaning | Exit authority |
|---|---|---|
| Planned | Defined, not started. | Governance Thread authorizes Executing. |
| Executing | One assigned task works continuously within scope. | Execution task submits Mandatory Return and marks Reported. |
| Reported | Evidence returned; human review pending. | Governance Thread confirms Reviewed or returns scoped corrections. |
| Reviewed | Human review accepted the technical result; publication or closure may still be pending. | Governance Thread separately authorizes publication and Archived. |
| Archived | Required disposition and archive evidence are recorded. | Reopening requires a new Stage or approved governance change. |

Every Mandatory Return has four headings: **本次完成**, **证据链接**, **阻塞项**, and **下一步**. Reported does not mean Reviewed; Reviewed does not mean merged, published or Archived. A blocker is recorded without inventing a lifecycle state.

## 5. Source of truth and version freeze

The authoritative chain is:

1. this latest published governance policy;
2. `Governance/AIOS-Stage-Registry.md` for assignments and lifecycle;
3. explicit Governance Thread decisions awaiting repository publication;
4. linked GitHub evidence;
5. tasks and tools as working context only.

Version 2.2 is a backward-compatible minor upgrade. Frozen v2.1, v2.0 and v1.1 files remain unchanged and readable. Any later governance change requires an explicit decision, registry entry, independent Issue and Draft PR, compatibility note, review and publication.

## 6. Frozen remediation roadmap

Stages 1 through 10 retain their historical identifiers and evidence. The controlled remediation sequence is:

| Stage | Stage ID | Outcome | Authority boundary |
|---:|---|---|---|
| 11 | AF-01 | Architecture and Security Foundations | Documentation, design, threat model, synthetic/read-only verification only. |
| 12 | DG-01 | Privacy and Data Governance | Planned only; no real data, source connection, retention action or owner assignment. |
| 13 | OR-01 | Operational Resilience | Planned only; no infrastructure, deployment, monitoring connection or incident operation. |
| 14 | PS-01 | Support and Controlled Pilot Design | Planned design only; not pilot authorization and not release authority. |

Stage 12 may enter Executing only after Stage 11 is Reviewed, dispositioned and Archived and the Governance Thread gives a separate start decision. The same sequential gate applies from Stage 12 to 13 and Stage 13 to 14. Stage 14 completion cannot authorize a pilot; any actual pilot or release requires a later independent governance decision with named human owners, accepted evidence and explicit bounded authority.

## 7. Stage 10 disposition

Stage 10 / PR-01 assessed readiness; it did not remediate blockers or prove production operation. Its published result is final for that Stage:

- recommendation: `BLOCKED / NO-GO`;
- readiness dimensions blocked: 9 of 10;
- human gates authorized: 0 of 6;
- accepted risks: 0 of 10;
- remediation owners: `unassigned / governance decision required`.

Archiving Stage 10 means the assessment is complete and published. It does not mean production-ready, pilot-ready, released, risk-accepted or owner-assigned.

## 8. Stage 11 authorization

Stage 11 / AF-01 is authorized through Issue #24, Execution Thread `019f89ac-e3b7-7b90-ad27-286708c407e0`, and branch `feat/aios-architecture-security-foundations-v1`.

AF-01 must answer the six system questions, define bounded target topology and trust zones, identify threats and controls, specify identity/authentication/authorization/least-privilege and secrets-lifecycle designs, preserve BUW/PC and company boundaries, and define synthetic non-production acceptance evidence. It must fail closed and stop at Reported through a Draft PR and Mandatory Return.

AF-01 does not authorize infrastructure creation, deployment, production or staging access, credentials, permissions, real data, connector operations, real owner names, risk acceptance, pilot execution, merge, publication or archival.

## 9. Compliance gate

A Stage must not advance if it lacks the recognized Governance Thread, one registered Execution Thread, explicit boundaries, an allowed status, reviewable evidence, Mandatory Return, or the required human decision. Conflicts fail closed and return to governance.

## 10. v2.2 change log and migration

- Preserved all v2.1 authority, lifecycle, evidence hierarchy and safety controls.
- Recorded PR #23 publication and post-merge verification, then archived Stage 10 without changing its `BLOCKED / NO-GO` conclusion.
- Extended the frozen roadmap to Stage 14 and separated architecture/security, privacy/data, operational resilience, and support/pilot design.
- Authorized only Stage 11 / AF-01 to enter Executing; Stages 12 through 14 remain Planned.
- Kept all remediation owners unassigned pending explicit human naming.
- Preserved separate future decisions for publication, risk acceptance, pilot entry and release.
