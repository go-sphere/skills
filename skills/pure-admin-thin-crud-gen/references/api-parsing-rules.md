# API Parsing Rules

## Purpose
Map swagger-ts-api methods in `src/api/swagger/Api.ts` to module CRUD capabilities for pure-admin-thin.

## 1. Module Resolution
Resolve module name with this priority:

1. explicit user selection by tag/entity/path
2. service tag suffix in `@tags` (preferred)
3. first stable path segment after `/api/`

### 1.1 Tag to module
Prefer tags shaped like `dash.v1.<ServiceName>`.

Examples:

- `dash.v1.AdminService` -> `admin`
- `dash.v1.UserService` -> `user`
- `dash.v1.VoiceGenerateTextService` -> `voice-generate-text`

Conversion rule:

- remove `Service` suffix
- convert PascalCase to kebab-case

### 1.2 Path fallback
If service tag is missing or generic, fallback to path.

Examples:

- `/api/voice-features/list` -> `voice-features`
- `/api/voice-generate/list` -> `voice-generate`

## 2. Endpoint Classification
Classify methods by request metadata and method name.

## 2.1 List
Match when any condition is true:

- request path ends with `/list`
- method name contains `List`
- GET with query containing pagination-like keys (`page`, `page_size`, `size`, `limit`)

## 2.2 Detail
Match when any condition is true:

- request path contains `/detail/{id}`
- GET path has `/{id}` and is not list
- method name contains `Detail`

## 2.3 Create
Match when any condition is true:

- path ends with `/create`
- POST or PUT method name contains `Create`
- request body type maps to create payload semantics

## 2.4 Update
Match when any condition is true:

- path ends with `/update`
- path has `/{id}` with PUT/PATCH semantics
- method name contains `Update`

Note: in this repository many updates are POST `/update`.

## 2.5 Delete
Match when any condition is true:

- HTTP DELETE
- path contains `/delete/{id}` or `/delete`
- method name contains `Delete`

## 2.6 Action
Everything not selected by CRUD and still module-related is action.

Common action indicators:

- path or name includes `retry`, `enable`, `disable`, `reset`, `export`, `vip`, `approve`, `audit`

## 3. Type Inference
Use local type aliases and interfaces:

- `type XxxData = GinxDataResponseYyy`
- `interface GinxDataResponseYyy { data?: Zzz }`
- `interface Zzz` may include list keys and totals

Infer in this order:

1. parse method return alias `XxxData`
2. resolve `GinxDataResponse*` wrapper
3. inspect nested `data` interface for list keys and totals
4. inspect entity interface for form fields

## 4. Pagination Inference
Internal page state must be 0-based.

Interpret query keys:

- page-like: `page`, `pageIndex`, `pageNo`, `current`
- size-like: `size`, `pageSize`, `page_size`, `limit`

If multiple keys exist, use repository-observed keys first (`page`, `page_size`).

UI mapping rule:

- UI page = `pageIndex + 1`
- backend page = `uiPage - 1`

## 5. List Payload Inference
Preferred list keys under `res.data`:

1. `records`
2. `list`
3. `items`
4. module-named arrays (`users`, `admins`, `voice_generate_text`, etc.)

Preferred total keys under `res.data`:

1. `total`
2. `total_size`
3. `count`
4. `total_page` (only as fallback)
5. fallback `array.length`

If only `total_page` exists, derive total carefully:

- prefer `total = total_page * pageSize` when semantics are clearly total pages
- otherwise keep backend paging UI usable with conservative fallback and explain assumption in output section 1

## 6. Current-Repo Priority Rules
Use these repository-specific interpretations first:

- list endpoints often use GET `/api/<module>/list`
- detail endpoints may use GET `/api/<module>/detail/{id}`
- update may be POST `/api/<module>/update`
- responses are already unwrapped once by `API` (`src/api/api.ts`)

## 7. Useful Extraction Commands
Use shell inspection commands when needed.

```bash
rg -n "@tags|@name|@request" src/api/swagger/Api.ts
```

```bash
awk '/@name /{name=$3} /@request /{req=$3; print name"\t"req}' src/api/swagger/Api.ts
```

```bash
rg -n "export type .*Data =|interface GinxDataResponse|interface Dashv1" src/api/swagger/Api.ts
```
