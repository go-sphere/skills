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

## 2. Unified Error and Retry Contract
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

## 3. `useRequest` Integration Rule
If `vue-hooks-plus` is available in project dependencies, AI may use:

```ts
import useRequest from "vue-hooks-plus/es/useRequest";
```

Recommended usage:

- list fetch: `manual: true` with `run`/`refresh`
- detail fetch: use `ready` to avoid empty-id requests
- action requests: `runAsync` + `onSuccess` to refresh list
- dashboard auto-refresh (only when needed): use `pollingInterval`; set `pollingWhenHidden: false`

Fallback:

- if dependency is not installed, keep classic `ref/reactive` request flow
- do not add new dependency automatically

Decision rule:

- do not force `useRequest` on every dashboard
- use it when it clearly simplifies multi-source loading/error/retry orchestration

## 4. Non-negotiable Compatibility Rules
Even with dashboard mode and `useRequest`:

- keep 0-based backend page index and 1-based UI page
- keep `route.params.id ?? route.query.id` id extraction
- keep `ElMessageBox.confirm` for delete and risky actions
- keep generated output structure contract from `output-contract.md`
