---
name: sphere-feature-workflow
description: Implement end-to-end feature changes in go-sphere scaffold projects by following sphere-layout conventions and generation workflow. Use when adding or modifying APIs, protobuf contracts, Ent schemas, bind/map registration, service logic, or cross-layer refactors that must stay protocol-first and avoid manual edits to generated files.
---

# Sphere Feature Workflow

## Overview

Implement merge-ready feature changes in `go-sphere` scaffold projects while keeping
`proto`, `schema`, `service`, and `render` layers synchronized.

This skill is scaffold-specific. Prefer repository conventions over generic architecture
patterns unless the user explicitly requests otherwise.

## Required Reading Order

Read these references before making edits:

1. [references/workflow-matrix.md](references/workflow-matrix.md)
2. [references/source-of-truth-and-generated-boundaries.md](references/source-of-truth-and-generated-boundaries.md)
3. [references/change-checklist.md](references/change-checklist.md)

## Scope

Use this skill when the task involves one or more of the following:

1. HTTP/API contract changes in `proto/**`
2. Ent schema updates in `internal/pkg/database/schema/**`
3. Bind/map registration updates in `cmd/tools/bind/main.go`
4. Service/DAO/render behavior updates that must stay generation-safe
5. Cross-layer refactors that require protocol-first consistency

## Workflow Selection

Classify the task first, then run the matching workflow:

1. `Contract-first`
- Start from `proto/**`
- Use when adding or changing service methods, HTTP annotations, errors, or validation
2. `Schema-first`
- Start from `internal/pkg/database/schema/**`
- Use when adding/changing entities, fields, indexes, or relationships
3. `Service-only`
- Start from `internal/service/**` and `internal/pkg/dao/**`
- Use when behavior changes without contract/schema changes
4. `Cross-layer`
- Use `Contract-first` or `Schema-first` as entrypoint, then complete all impacted layers

If classification is unclear, follow the preflight checks in
[references/workflow-matrix.md](references/workflow-matrix.md).

## Reuse-First Policy

Before implementing new framework-level capability, check existing Sphere packages first.
Do not duplicate behavior already covered by:

1. Lifecycle and bootstrapping: `core/boot`
2. HTTP transport and error flow: `server/httpz`
3. Auth and authorization: `server/auth/*`, `server/middleware/auth`
4. Common middleware: `server/middleware/cors`, `ratelimiter`, `selector`
5. Infrastructure adapters and shared runtime packages: `cache/*`, `storage/*`, `log/*`, `utils/*`, `infra/*`

When overlap exists, reuse existing packages and document the decision.

## Execution Workflows

### Contract-first Workflow

1. Edit `proto/**` (service/method, HTTP annotation, validation, errors).
2. Run `make gen/proto`.
3. Resolve compile and behavior impacts in:
- `internal/service/**`
- `internal/pkg/dao/**`
- `internal/pkg/render/**` non-generated files
4. If contract-facing docs or SDK are impacted, run `make gen/docs` and/or `make gen/dts`.
5. Run tests and ensure generated diffs are consumed by manual code.

### Schema-first Workflow

1. Edit `internal/pkg/database/schema/**` (field policy, relation, index strategy).
2. Verify bind/map registration impact in `cmd/tools/bind/main.go#createFilesConf`.
3. Review `WithIgnoreFields` for system-managed and sensitive fields.
4. Run `make gen/proto`.
5. Resolve compile and behavior impacts across service/dao/render.
6. Run tests and verify query paths align with index intent.

### Service-only Workflow

1. Edit only non-generated business code:
- `internal/service/**`
- `internal/pkg/dao/**`
- `internal/pkg/render/**` non-generated files
- optional shared orchestration in `internal/biz/**`
2. Keep contract/schema stable unless explicitly requested.
3. Run targeted or full tests and confirm no API behavior regression.

## Hard Rules

1. Edit source-of-truth files only; never patch generated files directly.
2. Run `make gen/proto` after any proto/schema change.
3. Run `make gen/docs` when HTTP contract output changes.
4. Run `make gen/wire` when dependency wiring signatures change.
5. New entity exposure must be reviewed in `cmd/tools/bind/main.go#createFilesConf`.
6. `WithIgnoreFields` must cover system-managed and sensitive fields.
7. Keep service-specific business errors in the owning service proto unless explicitly shared.
8. Block delivery on route conflicts, cross-layer drift, or unconsumed generated changes.
9. Never manually edit `internal/pkg/render/entbind/**` or `internal/pkg/render/entmap/**`.

## Standard Commands

```bash
# ent + proto + bind/map generation chain
make gen/proto

# openapi/swagger generation
make gen/docs

# dependency injection generation
make gen/wire

# validation
go test ./...
```

## Failure Conditions

Do not mark the task complete if any of the following is true:

1. Workflow type is not explicitly classified.
2. Required generation commands were skipped.
3. Generated diffs exist but are not reflected in service/dao/render logic.
4. Generated files were manually edited.
5. Bind/map or ignore-field policy impact was missed for schema-affecting changes.
6. Compatibility impact and residual risks were not reported.

When a failure condition is hit, output `Blocking Issues` first, then a fix plan.

## Final Output Contract

Use this exact section order when reporting completion:

1. `Scope`
2. `Workflow Selection`
3. `Reuse Decision`
4. `Source-of-Truth Files`
5. `Generation Commands`
6. `Behavior/Compatibility Notes`
7. `Validation`
8. `Blocking Issues` (only when applicable)
