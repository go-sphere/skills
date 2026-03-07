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

### Ent-Specific Field Annotations

When extracting from Ent schemas, recognize these patterns:

**Field Types to SQL Mapping:**
| Ent Field Type | SQL Column Type | Notes |
|----------------|-----------------|-------|
| `field.Int` | INT/BIGINT | Check for `uint` variant |
| `field.String` | VARCHAR/TEXT | Note `Size()` if present |
| `field.Bool` | TINYINT/BOOLEAN | |
| `field.Time` | DATETIME/TIMESTAMP | Note timezone settings |
| `field.JSON` | JSON/TEXT | |
| `field.Enum` | ENUM/VARCHAR | Extract values from constraint |
| `field.Bytes` | BLOB/VARBINARY | Binary data |
| `field.Float` | FLOAT/DOUBLE | Decimal numbers |
| `field.UUID` | UUID/VARCHAR | Check generation strategy |

**Complex Field Types:**
| Ent Field Type | SQL Column Type | Seed Format |
|----------------|-----------------|-------------|
| `field.JSON` | JSON/JSONB | `'{"key": "value"}'` |
| `field.JSON` (MySQL) | JSON | `'{"key": "value"}'` |
| `field.JSON` (PostgreSQL) | JSONB | `'{"key": "value"}'::jsonb` |
| Array field (PostgreSQL) | TEXT[] | `ARRAY['a', 'b']::text[]` |
| `field.Bytes` | BLOB | `X'48656C6C6F'` (hex) |

**Important Ent Options:**
- `Unique()`: Single-column unique constraint
- `Required()`: NOT NULL constraint
- `Default(value)`: Default value expression
- `Immutable()`: Cannot be updated after creation
- `Sensitive()`: Marked as sensitive data
- `Nillable()`: Allows NULL values (but avoid for entproto)

**Entproto Annotations:**
If `entproto` package is used, check for:
- `entproto.Field(n)`: Field number in protobuf
- `entproto.MapField()`: Custom mapping

## Step 2: Relationship Graph

Capture cardinality and FK ownership:

- 1-N: parent FK in child
- 1-1: unique FK or shared PK strategy
- N-N: explicit join table plus unique pair policy

**Ent Edge Patterns:**
```go
// 1-N: Organization has many Users
edge.From("users", User.Type).Ref("organization").Required()

// N-N: User has many Roles through user_roles
edge.From("roles", Role.Type).Ref("users").Through("user_roles", UserRole.Type)

// 1-1: User has one Profile (unique)
edge.From("profile", Profile.Type).Ref("user").Unique()
```

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
