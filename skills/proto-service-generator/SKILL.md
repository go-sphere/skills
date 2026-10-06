---
name: proto-service-generator
description: "Generate or complete unary and server-streaming Go service implementations from the protobuf-generated HTTP interfaces in a go-sphere project. Use to create internal service files, append missing method implementations, or produce compilable stubs — service implementation, proto handler, SSE producer, interface assertion. Not for cross-layer changes — that is `sphere-feature-workflow`."
---

# Proto Service Generator

Generate or complete compilable service implementations under `internal/service/<module>/` from the
generated `*ServiceHTTPServer` interfaces in `api/<module>/v1/*.sphere.pb.go`.

Out of scope: `BotServer` and other non-HTTP interfaces, redesigning proto contracts, editing
generated files, and rewriting existing business logic unless explicitly asked.

## Inputs

Do not generate or modify any service file until both are true:

1. The target module is known, for example `task`, `user`, `order`.
2. The generated `*ServiceHTTPServer` interface exists in `api/<module>/v1/*.sphere.pb.go`.

If the module is unspecified, ask: "Which module should I generate service files for?" Never guess
the module from context when several candidates exist. If proto generation has not run yet, stop
and ask the user to run `make gen/proto` first.

## Steps

1. Find every `type XxxServiceHTTPServer interface` in `api/<module>/v1/*.sphere.pb.go` and list all method signatures.
2. Check whether `internal/service/<module>/xxx.go` exists. If it does, list the methods already implemented. If not, mark it for creation.
3. Pick a strategy per method using the table below.
4. Implement append-only: create the file with the assertion and all methods when missing; append only the missing methods when it exists; add only the imports you need; leave existing implementations untouched.
5. Run `go build ./internal/service/...`, then `go test ./internal/service/...` and `go test ./cmd/app/...`. If a constructor or provider signature changed, run `make gen/wire` and rerun the tests.
6. Report using the Output contract.

| When the method | Strategy |
|-----------------|----------|
| has a `send func(*Reply) error) error` signature | Server-streaming producer. Honor cancellation and every send error. This wins even when the name starts with `List`. |
| is `Create*`, `Get*`, `List*`, `Update*`, or `Delete*` on a single entity | Simple CRUD, direct Ent through `s.db` with render helpers |
| has logic you cannot infer | Compilable stub: `return nil, errors.New("not implemented: <Method>")`. A streaming stub returns only the error. |
| spans entities, is reusable orchestration, or is a long flow | Split into `internal/usecase/` plus wire DI |

## Reference Map

| Read | When |
|------|------|
| [references/service-implementation-best-practices.md](references/service-implementation-best-practices.md) | Always, before step 4 — interface assertion, file mapping, append-only procedure, stub template |
| [references/implementation-templates.md](references/implementation-templates.md) | Writing a CRUD method, an append-only update, or a usecase split |
| [references/wiring-and-streaming.md](references/wiring-and-streaming.md) | Wire injection, import and naming checks, reuse lookups, or a server-streaming method |

## Rules

1. One `Service` struct per proto module, one Go file per proto service.
2. File naming: `XxxService` becomes `xxx.go` — snake_case, `Service` suffix removed.
3. Every service file carries the interface assertion: `var _ <pkg>.<ServiceName>HTTPServer = (*Service)(nil)`.
4. Never modify generated files under `api/*`.
5. Never add a new DAO wrapper for simple CRUD.
6. Never delete or rewrite an existing assertion or method body in a target service file.
7. Add only the imports the new code requires.
8. Keep dependency injection compilable when a constructor signature changes.
9. Never retain or use `httpx.Context` in a streaming producer. The generated interface supplies a standard `context.Context`, the request, and the send callback.

## Output

Report in this exact order:

1. `Scaffold Plan`
2. `Files To Create/Update`
3. `Interface Coverage Check`
4. `Stub Methods Added`
5. `Usecase Split Decision`
6. `Validation Result`

Acceptance, by case:

- New file — the file exists, the assertion exists, every interface method exists, and the code compiles.
- Existing file — only missing methods were appended; existing implementations are unchanged.
- Simple CRUD — direct Ent via `s.db` with render helpers.
- Complex flow — the usecase split plus the DI chain updates still compile.
- Server-streaming — the signature matches the generated interface, every send error is handled, and the producer observes context cancellation.

## Related Skills

- Upstream — `proto-api-generator` owns the contract; this skill starts only after `make gen/proto` has produced `*ServiceHTTPServer` in `api/<module>/v1/*.sphere.pb.go`.
- Downstream — none; compilable per-service files are the deliverable. Use `go-test-engineering` when the generated service behavior needs test coverage.
- Boundary — use `sphere-feature-workflow` instead when the change also touches proto contracts, Ent schemas, bind/map registration, or generation commands.
- Companion — `sphere-feature-workflow` handles framework-native end-to-end integration (routing, middleware, auth, errors, wiring flow); this skill handles per-service file generation and completion. If it is unavailable, continue here and enforce the reuse-first checks in [references/wiring-and-streaming.md](references/wiring-and-streaming.md).
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
