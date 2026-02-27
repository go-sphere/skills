# Dashboard Best Practices

## 1. Dashboard Skeleton Contract
Use this layout contract for admin dashboards.

### 1.1 Filter row
Use `el-form` with `inline` to provide global filters.

Typical controls:

- keyword: `el-input`
- status/type: `el-select`
- time range: `el-date-picker` (`daterange`)

Actions:

- query
- reset
- refresh
- export (if API exists)

### 1.2 Metrics row
Use `el-row` + `el-col` + `el-card` for KPI cards.

Each card should include:

- title
- primary metric value
- secondary info (trend/range/update time)

### 1.3 Main content row
Use `el-card` blocks for charts and tables.

- each block must have its own loading/error/retry state
- empty data should use `el-empty`

### 1.4 Actions row
Place secondary operations such as refresh/export/batch ops.

## 2. Visual Quality Baseline (Mandatory)
Use these visual rules to avoid "plain form + bare table" output.

### 2.1 Page hierarchy

- split page into clear blocks: toolbar, KPI/summary, primary data block, secondary blocks
- avoid placing all controls and table directly in one undifferentiated card
- every block should have a clear title and optional subtitle

### 2.2 Spacing and density

- card-to-card vertical spacing: `16px`
- card internal spacing: `16px` (compact mode can be `12px`)
- toolbar controls use `el-space` to keep stable spacing
- avoid oversized empty white areas and single-line content inside large cards

### 2.3 Table readability

- use `border` + `stripe` for management tables by default
- set meaningful `min-width` and avoid narrow squeezed columns
- align numeric columns to the right; IDs and short enums centered/left as appropriate
- use `show-overflow-tooltip` for long text columns
- operation buttons should be grouped and visually prioritized (primary action first, danger action last)

### 2.4 Status semantics

- represent status/type with `el-tag` instead of plain text where possible
- use semantic colors consistently: success/info/warning/danger
- do not use custom hardcoded colors that conflict with existing theme

### 2.5 State visuals

- loading: use `v-loading` and skeleton for first screen
- empty: use `el-empty` with concise guidance text
- error: use `el-alert` with retry action in place (not only toast)

### 2.6 Responsive behavior

- desktop first, then degrade on smaller screens
- toolbar should wrap gracefully; avoid control overlap
- KPI cards should collapse from multi-column to single-column on narrow viewports

### 2.7 Theme compatibility

- follow pure-admin-thin/Element Plus theme tokens and component defaults
- avoid custom global style overrides
- avoid fixed background/text color pairs that break dark mode or theme switching

## 3. Unified Error and Retry Contract
Apply the same recovery model for every async data region.

State shape per region:

- `loading: boolean`
- `errorMessage: string`
- `data: ...`

Behavior:

1. before request: clear `errorMessage`, set `loading=true`
2. on success: set data, `loading=false`
3. on failure: set `errorMessage`, `loading=false`, keep previous filters and paging
4. retry action: rerun the same request function with current state

UI elements:

- loading: `v-loading` or `el-skeleton`
- error display: `el-alert`
- retry trigger: `el-button`
- global toast: `ElMessage.error` for immediate feedback

## 4. VueUse Integration Rule
If `@vueuse/core` is available in project dependencies, AI may use VueUse composables (for example `useAsyncState`, `useDebounceFn`, `useIntervalFn`) to organize request orchestration.

Recommended usage:

- list fetch: trigger unified request executor from query/pagination events
- detail fetch: guard by valid id to avoid empty-id requests
- action requests: run mutation then refresh list in success branch
- dashboard auto-refresh (only when needed): use interval composables and pause when hidden

Fallback:

- if dependency is not installed, keep classic `ref/reactive` request flow
- do not add new dependency automatically

Decision rule:

- do not force VueUse on every dashboard
- use it when it clearly simplifies multi-source loading/error/retry orchestration

## 5. Non-negotiable Compatibility Rules
Even with dashboard mode and VueUse composables:

- keep 0-based backend page index and 1-based UI page
- keep `route.params.id ?? route.query.id` id extraction
- keep `ElMessageBox.confirm` for delete and risky actions
- keep generated output structure contract from `output-contract.md`
- keep visual quality baseline in this file

## 6. Visual Anti-patterns (Do Not Generate)

- one huge blank card with only one button or one sentence
- action area scattered across random positions with no grouping
- table columns without width strategy causing unreadable truncation
- filter controls and actions mixed into an unstructured block
- plain status text when tag/badge can improve scanning
