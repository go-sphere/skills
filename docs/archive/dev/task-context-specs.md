# 任务上下文：PRD / UX / SPEC / 影响分析

本文是 [AI Agent 协作开发流程规范](../dev.md) 的一部分。完整阶段列表与最小流程见索引文档。

策略原则见 `context-strategy.md`。

---

### 1. 写 PRD

#### 任务目标
把想法、需求、demo 整理成业务文档。

#### 主要上下文
- 用户原始想法
- demo / 原型
- 截图 / Figma / 交互稿
- 竞品或参考流程
- 业务背景

#### 可选上下文
- 旧版 PRD
- 现有系统概述

#### 一般不需要
- API
- DDL
- service 代码

#### 为什么
这一步还在定义业务，不该被现有技术实现反向绑死。

---

### 2. 写 UX / 页面行为说明

#### 任务目标
把 demo 的视觉/交互转成行为语义。

#### 主要上下文
- PRD
- 原型 demo
- 页面截图 / Figma
- 用户流程说明

#### 可选上下文
- 现有 API（如果页面已经依赖后端）
- 现有前端代码

#### 一般不需要
- DDL
- 后端 service 实现

#### 为什么
这一步主要定义“页面在业务上怎么工作”，不是定义后端数据层。

---

### 3. 写 SPEC

#### 任务目标
把 PRD 和页面行为压成系统契约。

#### 主要上下文
- PRD
- UX / demo 行为说明
- 当前系统架构
- 现有代码仓库结构
- 现有 API / DDL（如果是增量改造）

#### 可选上下文
- 现有 proto / schema
- 相关历史设计文档

#### 一般不需要
- 太多实现细节代码
- 无关模块源码

#### 为什么
这一步的重点是把业务目标转成工程约束。

---

### 4. 修改 SPEC

#### 任务目标
对已有规格做增强、修正、扩展。

#### 主要上下文
- 当前 `SPEC.md`
- 变更原因
- 相关 PRD 片段
- 当前 API / Schema
- 当前 repo 结构

#### 可选上下文
- git diff
- 相关模块代码

#### 最重要的补充
- 这次变更是：
  - additive
  - behavioral
  - breaking
  - deepening

#### 为什么
改 SPEC 不是重写 PRD，而是改系统契约。

---

### 5. 根据 SPEC 跑 impact analysis

#### 任务目标
生成 impact map / api delta / schema delta / task plan。

#### 主要上下文
- `SPEC.md`
- `SPEC` 的 git diff
- repo 结构
- 当前 proto / API 文档
- 当前 schema / DDL / Ent schema
- 当前 surface 目录（mobile/dashboard/web/sdk 等）

#### 可选上下文
- PRD（只在需要理解业务背景时）
- 相关代码目录

#### 一般不需要
- 整个代码仓库的所有文件

#### 为什么
这一步的核心是“变更传播”，不是写实现。

---
