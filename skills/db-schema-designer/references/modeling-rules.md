# Modeling Rules

Reference guide for review-first database design.

## 1. Evidence Priority

When inputs conflict, resolve them in this order:

1. Explicit user requirement or accepted assumption
2. Approved requirement/spec document
3. Existing repository behavior or public API contract
4. Generic database best practices

Always report conflicts and resolutions explicitly.

## 2. Entity Extraction

- Extract stable business nouns first.
- Define each entity's purpose, lifecycle state, and ownership boundary.
- Split an entity only when one of these is true:
  - Optional field groups appear and disappear together
  - Large low-frequency fields would bloat hot rows
  - Update frequency differs enough to create write hotspots

## 3. Field Design

For each field, decide:

- Type
- Required vs optional
- Default behavior
- Unique constraint
- Mutability
- Validation notes
- **Volatility class** — stable core, query-hot, or volatile (see section 4)
- **Lifecycle stage** — active, deprecated, or removed (see section 11)

Use these defaults:

- `created_at`: immutable
- `updated_at`: mutable
- `deleted_at`: only for soft-delete
- Prefer explicit defaults over ambiguous nulls unless null has business meaning

## 4. Field Volatility and Storage Shape

Not every field belongs as a column on the main table. Before deciding the type of a field, decide where it lives. The shape follows the volatility, not the other way around.

### Three volatility classes

| Class | Examples | Where it lives |
|-------|----------|----------------|
| **Stable core** | user id, order no, status, amount, created_at | Regular column on the main table |
| **Query-hot** | order status, channel, city, tag type — anything filtered, sorted, joined, or aggregated frequently | Regular column on the main table, with an index |
| **Volatile** | marketing tag, campaign id, A/B experiment flag, display-only attributes, throwaway form fields | JSON field, extension table, or dynamic field model |

Classify every field at design time. If a field is volatile today but will clearly be query-hot once stable, design it as volatile now and plan the promotion path.

### Decision tree for volatile fields

Walk down in order. The first match wins.

1. **Does this field need indexing, uniqueness, foreign keys, sorting, aggregation, or frequent filtering?** → Promote to a regular column. It is not actually volatile.
2. **Is this set of fields specific to one business module (marketing, risk, ops) and the main entity is hot?** → Use an **extension table** (a separate entity, one-to-one with the main entity).
3. **Are the fields defined per-tenant or per-business-type at runtime (SaaS custom fields, dynamic forms, surveys, approval flows, product attributes)?** → Use a **dynamic field model**: a `custom_field_def` table for the schema and a `custom_field_value` table for the data. Do not keep adding columns.
4. **Otherwise (low-frequency, display/passthrough, experimental, structure may change)** → Use a **JSON field** on the main or extension table.

### JSON field guidance

JSON is the default escape hatch for low-frequency, non-core, structurally-unstable attributes. It is allowed in approved designs when the volatility is justified.

- Use one canonical name per purpose:
  - `extra` — business extension attributes
  - `metadata` — system / tracing / source info
  - `settings` — config-like flags
  - `payload` — event, message, task payloads
  - `attrs` — product or object attributes
- Pick one of these per field; do not invent ad-hoc names per table.
- Do **not** make JSON a dumping ground for fields that should be query-hot. Every JSON field needs a one-line justification ("low-frequency display only", "experimental, may change", "module-scoped extension").
- JSON in MySQL supports query (`JSON_EXTRACT`, generated columns + functional indexes) but treat that as a stopgap. If you find yourself wanting to index it, that field has already graduated and should be a real column.

### Extension table guidance

Use a separate entity, one-to-one with the main entity, when:

- The main entity is a hot core table you do not want churning.
- A set of fields belongs to one module (marketing / risk / ops / KYC).
- Extension fields are large or low-read-rate compared to the main row.
- Different teams own different attribute groups.

Each module can own its own JSON inside the extension table (e.g. `marketing JSON`, `risk JSON`) so module-specific churn does not interfere across modules.

### Dynamic field model guidance

`custom_field_def` (schema) + `custom_field_value` (data) only when fields are genuinely defined at runtime by end users / tenants. This pattern is powerful and dangerous: queries get complex, types weaken, performance needs care. **Never** put core transactional fields (price, status, payment outcome) in this model.

### Promotion path: JSON → column

Plan the promotion path during design when a JSON sub-field looks likely to stabilize:

1. Add the real column (Optional / Nillable).
2. Dual-write the column and the JSON sub-field.
3. Backfill historical rows.
4. Switch reads to the column.
5. Stop writing the JSON sub-field.
6. Drop the JSON sub-field on the next cleanup.

Note the candidates explicitly in the review brief so the implementation skill knows which fields are "JSON for now, real column later".

## 5. Field Type Policy

