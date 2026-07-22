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

公司与品牌边界：本契约服务于汇沣电商的 BUW AIOS，不得把汇沣电商与六合通合并为同一 `company`。`brand: shared` 仅在 Tony/Stone 或明确业务决策人授权跨品牌视图时使用；输出仍须保留 BUW、PC 的来源、客户、门店、指标和结果分项，不得用合计替代品牌明细。无明确授权时返回 `partial` 或 `blocked` 并要求确认，不得默认合并。

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
agent: "CEO|Marketing|Retail|CRM|Shopify|Developer|Data|CustomerService"
status: "completed|partial|blocked|needs_approval|escalated|rejected"
reporting_period:
  period: "date-range-or-review-window"
  data_updated_through: "date-or-timestamp"
executive_status: "Green|Yellow|Red"
summary: "business-first conclusion"
kpi_snapshot:
  items: []
  not_applicable_reason: "required when items is empty"
completed: []
in_progress: []
business_impact: "impact-or-none"
findings: []
recommended_actions: []
decisions_required: []
risks_and_exceptions: []
evidence_used: []
confidence: "high|medium|low"
missing_information: []
approval_request: {}
handoffs: []
blockers: []
next_priorities: []
next_review: "date-or-null"
domain_payload: {}
```

统一包络的子结构要求：

- 每个 `kpi_snapshot.items` 项包含 `kpi`、`current`、`previous_or_target`、`trend`、`data_source`；无适用 KPI 时保持空数组并填写 `not_applicable_reason`。
- 每个 `completed` 项包含 `item` 和 `evidence_links`。
- 每个 `in_progress` 项包含 `item`、`owner`、`target_date`、`current_status`。
- 每个 `risks_and_exceptions` 项包含 `risk`、`business_impact`、`confidence`、`evidence`、`recommended_action`。
- 每个 `decisions_required` 项包含 `decision`、`options`、`recommended_option`、`latest_decision_time`。
- `next_priorities` 必须按优先级排序。

This output must map to `Templates/Agent-Status-Report.md`:

- agent + reporting_period → Reporting period（Agent、Period、Data updated through）
- executive_status + summary → Executive status（Green / Yellow / Red、One-sentence summary）
- kpi_snapshot → KPI snapshot（KPI、Current、Previous/Target、Trend、Data source；不适用时说明原因）
- completed → Completed（事项与证据）
- in_progress → In progress（事项、负责人、目标日期、当前状态）
- risks_and_exceptions → Risks and exceptions（风险、业务影响、可信度、证据、建议动作）
- decisions_required → Decisions required（事项、选项、推荐、最晚决策时间）
- next_priorities → Next priorities

`status` 表示 Runtime 执行状态，`executive_status` 表示经营红黄绿状态，两者不得混用。`domain_payload` 保留各 Agent 的领域输出，但不得替代以上统一包络。

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

在 Human Authority Matrix 与 Approval Threshold Registry 生效前，所有高风险、重大、大额、大规模、敏感、不可逆或权限类动作统一提交 Tony 或 Stone；二人之一明确书面授权的人工负责人也可在授权范围内批准。无法确认审批人、授权范围或阈值时，保持 `needs_approval`、暂停执行，并由 CEO Agent 建立审批队列升级，不得视为默许。

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

- 每个跨 Agent 事项必须指定一个专业 Agent 为单一 Accountable / Responsible（A/R）；CEO Agent 不替代专业 A/R。
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
