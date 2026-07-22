# BUW AIOS Workflow Library v1

## Purpose

将 Agent RACI、Prompt Library 与 Runtime Contract 转化为可复用的业务工作流。所有工作流默认使用 `runtime_version: 1.0`，高风险动作仅形成审批包，不直接执行。

## Common workflow envelope

每次运行必须遵守 Agent Runtime Contract 1.0。工作流扩展输入包含：`workflow_id`、`run_id`、`trigger`、`business_outcome`、`scope`、`workflow_owner_agent`、`supporting_agents`、`workflow_acceptance_criteria`。

- `workflow_owner_agent` 必须使用一个规范 Agent ID，并作为工作流结果的单一专业 A/R。允许的规范 ID：`CEO`、`Marketing`、`Retail`、`CRM`、`Shopify`、`Developer`、`Data`、`CustomerService`。
- 输入、证据、风险和审批字段沿用 Runtime Contract，不建立第二套同义字段。
- 标准输出必须精确采用 Runtime Contract 1.0 的统一包络：`run_id`、`agent`、`status`、`reporting_period`、`executive_status`、`summary`、`kpi_snapshot`、`completed`、`in_progress`、`business_impact`、`findings`、`recommended_actions`、`decisions_required`、`risks_and_exceptions`、`evidence_used`、`confidence`、`missing_information`、`approval_request`、`handoffs`、`blockers`、`next_priorities`、`next_review`、`domain_payload`。
- `runtime_version` 仅属于调用输入包络；标准输出不得使用 `agent_id`、顶层 `data_cutoff` 或 `evidence_links` 替代契约字段 `agent`、`reporting_period.data_updated_through` 和 `evidence_used`。
- `status` 只允许 `completed`、`partial`、`blocked`、`needs_approval`、`escalated`、`rejected`；业务灯号使用独立的 `executive_status`（Green/Yellow/Red），不得混用。
- 工作流专有结果写入 `domain_payload`，并保留 `workflow_id`，不得用旧字段 `next_step` 代替 `next_priorities`。
- Agent 间 handoff 必须包含：`from_agent`、`to_agent`、`situation`、`requested_outcome`、`evidence`、`scope_in`、`scope_out`、`acceptance_criteria`、`risk_level`、`approval_required`、`deadline_or_review_date`、`data_cutoff`、`confidence`、`originating_run_id`。

默认审批人为 Tony 或 Stone，或其书面指定的代理人。无法确认审批人、授权范围或阈值时，状态必须为 `needs_approval` 并暂停执行，由 CEO Agent 升级；沉默不构成批准。

主体和数据边界默认隔离：BUW 与 PC 不跨品牌合并，除非获得明确授权并保留品牌明细；不得把汇沣电商与六合通合并为一个主体。共享视图必须写明授权范围、口径和数据截止时间。

---

# WF-001 门店异常调查与升级

## Trigger
门店出现经营、货物安全、财务结算、接待秩序或执行异常。

## Ownership
- `workflow_owner_agent: Retail`（工作流单一 A/R）
- 现实业务负责人：李涛
- C：`Data`、`CustomerService`、Finance/HR（按事件）
- 升级协调：`CEO`

## Flow
1. 验证品牌、门店代码、日期、异常类型和证据。
2. 缺关键字段时状态为 blocked，不推断根因。
3. Retail Agent 判断严重度与影响范围。
4. 李涛根据地点、问题类型和紧急程度动态派遣梁其乐、Jenny 或小田；不固定绑定门店。
5. 形成检查、整改、培训和复查计划。
6. 单店常规问题由李涛闭环；持续、多店、跨部门或重大风险升级 Stone。
7. 库存账面、现金、处分、停业、法律或安全事件转 needs_approval。

## Completion evidence
调查事实、整改动作、负责人、复查日期、剩余风险、是否升级。

---

# WF-002 顾客投诉到门店整改闭环

## Trigger
客户投诉涉及门店现场行为、接待秩序、员工执行或商品保管。

## Ownership
- `workflow_owner_agent: CustomerService`（从投诉到关闭的工作流单一 A/R）
- 客户 case 结果 A/R：`CustomerService`
- 门店整改结果 A/R：`Retail`
- 数据核验：`Data`（需要时）

