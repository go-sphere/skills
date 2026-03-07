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

## Required Reading

Read in order:

1. [references/best-practices.md](references/best-practices.md) - Decision rules for schema design
2. [references/output-template.md](references/output-template.md) - Output format (required)

Reference when needed:

- [references/ent-schema-examples.md](references/ent-schema-examples.md) - Code examples with entproto annotations
- [references/go-ent-service-patterns.md](references/go-ent-service-patterns.md) - DAO/service integration patterns

## Workflow

1. Gather evidence from prompt/docs/proto/schema/service/dao/render
2. Extract candidate entities and lifecycle states
3. Design field-level policy per field (Optional/Nillable/Unique/Immutable/Default)
4. Decide ID strategy - use generator-managed by default
5. Decide relation strategy: relation-entity > array > join table > JSON fallback
6. Build query-driven index plan from real list/filter/sort paths
7. Add Go implementation guidance (weak relation IDs, batch IDIn, chunking)
8. **Add entproto annotations** - REQUIRED for all schemas:
   - Schema: `entproto.Message()` in `Annotations()` method
   - Fields: `entproto.Field(n)` with sequential numbers (ID=1)
   - Enums: `entproto.Field(n)` + `entproto.Enum(map[string]int32{...})` starting from 1
9. Map repository integration: bind registration, WithIgnoreFields, render/dao/service
10. Produce final brief using [references/output-template.md](references/output-template.md)

## Hard Rules

1. Do not stop at schema-only output when integration is impacted
2. If new entities introduced, explicitly check bind registration impact
3. If bind/render mapping affected, review `WithIgnoreFields` for sensitive fields
4. Always include post-change commands: `make gen/proto`, `go test ./...`
5. Always include generation diff checklist for entpb/proto/bind/map

## Failure Conditions

Task is incomplete when:

1. Schema change proposed but bind registration impact missing
2. Mapping-sensitive fields discussed without `WithIgnoreFields` impact
3. Post-change commands missing
4. Generation diff checklist missing

## Resources

- [references/best-practices.md](references/best-practices.md)
- [references/output-template.md](references/output-template.md)
- [references/ent-schema-examples.md](references/ent-schema-examples.md)
- [references/go-ent-service-patterns.md](references/go-ent-service-patterns.md)
