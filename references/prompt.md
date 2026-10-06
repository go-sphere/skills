# AI Agent 协作开发提示词指南

本文档提供从"简单 PRD + 原型 demo"到可交付成果的完整提示词模板。

## 前提假设

- PRD 位置：`/Users/tbxark/Repos/go-sphere/skills/PRD.md`
- Demo 位置：`/Users/tbxark/Repos/go-sphere/skills/demo`
- 输出目录：`prd/`、`design/changes/<change-id>/`

## 目录

| 内容 | 位置 |
|------|------|
| 第 1-5 轮提示词模板（PRD、UX、SPEC、影响分析、API） | [prompt/rounds-01-05.md](prompt/rounds-01-05.md) |
| 第 6-10 轮提示词模板（Schema、实现、测试数据、前端、精简） | [prompt/rounds-06-10.md](prompt/rounds-06-10.md) |
| 流程标准与文档细度 | [dev.md](dev.md) |

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
    │
    ▼
安全精简（可选）► 精简修改 + 精简报告
```

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
| 6 | `/db-schema-designer` | prd/DDL.md | 可选 |
| 7 | `/sphere-feature-workflow` | 代码 | ✅ |
| 8 | `/ent-seed-sql-generator` | seed SQL | 可选 |
| 9 | `/frontend-crud-generator` | 前端页面与路由 | 可选 |
| 10 | `/go-simplify` | 精简修改 + 精简报告 | 可选 |

---

## 上下文优先级

根据 [dev/context-quick-reference.md](dev/context-quick-reference.md) 中的最佳实践：

- **写代码时**：`SPEC` 为主，`PRD` 为辅
- **写前端时**：`PRD` + `UX-FLOWS` + `SPEC` + `API`
- **做 review 时**：`SPEC` + 代码 diff
- **按任务摘取**相关章节，而不是整份全塞
