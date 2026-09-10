---
name: frontend-crud-generator
description: Generate frontend CRUD, list, edit, detail, and dashboard pages plus frontend route registration from the TypeScript swagger client that go-sphere generates, or the project's wrapper around it (protoc-gen-sphere, swag, and swagger-typescript-api, usually into src/api/swagger/Api.ts). Use when scaffolding or updating admin panel screens, management modules, route modules, menu entries, or permission-gated actions in whatever frontend framework the project already uses, including Vue 3 + Element Plus/pure-admin-thin and React SPAs with react-router, and when the user asks in Chinese, for example 生成后台管理页面, 生成 CRUD 页面, 生成路由模块, 加管理页, 列表页, 菜单项, 权限控制, 根据 swagger 写界面. It detects the framework and mirrors an existing page, so unknown or custom frontend setups also work. Do not use to design or change the API contract itself — that is `proto-api-generator` — or to regenerate or debug the generated client — that is `sphere-feature-workflow`.
---

# Frontend CRUD Generator

## Overview

Generate the frontend half of a go-sphere feature: pages and route registration derived from the TypeScript swagger client that `protoc-gen-sphere`, `swag`, and `swagger-typescript-api` produce.

The workflow is framework-neutral. Concrete stack rules live in `references/frameworks/` packs (Vue 3 + Element Plus / pure-admin-thin, React SPA), and everything else goes through the convention-discovery fallback.

This is an AI-first generator: no external OpenAPI generators, no helper codegen scripts, no new runtime dependencies, no reusable business component library.

## When to Use

**ALWAYS use this skill** when the user wants admin, management, or dashboard pages built from an existing generated client, in any frontend framework:

- CRUD pages (list, edit/create, optional detail)
- dashboard-first pages
- route modules, menu entries, or route-table registration
- action buttons backed by non-CRUD endpoints (retry/enable/disable/export)
- permission-gated pages and controls

**Trigger examples:**

- "Generate admin pages for user management"
- "Create CRUD for voice-features module"
- "Add a system page in the React admin"
- "Scaffold product list/detail in the dashboard"
- "生成后台管理页面" / "生成 CRUD 页面和路由"

Do not use this skill to define or change the API contract, the backend, or the database — route those to `proto-api-generator` and `sphere-feature-workflow`.

## Hard Gates

These are non-optional. If a gate fails, stop and report blocking issues.

1. Generate only from the project's existing generated swagger client and its real consumption layer. Never re-run code generation here, and never hand-edit generated files (`Api.ts` and other generated artifacts).
2. Complete the Convention Discovery sweep and report the Convention Report before generating. Project conventions outrank pack defaults; pack defaults outrank generic heuristics.
3. Use exactly one framework pack per generation. Never mix idioms from two stacks.
4. Do not add runtime dependencies, and do not create a reusable business component library. Reuse the project's existing UI primitives and shared helpers.
5. Never invent permission keys, roles, or endpoints. Use only identifiers that exist in the project.
6. Route names must be unique. When the framework caches pages by component name (keepAlive), the component name must match the route name.
7. Pagination base and query keys must match the project's observed convention. Filters must correspond to real query parameters, and the server total must never be replaced by the current page length.
8. Missing endpoints degrade the UI explicitly: unsupported actions are removed or disabled, and the gap is reported. A capability the user asked for that no endpoint or field supports (a filter with no query parameter, an edit with no update endpoint) is reported as a contract gap, never approximated with fabricated parameters or client-side tricks.

<HARD-GATE>
Do NOT write any page, route, or registration file until all of the following are confirmed:

- The target module is known and specific (not just "management"). If vague, ask one clarifying question.
- The module's existing surface has been checked: any page, route module, menu entry, or wrapper method that already exists is planned as an update, not duplicated.
- The Convention Report is complete: detected framework and chosen pack (or fallback plan), generated client path, API consumption convention, route registration mechanism, page layout, pagination base, the route id / params mechanism, and the representative pages read.
- The page mode intent is known: `crud`, `dashboard`, or `mixed`.
- The generated client exists. If it does not, stop and offer the two paths in [references/conventions-discovery.md](references/conventions-discovery.md) (Step E) instead of inventing endpoints.

