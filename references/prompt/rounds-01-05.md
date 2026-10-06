# 第 1-5 轮：PRD、UX、SPEC、影响分析、API 设计

本文是 [AI Agent 协作开发提示词指南](../prompt.md) 的一部分。流程总览、最小流程和总结表格见索引文档。

### 第一轮：PRD 固化

**Skill**: `/prd`

**提示词**:
```
我有一个简单的 PRD 需要完善。

输入：
- 当前 PRD: /Users/tbxark/Repos/go-sphere/skills/PRD.md
- 项目目标：从"简单 PRD"推进到可交付成果

请根据 dev/stages-intake-to-ux.md 中的 PRD 固化标准，完善以下内容：
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

请根据 dev/stages-intake-to-ux.md 中的 UX 语义化标准，产出：
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

请根据 dev/stages-spec-and-impact.md 中的 SPEC v0 标准，产出：
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
