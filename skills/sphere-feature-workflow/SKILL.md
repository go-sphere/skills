---
name: sphere-feature-workflow
description: Implement end-to-end feature changes in go-sphere scaffold projects by following sphere-layout conventions and generation workflow. Use when adding or modifying APIs, protobuf contracts, Ent schemas, bind/map registration, service logic, or cross-layer refactors that must stay protocol-first and avoid manual edits to generated files.
---

# Sphere Feature Workflow

将需求变更落地为可合并代码，保持 `proto`、`schema`、`service`、`render` 一致演进，避免 generated drift。

## Required Reading Order

按顺序读取以下文档，再开始改动：

1. [references/workflow-matrix.md](references/workflow-matrix.md)
2. [references/source-of-truth-and-generated-boundaries.md](references/source-of-truth-and-generated-boundaries.md)
3. [references/change-checklist.md](references/change-checklist.md)

## Workflow Decision

先判断任务类型，再走对应流程：

1. `Contract-first`：新增/修改 HTTP API、RPC、errors、binding、validate 规则。
2. `Schema-first`：新增/修改 Ent schema、字段、索引、关系。
3. `Service-only`：不改 proto/schema，仅改业务实现、查询、渲染、权限或事务流程。

## Hard Rules

1. 只编辑 source-of-truth；不要手改 generated 文件。
2. 任何 `proto` 或 `schema` 变更后都执行 `make gen/proto`。
3. 若 API 文档或 TS SDK 受影响，执行 `make gen/docs` 或 `make gen/dts`。
4. 新实体必须评估并更新 `cmd/tools/bind/main.go` 的 `createFilesConf` 注册。
5. `WithIgnoreFields` 必须覆盖系统字段与敏感字段（如 `created_at/updated_at/password`）。
6. service-specific 业务错误优先放在所属 service 的 `.proto` 文件中。
7. 发现路由冲突、跨层不一致、生成产物未消费时，阻断提交并先修复。
8. 不要手改 `internal/pkg/render/entbind/**` 和 `internal/pkg/render/entmap/**`，如需调整映射，改 source-of-truth 并重新生成。

## Sphere Reuse-First Policy

新增功能前先检查 `github.com/go-sphere/sphere` 现有能力。以下场景禁止重复实现：

1. 应用启动与生命周期：`core/boot`
2. HTTP 服务与统一错误输出：`server/httpz`
3. 认证鉴权：`server/auth/jwtauth`、`server/auth/authorizer`、`server/auth/acl`
4. 通用中间件：`server/middleware/auth`、`server/middleware/cors`、`server/middleware/ratelimiter`、`server/middleware/selector`
5. 缓存抽象与实现：`cache`、`cache/memory`、`cache/mcache`
6. 存储抽象与文件服务：`storage`、`storage/fileserver`
7. 内置服务组件：`server/service/file`、`server/service/docs`
8. 日志能力：`log`、`log/zapx`
9. 基础设施适配：`infra/sqlite`
10. 常用安全与标识工具：`utils/idgenerator`、`utils/secure`
11. 消息队列与搜索（按需）：`mq`、`mq/memory`、`mq/redis`、`search`、`search/meilisearch`
12. 反向代理（按需）：`server/service/reverseproxy`

若需求与上述能力重合，必须优先组合这些包，而不是新建平行实现。

## Execution Workflows

### Contract-first Workflow

1. 修改 `proto/**` 的 service/method、HTTP annotations、binding、validate、error enum。
2. 执行 `make gen/proto`，确保 `api/**`、`internal/pkg/render/entbind`、`internal/pkg/render/entmap` 同步。
3. 根据编译错误补全 `internal/service/**` 的实现。
4. 若返回结构或查询策略变化，补 `internal/pkg/dao/**` 与 `internal/pkg/render` 下非生成代码（如 `render.go`、`errors.go`）。
5. 若 swagger/SDK 受影响，执行 `make gen/docs` 或 `make gen/dts`。
6. 运行测试并检查 generated diff 被业务代码消费。

### Schema-first Workflow

1. 修改 `internal/pkg/database/schema/**`，明确字段注释、Optional/Nillable、索引策略。
2. 判断 ID 策略：默认跟随生成器配置；仅业务强制时自定义 `id`。
3. 若引入新实体或字段映射变更，更新 `cmd/tools/bind/main.go`。
4. 执行 `make gen/proto`，然后修复 service/dao/render 的编译与行为变化。
5. 补齐分页、批量查询、敏感字段处理，避免只停留在 schema 变更。
6. 执行测试并验证查询路径与索引匹配。

### Service-only Workflow

1. 优先修改 `internal/service/**`、`internal/pkg/dao/**`、`internal/pkg/render` 下非生成代码。
2. 保持 proto contract 不变，避免破坏兼容性。
3. 涉及权限、事务、幂等等逻辑时，在 `internal/biz/**` 或共享包内集中封装。
4. 跑测试并确认无接口行为回归。

## Standard Commands

```bash
# 生成 ent + proto + bind/map
make gen/proto

# swagger/openapi
make gen/docs

# wire
make gen/wire

# 测试（按需缩小范围）
go test ./...
```

## Final Output Contract

在完成任务时，使用以下结构汇报：

1. `Scope`：本次变更范围与假设。
2. `Reuse Decision`：需求与 `github.com/go-sphere/sphere` 的复用映射（复用了哪些包，为什么）。
3. `Source-of-Truth Files`：实际改动的人工维护文件。
4. `Generation Commands`：执行过的生成命令与结果。
5. `Behavior/Compatibility Notes`：接口或数据兼容性影响。
6. `Validation`：测试命令、结果、剩余风险。

若任一 Hard Rule 未满足，先输出 `Blocking Issues`，不要宣称完成。
