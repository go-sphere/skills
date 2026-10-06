# 阶段 6-8：API / Proto、Schema、Task Plan

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


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
- `db-schema-designer`
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
