# Best Practices for DB Schema Summary (sphere-layout)

## Table of Contents

1. Extract Entities from Requirements
2. Design Fields, Comments, and Nullability
3. Decide ID Strategy
4. Decide Relation Strategy
5. Build Minimal Indexes
6. Implement with Ent in Weak-Relation Style
7. Query with Batch `WHERE IN`
8. Integrate with Bind/Render/Service Layers
9. Improve Evolvability and Consistency

## 1. Extract Entities from Requirements

- Extract domain nouns and API resources into candidate entities.
- Define per entity:
  - lifecycle status (`status/state`) and mutation source
  - key timestamps (`created_at`, `updated_at`, `paid_at`, `closed_at`)
  - key constraints (unique/not-null/range/enum)
- Avoid over-splitting tables.
- Split only when:
  - optional field groups appear/disappear together and bloat main table
  - large low-frequency fields (long text/blob)
  - high-frequency updates on a few fields create write hotspots

## 2. Design Fields, Comments, and Nullability

- Add business comments for each schema and key fields.
- Decide each field policy explicitly:
  - required vs optional (`Optional/Nillable`)
  - mutable vs immutable (`Immutable`)
  - uniqueness (`Unique`)
  - default behavior (`Default`)
- Use Ent native enum (`field.Enum`) with explicit default.
- Keep timestamp naming unified: `created_at`, `updated_at`.
- Add `deleted_at` only when soft-delete policy exists.
- Prefer `NULL` for missing semantics; avoid empty-string-as-missing.

## 3. Decide ID Strategy

- Default: do not manually define `id` field in each schema.
- Prefer centralized ent generator ID configuration when available.
- Define custom `id` manually only for explicit business needs, and describe bind/proto impact.

## 4. Decide Relation Strategy

### One-to-many / many-to-one

- Store parent ID on the "many" side (`user_id`, `order_id`, `product_id`).
- Enforce naming consistency even if physical foreign key is not used.

### Many-to-many priority (fixed)

1. relation-entity table (preferred)
2. array IDs (only when DB dialect support is confirmed)
3. join table (when reverse query/filter/pagination is strong)
4. JSON fallback (last resort; must justify)

JSON is exception-only, not default modeling strategy.

## 5. Build Minimal Indexes

Create indexes only for:
- primary key / unique key
- high-selectivity filters
- sort/pagination keys used by list queries

Avoid:
- indexing every relation ID by default
- standalone low-cardinality status indexes unless with selective composite prefix

Rule of thumb:
- "Design composite index in the same order as list query filter/sort."
- "Try one index per hot query path."
- "Ship first, observe slow query logs, then add indexes."

## 6. Implement with Ent in Weak-Relation Style

- Keep target references as scalar fields (e.g. `field.Int64("user_id")`).
- Avoid forcing `edge` for all relations.
- Add edge only when query readability or ORM composition clearly benefits.

## 7. Query with Batch `WHERE IN`

Typical flow:
1. Query source rows and collect target IDs.
2. De-duplicate IDs.
3. Batch query target rows with `IDIn(...)`.
4. Build lookup map and hydrate output.

When ID list is large:
- chunk IDs (`500` to `1000` per batch)
- cap batch API request size
- use singleflight + cache when repeatedly queried

## 8. Integrate with Bind/Render/Service Layers

- New entities must be registered in `cmd/tools/bind/main.go#createFilesConf`.
- Review `WithIgnoreFields` for:
  - system-managed timestamps (`created_at`, `updated_at`)
  - sensitive fields (`password`, keys, secrets)
- Ensure render/service code consumes generated bind/map changes.
- Do not consider task complete with schema-only changes.

## 9. Improve Evolvability and Consistency

- Add denormalized snapshots for historical read consistency.
- Prefer typed/array fields for proto-friendly contract evolution.
- Use JSON only when requirement shape is truly open-ended and typed options fail.
- When skipping foreign key constraints, add:
  - write-path existence validation (sync or async)
  - periodic dangling-reference checks
