---
name: sphere-feature-workflow
description: Implement end-to-end feature changes in go-sphere scaffold projects by following the layout ownership contract and generation workflow. Use when adding or modifying APIs, protobuf contracts, Ent schemas, bind/map registration, service logic, or cross-layer refactors that must stay protocol-first and avoid manual edits to generated or layout-owned files. This skill is REQUIRED for any task involving go-sphere proto files, Ent schemas, service implementations, or generation commands (make gen/proto, make gen/docs, make gen/wire).
---

# Sphere Feature Workflow

## Overview

Implement merge-ready feature changes in `go-sphere` scaffold projects while keeping
`proto`, `schema`, `service`, and `render` layers synchronized.

This skill is **scaffold-specific** and **required** for any go-sphere feature work.
Prefer repository conventions over generic architecture patterns unless the user explicitly requests otherwise.

## Required Reading Order

**Step 0 — read the project's own contract first.** These files ship inside the
generated project and outrank this skill wherever they disagree:

| File | Why |
|------|-----|
| `.sphere/layout.json` | Machine-readable file ownership (`generated` / `layout_owned` / `mixed` / `project_owned`) |
| `AGENTS.md` | Layout profile, capabilities, and the extension seams for this specific layout |
| `docs/LAYOUT_CONTRACT.md` | Full authoring and synchronization protocol |

If the project has no `.sphere/layout.json`, it predates the ownership contract.
Treat every path as `project_owned` except the generated outputs in
[references/source-of-truth-and-generated-boundaries.md](references/source-of-truth-and-generated-boundaries.md), and say so in your report.

Then read these references **in order** before making edits:

1. **[references/layout-contract-and-ownership.md](references/layout-contract-and-ownership.md)** - Identify the layout variant and classify every file you intend to touch
2. **[references/workflow-matrix.md](references/workflow-matrix.md)** - Classify change type and select workflow
3. **[references/source-of-truth-and-generated-boundaries.md](references/source-of-truth-and-generated-boundaries.md)** - Understand what files to edit vs. regenerate
4. **[references/change-checklist.md](references/change-checklist.md)** - Verify complete coverage before delivery

## Scope

**You MUST use this skill** when the task involves any of the following:

| Trigger | Examples |
|---------|-----------|
| Proto file changes | Adding RPC methods, HTTP annotations, validation, error enums |
| Ent schema changes | Adding fields, relations, indexes, policy changes |
| Service implementation | Implementing generated interfaces, business logic |
| Generation commands | Running `make gen/proto`, `make gen/docs`, `make gen/wire` |
| Cross-layer work | Anything affecting both proto and schema layers |
| Bind/map registration | Changes to `cmd/tools/gen/entcrud/main.go` (`conf.NewFilesConf` / `conf.NewEntity`) |
| Layout-owned or mixed paths | Any edit to a path `.sphere/layout.json` classifies as `layout_owned` or `mixed` |

## Workflow Selection (Critical - Do Not Skip)

**Classify the task FIRST**, then run the matching workflow. See
[references/workflow-matrix.md](references/workflow-matrix.md) for detailed preflight checks.

| Workflow | Start Point | Use When |
|----------|-------------|----------|
| `Contract-first` | `proto/**` | Adding/changing service methods, HTTP annotations, errors, validation |
| `Schema-first` | `internal/pkg/database/schema/**` | Adding/changing entities, fields, indexes, relationships |
| `Service-only` | `internal/service/**` + `internal/pkg/dao/**` | Behavior changes WITHOUT contract/schema changes |
| `Cross-layer` | Contract-first or Schema-first | Both proto AND schema layers affected |

If classification is unclear, answer these questions first:
1. Does the request change external API behavior, route shape, validation, or error contract? → Contract-first
2. Does the request change persisted fields, entity relations, or index/query strategy? → Schema-first
3. Does the request only change orchestration/query/render logic? → Service-only
4. If multiple "yes", treat as Cross-layer

## Reuse-First Policy (Required)

Before implementing new capability, **check existing Sphere packages first**.
DO NOT duplicate behavior already covered by:

| Category | Available Packages |
|----------|-------------------|
| Lifecycle/bootstrapping | `core/boot`, `core/task` |
| HTTP transport | `server/httpz`, `httpx` |
| Auth/authorization | `server/auth/*`, `server/middleware/auth` |
| Middleware | `server/middleware/*` (cors, ratelimiter, selector, online) |
| Caching | `cache/*` (Redis, Memory, BadgerDB, etc.) |
| Storage | `storage/*` (S3, Qiniu, Local) |
| Logging | `log/*` |
| Message Queue | `mq/*` (Redis, In-memory) |
| Search | `search/*` (Meilisearch) |
| Scheduling | `scheduler/*` (cron/periodic jobs) |
| Infrastructure | `infra/*` (Redis client, SQLite) |
| Utilities | `utils/*`, `test/*` |
| Core helpers | `core/pool`, `core/safe` |
| Compatibility shims | `compat/*` |

**Always** document your reuse decision in the final output.

A helper that is useful across unrelated projects and imports nothing from the
project module belongs in a versioned go-sphere library, not copied into the
project. Conversely, do not push product-specific logic into layout-owned helpers.

## Execution Workflows

### Contract-first Workflow

