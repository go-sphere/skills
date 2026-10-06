# 文档颗粒度标准与目录结构

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


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
