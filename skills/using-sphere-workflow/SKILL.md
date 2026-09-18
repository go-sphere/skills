---
name: using-sphere-workflow
description: Use when the task is in a go-sphere repository, follows the go-sphere delivery lifecycle, or you need to decide which bundled go-sphere skill should run first. This is the bootstrap entrypoint for the sphere-workflow plugin and routes work to the smallest relevant skill.
---

# Using Sphere Workflow

This skill is the bootstrap entrypoint for the `sphere-workflow` plugin.

Use it to classify the request first, then invoke only the next needed go-sphere skill.
Do not load every bundled skill preemptively.

## Routing Rules

1. If the user explicitly names a skill, use that skill.
2. If the request spans multiple lifecycle stages, start at the earliest missing artifact.
3. If the request is already narrowed to a single stage, invoke only that stage skill.
4. If the task will modify go-sphere scaffold contracts, schemas, services, or generation commands, route into `sphere-feature-workflow`.
5. If the task is about pulling upstream layout changes into an existing project, or adopting a pre-contract project, route into `sphere-layout-sync` — not `sphere-feature-workflow`.
6. If the task is about the `protoc-gen-*` plugins themselves rather than the `.proto` contracts they consume, route into `protoc-plugin-engineering` — not `proto-api-generator`.
7. If the work is only filling in missing methods in one service file from an existing generated interface, route into `proto-service-generator` — not `sphere-feature-workflow`.
8. If the task is auditing or simplifying existing Go code for over-design, over-optimization, or over-defensive checks rather than adding a feature, route into `go-simplify` — not `sphere-feature-workflow`.

## Stage Handoffs

Stage skills end with a `## Related Skills` block naming their upstream, downstream,
boundary, and companion skills.

1. When a stage skill finishes and names a default next skill, announce the handoff
   with the artifact it needs, for example "next: use `db-schema-designer` with `prd/SPEC.md`".
2. Honor that handoff before re-classifying the request from scratch.
3. Invoke the next skill when the user agrees, or when the user already asked for the
   whole flow and the current stage's completion criteria are met. Do not blend two stages in one pass.
4. If the named skill is not installed in this session, say which skill and artifact are
   needed, then continue with the current work; do not stall. The user's explicit skill
   choice still outranks any handoff suggestion.
5. When one request spans two skills' boundaries, own this stage's side and name the other
   skill for the rest instead of silently absorbing it.

## Workflow Map

### Discovery and Requirement Shaping

- `interview-me`
  - Use for step-by-step interactive interviews to resolve design decisions before drafting specs or code.
- `project-intake`
  - Use for new project kickoff, scattered requirements, demos, screenshots, or rough drafts.
- `prd`
  - Use when the user wants a PRD or when intake is complete and product requirements need to be formalized.
- `ux-analyst`
  - Use when visual prototypes or demos need to be translated into user flows and behavior semantics.

### Specification and Planning

- `spec-writer`
  - Use to create or refine an implementation-ready specification.
- `spec-diff-pipeline`
  - Use when a spec changed and downstream proto/schema/task impact needs to be analyzed.

### Data and Contract Design

- `db-schema-designer`
  - Use to design entities, fields, relationships, and indexes before coding.
- `ent-schema-implementer`
  - Use to turn an approved schema design into Go Ent schema files.
- `ent-seed-sql-generator`
  - Use for deterministic development, test, or demo seed SQL.
- `proto-api-generator`
  - Use to define or revise proto3 and HTTP API contracts.
- `proto-service-generator`
  - Use to generate or complete service skeletons from generated interfaces.

### Implementation and Surfaces

- `sphere-feature-workflow`
  - Use for end-to-end go-sphere scaffold implementation, especially when proto, schema, service, bind/map, or generation commands are involved.
- `frontend-crud-generator`
  - Use to generate admin pages and route registration from a sphere-generated TypeScript swagger client, in whatever frontend framework the project already uses.

### Layout and Toolchain Maintenance

- `sphere-layout-sync`
  - Use to update a generated project to a newer layout revision, resolve layout drift, or adopt a legacy project into the `.sphere/layout.lock.json` contract.
- `protoc-plugin-engineering`
  - Use to write, refactor, or review the `protoc-gen-*` plugins themselves, including config, templates, generated-output stability, and golden tests.

### Quality and Verification

- `go-test-engineering`
  - Use to audit, repair, or write Go tests, including reusable interface contract suites and justified golden tests.
- `go-simplify`
  - Use to audit and safely simplify Go codebases for over-design, over-optimization, and over-defensive checks, with a green test baseline as the safety net.
- `go-sphere-makefiles`
  - Use to standardize or repair repository Make targets, root batch orchestration, and Make-driven CI while preserving multi-module, generator, and layout behavior.

## Common Starting Points

- Rough feature idea with mixed notes:
  - Start with `project-intake`.
- Need a PRD from agreed business direction:
  - Start with `prd`.
- Need a SPEC from PRD or requirement text:
  - Start with `spec-writer`.
- Need review-ready schema design:
  - Start with `db-schema-designer`.
- Need contract-first API definition:
  - Start with `proto-api-generator`.
- Need deterministic development, test, or demo seed SQL:
  - Start with `ent-seed-sql-generator`.
- Need a merge-ready scaffold feature touching generated boundaries:
  - Start with `sphere-feature-workflow`.
- Need admin or dashboard pages and routes from a generated swagger client:
  - Start with `frontend-crud-generator`.
- Need to audit AI-generated tests or add trustworthy Go tests:
  - Start with `go-test-engineering`.
- Need to slim down over-engineered Go code without changing behavior:
  - Start with `go-simplify`.
- Need consistent Makefiles or Make-driven CI across repositories:
  - Start with `go-sphere-makefiles`.
- Need to upgrade a project to a newer layout revision or fix layout drift:
  - Start with `sphere-layout-sync`.
- Need to change or review a `protoc-gen-*` plugin:
  - Start with `protoc-plugin-engineering`.

## Operating Constraints

- Prefer go-sphere repository conventions over generic engineering defaults.
- Inside a generated project, the project's own `.sphere/layout.json`, `AGENTS.md`, and `docs/LAYOUT_CONTRACT.md` outrank any bundled skill where they disagree. Read them before editing.
- There are four official layouts (`standard`, `simple`, `bun`, `telegram`) with different capabilities. Do not assume the standard layout.
- Keep stage boundaries clear: requirements first, then spec, then schema/contract design, then implementation.
- When multiple skills are needed, progress forward one stage at a time instead of blending outputs.
- Reuse the existing bundled skill outputs and default artifact locations unless the user specifies otherwise.

## Plugin Bootstrap Note

When this skill is injected by the `sphere-workflow` plugin, treat it as already loaded bootstrap context.
Use the native skill mechanism only for the relevant follow-up skill, such as `project-intake`, `spec-writer`, `db-schema-designer`, `proto-api-generator`, `sphere-feature-workflow`, `sphere-layout-sync`, `protoc-plugin-engineering`, `go-test-engineering`, `go-simplify`, or `go-sphere-makefiles`.
