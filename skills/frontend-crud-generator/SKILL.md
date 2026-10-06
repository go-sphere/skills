---
name: frontend-crud-generator
description: Generate frontend CRUD, detail, and dashboard pages plus route registration from the project's generated TypeScript swagger client. Use for admin screens, route modules, menu entries, and permission-gated actions in the project's own frontend framework (Vue, React, or custom) — including 生成后台管理页面, 生成 CRUD 页面, 生成路由模块, 列表页, 权限控制. Not for changing the API contract — that is `proto-api-generator`.
---

# Frontend CRUD Generator

Generate the frontend half of a go-sphere feature: pages and route registration derived from the
TypeScript swagger client that `protoc-gen-sphere`, `swag`, and `swagger-typescript-api` produce
(usually `src/api/swagger/Api.ts`).

The workflow is framework-neutral. Concrete stack rules live in the framework packs; everything
else goes through the convention-discovery fallback. This is an AI-first generator: no external
OpenAPI generators, no helper codegen scripts, no new runtime dependencies, and no reusable
business component library.

Covers CRUD pages, dashboard-first pages, route modules and menu entries, action buttons backed by
non-CRUD endpoints (retry, enable, disable, export), and permission-gated controls.

## Inputs

| Parameter | Default | Values |
|-----------|---------|--------|
| `moduleSelector` | required | module tag, entity, or path keyword: `user`, `voice-features`, `order` |
| `selectorMode` | `auto` | `auto`, `tag`, `entity`, `path` |
| `pageMode` | `crud` | `crud`, `dashboard`, `mixed` |
| `forceDetailPage` | `auto` | `auto` includes detail only when the endpoint exists and the project pattern has one |
| `routeBase` | from discovery | route path root; falls back to `/<kebab-module>` |
| `framework` | `auto` | `auto`, `vue-pure-admin`, `react-spa`, `generic` |
| `routeRegistration` | `auto` | an explicit file or registry path when the user already knows it |
| `permissionIntegration` | `auto` | `auto`, `on`, `off` |
| `outputMode` | `write` | `write` edits project files; `content` prints full file contents and writes nothing |

"Generate pages for user management" means `moduleSelector="user"`. "先给我看，不要写文件" means
`outputMode="content"`. For a vague module name, resolve with `selectorMode=auto` and state which
methods matched.

Do not write any page, route, or registration file until all of these hold:

1. The target module is specific, not just "management". If vague, ask one question.
2. The module's existing surface was checked. Any existing page, route module, menu entry, or wrapper method is planned as an update, never duplicated.
3. The Convention Report is complete: detected framework and chosen pack (or fallback plan), generated client path, API consumption convention, route registration mechanism, page layout, pagination base, the route id/params mechanism, and the representative pages read.
4. The page mode is known: `crud`, `dashboard`, or `mixed`.
5. The generated client exists. If it does not, stop and offer the two paths in Step E of `references/conventions-discovery.md` instead of inventing endpoints.

A matched pack needs no user question. An unknown framework, or `Low` confidence on API
consumption, route registration, or page layout, does.

## Steps

1. Run the read-only discovery sweep, including the existing-surface check. Emit the Convention Report before anything else.
2. Pick exactly one framework pack from the table below, or the fallback protocol.
3. Parse the generated client. Classify list, detail, create, update, delete, and action methods, and for the full path analyze response shapes into a capability matrix.
4. Plan the file set for `pageMode` and state every target path plus every registration touchpoint (route table, menu, guards, permission maps). Mark existing files as updates.
5. Generate the pages following the pack and the page blueprint. Add per-region loading, error, and retry where the blueprint requires it.
6. Generate action buttons only for endpoints that exist, with confirmation on risky ones.
7. Register routes through the discovered mechanism. Edit shared files only with anchored patches.
8. Run the pack's `## Verification` section, or the project's discovered typecheck/lint/build command when no pack matched, and say which command ran.
9. Report with the condensed or full format from the output contract.

