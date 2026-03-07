---
name: pure-admin-crud-generator
description: Generate CRUD pages and router modules for pure-admin-thin from local swagger API definitions. MUST be used whenever you need to scaffold admin list/edit/detail pages, dashboard views, or route configurations from existing API methods in src/api/swagger/Api.ts. This skill replaces manual Vue page creation - use it for any admin panel development task involving API-driven pages.
---

# Pure Admin Thin CRUD Generator

## Overview
Generate runnable Vue pages under `src/views/<module>/` and route modules under `src/router/modules/` from local swagger-ts-api output in `src/api/swagger/Api.ts` and API wrapper behavior in `src/api/api.ts`.

This is an AI-first generator skill. Do not use external OpenAPI generators and do not add helper codegen scripts.

## When to Use
**ALWAYS use this skill** when the user asks to scaffold or update pure-admin-thin admin pages, including:

- CRUD pages (`index.vue`, `edit.vue`, optional `detail.vue`)
- dashboard-first admin pages
- route module files under `src/router/modules`
- action buttons backed by non-CRUD APIs (retry/enable/disable/export etc.)
- ANY admin management interface in a pure-admin-thin project

**Trigger examples:**
- "Generate admin pages for user management"
- "Create CRUD for voice-features module"
- "Add dashboard view for analytics"
- "Scaffold edit and detail pages for product management"
- "Generate route module and views for order management"

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

- `moduleSelector` (required): module tag/entity/path keyword (e.g., "user", "voice-features", "order").
- `selectorMode` (optional, default `auto`): `auto | tag | entity | path`.
- `forceDetailPage` (optional, default `auto`): `auto | true | false`.
- `pageMode` (optional, default `crud`): `crud | dashboard | mixed`.
- `routeBase` (optional, default `/<kebab-module>`).
- `outputMode` (fixed): full file contents only.

**Examples:**
- User says: "Generate pages for user management" → `moduleSelector="user"`, infer module from API tags
- User says: "Create dashboard for voice-generate-text" → `moduleSelector="voice-generate-text"`, `pageMode="dashboard"`
- User says: "Add edit page for product module" → `moduleSelector="product"`, generate edit.vue + route module

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

### Step 1: Parse API Definitions
1. Read `src/api/swagger/Api.ts` to find methods matching the module
2. Use `references/api-parsing-rules.md` for module resolution, CRUD/action classification
3. Identify all matching endpoints: list, detail, create, update, delete, and actions

### Step 2: Infer Data Structures
1. Parse TypeScript types for request parameters (query, body, path)
2. Identify response structures: items key (`records`, `list`, `items`), total key, detail payload
3. Map pagination keys: `page`/`pageIndex` → internal 0-based, UI shows +1

### Step 3: Plan File Set
- `crud | mixed`: `index.vue`, `edit.vue`, route module, optional `detail.vue`
- `dashboard`: `dashboard.vue` (or `index.vue`), optional `edit.vue`, route module

### Step 4: Generate Pages
Apply `references/page-generation-spec.md`:
- safe route id parsing: `const id = computed(() => route.params.id ?? route.query.id)`
- 0-based backend paging → 1-based UI mapping
- `ElMessageBox.confirm` for delete/destructive actions
- runtime-safe rendering: guard uncertain arrays with `Array.isArray()`

### Step 5: Apply Dashboard Spec (if needed)
For dashboard requests, apply `references/dashboard-best-practices.md`:
- filter row + metrics row + main content + actions
- independent loading/error/retry per region

### Step 6: Generate Route Module
Create `src/router/modules/<kebab-module>.ts`:
```ts
export default {
  path: "/<module>",
  redirect: "/<module>/index",
  children: [
    { path: "/<module>/index", component: () => import("@/views/<module>/index.vue") },
    { path: "/<module>/edit/:id?", component: () => import("@/views/<module>/edit.vue") }
  ]
} satisfies RouteConfigsTable
```

### Step 7: Verify
Run `pnpm typecheck`. Fix any errors in generated files.

### Step 8: Output
Return exactly the four sections defined by `references/output-contract.md`:
1. Recognized APIs
2. Files
3. File Contents
4. Route Registration

## Degrade Gracefully
When full CRUD is not available:

- Generate only valid pages/operations based on available endpoints
- Remove unsupported actions from UI (e.g., no delete button if no delete endpoint)
- Explicitly report missing CRUD endpoints in output section 1
- Keep code runnable even when some operations are unavailable

**Common degradation scenarios:**
- Only list endpoint → generate list page only, disable create/edit/delete buttons
- List + create only → generate index + edit (create mode), no edit for existing items
- No detail endpoint → omit detail page or disable view action

## Optional VueUse Policy
VueUse composables are optional. Use them only when complexity justifies it and `@vueuse/core` already exists in the project.

- do not add dependency automatically
- keep manual `ref/reactive` flow for simple pages
- when available in this session, `vueuse-functions` can be used for composable selection patterns

## Completion Checklist
Before returning, verify ALL of the following:

1. **Output format**: Section order matches `output-contract.md` exactly (Recognized APIs → Files → File Contents → Route Registration)
2. **Type safety**: Generated files compile under `pnpm typecheck`
3. **Pagination**: Internal state is 0-based, UI displays 1-based (`pageIndex + 1`)
4. **Route id handling**: Invalid id shows error message, does NOT silently fallback to create mode
5. **Filters**: Only include filters that match real API query parameters
6. **Delete safety**: All delete/destructive actions use `ElMessageBox.confirm`
7. **Runtime safety**: Uncertain API fields use `Array.isArray()` guards
8. **Missing endpoints**: Explicitly report which CRUD operations are unavailable
9. **Route module**: Root route redirects to `/index`, hidden routes use `showLink: false`
10. **Dashboard quality** (if dashboard mode): Has filter + metrics + main content + actions, per-region retry
