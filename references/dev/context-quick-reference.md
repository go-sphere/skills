# 上下文选择速查与最佳实践

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。


如果你不想记这么多分类，可以用这个简化规则：

---

### A. 偏业务问题
例如：
- 这个功能到底为什么存在？
- 用户在这个页面想完成什么？
- 这个流程的目标是什么？

给：
- `PRD`
- `UX-FLOWS`
- demo

---

### B. 偏系统规则问题
例如：
- 这个状态什么时候推进？
- 失败后应该怎么处理？
- 这个字段是不是 authoritative？
- 这个功能要不要阻断？

给：
- `SPEC`

---

### C. 偏系统边界问题
例如：
- 接口长什么样？
- 错误码如何设计？
- 哪些字段返回给前端？

给：
- `SPEC`
- `API/proto`

---

### D. 偏持久化问题
例如：
- 这个对象怎么落库？
- 这个状态要不要存？
- 哪个字段要加索引？

给：
- `SPEC`
- `Schema / DDL / Ent schema`

---

### E. 偏实现问题
例如：
- 这段 service 怎么写？
- 这个 handler 怎么改？
- 这条 query 怎么实现？

给：
- `SPEC`
- `API`
- `Schema`
- 当前代码

---

### F. 偏验证问题
例如：
- 这个实现是否符合要求？
- 需要测哪些场景？
- 这个变更是否有回归风险？

给：
- `SPEC`
- 代码 diff
- 相关 API / Schema

---

## 上下文使用最佳实践

最好的方式不是：

- 整份 PRD
- 整份 SPEC
- 整份 API
- 整份 DDL
- 全仓库代码

一起塞给 AI。

而是像这样：

```text
任务：实现验收提交接口

主要约束：
- SPEC 7.5 Inspection State Machine
- SPEC 8.1 Error Classes
- API.md 中 SubmitInspection contract
- DDL.md 中 task_equip_metrics
- 当前代码目录 internal/service/api/inspection.go

补充背景：
- PRD 中完工验收要求所有必填项完成后才能提交
```

这种效果远好于全塞。

---

## 上下文优先级建议

### 写代码时
1. 当前任务描述
2. 相关 SPEC 小节
3. 相关 API / Schema
4. 相关代码文件
5. PRD 片段

### 写前端时
1. 当前任务描述
2. PRD / UX-FLOWS
3. 相关 SPEC 小节
4. API contract
5. 当前前端代码

### 做 review 时
1. 代码 diff
2. 相关 SPEC 小节
3. API / Schema
4. PRD 片段（必要时）

---

### 什么时候必须把 PRD 和 SPEC 一起给

这些情况建议一起给：

1. 前端页面实现
- 因为既要理解业务目标，也要遵守系统规则

2. 从 0 到 1 新写功能
- AI 需要 PRD 理解“为什么”
- 需要 SPEC 理解“怎么做”

3. 功能存在多个合理实现路径
- PRD 帮助判断业务优先级
- SPEC 帮助判断工程约束

4. 做方案设计，不是直接写代码
- 这时 PRD 和 SPEC 都有价值

---

### 什么时候只给 SPEC 就够了

这些情况通常只给 SPEC 就够：

1. 改 service
2. 改状态机
3. 改 handler
4. 改错误码
5. 补测试
6. 做 code review
7. 跑 impact analysis

---

### 一句话结论

**实现代码时要给 AI 文档上下文，但默认以 `SPEC` 为主，`PRD` 为辅。**  
**最好的做法不是全量喂，而是按任务摘取相关章节。**

如需继续扩展，可进一步补充以下标准提示词模板：

**“给 AI 下开发任务时的标准提示词模板”**  
分别针对：
1. 写 API
2. 写 schema
3. 写 service
4. 写前端
5. 做 review
