# Service Completion

Create or complete compilable service implementations under `internal/service/<module>/` from the
generated `*ServiceHTTPServer` interfaces in `api/<module>/v1/*.sphere.pb.go`. Follow this
procedure for Service-only work that fills in a generated interface, and for the service step of
Contract-first and Cross-layer work.

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

Read [service-implementation-best-practices.md](service-implementation-best-practices.md) before step 4.

1. Find every `type XxxServiceHTTPServer interface` in `api/<module>/v1/*.sphere.pb.go` and list all method signatures.
2. Check whether the service file exists under `internal/service/<module>/` (snake_case like `admin_session.go`, or flat lowercase like `keyvaluestore.go`). If it does, list the methods already implemented. If not, mark it for creation.
3. Pick a strategy per method using the table below.
4. Implement append-only: create the file with the assertion and all methods when missing; append only the missing methods when it exists; add only the imports you need; leave existing implementations untouched.
5. Run `go build ./internal/service/...`, then `go test ./internal/service/...` and `go test ./cmd/app/...`. If a constructor or provider signature changed, run `make gen/wire` and rerun the tests.
6. Report using the Reporting section below.

| When the method | Strategy |
|-----------------|----------|
| has a `send func(*Reply) error) error` signature | Server-streaming producer. Honor cancellation and every send error. This wins even when the name starts with `List`. |
| is `Create*`, `Get*`, `List*`, `Update*`, or `Delete*` on a single entity | Simple CRUD, direct Ent through `s.db` with render helpers |
| has logic you cannot infer | Compilable stub: `return nil, errors.New("not implemented: <Method>")`. A streaming stub returns only the error. |
| spans entities, is reusable orchestration, or is a long flow | Split into `internal/biz/<domain>` plus wire DI |

Load the other references from `SKILL.md` as the work needs them:
[implementation-templates.md](implementation-templates.md) for a CRUD method, an append-only update, or a usecase
split, and [wiring-and-streaming.md](wiring-and-streaming.md) for wire injection, import and naming checks, reuse
lookups, or a server-streaming method.

## Rules

1. One `Service` struct per proto module, one Go file per proto service.
2. File naming: `XxxService` becomes `xxx.go` (`Service` suffix removed) — snake_case (`admin_session.go`), or flat lowercase (`keyvaluestore.go`) when matching existing files.
3. Every service file carries the interface assertion: `var _ <pkg>.<ServiceName>HTTPServer = (*Service)(nil)`.
4. Never modify generated files under `api/*`.
5. Never add a new DAO wrapper for simple CRUD.
6. Never delete or rewrite an existing assertion or method body in a target service file.
7. Add only the imports the new code requires.
8. Keep dependency injection compilable when a constructor signature changes.
9. Never retain or use `httpx.Context` in a streaming producer. The generated interface supplies a standard `context.Context`, the request, and the send callback.

## Reporting

Use the Output contract in `SKILL.md`. Under `## Source-of-Truth Files`, list each service file
created or updated. Under `## Validation`, add these items in this order:

1. Interface Coverage Check — every method of the generated interface exists in the service.
2. Stub Methods Added — each stub, by method name.
3. Usecase Split Decision — which methods moved to `internal/biz/<domain>`, or why none did.
4. The build and test results from step 5.

Acceptance, by case:

- New file — the file exists, the assertion exists, every interface method exists, and the code compiles.
- Existing file — only missing methods were appended; existing implementations are unchanged.
- Simple CRUD — direct Ent via `s.db` with render helpers.
- Complex flow — the usecase split plus the DI chain updates still compile.
- Server-streaming — the signature matches the generated interface, every send error is handled, and the producer observes context cancellation.
