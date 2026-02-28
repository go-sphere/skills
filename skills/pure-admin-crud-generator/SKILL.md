---
name: pure-admin-crud-generator
description: Generate CRUD pages and router module files for pure-admin-thin by parsing src/api/swagger/Api.ts and src/api/api.ts in this repository. Use when asked to scaffold backend admin list/edit/detail pages, CRUD actions, and route modules from swagger-ts-api methods without external generators.
---

# Pure Admin Thin CRUD Generator

## Overview
Generate runnable Vue pages under `src/views/<module>/` and route modules under `src/router/modules/` from local swagger-ts-api output in `src/api/swagger/Api.ts` and API wrapper behavior in `src/api/api.ts`.

This is an AI-first generator skill. Do not use external OpenAPI generators and do not add helper codegen scripts.

## When to Use
Use this skill when the user asks to scaffold or update pure-admin-thin admin pages from existing swagger methods, including:

- CRUD pages (`index.vue`, `edit.vue`, optional `detail.vue`)
- dashboard-first admin pages
- route module files under `src/router/modules`
- action buttons backed by non-CRUD APIs (retry/enable/disable/export etc.)

## Hard Constraints
1. Parse and generate from local `Api.ts` + `api.ts` only.
2. Do not regenerate API clients with external tools.
3. Do not create reusable business UI component libraries.
4. Use Element Plus components for page UI.
5. Do not add runtime dependencies only for generated pages.
6. Keep repository conventions first; only fallback to generic heuristics if local patterns are missing.

## Required Reading Order
Read references with progressive disclosure to keep context lean.

Always read:
1. `references/output-contract.md`
2. `references/api-parsing-rules.md`
3. `references/page-generation-spec.md`

Read only when `pageMode=dashboard` or dashboard UI is explicitly requested:
1. `references/dashboard-best-practices.md`

## Input Contract
Required and optional generation inputs:

- `moduleSelector` (required): module tag/entity/path keyword.
- `selectorMode` (optional, default `auto`): `auto | tag | entity | path`.
- `forceDetailPage` (optional, default `auto`): `auto | true | false`.
- `pageMode` (optional, default `crud`): `crud | dashboard | mixed`.
- `routeBase` (optional, default `/<kebab-module>`).
- `outputMode` (fixed): full file contents only.

If the user provides only a vague module name, resolve with `selectorMode=auto` and explicitly state matched methods.

## Repository Facts
Use these local assumptions first:

- API calls go through `API` from `src/api/api.ts`.
- `API` already unwraps axios response once.
- Swagger methods are under `new Api().api` in `src/api/swagger/Api.ts`.
- Method doc blocks include `@tags`, `@name`, `@summary`, `@request`.
- Routes are auto-collected via `import.meta.glob("./modules/**/*.ts")`; route index edits are usually unnecessary.

## Workflow
Follow this sequence every run.

1. Resolve module and classify endpoints.
Use `references/api-parsing-rules.md` for module resolution, CRUD/action classification, and tie-break rules.

2. Infer request/response structures.
Identify query/form/detail fields, pagination keys, items key, and total key from local TypeScript types.

3. Decide file set.
- `crud | mixed`: `index.vue`, `edit.vue`, route module, and optional `detail.vue`.
- `dashboard`: `dashboard.vue` (or `index.vue` if appropriate), optional `edit.vue`, route module.

4. Generate pages by spec.
Apply `references/page-generation-spec.md` and ensure mandatory behaviors:
- safe route id parsing
- 0-based backend paging mapped to 1-based UI paging
- `ElMessageBox.confirm` for destructive operations
- runtime-safe rendering for uncertain API field shapes

5. Apply dashboard spec only when needed.
For dashboard requests, apply `references/dashboard-best-practices.md` for layout, state regions, and visual quality.

6. Generate route module.
Create `src/router/modules/<kebab-module>.ts` using repository route conventions.

7. Verify before final output.
Run at least `pnpm typecheck`. Fix generated files if checks fail.

8. Return the result with the fixed contract.
Use exactly the four output sections defined by `references/output-contract.md`.

## Degrade Gracefully
When full CRUD is not available:

- generate only valid pages/operations
- remove unsupported actions from UI
- explicitly report missing CRUD endpoints
- keep code runnable and predictable

## Optional VueUse Policy
VueUse composables are optional. Use them only when complexity justifies it and `@vueuse/core` already exists in the project.

- do not add dependency automatically
- keep manual `ref/reactive` flow for simple pages
- when available in this session, `vueuse-functions` can be used for composable selection patterns

## Completion Checklist
Before returning:

1. Output section order matches `output-contract.md` exactly.
2. Generated files compile under project typecheck.
3. Pagination semantics preserve backend totals and page index mapping.
4. Invalid route id handling is explicit and safe (no silent fallback to create mode).
5. List filters reflect real API query fields (no fabricated backend filters).
