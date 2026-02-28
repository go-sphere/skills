# Page Generation Specification

## Table of Contents
- [Scope](#scope)
- [1. Naming and Paths](#1-naming-and-paths)
- [2. File Planning Rules](#2-file-planning-rules)
- [3. List Page Requirements (`index.vue`)](#3-list-page-requirements-indexvue)
- [4. Edit Page Requirements (`edit.vue`)](#4-edit-page-requirements-editvue)
- [5. Detail Page Requirements (`detail.vue`)](#5-detail-page-requirements-detailvue)
- [6. Action Endpoint Handling](#6-action-endpoint-handling)
- [7. Route Module Specification](#7-route-module-specification)
- [8. API Call Usage and Runtime Safety](#8-api-call-usage-and-runtime-safety)
- [9. Dashboard Variant](#9-dashboard-variant)
- [10. Unified Async Status and Retry](#10-unified-async-status-and-retry)
- [11. Optional VueUse Policy](#11-optional-vueuse-policy)
- [12. Verification Checklist](#12-verification-checklist)

## Scope
Generate module pages in:

- `src/views/<module>/index.vue`
- `src/views/<module>/edit.vue`
- optional `src/views/<module>/detail.vue`
- `src/router/modules/<module>.ts`

Dashboard variant:

- `src/views/<module>/dashboard.vue` can replace `index.vue` as main entry when dashboard-first output is requested.

Tech constraints:

- Vue 3 + `script setup` + TypeScript
- Element Plus UI components
- no reusable business component library generation

## 1. Naming and Paths
Use kebab-case for module folder and route file names.

Examples:

- `voice-generate-text` -> `src/views/voice-generate-text/*`
- `voice-generate-text` -> `src/router/modules/voice-generate-text.ts`

## 2. File Planning Rules
Default file plan (`pageMode=crud|mixed`):

- `src/views/<module>/index.vue`
- `src/views/<module>/edit.vue`
- `src/router/modules/<module>.ts`
- optional `src/views/<module>/detail.vue`

Dashboard-first plan (`pageMode=dashboard`):

- `src/views/<module>/dashboard.vue` (or `index.vue` if dashboard is the index page)
- add `edit.vue` only when create/update workflow exists
- optional `detail.vue` when detail endpoint exists and user flow needs it

## 3. List Page Requirements (`index.vue`)
List page must include filter area, table area, pagination, and async feedback.

### 3.1 Filter area
Use:

- `el-form` with `inline`
- `el-form-item`
- `el-input`
- `el-select` or `el-switch` for status-like fields
- `el-date-picker` (`daterange`) when time range exists

Filter source-of-truth rules:

- generate only API-backed filter fields that exist in list query params
- if list query has only pagination fields, do not fabricate backend filter fields
- do not implement client-only filtering on server-paged subsets unless explicitly labeled as local filter

Buttons:

- query: `el-button type="primary"`
- reset: default `el-button`
- create: `el-button type="success"` when create endpoint exists

### 3.2 Table area
Use:

- `el-table`
- `el-table-column`
- optional selection column for batch operations

Operation column should include supported actions based on recognized APIs:

- view (when detail endpoint exists)
- edit (when update endpoint exists)
- delete (when delete endpoint exists)
- action buttons for non-CRUD endpoints when relevant

Delete and destructive operations must call `ElMessageBox.confirm` before request execution.

### 3.3 Pagination
Use `el-pagination` with required mapping:

- internal state: `pageIndex` (0-based), `pageSize`
- UI page: `pageIndex + 1`
- page change: `pageIndex = uiPage - 1`
- any filter reset should set `pageIndex = 0`

Run initial fetch for page index `0` in `onMounted`.

Server pagination rule:

- `total` must come from server response when server paging is used
- do not override `total` with current-page filtered length

### 3.4 Feedback and loading
Use:

- `v-loading="loading"` for list container
- `ElMessage.error` on failed requests
- `ElMessage.success` on successful mutation actions

## 4. Edit Page Requirements (`edit.vue`)
Use:

- `el-form`
- `el-form-item`
- validation `rules` (at least required rules)
- submit and cancel actions

### 4.1 Route id and mode
Must parse id with params-first logic:

```ts
const id = computed(() => route.params.id ?? route.query.id);
```

On mounted:

1. read id
2. if id exists -> edit mode, fetch detail and fill model
3. if id is absent -> create mode, initialize defaults

Loading/error behavior:

- use `v-loading="loading"`
- on load failure use `ElMessage.error("Load failed")`

Invalid id guard (mandatory):

- if route carries an id but parsing fails, do not fallback silently to create mode
- show error and navigate safely (list route or `router.back()`)

### 4.2 Field-to-control mapping defaults
- string -> `el-input`
- number/int -> `el-input-number`
- boolean -> `el-switch`
- enum -> `el-select`
- date/datetime -> `el-date-picker`
- array<string> enum-like -> `el-select multiple` or `el-checkbox-group`
- long text (`text`, `remark`, `desc`) -> `el-input type="textarea"`
- file/image -> `el-upload` only when API semantics clearly require it

## 5. Detail Page Requirements (`detail.vue`)
When generated, detail page must:

- parse id with same logic as edit page
- auto-fetch detail on mounted
- use loading and error feedback
- render with `el-descriptions` or `el-card` + `el-row` + `el-col`
- render `el-empty` when request succeeds but payload is empty

Apply the same invalid-id guard used by `edit.vue`.

## 6. Action Endpoint Handling
For recognized non-CRUD action endpoints:

- add operation buttons only for supported actions
- use `ElMessageBox.confirm` for risky/destructive actions
- on success: show `ElMessage.success` and refresh current list state
- on error: show `ElMessage.error`

## 7. Route Module Specification
Generate `src/router/modules/<module>.ts` in repository style.

Required traits:

- lazy layout import: `const Layout = () => import("@/layout/index.vue")`
- route export uses `satisfies RouteConfigsTable`
- include root route `path`, `redirect`, `meta`, `children`
- default icon: `ep/setting` if no explicit icon is provided

Default route structure:

- root path: `routeBase` or `/<module>`
- root redirect: `<rootPath>/index`
- list path: `<rootPath>/index`
- edit path: `<rootPath>/edit/:id?`
- detail path: `<rootPath>/detail/:id` (only when detail page exists)
- `showLink: true` for root/list
- `showLink: false` for edit/detail
- hidden edit/detail routes should set `meta.activePath = <rootPath>/index`

Default route name convention:

- list: `<moduleCamel>Index`
- edit: `<moduleCamel>Edit`
- detail: `<moduleCamel>Detail`

Reference template:

```ts
const Layout = () => import("@/layout/index.vue");

export default {
  path: "/voice-features",
  redirect: "/voice-features/index",
  meta: {
    showLink: true,
    title: "Voice Features",
    icon: "ep/setting"
  },
  children: [
    {
      path: "/voice-features/index",
      name: "voiceFeaturesIndex",
      component: () => import("@/views/voice-features/index.vue"),
      meta: {
        title: "Voice Features List",
        showLink: true
      }
    },
    {
      path: "/voice-features/edit/:id?",
      name: "voiceFeaturesEdit",
      component: () => import("@/views/voice-features/edit.vue"),
      meta: {
        title: "Voice Features Edit",
        showLink: false,
        activePath: "/voice-features/index"
      }
    }
  ]
} satisfies RouteConfigsTable;
```

## 8. API Call Usage and Runtime Safety
Always use `API` from `src/api/api.ts`.

Response handling priority:

- first inspect `res.data`
- then fallback to non-standard keys only if needed

Keep request helpers local to each page.

Runtime safety rules (mandatory):

- never call `join/map/filter/forEach` directly on uncertain API fields
- guard uncertain arrays with `Array.isArray(...)` or normalizer helpers
- provide safe format helpers with fallback values
- avoid crash-prone template expressions for uncertain field shapes

## 9. Dashboard Variant
When dashboard mode is required, build this skeleton:

- filter area (`el-form inline`)
- metrics area (`el-row` + `el-col` + `el-card`)
- main content area (table/chart cards)
- actions area (refresh/export/quick ops)

Dashboard quality baseline:

- clear visual hierarchy with titled blocks
- spacing rhythm via `el-space` / grid layout
- scannable key data (KPI cards, status tags, aligned numeric columns)

For dashboard-specific details, also apply `dashboard-best-practices.md`.

## 10. Unified Async Status and Retry
Each async region should maintain:

- `loading`
- `errorMessage`
- success data payload

UI behavior:

- loading: `v-loading` or `el-skeleton`
- error: inline `el-alert` with retry button
- retry must call the same request function and keep current query state

Do not rely on toast-only error handling.

## 11. Optional VueUse Policy
VueUse usage is optional.

Example import:

```ts
import { useAsyncState } from "@vueuse/core";
```

Policy:

1. first check whether `@vueuse/core` exists
2. if missing, do not add dependency automatically
3. if present, use VueUse only when complexity reduction is clear
4. generated code must remain runnable under repository constraints

Dependency check options:

- inspect `package.json`
- run `pnpm ls @vueuse/core --depth=0`

When using VueUse, keep required behavior unchanged:

- pagination mapping
- id extraction logic
- confirm dialogs and message feedback

## 12. Verification Checklist
Before final response:

1. page imports compile
2. route module compiles
3. run `pnpm typecheck`
4. no forbidden shared business component is introduced
5. invalid route id handling is explicit in edit/detail pages
6. server total semantics are preserved for paged APIs
7. uncertain response field rendering is runtime-safe
