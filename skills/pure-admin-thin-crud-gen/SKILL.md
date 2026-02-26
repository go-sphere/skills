---
name: pure-admin-thin-crud-gen
description: Generate CRUD pages and router module files for pure-admin-thin by parsing src/api/swagger/Api.ts and src/api/api.ts in this repository. Use when asked to scaffold backend admin list/edit/detail pages, CRUD actions, and route modules from swagger-ts-api methods without external generators.
---

# Pure Admin Thin CRUD Generator

## Overview
Generate runnable Vue pages under `src/views/<module>/` and route modules under `src/router/modules/` from swagger-ts-api output in `src/api/swagger/Api.ts` plus the wrapper behavior in `src/api/api.ts`.

Keep generation AI-driven. Do not run external OpenAPI generators. Do not add helper generation scripts.

## Input Contract
Require these inputs before generation:

- `moduleSelector` (required): select target module by `tag`, entity name, or path keyword.
- `selectorMode` (optional): default `auto`. Allowed values: `auto`, `tag`, `entity`, `path`.
- `forceDetailPage` (optional): default `auto`. Allowed values: `auto`, `true`, `false`.
- `pageMode` (optional): default `crud`. Allowed values: `crud`, `dashboard`, `mixed`.
- `routeBase` (optional): default `/<kebab-module>`.
- `outputMode` (fixed): always output full file contents.

If the user only gives a vague module name, resolve it with `selectorMode=auto` and state the matched methods explicitly.

## Hard Constraints
Follow all rules below:

1. Parse and generate by AI from local `Api.ts` and `api.ts`.
2. Do not regenerate APIs with external tools.
3. Do not build reusable business UI component libraries.
4. Use only Element Plus components for page UI.
5. Generate pages by mode:
   - `crud`/`mixed`: generate at least `index.vue` and `edit.vue` (plus optional `detail.vue`)
   - `dashboard`: generate `dashboard.vue` or `index.vue`; add `edit.vue` only when create/update flow is required
6. Create `src/router/modules/<kebab-module>.ts`.
7. Use repository conventions first; only fall back to generic heuristics if needed.
8. Do not add new runtime dependencies just for generated pages.

## Repository-First Facts
Assume and use these local facts:

- API calls are made through `API` from `src/api/api.ts`.
- `API` unwraps axios response once and returns swagger response objects directly.
- Swagger methods live in `src/api/swagger/Api.ts` inside `new Api().api` method map.
- Method doc blocks include `@tags`, `@name`, `@summary`, `@request`.
- Router static modules are auto-collected by `import.meta.glob("./modules/**/*.ts")`; usually no `src/router/index.ts` edits are needed.

## Workflow
Execute this sequence every time.

### 1) Parse target API methods
Group candidate methods using `@tags`, path, and method names.

Identify:

- list: `/list` or method names ending with `List`
- detail: `/detail/{id}` or path with `/{id}` plus GET semantics
- create: `/create` or POST with create semantics
- update: `/update` or PUT/PATCH or POST update semantics
- delete: DELETE with `/{id}` or `/delete`
- action: non-CRUD operation (`retry`, `enable`, `disable`, `reset`, `export`, `vip`, etc.)

Read detailed rules from `references/api-parsing-rules.md`.

### 2) Infer request/response shapes
Infer from `Dashv1*Request/Response`, `Entpb*`, `Sharedv1*`, and `GinxDataResponse*`.

Determine:

- query fields
- pagination fields and base index
- list data key (`users`, `admins`, `voice_generate_text`, etc.)
- total key (`total_size`, `total`, `count`, fallback)
- form fields and scalar types

### 3) Decide generated files
Default set (`pageMode=crud|mixed`):

- `src/views/<module>/index.vue`
- `src/views/<module>/edit.vue`
- `src/router/modules/<module>.ts`

Mode adjustment:

- `pageMode=dashboard`: allow `src/views/<module>/dashboard.vue` as main page and skip `edit.vue` when module has no create/update requirement.

Generate `src/views/<module>/detail.vue` when:

- `forceDetailPage=true`, or
- a clear detail endpoint exists and read-only view improves usability, or
- field count and density make list-only preview unreasonable.

### 4) Apply required UI behavior
Read exact page rules from `references/page-generation-spec.md`.
When user asks dashboard pages, additionally apply `references/dashboard-best-practices.md`.

Mandatory behavior:

- list page filtering, table, pagination, loading, errors, success messages
- delete and action operations behind `ElMessageBox.confirm`
- edit/detail route id parsing and auto-fetch
- 0-based backend paging mapped to 1-based `el-pagination`
- unified error and retry behavior for each async block (table/card/chart)
- request abstraction is AI-selected: `useRequest` is optional and only used when it clearly simplifies complex async flows
- list filters must align with real API query fields (no fake backend filters)
- server-paged list must keep server `total` semantics (no client-side current-page total override)
- invalid route id must not fallback to create; show error and leave page safely
- detail page must show explicit empty state when payload is empty
- dashboard/list pages must satisfy visual quality baseline (hierarchy, spacing, table readability, semantic status style)
- rendering must be runtime-safe: no direct array method calls on uncertain API fields without `Array.isArray` guard/normalizer

Required snippets:

```ts
const id = computed(() => route.params.id ?? route.query.id);
```

```ts
const pageIndex = ref(0);
// UI current-page = pageIndex + 1
// onCurrentChange(uiPage) => pageIndex = uiPage - 1
```

### 5) Generate route module
Create `src/router/modules/<module>.ts` using local route style:

- `const Layout = () => import("@/layout/index.vue");`
- `export default { ... } satisfies RouteConfigsTable;`
- include menu `meta.title` and default icon when user does not specify one.
- route object must include `path`, `redirect`, `meta`, and `children`.
- default root `path` is `routeBase` or `/<module>`.
- default root `redirect` is `<rootPath>/index`.
- list child route uses `<rootPath>/index` and `showLink: true`.
- edit child route uses `<rootPath>/edit/:id?` and `showLink: false`.
- detail child route (when generated) uses `<rootPath>/detail/:id` and `showLink: false`.
- hidden child routes should set `meta.activePath` to list route path for menu highlight consistency.

### 6) Verify generated result
Run at least:

- `pnpm typecheck`

If typecheck fails, fix generated files before final output.

### 7) Return output in fixed contract
Always respond in the exact 4 sections defined in `references/output-contract.md`.

## Degrade Gracefully
If the selected module lacks full CRUD endpoints:

- generate only valid pages and operations
- remove unsupported actions from UI
- state missing endpoints in section 1 (API recognition)
- keep code runnable and predictable

## References
Load only needed files:

- API parsing rules: `references/api-parsing-rules.md`
- Page generation specification: `references/page-generation-spec.md`
- Dashboard best practices: `references/dashboard-best-practices.md`
- Response/output contract: `references/output-contract.md`

If considering `useRequest`, follow repository-safe policy:

- use import path `vue-hooks-plus/es/useRequest`
- do not add dependency automatically
- keep manual state flow when complexity is low
