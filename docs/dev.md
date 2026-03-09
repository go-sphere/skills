# AI Agent 协作开发流程规范

适用范围：从“简单 PRD + 原型 demo”推进到可上线交付成果的研发场景。  
文档目标：提供一套比较完整、适合 AI Agent 协作的开发流程，并按真实工程顺序说明每一步的：

- 目标
- 主要 agent 角色
- 输入
- 输出文档
- 文档需要写到什么细节
- 这一阶段什么时候算完成

## 目录

1. [总体流程](#总体流程)
2. [标准开发流程](#标准开发流程)
3. [文档颗粒度标准](#文档颗粒度标准)
4. [推荐目录结构](#推荐目录结构)
5. [AI Agent 角色分工](#ai-agent-角色分工)
6. [最小可执行版本](#最小可执行版本)
7. [AI 上下文使用策略](#ai-上下文使用策略)
8. [任务类型与上下文矩阵](#任务类型与上下文矩阵)
9. [上下文选择速查](#上下文选择速查)
10. [上下文使用最佳实践](#上下文使用最佳实践)

## 总体流程

从 `简单 PRD + 原型 demo` 到最终成果，建议走这条主线：

1. `Intake / 对齐输入`
2. `PRD 固化`
3. `UX / Demo 语义化`
4. `SPEC v0`
5. `影响分析与 change pipeline`
6. `API / Proto 设计`
7. `Domain / Schema 设计`
8. `Task Plan / 实施拆分`
9. `实现`
10. `验证 / 测试 / Review`
11. `发布准备`
12. `运行后反馈再迭代`

最重要的原则是：

**每一层文档只负责一层问题，不要混写。**

---

## 标准开发流程

### 1. Intake / 对齐输入

#### 目标
把零散输入整理成一个明确起点。

#### 输入
- 初始 PRD
- 原型 demo
  - Figma
  - HTML demo
  - 截图
  - 视频
  - 交互说明
- 任何已有代码仓库
- 用户补充口头描述

#### 输出文档
- `docs/00-intake.md`

#### `00-intake.md` 应包含
- 项目目标一句话
- 当前已有输入清单
- 缺失输入清单
- 已确认的主要角色
- 已确认的主要模块
- demo 是“视觉参考”还是“行为参考”
- 现有代码/仓库边界
- 不确定项列表

#### 需要的细节
不要写长。重点是把输入边界钉住。

#### 完成标准
- 团队和 AI 都知道“现在有哪些真实输入”
- 知道哪些东西是事实，哪些只是草图

---

### 2. PRD 固化

#### 目标
把产品目标和业务流程说清楚，但不进入工程实现。

#### 关于本节 `agent` 的说明
- 本文中的 `*-agent` 默认表示“逻辑角色 / 职责分工”，不是 Codex、Claude 或其他平台内置的固定 agent 名称。
- 实际落地时，可以由同一个主 Agent 通过不同提示词切换角色完成，也可以在支持多代理的平台中拆成多个子任务并行执行。
- 如果仓库里存在真实 skill，应优先使用 skill；如果没有，就把这些名字理解为“这一步应该由什么能力来完成”。

#### 主要 agent
- `product-agent`
- 注：负责澄清业务目标、范围和成功标准。通常不是现成 skill，而是“产品经理式提示词角色”。
- `requirements-agent`
- 注：负责把口头需求、demo 和约束整理成结构化需求。通常与 `product-agent` 可由同一个 Agent 兼任。

#### 输入
- `00-intake.md`
- demo / 原型
- 用户补充

#### 输出文档
- `prd/PRD.md`

#### `PRD.md` 应包含
1. 背景与目标
2. 用户角色
3. 核心业务流程
4. 模块边界
5. 页面 / 场景清单
6. 成功标准
7. 范围 / 非范围
8. 风险与依赖

#### 需要的细节
PRD 要回答这些问题：
- 谁在用
- 什么时候用
- 做成什么样才算成功
- 哪些功能必须做
- 哪些这次不做

PRD 不需要写：
- 字段类型
- 数据表
- 状态机细节
- API 返回结构

#### 完成标准
- 看完 PRD，可以知道产品做什么
- 但还不能直接写代码，这很正常

---

### 3. UX / Demo 语义化

#### 目标
把原型 demo 从“视觉表现”转成“行为语义”。

#### 主要 agent
- `ux-analysis-agent`
- 注：负责把界面和交互稿翻译成业务行为与状态，不是平台内置 agent。
- `frontend-reading-agent`
- 注：负责从前端原型、页面结构或交互细节中抽取实现语义；通常也是提示词角色。

#### 输入
- PRD
- Figma / demo / 截图 / 视频

#### 输出文档
- `prd/UX-FLOWS.md`
- 可选：`prd/SCREEN-INVENTORY.md`

#### `UX-FLOWS.md` 应包含
- 每个关键页面的目的
- 页面进入条件
- 页面退出条件
- 关键按钮触发的业务动作
- 用户可见状态
- 阻断情况
- 异常提示情况

#### 需要的细节
例如不要只写：
- “点击提交按钮”

而要写：
- 提交按钮什么时候可点
- 提交后会不会推进状态
- 失败时提示什么
- 成功后跳转去哪
- 是否允许中断后恢复

#### 完成标准
- demo 中的行为都被翻译成业务动作
- 页面不再只是 UI 图，而是业务流程节点

---

### 4. SPEC v0

#### 目标
把 PRD 和 UX 行为压成系统契约。

#### 主要 agent
- `spec-writer`
- `architecture-agent`

#### 输入
- `PRD.md`
- `UX-FLOWS.md`
- 现有代码和仓库结构

#### 输出文档
- `prd/SPEC.md`

#### `SPEC.md` 至少应包含
1. Problem Statement
2. Goals / Non-Goals
3. System Overview
4. Core Domain Model
5. Contracts / Configuration
6. Workflows / State Changes
7. Failure Handling / Observability
8. Validation / Testing
9. Migration / Compatibility
10. Open Questions

#### `SPEC.md` 需要的细节
这是最关键的文档。要写到这些层面：

##### 1. 领域对象
- 核心实体有哪些
- 哪些是 authoritative state
- 哪些是 derived state
- 每个对象的 canonical identifier 是什么

##### 2. 状态机
- 外部状态
- 内部状态
- 合法状态转换
- 触发器
- guard condition
- side effect

##### 3. 合同
- 哪些接口/文件/事件是 contract
- contract discovery / version / validation
- 错误语义

##### 4. 配置语义
- 默认值
- 优先级
- 动态 reload 还是 restart-required
- invalid config 怎么处理

##### 5. 失败与恢复
- 什么会阻断
- 什么会重试
- 什么进入补偿流程
- 重启后怎么恢复

##### 6. 测试与验收
- 哪些行为必须被验证
- 哪些场景是关键回归场景

#### 完成标准
- 不看 PRD，只看 SPEC，另一个工程师或 AI 也能大体实现兼容行为

---

### 5. 影响分析与 Change Pipeline

#### 目标
每次 `SPEC` 变化后，自动推导下游影响。

#### 主要 agent
- `spec-diff-pipeline`

#### 输入
- `SPEC.md` 当前版本
- git diff
- repo 结构
- 当前 API / schema / source-of-truth files

#### 输出文档
放在：
- `design/changes/<change-id>/`

包括：
- `00-inputs.md`
- `01-spec-delta.md`
- `02-impact-map.md`
- `03-api-delta.md`
- `04-schema-delta.md`
- `surface-<name>-impact.md`（按需）
- `05-task-plan.md`
- `06-open-questions.md`（按需）

#### 每个文档的细节

##### `01-spec-delta.md`
写：
- 变更摘要
- 变更类型：`additive / behavioral / breaking / deepening / mixed`
- 具体变了哪些语义
- 影响哪些 contract area

##### `02-impact-map.md`
写：
- enums/states 影响
- API/route 影响
- schema/entity 影响
- service/orchestration 影响
- surface 影响
- tests 影响
- compatibility 风险

##### `03-api-delta.md`
写：
- 哪些 service boundary 要变
- 哪些 route/RPC 要变
- 请求响应 contract 怎么变
- 哪些 enum/error 受影响
- candidate files

##### `04-schema-delta.md`
写：
- 哪些实体变了
- 哪些字段变了
- 哪些状态需要落库
- 索引/query shape 影响
- migration note
- authoritative vs derived decision

##### `surface-*.md`
例如 `surface-mobile-impact.md`
写：
- 为什么这个 surface 受影响
- 它消费了什么新 contract
- 哪些模块可能要改
- 行为上有什么变化
- 需要什么验证

##### `05-task-plan.md`
写：
- contract layer tasks
- schema layer tasks
- service layer tasks
- surface layer tasks
- test tasks
- generation / validation tasks

#### 完成标准
- 下游 agent 已经不需要再重新读整份 SPEC 才能开始工作

---

### 6. API / Proto 设计

#### 目标
从 `SPEC` 中提取对外 contract。

#### 主要 agent
- `proto-api-generator`
- `contract-agent`

#### 输入
- `SPEC.md`
- `03-api-delta.md`
- 现有 proto / API docs

#### 输出文档
- `prd/API.md`
- 需要时进一步生成 `.proto` 设计草案

#### API 文档需要的细节
1. 服务边界
2. 路径或 RPC
3. 请求消息
4. 响应消息
5. enum
6. 错误码
7. 分页 / 过滤 / 排序
8. 幂等语义
9. 兼容性说明

#### 文档应该写到什么程度
不要只写：
- `POST /api/task/submit`

要写：
- 请求字段
- 哪些字段必填
- 状态前置条件
- 成功后推进到哪个状态
- 失败错误码有哪些
- 是否幂等
- 重复请求如何处理

#### 完成标准
- API 已经足够让 backend 和 client 分头工作
- 不需要再靠聊天解释接口语义

---

### 7. Domain / Schema 设计

#### 目标
把 `SPEC` 中的事实对象落到可持久化模型。

#### 主要 agent
- `ent-schema-generator`
- `data-model-agent`

#### 输入
- `SPEC.md`
- `04-schema-delta.md`
- 现有 DDL / Ent schema

#### 输出文档
- `prd/DDL.md`
- 或 schema design note
- 之后再落 ent schema

#### Schema 文档需要的细节
1. 实体列表
2. 字段列表
3. 类型
4. 约束
5. 枚举
6. 索引
7. 关系
8. authoritative vs derived
9. migration notes

#### 要特别写清
- 哪些状态只是派生视图，不要落库
- 哪些字段归档后只读
- 哪些对象要审计
- 哪些字段用于幂等或补偿
- 哪些字段是 runtime snapshot

#### 完成标准
- 数据模型能支撑 SPEC 的状态机和审计要求
- 不是按页面堆表，而是按业务事实建模

---

### 8. Task Plan / 实施拆分

#### 目标
把设计变成可执行工作包。

#### 主要 agent
- `planning-agent`
- `orchestrator-agent`

#### 输入
- `05-task-plan.md`
- API / schema delta
- repo conventions

#### 输出文档
- `design/tasks/<change-id>.md`
- 或直接在 `05-task-plan.md` 中保留执行版

#### Task Plan 需要的细节
任务应分层：

1. Contract Layer
- 改哪些 proto / API contract
- 哪些错误码新增

2. Schema Layer
- 哪些 ent schema / DDL 改动
- 哪些 migration 风险

3. Service Layer
- 哪些 service / dao / orchestration 改动

4. Surface Layer
- mobile / dashboard / web / sdk 哪些模块消费新能力

5. Test Layer
- 单元测试
- 集成测试
- E2E 验证点

每个任务最好包含：
- 输入依赖
- 目标文件/目录
- 完成标准
- 是否会触发代码生成
- 是否可能 breaking

#### 完成标准
- 可以把任务分发给多个 agent 并行做
- 不需要每个 agent 再自己拆需求

---

### 9. 实现

#### 目标
按任务分层落代码。

#### 主要 agent
- `sphere-feature-workflow`
- service / frontend / review agents

#### 输入
- `05-task-plan.md`
- API 文档
- schema 文档
- repo conventions

#### 输出
- 代码改动
- 生成文件
- tests

#### 实现阶段文档
实现阶段不一定新增大文档，但至少应保留：
- `design/changes/<change-id>/implementation-notes.md`（可选）
- 或在 PR / commit message 中说明：
  - 改了什么
  - 为什么改
  - 对应哪个 spec/task

#### 需要的细节
AI agent 在这一步最容易偏，所以要强约束：
- source-of-truth file
- generated boundary
- workflow type
- validation command

#### 完成标准
- 代码与文档一致
- 没有出现“文档说一套，代码做另一套”

---

### 10. 验证 / 测试 / Review

#### 目标
验证实现符合 SPEC，不只是能跑。

#### 主要 agent
- `test-agent`
- `review-agent`
- `qa-agent`

#### 输入
- SPEC
- task plan
- 实现代码

#### 输出文档
- `design/changes/<change-id>/validation-report.md`

#### `validation-report.md` 应包含
- 测试范围
- 已执行测试
- 关键状态机用例
- 幂等验证结果
- 失败恢复验证结果
- 残留风险
- 未覆盖项

#### 重点验证什么
1. happy path
2. illegal transition
3. permission denied
4. threshold blocked
5. duplicate submission
6. archive failure + retry
7. restart / resume / draft recovery
8. surface-level compatibility

#### 完成标准
- 实现行为能映射回 SPEC 中的规则
- 不只是“接口通了”

---

### 11. 发布准备

#### 目标
把系统从“实现完成”推进到“可上线”。

#### 主要 agent
- `release-agent`
- `ops-agent`

#### 输出文档
- `ops/release-plan.md`
- `ops/runbook.md`
- `ops/migration-plan.md`（如需要）

#### 文档需要的细节

##### `release-plan.md`
- 发布范围
- 发布顺序
- 是否有 breaking change
- 是否要分阶段开关

##### `migration-plan.md`
- 数据迁移步骤
- 回滚策略
- 双写 / 兼容窗口（如需要）

##### `runbook.md`
- 常见故障
- 如何排查
- 如何补偿
- 哪些指标/日志要看

#### 完成标准
- 发布风险已被显式管理
- 出问题时知道怎么处理

---

### 12. 运行后反馈再迭代

#### 目标
上线后继续用 AI 驱动文档和实现同步演化。

#### 主要 agent
- `incident-agent`
- `spec-diff-pipeline`
- `review-agent`

#### 输入
- 线上反馈
- bug
- 指标
- 客户诉求
- 新需求

#### 输出
- capability gap note
- 新 spec diff
- 新 impact bundle

#### 核心做法
任何新增需求或线上问题，重新进入：

`Capability Gap -> SPEC 更新 -> spec-diff-pipeline -> API/schema/task -> implementation`

这样整个体系是闭环的。

---

## 文档颗粒度标准

这是最关键的问题。可以用这个标准判断：

### PRD 的细度
写到“人能理解产品要做什么”。

不需要写：
- 字段类型
- 错误码
- 内部状态机

### SPEC 的细度
写到“工程师或 AI 能实现兼容行为”。

必须写：
- 状态
- 规则
- 阻断
- 失败
- 恢复
- 配置语义
- authoritative source

### API 文档的细度
写到“前后端可以并行开发”。

必须写：
- request / response
- 前置条件
- 幂等
- 错误码
- 兼容性

### Schema 文档的细度
写到“数据层不会和业务层冲突”。

必须写：
- 实体
- 字段
- 约束
- 状态落库策略
- 索引
- migration

### Task Plan 的细度
写到“另一个 agent 可以独立执行一个 batch”。

必须写：
- 任务边界
- 输入依赖
- 目标文件/目录
- 完成标准

### Validation 文档的细度
写到“知道验证了什么，没验证什么”。

必须写：
- 核心场景
- 失败场景
- 残留风险

---

## 推荐目录结构

```text
prd/
  PRD.md
  UX-FLOWS.md
  SPEC.md
  API.md
  DDL.md

design/changes/<change-id>/
  00-inputs.md
  01-spec-delta.md
  02-impact-map.md
  03-api-delta.md
  04-schema-delta.md
  surface-mobile-impact.md
  surface-dashboard-impact.md
  05-task-plan.md
  06-open-questions.md
  validation-report.md

ops/
  release-plan.md
  migration-plan.md
  runbook.md
```

小项目可以合并文档，大项目建议分开。

---

## AI Agent 角色分工

说明：
- 下表中的大部分名称是推荐的“逻辑角色”，用于描述职责边界，不代表 Codex / Claude 内置就有这个 agent。
- 真实可直接落地的能力通常来自两类：`skill`，或平台提供的子代理机制。
- 本仓库里更接近“真实可用能力”的是：`proto-api-generator`、`ent-schema-generator`、`sphere-feature-workflow` 等 skill。

1. `intake-agent`
- 整理输入
- 注：负责收集原始材料、边界和缺失项；通常由主 Agent 直接完成。

2. `prd-agent`
- 产出 PRD
- 注：偏产品与需求整理角色，通常不是独立 skill。

3. `ux-agent`
- 把 demo 行为语义化
- 注：偏 UX/交互分析角色，负责把界面翻译成可执行行为。

4. `spec-agent`
- 写 SPEC
- 注：偏系统设计角色，负责把业务目标压成工程契约。

5. `spec-diff-pipeline`
- 每次变更后做影响分析和任务拆分
- 注：这是一个“流程能力”名称，不一定是平台里的单个 agent；可以由主 Agent 按固定模板执行。

6. `api-agent`
- 设计 API/proto
- 注：如果仓库已有 `proto-api-generator` skill，优先用 skill；这里的 `api-agent` 只是职责名。

7. `schema-agent`
- 设计 schema/DDL/Ent
- 注：如果仓库已有 `ent-schema-generator` skill，优先用 skill；这里的 `schema-agent` 只是职责名。

8. `planning-agent`
- 拆任务
- 注：负责把设计拆成可并行执行的工作包，通常由主 Agent 或 orchestrator 完成。

9. `implementation-agent`
- 落代码
- 注：实现角色；在本仓库内更接近真实能力的是 `sphere-feature-workflow` 这类 skill。

10. `review-agent`
- 做变更 review
- 注：负责从规格、回归和风险角度审查实现，不代表平台内置 reviewer。

11. `qa-agent`
- 做验证报告
- 注：负责测试覆盖、验收映射和残留风险整理。

12. `release-agent`
- 准备发布和 runbook
- 注：负责发布计划、迁移步骤和运行手册整理。

---

## 最小可执行版本

如果你不想一开始搞太重，可以先用这套简化版：

### 最小流程
1. `PRD.md`
2. `UX-FLOWS.md`
3. `SPEC.md`
4. `spec-diff-pipeline` 产出：
   - `01-spec-delta.md`
   - `02-impact-map.md`
   - `03-api-delta.md`
   - `04-schema-delta.md`
   - `05-task-plan.md`
5. AI 实现
6. `validation-report.md`

这已经足够支撑大多数中小型 AI 协作开发。

---

## 可选补充产物

如果需要，下一步可以继续补齐两样很实用的内容：

1. 一套 **可直接复制使用的文档模板**
   - `PRD.md`
   - `UX-FLOWS.md`
   - `SPEC.md`
   - `API.md`
   - `DDL.md`

2. 一套 **AI Agent 编排蓝图**
   - 哪一步由哪个 agent 做
   - 哪一步可以并行
   - 哪一步必须人工 gate

## AI 上下文使用策略

### 实现代码时是否要同时提供 `PRD` 和 `SPEC`

要，但不是无脑两个都全塞。

更实用的原则是：

**实现代码时，`SPEC` 是主上下文，`PRD` 是辅助上下文。**

---

**为什么**

**PRD**
- 提供业务意图
- 防止代码实现偏离产品目标
- 适合回答“为什么这么做”

**SPEC**
- 提供工程约束
- 决定状态、字段、接口、失败语义、边界
- 适合回答“具体应该怎么做”

真正写代码时，AI 更需要的是 `SPEC`，因为代码实现依赖的是契约，不是愿景。

---

**推荐用法**

### 1. 写代码时默认给 `SPEC`
适用于：
- 写 service
- 写 API
- 写 schema
- 写状态机
- 写测试

因为这些都直接依赖技术语义。

### 2. 只在这些情况补 `PRD`
适用于：
- 需求还模糊
- 某个实现要判断业务优先级
- 需要理解用户流程或页面目的
- `SPEC` 写得还不够完整
- 做 UI / 前端行为实现

这时 `PRD` 是补充，不是主约束。

---

**最稳的上下文组合**

### 场景 A：后端实现
给 AI：
- `SPEC.md`
- `API.md`
- `DDL.md` 或 schema 文件
- 相关代码目录

`PRD.md`：
- 可选
- 只在业务意图不清时补

### 场景 B：前端实现
给 AI：
- `PRD.md`
- `UX-FLOWS.md`
- `SPEC.md`
- `API.md`

因为前端同时关心：
- 业务流程
- 页面行为
- 接口契约

### 场景 C：改接口 / 改数据模型
给 AI：
- `SPEC.md`
- `spec diff artifacts`
- 当前 proto/schema

`PRD.md` 通常不用全给。

### 场景 D：做 code review
给 AI：
- 改动代码
- `SPEC.md`
- 必要时补 `PRD.md`

因为 review 更关心“实现有没有违背规格”。

---

**不要这样做**

### 1. 不要每次都把 PRD + SPEC 全量塞进去
问题：
- 噪音太大
- AI 更容易抓错重点
- 容易把业务描述和工程契约混在一起

### 2. 不要只有 PRD 没有 SPEC 就让 AI 大规模写代码
问题：
- 很容易写出“看起来对、实际边界松”的代码

### 3. 不要让 AI 自己从 PRD 推完整技术语义，除非你就是在让它写 SPEC
这是最容易漂的地方。

---

**最好的做法：按任务裁切上下文**

你可以把规则记成一句话：

**“谁离代码更近，就给谁。”**

- 写业务目标：给 `PRD`
- 写系统契约：给 `PRD + UX + demo`
- 写代码：给 `SPEC + API + Schema + 相关代码`
- 做校验：给 `SPEC + 变更代码`

---

**一个简单判断标准**

如果你要问 AI 的问题是：

- “这个功能到底是干嘛的？”
  - 看 `PRD`

- “这个状态什么时候推进？”
  - 看 `SPEC`

- “这个接口应该返回什么？”
  - 看 `API`

- “这个字段该不该落库？”
  - 看 `SPEC + Schema`

- “这段代码写得对不对？”
  - 看 `SPEC + 代码`

---

**最实用的上下文传递方式**

不是传“全部文档”，而是传“文档摘录 + 当前任务边界”。

例如你可以这样喂 AI：

```text
任务：实现验收提交逻辑

主要约束来源：
- SPEC: 6.4 Inspection Workflow
- SPEC: 8.1 Failure Classes
- API: SubmitInspection request/response
- Schema: task_equip_metrics

补充业务背景：
- PRD: 完工验收页面要求所有必填项完成后才能提交
```

这比直接扔整份 PRD 和 SPEC 效果好很多。

---

**一句话总结**

- `PRD` 不是不用给
- 但实现代码时，**`SPEC` 一定是主上下文**
- `PRD` 只在需要理解业务意图时作为补充
- 最好按任务摘取相关章节，而不是整份全塞

作为进一步延展，也可以继续整理以下对照表：

**“不同开发任务应该给 AI 哪些上下文”对照表**  
比如：
- 写 API
- 写 schema
- 写 service
- 写前端页面
- 写测试
- 做 review

以下是一套实用对照表。

核心原则先放前面：

**给 AI 的上下文，不是越多越好，而是越贴近当前任务越好。**

优先级通常是：

`当前任务直接相关的 SPEC / API / Schema / 代码 > PRD > 其他背景材料`

---

## 任务类型与上下文矩阵

---

### 1. 写 PRD

#### 任务目标
把想法、需求、demo 整理成业务文档。

#### 主要上下文
- 用户原始想法
- demo / 原型
- 截图 / Figma / 交互稿
- 竞品或参考流程
- 业务背景

#### 可选上下文
- 旧版 PRD
- 现有系统概述

#### 一般不需要
- API
- DDL
- service 代码

#### 为什么
这一步还在定义业务，不该被现有技术实现反向绑死。

---

### 2. 写 UX / 页面行为说明

#### 任务目标
把 demo 的视觉/交互转成行为语义。

#### 主要上下文
- PRD
- 原型 demo
- 页面截图 / Figma
- 用户流程说明

#### 可选上下文
- 现有 API（如果页面已经依赖后端）
- 现有前端代码

#### 一般不需要
- DDL
- 后端 service 实现

#### 为什么
这一步主要定义“页面在业务上怎么工作”，不是定义后端数据层。

---

### 3. 写 SPEC

#### 任务目标
把 PRD 和页面行为压成系统契约。

#### 主要上下文
- PRD
- UX / demo 行为说明
- 当前系统架构
- 现有代码仓库结构
- 现有 API / DDL（如果是增量改造）

#### 可选上下文
- 现有 proto / schema
- 相关历史设计文档

#### 一般不需要
- 太多实现细节代码
- 无关模块源码

#### 为什么
这一步的重点是把业务目标转成工程约束。

---

### 4. 修改 SPEC

#### 任务目标
对已有规格做增强、修正、扩展。

#### 主要上下文
- 当前 `SPEC.md`
- 变更原因
- 相关 PRD 片段
- 当前 API / Schema
- 当前 repo 结构

#### 可选上下文
- git diff
- 相关模块代码

#### 最重要的补充
- 这次变更是：
  - additive
  - behavioral
  - breaking
  - deepening

#### 为什么
改 SPEC 不是重写 PRD，而是改系统契约。

---

### 5. 根据 SPEC 跑 impact analysis

#### 任务目标
生成 impact map / api delta / schema delta / task plan。

#### 主要上下文
- `SPEC.md`
- `SPEC` 的 git diff
- repo 结构
- 当前 proto / API 文档
- 当前 schema / DDL / Ent schema
- 当前 surface 目录（mobile/dashboard/web/sdk 等）

#### 可选上下文
- PRD（只在需要理解业务背景时）
- 相关代码目录

#### 一般不需要
- 整个代码仓库的所有文件

#### 为什么
这一步的核心是“变更传播”，不是写实现。

---

### 6. 设计 API / Proto

#### 任务目标
从 SPEC 落接口 contract。

#### 主要上下文
- `SPEC.md`
- `03-api-delta.md`
- 当前 `API.md`
- 当前 proto 文件
- repo 框架约束（例如 go-sphere）

#### 可选上下文
- PRD 某些页面行为片段
- Schema 设计草案

#### 一般不需要
- 整份 PRD 全文
- 大量 service 实现

#### 为什么
API 设计靠 contract，不靠业务长文。

#### 额外建议
如果任务是改 API，最好只给 AI：
- 相关 SPEC 小节
- 相关 API diff artifact
- 相关 proto 文件

而不是全量文档。

---

### 7. 设计 DB Schema / Ent Schema

#### 任务目标
从 SPEC 落 authoritative data model。

#### 主要上下文
- `SPEC.md`
- `04-schema-delta.md`
- 当前 DDL
- 当前 Ent schema
- 当前 API contract（用于理解 query shape）

#### 可选上下文
- PRD 的业务流程片段
- task plan

#### 一般不需要
- 前端 demo
- 大量 UI 文案

#### 为什么
Schema 设计重点是事实建模，不是视觉行为。

---

### 8. 写后端 service

#### 任务目标
实现状态机、校验、编排、持久化逻辑。

#### 主要上下文
- `SPEC.md`
- `API.md` / proto
- Schema / Ent schema
- `05-task-plan.md`
- 当前相关 service / dao / render 代码

#### 可选上下文
- `PRD.md` 相关业务背景
- `validation-report` 历史问题

#### 一般不需要
- 整份 UX 文档
- 全量页面说明

#### 为什么
这一步依赖的是工程契约和本地代码上下文。

#### 最推荐的喂法
不要只说“实现这个功能”。

应该说：
- 任务目标
- 约束来自哪个 SPEC 小节
- 相关 proto / schema 文件
- 目标目录
- 不要修改哪些生成文件

---

### 9. 写前端页面

#### 任务目标
实现页面、交互和状态展示。

#### 主要上下文
- `PRD.md`
- `UX-FLOWS.md`
- `SPEC.md`
- `API.md`
- 当前前端代码 / design system

#### 可选上下文
- Dashboard/mobile/web 对应的 impact artifact
- demo/截图

#### 一般不需要
- DDL
- Ent schema 实现细节

#### 为什么
前端既关心业务体验，也关心接口契约，但不直接关心数据库。

---

### 10. 写 Dashboard / Admin 页面

#### 任务目标
实现运营 / 审核 / 监管界面。

#### 主要上下文
- `PRD.md`
- `SPEC.md`
- `API.md`
- `surface-dashboard-impact.md`
- 当前 dashboard 代码

#### 可选上下文
- 权限模型说明
- 运营流程文档

#### 一般不需要
- 移动端页面细节
- 底层 schema 细节（除非是调试）

#### 为什么
Dashboard 经常消费一些 internal state 和管理动作，所以它比普通前端更依赖 SPEC。

---

### 11. 写测试

#### 任务目标
验证实现是否符合规格。

#### 主要上下文
- `SPEC.md`
- `05-task-plan.md`
- API contract
- 当前实现代码

#### 可选上下文
- PRD 中的关键场景
- 历史 bug case

#### 最关键的上下文
- 状态机规则
- 幂等规则
- 阻断规则
- 恢复 / 补偿规则

#### 为什么
测试不是验证“看起来能用”，而是验证“符合 SPEC”。

---

### 12. 做 code review

#### 任务目标
判断代码改动是否存在 bug、语义偏差或回归。

#### 主要上下文
- 代码 diff
- `SPEC.md`
- 相关 API / Schema
- `05-task-plan.md`（可选）

#### 可选上下文
- `PRD.md`（只在想判断业务方向是否偏了时）

#### 一般不需要
- 全量 demo
- 大量无关代码

#### 为什么
review 更关心“是否违背规格”，不是重新理解产品愿景。

---

### 13. 做发布 / 运维文档

#### 任务目标
准备 release、migration、runbook。

#### 主要上下文
- `SPEC.md`
- `04-schema-delta.md`
- `05-task-plan.md`
- 当前部署方式
- 测试结果

#### 可选上下文
- PRD（用于理解业务优先级）
- Dashboard/admin 操作流程

#### 为什么
发布文档需要知道影响面和回滚点，不需要太多 UI 细节。

---

## 上下文选择速查

如果你不想记这么多分类，可以用这个简化规则：

---

### A. 偏业务问题
例如：
- 这个功能到底为什么存在？
- 用户在这个页面想完成什么？
- 这个流程的目标是什么？

给：
- `PRD`
- `UX-FLOWS`
- demo

---

### B. 偏系统规则问题
例如：
- 这个状态什么时候推进？
- 失败后应该怎么处理？
- 这个字段是不是 authoritative？
- 这个功能要不要阻断？

给：
- `SPEC`

---

### C. 偏系统边界问题
例如：
- 接口长什么样？
- 错误码如何设计？
- 哪些字段返回给前端？

给：
- `SPEC`
- `API/proto`

---

### D. 偏持久化问题
例如：
- 这个对象怎么落库？
- 这个状态要不要存？
- 哪个字段要加索引？

给：
- `SPEC`
- `Schema / DDL / Ent schema`

---

### E. 偏实现问题
例如：
- 这段 service 怎么写？
- 这个 handler 怎么改？
- 这条 query 怎么实现？

给：
- `SPEC`
- `API`
- `Schema`
- 当前代码

---

### F. 偏验证问题
例如：
- 这个实现是否符合要求？
- 需要测哪些场景？
- 这个变更是否有回归风险？

给：
- `SPEC`
- 代码 diff
- 相关 API / Schema

---

## 上下文使用最佳实践

最好的方式不是：

- 整份 PRD
- 整份 SPEC
- 整份 API
- 整份 DDL
- 全仓库代码

一起塞给 AI。

而是像这样：

```text
任务：实现验收提交接口

主要约束：
- SPEC 7.5 Inspection State Machine
- SPEC 8.1 Error Classes
- API.md 中 SubmitInspection contract
- DDL.md 中 task_equip_metrics
- 当前代码目录 internal/service/api/inspection.go

补充背景：
- PRD 中完工验收要求所有必填项完成后才能提交
```

这种效果远好于全塞。

---

## 上下文优先级建议

### 写代码时
1. 当前任务描述
2. 相关 SPEC 小节
3. 相关 API / Schema
4. 相关代码文件
5. PRD 片段

### 写前端时
1. 当前任务描述
2. PRD / UX-FLOWS
3. 相关 SPEC 小节
4. API contract
5. 当前前端代码

### 做 review 时
1. 代码 diff
2. 相关 SPEC 小节
3. API / Schema
4. PRD 片段（必要时）

---

### 什么时候必须把 PRD 和 SPEC 一起给

这些情况建议一起给：

1. 前端页面实现
- 因为既要理解业务目标，也要遵守系统规则

2. 从 0 到 1 新写功能
- AI 需要 PRD 理解“为什么”
- 需要 SPEC 理解“怎么做”

3. 功能存在多个合理实现路径
- PRD 帮助判断业务优先级
- SPEC 帮助判断工程约束

4. 做方案设计，不是直接写代码
- 这时 PRD 和 SPEC 都有价值

---

### 什么时候只给 SPEC 就够了

这些情况通常只给 SPEC 就够：

1. 改 service
2. 改状态机
3. 改 handler
4. 改错误码
5. 补测试
6. 做 code review
7. 跑 impact analysis

---

### 一句话结论

**实现代码时要给 AI 文档上下文，但默认以 `SPEC` 为主，`PRD` 为辅。**  
**最好的做法不是全量喂，而是按任务摘取相关章节。**

如需继续扩展，可进一步补充以下标准提示词模板：

**“给 AI 下开发任务时的标准提示词模板”**  
分别针对：
1. 写 API
2. 写 schema
3. 写 service
4. 写前端
5. 做 review