```
1. Classify every target path against .sphere/layout.json
2. Edit proto/** (service/method, HTTP annotation, validation, errors)
3. Run: make gen/proto
4. Resolve impacts in:
   - internal/service/**    (implement generated interface)
   - internal/pkg/dao/**   (query/mutation support)
   - internal/pkg/render/** non-generated files
5. If docs changed: make gen/docs
6. Run: make test  (then make check before delivery)
7. Verify generated diffs are consumed
```

### Schema-first Workflow

```
1. Classify every target path against .sphere/layout.json
   (schema/** and cmd/tools/** are commonly `mixed` or `layout_owned`)
2. Edit internal/pkg/database/schema/** (field, relation, index)
3. Verify bind/map: cmd/tools/gen/entcrud/main.go (`conf.NewFilesConf`)
4. Review WithIgnoreFields for sensitive/system fields
5. Run: make gen/proto
6. Resolve impacts in service/dao/render
7. Run: make test  (then make check before delivery)
8. Verify query paths align with index intent
```

### Service-only Workflow

```
1. Edit ONLY non-generated code:
   - internal/service/**
   - internal/pkg/dao/**
   - internal/pkg/render/** (non-generated)
   - optional: internal/biz/**
2. Keep proto/schema STABLE
3. Run: make test  (then make check before delivery)
4. Verify no API regression
```

## Hard Rules (Non-Negotiable)

| # | Rule | Failure Mode |
|---|------|--------------|
| 1 | Edit source-of-truth only; NEVER patch generated files | Generated code overwritten on next `make gen` |
| 2 | Run `make gen/proto` after ANY proto/schema change | Stale generated code causes compile/behavior issues |
| 3 | Run `make gen/docs` when HTTP contract changes | API docs out of sync |
| 4 | Run `make gen/wire` when DI signatures change | Wire errors, runtime panics |
| 5 | Register new entities in `cmd/tools/gen/entcrud/main.go` | Bind/map missing, runtime errors |
| 6 | Use `WithIgnoreFields` for timestamps, soft-delete, secrets | Data leakage |
| 7 | Keep business errors in owning service proto | Error pollution across services |
| 8 | Block on route conflicts or unconsumed generated changes | Runtime routing/behavior bugs |
| 9 | NEVER edit `entbind/**` or `entmap/**` files | Changes lost on regeneration |
| 10 | Classify paths against `.sphere/layout.json` before editing | Product logic lands in layout-owned files and is lost or conflicts on the next layout sync |
| 11 | Put new product code in `project_owned` domain paths | Layout upgrades cannot cleanly merge it |
| 12 | Treat `mixed` paths as integration seams — preserve layout wiring AND project additions | One side silently dropped |

## Standard Commands

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

Make targets are the public workflow contract. Prefer them over raw `go test ./...`
so the project's own generation and lint steps are not bypassed. Run `make help`
when unsure — a layout must not point a target at a missing script.

## Proto Organization

| Package | Purpose |
|---------|---------|
| `sphere/binding` | Request binding annotations (URI, query, header, body) |
| `sphere/errors` | Error definitions and helpers |
| `sphere/options` | Common option patterns |

**Code Generation Chain** is layout-dependent. Read the project's `buf.gen.yaml`
and `buf.binding.yaml` instead of assuming a fixed chain.

| Plugin | Where it runs |
|--------|---------------|
| `protoc-gen-go` | all layouts |
| `protoc-gen-sphere-binding` | all layouts (via `buf.binding.yaml`) |
| `protoc-gen-sphere` | all layouts |
| `protoc-gen-sphere-errors` | all layouts |
| `protoc-gen-route` | **only** layouts with a non-HTTP transport (currently the Telegram layout) |

Do not add `protoc-gen-route` output expectations to a layout whose `buf.gen.yaml`
does not declare it.

## HTTP Framework (httpx)

The `server/httpz` package uses `httpx` as its foundation — a unified HTTP framework abstraction that supports multiple backends:
- **ginx** (Gin), **fiberx** (Fiber), **echox** (Echo), **hertzx** (Hertz)

Core interfaces: `Handler`, `Middleware`, `Router`, `Engine`, `Context`. Generated handlers call `ctx.BindJSON` / `BindQuery` / `BindURI` / `BindHeader` / `BindForm` and wrap results with `httpz.WithJson`. Do not generate `*gin.Context` handlers.

## Failure Conditions (Block Delivery If)

1. Workflow type not explicitly classified
2. Required generation commands skipped
3. Generated diffs exist but NOT consumed by service/dao/render
4. Generated files manually edited
5. Bind/map or ignore-field policy missed
6. Compatibility impact NOT reported
7. A `layout_owned` or `mixed` path was edited without stating why and what it costs at the next layout sync
8. `.sphere/layout.json` exists but path ownership was never checked

When a failure condition is hit, output `Blocking Issues` first, then a fix plan.

## Final Output Contract (Required Format)

Use this **exact section order** when reporting completion:

```
## Scope
[What was changed]

## Workflow Selection
[Contract-first / Schema-first / Service-only / Cross-layer]

## Layout and Ownership
[Layout variant (standard / simple / bun / telegram / unknown).
Each edited path with its .sphere/layout.json classification.
Justify every layout_owned or mixed edit and note the sync cost.]

## Reuse Decision
[What existing packages were used, or why new code was needed]

## Source-of-Truth Files
[List of files edited]

## Generation Commands
[Commands run: make gen/proto, make gen/docs, etc.]

## Behavior/Compatibility Notes
[API changes, breaking changes, migration needs]

## Validation
[Tests run, results]

## Blocking Issues
[Only if applicable - describe issue + fix plan]
```
