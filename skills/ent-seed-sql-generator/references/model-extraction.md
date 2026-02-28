# Model Extraction Guide

Use this guide to convert mixed inputs into a concrete seed plan before writing SQL.

## Source Priority

When sources conflict, apply this precedence:

1. Explicit requirement in current prompt
2. Ent schema + migration/DDL definitions
3. Existing seed/demo behavior
4. Product docs narrative
5. Conservative inference (must be documented)

## Step 1: Entity Inventory

For each table/entity, capture:

- Table name
- PK type and generation style
- Required vs nullable fields
- Unique constraints (single/composite)
- Enum/state fields and allowed values
- Audit fields (`created_at`, `updated_at`, `deleted_at`)

For Ent projects, inspect:

- `field.*` options (`Optional`, `Nillable`, `Unique`, `Default`, `Immutable`, `Sensitive`)
- `edge.To`/`edge.From` and `Required`/`Unique`
- enum/value validation constraints

## Step 2: Relationship Graph

Capture cardinality and FK ownership:

- 1-N: parent FK in child
- 1-1: unique FK or shared PK strategy
- N-N: explicit join table plus unique pair policy

Output a dependency order for inserts (topological order).

## Step 3: Candidate Seed Shape

Unless user specifies size:

- Core business tables: 3-10 rows each
- Dictionary/reference tables: minimal complete set
- Join tables: only meaningful links, avoid cartesian expansion

Prioritize rows that demonstrate realistic product flow over raw volume.

## Step 4: Assumptions

If semantics are unclear, infer cautiously from:

- Field names (`status`, `owner_id`, `tenant_id`)
- Demo behavior and fixture values
- Domain terms in docs

Record each non-trivial inference in SQL header comments.

## Extraction Output (Internal Working Format)

Use a compact internal model before final SQL:

- `entities`: table -> columns/constraints
- `relations`: source_table -> target_table + cardinality + FK column
- `insert_order`: ordered table list
- `seed_size`: per-table row targets
- `assumptions`: explicit bullet list
