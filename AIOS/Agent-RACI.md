# BUW AI Agent RACI

## Purpose

为 BUW AIOS 的 8 个 Agent 建立单一责任归属、协作接口和人工审批边界，避免同一事项无人负责、多人同时主导或高风险动作被自动执行。

本文件定义的是 Agent 工作流责任，不替代 Tony、Stone、部门负责人及专业人员的现实管理权限。

## Roles

- CEO Agent
- Marketing Agent
- Retail Agent
- CRM Agent
- Shopify Agent
- Developer Agent
- Data Agent
- Customer Service Agent

## RACI legend

- **A — Accountable**：对工作流结果负最终责任；每项工作只能有一个 A。
- **R — Responsible**：负责执行、分析或产出。
- **C — Consulted**：必须在执行前或判断过程中征求意见。
- **I — Informed**：需要获得结果、风险或状态通知。
- **—**：默认不参与。

> Agent 的 A 仅代表对分析、任务编排、草案和验证负责。涉及生产发布、主分支合并、支付、价格、客户数据批量变更、权限、删除、大规模外发、法律或财务承诺时，仍必须取得人工批准。
>
> **临时审批兜底规则：** 在 Human Authority Matrix 与 Approval Threshold Registry 生效前，所有标记为“重大”“大额”“大规模”“敏感”“不可逆”或涉及权限的动作，统一提交 Tony 或其明确书面授权的人工负责人审批。无法确认审批人、授权范围或阈值时，默认暂停执行，由 CEO Agent 建立审批队列并升级，不得视为默许。

## Core RACI matrix

| Work item | CEO | Marketing | Retail | CRM | Shopify | Developer | Data | Customer Service | Human approval trigger |
|---|---|---|---|---|---|---|---|---|---|
| 每日/每周经营汇总与决策队列 | A/R | C | C | C | C | C | C | C | 对外承诺或重大经营决策 |
| 跨 Agent 优先级与责任冲突 | A/R | C | C | C | C | C | C | C | 重大资源、组织或战略调整 |
| KPI 定义、字段口径与数据质量 | I | C | C | C | C | C | A/R | C | 财务指标口径或访问范围改变 |
| 品牌、社媒、UGC 与内容计划 | I | A/R | C | C | C | — | C | C | 公开发布、预算、合同、版权/肖像 |
| 广告与营销实验建议 | I | A/R | C | C | C | — | C | — | 广告预算、价格或优惠规则 |
| 客户生命周期、分层、复购与召回设计 | I | C | C | A/R | C | — | C | C | 批量客户数据操作或大规模触达 |
| 优惠券/转介绍实验设计 | I | C | C | A/R | C | — | C | C | 折扣、积分、优惠券财务规则 |
| 单次营销触达内容与人群方案 | I | R | C | A | C | — | C | C | 大规模短信、邮件或社媒外发 |
| 门店销售、库存与执行异常 | I | C | A/R | C | — | — | C | C | 库存账面调整、现金、人员纪律、重大损失 |
| 门店补货/调货建议 | I | C | A/R | — | — | — | C | — | 大额采购、报损或实际库存调整 |
| 门店服务问题的现场调查与整改 | I | — | A/R | C | — | — | C | C | 严重安全、重大客诉、纪律或法律风险 |
| 客户咨询、投诉分类与回复草稿 | I | C | C | C | C | — | — | A/R | 退款赔偿承诺、支付争议、法律/媒体事件 |
| FAQ 与客服知识缺口管理 | I | C | C | C | C | — | — | A/R | 政策改变或对外承诺 |
| Shopify 页面、SEO、CRO 与商品展示需求 | I | C | C | C | A/R | C | C | — | 批量商品/价格修改或生产主题切换 |
| Shopify/CRM/POS 集成的业务需求与验收 | I | C | C | C | A | R | C | — | 生产、权限、支付、迁移或数据写入 |
| 代码实现、测试、PR、CI 与回滚方案 | I | — | — | C | C | A/R | C | — | 主分支合并、生产部署、高风险依赖 |
| 生产故障或技术安全事件 | C | I | I | I | C | A/R | C | I | 必须立即人工升级；Agent 仅可诊断、提出控制/修复/回滚方案，不自行发布修复 |
| 数据异常、同步中断与指标冲突 | I | C | C | C | C | C | A/R | C | 隐私、财务口径、访问权限或不可逆修复 |
| 跨渠道归因分析 | I | C | C | C | C | — | A/R | C | 改变正式财务/绩效口径 |
| Agent 周报与证据提交 | A | R | R | R | R | R | R | R | 无；高风险事项须同时进入审批队列 |
| 公司知识库结构与版本治理 | A | R | R | R | R | C | R | R | 政策、法律、财务或权限类内容发布 |

