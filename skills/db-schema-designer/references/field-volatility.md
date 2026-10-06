# Field Volatility, Lifecycle, and DDL Change Management

How to decide where an attribute lives, how to retire a field, and how to ship a DDL change.
Field type policy, ID strategy, relations, and index planning live in `modeling-rules.md`.

## Field Volatility and Storage Shape

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


## Field Lifecycle

Fields rarely disappear cleanly. Treat their removal as a multi-stage process so live systems do not break.

| Stage | Meaning | Schema state |
|-------|---------|--------------|
| `active` | Normal use | Field present, no deprecation note |
| `deprecated` | New code stops writing it; reads still tolerated | Field present, marked deprecated in comment |
| `read_only` | Writes stopped, observation period | Same as deprecated; monitored |
| `removed_from_code` | No code references | Field present in DB only |
| `dropped` | Physical column removed | Migration applied |

Do not skip stages on production tables. If the review introduces a replacement field, the brief should call out the deprecation plan for the old one, not silently drop it.

## DDL Change Management

The design brief is one half of the contract; the migration that ships it is the other. The brief should assume:

- All schema changes ship as versioned migrations (Atlas / Bytebase / Flyway / equivalent), not ad-hoc `ALTER TABLE` and not application-startup auto-migration.
- Each new column on a high-traffic table flags whether it can use `ALGORITHM=INSTANT` or needs an online DDL tool (`gh-ost`, `pt-online-schema-change`).
- New required columns on existing tables are introduced as nullable first, backfilled, and only then tightened.

Surface these constraints in the brief whenever a change touches an existing large table.
