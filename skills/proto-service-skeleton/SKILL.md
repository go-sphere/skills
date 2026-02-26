---
name: proto-service-skeleton
description: Generate or complete `internal/service/<module>/*.go` service implementation skeletons from generated `api/<module>/v1/*.sphere.pb.go` HTTP interfaces in this repository. Use when proto and generated API files already exist and you need per-service files, interface assertion checks, safe append-only updates, simple CRUD direct Ent implementation, and fallback stub methods for unknown business logic.
---

# Proto Service Skeleton

Turn generated `*ServiceHTTPServer` interfaces into compilable service files under `internal/service/<module>/`.

## Required Reading

Read before generating:
1. [references/service-implementation-best-practices.md](references/service-implementation-best-practices.md)

## Companion Skill Policy

When `sphere-layout-feature-workflow` is available in the current session, use it together with this skill.

Collaboration rules:
1. Let `sphere-layout-feature-workflow` drive framework-native feature assembly (middleware, auth, errors, routing, wiring flow).
2. Let `proto-service-skeleton` focus on per-service file generation/completion from `*ServiceHTTPServer`.
3. Prefer shared framework capabilities over custom implementation.
4. Avoid implementing duplicate functionality when an equivalent capability already exists in this repository or the Sphere stack.

If `sphere-layout-feature-workflow` is unavailable, continue with this skill and enforce the Reuse-First Checklist below.

## Scope

1. Handle only `*ServiceHTTPServer` interfaces.
2. Cover all modules (such as `api`, `dash`, `shared`).
3. Do not handle `BotServer` or other non-HTTP interfaces.

## Repository Conventions

1. Keep one `Service` struct per proto module.
2. Keep one Go file per proto service.
3. File naming: remove the `Service` suffix and convert to `snake_case`.
4. Every service file must include an interface assertion:
`var _ <pkg>.<ServiceName>HTTPServer = (*Service)(nil)`

## Workflow

1. Discover modules and interfaces:
Use `type XxxServiceHTTPServer interface` from `api/<module>/v1/*.sphere.pb.go` as the single source of truth.
2. Run Reuse-First Checklist:
Before adding new code, check whether existing Sphere/repository capabilities already solve the need.
3. Map target files:
`XxxService -> internal/service/<module>/xxx.go`.
4. Check target file state:
If the file does not exist, create it. If it exists, only append missing methods/assertions/imports.
5. Generate method signatures:
Signatures must exactly match the interface; receiver is always `func (s *Service)`.
6. Fill method bodies using strategy:
Prefer the simple CRUD fast path; otherwise generate stubs.
Reuse templates from `references/service-implementation-best-practices.md` when needed.
7. Return change summary and validation result:
Follow this skill's Output Contract.

## Reuse-First Checklist

Before implementing new logic, verify these in order:
1. Existing service implementation in the same module (`internal/service/<module>/*.go`).
2. Existing generated converters and binders (`internal/pkg/render/entbind`, `internal/pkg/render/entmap`).
3. Existing shared helpers (`internal/pkg/*`, `internal/service/shared/*`).
4. Existing dependency wiring (`internal/service/wire.go`, `internal/wire.go`, `cmd/app/wire.go`).
5. Existing Sphere-native middleware/auth/error flow already used by sibling services.

If a capability already exists, reuse it. Do not re-implement equivalent behavior.

## Implementation Strategy

### A) Simple CRUD Fast Path (Direct Ent)

For methods classified as simple CRUD, call Ent directly inside Service without adding an extra DAO business layer.

Classification rules:
1. Method name is `Create*`, `Get*`, `List*`, `Update*`, or `Delete*`.
2. It operates on a single entity.
3. It does not require complex cross-domain orchestration or complex transactions.

Implementation style:
1. `Create*` / `Update*`: prefer `entbind.CreateXxx` / `entbind.UpdateOneXxx`.
2. `Get*` / `Delete*`: call `s.db.<Entity>.Get/DeleteOneID` directly.
3. `List*`: use `query.Clone().Count`, `conv.Page`, and `Limit/Offset/Order(sql.OrderDesc())`.
4. Response mapping: use `s.render.<Entity>(...)` or `conv.Map(..., s.render.<Entity>)`.

Prohibited:
1. Do not add a new `internal/pkg/dao` business wrapper for simple CRUD.

### B) Unknown or Complex Logic

When business logic cannot be safely inferred, generate a compilable stub first:

```go
return nil, errors.New("not implemented: <Method>")
```

When logic is clearly complex (cross-entity transactions, long flows, reusable orchestration), split it into:
`internal/usecase/<module>/<service>/`

Rules after split:
1. Service methods keep orchestration only.
2. Update `type Service struct` dependencies in `internal/service/<module>/service.go` when needed.
3. Update `NewService(...)` parameters and assignments when needed.
4. Update wire providers when needed so dependency injection remains compilable.

## Safe Update Policy

1. Append missing methods only; do not rewrite existing method bodies.
2. Append missing assertions only; do not delete existing assertions.
3. Add only required imports; avoid unrelated reordering.
4. Do not modify generated files under `api/*`.
5. Do not change existing business semantics.

## Output Contract

Output in this exact order:
1. `Scaffold Plan`
2. `Files To Create/Update`
3. `Interface Coverage Check`
4. `Stub Methods Added`
5. `Usecase Split Decision`
6. `Validation Result`

## Minimal Validation Checklist

1. `go test ./internal/service/...`
2. `go test ./cmd/app/...`
3. If dependency injection signatures change, run `make gen/wire` and rerun the tests above.

## Acceptance Checklist

1. New-file scenario: file exists, assertion exists, all interface methods exist, and code compiles.
2. Existing-file scenario: only missing methods are appended; existing implementations are unchanged.
3. Simple CRUD scenario: direct Ent via `s.db`, matching the `keyvaluestore` style.
4. Complex-logic scenario: split into `internal/usecase/...` as needed and complete the injection chain.
