---
name: ent-schema-implementer
description: Implement an approved database design as Go Ent schemas in a go-sphere project. Use when the data model is already settled and the next step is writing or updating Ent schema code, entproto annotations, generation steps, and bind/render/service integration notes. Not for early-stage modeling or review-first discussion — that is `db-schema-designer`.
---

# Ent Schema Implementer

Convert an approved database design into concrete Ent schema changes. Confirm the implementation
plan first, then write code. Field types, enum values, and relation ownership are hard to change
after generation, so never guess them.

## Inputs

Use this skill only when at least one is true:

1. The user says the database design is approved.
2. An accepted review brief or spec defines the entities.
3. The task is clearly to write or update Ent schema code rather than to debate the data model.

Do not write Ent schema code, modify any file, or run any generation command until you have
presented an implementation plan and the user has confirmed it. If requirements are still fluid or
ambiguous, stop and return to `db-schema-designer`.

## Steps

Track these with TodoWrite, one task per step.

1. Read the approved design. Extract confirmed entities and purposes, the field list with types, nullability, defaults, and mutability, relation shapes, the index plan with its query patterns, and any open questions the design still marks.
2. Identify affected files: which schema files change, which are new.
3. Ask clarifying questions, one at a time, only for ambiguity that would change the code shape. Never ask about something the design already specifies.
4. Present the implementation plan and get approval.
5. Implement the schema files, one entity at a time.
6. Add entproto annotations to every schema.
7. Work through the integration impact.
8. List the generation and verification commands in the order they must run.
9. Close with the handoff message.

### The implementation plan (step 4)

Scale it to the work — brief for one entity with a few fields. Include:

- **Affected files** — each schema file, new or modified.
- **Entity mapping** — one row per entity: name, field count, relation count, index count.
- **Entproto field numbering** — the field order for the `ID = 1` assignment. For a modified schema, confirm which existing numbers must not shift.
- **JSON field plan** — per approved JSON field: the canonical name (`extra`, `metadata`, `settings`, `payload`, `attrs`), typed struct or `json.RawMessage`, and the domain package that will hold the struct.
- **Deprecation plan** — per deprecated field: which stage to implement now, and which proto field number stays reserved.
- **Integration scope** — which bind, render, or service files need manual follow-up.
- **Migration plan** — the versioned migration command to run after `go generate`, and whether any large-table change needs online DDL.
- **Assumptions** — every design gap you filled with a default.

Then ask: "Does this plan look right before I start writing?"

### Implementing a schema (step 5)

For each entity: write the struct plus `Fields()`, `Edges()`, and `Indexes()`; apply the field
policies (required, optional, default, unique, immutable); define or reuse the typed struct for
each approved JSON field and reference it from `field.JSON(...)`; keep approved deprecated fields
in place with a `deprecated:` comment until a later migration drops them; implement relations with
project conventions, using `edge.To(...).Unique()` plus a back-edge for an extension entity; and
add only the indexes tied to approved query patterns.

Never invent an unapproved entity or field. When something clearly standard is missing, such as a
`created_at` timestamp, add it with a comment: `// Assumption: added standard audit timestamp`.

### Integration impact (step 7)

Cover bind registration (which entities, and where), ignored fields (which to exclude from proto
generation), render impacts (which render files reference the changed schema), and service
touchpoints (which service files need updates after generation).

Mark each item as handled by generation, requiring manual follow-up, or requiring a separate skill.

## Reference Map

| Read | When |
|------|------|
| [references/implementation-rules.md](references/implementation-rules.md) | Always, before step 4 — field mapping, ID strategy, relations, entproto requirements, migration policy |
| [references/ent-schema-examples.md](references/ent-schema-examples.md) | Always, before step 5 — baseline entity, manual ID, and enum patterns |
| [references/ent-advanced-examples.md](references/ent-advanced-examples.md) | When the design approved a typed JSON field, an extension entity, a deprecated field, or a custom-fields model |
| [references/go-ent-service-patterns.md](references/go-ent-service-patterns.md) | When integration work reaches the service layer |

## Rules

1. `entproto.Message()` goes on every schema struct.
2. `entproto.Field(n)` numbers are sequential and start with `ID` at `1`.
3. `entproto.Enum(...)` values start at `1`, never `0` — `0` is the proto3 default.
4. Preserve existing field numbers exactly when modifying a schema. Shifting them breaks proto compatibility.
5. Flag a field-number conflict before writing. Never pick a number silently.
6. Add no speculative indexes. Every index traces to an approved query pattern.
7. If the project runs `client.Schema.Create(ctx)` against production in a startup path, flag it in the handoff. New columns ship as reviewed migrations, not application-side auto-migrate.

## Output

List the generation and verification commands in run order, adapted to the actual project setup:

```
go generate ./ent/...
buf generate
# When the change is destined for a real database, generate a versioned migration:
atlas migrate diff <name> --env local
go build ./...
```

Then close with:

> **Done.** Implemented `N` entities across `M` files.
>
> **Run these commands:**
> 1. `...`
>
> **Manual follow-up needed:**
> - `...`
>
> **Next skill:** use `proto-service-generator` if you need service implementations from the generated interfaces.

## Related Skills

- Upstream — `db-schema-designer` owns the approved design; return there when requirements are still fluid. `spec-writer` supplies entity definitions when no schema design exists yet.
- Downstream — `proto-service-generator` for implementations of the generated interfaces (see the handoff message above); `ent-seed-sql-generator` when the new schemas need deterministic seed data. Hand off after the listed generation and verification commands pass.
- Boundary — use `db-schema-designer` for entity, field, relationship, and index design; this skill owns Ent schema files and entproto annotations.
- Companion — `sphere-feature-workflow` when integration spills past schema files into bind, render, or service layers; if it is unavailable, report those touchpoints as manual follow-up instead.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
