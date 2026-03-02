---
name: ent-schema-generator
description: Summarize database schema design from requirement inputs and produce implementation-ready outputs for Go + Ent in this repository. Use when the input may be a prompt, Markdown requirement document, repository folder, or runnable demo behavior and you need entity extraction, field/constraint design, weak-relation ID strategy, index planning, Ent schema guidance, and concrete bind/render/service integration impacts.
---

# Ent Schema Generator

## Overview

Turn requirement inputs into implementation-ready DB schema plans for `sphere-layout` projects.
Focus on decisions that are directly actionable in Ent schema code and downstream
`bind/render/service` integration.

This skill is repository-specific. Prefer local scaffold conventions over generic patterns
unless the user explicitly requests otherwise.

## Required Reading Order

Read these references before producing a final schema brief:

1. [references/best-practices.md](references/best-practices.md)
2. [references/output-template.md](references/output-template.md)

Load conditionally when needed:

1. [references/go-ent-service-patterns.md](references/go-ent-service-patterns.md)
   Use when the task includes DAO/service/render consumption details.
2. [references/ent-schema-examples.md](references/ent-schema-examples.md)
   Use when concrete Ent schema snippets are required.

## Input Modes

1. Prompt-only:
   - infer entities, lifecycle, and query paths from text
   - state assumptions explicitly
2. Requirement document / repo folder:
   - treat requirement docs as business truth
   - treat local code and generated artifacts as integration truth
3. Runnable demo behavior:
   - extract objects, state transitions, and key actions before schema design

## Workflow

1. Gather evidence from prompt/docs/proto/schema/service/dao/render.
2. Extract candidate entities and lifecycle states.
3. Design field-level policy per field:
   - `Optional/Nillable/Unique/Immutable/Default`
   - enum defaults
   - timestamp and soft-delete strategy
4. Decide ID strategy:
   - **REQUIRED**: explicitly define primary key field with `entproto.Field(1)` for proto mapping
   - custom `id` with explicit business need and compatibility note
5. Decide relation strategy with fixed priority:
   - relation-entity > array (if dialect-safe) > join table > JSON fallback
6. Build query-driven index plan from real list/filter/sort paths.
7. Add Ent + Go implementation guidance:
   - weak relation IDs first
   - batch `IDIn(...)` retrieval and map backfill
   - chunk strategy for large ID sets
8. **Add entproto annotations** (REQUIRED for all schemas):
   - Schema-level: add `entproto.Message()` in `Annotations()` method
   - Field-level: add `entproto.Field(n)` annotation to each field
   - Enum fields: use `entproto.Enum(map[string]int32{...})` for value mapping
   - Field numbers: ID=1, then assign sequentially (2, 3, 4...)
9. Map repository integration impact:
   - `cmd/tools/ent/main.go`
   - `cmd/tools/bind/main.go#createFilesConf`
   - render/dao/service touchpoints
10. Add consistency controls:
    - snapshot fields where history consistency matters
    - dangling-reference checks when using weak relations
11. Produce final brief with the required template.

## Hard Rules

1. Do not stop at schema-only output when integration is impacted.
2. If new entities are introduced, explicitly check bind registration impact.
3. If bind/render mapping is affected, explicitly review `WithIgnoreFields`
for system-managed or sensitive fields.
4. Always include post-change commands, at minimum:
   - `make gen/proto`
   - `go test ./...` (or explicit alternative)
5. Always include a generation diff checklist for `entpb/proto/bind/map`.

## EntProto Hard Rules (REQUIRED)

All schemas MUST include entproto annotations for gRPC/proto generation:

1. **Schema-level annotation**: Every schema MUST define `Annotations()` method returning `entproto.Message()`:
   ```go
   func (EntityName) Annotations() []schema.Annotation {
       return []schema.Annotation{
           entproto.Message(),
       }
   }
   ```

2. **Field-level annotation**: Every field MUST have `entproto.Field(n)` where n is the proto field number:
   - Primary key field MUST use `entproto.Field(1)`
   - Other fields use sequential numbers (2, 3, 4...)
   ```go
   field.String("name").
       Annotations(entproto.Field(2))
   ```

3. **Enum field annotation**: Enum fields MUST include both `entproto.Field(n)` and `entproto.Enum(map[string]int32{...})`:
   ```go
   field.Enum("status").
       Values("pending", "in_progress", "done").
       Annotations(
           entproto.Field(3),
           entproto.Enum(map[string]int32{
               "pending":     0,
               "in_progress": 1,
               "done":        2,
           }),
       )
   ```

4. **Avoid Optional/Nillable for entproto fields**:
    - EntProto’s `optional` type handling is cumbersome; try to avoid using `Optional()` or `Nillable()` whenever possible.
    - Instead, use zero-value defaults or `DefaultFunc` to generate default values:
     ```go
     // Bad: Optional with entproto
     field.Int64("deleted_at").
         Optional().
         Nillable().
         Annotations(entproto.Field(10))

     // Good: Zero-value default
     field.Int64("deleted_at").
         Default(0).
         Annotations(entproto.Field(10))

     // Good: DefaultFunc for dynamic zero value
     field.Int64("created_at").
         Immutable().
         DefaultFunc(func() int64 { return time.Now().Unix() }).
         Annotations(entproto.Field(7))
     ```

5. **Import requirement**: Add `"entgo.io/contrib/entproto"` to imports.

6. **Output must include**: In the Ent Implementation Plan section, show complete schema code with all `entproto.Field(n)` annotations, using zero-value defaults instead of Optional.

## Failure Conditions

Do not consider the task complete when any of the following is true:

1. Schema change is proposed but bind registration impact is missing.
2. Mapping-sensitive fields are discussed without `WithIgnoreFields` impact.
3. Post-change commands are missing.
4. Generation diff checklist is missing.

## Output Format

Use [references/output-template.md](references/output-template.md) exactly.
Keep all 11 sections and the generation diff checklist.

## Resources

- [references/best-practices.md](references/best-practices.md)
- [references/output-template.md](references/output-template.md)
- [references/go-ent-service-patterns.md](references/go-ent-service-patterns.md)
- [references/ent-schema-examples.md](references/ent-schema-examples.md)

## Notes

This skill is AI-first and does not rely on local scripts for drafting.
