# Output Contract

## Required Response Shape
When generating a module, always return exactly four top-level sections in order.

## 1) Recognized API methods
List all recognized methods for the selected module.

For each method include:

- method name in `Api.ts`
- classified purpose (`list`, `detail`, `create`, `update`, `delete`, `action`)
- key params (query/body/path id)
- response structure judgment (`res.data.<itemsKey>`, total key, detail key)

Also include missing CRUD items explicitly.

## 2) Files to add or modify
List full file paths that will be created or changed.

At minimum include:

- `src/views/<module>/index.vue` (or `src/views/<module>/dashboard.vue` in dashboard-first mode)
- `src/views/<module>/edit.vue` when create/update flow exists
- optional `src/views/<module>/detail.vue`
- `src/router/modules/<module>.ts`

If any existing file must change, mark it as modified.

## 3) Complete content of every file
Provide complete file content for each listed file.

Rules:

- do not provide partial snippets for generated files
- include imports and full template/script/style blocks for Vue files
- keep code directly copy-pastable and runnable

## 4) Route registration changes
Report route registration result.

- if only adding module route file and auto-import handles registration, state that clearly
- if manual registration is needed in another project shape, include full before/after diff or full updated file content

## Formatting Rules
Use this section heading order exactly:

1. `Recognized APIs`
2. `Files`
3. `File Contents`
4. `Route Registration`

Use concise explanations; keep decision logs focused on implementation-relevant facts.

## Quality Gates Before Responding
Verify all of the following:

1. pagination mapping is 0-based internal and 1-based UI
2. edit/detail uses `route.params.id ?? route.query.id` and auto-fetch
3. list includes required Element Plus controls and feedback
4. delete/action confirms use `ElMessageBox.confirm`
5. output includes missing endpoint degradations when applicable
6. route module contains root `redirect` to `/index` child and hidden edit/detail routes use `showLink: false` (with `activePath` when applicable)
7. when dashboard is requested, output includes dashboard skeleton blocks (filter, metrics, main content) and per-block retry behavior
8. request abstraction choice is explicit: `useRequest` is optional (never mandatory), only considered when dependency exists and complexity justifies it
