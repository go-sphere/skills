# Conventions Discovery

## Table of Contents
- [Why Discovery Comes First](#why-discovery-comes-first)
- [Detection Sweep](#detection-sweep)
- [Framework Signals](#framework-signals)
- [Convention Report](#convention-report)
- [Unknown-Framework Fallback Protocol](#unknown-framework-fallback-protocol)
- [Discovery Wins Over Packs](#discovery-wins-over-packs)

## Why Discovery Comes First

The generated TypeScript swagger client is the same artifact in every sphere project. Everything around it differs: the transport wrapper pages import, the route registration mechanism, the UI kit, the permission system, the language of UI strings. A generator that assumes any of these produces code that does not fit.

Discovery is read-only, happens before generation, and its result is reported to the user. Skipping it is the single most common cause of unusable output.

## Detection Sweep

Work through these steps in order. Stop reading when a step is answered; do not open unrelated files.

1. **Rule and ownership files** — `AGENTS.md`, `CLAUDE.md`, frontend-local rule files, `.sphere/layout.json` (generated / mixed / project-owned boundaries). These outrank everything else, including this skill's packs.
2. **Manifest and build** — `package.json` (dependencies, scripts, package manager), `tsconfig` path aliases, Vite/config aliases, and which command actually typechecks (`pnpm typecheck`, `pnpm build`, `tsc -b`, ...). The project's command is the one to report, never a default.
3. **Generated client** — locate the imported `Api.ts` (default `src/api/swagger/Api.ts`), confirm it is generated, and note its export shape.
4. **Transport and unwrap convention** — which module instantiates or proxies the client, what a page receives after a call (`plain data`, `res.data?.data`, or a helper result), and what error type pages catch. See `client-parsing.md` section 5.
5. **Route registration** — where routes are declared (glob-collected module files, one central router, file-based routing), every file a new page touches (route table, menu, guards, permission maps), and where titles and icons live. Keep going until all registration sites are identified; they are often spread across two or more files.
6. **Representative pages** — read one to two existing pages of the same `pageMode`: a list page with pagination, a form page for edit/create, or a dashboard. Prefer the same feature area as the requested module. Read them fully; mirroring structure is the whole point.
7. **Cross-cutting conventions** — permission mechanism and existing keys, date/currency formatters, enum label sources, UI text language, lint/format rules, and any layering bans (for example `shared/` must not import `features/`).
8. **Existing surface** — search for a page, route module, menu entry, and wrapper method that already serve the target module (for example `rg -il "<module-key>" src | rg -i "page|view|router|menu|api"`). If any exists, this run is an update: plan anchored patches and report those files as already present, never generate a duplicate page or route.

## Framework Signals

Use manifest evidence, not file names alone.

| Signal | Likely pack |
|---|---|
| `vue`, `vue-router`, `element-plus`, `@pureadmin/table`, `pinia`; `src/router/modules/*.ts` | [frameworks/vue-pure-admin.md](frameworks/vue-pure-admin.md) |
| `react`, `react-router-dom`, Tailwind, `lucide-react`, shadcn-style `src/shared/components/ui/` | [frameworks/react-spa.md](frameworks/react-spa.md) |
| anything else | generic fallback protocol below |

Both packs were written from verified projects; a project that matches the dependencies but diverges in structure still follows the project, not the pack. Record the divergence.

## Convention Report

Report this before generating. It is the evidence that discovery happened, and the user's chance to correct a wrong read cheaply.

| Field | Value |
|---|---|
| Framework and pack | detected stack, chosen pack or `generic` |
| Generated client | path, and whether the project actually imports it |
| API consumption | wrapper layer / raw call / unwrap helper, with the file that proves it |
| Route registration | mechanism and the exact files a new page touches |
| Page layout | where new pages live (directory, naming) |
| Pagination base | internal page value and the UI control's base, as observed on a real list page |
| Route id / params | how an edit or detail page receives the record id, or `none observed` |
| UI kit | component library or primitives to reuse |
| Permission mechanism | how pages and buttons are gated, or `none found` |
| UI text language | language existing pages use |
| Sources read | file paths actually opened |
| Confidence | `High` / `Medium` / `Low`, with the weak field named |

Any field may be `Unknown`, but it must then be listed as an open question in Validation Notes. A `Low` confidence on API consumption or route registration opens the HARD-GATE confirmation even when a pack matched.

## Unknown-Framework Fallback Protocol

### Step A — Inspect

Run the full detection sweep. No shortcuts, no assumptions from framework brand.

### Step B — Report before generating (blocking)

Emit the Convention Report. If API consumption, route registration, or page layout is `Unknown`, say what is missing and ask one question rather than guessing.

### Step C — Generate from discovered primitives only

- no new dependencies, no invented design system, no new component library
- no idioms copied from a pack that did not match
- state management only if the project already uses it
- registration performed exactly through the mechanism found
- if there is no wrapper for the module, extend the project's existing wrapper layer
- when a page needs a mechanism the project has no precedent for (passing an id to a route, prefilling a form, confirming a destructive action), do not invent one: degrade to the closest supported flow (for example editing in place from the list row) or stop and ask one question, and record the choice as an assumption
- verify with the project's discovered check command (typecheck, lint, or build); there is no pack `## Verification` on this path

### Step D — No analogous page and no pack match

Stop before writing code and ask exactly one question: provide one representative page plus its route registration, or authorize bootstrapping a minimal pattern.

On the bootstrap path:

1. generate one list page plus its data layer only
2. put every invented structure in Validation Notes, each assumption naming its source (manifest, config, transport, or user instruction)
3. do not generate edit, detail, or dashboard pages until the list pattern is reviewed

### Step E — Generated client absent

Stop and report. Offer either to run the sphere generation commands through `sphere-feature-workflow` (`make gen/docs`, `make gen/dts`), or an explicitly degraded run against the project's existing transport. Mark the degraded run in Blocking Issues; never invent endpoints from memory.

### Step F — Never

- silently substitute a different client or transport
- edit generated files
- claim a convention was observed when it was assumed
- present an invented mechanism as an observed convention
- skip the report because the framework "looks obvious"

## Discovery Wins Over Packs

When a pack and the project disagree, the project wins. Follow the observed convention, note the divergence in Validation Notes, and name the pack rule that did not apply. Packs are accelerators for known stacks, not contracts imposed on them.

The same applies to names already in the UI: when the user's wording differs from the label the project uses for the same entity (for example 消耗品管理 vs an existing 「耗材管理」), keep the project's existing label unless the user explicitly asks for a rename, and mention the mismatch in the report. Field and route vocabulary follow the same rule.

A newly requested page may also need a mechanism no existing page demonstrates (routed edit ids, form prefill, confirmation). Absence of precedent is not permission to invent: prefer a flow the project already supports, or ask.
