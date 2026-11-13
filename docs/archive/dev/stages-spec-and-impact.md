# 阶段 4-5：SPEC v0 与影响分析

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


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
