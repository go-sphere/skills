# Workflow Matrix (sphere-layout)

## Table of Contents

1. Change Type to Workflow
2. Minimal File Touchpoints
3. Command Matrix
4. Delivery Gate

## 1. Change Type to Workflow

| Change type | Start point | Primary source of truth | Required workflow |
| --- | --- | --- | --- |
| API contract change | `proto/**` | `.proto` files | Contract-first |
| DB model change | `internal/pkg/database/schema/**` | Ent schema files | Schema-first |
| Business behavior change only | `internal/service/**` / `internal/pkg/dao/**` | Service and DAO code | Service-only |
| Cross-layer feature | `proto/**` + `schema/**` + service | Proto + schema | Contract-first or Schema-first, then merge |

## 2. Minimal File Touchpoints

### Contract-first

1. `proto/**`: service/rpc/message/error changes.
2. `internal/service/**`: implement generated server interface.
3. `internal/pkg/dao/**`: query or mutation support.
4. `internal/pkg/render/**` non-generated files: output mapping adjustments (`render.go`, `errors.go`, wrappers).

### Schema-first

1. `internal/pkg/database/schema/**`: fields/indexes/comments.
2. `cmd/tools/bind/main.go`: `createFilesConf` registration and ignore-fields policy.
3. `internal/service/**` + `internal/pkg/dao/**` + `internal/pkg/render/**`: consume generated types.
4. `proto/**` (optional): when external contract must expose new fields.

### Service-only

1. `internal/service/**`: API behavior and orchestration.
2. `internal/pkg/dao/**`: query composition and batch strategy.
3. `internal/pkg/render/**` non-generated files: response shaping or masking.
4. `internal/biz/**` (optional): scheduled jobs or shared use-case logic.

## 3. Command Matrix

| Trigger | Command | Expected result |
| --- | --- | --- |
| Any proto/schema change | `make gen/proto` | ent/proto/bind/map artifacts are synchronized |
| OpenAPI impact | `make gen/docs` | swagger files are refreshed |
| DI wiring changed | `make gen/wire` | `wire_gen.go` is updated |
| Runtime verification | `go test ./...` | behavior-level safety check |

## 4. Delivery Gate

Only mark task complete when all statements are true:

1. Source-of-truth file edits are complete and consistent.
2. Required generation commands ran successfully.
3. Generated changes are consumed by service/dao/render code.
4. No manual edits exist in generated files.
5. Validation/test results are reported with known residual risks.
