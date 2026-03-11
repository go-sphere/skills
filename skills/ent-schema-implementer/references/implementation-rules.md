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

## 5. Indexes

Indexes must come from approved query patterns.

Good reasons:

- List filters
- Sort + pagination
- Uniqueness guarantees
- Reverse lookup paths

## 6. EntProto Requirements

Every schema must include:

- `entproto.Message()` in `Annotations()`
- `entproto.Field(1)` on the primary key
- Sequential `entproto.Field(n)` on all other fields
- `entproto.Enum(map[string]int32{...})` on enum fields

Enum values must start from `1`. `0` is reserved.

## 7. Integration Checklist

For each new or changed entity, review:

- `cmd/tools/bind/main.go#createFilesConf`
- `WithIgnoreFields` for timestamps and sensitive fields
- render mapping impact
- DAO batch query helpers
- service-layer usage of the new fields

## 8. Required Commands

After schema changes, plan or run:

```bash
make gen/proto
go test ./...
```