## Flow
1. Customer Service 建立 case，记录品牌、case_id、门店代码、时间线和客户诉求。
2. 生成合规回复草稿，不承诺退款、赔偿、特殊折扣或法律责任。
3. 通过标准 handoff 将现场调查移交 Retail。
4. Retail 由李涛动态派督导调查，并回传事实、动作、预计完成时间。
5. Customer Service 保持客户沟通和 case ownership。
6. 严重安全、歧视、欺诈、法律、媒体或舆情风险立即升级 Stone/CEO Agent。
7. 退款、赔偿和公开回应转人工审批。

## Completion evidence
客户回复状态、门店调查事实、整改结果、复查节点、审批事项。

---

# WF-003 Shopify 需求到 Developer Draft PR

## Trigger
伍淑娴或业务助理提出 Shopify 页面、SEO、CRO、商品展示或订单流程改进需求。

## Ownership
- `workflow_owner_agent: Shopify`（需求到验收的工作流单一 A/R）
- 业务需求结果 A/R：`Shopify`
- 技术交付结果 A/R：`Developer`
- C：`Marketing`、`CRM`、`Data`

## Flow
1. Shopify Agent确认品牌、页面/流程、商品范围、当前问题、目标和基线。
2. 输出业务需求、用户旅程、验收标准、KPI、风险和回滚要求。
3. 生产主题、价格、支付、批量商品/订单、权限、应用安装或迁移标记 needs_approval。
4. 向 Developer Agent 移交结构化技术任务。
5. Developer 输出设计、影响组件、实现计划、测试、安全/数据影响和回滚方案。
6. 只允许创建分支、非生产实现、测试和 Draft PR。
7. 主分支合并与生产部署必须人工批准。

## Completion evidence
需求链接、Draft PR、测试结果、回滚方案、待审批清单。

---

# WF-004 Marketing 与 CRM 联合活动

## Trigger
需要开展获客、复购、召回、UGC 或跨渠道营销活动。

## Ownership
- 启动前必须依据主要业务结果指定一个 `workflow_owner_agent`：获客/内容为主时由 `Marketing` A/R，复购/召回为主时由 `CRM` A/R；未指定不得进入执行。
- 内容与渠道结果 A/R：`Marketing`
- 人群、许可、排除和频次结果 A/R：`CRM`
- 数字与增量评估结果 A/R：`Data`（指标事实）

## Flow
1. 明确 BUW 或 PC，不默认跨品牌合并。
2. Marketing 定义目标、内容、渠道、创意与实验假设。
3. CRM 定义人群、许可、排除、频次、触发和生命周期目标。
4. Data 定义指标、基线、覆盖、增量评估和可信度。
5. 联合输出活动草案与单一决策包。
6. 公开发布、预算、合同、版权/肖像、价格优惠、名单导出和大规模外发必须审批。
7. 缺许可或排除规则时不得生成可执行名单。

## Completion evidence
活动方案、人群规则、KPI、数据口径、审批状态、复盘日期。

---

# WF-005 Agent 周报到 CEO 决策队列

## Trigger
每日/每周 Agent 状态报告到期，或出现重大异常。

## Ownership
- `workflow_owner_agent: CEO`（仅对决策队列结果单一 A/R）
- 各执行项：保留一个专业 Agent A/R
- 人工决策：Tony/Stone

## Flow
1. 收集 8 个 Agent 的标准 Runtime 输出。
2. 校验状态、证据、数据截止时间、可信度、负责人和截止日期。
3. 去重相同问题，识别跨 Agent 冲突和依赖。
4. 按业务影响、紧急程度、风险和可逆性排序。
5. 输出：已完成、需决定、需审批、已升级、阻塞和下一步。
6. 每项执行任务保留一个单一专业 A/R，CEO Agent 不替代专业执行。
7. 战略、重大预算、组织、品牌危机、法律、生产、支付、权限、删除和大规模外发进入 Tony/Stone 审批队列。

## Completion evidence
决策队列、责任人、截止时间、证据链接、审批记录和后续状态。

---

## Global safety rules

任何工作流均不得自动执行：生产部署、主分支合并、支付或价格规则、权限/密钥、客户数据批量写入或删除、库存/财务不可逆调整、人员处分、退款赔偿承诺、法律/媒体回应、大规模外发。

本库仅定义文档级工作流约束；机器可读 Workflow Schema、受控调用和 Runtime Orchestrator 验证属于后续独立阶段，当前版本不得被解释为已具备自动执行能力。

## Versioning

- Library version: 1.0
- Runtime dependency: Agent Runtime Contract 1.0
- Review cadence: 每月复查；真实升级案例发生后及时更新。
