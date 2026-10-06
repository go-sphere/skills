# Commands, Codegen, and Runtime

What to run, what generates what, and which HTTP primitives generated code expects.

## Standard Commands

Make targets are the public workflow contract. Prefer them over raw `go test ./...` so the
project's own generation and lint steps are not bypassed. Run `make help` when unsure — a layout
must not point a target at a missing script.

| Command | Purpose |
|---------|---------|
| `make gen/proto` | Ent + proto + bind/map generation (most common) |
| `make gen/db` | Ent + autoproto generation |
| `make gen/docs` | OpenAPI/Swagger refresh |
| `make gen/wire` | DI wiring refresh |
| `make gen/dts` | TypeScript type generation |
| `make gen/all` | Run all generation commands |
| `make test` | Run the project's Go tests |
| `make lint` | Non-mutating Go and Buf checks |
| `make check` | Dependency, formatting, lint, and test gate — the delivery gate |
| `make build` | Build the local binary |

## Proto Package Roles

| Package | Purpose |
|---------|---------|
| `sphere/binding` | Request binding annotations (URI, query, header, body) |
| `sphere/errors` | Error definitions and helpers |
| `sphere/options` | Common option patterns |

## Code Generation Chain

The chain is layout-dependent. Read the project's `buf.gen.yaml` and `buf.binding.yaml` instead
of assuming a fixed chain.

| Plugin | Where it runs |
|--------|---------------|
| `protoc-gen-go` | all layouts |
| `protoc-gen-sphere-binding` | all layouts (via `buf.binding.yaml`) |
| `protoc-gen-sphere` | all layouts |
| `protoc-gen-sphere-errors` | all layouts |
| `protoc-gen-route` | only layouts with a non-HTTP transport (currently the Telegram layout) |

Do not expect `protoc-gen-route` output in a layout whose `buf.gen.yaml` does not declare it.

## HTTP Framework (httpx)

`server/httpz` is built on `httpx`, a unified HTTP framework abstraction with multiple backends:

- **stdx** (`net/http`) — the default in the official templates
- **ginx** (Gin), **fiberx** (Fiber), **echox** (Echo), **hertzx** (Hertz)

Core interfaces: `Handler`, `Middleware`, `Router`, `Engine`, `Context`.

Generated handlers call `ctx.BindJSON`, `ctx.BindQuery`, `ctx.BindURI`, `ctx.BindHeader`, or
`ctx.BindForm`, and wrap results with `httpz.WithJson`. Never write or generate handlers that
take `*gin.Context`.

## Reuse-First Catalog

Before implementing new capability, check whether an existing Sphere package already covers it.
Do not duplicate behavior from this list. Document the reuse decision in the final report.

| Category | Available packages |
|----------|--------------------|
| Lifecycle/bootstrapping | `core/boot`, `core/task` |
| HTTP transport | `server/httpz`, `httpx` |
| Auth/authorization | `server/auth/*`, `server/middleware/auth` |
| Middleware | `server/middleware/*` (cors, ratelimiter, selector, online) |
| Caching | `cache/*` (Redis, Memory, BadgerDB) |
| Storage | `storage/*` (S3, Qiniu, Local) |
| Logging | `log/*` |
| Message queue | `mq/*` (Redis, in-memory) |
| Search | `search/*` (Meilisearch) |
| Scheduling | `scheduler/*` (cron and periodic jobs) |
| Infrastructure | `infra/*` (Redis client, SQLite) |
| Utilities | `utils/*`, `test/*` |
| Core helpers | `core/pool`, `core/safe` |
| Compatibility shims | `compat/*` |

Placement rule: a helper that is useful across unrelated projects and imports nothing from the
project module belongs in a versioned go-sphere library, not copied into the project. Conversely,
never push product-specific logic into layout-owned helpers.
