---
name: ent-seed-sql-generator
description: Generate deterministic INSERT SQL seed data from Go Ent schemas and mixed inputs (prompt requirements, product docs, demo code). Use when Codex must infer entities and relationships, create meaningful linked sample records, and output one executable SQL seed artifact with stable IDs (not random) for dev/test data initialization.
---

# Ent Seed SQL

## Overview

Generate one SQL seed file that can be executed directly. Infer schema and relationships from Ent definitions or other inputs, then create realistic data with referential integrity and deterministic IDs.

## Scope

Use this skill when the task is "produce executable seed SQL from Ent and related context."

Do not use this skill when the task is schema migration design, query optimization, or runtime repository/service implementation.

## Workflow

1. Collect inputs and constraints:
   - Prompt requirements
   - Product documentation
   - Demo program or existing seed snippets
   - Ent schema files, migration files, or table DDL if available

2. Determine SQL dialect:
   - Use project evidence first (driver/config/migrations)
   - If evidence is insufficient, ask user to confirm dialect first
   - If user is unavailable and you must proceed, fall back to SQLite-compatible SQL and mark it as an explicit assumption
   - State dialect assumptions explicitly in the SQL header comment

3. Build schema map:
   - Extract entities, required fields, unique constraints, enum-like fields
   - Extract relationships and cardinality (1-1, 1-N, N-N)
   - Resolve insertion order by dependency (parent before child)

4. Choose seed execution strategy before writing SQL:
   - One-shot: plain inserts, may fail on rerun
   - Idempotent: cleanup or conflict-safe inserts
   - Upsert-style: update-on-conflict when explicitly needed
   - Record chosen strategy in SQL header comments

5. Design deterministic sample records:
   - Choose stable IDs with business meaning, never purely random values
   - Keep cross-table references consistent
   - Ensure values look realistic and match domain semantics

6. Generate one executable SQL seed file:
   - Use transaction-safe structure where supported
   - Insert in dependency order
   - Add concise comments for assumptions and special handling (e.g., password hash)
   - Ensure conflict handling matches chosen execution strategy and target dialect

7. Self-check before finalizing:
   - No orphan foreign keys
   - No duplicate unique keys unless intentional conflict strategy is used
   - No TODO placeholders left in SQL
   - IDs and references remain deterministic across reruns
   - If local tooling is available, run at least one lightweight syntax/execution check

## Output Contract

Produce one SQL seed artifact by default (inline SQL or file write, based on user request):
- Header comment: source inputs, dialect, assumptions
- Strategy comment: one-shot / idempotent / upsert
- Optional cleanup section (only when requested or chosen as the strategy)
- `INSERT` statements grouped by table in dependency order
- Optional verification `SELECT` statements at the end (only when requested)

Use deterministic and meaningful IDs:
- Integer IDs: reserve fixed ranges per table/entity group
- String IDs: use semantic patterns (`usr_alice`, `team_core_platform`)
- UUID IDs: derive deterministic UUID from stable keys, not random UUID4

## Guardrails

- Never generate unrelated random data just to increase row count.
- Never break foreign key dependencies.
- Never invent columns or tables not supported by evidence; if inferred, mark as assumption.
- Never assume nullable fields are safe defaults when business semantics require explicit values.
- Prefer explicit column lists in every `INSERT`.
- Keep row count pragmatic: enough to demonstrate relationships and product flow, not bloated.

## Password Handling

When seed data includes credentials:
- Detect hashing algorithm from code/docs first (bcrypt/argon2/pbkdf2).
- Prefer reusing known valid hash samples from fixtures/docs.
- If hashing is required and no hash sample exists, generate hash output once, then pin that literal in SQL for deterministic reruns.
- For salted algorithms (bcrypt/argon2), generation output is intentionally non-deterministic; seed determinism is achieved by reusing pinned hash literals.
- Document the plain test password only when user allows it for dev/test usage.

## References

- Use [model extraction guide](references/model-extraction.md) to infer entities and relationships.
- Use [ID and relationship rules](references/id-and-relation-rules.md) to enforce deterministic linking.
- Use [SQL output pattern](references/output-sql-pattern.md) for final SQL layout and checks.
- Use [password hash notes](references/password-hashing.md) only when credential fields exist.

## Execution Notes

This skill is AI-first and does not require dedicated generation scripts. Use scripts only for narrow tasks such as one-time password hash generation.
