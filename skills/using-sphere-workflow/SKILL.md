---
name: using-sphere-workflow
description: Use when the task is in a go-sphere repository, follows the go-sphere delivery lifecycle, or you need to decide which bundled go-sphere skill should run first. This is the bootstrap entrypoint for the sphere-workflow plugin and routes work to the smallest relevant skill.
---

# Using Sphere Workflow

The bootstrap entrypoint for the `sphere-workflow` plugin. Classify the request first, then invoke
only the next needed skill. Never load every bundled skill preemptively.

## Routing Rules

Apply in order. The first rule that matches decides.

1. The user named a skill — use that skill.
2. The request spans several lifecycle stages — start at the earliest missing artifact.
3. The request is already narrowed to one stage — invoke only that stage's skill.
4. The task is about pulling upstream layout changes into an existing project, or adopting a pre-contract project — `sphere-layout-sync`, not `sphere-feature-workflow`.
5. The task is about the `protoc-gen-*` plugins themselves rather than the `.proto` files they consume — `protoc-plugin-engineering`, not `proto-api-generator`.
6. The work is only filling in missing methods in one service file from an existing generated interface — `proto-service-generator`, not `sphere-feature-workflow`.
7. The task is auditing or simplifying existing Go code for over-design, over-optimization, or over-defensive checks rather than adding a feature — `go-simplify`, not `sphere-feature-workflow`.
8. The task will modify go-sphere scaffold contracts, schemas, services, or generation commands — `sphere-feature-workflow`.

## Workflow Map

### Discovery and Requirement Shaping

- `interview-me` — resolve design decisions through a step-by-step interview before drafting specs or code.
- `project-intake` — new project kickoff, scattered requirements, demos, screenshots, rough drafts.
- `prd` — the user wants a PRD, or intake is done and product requirements need formalizing.
- `ux-analyst` — visual prototypes or demos must become user flows and behavior semantics.

### Specification and Planning

- `spec-writer` — create or refine an implementation-ready specification.
- `spec-diff-pipeline` — a spec changed and downstream proto, schema, and task impact needs analysis.

### Data and Contract Design

- `db-schema-designer` — design entities, fields, relationships, and indexes before coding.
- `ent-schema-implementer` — turn an approved schema design into Go Ent schema files.
- `ent-seed-sql-generator` — deterministic development, test, or demo seed SQL.
- `proto-api-generator` — define or revise proto3 and HTTP API contracts.
- `proto-service-generator` — generate or complete service skeletons from generated interfaces.

### Implementation and Surfaces

- `sphere-feature-workflow` — end-to-end scaffold implementation, especially across proto, schema, service, bind/map, or generation commands.
- `frontend-crud-generator` — admin pages and route registration from the generated TypeScript swagger client, in the project's own frontend framework.

### Layout and Toolchain Maintenance

- `sphere-layout-sync` — update a project to a newer layout revision, resolve layout drift, or adopt a legacy project into `.sphere/layout.lock.json`.
- `protoc-plugin-engineering` — write, refactor, or review the `protoc-gen-*` plugins, including config, templates, output stability, and golden tests.

### Quality and Verification

- `godoc` — write self-contained Go API comments and verified usage examples for consumers and AI agents.
- `go-test-engineering` — audit, repair, or write Go tests, including interface contract suites and justified golden tests.
- `go-simplify` — audit and safely simplify Go code for over-design, over-optimization, and over-defensive checks, with a green test baseline as the safety net.
- `go-sphere-makefiles` — standardize or repair Make targets, root batch orchestration, and Make-driven CI.

## Stage Handoffs

Every stage skill ends with a `## Related Skills` block naming its upstream, downstream, boundary,
and companion skills.

1. When a stage skill finishes and names a default next skill, announce the handoff with the artifact it needs, for example "next: use `db-schema-designer` with `prd/SPEC.md`".
2. Honor that handoff before re-classifying the request from scratch.
3. Invoke the next skill when the user agrees, or when the user already asked for the whole flow and the current stage's completion criteria are met. Never blend two stages in one pass.
4. If the named skill is not installed in this session, say which skill and artifact are needed, then continue with the current work; do not stall. The user's explicit skill choice outranks any handoff suggestion.
5. When one request spans two skills' boundaries, own this stage's side and name the other skill for the rest instead of silently absorbing it.

## Operating Constraints

1. Prefer go-sphere repository conventions over generic engineering defaults.
2. Inside a generated project, the project's own `.sphere/layout.json`, `AGENTS.md`, and `docs/LAYOUT_CONTRACT.md` outrank any bundled skill where they disagree. Read them before editing.
3. There are four official layouts — `standard`, `simple`, `bun`, `telegram` — with different capabilities. Never assume the standard layout.
4. Keep stage boundaries clear: requirements, then spec, then schema and contract design, then implementation.
5. Progress one stage at a time instead of blending outputs.
6. Reuse the existing bundled skill outputs and their default artifact locations unless the user specifies otherwise.
7. When this skill is injected by the plugin, treat it as already-loaded bootstrap context. Use the native skill mechanism only for the follow-up skill.
