---
name: sphere-feature-workflow
description: Implement end-to-end feature changes in go-sphere scaffold projects under the layout ownership contract. Use for any task touching go-sphere proto files, Ent schemas, bind/map registration, service logic, cross-layer refactors, or the `make gen/*` commands, so edits stay protocol-first and never land in generated files. Not for layout upgrades or drift — that is `sphere-layout-sync`.
---

# Sphere Feature Workflow

Deliver merge-ready feature changes in `go-sphere` scaffold projects with the `proto`, `schema`,
`service`, and `render` layers in sync. Prefer repository conventions over generic architecture
patterns unless the user explicitly asks otherwise.

## Inputs

Read the project's own contract before anything else. These files ship inside the generated
project and outrank this skill wherever they disagree.

| File | Why |
|------|-----|
| `.sphere/layout.json` | Machine-readable file ownership: `generated`, `layout_owned`, `mixed`, `project_owned` |
| `AGENTS.md` | Layout profile, capabilities, and the extension seams for this layout |
| `docs/LAYOUT_CONTRACT.md` | Full authoring and synchronization protocol |

If the project has no `.sphere/layout.json`, it predates the ownership contract. Treat every path
as `project_owned` except the generated outputs listed in
`references/source-of-truth-and-generated-boundaries.md`, and say so in your report.

## Steps

1. Classify the change type, then state it out loud before editing. Use the question list below.
2. Classify every path you intend to touch against `.sphere/layout.json`.
3. Check the reuse catalog before writing new capability. Record the reuse decision.
4. Run the execution sequence for the classified workflow from `references/workflow-matrix.md`.
5. Run the required generation commands for what you changed. Never hand-edit their output.
6. Consume every generated diff in `internal/service/**`, `internal/pkg/dao/**`, and non-generated `internal/pkg/render/**`.
7. Run `make test`, then `make check` as the delivery gate.
8. Report using the Output contract below.

Classification questions, in order. The first "yes" picks the workflow; two or more "yes" means
Cross-layer.

| Question | Workflow | Starts at |
|----------|----------|-----------|
| Does it change external API behavior, route shape, validation, or the error contract? | Contract-first | `proto/**` |
| Does it change persisted fields, entity relations, or index/query strategy? | Schema-first | `internal/pkg/database/schema/**` |
| Does it only change orchestration, query, or render logic? | Service-only | `internal/service/**`, `internal/pkg/dao/**` |
| Two or more of the above? | Cross-layer | Contract-first, unless the primary change is clearly schema |

## Reference Map

| Read | When |
|------|------|
| [references/layout-contract-and-ownership.md](references/layout-contract-and-ownership.md) | Always, at step 2 — identify the layout variant and classify every path |
| [references/workflow-matrix.md](references/workflow-matrix.md) | Always, at step 4 — preflight checks, execution sequence, delivery gate |
| [references/source-of-truth-and-generated-boundaries.md](references/source-of-truth-and-generated-boundaries.md) | Before the first edit, to separate what you edit from what you regenerate |
| [references/commands-and-codegen.md](references/commands-and-codegen.md) | Before running a generation command, picking a reuse package, or touching an HTTP handler |
| [references/change-checklist.md](references/change-checklist.md) | At step 8, to verify coverage before delivery |

## Rules

1. Edit source-of-truth files only. Never patch generated files — the next `make gen` overwrites them.
2. Run `make gen/proto` after any proto or schema change, or generated code goes stale.
3. Run `make gen/docs` when the HTTP contract changes, or the API docs drift.
4. Run `make gen/wire` when DI signatures change, or wire fails and the runtime panics.
5. Register every new entity in `cmd/tools/gen/entcrud/main.go`, or bind/map is missing at runtime.
6. Use `WithIgnoreFields` for timestamps, soft-delete, and secrets, or data leaks into responses.
7. Keep business errors in the owning service's proto, or errors pollute other services.
8. Never edit `entbind/**` or `entmap/**`; regeneration discards the changes.
9. Classify paths against `.sphere/layout.json` before editing, or product logic lands in layout-owned files and is lost at the next sync.
10. Put new product code in `project_owned` domain paths, or layout upgrades cannot merge it cleanly.
11. Treat `mixed` paths as integration seams. Preserve both the layout wiring and the project additions, or one side is silently dropped.
12. Block delivery on route conflicts or unconsumed generated changes.

## Blocking Conditions

Output `Blocking Issues` first, then a fix plan, when any of these is true:

1. The workflow type was never explicitly classified.
2. A required generation command was skipped.
3. Generated diffs exist but service, dao, or render does not consume them.
4. A generated file was edited by hand.
5. Bind/map registration or the ignore-field policy was missed.
6. Compatibility impact was not reported.
7. A `layout_owned` or `mixed` path was edited without stating why and what it costs at the next layout sync.
8. `.sphere/layout.json` exists but path ownership was never checked.

## Output

Report completion in this exact section order:

1. `## Scope` — what changed.
2. `## Workflow Selection` — Contract-first, Schema-first, Service-only, or Cross-layer.
3. `## Layout and Ownership` — the layout variant (`standard`, `simple`, `bun`, `telegram`, or unknown), every edited path with its `.sphere/layout.json` classification, and a justification plus sync cost for each `layout_owned` or `mixed` edit.
4. `## Reuse Decision` — which existing packages were used, or why new code was needed.
5. `## Source-of-Truth Files` — the files edited.
6. `## Generation Commands` — the commands run.
7. `## Behavior/Compatibility Notes` — API changes, breaking changes, migration needs.
8. `## Validation` — tests run and their results.
9. `## Blocking Issues` — only when applicable: the issue plus a fix plan.

## Related Skills

- Upstream — `spec-writer` supplies intended behavior; `proto-api-generator` and `ent-schema-implementer` supply the contracts and schemas that must exist before generation. When the project has no `.sphere/layout.json`, run `sphere-layout-sync` first instead of guessing ownership.
- Downstream — `go-test-engineering` when `make test` coverage does not prove the behavior; `go-simplify` for an optional behavior-neutral leanness pass once validation is green; and `go-sphere-makefiles` when the `make check` delivery gate is missing or broken. Hand off after the final output contract is reported with validation results.
- Boundary — use `sphere-layout-sync` for layout drift and upgrades, `proto-service-generator` for filling in one service file from an existing generated interface, and `frontend-crud-generator` for frontend pages and routes.
- Companion — `proto-service-generator` covers per-service file completion while this skill owns cross-layer integration; if it is unavailable, complete the service files here and say so in the validation section.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
