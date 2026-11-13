# Framework Pack: React SPA (react-router + Tailwind + shadcn-style primitives)

Reference implementation: `zdmaker-tools/frontend`. Patterns below are verified there; a project with the same stack but different structure follows the project. See [Discovery Wins Over Packs](../conventions-discovery.md#discovery-wins-over-packs).

## Table of Contents
- [Detection Signals](#detection-signals)
- [File Layout](#file-layout)
- [API Consumption](#api-consumption)
- [Route Registration](#route-registration)
- [Menu Registration](#menu-registration)
- [List Page](#list-page)
- [Create / Edit Modal](#create--edit-modal)
- [Detail Page](#detail-page)
- [Permissions](#permissions)
- [Theming and UI Language](#theming-and-ui-language)
- [Verification](#verification)
- [Anti-patterns](#anti-patterns)

## Detection Signals

`package.json` contains `react`, `react-router-dom`, Tailwind, `lucide-react`, and often Radix UI primitives; shared primitives live under `src/shared/components/ui/`; all routes are declared in one `src/app/router.tsx`; pages live under `src/features/<slice>/pages/`. No react-query, Redux, Zustand, react-hook-form, or zod in the manifest — do not introduce them.

## File Layout

```
src/features/<slice>/pages/<Name>Page.tsx      # page component (default export)
src/features/<slice>/components/<Name>Modal.tsx# create/edit modal
src/api/domain/<domain>/<name>Api.ts           # hand-written wrapper methods
src/app/router.tsx                             # lazy const + <Route>
src/features/<slice>/components/<Slice>Layout.tsx  # menu entries + auth gate
```

Feature slices may import across slices, but `shared/` must never import `features/` or `app/`. A new shared component is justified only when at least two slices use it; otherwise keep it inside the slice.

## API Consumption

The generated client is instantiated once in the transport module (`src/api/http/client.ts` in the reference project):

```ts
export const httpClient = new HttpClient({ baseURL: "/", timeout: API_TIMEOUT_MS });
export const api = new Api(httpClient).api;
```

Two consumption flavors exist; detect which one the neighboring feature uses and stay consistent within the feature:

| Flavor | Shape | Error handling |
|---|---|---|
| Domain wrapper (`src/api/domain/**`) | `const res = await api.adminListList({ page, page_size }); const data = res.data?.data;` — no unwrap | raw axios error; pages read `err.response?.data?.message` |
| Direct `unwrap(api.xxx())` | returns the payload, throws `ApiError` | `ApiError` with a user-facing message |

CRUD/system pages use the domain-wrapper flavor in the reference project. Extend the existing wrapper for the module rather than calling the client from the page. Generated methods are proto-derived (`adminListList`, `consumableCreateCreate`) and return `AxiosResponse<HttpzDataResponse<...>>`; query params are snake_case.

Envelope keys are snake_case: list payloads expose `admins` / `consumables` / `total_size` / `total_page`, and mutations return `res.data?.data?.admin`. Import or re-export request/response/item types from the generated client (the reference wrappers re-export entity types); never edit `Api.ts`.

## Route Registration

Three edits, all required:

1. Lazy component const at the top of `src/app/router.tsx`:

```tsx
const ConsumablesPage = lazy(() => import('@/features/system/pages/ConsumablesPage'));
```

2. A `<Route>` inside the owning layout route (paths relative, no leading slash; unknown paths redirect to `/`):

```tsx
<Route path="system" element={<RequireProductionAuth module="system"><SystemLayout /></RequireProductionAuth>}>
  <Route index element={<SystemIndexRedirect />} />
  <Route path="consumables" element={<ConsumablesPage />} />
</Route>
```

3. The menu entry in the layout component's array (see below).

Do not add a root-level layout with `<Outlet/>` around all routes; the reference project keeps routes flat under the app chrome on purpose. Do not use `useBlocker` — this is a `BrowserRouter`, not a data router.

Registration can span more than these three sites (a permission map or shared navigation component, for example). Trace every touchpoint during discovery before editing, and prefer anchored patches.

## Menu Registration

Each layout owns its menu array:

```tsx
const SYSTEM_MENU_ITEMS: SystemMenuItem[] = [
  { path: 'consumables', label: '耗材管理', description: '库存录入与出入库流水', icon: Package },
];
```

Items render as `<NavLink>`; an optional `adminOnly` flag filters items by `isAdmin`. **Do not copy permission flags from this or any nearby example** — check the project's permission map and the API's documented role requirements first. In the reference repo the consumable endpoints need only a logged-in session, so that menu entry deliberately carries no `adminOnly`. Add the entry, keep the label style consistent, and reuse an existing lucide icon rather than inventing decorative markup.

## List Page

Structure, top to bottom:

- root `<div className="flex h-full flex-col overflow-hidden">`
- `<PageHeader title description actions={<refresh + create buttons>} />`
- filter bar with raw `<Input>`/`<Select>` and local state; send `keyword`/`type` to the server when the API supports it (client-side filtering only when it does not)
- inline error banner on failure (red-tinted border/background classes)
- table region `min-h-0 flex-1 overflow-auto p-6` containing a hand-written `<table>`: `<thead>` with the project's header classes, loading/empty row with `<Loader2 className="animate-spin">`, row actions as ghost `<Button>` with lucide icons
- `<PaginationBar page pageSize total onPageChange onPageSizeChange />` — UI is 1-based; the domain wrapper converts with `Math.max(0, page - 1)`

Loading pattern: `loading`/`errorMsg` state plus `loadData` in `useCallback` and `useEffect(() => { void loadData(); }, [loadData])`. There is no query-cache invalidation; refresh by re-running `loadData` after mutations. `useAutoRefresh(enabled, intervalMs, onTick)` exists for polling pages. Delete confirmation is an inline `<Dialog>` driven by `deleteTarget` and `deleting` state.

## Create / Edit Modal

Modal components follow this contract:

```tsx
type Props = { open: boolean; item: Item | null; onClose: () => void; onSuccess: () => void };
const isEditing = Boolean(item?.id);
```

- Radix `Dialog` / `DialogContent` / `DialogHeader` / `DialogTitle` / `DialogFooter`
- controlled `useState` per field, seeded in `useEffect` when `open`
- validation is manual `if` checks with a Chinese message in an inline banner; no validation library
- submit calls the domain wrapper, then `onSuccess(); onClose();`; a busy flag disables inputs and shows `<Loader2>`
- server errors render in the same banner

Enum/select options come from the options dictionary, not hardcoded labels: `useOptions('production_role')` / `getOptionLabel('production_role', slug)`.

## Detail Page

When the API exposes a detail endpoint and the flow needs a page, follow the project's existing detail pages: fetch by route param with an invalid-id guard, render read-only descriptions/cards with project primitives, and show an empty state when the payload is empty. If comparable feature pages use a modal instead, mirror that.

## Permissions

| Mechanism | Use |
|---|---|
| `<RequireProductionAuth module="system" permission="perm:..." adminOnly>` | route access; redirects unauthenticated users and sends unauthorized users to their first accessible path |
| `useProductionAuth()` -> `isAdmin`, `hasPermission`, `canAccess` | conditional controls inside pages |
| static `ROLE_PERMISSIONS` / `MODULE_REQUIRED_PERMISSIONS` (`src/features/auth/permissions.ts`) | role/module mapping |

Gate buttons with `isAdmin`/`hasPermission` when a comparable page does. Changing role mappings, modules, or permissions also requires updating the repository's permission spec file (`spec/API_ROLE_PERMISSIONS.md` in the reference repo) — check the project's rule file for the exact requirement. Before gating anything, verify what the backend actually requires: some modules need only a valid login and must stay ungated.

## Theming and UI Language

Use semantic Tailwind tokens: `bg-background`, `bg-card`, `text-foreground`, `text-foreground-soft`, `text-foreground-faint`, `text-muted-foreground`, `border-border/10`, `bg-accent text-accent-foreground`, `text-destructive`. Never hardcode theme hex values or use `text-white/xx` for UI text; status text uses patterns like `text-red-600 dark:text-red-400`. For dates, reuse whatever the project actually has: the reference project has no `src/utils/format` module — each page defines the same local `formatTimestamp` (unix seconds) helper, so mirror that rather than creating a shared module that does not exist.

UI strings, comments, and error messages follow the project's language; the reference project is Chinese. Error text thrown from library code surfaces directly in the UI.

## Verification

- `pnpm build` (which runs `tsc -b && vite build`) is the typecheck; there is no test runner. Use the project's actual script.
- `pnpm lint` (oxlint in the reference project) should stay clean.
- Route, menu, and auth guard are all updated; the page is reachable.
- Pagination converts 1-based UI to the API's 0-based page.
- No new dependency; generated `Api.ts` untouched; `shared/` did not import `features/`/`app/`.
- Domain wrapper added for any missing method instead of calling the client from the component.

## Anti-patterns

- Adding react-query, Zustand, react-hook-form, zod, or any dependency the manifest does not already have.
- Running `npx shadcn add` — the reference project's `components.json` has stale aliases; files land in the wrong directory.
- Hand-editing `src/api/swagger/Api.ts` (it is `@ts-nocheck`, so mistakes are invisible).
- Mixing the two API flavors inside one feature.
- Importing through an `@/api` barrel; import concrete paths.
- Hardcoded enum labels instead of the options dictionary.
- Replacing the server total with the current page length.
