# AIOS Project Governance Baseline Validation

## Scope

This validation covers Stage 9 / PG-01 documentation and registry controls only.
It reads repository files and performs no production access, real-data access,
permission change, deployment or external write.

Automated checks live in `Tests/test_project_governance.py` and run in the
`Validate AIOS Project Governance` pull-request workflow.

## Positive cases

| Case | Expected result |
|---|---|
| Effective governance dependency | Baseline references published Thread Governance v2.1. |
| Project identity | Exactly one initial `BUW-AIOS` registry row exists. |
| Business boundary | BUW, PC, 汇沣电商 and 六合通 remain explicitly separated. |
| Registry separation | Project Registry and Stage Registry have different control roles. |
| Assignment | Stage 9 identifies Issue #13, the single Execution Thread and authorized branch. |
| Lifecycle | Stages 9–11 are Archived; Stage 11 publication is evidenced by PR #26 under Issue #24; Stages 12–14 remain Planned. |
| Return controls | Mandatory Return and human review/archive gates are explicit. |

## Negative cases

| Case | Expected result |
|---|---|
| ChatGPT Project claims authority | Rejected; it is working context only. |
| Duplicate initial project | Rejected; exactly one `BUW-AIOS` entry is allowed. |
| BUW absorbs PC or a company | Rejected; brand and company boundaries remain separate. |
| Multiple execution authorities | Rejected; one Stage has one active Execution Thread. |
| Missing evidence | Fail closed; truthful status remains unchanged. |
| Self-review or self-archive | Rejected; human Governance Thread decision required. |
| Production, real data, permission or external write | Rejected under Stage 9 authorization. |
| Stage 10 archive interpreted as production approval | Rejected; the published PR-01 assessment remains `BLOCKED / NO-GO`. |

## Local command

```text
python3 -m unittest Tests.test_project_governance -v
```
