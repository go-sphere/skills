# Implementation Rules

Reference guide for translating approved database designs into Ent schema code.

## 1. Input Contract

Preferred source order:

1. Approved review brief or accepted assumptions
2. Existing Ent schema and proto contracts
3. Service/DAO/render usage
4. Generic Ent best practices

If the approved design and existing code conflict, report the conflict before coding around it.

## 2. Field Mapping

For each approved field, decide:

- Ent field type
- `Optional` / `Nillable`
- `Unique`
- `Immutable`
- `Default` / `DefaultFunc`
- Comment on non-obvious business meaning

Prefer explicit defaults over nullable fields when the business model allows it.

## 3. ID Strategy

Default to generator-managed IDs unless the approved design explicitly requires otherwise.

If using custom IDs, explain:

- Why generator-managed IDs are insufficient
- What compatibility or migration rule requires the custom ID

## 4. Relation Strategy

Prefer simple scalar relation keys first.

Use ORM edges only when they materially improve composition or query ergonomics.

For many-to-many:

1. Relation entity first
2. Join table second
3. Arrays or JSON only when explicitly justified

## 5. JSON Fields

JSON fields exist for one purpose: low-frequency, non-core, structurally-unstable attributes that the design brief has explicitly classified as volatile. Do not invent JSON fields that the approved design did not call for.

### Pick the right shape

| Situation | Use | Rationale |
|-----------|-----|-----------|
| Brief lists known sub-keys; some type safety is wanted | `field.JSON("extra", domain.OrderExtra{}).Optional()` | Typed struct, easy to read in Go code, callers get autocomplete |
| Structure is genuinely unknown / passthrough | `field.JSON("extra", json.RawMessage{}).Optional()` | No structural assumptions; treat as bytes |
| Anything else | (none) | Do **not** use `field.Any` as a default — its weak typing leaks type assertions everywhere |

### Naming

JSON field names are not free. Use the canonical name from the approved brief:

| Name | Use case |
|------|----------|
| `extra` | Business extension attributes |
| `metadata` | System / tracing / source info |
| `settings` | Config-like flags |
| `payload` | Event, message, task payloads |
| `attrs` | Product or object attributes |

One name per purpose per table — do not mix `extra` and `metadata` for the same kind of data across entities.

### Where the struct lives

The JSON struct is **business code**, not schema code. Put it in a domain package:

```
internal/domain/order/extra.go     // type OrderExtra struct { ... }
ent/schema/order.go                 // field.JSON("extra", order.OrderExtra{})
```

This keeps the ent schema free of business-shaped types and lets domain code evolve the struct without touching generated code unnecessarily.

### Comments are required

Every JSON field carries a comment that states why it's JSON and what's allowed in it:

```go
field.JSON("extra", order.OrderExtra{}).
    Optional().
    Comment("Low-frequency, non-core extensions. Promote stable sub-keys to real columns.")
```

### When a sub-key graduates

If the brief flagged a JSON sub-key as a promotion candidate (or one becomes query-hot in practice), the implementation path is:

1. Add the real column as `Optional().Nillable()` with a comment naming the JSON source.
2. Plan dual-write at the service layer (do not bake this into the schema).
3. Generate an Atlas migration; do not rely on auto-migrate.
4. After backfill and read switch, mark the JSON sub-key deprecated in the struct (see section 6).

## 6. Field Deprecation

Never delete a field from the ent schema as step one. Production tables expect to find it.

The stages:

| Stage | ent schema state | Code change |
|-------|------------------|-------------|
| `deprecated` | Field still present, `Optional()`, comment starts with `deprecated:` | Stop new code paths from writing it |
| `read_only` | Same as deprecated | Stop reading from it; monitor |
| `removed_from_code` | Same | No live references |
| `dropped` | Field removed, migration drops column | Generate & ship migration |

ent schema example:

```go
field.String("old_tag").
    Optional().
    Nillable().
    Comment("deprecated: use extra.marketing_tag instead"),
```

If a `OrderExtra` sub-field is deprecated, mark it with a `// Deprecated:` line in the struct so `go vet`/IDE warnings show up at call sites.

If the design brief includes a deprecation, do not skip ahead to the drop. Verify which stage the brief asks for and implement only that stage.

## 7. Indexes

Indexes must come from approved query patterns.

Good reasons:

- List filters
- Sort + pagination
- Uniqueness guarantees
- Reverse lookup paths

## 8. EntProto Requirements

Every schema must include:

- `entproto.Message()` in `Annotations()`
- `entproto.Field(1)` on the primary key
- Sequential `entproto.Field(n)` on all other fields
- `entproto.Enum(map[string]int32{...})` on enum fields

Enum values must start from `1`. `0` is reserved.

## 9. Integration Checklist

For each new or changed entity, review:

- `cmd/tools/gen/entcrud/main.go` (`conf.NewEntity` in `conf.NewFilesConf`)
- `WithIgnoreFields` for timestamps and sensitive fields
- render mapping impact
- DAO batch query helpers
- service-layer usage of the new fields

## 10. Migration Policy

Generated `ent` code can auto-migrate via `client.Schema.Create(ctx)`. That is fine for local dev and integration tests. It is not fine for production.

Production migrations are versioned: each schema change produces a reviewable SQL file (Atlas, Bytebase, Flyway, or the project's equivalent). The usual loop is:

```
edit ent/schema/*.go
↓ go generate ./ent/...
↓ generate migration diff (atlas migrate diff / equivalent)
↓ review the SQL
↓ apply in staging
↓ apply in prod (online-DDL tool for large hot tables)
```

When the change touches a high-traffic table, surface whether the operation can use `ALGORITHM=INSTANT` or needs `gh-ost` / `pt-online-schema-change`. That's a decision the user must make before the migration is applied — never assume "it'll be fine".

If the project still relies on `client.Schema.Create` in production code paths, flag it as a follow-up risk in the handoff message; do not silently leave it.

## 11. Required Commands

After schema changes, plan or run:

```bash
make gen/proto
go test ./...
```

Add the project's migration-diff command (e.g. `atlas migrate diff`) when the change is destined for a production database.