A matched pack does not require a user question; an unknown framework or a `Low` confidence on API consumption, route registration, or page layout does.
</HARD-GATE>

## Framework Detection and Convention Discovery

Discovery is mandatory and read-only. Read [references/conventions-discovery.md](references/conventions-discovery.md) and run its sweep:

1. Rule and ownership files (`AGENTS.md`, `CLAUDE.md`, frontend rule files, `.sphere/layout.json`) — they outrank everything here.
2. Manifest and build: dependencies, aliases, and the project's actual typecheck/build command.
3. Generated client location and export shape.
4. Transport and unwrap convention: what a page receives from a call, and what error type it catches.
5. Route registration: where routes are declared and exactly which files a new page touches.
6. One to two representative pages of the same mode; read them fully.
7. Permissions, formatters, enum-label sources, UI text language, layering bans.

Then pick the pack:

| Detected stack | Pack |
|---|---|
| Vue 3 + Element Plus / pure-admin-thin | [references/frameworks/vue-pure-admin.md](references/frameworks/vue-pure-admin.md) |
| React + react-router + Tailwind primitives | [references/frameworks/react-spa.md](references/frameworks/react-spa.md) |
| anything else | the fallback protocol in `conventions-discovery.md` |

Report the result as the Convention Report table before generating. Concrete markup rules live in the packs; this file and the core references stay neutral.

## Input Contract

- `moduleSelector` (required): module tag/entity/path keyword (e.g. "user", "voice-features", "order").
- `selectorMode` (optional, default `auto`): `auto | tag | entity | path`.
- `forceDetailPage` (optional, default `auto`): `auto | true | false`. When `auto`, include detail only if the detail endpoint exists and the observed project pattern includes one.
- `pageMode` (optional, default `crud`): `crud | dashboard | mixed`.
- `routeBase` (optional, default from discovery): route path root; falls back to `/<kebab-module>`.
- `framework` (optional, default `auto`): `auto | vue-pure-admin | react-spa | generic`.
- `routeRegistration` (optional, default `auto`): explicit file or registry path when the user already knows where the route belongs.
- `permissionIntegration` (optional, default `auto`): `auto | on | off`.
- `outputMode` (optional, default `write`): `write` edits project files; `content` prints complete file contents and writes nothing.

Examples:

- "Generate pages for user management" → `moduleSelector="user"`, infer module from client tags.
- "Create dashboard for voice-generate-text" → `moduleSelector="voice-generate-text"`, `pageMode="dashboard"`.
- "先给我看，不要写文件" → `outputMode="content"`.

If the user provides only a vague module name, resolve with `selectorMode=auto` and explicitly state the matched methods.

## Progressive Reference Loading

### Phase 1: Always Read First

1. [references/conventions-discovery.md](references/conventions-discovery.md) — discovery sweep, Convention Report, fallback protocol
2. [references/client-parsing.md](references/client-parsing.md) — module resolution, endpoint classification, type inference, consumption detection
3. [references/output-contract.md](references/output-contract.md) — write rules and report format

### Phase 2: The Matching Pack

Exactly one of:

- [references/frameworks/vue-pure-admin.md](references/frameworks/vue-pure-admin.md)
- [references/frameworks/react-spa.md](references/frameworks/react-spa.md)

For an unknown framework, skip to the fallback protocol in `conventions-discovery.md`.

### Phase 3: By Page Mode

- [references/page-blueprint.md](references/page-blueprint.md) — the framework-neutral behavior contract for every page mode
- [references/access-control.md](references/access-control.md) — when permissions exist in the project

### Phase 4: Final Gate

Run the Completion Checklist below plus the pack's `## Verification` section. When no pack matched, run the project's discovered typecheck/lint/build command instead and state which command was used.

## Workflow

### Quick Path (Simple CRUD)

