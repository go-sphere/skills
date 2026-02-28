# Workflow Matrix (sphere-layout)

## Table of Contents

1. Preflight Classification
2. Change Type to Workflow
3. Minimal File Touchpoints
4. Command Policy
5. Delivery Gate

## 1. Preflight Classification

Run these checks before editing files:

1. Does the request change external API behavior, route shape, validation, or error contract?
- Yes -> `Contract-first`
2. Does the request change persisted fields, entity relations, or index/query strategy?
- Yes -> `Schema-first`
3. Does the request only change orchestration/query/render logic without contract/schema changes?
- Yes -> `Service-only`
4. If two or more answers are `Yes`, treat as `Cross-layer`:
- pick `Contract-first` or `Schema-first` as the entry workflow
- complete all affected downstream layers before delivery

## 2. Change Type to Workflow

| Change type | Start point | Primary source of truth | Required workflow |
| --- | --- | --- | --- |
| API contract change | `proto/**` | `.proto` files | Contract-first |
| DB model change | `internal/pkg/database/schema/**` | Ent schema files | Schema-first |
| Business behavior change only | `internal/service/**` / `internal/pkg/dao/**` | Service and DAO code | Service-only |
| Cross-layer feature | `proto/**` + `schema/**` + service | Proto + schema | Contract-first or Schema-first, then merge |

## 3. Minimal File Touchpoints

### Contract-first

1. `proto/**`: service/rpc/message/error changes.
2. `internal/service/**`: implement generated server interface behavior.
3. `internal/pkg/dao/**`: query/mutation support for contract behavior.
4. `internal/pkg/render/**` non-generated files: response shaping and error mapping.

### Schema-first

1. `internal/pkg/database/schema/**`: fields/indexes/relations/comments.
2. `cmd/tools/bind/main.go`: `createFilesConf` registration and ignore-field policy.
3. `internal/service/**` + `internal/pkg/dao/**` + `internal/pkg/render/**`: consume generated type changes.
4. `proto/**` (optional): only when external contract must expose new schema fields.

### Service-only

1. `internal/service/**`: API behavior and orchestration.
2. `internal/pkg/dao/**`: query composition and batch strategy.
3. `internal/pkg/render/**` non-generated files: masking, shaping, and compatibility behavior.
4. `internal/biz/**` (optional): shared domain orchestration.

## 4. Command Policy

| Trigger | Command | Expected result |
| --- | --- | --- |
| Any proto/schema change | `make gen/proto` | Ent/proto/bind/map artifacts are synchronized |
| HTTP/OpenAPI impact | `make gen/docs` | Swagger/OpenAPI artifacts are refreshed |
| DI signature/provider change | `make gen/wire` | `wire_gen.go` is updated |
| Runtime verification | `go test ./...` (or scoped suites) | behavior-level safety check |

## 5. Delivery Gate

Only mark task complete when all statements are true:

1. The workflow type is explicitly stated (`Contract-first`, `Schema-first`, `Service-only`, or `Cross-layer`).
2. Source-of-truth edits are complete and internally consistent.
3. Required generation commands ran successfully.
4. Generated changes are consumed by service/dao/render behavior.
5. No manual edits exist in generated files.
6. Validation results and residual risks are reported.

If any gate fails, stop and report `Blocking Issues` plus a concrete fix plan.
