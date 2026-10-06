# 任务上下文：实现、前端、测试、Review、发布

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。

策略原则见 `context-strategy.md`。

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
