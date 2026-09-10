---
name: proto-service-generator
description: "Generate or complete unary and server-streaming Go service implementations from protobuf-generated HTTP interfaces in go-sphere scaffold projects. Use when creating internal service files, adding missing method implementations, or generating compilable stubs for new proto endpoints. Trigger for: service implementation, proto handler, SSE producer, append-only update, interface assertion, CRUD via Ent, stub method generation. Do not use for cross-layer changes that also touch proto contracts, Ent schemas, bind/map, or generation commands — that is `sphere-feature-workflow`."
---

# Proto Service Generator

Generate or complete compilable service implementations under `internal/service/<module>/` from generated `*ServiceHTTPServer` interfaces in `api/<module>/v1/*.sphere.pb.go`.

<HARD-GATE>
Do not generate or modify any service file until:
1. The target module is known (e.g., `task`, `user`, `order`)
2. The generated `*ServiceHTTPServer` interface exists in `api/<module>/v1/*.sphere.pb.go`

If the module name is not specified, ask: "Which module should I generate service files for?"
If the proto generation has not been run yet, stop and ask the user to run `make gen/proto` first.
Do not guess the module from context alone if there are multiple candidates.
</HARD-GATE>

## When To Use

1. Proto and generated API files already exist.
2. You need missing service files or method implementations for `*ServiceHTTPServer`.
3. You need safe append-only completion for existing service files.

## Out of Scope

1. `BotServer` and non-HTTP interfaces.
2. Redesigning proto contracts or editing generated files.
3. Rewriting existing business logic unless explicitly requested.

## Required Reading

Read before generation:
1. [references/service-implementation-best-practices.md](references/service-implementation-best-practices.md)

Load sections selectively:
1. Always: `1) Interface Assertion and File Mapping`, `4) Append-Only Update Procedure`, `7) Import and Naming Checklist`.
2. Simple CRUD: `3) Simple CRUD (Direct Ent) Template`.
3. Unknown logic: `2) Stub Template for Unknown Logic`.
4. Complex orchestration and DI changes: `5) Complex Logic Split to Usecase`, `6) Wire Injection Pattern`.
5. Reuse checks: `8) Sphere Feature Reuse Pattern`.
6. Server-streaming methods: `9) Server-Streaming SSE Template`.

## Repository Conventions

1. Keep one `Service` struct per proto module.
2. Keep one Go file per proto service.
3. File naming: `XxxService -> xxx.go` (snake_case, remove `Service` suffix).
4. Every service file must include an interface assertion:
`var _ <pkg>.<ServiceName>HTTPServer = (*Service)(nil)`

## Workflow

### Step 1: Discover Interface
1. Find all `type XxxServiceHTTPServer interface` in `api/<module>/v1/*.sphere.pb.go`.
2. List all method signatures from each interface.

### Step 2: Check Existing Files
1. Check if `internal/service/<module>/xxx.go` exists.
2. If exists, list implemented methods.
3. If missing, mark for creation.

### Step 3: Decide Implementation Strategy

| Scenario | Strategy |
|----------|----------|
| Signature ends with `send func(*Reply) error) error` | Server-streaming producer; honor cancellation and send errors |
| Method is `Create*`, `Get*`, `List*`, `Update*`, `Delete*` on single entity | Simple CRUD via direct Ent |
| Logic cannot be inferred | Compilable stub with `errors.New("not implemented")` |
| Cross-entity transactions or complex orchestration | Split to usecase + wire DI |

### Step 4: Implement (Append-Only)
1. Create file if missing with assertion + all methods.
2. If existing, append only missing methods.
3. Add only required imports.
4. Keep existing implementations untouched.

### Step 5: Validate
1. Run `go build ./internal/service/...`
2. Report using Output Contract.

## Decision Rules

1. **Server stream first**: A `send func(*Reply) error` signature always uses the streaming template, even when the method name starts with `List` or another CRUD verb.
2. **Simple CRUD**: Method name matches `Create*`, `Get*`, `List*`, `Update*`, `Delete*` + single entity = direct Ent.
3. **Stub**: Logic unclear = `return nil, errors.New("not implemented: <Method>")`; streaming stubs return only the error.
4. **Usecase**: Cross-entity, reusable orchestration, or long flows = split to `internal/usecase/`.

## Hard Rules

1. Do not modify generated files under `api/*`.
2. Do not add a new DAO wrapper for simple CRUD.
3. Do not delete or rewrite existing assertions or method bodies in target service files.
4. Add only required imports.
5. Keep dependency injection compilable when constructor signatures change.
6. Never retain or use `httpx.Context` in a streaming producer. The generated interface supplies a standard `context.Context`, request, and send callback.

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
3. If constructor or provider signatures changed, run `make gen/wire` and rerun tests.

## Acceptance Checklist

1. New-file case: file exists, assertion exists, all interface methods exist, and code compiles.
2. Existing-file case: only missing methods are appended; existing implementations are unchanged.
3. Simple CRUD case: direct Ent via `s.db` with render helpers.
4. Complex-flow case: usecase split plus DI chain updates remain compilable.
5. Server-streaming case: signature matches the generated interface, every send error is handled, and the producer observes context cancellation.

## Related Skills

- Upstream — `proto-api-generator` owns the contract; this skill starts only after `make gen/proto` has produced `*ServiceHTTPServer` in `api/<module>/v1/*.sphere.pb.go`.
- Downstream — none; compilable per-service files are the deliverable. Use `go-test-engineering` when the generated service behavior needs test coverage.
- Boundary — use `sphere-feature-workflow` instead when the change also touches proto contracts, Ent schemas, bind/map registration, or generation commands.
- Companion — `sphere-feature-workflow` handles framework-native end-to-end integration (routing, middleware, auth, errors, wiring flow); this skill handles per-service file generation and completion. If it is unavailable, continue here and enforce the reuse-first checks in [references/service-implementation-best-practices.md](references/service-implementation-best-practices.md).
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
