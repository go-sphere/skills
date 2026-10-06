# AI Agent 角色分工

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


> **重要说明**：本节的 `*-agent` 名称代表”逻辑角色/职责分工”，不代表 Codex、Claude 或其他平台内置的固定 agent。
> - **真实可直接落地的 skill**：请参考 [README.md](../../README.md) 中列出的 skills
> - **通用 AI 能力**：部分角色可由 Codex、Claude Code 的内置功能实现，无需创建 skill

### 角色与 Skill 对照表

| 角色 | 职责 | 实现方式 |
|------|------|----------|
| `intake-agent` | 整理输入 | 已有 `project-intake` skill |
| `prd-agent` | 产出 PRD | 已有 `prd` skill |
| `ux-agent` | UX/Demo 语义化 | 已有 `ux-analyst` skill |
| `spec-agent` | 写 SPEC | 已有 `spec-writer` skill |
| `spec-diff-pipeline` | 影响分析 | 已有 `spec-diff-pipeline` skill |
| `api-agent` | 设计 API/proto | 已有 `proto-api-generator` skill |
| `schema-agent` | 设计 schema | 已有 `db-schema-designer` skill |
| `seed-agent` | 生成测试数据 | 已有 `ent-seed-sql-generator` skill |
| `service-agent` | 生成 service 骨架 | 已有 `proto-service-generator` skill |
| `frontend-agent` | 生成前端页面与路由 | 已有 `frontend-crud-generator` skill |
| `planning-agent` | 拆任务 | Codex/Claude Code plan 功能 |
| `implementation-agent` | 落代码 | 已有 `sphere-feature-workflow` skill |
| `simplify-agent` | 安全精简代码 | 已有 `go-simplify` skill |
| `review-agent` | 代码 review | Codex/Claude Code review 功能 |
| `qa-agent` | 验证报告 | 提示词实现 |
| `release-agent` | 发布准备 | 提示词实现 |

### 各角色详细说明

1. `intake-agent`
   - 整理输入
   - 注：负责收集原始材料、边界和缺失项
   - **实现方式**：使用现有 `project-intake` skill

2. `prd-agent`
   - 产出 PRD
   - 偏产品与需求整理角色
   - **实现方式**：使用现有 `prd` skill

3. `ux-agent`
   - 把 demo 行为语义化
   - 偏 UX/交互分析角色，负责把界面翻译成可执行行为
   - **实现方式**：使用现有 `ux-analyst` skill

4. `spec-agent`
   - 写 SPEC
   - 偏系统设计角色，负责把业务目标压成工程契约
   - **实现方式**：使用现有 `spec-writer` skill

5. `spec-diff-pipeline`
   - 每次变更后做影响分析和任务拆分
   - **实现方式**：使用现有 `spec-diff-pipeline` skill

6. `api-agent`
   - 设计 API/proto
   - **实现方式**：使用现有 `proto-api-generator` skill

7. `schema-agent`
   - 设计 schema/DDL/Ent
   - **实现方式**：使用现有 `db-schema-designer` skill

8. `seed-agent`
   - 生成测试数据
   - 负责从 Ent schema 生成可执行的 SQL seed 数据
   - **实现方式**：使用现有 `ent-seed-sql-generator` skill

9. `service-agent`
   - 生成 service 骨架
   - 负责从 proto 接口生成 service 实现模板
   - **实现方式**：使用现有 `proto-service-generator` skill

10. `frontend-agent`
    - 生成前端页面与路由
    - 负责从生成的 TS swagger client 生成页面和路由注册
    - **实现方式**：使用现有 `frontend-crud-generator` skill

11. `planning-agent`
    - 拆任务
    - 负责把设计拆成可并行执行的工作包
    - **实现方式**：使用 Codex 或 Claude Code 的 plan 功能（无需创建 skill）

12. `implementation-agent`
    - 落代码
    - **实现方式**：使用现有 `sphere-feature-workflow` skill

13. `simplify-agent`
    - 安全精简代码
    - 负责在测试基线全绿的前提下审计过度设计、过度优化、过度防御，并输出已改清单与有意不动清单
    - **实现方式**：使用现有 `go-simplify` skill

14. `review-agent`
    - 做变更 review
    - 负责从规格、回归和风险角度审查实现
    - **实现方式**：使用 Codex 或 Claude Code 的 review 功能（无需创建 skill）

15. `qa-agent`
    - 做验证报告
    - 负责测试覆盖、验收映射和残留风险整理
    - **实现方式**：提示词实现，不创建独立 skill

16. `release-agent`
    - 准备发布和 runbook
    - 负责发布计划、迁移步骤和运行手册整理
    - **实现方式**：提示词实现，不创建独立 skill

---
