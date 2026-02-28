---
name: ent-seed-sql-generator
description: Generate deterministic INSERT SQL seed data from Go Ent schemas and mixed inputs (prompt requirements, product docs, demo code). Use when Codex must infer entities and relationships, create meaningful linked sample records, and output one executable SQL seed artifact with stable IDs (not random) for dev/test data initialization.
---

# Ent Seed SQL Generator

## Goal

Produce one executable seed SQL artifact from Ent schemas and mixed evidence, with deterministic IDs, valid relationships, and realistic domain data.

## Trigger / Non-Trigger

Use this skill when the task is to generate or revise seed SQL from Ent schema context, docs, demo behavior, or prompt requirements.

Do not use this skill for schema migration design, runtime repository/service implementation, or query performance tuning.

## Input Sources

Collect available inputs in this order:

1. Current prompt requirements
2. Ent schemas and migration/DDL files
3. Existing seed files and demo code behavior
4. Product docs and domain notes

## Reference Loading Plan

Load only what is needed for the current task:

- [references/model-extraction.md](references/model-extraction.md): entity/field/relation extraction and dependency planning
- [references/id-and-relation-rules.md](references/id-and-relation-rules.md): deterministic IDs, FK integrity, multi-tenant constraints
- [references/output-sql-pattern.md](references/output-sql-pattern.md): final SQL layout and strategy-specific patterns
- [references/password-hashing.md](references/password-hashing.md): only when credential fields are seeded

## Workflow

1. Confirm scope and dialect evidence.
- Infer dialect from driver/config/migrations first.
- If still unknown and progress is required, use SQLite-compatible SQL and record this assumption in the header.

2. Build a schema map.
- Extract entities, required fields, unique constraints, enum/state fields, and audit columns.
- Extract relationships and cardinality (1-1, 1-N, N-N).
- Compute insert order from dependency graph.

3. Choose execution strategy before writing SQL.
- `one-shot`: plain inserts, not rerun-safe.
- `idempotent`: cleanup or conflict-safe insert behavior.
- `upsert`: update-on-conflict when explicitly needed.
- Record strategy in SQL header comments.

4. Design deterministic data.
- Use stable, meaningful IDs (integer ranges, semantic string IDs, or deterministic UUIDs).
- Keep FK references, ownership chains, and timestamps coherent.
- Keep row counts pragmatic and scenario-driven.

5. Generate one executable SQL artifact.
- Use explicit column lists for every `INSERT`.
- Group by table in dependency order.
- Add concise assumption comments and special handling notes (for example pinned password hash).
- Keep conflict handling aligned with chosen strategy and dialect.

6. Run final quality gates.
- No orphan foreign keys.
- No unintended unique collisions.
- No placeholder values or unresolved TODOs.
- Deterministic IDs/references across reruns.
- Run lightweight local syntax/execution check when tooling is available.

## Output Contract

Return exactly one seed SQL artifact (inline or file, per user request) with:

1. Header comments: source inputs, dialect, assumptions
2. Strategy comment: `one-shot` or `idempotent` or `upsert`
3. Optional cleanup block (only when strategy requires it)
4. `INSERT` blocks grouped by dependency order
5. Optional verification `SELECT` queries (only when requested)

## Guardrails

- Never invent tables or columns without evidence; mark any inference as assumption.
- Never use random IDs as final seed values.
- Never break FK dependency order.
- Never bloat row counts with unrelated fake data.
- Never expose production credential claims from seed SQL.

## Notes

This is an AI-first workflow. Dedicated scripts are optional and only needed for narrow deterministic sub-tasks (for example one-time hash generation to pin in SQL).
