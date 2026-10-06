# AI Agent 协作开发流程规范

适用范围：从“简单 PRD + 原型 demo”推进到可上线交付成果的研发场景。

文档目标：提供一套适合 AI Agent 协作的开发流程，并按真实工程顺序说明每一步的目标、主要角色、
输入、输出文档、文档细节要求，以及这一阶段什么时候算完成。

最重要的原则是：**每一层文档只负责一层问题，不要混写。**

本文是索引。按需打开下面的分册，不要一次性全读。

## 总体流程

从 `简单 PRD + 原型 demo` 到最终成果，建议走这条主线：

| 阶段 | 分册 |
|------|------|
| 1 `Intake / 对齐输入`、2 `PRD 固化`、3 `UX / Demo 语义化` | [dev/stages-intake-to-ux.md](dev/stages-intake-to-ux.md) |
| 4 `SPEC v0`、5 `影响分析与 change pipeline` | [dev/stages-spec-and-impact.md](dev/stages-spec-and-impact.md) |
| 6 `API / Proto 设计`、7 `Domain / Schema 设计`、8 `Task Plan / 实施拆分` | [dev/stages-api-schema-tasks.md](dev/stages-api-schema-tasks.md) |
| 9 `实现`、10 `验证 / 测试 / Review` | [dev/stages-build-and-verify.md](dev/stages-build-and-verify.md) |
| 11 `发布准备`、12 `运行后反馈再迭代` | [dev/stages-release-and-iterate.md](dev/stages-release-and-iterate.md) |

## 其他分册

| 想解决的问题 | 读哪一篇 |
|--------------|----------|
| 每类文档要写到什么细度，目录怎么放 | [dev/document-granularity.md](dev/document-granularity.md) |
| 每个阶段由哪个逻辑角色负责，对应哪个 skill | [dev/roles.md](dev/roles.md) |
| 写代码时到底该给 AI `PRD` 还是 `SPEC` | [dev/context-strategy.md](dev/context-strategy.md) |
| 写 PRD / UX / SPEC / 影响分析时要带哪些上下文 | [dev/task-context-specs.md](dev/task-context-specs.md) |
| 设计 API / Proto 或 Schema 时要带哪些上下文 | [dev/task-context-contracts.md](dev/task-context-contracts.md) |
| 写后端、前端、测试、review、发布文档时要带哪些上下文 | [dev/task-context-implementation.md](dev/task-context-implementation.md) |
| 只想要一张速查表和几条最佳实践 | [dev/context-quick-reference.md](dev/context-quick-reference.md) |

每轮可直接复制的提示词模板见 [prompt.md](prompt.md)。

## 最小可执行版本

如果不想一开始就上全流程，先用这套简化版：

1. `PRD.md`
2. `UX-FLOWS.md`
3. `SPEC.md`
4. `spec-diff-pipeline` 产出 `01-spec-delta.md`、`02-impact-map.md`、`03-api-delta.md`、`04-schema-delta.md`、`05-task-plan.md`
5. AI 实现
6. `validation-report.md`

这已经足够支撑大多数中小型 AI 协作开发。

## 可选补充产物

如果需要，下一步可以继续补齐两样很实用的内容：

1. 一套可直接复制使用的文档模板：`PRD.md`、`UX-FLOWS.md`、`SPEC.md`、`API.md`、`DDL.md`。
2. 一套 AI Agent 编排蓝图：哪一步由哪个 agent 做，哪一步可以并行，哪一步必须人工 gate。
