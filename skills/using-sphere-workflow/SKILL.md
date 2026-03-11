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

## Workflow Map

### Discovery and Requirement Shaping

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
- `pure-admin-crud-generator`
  - Use to scaffold pure-admin-thin CRUD views and router modules from swagger-generated client methods.

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
- Need a merge-ready scaffold feature touching generated boundaries:
  - Start with `sphere-feature-workflow`.

## Operating Constraints

- Prefer go-sphere repository conventions over generic engineering defaults.
- Keep stage boundaries clear: requirements first, then spec, then schema/contract design, then implementation.
- When multiple skills are needed, progress forward one stage at a time instead of blending outputs.
- Reuse the existing bundled skill outputs and default artifact locations unless the user specifies otherwise.

## Plugin Bootstrap Note

When this skill is injected by the `sphere-workflow` plugin, treat it as already loaded bootstrap context.
Use the native skill mechanism only for follow-up skills such as `project-intake`, `spec-writer`, `db-schema-designer`, `proto-api-generator`, or `sphere-feature-workflow`.
