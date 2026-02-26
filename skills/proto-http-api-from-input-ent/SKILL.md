---
name: proto-http-api-from-input-ent
description: Design proto3 + HTTP API contracts for go-sphere scaffold projects from prompts, input folders, or requirement docs with mock data. Use when defining service APIs, selecting between entpb/shared/custom messages, and enforcing scaffold conventions, router-safety rules, and service-local error placement.
---

# Proto HTTP API From Input Ent

## Overview

Design implementation-ready `proto3 + HTTP` contracts for go-sphere scaffolds.

This skill targets go-sphere scaffold projects only.
Do not optimize for generic/non-scaffold project structures unless explicitly requested.
Directory conventions (`proto/`, `internal/`, `api/`) are assumed scaffold defaults.

## Required Reading Order

Read these local references before drafting any proto:

1. [references/repo-proto-conventions-reference.md](references/repo-proto-conventions-reference.md)
2. [references/router-conflict-reference.md](references/router-conflict-reference.md)
3. [references/go-sphere-api-definitions-reference.md](references/go-sphere-api-definitions-reference.md)
4. [references/go-sphere-error-handling-reference.md](references/go-sphere-error-handling-reference.md)
5. [references/protocol-and-codegen-reference.md](references/protocol-and-codegen-reference.md)
6. [references/proto-packages-and-runtime-reference.md](references/proto-packages-and-runtime-reference.md)
7. [references/go-sphere-api-definitions-checklist.md](references/go-sphere-api-definitions-checklist.md)
8. [references/proto-output-template.md](references/proto-output-template.md)

Do not replace local references with external links in final outputs.

## Scaffold Convention Policy

When generic best practices conflict with scaffold conventions, follow scaffold conventions unless the user explicitly asks for a different style.

Examples:

1. Keep `dash.v1` action-style routes instead of forcing pure REST resources.
2. Keep scaffold paging style (`page/page_size + total_page`) unless cursor paging is explicitly required.
3. Preserve compatibility-driven field naming exceptions.
4. Keep one stable route namespace prefix per service (for example `AdminService` -> `/api/admin...`).

## Reuse Policy

Apply this reuse order by default:

1. Reuse `entpb` messages if they satisfy external contract requirements.
2. Reuse or extract shared domain messages to `proto/shared/v1` when multiple servers/services need them.
3. Create custom DTO/VO messages only when required.

## Error Placement Policy

Use scaffold error placement rules:

1. Define service-specific business errors in the same `.proto` file as the service.
2. Put only cross-service/common errors in `proto/shared/v1` (or shared proto package).
3. Do not create a separate dedicated error package/file for each service unless explicitly requested.

Use custom DTO/VO only when at least one condition is true:

1. Sensitive/internal fields must be hidden.
2. Cross-aggregate composition is required.
3. A stable external contract must be isolated from storage model changes.

## Input Modes

### Prompt-only

1. Infer entities, use cases, read model, and write model.
2. State assumptions explicitly.

### Folder

1. Inspect only the folder content explicitly provided as task input.
2. Prefer scaffold-standard directories such as `proto/` and `internal/` when they exist.
3. Apply scaffold conventions as defaults when folder context is incomplete.

### Requirement + mock demo

1. Treat requirement docs as business truth.
2. Treat mock payloads as response-shape truth.
3. Use Ent schema as implementation reference, not as external API mirror.

## Workflow

1. Extract use cases (`Create`, `Get`, `List`, `Patch/Update`, `BatchGet`).
2. Draft mock JSON for list, detail, and error responses.
3. Make a documented reuse decision for each response object.
4. Select scaffold-compatible path/method style for the target package (`api.v1`, `dash.v1`, `shared.v1`, `bot.v1`).
5. Define HTTP bindings and request/response messages.
6. Define error enums with `sphere.errors` options.
7. Run a route conflict check against Gin/Fiber/Echo compatibility rules.
8. Validate package structure, imports, and codegen assumptions against this skill's references.
9. Add validation constraints and machine-readable error behavior.
10. Run the checklist before final output.

## Hard Rules

1. Model capability first, proto second.
2. Avoid table-mirror CRUD proto design for public contracts.
3. Require pagination for list APIs.
4. Prefer explicit batch APIs over repeated single reads.
5. Avoid `oneof` in HTTP-exposed request/response messages.
6. Keep error contracts machine-readable (`status`, business code, optional `reason`, `message`).
7. Avoid leaking internal storage details.
8. Prefer `entpb` reuse when it already satisfies contract needs.
9. Promote cross-server shared messages into `proto/shared/v1`.
10. Ensure contracts are compatible with protocol-first generation flow; do not rely on manual edits to generated files.
11. Ensure generated route paths do not create Gin/Fiber/Echo conflicts.
12. Use canonical wildcard naming per resource branch (for example keep `:task_id` consistent).
13. Use a stable service-level prefix namespace so routes from different services do not collide.
14. Keep business error enums in the same proto file as the owning service; use shared proto only for common errors.
15. If any hard rule fails, stop and output `Validation Notes -> Blocking Issues` with corrected route/error proposals.
16. Add business-facing comments to exposed `service/rpc`, core `message`, and key `enum` values so generated swagger/openapi output remains readable.
17. Prefer `//` single-line comment style in proto files for business annotations; avoid block comments unless a tool requires them.

## Output Contract

Produce output in this exact order:

1. `Scaffold Fit Decision`
2. `Route Conflict Check`
3. `Error Placement Check`
4. `Comment Coverage Check`
5. `API Capability Matrix`
6. `Mock JSON`
7. `Reuse Decision`
8. `Proto3 Contract`
9. `Error Enum Design`
10. `Ent -> Proto Mapping`
11. `Validation Notes`

Use [references/proto-output-template.md](references/proto-output-template.md) as the output shape.

## Quality Gates

Ensure all of the following:

1. Contract expresses business capability, not persistence leakage.
2. Query fields imply practical index strategy.
3. Batch/backfill patterns avoid N+1 calls.
4. Error behavior is consistent across RPC and HTTP responses.
5. Message reuse strategy is explicit and justified.
6. Package/import/path/method choices align with scaffold conventions.
7. Route set passes cross-backend conflict sanity checks.
8. Contract remains evolvable without breaking existing clients.
9. Swagger/OpenAPI-relevant comments exist for exposed RPCs/messages/enums and use `//` single-line style.
