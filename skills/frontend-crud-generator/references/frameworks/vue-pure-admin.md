# Framework Pack: Vue 3 + Element Plus (pure-admin-thin)

Reference implementation: `cardbot-ng/assets/dash/dashboard` (pure-admin-thin v6.x). Patterns below are verified there; a project with the same stack but different structure follows the project. See [Discovery Wins Over Packs](../conventions-discovery.md#discovery-wins-over-packs).

## Table of Contents
- [Detection Signals](#detection-signals)
- [File Layout](#file-layout)
- [API Consumption](#api-consumption)
- [List Page](#list-page)
- [Edit / Create Page](#edit--create-page)
- [Detail Page](#detail-page)
- [Route Module](#route-module)
- [Page Name and keepAlive](#page-name-and-keepalive)
- [Permissions](#permissions)
- [Formatters and UI Language](#formatters-and-ui-language)
- [Optional VueUse Policy](#optional-vueuse-policy)
- [Verification](#verification)
- [Anti-patterns](#anti-patterns)

## Detection Signals

`package.json` contains `vue`, `vue-router`, `pinia`, `element-plus`, usually `@pureadmin/table` and `@vueuse/core`; routes live under `src/router/modules/`; views under `src/views/<module>/`. Element Plus is commonly registered globally.

## File Layout

```
src/views/<module>/index.vue      # list
src/views/<module>/edit.vue       # create + edit (route id decides)
src/views/<module>/detail.vue     # optional
src/router/modules/<module>.ts    # route module, auto-collected
```

Use kebab-case for the module directory and route file. Route modules are collected by `import.meta.glob(["./modules/**/*.ts", "!./modules/**/remaining.ts"], { eager: true })`, so no index file needs editing. Verify the glob in the project before relying on it.

Forms are routed pages here, not dialogs. Do not introduce `el-dialog` CRUD forms into a project whose existing pages route to `edit.vue`.

## API Consumption

Detect before writing calls:

- If pages import a hand-written wrapper (`src/api/api.ts`, `src/api/<domain>.ts`), extend that wrapper with the module's methods and keep pages on plain data. This is what the reference project does: `productApi.list({ page, page_size })` resolves to `{ products, total_size, total_page }` through a `PureHttp` layer that unwraps `{ success, data }`.
- If the project genuinely consumes the generated client, instantiate it once next to the project's HTTP setup and expose `new Api(httpClient).api`; wire the auth header through the client's security worker, never by editing the generated file.
- When the generated `Api.ts` exists but nothing imports it, do not "fix" that by calling it from pages. Follow the project's transport, mirror the wrapper's type-source convention (below), and report the divergence in Validation Notes.

Type source: mirror what the existing wrappers do. In the reference project every wrapper redeclares local item interfaces (`ProductItem`, `AdminItem`, ...) and never imports the generated client, even for types — follow that there. When a project's wrappers import or re-export client types, follow that instead.

Response keys are snake_case (`total_size`, `total_page`, `created_at`); update is typically `POST /api/<module>/update` with the id in the body. Timestamps are unix seconds.

## List Page

- Root template `<div class="main">`; Tailwind utility classes are acceptable alongside Element Plus.
- Filters: `<el-form :inline="true" @submit.prevent>` with `el-input` / `el-select`; bind a `reactive` filter object; send unset values as `|| undefined`; convert date ranges to the API's expected format (the reference project sends unix seconds).
- Table: `<el-table v-loading="loading" :data="items" border stripe>`; action column `fixed="right"` with `link` buttons.
- Pagination (reference project: 0-based internal, 1-based control; confirm against an existing list page and follow the project if it differs):

```html
<el-pagination
  layout="total, sizes, prev, pager, next"
  :total="total"
  :page-size="pageSize"
  :current-page="page + 1"
  :page-sizes="[10, 20, 50]"
  @size-change="onSizeChange"
  @current-change="onPageChange"
/>
```

```ts
const page = ref(0);
const pageSize = ref(20);
function onSearch() { page.value = 0; load(); }
function onPageChange(p: number) { page.value = p - 1; load(); }
```

- Destructive actions: `ElMessageBox.confirm(...)` before the request; `ElMessageBox.prompt` for actions that need input, as the reference project does for blocking a user. On success `ElMessage.success`, then reload.
- Load errors surface through `ElMessage.error` and/or an inline state.

## Edit / Create Page

```ts
defineOptions({ name: "ProductEdit" });
const id = computed(() => Number(route.params.id ?? 0));
const isCreate = computed(() => !id.value);
```

- `FormInstance` + `FormRules` from `element-plus`; at minimum required rules; validators for money/percent-style fields rather than raw coercion.
- On mount, prefill the form in edit mode: fetch the detail endpoint when one exists, otherwise use the row data the list passes into the edit page; create mode initializes defaults. Never fetch a detail endpoint that does not exist.
- Invalid id guard: a non-numeric or unresolvable id shows an error and returns to the list; never silently creates.
- Submit: validate, set `saving`, call create or update, `ElMessage.success`, then `router.push` back to the list. Cancel is `router.back()`.

Field-to-control mapping:

| Field | Control |
|---|---|
| string | `el-input` |
| number | `el-input-number` |
| boolean | `el-switch` |
| enum | `el-select` |
| date/datetime | `el-date-picker` |
| string array | `el-select multiple` or `el-checkbox-group` |
| long text | `el-input type="textarea"` |
| file/image | `el-upload`, only when the API semantics require it |

## Detail Page

`el-page-header` plus `<el-descriptions :column="2" border>` with `v-if` on the loaded payload; render `el-empty` when the request succeeds but the payload is empty. Parse the id as in edit; a missing or invalid id redirects to the list.

## Route Module

`src/router/modules/<module>.ts`:

```ts
const Layout = () => import("@/layout/index.vue");

export default {
  path: "/product",
  name: "Shop",
  component: Layout,
  redirect: "/product/index",
  meta: { icon: "ep/goods", title: "商品", rank: 1 },
  children: [
    { path: "/product/index", name: "ProductIndex", component: () => import("@/views/product/index.vue"), meta: { title: "商品列表" } },
    { path: "/product/edit/:id?", name: "ProductEdit", component: () => import("@/views/product/edit.vue"), meta: { title: "编辑商品", showLink: false, activePath: "/product/index" } }
  ]
} satisfies RouteConfigsTable;
```

Rules:

- `satisfies RouteConfigsTable` for type safety; import it from `@/router/types` only if the project does not declare it globally.
- Child paths are absolute; root redirects to the list path.
- `rank` only on top-level routes and controls menu order; use the next free value and note the choice if the range is crowded; icons are iconify strings (`ep/setting`, `ep/goods`).
- Hidden routes (edit, detail) set `showLink: false` and `meta.activePath` pointing at the list.
- Route names are unique; follow the project's existing naming (`<Module>Camel><Page>`).
- Reuse the project's titles and icon style; UI strings follow the project's language (the reference project uses Chinese).

## Page Name and keepAlive

pure-admin caches pages by route name. Every view must declare a component name that matches its route name:

```ts
defineOptions({ name: "ProductEdit" });
```

A mismatch silently breaks keepAlive — the page re-mounts and loses filter state. Add this to every generated view.

## Permissions

Verified mechanisms in the reference project (do not use `usePermissionStoreHook().auths` or `.roles` — stock pure-admin-thin has no such store fields):

| Mechanism | Reads from | Use for |
|---|---|---|
| `v-auth` directive / `hasAuth()` | `route.meta.auths` | route-scoped action keys |
| `v-perms` directive / `hasPerms()` | user store `permissions` (wildcard `*:*:*`) | backend-driven permission keys |
| `meta.roles` | route metadata, checked in the router | page access |

`<Auth value="...">` and `<Perms value="...">` wrappers exist for template use. Static module routes in the reference project set no `roles`/`auths`; do not add metadata speculatively. Use the project's existing `btn_*` keys when they exist, otherwise generate ungated controls and say so in Validation Notes.

## Formatters and UI Language

Reuse the project's shared helpers before writing new ones: `formatMoney(cent)`, `yuanToCent(yuan)`, `formatTime(unixSeconds)`, and the status maps (`orderStatusMap`, `payTypeMap`, ...). Do not reformat timestamps by hand.

Match the project's UI language and label style; the reference project is Chinese.

## Optional VueUse Policy

VueUse is optional: use it only when the project already depends on `@vueuse/core` and the composable removes real complexity. Never add the dependency for generated pages; simple pages keep manual `ref`/`reactive` state. When available, `vueuse-functions` can help choose composables.

## Verification

- `pnpm typecheck` — the reference project runs `tsc --noEmit && vue-tsc --noEmit --skipLibCheck`. Use the project's actual script.
- Every generated view has `defineOptions({ name })` matching its route name.
- Type source matches the existing wrapper convention (local interfaces, or client types where the project imports them).
- Route module is picked up by the glob (no manual import) unless the project's router differs.
- Pagination is 0-based internally, 1-based in `el-pagination`.
- `ElMessageBox.confirm` guards every destructive action.
- No new dependency; generated `Api.ts` untouched.

## Anti-patterns

- `permissionStore.auths` / `permissionStore.roles` — these do not exist in stock pure-admin-thin.
- `el-dialog` CRUD forms in a project whose pages route to `edit.vue`.
- Editing `src/api/swagger/Api.ts`, or calling it directly when pages use a wrapper layer.
- Introducing generated-client type imports into a wrapper layer that redeclares its own interfaces (or redeclaring interfaces in a project whose wrappers re-export client types).
- Forgetting `defineOptions({ name })`, or letting it drift from the route name.
- Relative child paths in route modules.
- `route.query.id` only, without params-first parsing.
- Replacing the server total with the current page length.
