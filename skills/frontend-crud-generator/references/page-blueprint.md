# Page Blueprint

## Table of Contents
- [Scope](#scope)
- [Page Set by Mode](#page-set-by-mode)
- [1. List Page Contract](#1-list-page-contract)
- [2. Edit / Create Page Contract](#2-edit--create-page-contract)
- [3. Detail Page Contract](#3-detail-page-contract)
- [4. Action Endpoints](#4-action-endpoints)
- [5. Runtime Safety](#5-runtime-safety)
- [6. Degradation](#6-degradation)
- [7. Dashboard Variant](#7-dashboard-variant)

## Scope

This file is the framework-neutral behavioral contract for generated pages: what must exist and how it must behave. It never names a component library or framework API. The matching pack in `references/frameworks/` decides how each item is rendered.

Framework mapping of the same contract: a component per region, a state holder, an event handler. If a behavior below cannot be expressed with the project's primitives, report it as a blocking issue instead of dropping it.

## Page Set by Mode

| `pageMode` | Files |
|---|---|
| `crud` | list, edit (create and edit share one page unless the project separates them), route registration; detail only when the detail endpoint exists and the flow needs it |
| `dashboard` | dashboard page plus route registration; add edit/detail only when create/update workflows exist |
| `mixed` | list + edit + optional detail + a dashboard block inside the module route |

Use kebab-case module names for directories and route files; use the project's own naming for components and route names.

## 1. List Page Contract

Regions, in order: filters, table, pagination, async feedback.

### 1.1 Filters

- Generate only filters backed by real query parameters of the list endpoint.
- If the list query has only pagination fields, do not fabricate filter fields.
- Do not client-filter a server-paged subset unless the control is explicitly labeled as a local filter.
- Reset clears every filter and returns pagination to the project's first page value.

### 1.2 Table

- Columns come from fields that exist in the list payload type; long text gets truncation or overflow handling.
- Row actions are limited to operations the client actually exposes: view (detail), edit (update), delete (delete), plus action buttons.
- Destructive actions require a confirmation step before the request, using the project's confirmation primitive.
- Numbers align consistently; status-like fields render with the project's status affordance rather than raw numbers when a mapping exists.

### 1.3 Pagination

- Keep the project's observed base for internal state; derive the control's value from it.
- If the project is 0-based internally, UI shows `page + 1` and page changes set `page = uiPage - 1`; if it is 1-based, pass through. Confirm against an existing list page.
- Any filter change resets to the first page.
- Run the initial fetch on mount.
- `total` always comes from the server response; never substitute the current page length.

### 1.4 Feedback

- One `loading` state around the list request; failures surface a readable error in the page, not only in the console.
- Loading, empty, and error states are visually distinct; an empty result is not an error.
- Mutations report success/failure through the project's notification mechanism and refresh the list; when the project has no toast/notification primitive, inline success or error feedback is the correct fallback.

## 2. Edit / Create Page Contract

- Read the route id using the project's observed route mechanism, params first, then query. If the project has no precedent for a routed id (no router library, no existing edit route), do not invent URL parsing: prefer editing in place from the list row, or stop and ask one question.
- Id present -> edit mode: prefill from the detail endpoint when one exists; otherwise from the row payload the project already passes into the form (modal or list-row edit). If neither source exists, degrade or ask — never invent a fetch or a detail endpoint.
- Id absent -> create mode: initialize defaults.
- **Invalid id guard (mandatory):** if the route carries an id that cannot be parsed or resolved, show an error and leave the page safely (back to list or back). Never silently fall back to create mode.
- Fields map to controls by type: string -> text input, number -> number input, boolean -> switch, enum -> select, date/time -> date picker, string arrays -> multi-select or checkbox group, long text -> textarea, file/image -> upload only when the API semantics require it. Use the closest primitive the project actually has; with no component kit, native inputs are the correct mapping, and a field with no available primitive is omitted rather than approximated.
- At minimum, required-field validation matching the request type.
- Submit disables the form while in flight; cancel returns without mutating.
- Create and edit share one page unless the project splits them; keep one payload builder to avoid drift.

## 3. Detail Page Contract

- Same id parsing and invalid-id guard as edit.
- Auto-fetch on mount with loading and error feedback.
- Render empty state when the request succeeds but the payload is empty.
- Read-only: no mutation controls except explicit action buttons.

## 4. Action Endpoints

For non-CRUD operations (`retry`, `enable`, `disable`, `export`, ...):

- render a button only for endpoints the client exposes
- confirm risky or destructive actions before the request
- refresh the affected list region after success; report errors inline or via the project's notification mechanism
- when an action's request/response shape is unclear, state the assumption in Validation Notes

## 5. Runtime Safety

- Never call `join/map/filter/forEach` directly on a field whose shape is uncertain; guard with `Array.isArray(...)` or a normalizer.
- Null/undefined-check optional fields before rendering nested data.
- Provide safe formatters with fallback values for dates, money, and statuses.
- Avoid crash-prone expressions in templates/JSX; compute derived values in code.

## 6. Degradation

Generate only operations the client supports and report the gaps explicitly.

| Situation | Behavior |
|---|---|
| list only | list page; create/edit/delete controls absent, not disabled-but-broken |
| list + create | list and create mode only; no edit action on existing rows |
| no detail endpoint | omit detail page and view action |
| no delete endpoint | omit delete action |
| no list endpoint | do not fabricate one; report and stop |
| update without detail | edit prefills from the row data the project passes to the form; never call a detail endpoint that does not exist |
| requested field or filter absent from the API | omit the control; report it as a contract gap for `proto-api-generator` |

Partial CRUD must still run. Unavailable operations are named in the report, never silently omitted. Capabilities the user explicitly asked for that the client cannot support are listed as contract gaps, each with the proto change or endpoint it would need, and handed to `proto-api-generator` rather than faked.

## 7. Dashboard Variant

Skeleton, top to bottom:

1. **Filter region** — keyword, status, time range, and only parameters the APIs accept
2. **Metrics region** — KPI blocks, each with title, primary value, secondary context
3. **Main content region** — tables and charts, each in its own titled block
4. **Actions region** — refresh, export, and secondary operations in a predictable place

Region contract, per region:

- `loading` flag, `errorMessage`, and a retry that re-runs the same request without losing current state
- independent state: one failing region must not blank the others
- explicit empty state

Quality baseline: clear hierarchy (toolbar -> KPI -> main -> actions), consistent spacing and alignment, scannable numbers and statuses, tables readable at narrow widths.

Anti-patterns: one large empty card, scattered ungrouped actions, unreadable columns, raw status text where the project has a status affordance.
