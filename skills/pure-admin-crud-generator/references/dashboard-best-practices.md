# Dashboard Best Practices

## Table of Contents
- [Scope](#scope)
- [1. Dashboard Skeleton Contract](#1-dashboard-skeleton-contract)
- [2. Visual Quality Baseline (Mandatory)](#2-visual-quality-baseline-mandatory)
- [3. Unified Error and Retry Contract](#3-unified-error-and-retry-contract)
- [4. VueUse Integration Rule](#4-vueuse-integration-rule)
- [5. Non-negotiable Compatibility Rules](#5-non-negotiable-compatibility-rules)
- [6. Visual Anti-patterns (Do Not Generate)](#6-visual-anti-patterns-do-not-generate)
- [7. Final Dashboard Self-check](#7-final-dashboard-self-check)

## Scope
Apply this reference only when the request is dashboard-first (`pageMode=dashboard` or explicit dashboard requirement).

## 1. Dashboard Skeleton Contract
Use this block layout for admin dashboards.

### 1.1 Filter row
Use `el-form` with `inline`.

Typical controls:

- keyword: `el-input`
- status/type: `el-select`
- time range: `el-date-picker` (`daterange`)

Typical actions:

- query
- reset
- refresh
- export (if API exists)

### 1.2 Metrics row
Use `el-row` + `el-col` + `el-card` for KPI cards.

Each card should include:

- title
- primary metric
- secondary info (trend/range/update time)

### 1.3 Main content row
Use separate `el-card` blocks for charts and tables.

- each block keeps independent loading/error/retry state
- empty blocks show `el-empty`

### 1.4 Actions row
Place secondary operations (refresh/export/batch) in one predictable region.

## 2. Visual Quality Baseline (Mandatory)
Avoid flat or template-like outputs. Keep clear hierarchy and scanning quality.

### 2.1 Page hierarchy
- split into toolbar, KPI summary, primary data region, secondary regions
- do not place all controls and table inside one undifferentiated card
- each block should have a title (subtitle when helpful)

### 2.2 Spacing and density
- vertical spacing between cards: `16px`
- card internal spacing: `16px` (`12px` in compact contexts)
- toolbar controls should use `el-space` or equivalent wrapping layout
- avoid oversized blank areas

### 2.3 Table readability
- default to `border` + `stripe`
- set practical `min-width` values
- align numeric columns to the right
- use `show-overflow-tooltip` for long text
- group operation buttons with clear priority

### 2.4 Status semantics
- prefer `el-tag` for status/type values
- use semantic colors consistently: success/info/warning/danger
- avoid custom hardcoded colors that fight theme tokens

### 2.5 State visuals
- loading: `v-loading` or skeleton for first render
- empty: `el-empty` with concise guidance text
- error: inline `el-alert` with retry action (not toast-only)

### 2.6 Responsive behavior
- desktop-first structure with graceful small-screen wrap
- toolbar controls should wrap without overlap
- KPI grid should collapse to fewer columns on narrower viewports

### 2.7 Theme compatibility
- follow pure-admin-thin/Element Plus tokens and defaults
- avoid global style overrides for generated pages
- avoid fixed background/text color pairs that break theme switching

## 3. Unified Error and Retry Contract
Each async region should expose:

- `loading: boolean`
- `errorMessage: string`
- region data payload

Behavior sequence:

1. before request: clear `errorMessage`, set `loading=true`
2. on success: set data, set `loading=false`
3. on failure: set `errorMessage`, set `loading=false`, keep current query/paging state
4. retry: rerun the same request function with current state

UI elements:

- loading: `v-loading` or `el-skeleton`
- error surface: `el-alert`
- retry action: `el-button`
- optional immediate toast: `ElMessage.error`

## 4. VueUse Integration Rule
VueUse is optional.

If `@vueuse/core` exists, composables may be used to simplify orchestration:

- list fetch orchestration with query/pagination triggers
- guarded detail fetch by valid id
- refresh-after-mutation for actions
- optional dashboard auto-refresh that pauses when hidden

Fallback:

- if dependency is missing, keep classic `ref/reactive` state flow
- do not add new dependencies automatically

Decision rule:

- do not force VueUse on every dashboard
- use only when it reduces complexity meaningfully

## 5. Non-negotiable Compatibility Rules
Even in dashboard mode:

- keep backend 0-based page index and UI 1-based page display
- keep id extraction `route.params.id ?? route.query.id`
- keep `ElMessageBox.confirm` for risky/destructive actions
- keep output format aligned with `output-contract.md`
- keep runtime-safe rendering for uncertain API field shapes

## 6. Visual Anti-patterns (Do Not Generate)
- one oversized blank card with almost no content
- scattered actions without grouping
- unreadable table columns due to missing width strategy
- unstructured mixing of filter controls and action buttons
- plain status text where tags or badges are more scannable

## 7. Final Dashboard Self-check
Before returning generated dashboard code, verify:

1. layout has clear hierarchy (toolbar/metrics/main/action)
2. each async block has independent loading/error/retry state
3. table readability rules are applied
4. responsive wrap behavior is present
5. generated dashboard remains compatible with project theme and route/page conventions
