# 阶段 9-10：实现与验证

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


### 9. 实现

#### 目标
按任务分层落代码。

#### 主要 agent
- `sphere-feature-workflow`
- service / frontend / review agents

#### 输入
- `05-task-plan.md`
- API 文档
- schema 文档
- repo conventions

#### 输出
- 代码改动
- 生成文件
- tests

#### 实现阶段文档
实现阶段不一定新增大文档，但至少应保留：
- `design/changes/<change-id>/implementation-notes.md`（可选）
- 或在 PR / commit message 中说明：
  - 改了什么
  - 为什么改
  - 对应哪个 spec/task

#### 需要的细节
AI agent 在这一步最容易偏，所以要强约束：
- source-of-truth file
- generated boundary
- workflow type
- validation command

#### 完成标准
- 代码与文档一致
- 没有出现“文档说一套，代码做另一套”

---

### 10. 验证 / 测试 / Review

#### 目标
验证实现符合 SPEC，不只是能跑。

#### 主要 agent
- `test-agent`
- `review-agent`
- `qa-agent`

#### 输入
- SPEC
- task plan
- 实现代码

#### 输出文档
- `design/changes/<change-id>/validation-report.md`

#### `validation-report.md` 应包含
- 测试范围
- 已执行测试
- 关键状态机用例
- 幂等验证结果
- 失败恢复验证结果
- 残留风险
- 未覆盖项

#### 重点验证什么
1. happy path
2. illegal transition
3. permission denied
4. threshold blocked
5. duplicate submission
6. archive failure + retry
7. restart / resume / draft recovery
8. surface-level compatibility

#### 完成标准
- 实现行为能映射回 SPEC 中的规则
- 不只是“接口通了”

#### 可选：安全精简 pass

验证通过后，若代码存在 AI 生成代码常见的过度设计、过度优化、过度防御，可跑一次 `go-simplify`：

- 前置条件：测试基线全绿，测试是本步骤唯一的安全网
- 硬约束：不破坏导出 API、零行为变化（含非法输入的处理方式）
- 产出：已改清单、有意不动清单、验证证据
- 注意：扫描给出的“死代码”结论只是假设，必须先读源码验证才能动手

---
