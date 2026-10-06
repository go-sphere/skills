---
name: ent-seed-sql-generator
description: Generate deterministic INSERT SQL seed data from Go Ent schemas, handling entity inference, relationship integrity, stable IDs, and dialect-specific values. Use for any seed data, test fixture, demo initialization, or database population task, even when the user never says "seed" or "SQL". Not for schema or migration design — that is `db-schema-designer`.
---

# Ent Seed SQL Generator

Produce one executable seed SQL artifact from Ent schemas and mixed evidence, with deterministic
IDs, valid relationships, and realistic production-like data.

Do not use this skill for schema migration design, runtime repository or service implementation, or
query performance tuning.

## Inputs

Do not write any SQL until the dialect, strategy, entity scope, and approximate row counts are
confirmed — either resolved from evidence or answered by the user. A wrong dialect invalidates
every line; a wrong strategy creates rework.

Gather inputs in this order:

1. The current prompt requirements.
2. Ent schemas and migration/DDL files: `ent/schema/*.go`, `ent/migrate/`.
3. Existing seed files and demo code behavior.
4. Product docs and domain notes.

Detect the dialect from the driver name in `ent/client.go` or config (`mysql`, `postgres`,
`sqlite`), from dialect-specific syntax in migration files, and from dialect imports in `go.mod`.

Ask one question at a time, and only for what the files cannot answer:

- Dialect — "I couldn't determine the database dialect from the project files. Which are you targeting: MySQL, PostgreSQL, or SQLite?"
- Strategy — "Should this seed be one-shot (fresh setup only), idempotent (`INSERT OR IGNORE` / `ON CONFLICT DO NOTHING`), or upsert (`ON CONFLICT DO UPDATE`)?"
- Scope — "Should I seed all entities, or a subset? If a subset, which ones?"
- Row counts — "How many rows per entity? 3-10 is typical for a development seed."

## Steps

Track these with TodoWrite, one task per step.

1. Collect the inputs above and detect the dialect.
2. Resolve remaining ambiguities by asking one question at a time.
3. Present the generation plan and get approval.
4. Build the schema map: extract fields (type, `Optional`, `Nillable`, `Unique`, `Default`, `Immutable`, `Sensitive`), every valid enum value, edges (`edge.To`, `edge.From`, `Required`, `Unique`, `Ref`) to derive FK ownership, and unique or composite indexes. Compute the topological order: tables with no FK references first, dependents after, join tables last.
5. Generate the SQL artifact.
6. Run the quality gates below before delivering.

### The generation plan (step 3)

Scale it to the task. One entity with no FKs needs one line. A multi-tenant system needs the full
dependency order.

> **Dialect:** MySQL
> **Strategy:** idempotent
> **Entity order** (by dependency):
> 1. `organizations` — 3 rows, no dependencies
> 2. `users` — 5 rows, FK → organizations
> 3. `projects` — 4 rows, FK → organizations + users
>
> **ID ranges:** organizations 2000-2999, users 1000-1999, projects 3000-3999
> **Assumptions:** password fields use a fixed bcrypt hash for test credentials
>
> Does this look right before I start writing?

## Reference Map

| Read | When |
|------|------|
| [references/model-extraction.md](references/model-extraction.md) | At step 4, to extract entities, fields, relations, and dependency order |
| [references/id-and-relation-rules.md](references/id-and-relation-rules.md) | At step 5, for ID ranges, FK integrity, multi-tenant rules, soft deletes, trees, and composite uniqueness |
| [references/output-sql-pattern.md](references/output-sql-pattern.md) | At step 5, for the file layout, strategy snippets, and dialect-specific value syntax |
| [references/password-hashing.md](references/password-hashing.md) | Only when a credential field is being seeded |

## Rules

1. Never invent a table or column without evidence. Mark every inference as a SQL comment.
2. Never use a random ID. Seed IDs must be identical across runs: integer ranges per entity, semantic string IDs (`usr_admin`, `org_acme`), or UUIDs derived deterministically from business keys.
3. Never break FK dependency order: parents before children, join tables last.
4. Keep timestamps coherent: `created_at <= updated_at`, spread over realistic ranges.
5. Make status values follow a realistic lifecycle, for example `draft → active → archived`.
6. Write meaningful text content and real email patterns. No Lorem Ipsum.
7. Keep row counts small: 3-10 rows per core table is usually enough.
8. Never expose production credentials. Use test-only values.
9. Never mix dialects in one file.
10. Never omit a field the Ent schema marks `Required()`.

## Output

Deliver exactly one SQL artifact — inline or as a file, as the user asked — containing:

1. Header comments: source inputs, dialect, strategy, assumptions.
2. An optional cleanup block, only for the idempotent and upsert strategies.
3. `INSERT` blocks grouped by dependency order, each group preceded by a comment.
4. Optional verification `SELECT` queries, only when requested.

Quality gates — verify every one before delivering:

- [ ] No orphan FKs; every referenced ID exists.
- [ ] No unique constraint violations, including composite unique indexes.
- [ ] No placeholder or TODO values.
- [ ] Every ID is deterministic; nothing random or auto-generated.
- [ ] Timestamps are internally consistent.
- [ ] Every `Required()` field appears in every `INSERT`.
- [ ] No invalid enum value.
- [ ] Every JSON column holds valid JSON.

## Related Skills

- Upstream — `ent-schema-implementer` supplies `ent/schema/*.go`, the primary input; `db-schema-designer` supplies `prd/DDL.md` when the schemas are not written yet. When neither exists, work from the schema evidence the user provides rather than inventing tables.
- Downstream — none; the SQL artifact is terminal. Use `sphere-feature-workflow` when the runtime service code, not the data, is what needs work.
- Boundary — use `db-schema-designer` for schema and migration design; this skill owns deterministic seed and fixture SQL only.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
