# 第 6-10 轮：Schema、实现、测试数据、前端、精简

本文是 [AI Agent 协作开发提示词指南](../prompt.md) 的一部分。流程总览、最小流程和总结表格见索引文档。

### 第六轮：Schema 设计

**Skill**: `/db-schema-designer`

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

### 第九轮：前端页面与路由生成（如需要）

**Skill**: `/frontend-crud-generator`

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

遵循项目既有的前端框架与页面规范
```

---

### 第十轮：安全精简（可选）

**Skill**: `/go-simplify`

**提示词**:
```
我需要审计并精简现有 Go 代码。

前提：
- 测试基线必须全绿（先跑 make test 或 go test ./...）
- 不破坏导出 API，不允许行为变化

请审计三类问题：
1. 过度设计（无人使用的注入点、预留空壳、零调用者抽象）
2. 过度优化（无测量支撑的复杂度、错误的容量提示）
3. 过度安全判断（对不可能状态的检查）

产出：
1. 已改清单（按三类分组，file:line + 理由）
2. 有意不动清单（合理防御 + 导出面债务，带理由）
3. 验证证据（build / test / race / lint 的实际结果）
```

---