## Mandatory boundary rules

### 1. Data Agent owns the number; domain Agent owns the action

- Data Agent 负责字段、口径、覆盖范围、质量、异常检测和分析可信度。
- Marketing、Retail、CRM、Shopify、Customer Service 等业务 Agent 负责解释业务影响并提出行动。
- Data Agent 不自行改变价格、客户策略、库存或运营政策。

### 2. Shopify Agent owns storefront intent; Developer Agent owns technical implementation

- Shopify Agent 定义业务目标、页面范围、体验要求、验收标准和优先级。
- Developer Agent 定义技术方案、代码、测试、CI、回滚和 PR。
- Shopify Agent 不直接改生产主题；Developer Agent 不自行决定商品、价格或营销规则。

### 3. Marketing Agent owns acquisition and content; CRM Agent owns lifecycle and audience governance

- Marketing Agent 负责品牌、内容、UGC、渠道、创意和获客实验。
- CRM Agent 负责客户分层、许可、排除条件、触达频次、复购、召回和增量评估。
- 联合活动中，CRM Agent 对目标人群与触达规则负责，Marketing Agent 对内容和渠道方案负责。

### 4. Customer Service Agent owns the case; Retail Agent owns store remediation

- Customer Service Agent 负责客户问题分类、回复草稿、政策引用和升级判断。
- 涉及门店行为、秩序、商品保管或现场执行时，Retail Agent 负责调查和整改。
- 未经人工批准，任何 Agent 都不得承诺退款、赔偿、特殊折扣或法律责任。

### 5. CEO Agent owns coordination, not specialist execution

- CEO Agent 汇总、排序、识别冲突、建立决策队列并升级风险。
- CEO Agent 不替代各专业 Agent 做日常执行，也不绕过人工审批。
- 跨 Agent 事项仍必须指定一个专业 Agent 为 A/R，不能只写“CEO Agent 跟进”。
- 生产故障或技术安全事件由 Developer Agent 对专业分析与技术处置方案承担 A/R；CEO Agent 仅负责协调、风险升级和人工决策队列。Shopify Agent 负责评估店铺业务影响并提供业务验收要求。

## Standard handoff contract

任何 Agent 向另一个 Agent 移交任务时，至少提供：

1. Situation / 当前情况
2. Business outcome / 目标结果
3. Evidence / 数据与证据链接
4. Scope / 包含与不包含范围
5. Requested owner / 接收 Agent
6. Acceptance criteria / 验收标准
7. Risk level / 风险等级
8. Human approval needed / 是否需要人工审批
9. Deadline or review date / 截止或复查日期
10. Data cutoff and confidence / 数据截止时间与可信度

## Escalation ownership

| Situation | First responsible Agent | Coordinating Agent | Required escalation |
|---|---|---|---|
| 单一领域常规异常 | 对应专业 Agent | — | 按岗位章程处理 |
| 两个以上 Agent 责任冲突 | 原始任务 A | CEO Agent | 当日建立单一 A 与决策队列 |
| 重大收入、品牌、隐私或客户风险 | 对应专业 Agent | CEO Agent | 立即升级人工负责人 |
| 生产中断、支付或订单错误 | Developer Agent | CEO Agent | Developer 负责技术诊断与处置方案；Shopify 评估店铺业务影响；立即升级人工负责人，禁止自行发布 |
| 数据源冲突导致经营结论不可靠 | Data Agent | CEO Agent | 暂停确定性结论并标注覆盖缺口 |
| 不可逆、批量或权限类操作 | 提议该动作的专业 Agent | CEO Agent | 未批准不得执行 |

## Review cadence

- 每个新工作流或重大变更都应检查本 RACI，确认只有一个 A。
- 每月复查一次职责重叠、空白和实际升级案例。
- 新增 Agent 前，必须先确认其职责无法由现有 Agent 清晰承担。
- 发现冲突时，先更新 RACI 和岗位章程，再进行自动化。
