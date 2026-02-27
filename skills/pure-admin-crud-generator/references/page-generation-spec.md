# Page Generation Specification

## Scope
Generate module pages in:

- `src/views/<module>/index.vue`
- `src/views/<module>/edit.vue`
- optional `src/views/<module>/detail.vue`
- `src/router/modules/<module>.ts`

Dashboard mode variant:

- `src/views/<module>/dashboard.vue` can replace `index.vue` as the main entry when user asks dashboard-first output.

Use Vue 3 + `script setup` + TypeScript.

Do not create reusable business components.

## 1. Naming and Paths
Use kebab-case for module folder and route file name.

Examples:

- `voice-generate-text` -> `src/views/voice-generate-text/*`
- `voice-generate-text` -> `src/router/modules/voice-generate-text.ts`

## 2. List Page Requirements (`index.vue`)
Include all required sections and behavior.

### 2.1 Filter area
Use:

- `el-form` with `inline`
- `el-form-item`
- `el-input`
- `el-select` or `el-switch` for status-like fields
- `el-date-picker` with `daterange` when time range exists

Filter source-of-truth rule:

- only generate API-backed filter fields that exist in list query params
- if list query only contains pagination fields, do not generate fake backend filter form items
- in pagination-only APIs, avoid "query" behavior that is actually client-side filtering on current page rows

Buttons:

- query: `el-button type="primary"`
- reset: default `el-button`
- create: `el-button type="success"`

### 2.2 Table area
Use:

- `el-table`
- `el-table-column`
- optional selection column for batch actions

Operation column must include:

- view
- edit
- delete

Delete operation must call `ElMessageBox.confirm` before request.

### 2.3 Pagination
Use `el-pagination` with required mapping:

- internal state: `pageIndex` (0-based), `pageSize`
- UI current page: `pageIndex + 1`
- page change: `pageIndex = uiPage - 1`
- filter change resets `pageIndex = 0`

Run initial fetch in `onMounted` for page index `0`.

Server pagination consistency rule:

- when API is paginated by server, `total` must come from server response fields
- do not override total with client-side filtered current-page length
- do not apply client-only filtering to paged subsets unless explicitly labeled as local filter

### 2.4 Feedback and loading
Use:

- `v-loading="loading"` on list container
- `ElMessage.error` on failed requests
- `ElMessage.success` on successful actions

## 3. Edit Page Requirements (`edit.vue`)
Use:

- `el-form`
- `el-form-item`
- `rules` validation (at least required rules)
- submit and cancel actions

## 3.1 Route id and mode
Must support params and query id, with params first.

```ts
const id = computed(() => route.params.id ?? route.query.id);
```

On mounted:

1. read id
2. if id exists -> edit mode, fetch detail, fill model
3. if id absent -> create mode, initialize defaults

Use `v-loading="loading"` and `ElMessage.error("Load failed")` on fetch failure.

Invalid route id guard (mandatory):

- if route carries an id but parsing fails, do not silently fallback to create mode
- show `ElMessage.error` and navigate back to list (or router.back)
- apply the same guard to `detail.vue`

## 3.2 Field-to-control mapping
Apply this default mapping:

- string -> `el-input`
- number/int -> `el-input-number`
- boolean -> `el-switch`
- enum -> `el-select`
- date/datetime -> `el-date-picker`
- array<string> enum-like -> `el-select multiple` or `el-checkbox-group`
- long text (`text`, `remark`, `desc`) -> `el-input type="textarea"`
- file/image (only when clearly indicated) -> `el-upload`

## 4. Detail Page Requirements (`detail.vue`)
When generated, it must:

- parse route id with same logic as edit page
- auto-fetch detail in `onMounted`
- use `v-loading` and message feedback
- render with `el-descriptions` or `el-card` + `el-row` + `el-col`
- render `el-empty` when request succeeds but detail payload is empty

Do not create custom display components.

## 5. Action Endpoint Handling
For detected actions:

- add button in operation column
- apply `ElMessageBox.confirm` when action is destructive or sensitive
- on success: `ElMessage.success` and refresh list
- on error: `ElMessage.error`

## 6. Route Module Spec
Generate `src/router/modules/<module>.ts` in local style:

- import layout lazily
- define module root route and children
- use `satisfies RouteConfigsTable`
- set `meta.title` and icon (`ep/setting` default if unknown)

