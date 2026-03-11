# AI Agent 协作开发提示词指南

本文档提供从"简单 PRD + 原型 demo"到可交付成果的完整提示词模板。

## 前提假设

- PRD 位置：`/Users/tbxark/Repos/go-sphere/skills/PRD.md`
- Demo 位置：`/Users/tbxark/Repos/go-sphere/skills/demo`
- 输出目录：`prd/`、`design/changes/<change-id>/`

## 目录

1. [标准开发流程](#标准开发流程)
2. [每轮提示词模板](#每轮提示词模板)
3. [最小流程](#最小流程)
4. [总结表格](#总结表格)

---

## 标准开发流程

```
PRD + Demo
    │
    ▼
PRD 固化 ──────► prd/PRD.md
    │
    ▼
UX 语义化 ────► prd/UX-FLOWS.md
    │
    ▼
SPEC v0 ──────► prd/SPEC.md
    │
    ▼
影响分析 ────► design/changes/<change-id>/
    │
    ▼
API 设计 ────► prd/API.md
    │
    ▼
Schema 设计 ──► prd/DDL.md
    │
    ▼
实现 ────────► 代码改动
    │
    ▼
测试/验证 ───► validation-report.md
```

---

## 每轮提示词模板

### 第一轮：PRD 固化

**Skill**: `/prd`

**提示词**:
```
我有一个简单的 PRD 需要完善。

输入：
- 当前 PRD: /Users/tbxark/Repos/go-sphere/skills/PRD.md
- 项目目标：从"简单 PRD"推进到可交付成果

请根据 dev.md 中的 PRD 固化标准，完善以下内容：
1. 背景与目标
2. 用户角色
3. 核心业务流程
4. 模块边界
5. 页面/场景清单
6. 成功标准
7. 范围/非范围
8. 风险与依赖

输出到: prd/PRD.md
```

---

### 第二轮：UX / Demo 语义化

**Skill**: `/ux-analyst`

**提示词**:
```
我需要把原型 demo 语义化。

输入：
- PRD: prd/PRD.md
- Demo 目录: /Users/tbxark/Repos/go-sphere/skills/demo

请根据 dev.md 中的 UX 语义化标准，产出：
- prd/UX-FLOWS.md

包含内容：
- 每个关键页面的目的
- 页面进入条件
- 页面退出条件
- 关键按钮触发的业务动作
- 用户可见状态
- 阻断情况
- 异常提示情况

demo 是"行为参考"还是"视觉参考"：行为参考
```

---

### 第三轮：SPEC v0

**Skill**: `/spec-writer`

**提示词**:
```
我需要产出系统契约 SPEC。

输入：
- PRD: prd/PRD.md
- UX-FLOWS: prd/UX-FLOWS.md

请根据 dev.md 中的 SPEC v0 标准，产出：
- prd/SPEC.md

必须包含：
1. Problem Statement
2. Goals / Non-Goals
3. System Overview
4. Core Domain Model（领域对象、authoritative state、derived state）
5. Contracts / Configuration（接口/文件/事件是 contract）
6. Workflows / State Changes（状态机、外部/内部状态、合法转换）
7. Failure Handling / Observability
8. Validation / Testing
9. Migration / Compatibility
10. Open Questions

重点写清楚：
- 状态机规则
- 失败与恢复
- 合同语义
- authoritative source
```

---

### 第四轮：影响分析

**Skill**: `/spec-diff-pipeline`

**提示词**:
```
我需要对 SPEC 做影响分析。

输入：
- SPEC: prd/SPEC.md
- 当前 repo 结构

请产出：
- design/changes/<change-id>/ 目录下的文档

必须包含：
1. 00-inputs.md - 输入清单
2. 01-spec-delta.md - 变更摘要、变更类型
3. 02-impact-map.md - 影响映射（API/schema/surface/tests）
4. 03-api-delta.md - API 变更
5. 04-schema-delta.md - Schema 变更
6. 05-task-plan.md - 实施任务拆分

任务分层：
- Contract Layer
- Schema Layer
- Service Layer
- Surface Layer
- Test Layer
```

---

### 第五轮：API 设计

**Skill**: `/proto-api-generator`

**提示词**:
```
我需要设计 API/proto。

输入：
- SPEC: prd/SPEC.md
- API delta: design/changes/<change-id>/03-api-delta.md

请产出：
- prd/API.md
- proto 设计草案（如需要）

必须包含：
1. 服务边界
2. 路径或 RPC
3. 请求/响应消息
4. enum
5. 错误码
6. 分页/过滤/排序
7. 幂等语义
8. 兼容性说明
```

---

### 第六轮：Schema 设计

**Skill**: `/ent-schema-generator`

**提示词**:
```
我需要设计数据库 Schema。

输入：
- SPEC: prd/SPEC.md
- Schema delta: design/changes/<change-id>/04-schema-delta.md

请产出：
- prd/DDL.md 或 schema design note

必须包含：
1. 实体列表
2. 字段列表、类型、约束
3. 枚举
4. 索引
5. 关系
6. authoritative vs derived 决策
7. migration notes

重点：
- 哪些状态只是派生视图，不要落库
- 哪些字段归档后只读
- 哪些字段用于幂等或补偿
```

---

### 第七轮：实现

**Skill**: `/sphere-feature-workflow`

**提示词**:
```
我需要实现功能。

输入：
- SPEC: prd/SPEC.md
- API: prd/API.md
- Schema: prd/DDL.md
- Task Plan: design/changes/<change-id>/05-task-plan.md

任务：按 task plan 分层实现

请根据 sphere-layout 规范：
1. 先改 proto contract
2. 再改 schema
3. 再实现 service 逻辑
4. 最后验证

遵循：
- source-of-truth file
- generated boundary
- workflow type
- validation command
```

---

### 第八轮：测试数据生成（如需要）

**Skill**: `/ent-seed-sql-generator`

**提示词**:
```
我需要生成测试数据。

输入：
- Schema: prd/DDL.md 或 ent schema 文件

请生成：
- 可执行的 SQL seed 数据

确保：
- 实体关系完整性
- 稳定 ID
- dialect-specific SQL（JSON、array 等）
```

---

### 第九轮：Admin 页面生成（如需要）

**Skill**: `/pure-admin-crud-generator`

**提示词**:
```
我需要生成 Admin 页面。

输入：
- API 定义: src/api/swagger/Api.ts（已有 API 方法）
- PRD: prd/PRD.md
- SPEC: prd/SPEC.md

请生成：
- CRUD 页面
- 路由模块

遵循 pure-admin-thin 规范
```

---

## 最小流程

如果不想一开始搞太重，可以用简化版：

| 轮次 | Skill | 产出 |
|------|-------|------|
| 1 | `/prd` | prd/PRD.md |
| 2 | `/ux-analyst` | prd/UX-FLOWS.md |
| 3 | `/spec-writer` | prd/SPEC.md |
| 4 | `/spec-diff-pipeline` | design/changes/.../05-task-plan.md |
| 5 | `/sphere-feature-workflow` | 代码实现 |

---

## 总结表格

| 轮次 | Skill | 产出 | 必选 |
|------|-------|------|------|
| 1 | `/prd` | prd/PRD.md | ✅ |
| 2 | `/ux-analyst` | prd/UX-FLOWS.md | ✅ |
| 3 | `/spec-writer` | prd/SPEC.md | ✅ |
| 4 | `/spec-diff-pipeline` | design/changes/... | ✅ |
| 5 | `/proto-api-generator` | prd/API.md | 可选 |
| 6 | `/ent-schema-generator` | prd/DDL.md | 可选 |
| 7 | `/sphere-feature-workflow` | 代码 | ✅ |
| 8 | `/ent-seed-sql-generator` | seed SQL | 可选 |
| 9 | `/pure-admin-crud-generator` | Admin 页面 | 可选 |

---

## 上下文优先级

根据 dev.md 中的最佳实践：

- **写代码时**：`SPEC` 为主，`PRD` 为辅
- **写前端时**：`PRD` + `UX-FLOWS` + `SPEC` + `API`
- **做 review 时**：`SPEC` + 代码 diff
- **按任务摘取**相关章节，而不是整份全塞
