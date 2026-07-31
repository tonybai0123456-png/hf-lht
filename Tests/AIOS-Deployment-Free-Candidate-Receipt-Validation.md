# AIOS Deployment-Free Candidate Receipt Validation

## Purpose

This receipt records the exact technical evidence for source commit
`36716abc76373d053c75e68352f46589f4ddc8f1`, tree
`ec48f7c537162b32f6bc35947d9e49758e1b53bd`. It is evidence under Issue #49,
not a release or deployment decision.

## Exact manifest and reproduction

PR #41 contained exactly 29 changed paths at the recorded source head. A clean
copy was created with `git archive`, outside the working tree. From that clean
copy, the repository-controlled `requirements-dev.txt` resolved PyYAML 6.0.3.
The clean copy then passed:

- 127/127 repository tests;
- 10/10 controlled validators;
- Python compilation;
- exact base-to-head diff checking;
- sensitive-material pattern scanning.

The source head also completed 9/9 pull-request GitHub Actions successfully.

## Risk and control truth

The receipt joins every `PR-RISK-001` through `PR-RISK-010` entry to exact
synthetic evidence IDs and the proposed Gate 9 treatment owner. Every risk
remains `open_blocked_unaccepted`, `risk_accepted=false` and
`treatment_authorized=false`.

The eight control evidence IDs are repository-controlled and synthetic only.
No real data, connector, credential, infrastructure or account material was
used.

## Governance boundary

Gate 7–11 remain pending explicit ordered human decisions. Gate 12 remains
withheld by Issue #49. Merge, publication, archive, real data, credentials and
permissions, connectors, external infrastructure and accounts, real pilot,
risk acceptance, release and deployment remain withheld or excluded.

The receipt evaluates only to `not_ready_pending_human_governance` and不得解释为
生产就绪、风险接受、真实试点、合并、发布、归档、发布授权或部署授权。
Mandatory Return remains `external_actions_performed=[]`.

## Commands

```bash
python3 Tests/validate_aios_deployment_free_candidate_receipt.py
python3 -m unittest Tests.test_deployment_free_candidate_receipt -v
python3 -m unittest discover -s Tests -p 'test_*.py' -v
python3 -m compileall -q Runtime Tests
```
