# Output Contract

## Required Response Shape
When generating a module, always return exactly four top-level sections in this order.

1. `Recognized APIs`
2. `Files`
3. `File Contents`
4. `Route Registration`

Do not add extra top-level sections.

## 1) Recognized APIs
List all recognized methods for the selected module.

For each method include:

- method name in `Api.ts`
- classified purpose (`list`, `detail`, `create`, `update`, `delete`, `action`)
- key params (query/body/path id)
- response structure judgment (`res.data.<itemsKey>`, total key, detail key)

Also list missing CRUD capabilities explicitly.

## 2) Files
List full file paths that will be created or modified.

Minimum set:

- `src/views/<module>/index.vue` (or `src/views/<module>/dashboard.vue` when dashboard-first)
- `src/views/<module>/edit.vue` when create/update flow exists
- optional `src/views/<module>/detail.vue`
- `src/router/modules/<module>.ts`

If existing files are changed, mark them as modified.

## 3) File Contents
Provide full content for every listed file.

Rules:

- no partial snippets for generated files
- include complete imports and full Vue blocks (`template/script/style` where used)
- keep output directly runnable

## 4) Route Registration
Report route registration result:

- if auto-import discovers the module route file, state it clearly
- if manual registration is needed in another project shape, include full before/after diff or full updated file content

## Formatting Rules
Keep explanations concise and implementation-focused.

## Quality Gates Before Responding
Verify all checks:

1. pagination mapping is 0-based internally and 1-based in UI
2. edit/detail uses `route.params.id ?? route.query.id` with auto-fetch
3. list page includes required Element Plus controls and feedback
4. delete/action confirms use `ElMessageBox.confirm`
5. output includes missing endpoint degradations when applicable
6. route module has root redirect to `/index`; hidden edit/detail routes use `showLink: false` and `activePath` when applicable
7. dashboard outputs include filter + metrics + main content blocks and per-block retry behavior
8. VueUse usage is optional and explicit (never mandatory)
9. list filters map to real API query fields (no fabricated backend filters)
10. server-paged lists preserve server total semantics
11. invalid route id handling is explicit (error + safe navigation)
12. detail page includes explicit empty state when payload is empty
13. response documents concrete UI polish decisions (at least three)
14. templates are runtime-safe for uncertain API field shapes (`Array.isArray` or equivalent guards)
