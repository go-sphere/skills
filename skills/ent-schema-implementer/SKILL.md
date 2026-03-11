---
name: ent-schema-implementer
description: Implement approved database designs as Go Ent schemas for go-sphere projects. Use when the database model has already been reviewed or approved and the next step is to write or update Ent schema code, add entproto annotations, plan generation steps, and wire the schema into bind/render/service integration. Do not use this for early-stage database modeling or review-first discussions; use db-schema-designer first.
---

# Ent Schema Implementer

## Overview

Convert an approved database design into concrete Ent schema changes for go-sphere projects.

This skill starts after the data model is stable enough to code. Its focus is Ent schema files, entproto compliance, generation impact, and downstream integration checkpoints.

## Entry Gate

Use this skill only when at least one of these is true:

1. The user explicitly says the database design is approved.
2. There is an accepted review brief or spec that defines the entities.
3. The task is clearly to implement or update Ent schema code rather than debate data modeling.

If requirements are still fluid, stop and return to `db-schema-designer`.

## Required Reading

Read these files in order:

1. [references/implementation-rules.md](references/implementation-rules.md)
2. [references/ent-schema-examples.md](references/ent-schema-examples.md)

Read this when integration work is in scope:

3. [references/go-ent-service-patterns.md](references/go-ent-service-patterns.md)

## Workflow

### Phase 1: Confirm Inputs

1. Read the approved design or extract confirmed schema decisions from the task.
2. Identify all affected Ent schema files and generated outputs.
3. Record any remaining assumptions that could change code shape.

### Phase 2: Implement Ent Schema

4. Map approved entities and fields to Ent schema definitions.
5. Apply field policies: required, optional, default, unique, immutable.
6. Implement relation strategy using project conventions.
7. Add indexes tied to the approved query plan.

### Phase 3: EntProto Compliance

8. Add `entproto.Message()` to every schema.
9. Add sequential `entproto.Field(n)` annotations to every field with ID at `1`.
10. Add `entproto.Enum(...)` mappings for enum fields with values starting from `1`.

### Phase 4: Integration and Verification

11. Review bind registration, ignored fields, render impacts, and service touchpoints.
12. List required generation and verification commands.
13. Call out any blocking follow-up work outside the schema file itself.

## Hard Gates

1. Do not invent unapproved entities or fields unless labeled as `Assumption:`.
2. Every implemented field must map back to a reviewed business decision.
3. All Ent schemas must be entproto-ready.
4. New entities are not complete until bind integration impact is addressed.
5. Generated-file behavior must be planned, not hand-waved.

## Output Requirements

For implementation planning or code-review responses, include:

1. Target schema files
2. Entity-to-field mapping summary
3. Entproto compliance notes
4. Integration impact notes
5. Required commands and validation steps
