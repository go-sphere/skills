# 任务上下文：API / Proto 与 Schema 设计

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。

策略原则见 `context-strategy.md`。

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
