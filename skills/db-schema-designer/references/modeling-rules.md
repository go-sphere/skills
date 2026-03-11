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

Use these defaults:

- `created_at`: immutable
- `updated_at`: mutable
- `deleted_at`: only for soft-delete
- Prefer explicit defaults over ambiguous nulls unless null has business meaning

## 4. Field Type Policy

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
- No complex JSON objects, map-like blobs, or unbounded nested structures unless the user explicitly accepts the compatibility trade-off
- No UUID as the default identifier strategy; prefer `int64` IDs unless an external integration requires otherwise
- No heterogeneous arrays
- No field type that depends on custom serialization to become proto-compatible
- Do not use floating-point fields for money in normal business systems

### Review-time redesign rules

When a requested field does not fit:

1. Replace `time`-like values with `int64` timestamps and document units
2. Replace complex JSON with explicit columns or a separate relation entity
3. Replace UUID primary keys with `int64` unless a hard requirement says otherwise
4. Replace object arrays with relation tables
5. Store enum values as stable strings in the database and note that proto generation will map them to `int32` enum values
6. For money, default to `int64` in cents/fen and let clients format to dollars/yuan as needed
7. If exact decimal semantics exceed cents/fen, document the alternative storage strategy explicitly instead of leaving it ambiguous

## 5. ID Strategy

Default to generated surrogate IDs.

Use business or external IDs only when:

- External systems depend on them
- Migration compatibility requires them
- Natural keys are stable and business-significant

## 6. Relation Strategy

### One-to-many

- Store the parent key on the many side.

### Many-to-many

Prefer this order:

1. Relation entity when the relationship has attributes or lifecycle
2. Plain join table when reverse querying is needed
3. Array/JSON only when the storage engine and query shape clearly justify it

## 7. Index Planning

Create indexes for:

- Primary keys and unique constraints
- High-selectivity filters
- List pagination and sort keys
- Frequent composite query paths

Do not add indexes without a concrete query reason.

## 8. Review Questions

Before approval, confirm:

1. Which fields are business-required on create
2. Which fields can change after creation
3. Which relations need reverse lookup
4. Which list/detail/search queries must perform well
5. Which fields are snapshots rather than live references
6. Which requested field types had to be simplified for Ent + proto3 compatibility
7. Which money and enum fields need explicit representation rules

## 9. Review Deliverable Standard

The review document should answer:

1. What tables/entities exist
2. Why each exists
3. How they relate
4. What constraints matter
5. What field-type compromises were required for implementation compatibility
6. How enum and money fields are represented
7. What is still uncertain