| Detected stack | Pack |
|---|---|
| Vue 3 + Element Plus / pure-admin-thin | [references/frameworks/vue-pure-admin.md](references/frameworks/vue-pure-admin.md) |
| React + react-router + Tailwind primitives | [references/frameworks/react-spa.md](references/frameworks/react-spa.md) |
| anything else | the fallback protocol in `references/conventions-discovery.md` |

## Reference Map

| Read | When |
|------|------|
| [references/conventions-discovery.md](references/conventions-discovery.md) | Always, at step 1 — the discovery sweep, Convention Report, and fallback protocol |
| [references/client-parsing.md](references/client-parsing.md) | Always, at step 3 — module resolution, endpoint classification, type inference, consumption detection |
| [references/page-blueprint.md](references/page-blueprint.md) | Always, at step 5 — the framework-neutral behavior contract per page mode |
| [references/frameworks/vue-pure-admin.md](references/frameworks/vue-pure-admin.md) | Only when the project is Vue 3 + Element Plus or pure-admin-thin |
| [references/frameworks/react-spa.md](references/frameworks/react-spa.md) | Only when the project is a React SPA with react-router |
| [references/access-control.md](references/access-control.md) | Only when the project already has a permission system |
| [references/output-contract.md](references/output-contract.md) | Always, at step 9 — write rules, report format, and the quality gates |

## Rules

1. Generate only from the project's existing generated client and its real consumption layer. Never re-run code generation, and never hand-edit `Api.ts` or any other generated artifact.
2. Project conventions outrank pack defaults. Pack defaults outrank generic heuristics.
3. Use exactly one framework pack per generation. Never mix idioms from two stacks.
4. Add no runtime dependency, and create no reusable business component library. Use only libraries already in the manifest, and prefer the project's shared helpers. VueUse is a Vue-only optional policy described in the Vue pack; never add it for generated pages.
5. Never invent a permission key, role, or endpoint. Use only identifiers that exist in the project.
6. Route names must be unique. Where the framework caches pages by component name (keepAlive), the component name must match the route name.
7. Pagination base and query keys must match the project's observed convention. Filters must map to real query parameters. Never replace the server total with the current page length.
8. Degrade explicitly when an endpoint is missing: remove or disable the unsupported action, keep the page runnable, and report the gap. A capability the user asked for with no backing endpoint or field is a contract gap — report it, never approximate it with fabricated parameters or client-side tricks.
9. When the client exists but the project reaches the backend through another transport, follow the project transport, import types from the client, and report the divergence in Validation Notes.
10. When a page needs a mechanism the project has no precedent for — a routed id, a form prefill source, a confirmation primitive — degrade to the closest supported flow, or stop and ask. Never invent a convention and present it as observed.
11. When no analogous page exists to mirror, stop and ask before bootstrapping (Step D of the fallback protocol).

If a rule cannot be satisfied, stop and report blocking issues instead of generating.

## Output

Follow `references/output-contract.md`: the output mode, the writing rules, the condensed or full
report format, and the quality gates. Run every quality gate before reporting.

## Related Skills

- Upstream — `proto-api-generator` defines the HTTP contract, and `sphere-feature-workflow` runs the generation commands (`make gen/docs`, `make gen/dts`) that produce the TypeScript swagger client; generation cannot start before that client exists in the project.
- Downstream — none; generated pages, route registration, and permission wiring are the deliverable. When the UI needs a field or endpoint the client does not expose, hand back to `proto-api-generator` instead of faking it.
- Boundary — use `proto-api-generator` for contract changes and `sphere-feature-workflow` for backend, schema, or scaffold work; this skill owns only frontend pages and route registration, in whatever framework the project already uses. `prd` and `ux-analyst` own page intent when they exist.
- Companion — none bundled; the framework packs under `references/frameworks/` carry stack conventions, and `vueuse-functions` may be used for composable selection when the project already depends on VueUse.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
