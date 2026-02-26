---
name: ent-schema-generator
description: Summarize database schema design from requirement inputs and produce implementation-ready outputs for Go + Ent in this repository. Use when the input may be a prompt, Markdown requirement document, repository folder, or runnable demo behavior and you need entity extraction, field/constraint design, weak-relation ID strategy, index planning, Ent schema guidance, and concrete bind/render/service integration impacts.
---

# Ent Schema Generator

将需求输入整理成可直接落地到 `sphere-layout` 的 DB schema 方案，强调可执行性与可审查性。

## AI-First Workflow

1. Gather inputs from all available sources.
- 读取提示词、需求文档（`.md`）、接口定义（`.proto`）、现有 schema、service/dao/render 代码。
- 如有 demo 行为，先抽取对象、状态流转、关键动作。

2. Extract entities and lifecycle.
- 从业务名词与 API 资源抽候选实体。
- 每个实体明确：status/state、关键时间点、关键约束。
- 仅在明确必要时拆表（可选字段组、低频大字段、写热点冲突）。

3. Design fields and null strategy.
- schema 与关键字段必须有业务注释。
- 每个字段必须明确 Optional/Nillable/Unique/Immutable/Default。
- 状态字段使用 Ent 原生 `field.Enum`，并设置默认值。
- 统一 `created_at/updated_at`；仅在需要软删时添加 `deleted_at`。
- 缺失语义优先 `NULL`，避免空字符串哨兵。

4. Apply ID policy.
- 默认不在 schema 手写 `id`。
- 优先使用 ent generator 集中 ID 配置。
- 仅在业务明确需要时手写自定义 `id`，并说明对 bind/proto 的影响。

5. Choose relation strategy.
- 关系字段优先弱关联 ID（如 `user_id` / `order_id`）。
- many-to-many 优先级固定：relation-entity > array(确认方言支持) > join table > JSON(最后兜底)。
- JSON 不是常规方案，必须写明 typed/array/join table 不可行原因。

6. Plan indexes from real query paths.
- 基于真实 list/filter/sort/query 使用路径设计索引。
- 优先主键/唯一、高选择性过滤、分页排序复合索引。
- 避免仅建低基数 status 单列索引（除非有明确收益）。

7. Produce Ent + Go implementation guidance.
- Ent 侧优先 ID 字段表达关系，不强制 edge。
- Go 侧给出批量查询方案：收集 IDs -> 去重 -> `IDIn(...)` -> map 回填。
- IDs 很大时给出 chunk 策略与跨服务 `BatchGet*` 建议。

8. Add evolution and consistency safeguards.
- 读优化可加快照冗余字段（如 name/price snapshot）。
- 优先 typed/array 结构；JSON 只作例外。
- 弱关联场景必须给出 dangling refs 校验点。

## Repository Contract (sphere-layout)

必须显式对齐以下生成链路与接入点：
- Ent 生成入口：`cmd/tools/ent/main.go`
- Bind/Mapper 生成入口：`cmd/tools/bind/main.go`
- 统一后置命令：`make gen/proto`

输出中必须判断并说明：
- `ent tool config impact`：`IDType` / ent features / autoproto 影响。
- `bind registration impact`：是否需要更新 `createFilesConf`。
- `render/dao/service touchpoints`：哪些层要补代码。

## 新增实体必改清单

如果方案引入新实体，必须逐项检查并在输出中写明：
- 新 schema 文件与字段/索引。
- `cmd/tools/bind/main.go` 中 `createFilesConf` 注册。
- render 层（`entmap`/`entbind` 消费点）接入。
- DAO 层批量查询 helper 与去重策略。
- service 层分页/查询/映射接入。
- 生成命令执行与变更 diff 消费（entpb/proto/bind/map）。

## 失败处理约束

以下情况不允许视为完成：
- 只改 schema，未评估或未说明 bind 注册影响。
- 涉及绑定字段但未补 `WithIgnoreFields` 影响说明（例如 `created_at/updated_at` 或敏感字段）。
- 输出缺少 post-change commands 或 generation diff checklist。

## Output Format

使用 `references/output-template.md`。

最终输出必须包含：
- 11 段结构化内容。
- sphere-layout 生成链路影响说明。
- post-change commands（至少 `make gen/proto` 与测试命令）。
- generation diff checklist。

## Resources

- `references/best-practices.md`
- `references/output-template.md`
- `references/go-ent-service-patterns.md`
- `references/ent-schema-examples.md`

## Notes

- 本 skill 是 AI 推理驱动，不依赖本地脚本自动生成草稿。
- 语言默认中文说明 + 英文技术关键词（命令/类型/API 名不翻译）。