Approved database designs must already fit the downstream Ent + proto3 type system. If a field cannot map cleanly, redesign it during review instead of pushing the problem to implementation.

### Allowed default shapes

Prefer these storage shapes:

- Scalar basics: `int64`, `int32`, `bool`, `string`
- Timestamps: `int64` unix timestamp
- Enums/status: stable string enum values in the database
- Arrays: only simple scalar arrays such as `[]string`, `[]int64`, `[]int32`, `[]bool`
- Money: `int64` in the smallest business unit, usually cents/fen

### Disallowed or restricted shapes

- No native time/datetime object type in the contract layer; use timestamp fields instead
- No UUID as the default identifier strategy; prefer `int64` IDs unless an external integration requires otherwise
- No heterogeneous arrays
- No field type that depends on custom serialization to become proto-compatible
- Do not use floating-point fields for money in normal business systems

### JSON exception

Complex JSON objects are **not** disallowed, but they must be justified by the volatility model in section 4:

- Only for fields classified as volatile (low-frequency / display-only / experimental / module-scoped extension).
- Each JSON field carries a one-line justification in the review brief.
- Any sub-field that becomes query-hot must be planned for promotion to a real column.

Volatile structured data that does not meet these criteria is still treated as a redesign target — push it into a relation entity, an extension table, or explicit columns.

### Review-time redesign rules

When a requested field does not fit:

1. Replace `time`-like values with `int64` timestamps and document units
2. If the field is genuinely volatile, place it in a typed JSON field per section 4 (`extra`, `metadata`, etc.); otherwise replace it with explicit columns or a separate relation entity
3. Replace UUID primary keys with `int64` unless a hard requirement says otherwise
4. Replace object arrays with relation tables (or a JSON field when the array is volatile and never queried by index)
5. Store enum values as stable strings in the database and note that proto generation will map them to `int32` enum values
6. For money, default to `int64` in cents/fen and let clients format to dollars/yuan as needed
7. If exact decimal semantics exceed cents/fen, document the alternative storage strategy explicitly instead of leaving it ambiguous

## 6. ID Strategy

Default to generated surrogate IDs.

Use business or external IDs only when:

- External systems depend on them
- Migration compatibility requires them
- Natural keys are stable and business-significant

## 7. Relation Strategy

### One-to-many

- Store the parent key on the many side.

### Many-to-many

Prefer this order:

1. Relation entity when the relationship has attributes or lifecycle
2. Plain join table when reverse querying is needed
3. Array/JSON only when the storage engine and query shape clearly justify it

## 8. Index Planning

Create indexes for:

- Primary keys and unique constraints
- High-selectivity filters
- List pagination and sort keys
- Frequent composite query paths

Do not add indexes without a concrete query reason.

## 9. Review Questions

Before approval, confirm:

1. Which fields are business-required on create
2. Which fields can change after creation
3. Which relations need reverse lookup
4. Which list/detail/search queries must perform well
5. Which fields are snapshots rather than live references
6. Which requested field types had to be simplified for Ent + proto3 compatibility
7. Which money and enum fields need explicit representation rules
8. Which fields are stable core, which are query-hot (need index), and which are volatile (JSON / extension / dynamic)
9. Which volatile fields have a planned promotion path to a real column

## 10. Review Deliverable Standard

The review document should answer:

1. What tables/entities exist
2. Why each exists
3. How they relate
4. What constraints matter
5. What field-type compromises were required for implementation compatibility
6. How enum and money fields are represented
7. Which fields live as JSON, in extension tables, or in a dynamic field model — and why
8. What is still uncertain

## 11. Field Lifecycle

Fields rarely disappear cleanly. Treat their removal as a multi-stage process so live systems do not break.

| Stage | Meaning | Schema state |
|-------|---------|--------------|
| `active` | Normal use | Field present, no deprecation note |
| `deprecated` | New code stops writing it; reads still tolerated | Field present, marked deprecated in comment |
| `read_only` | Writes stopped, observation period | Same as deprecated; monitored |
| `removed_from_code` | No code references | Field present in DB only |
| `dropped` | Physical column removed | Migration applied |

Do not skip stages on production tables. If the review introduces a replacement field, the brief should call out the deprecation plan for the old one, not silently drop it.

## 12. DDL Change Management

The design brief is one half of the contract; the migration that ships it is the other. The brief should assume:

- All schema changes ship as versioned migrations (Atlas / Bytebase / Flyway / equivalent), not ad-hoc `ALTER TABLE` and not application-startup auto-migration.
- Each new column on a high-traffic table flags whether it can use `ALGORITHM=INSTANT` or needs an online DDL tool (`gh-ost`, `pt-online-schema-change`).
- New required columns on existing tables are introduced as nullable first, backfilled, and only then tightened.

Surface these constraints in the brief whenever a change touches an existing large table.
