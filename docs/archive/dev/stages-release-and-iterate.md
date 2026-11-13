# 阶段 11-12：发布准备与迭代

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


### 11. 发布准备

#### 目标
把系统从“实现完成”推进到“可上线”。

#### 主要 agent
- `release-agent`
- `ops-agent`

#### 输出文档
- `ops/release-plan.md`
- `ops/runbook.md`
- `ops/migration-plan.md`（如需要）

#### 文档需要的细节

##### `release-plan.md`
- 发布范围
- 发布顺序
- 是否有 breaking change
- 是否要分阶段开关

##### `migration-plan.md`
- 数据迁移步骤
- 回滚策略
- 双写 / 兼容窗口（如需要）

##### `runbook.md`
- 常见故障
- 如何排查
- 如何补偿
- 哪些指标/日志要看

#### 完成标准
- 发布风险已被显式管理
- 出问题时知道怎么处理

---

### 12. 运行后反馈再迭代

#### 目标
上线后继续用 AI 驱动文档和实现同步演化。

#### 主要 agent
- `incident-agent`
- `spec-diff-pipeline`
- `review-agent`

#### 输入
- 线上反馈
- bug
- 指标
- 客户诉求
- 新需求

#### 输出
- capability gap note
- 新 spec diff
- 新 impact bundle

#### 核心做法
任何新增需求或线上问题，重新进入：

`Capability Gap -> SPEC 更新 -> spec-diff-pipeline -> API/schema/task -> implementation`

这样整个体系是闭环的。

---
