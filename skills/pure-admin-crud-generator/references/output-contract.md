# Output Contract

## Output Format Selection

Choose output format based on task complexity:

- **Condensed Output**: Simple CRUD with clear API patterns
- **Full Output**: Dashboard pages, custom actions, complex workflows

## Condensed Output (Simple Tasks)

For straightforward CRUD with clear patterns, use exactly **four** sections:

### 1) Recognized APIs
Brief list of matched endpoints.

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

### 2) Files
List full file paths.

**Example:**
```
src/views/voice-generate-text/index.vue
src/views/voice-generate-text/edit.vue
src/views/voice-generate-text/detail.vue
src/router/modules/voice-generate-text.ts
```

### 3) File Contents
Provide **complete** file contents - no partial snippets.

### 4) Route Registration
Brief route module.

**Example:**
```
Auto-discovered via import.meta.glob("./modules/**/*.ts")
```

---

## Full Output (Complex Tasks)

For dashboards or complex pages, use all sections below:

### 1) Scaffold Fit Decision

| Module | Page Mode | Route Base | Detail Page | Notes |
| --- | --- | --- | --- | --- |
| voice-generate-text | crud | /voice-generate-text | auto | follows scaffold |

### 2) Recognized APIs
Full endpoint list with classification.

**Format:**
```
- `<methodName>`: `<classification>` | `<HTTP method>` `<path>` | `<key params>`
  - Request: query/body params
  - Response: res.data keys
```

### 3) API Capability Matrix

| Operation | Method | Path | Available | Notes |
| --- | --- | --- | --- | --- |
| List | GET | /api/xxx/list | yes | pagination |
| Detail | GET | /api/xxx/detail/{id} | yes | - |
| Create | POST | /api/xxx/create | yes | - |
| Update | POST | /api/xxx/update | yes | - |
| Delete | POST | /api/xxx/delete | no | missing |

### 4) Files
Full file paths.

### 5) File Contents
Complete file contents.

### 6) Route Registration
Full route module with meta.

### 7) Validation Notes
- Assumptions made
- Potential risks
- Open questions

### 8) Blocking Issues
Only if any required check fails:
- Issue: `<rule that failed>`
- Why blocked: `<why output is non-deliverable>`
- Correction: `<revised proposal>`

---

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
- [ ] Page name: Vue component `name` matches route `name` for keepAlive