Use this default route definition rule:

- root path: `routeBase` or `/<module>`
- root redirect: `<rootPath>/index`
- list path: `<rootPath>/index`
- edit path: `<rootPath>/edit/:id?`
- detail path: `<rootPath>/detail/:id` (only when detail page exists)
- `showLink: true` for root and list route
- `showLink: false` for edit/detail route
- `activePath: <rootPath>/index` for hidden edit/detail routes

If user explicitly requests camelCase route paths, keep it through `routeBase` and still follow the same child path pattern.

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
    title: "音色",
    icon: "ep/setting"
  },
  children: [
    {
      path: "/voice-features/index",
      name: "voiceFeaturesIndex",
      component: () => import("@/views/voice-features/index.vue"),
      meta: {
        title: "音色列表",
        showLink: true
      }
    },
    {
      path: "/voice-features/edit/:id?",
      name: "voiceFeaturesEdit",
      component: () => import("@/views/voice-features/edit.vue"),
      meta: {
        title: "音色编辑",
        showLink: false,
        activePath: "/voice-features/index"
      }
    }
  ]
} satisfies RouteConfigsTable;
```

## 7. API Call Usage
Always use `API` from `src/api/api.ts`.

Access response with repository-first assumption:

- first try `res.data`
- then fallback keys for non-standard responses

Keep request helpers local to each page; do not create shared abstractions.

Runtime shape guard rule (mandatory):

- never call array methods (`join`, `map`, `filter`, `forEach`) directly on API fields without runtime guard
- use `Array.isArray(...)` (or dedicated normalizer helpers) before array operations
- for uncertain fields, provide safe format helpers that return fallback display strings (`"-"`/`""`) instead of throwing
- templates must avoid crash-prone expressions like `foo?.join(", ")` when `foo` may be non-array at runtime

## 8. Verification Checklist
Before final answer:

1. ensure page imports compile
2. ensure route file compiles
3. run `pnpm typecheck`
4. confirm no forbidden custom component introduced

## 9. Dashboard Page Skeleton (When `pageMode=dashboard` or user asks dashboard)
Build dashboard pages with this structure:

- top filter area: `el-form inline`
- metric cards area: `el-row` + `el-col` + `el-card`
- main content area: chart cards and table cards with `el-card`
- action area: refresh/export/quick actions

Recommended path:

- `src/views/<module>/dashboard.vue` or `src/views/<module>/index.vue` (if dashboard-only module)

Dashboard polish baseline:

- use titled sections/cards with clear hierarchy instead of one flat container
- use `el-space`/`el-row`/`el-col` for stable rhythm and responsive wrapping
- key data should be visually scannable (KPI cards, status tags, aligned numeric columns)

## 10. Unified Error and Retry
Every async block should keep explicit status:

- `loading`
- `errorMessage`
- success data

UI behavior:

- loading: `v-loading` or `el-skeleton`
- error: inline `el-alert` plus retry button
- retry button reuses the same request function and preserves current query state

Do not only toast errors. Keep visible recoverable state on the page.

## 11. VueUse Composable Rule
You can simplify request state management with VueUse composables, for example:

```ts
import { useAsyncState } from "@vueuse/core";
```

Use this policy (optional, not mandatory):

1. first check if project already has `@vueuse/core`
2. if dependency is missing, do not add it automatically; fallback to `ref/reactive` + manual `loading/error` states
3. if dependency exists, AI should decide whether VueUse reduces complexity; do not force it on every page
4. generated code must remain runnable under repository constraints

Dependency check options:

- inspect `package.json` dependencies
- or run `pnpm ls @vueuse/core --depth=0`

Decision guideline:

- use VueUse when page has multiple async regions, retry flows, or polling requirements
- keep manual state when page is small and direct `async/await` is clearer

When using VueUse composables, keep these behaviors:

- keep 0-based and 1-based pagination mapping unchanged
- keep `route.params.id ?? route.query.id` detail auto-fetch logic unchanged
- keep confirm dialogs and success/error messages unchanged

Recommended best practices:

- list request: call `execute`/refresh function on query and pagination change
- detail request: gate by valid id and trigger only when id exists
- retry: bind retry button to the same request executor
- action request: keep explicit success callback and refresh list after mutation
- avoid stale updates with abort/cleanup on route leave when needed
