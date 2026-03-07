# Dashboard Best Practices

## Table of Contents
- [Quick Reference](#quick-reference)
- [Scope](#scope)
- [1. Dashboard Skeleton Contract](#1-dashboard-skeleton-contract)
- [2. Visual Quality Baseline](#2-visual-quality-baseline)
- [3. Error and Retry Contract](#3-error-and-retry-contract)
- [4. Non-negotiable Rules](#4-non-negotiable-rules)
- [5. Anti-patterns](#5-anti-patterns)
- [6. Self-check](#6-self-check)

## Quick Reference
Dashboard layout structure:
```
┌─────────────────────────────────────┐
│ Filter Row (el-form inline)         │
├─────────────────────────────────────┤
│ Metrics Row (el-row + el-card)      │
├─────────────────────────────────────┤
│ Main Content (charts/tables)         │
├─────────────────────────────────────┤
│ Actions Row (refresh/export)        │
└─────────────────────────────────────┘
```

## Scope
Apply this reference only when the request is dashboard-first (`pageMode=dashboard` or explicit dashboard requirement).

## 1. Dashboard Skeleton Contract
Use this block layout for admin dashboards.

### 1.1 Filter row
- `el-form` with `inline`
- Controls: `el-input` (keyword), `el-select` (status), `el-date-picker` (time range)
- Actions: query, reset, refresh, export

### 1.2 Metrics row
- `el-row` + `el-col` + `el-card` for KPI cards
- Each card: title + primary metric + secondary info

### 1.3 Main content row
- Separate `el-card` blocks for charts/tables
- Each block: independent loading/error/retry state
- Empty: `el-empty`

### 1.4 Actions row
- Place secondary operations (refresh/export/batch) in predictable region

## 2. Visual Quality Baseline
- Clear hierarchy: toolbar → KPI → main → actions
- Spacing: 16px between cards, 16px internal padding
- Table: `border` + `stripe`, `min-width`, right-align numbers, `show-overflow-tooltip`
- Status: use `el-tag` with semantic colors
- State: `v-loading`, `el-empty`, `el-alert` with retry

## 3. Error and Retry Contract
Each region needs:
- `loading: boolean`
- `errorMessage: string`
- Retry calls same function, keeps current state

## 4. Non-negotiable Rules
- 0-based backend → 1-based UI pagination
- `route.params.id ?? route.query.id` with validation
- `ElMessageBox.confirm` for destructive actions
- Runtime-safe rendering (`Array.isArray` guards)

## 5. Anti-patterns (Do NOT Generate)
- One oversized blank card with no content
- Scattered actions without grouping
- Unreadable table columns
- Plain status text where tags are better

## 6. Self-check
Before returning:
- [ ] Clear hierarchy (filter/metrics/main/actions)
- [ ] Independent loading/error/retry per region
- [ ] Table readability rules applied
- [ ] Responsive wrap behavior present