1. Run discovery, including the existing-surface check; emit the Convention Report.
2. Parse the client and classify list/detail/create/update/delete/action methods.
3. Plan the file set for `pageMode` and state it with the target paths.
4. Generate pages following the pack (or fallback) and `page-blueprint.md`.
5. Register routes through the discovered mechanism; edit shared files only with anchored patches.
6. Report using the condensed format.

### Full Path (Complex / Dashboard / Custom Actions)

1. Run discovery, including the existing-surface check; emit the Convention Report.
2. Full classification plus response-shape analysis; build the capability matrix.
3. Plan the file set and every registration touchpoint (route table, menu, guards, permission maps) before writing; mark files that already exist as updates.
4. Generate pages with per-region loading/error/retry where the blueprint requires it.
5. Generate action buttons only for exposed endpoints, with confirmation for risky ones.
6. Register, verify, and report using the full format.

### Unknown Framework Path

Follow the fallback protocol in `conventions-discovery.md`: report first, generate only from discovered primitives, and stop for confirmation when there is no analogous page to mirror.

## Degrade Gracefully

- Generate only valid pages and operations based on available endpoints; remove unsupported actions and report the missing CRUD operations explicitly.
- Keep generated code runnable when operations are unavailable.
- When the generated client exists but the project talks to the backend through another transport, follow the project transport, import types from the client, and report the divergence in Validation Notes.
- When the framework is unknown, use the neutral fallback rather than approximating a pack.
- When there is no analogous page to mirror, stop and ask before bootstrapping (Step D of the fallback protocol).
- When a page needs a mechanism the project has no precedent for (routed id, form prefill source, confirmation primitive), degrade to the closest supported flow or stop and ask; never invent a convention and present it as observed.

## Dependency Policy

Use only libraries already in the project's manifest. Prefer the project's shared helpers over new ones. VueUse is a Vue-only optional policy, described in the Vue pack; never add it (or anything else) for generated pages.

## Completion Checklist

Before reporting, verify ALL of the following:

1. **Report format**: section order matches the output contract (condensed or full), and the Convention Report is present with real sources read.
2. **Single pack**: only one framework pack's idioms appear in the output.
3. **Type safety**: the project's own typecheck/build command was run, or its absence is stated in Validation Notes.
4. **Pagination**: internal base and query keys match the observed project convention; filter changes reset to the first page.
5. **Route id handling**: invalid id shows an error and never silently falls back to create mode.
6. **Filters**: only filters that match real API query parameters; no fabricated fields.
7. **Server total**: taken from the response, never from the current page length.
8. **Destructive actions**: confirmed with the project's confirmation primitive before the request.
9. **Mutations**: refresh the affected list/region after success.
10. **Runtime safety**: uncertain API fields are guarded (`Array.isArray` or normalizers); no crash-prone template/JSX expressions.
11. **Missing endpoints and contract gaps**: unsupported operations, and requested capabilities with no backing endpoint or field, are reported explicitly with the UI degraded rather than broken.
12. **Route registration**: complete for the project's mechanism; route names unique where the framework uses them.
13. **Page caching identity**: where the framework caches by component name, component name matches route name.
14. **No new dependencies; generated files untouched; permission keys only if they exist in the project.**
15. **Existing surface**: each target path was checked first; existing pages, routes, menus, and wrappers are updated in place, never duplicated or overwritten.

## Related Skills

- Upstream — `proto-api-generator` defines the HTTP contract, and `sphere-feature-workflow` runs the generation commands (`make gen/docs`, `make gen/dts`) that produce the TypeScript swagger client; generation cannot start before that client exists in the project.
- Downstream — none; generated pages, route registration, and permission wiring are the deliverable. When the UI needs a field or endpoint the client does not expose, hand back to `proto-api-generator` instead of faking it.
- Boundary — use `proto-api-generator` for contract changes and `sphere-feature-workflow` for backend, schema, or scaffold work; this skill owns only frontend pages and route registration, in whatever framework the project already uses. `prd` and `ux-analyst` own page intent when they exist.
- Companion — none bundled; the framework packs under `references/frameworks/` carry stack conventions, and `vueuse-functions` may be used for composable selection when the project already depends on VueUse.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
