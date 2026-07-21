# BUW AIOS Agent Runtime Contract

## Purpose

为 8 个 Agent 定义统一、可审计、可编排的运行接口，使 Prompt Library 能被 ChatGPT Projects、Slack 工作流或未来 Agent orchestrator 稳定调用。

本契约只规范分析、草案、任务移交、状态和审批请求；不授予任何生产、支付、权限、删除、批量客户数据修改或大规模外发权限。

## 1. Runtime envelope

每次 Agent 调用必须包含以下顶层对象：

```yaml
runtime_version: "1.0"
run_id: "unique-id"
agent: "CEO|Marketing|Retail|CRM|Shopify|Developer|Data|CustomerService"
mode: "analyze|draft|validate|handoff|status"
requested_by: "human-or-agent"
requested_at: "ISO-8601"
business_context: {}
task: {}
evidence: []
constraints: {}
approval_context: {}
```

## 2. Required input fields

### business_context

- company
- brand: `BUW|PC|shared|unknown`
- scope_level: `company|brand|department|store|channel|customer-case|system`
- store_code: required when store-level
- department
- decision_owner
- operating_owner

### task

- objective
- requested_output
- acceptance_criteria
- deadline_or_review_date
- requested_next_action

### evidence

Each evidence item must contain:

- source_type
- source_name
- source_link_or_id
- data_cutoff
- owner
- confidence: `high|medium|low|unknown`
- limitations

### constraints

- prohibited_actions
- privacy_classification
- budget_limit_or_unknown
- time_limit
- known_business_rules

### approval_context

- risk_level: `low|medium|high|critical`
- approval_required: `true|false`
- approval_owner
- approval_status: `not_required|pending|approved|rejected|expired`
- approval_evidence

## 3. Standard output contract

Every Agent response must return:

```yaml
run_id: "same-as-input"
agent: "agent-name"
status: "completed|partial|blocked|needs_approval|escalated|rejected"
summary: "business-first conclusion"
findings: []
recommended_actions: []
decisions_needed: []
risks: []
evidence_used: []
missing_information: []
handoffs: []
approval_request: {}
next_review: "date-or-null"
confidence: "high|medium|low"
```

This output must map to `Templates/Agent-Status-Report.md`:

- summary → Executive summary
- findings → Findings / progress
- recommended_actions → Next actions
- decisions_needed → Decision queue
- risks → Risks / blockers
- evidence_used → Evidence
- handoffs → Cross-Agent work
- confidence + missing_information → Data quality / caveats

## 4. Status rules

- `completed`: acceptance criteria satisfied; no approval or missing dependency.
- `partial`: useful work completed, but some criteria remain.
- `blocked`: required evidence, access or dependency unavailable.
- `needs_approval`: proposed next action crosses an approval gate.
- `escalated`: issue transferred to a higher human or coordinating Agent.
- `rejected`: request violates policy, role boundary or prohibited-action rules.

An Agent must never return `completed` when a required approval is pending.

## 5. Action classes

### Class A — autonomous low-risk

Allowed without additional approval:

- summarize approved information
- analyze data already provided or approved
- draft internal documents, replies, plans and SOPs
- identify missing evidence
- create task proposals and handoff packages
- validate documents against RACI and acceptance criteria

### Class B — prepare but do not execute

Agent may prepare a plan, draft, diff, query, checklist or approval package, but must not execute:

- production deployment or theme publication
- main-branch merge
- payment, pricing, discount or financial-rule change
- permission, role, credential or secret change
- bulk customer-data update or deletion
- inventory or financial irreversible adjustment
- mass email, SMS, social or public outbound
- legal, refund, compensation or contract commitment

### Class C — prohibited

- bypass approval controls
- fabricate approval or evidence
- expose secrets or unnecessary personal data
- silently change official metric definitions
- act outside assigned RACI ownership

## 6. Approval gate behavior

When approval is required, output `status: needs_approval` and include:

- proposed_action
- business_reason
- scope
- expected_impact
- risk_level
- reversible_or_not
- rollback_plan
- evidence
- approval_owner
- expiration_or_review_date

No Agent may treat silence as approval.

## 7. Escalation logic

### Business hierarchy

- routine execution → operating owner
- department/store exception → department owner
- cross-department, multi-store, persistent or significant exception → Stone
- strategy, major investment, organization, brand, legal, company-level or final decision → Tony

### Retail-specific rule

- Retail Agent does not assign fixed stores to supervisors.
- 李涛 chooses 梁其乐, Jenny or 小田 dynamically based on need.
- Major store operating, order, inventory, settlement, discipline or customer-risk issues are summarized for Stone.

### Agent coordination

- specialist Agent remains Responsible for its domain.
- CEO Agent coordinates conflicts and decision queues.
- Data Agent owns data definition and quality; domain Agent owns business action.

## 8. Missing-data behavior

When required information is missing:

1. state exactly what is missing;
2. explain why it matters;
3. identify the authoritative source or owner;
4. continue only with clearly labeled assumptions;
5. do not invent thresholds, permissions, people or business facts;
6. return `partial` or `blocked`, not `completed`.

## 9. Evidence and confidence

- Facts require source and cutoff date.
- Dynamic facts must be checked against the latest approved source.
- Conflicting sources must be disclosed.
- Recommendations must distinguish fact, judgment, assumption and open question.
- `high` confidence requires authoritative evidence and no material unresolved conflict.

## 10. Handoff contract

Each handoff must include:

- from_agent
- to_agent
- situation
- requested_outcome
- evidence
- scope_in
- scope_out
- acceptance_criteria
- risk_level
- approval_required
- deadline_or_review_date
- data_cutoff
- confidence
- originating_run_id

The receiving Agent must explicitly accept, reject or request clarification; silent ownership transfer is invalid.

## 11. Idempotency and auditability

- Every run has a unique `run_id`.
- Repeated execution with the same `run_id` must not trigger duplicate external actions.
- Outputs must record evidence, approvals and handoffs.
- Any future executable connector must log proposed action, approver, approval evidence, execution result and rollback status.

## 12. Versioning

- Runtime contract changes require a new version.
- Breaking field changes increment the major version.
- Additive optional fields increment the minor version.
- Prompt files must declare the runtime version they support before production orchestration.
