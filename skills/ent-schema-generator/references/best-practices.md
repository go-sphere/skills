# Best Practices for Ent Schema Design (sphere-layout)

Reference guide for schema decision-making in sphere-layout projects.

## Table of Contents

1. Evidence Priority
2. Entity Extraction
3. Field Design
4. ID Strategy
5. Relation Strategy
6. Index Planning
7. Weak-Relation Implementation
8. Batch Query Patterns
9. Integration Checklist
10. EntProto Requirements
11. Post-Change Commands

---

## 1. Evidence Priority

When inputs conflict, resolve in this order:

1. Explicit user requirement or accepted assumptions
2. Repository source-of-truth (`proto`, Ent schema, service code)
3. Generated artifacts (`entpb`, bind/map outputs)
4. Generic best practices

Always report conflicts and resolutions explicitly.

---

## 2. Entity Extraction

- Extract domain nouns and API resources into candidate entities
- Define per entity: lifecycle status, key timestamps, key constraints
- **Avoid over-splitting** — split only when:
  - Optional field groups appear/disappear together
  - Large low-frequency fields (long text/blob)
  - High-frequency updates create write hotspots

---

## 3. Field Design

### Nullability & Constraints

| Policy | When to Use |
|--------|-------------|
| Required | Business-critical, always needed |
| Optional/Nillable | May legitimately not exist |
| Unique | Business uniqueness constraint |
| Immutable | Once set, never changes |
| Default | Sensible fallback when not specified |

### Timestamp Conventions

- Use `created_at` (immutable), `updated_at` (mutable)
- Add `deleted_at` only for soft-delete
- Prefer 0/unix timestamp over NULL for "not set"

### Enum Fields

- Use Ent native `field.Enum` with explicit default
- Always add `entproto.Enum` mapping (values start from 1)

---

## 4. ID Strategy

**Default**: Generator-managed ID (no manual `id` field)

**Manual ID only** when business explicitly requires:
- External natural keys (e.g., ISBN, SKU)
- Distributed ID generation
- Migration compatibility

---

## 5. Relation Strategy

### Priority Order (many-to-many)

1. **Relation entity table** (preferred)
2. **Array IDs** (only when DB dialect confirmed)
3. **Join table** (when reverse query/filter needed)
4. **JSON fallback** (last resort — must justify)

### One-to-Many / Many-to-One

Store parent ID on "many" side: `user_id`, `order_id`, `product_id`

---

## 6. Index Planning

Create indexes only for:
- Primary key / unique constraints
- High-selectivity filters
- Sort/pagination keys in list queries

Avoid indexing every relation ID by default.

---

## 7. Weak-Relation Implementation

- Store target references as scalar fields: `field.Int64("user_id")`
- Add edges only when ORM composition clearly benefits
- Keep code simple: scalar first, edge second

---

## 8. Batch Query Patterns

```go
// 1. Collect and dedupe IDs
ids = conv.UniqueSortedNonZero(ids)

// 2. Batch query with IDIn
users, err := d.User.Query().Where(user.IDIn(ids...)).All(ctx)

// 3. Build lookup map
out := make(map[int64]*ent.User, len(users))
for _, u := range users {
    out[u.ID] = u
}
```

For large ID sets (>500), chunk into batches of 500-1000.

---

## 9. Integration Checklist

For each new entity, verify:

- [ ] Registered in `cmd/tools/bind/main.go#createFilesConf`
- [ ] `WithIgnoreFields` includes `created_at`, `updated_at`
- [ ] Sensitive fields (password, secrets) handled in bind/render
- [ ] Render mapper consumes generated bind changes
- [ ] Service code handles the new entity

---

## 10. EntProto Requirements

All schemas MUST be entproto-ready:

```go
func (User) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (User) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        // ... other fields with sequential entproto.Field(n)
    }
}
```

### Enum Mapping Rules

- Values **MUST** start from 1 (0 is reserved)
- Use sequential values for future extensibility

```go
// Good
entproto.Enum(map[string]int32{"pending": 1, "active": 2, "done": 3})

// Bad - starts from 0
entproto.Enum(map[string]int32{"pending": 0, "active": 1})
```

---

## 11. Post-Change Commands

Always run after schema changes:

```bash
make gen/proto
go test ./...
```

Validation checklist:
- [ ] All fields have `entproto.Field(n)`
- [ ] Schema has `entproto.Message()`
- [ ] Enum fields have `entproto.Enum` mapping
- [ ] New entity in bind config
- [ ] Generated diff consumed by render/service
