# Go + Ent Service Patterns (sphere-layout)

## Table of Contents

1. ID De-duplication Helper
2. DAO Batch Query Pattern
3. Service List Pagination Pattern
4. Render Post-Processing Pattern
5. Bind Registration Pattern (`createFilesConf`)
6. Sensitive Field Handling Pattern
7. Post-Schema Generation Pattern
8. New Entity Integration Checklist

## 1. ID De-duplication Helper

Use a helper before `IDIn(...)` to remove zero values, de-duplicate, and produce stable order.

```go
func UniqueSortedNonZero[T cmp.Ordered](origin []T) []T {
    var zero T
    seen := make(map[T]struct{}, len(origin))
    result := make([]T, 0, len(origin))
    for _, v := range origin {
        if v == zero {
            continue
        }
        if _, ok := seen[v]; ok {
            continue
        }
        seen[v] = struct{}{}
        result = append(result, v)
    }
    slices.Sort(result)
    return slices.Clone(result)
}
```

## 2. DAO Batch Query Pattern

```go
func (d *Dao) GetUsers(ctx context.Context, ids []int64) (map[int64]*ent.User, error) {
    ids = conv.UniqueSorted(ids)
    users, err := d.User.Query().Where(user.IDIn(ids...)).All(ctx)
    if err != nil {
        return nil, err
    }

    out := make(map[int64]*ent.User, len(users))
    for _, u := range users {
        out[u.ID] = u
    }
    return out, nil
}
```

## 3. Service List Pagination Pattern

```go
query := s.db.Admin.Query()
count, err := query.Clone().Count(ctx)
if err != nil {
    return nil, err
}

totalPage, pageSize := conv.Page(count, int(req.PageSize))
rows, err := query.Clone().
    Limit(pageSize).
    Offset(pageSize * int(req.Page)).
    Order(admin.ByID(sql.OrderDesc())).
    All(ctx)
if err != nil {
    return nil, err
}
```

## 4. Render Post-Processing Pattern

Use generated `entmap` as baseline and perform repository-specific post-processing in hook callback.

```go
val, _ := entmap.ToProtoUser(value, func(source *ent.User, target *sharedv1.User) error {
    target.Avatar = r.storage.GenerateURL(source.Avatar)
    return nil
})
```

## 5. Bind Registration Pattern (`createFilesConf`)

New entities must be registered in `cmd/tools/bind/main.go#createFilesConf`.

```go
conf.NewEntity(
    ent.Example{},
    entpb.Example{},
    []any{ent.ExampleCreate{}, ent.ExampleUpdateOne{}},
    conf.CheckOptions(bindMode, conf.WithIgnoreFields(example.FieldCreatedAt, example.FieldUpdatedAt)),
)
```

If entity is missing here, schema-only changes are incomplete.

## 6. Sensitive Field Handling Pattern

Sensitive fields must be explicitly constrained in bind/render flows.

- In bind mode, ignore system-managed fields such as `created_at/updated_at`.
- In non-bind mapping/rendering, mask or clear sensitive fields (for example `password`, secrets).

Pattern examples:
- `conf.WithIgnoreFields(admin.FieldCreatedAt, admin.FieldUpdatedAt)`
- `conf.WithIgnoreFields(admin.FieldPassword)`
- Render stage explicit clear: `target.Password = ""`

## 7. Post-Schema Generation Pattern

After schema updates, run repository-native generation commands before testing.

```bash
make gen/proto
```

This ensures Ent code, proto artifacts, and bind/map generated code are synchronized.

## 8. New Entity Integration Checklist

1. Add Ent schema fields/indexes and comments.
2. Confirm ID strategy (generator-managed by default).
3. Add DTO/proto fields and service contracts.
4. Register entity in `cmd/tools/bind/main.go#createFilesConf`.
5. Add `WithIgnoreFields` review for timestamps/sensitive fields.
6. Add render mapper and mutation binder consumption points.
7. Add DAO batch helpers using `IDIn(...)` + dedupe helper.
8. Verify array field portability in target DB; if unsupported, prefer relation tables.
9. Run `make gen/proto`.
10. Validate generated diff is fully consumed in render/service code.
