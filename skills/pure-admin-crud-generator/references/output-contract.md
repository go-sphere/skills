# Output Contract

## Required Response Shape
When generating a module, always return exactly **four** top-level sections in this order:

1. **Recognized APIs** - What endpoints were found
2. **Files** - What files will be created
3. **File Contents** - Full file contents
4. **Route Registration** - How routes are registered

## 1) Recognized APIs
List all recognized methods for the selected module.

**Format:**
```
- `<methodName>`: `<classification>` | `<path>` | `<key params>`
  - Response: `res.data.<itemsKey>`, total: `<totalKey>`
```

**Example:**
```
- getVoiceList: list | GET /api/voice-generate-text/list | page, page_size
  - Response: res.data.list, total: res.data.total
- getVoiceDetail: detail | GET /api/voice-generate-text/detail/{id} | id
- createVoice: create | POST /api/voice-generate-text/create | body fields
- updateVoice: update | POST /api/voice-generate-text/update | id, body fields
- deleteVoice: delete | POST /api/voice-generate-text/delete | id

Missing: none
```

## 2) Files
List full file paths.

**Example:**
```
src/views/voice-generate-text/index.vue
src/views/voice-generate-text/edit.vue
src/views/voice-generate-text/detail.vue
src/router/modules/voice-generate-text.ts
```

## 3) File Contents
Provide **complete** file contents - no partial snippets.

## 4) Route Registration
State how routes are registered. For pure-admin-thin with auto-import:
```
Auto-discovered via import.meta.glob("./modules/**/*.ts")
```

## Quality Gates Checklist
Before responding, verify ALL:

- [ ] Pagination: 0-based internal, 1-based UI
- [ ] Route id: `route.params.id ?? route.query.id` with validation
- [ ] Delete: uses `ElMessageBox.confirm`
- [ ] Missing endpoints: explicitly reported
- [ ] Route module: root redirect to `/index`, hidden routes use `showLink: false`
- [ ] Dashboard: filter + metrics + main + actions, per-region retry
- [ ] Filters: only real API query params
- [ ] Runtime safety: `Array.isArray()` guards for uncertain fields
- [ ] Empty state: detail page shows `el-empty` when payload empty
