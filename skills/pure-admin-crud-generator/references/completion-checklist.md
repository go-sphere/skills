# Completion Checklist

## Pre-Output Verification

Run through this checklist before final output:

## 1. Output Format

- [ ] Section order matches output contract (condensed or full)
- [ ] All required sections present
- [ ] File paths are correct

## 2. Type Safety

- [ ] Generated files compile under `pnpm typecheck`
- [ ] No `any` types without justification
- [ ] Props and emits properly typed

## 3. Pagination

- [ ] Internal state is 0-based
- [ ] UI displays 1-based (`pageIndex + 1`)
- [ ] Page change handler updates internal state correctly
- [ ] Filter reset sets `pageIndex = 0`

## 4. Route ID Handling

- [ ] Uses `route.params.id ?? route.query.id`
- [ ] Invalid id shows error message
- [ ] Does NOT silently fallback to create mode

## 5. Filters

- [ ] Only include filters matching real API query parameters
- [ ] Filter form uses correct v-model bindings
- [ ] Reset clears all filters and resets pagination

## 6. Delete Safety

- [ ] All delete buttons use `ElMessageBox.confirm`
- [ ] Confirmation message is clear
- [ ] Destructive actions clearly indicated

## 7. Runtime Safety

- [ ] Uncertain API fields use `Array.isArray()` guards
- [ ] Null/undefined checks for optional fields
- [ ] No crash-prone template expressions

## 8. Missing Endpoints

- [ ] Explicitly report which CRUD operations are unavailable
- [ ] UI buttons disabled/hidden for missing operations
- [ ] Code still runs with partial CRUD

## 9. Route Module

- [ ] Root route redirects to `/index`
- [ ] Hidden routes use `showLink: false`
- [ ] Uses `satisfies RouteConfigsTable`
- [ ] Route names are unique

## 10. Page Name (keepAlive)

- [ ] Vue component has `name` property
- [ ] Route `name` matches component `name`
- [ ] For keepAlive to work properly

## 11. Dashboard Quality (if applicable)

- [ ] Has filter + metrics + main content + actions
- [ ] Per-region loading/error/retry states
- [ ] Clear visual hierarchy

## 12. RBAC Integration (if applicable)

- [ ] Route has appropriate `auths` for buttons
- [ ] Uses `v-auth` directive or `permissionStore`
- [ ] Buttons hidden when user lacks permission

## Final Confirmation

```
[ ] All checks passed - output ready
[ ] Issues found - fix before output
```
