# API Parsing Rules

## Table of Contents
- [Scope](#scope)
- [Parsing Output](#parsing-output)
- [1. Module Resolution](#1-module-resolution)
- [2. Endpoint Classification](#2-endpoint-classification)
- [3. Type Inference](#3-type-inference)
- [4. Pagination and List Payload Inference](#4-pagination-and-list-payload-inference)
- [5. Conflict Resolution](#5-conflict-resolution)
- [6. Current-Repo Priority Rules](#6-current-repo-priority-rules)
- [7. Useful Extraction Commands](#7-useful-extraction-commands)

## Scope
Map swagger-ts-api methods in `src/api/swagger/Api.ts` to module CRUD capabilities for pure-admin-thin generation.

## Parsing Output
The parser should produce a structured decision set for one target module:

- selected module key (`kebab-case`)
- recognized methods and classifications (`list | detail | create | update | delete | action`)
- key request params (query/body/path id)
- response interpretation (`itemsKey`, `totalKey`, detail payload key)
- explicit missing CRUD capabilities

## 1. Module Resolution
Resolve module name with this priority:

1. explicit user selection (`selectorMode=tag|entity|path`)
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
Classify methods by request metadata and method naming.

### 2.1 List
Match when any condition is true:

- request path ends with `/list`
- method name contains `List`
- GET with query keys including pagination-like fields (`page`, `page_size`, `size`, `limit`)

### 2.2 Detail
Match when any condition is true:

- request path contains `/detail/{id}`
- GET path has `/{id}` and is not a list endpoint
- method name contains `Detail`

### 2.3 Create
Match when any condition is true:

- path ends with `/create`
- POST or PUT method name contains `Create`
- request body shape indicates create semantics

### 2.4 Update
Match when any condition is true:

- path ends with `/update`
- path has `/{id}` with PUT/PATCH semantics
- method name contains `Update`

Note: in this repository, many update operations are POST `/update`.

### 2.5 Delete
Match when any condition is true:

- HTTP DELETE
- path contains `/delete/{id}` or `/delete`
- method name contains `Delete`

### 2.6 Action
Everything module-related that is not classified as CRUD is `action`.

Common action indicators:

- path or name includes `retry`, `enable`, `disable`, `reset`, `export`, `vip`, `approve`, `audit`

## 3. Type Inference
Use local type aliases and interfaces:

- `type XxxData = GinxDataResponseYyy`
- `interface GinxDataResponseYyy { data?: Zzz }`
- `interface Zzz` may include list keys, totals, and detail data

Inference order:

1. parse method return alias `XxxData`
2. resolve `GinxDataResponse*` wrapper
3. inspect nested `data` interface for list keys and total keys
4. inspect entity/detail interfaces for form fields

## 4. Pagination and List Payload Inference
Internal page state must be 0-based.

### 4.1 Query keys
Interpret query keys:

- page-like: `page`, `pageIndex`, `pageNo`, `current`
- size-like: `size`, `pageSize`, `page_size`, `limit`

If multiple keys exist, prefer repository-observed defaults (`page`, `page_size`).

### 4.2 UI paging mapping
Use this mapping:

- UI page = `pageIndex + 1`
- backend page = `uiPage - 1`

### 4.3 List item key priority
Preferred list keys under `res.data`:

1. `records`
2. `list`
3. `items`
4. module-shaped arrays (`users`, `admins`, `voice_generate_text`, etc.)

### 4.4 Total key priority
Preferred total keys under `res.data`:

1. `total`
2. `total_size`
3. `count`
4. `total_page` (fallback only)
5. fallback `array.length` (last resort)

If only `total_page` exists:

- use `total = total_page * pageSize` only when semantics are clearly total pages
- otherwise use conservative fallback and report assumption in recognized API notes

## 5. Conflict Resolution
When multiple interpretations are possible, resolve with this order:

1. explicit user selector and user intent
2. stronger request-path semantics
3. method name semantics
4. repository-specific conventions
5. conservative fallback with explicit assumption

Never hide ambiguity. Record assumptions in output section 1.

## 6. Current-Repo Priority Rules
Use these repository-specific interpretations first:

- list endpoints are commonly GET `/api/<module>/list`
- detail endpoints may be GET `/api/<module>/detail/{id}`
- update may be POST `/api/<module>/update`
- `API` already unwraps axios response once (`src/api/api.ts`)

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
