---
name: db-schema-designer
description: Design review-ready database schemas for go-sphere and similar backend projects from requirements, docs, demos, or existing APIs. Use when the goal is to define or review entities, fields, relationships, constraints, indexes, lifecycle states, or schema evolution before any Ent implementation or code generation. Prefer this skill whenever the user wants database design first, review-first modeling, table structure discussion, or approval before coding.
---

# DB Schema Designer

## Overview

Turn product and backend requirements into review-ready database design briefs.

This skill stops at the database design stage. Its job is to help humans review and approve the data model before any Ent schema coding, entproto annotations, or project integration work begins.

Because approved designs will later be implemented in Ent and exposed through proto3 messages, this skill must reject or redesign field types that do not map cleanly to the Ent + proto3 constraint set.

## Scope Boundary

Do:

1. Extract entities, fields, relationships, constraints, statuses, and timestamps.
2. Design table-level structure, key naming, nullability, uniqueness, indexing, and field-type compatibility.
3. Surface assumptions, trade-offs, and open questions for review.
4. Produce a review brief using the required output template.

Do not:

1. Write Ent schema code unless the user explicitly asks for a follow-up implementation step.
2. Add entproto numbering or Go integration instructions.
3. Mix bind/render/service tasks into the review document.

If the design is approved and code should be written, hand off to `ent-schema-implementer`.

## Required Reading

Read these files in order before producing a database design:

1. [references/modeling-rules.md](references/modeling-rules.md)
2. [references/review-output-template.md](references/review-output-template.md)

## Workflow

### Phase 1: Evidence and Extraction

1. Gather inputs from prompt, docs, mockups, proto files, existing schemas, and service behavior.
2. Extract candidate entities, lifecycle states, key timestamps, and business invariants.
3. Record evidence conflicts and resolve them explicitly.

### Phase 2: Database Design

4. Design fields with type, requiredness, default behavior, uniqueness, and mutability.
5. Apply the field-type policy from [references/modeling-rules.md](references/modeling-rules.md) and redesign unsupported types before approval.
6. Choose ID strategy and explain why.
7. Design one-to-many and many-to-many relations.
8. Build an index plan from list/filter/sort/query patterns.
9. Decide deletion strategy, snapshot fields, and audit timestamps.

### Phase 3: Review Packaging

10. Mark assumptions explicitly as `Assumption:`.
11. List unresolved questions and approval blockers clearly.
12. Produce the final review brief using [references/review-output-template.md](references/review-output-template.md).

## Hard Gates

1. The output must be understandable without showing Ent code.
2. Every major table needs a business purpose, key fields, and lifecycle notes.
3. Every proposed index must be tied to a real query pattern.
4. Every field type must be checked against downstream Ent + proto3 compatibility before approval.
5. If a type does not map cleanly, redesign it in the review output instead of deferring the problem to implementation.
6. If the request is incomplete, stop at design options and blocking questions rather than forcing implementation details.
7. If DDL is requested, provide it only as an optional appendix after the review brief, not as the primary artifact.

## Output Requirements

Use the review template exactly:

1. Keep section order unchanged.
2. Write `N/A` for non-applicable sections.
3. Include a dedicated field-type compatibility section.
4. Separate confirmed design decisions from open questions.
5. Keep the document review-oriented rather than code-oriented.
