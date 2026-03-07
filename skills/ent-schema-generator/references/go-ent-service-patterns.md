# Go + Ent Service Patterns (sphere-layout)

DAO/Service integration patterns for sphere-layout projects.

## Table of Contents

1. ID De-duplication Helper
2. DAO Batch Query
3. Chunked Batch Query
4. Service Pagination
5. Render Post-Processing
6. Bind Registration
7. Sensitive Field Handling

---

## 1. ID De-duplication

```go
func UniqueSortedNonZero[T cmp.Ordered](origin []T) []T {
    var zero T
    seen := make(map[T]struct{}, len(origin))
    result := make([]T, 0, len(origin))
    for _, v := range origin {
        if v == zero { continue }
        if _, ok := seen[v]; ok { continue }
        seen[v] = struct{}{}
        result = append(result, v)
    }
    slices.Sort(result)
    return slices.Clone(result)
}
```

---

## 2. DAO Batch Query

```go
func (d *Dao) GetUsers(ctx context.Context, ids []int64) (map[int64]*ent.User, error) {
    ids = conv.UniqueSortedNonZero(ids)
    if len(ids) == 0 {
        return map[int64]*ent.User{}, nil
    }

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

---

## 3. Chunked Batch Query

For large ID sets (>500):

```go
func (d *Dao) GetUsersChunked(ctx context.Context, ids []int64) (map[int64]*ent.User, error) {
    ids = conv.UniqueSortedNonZero(ids)
    out := make(map[int64]*ent.User, len(ids))
    if len(ids) == 0 {
        return out, nil
    }

    const chunkSize = 800
    for start := 0; start < len(ids); start += chunkSize {
        end := start + chunkSize
        if end > len(ids) {
            end = len(ids)
        }

        rows, err := d.User.Query().Where(user.IDIn(ids[start:end]...)).All(ctx)
        if err != nil {
            return nil, err
        }
        for _, row := range rows {
            out[row.ID] = row
        }
    }
    return out, nil
}
```

---

## 4. Service Pagination

```go
query := s.db.Admin.Query()
count, err := query.Clone().Count(ctx)
if err != nil {
    return nil, err
}

totalPage, pageSize := conv.Page(count, int(req.PageSize))
offset := pageSize * int(req.Page)
if req.Page > 0 {
    offset = pageSize * int(req.Page-1)
}

rows, err := query.Clone().
    Limit(pageSize).Offset(offset).
    Order(admin.ByID(sql.OrderDesc())).
    All(ctx)
```

---

## 5. Render Post-Processing

```go
val, _ := entmap.ToProtoUser(value, func(source *ent.User, target *sharedv1.User) error {
    target.Avatar = r.storage.GenerateURL(source.Avatar)
    return nil
})
```

---

## 6. Bind Registration

Register in `cmd/tools/bind/main.go#createFilesConf`:

```go
conf.NewEntity(
    ent.Example{},
    entpb.Example{},
    []any{ent.ExampleCreate{}, ent.ExampleUpdateOne{}},
    conf.CheckOptions(bindMode,
        conf.WithIgnoreFields(example.FieldCreatedAt, example.FieldUpdatedAt)),
)
```

---

## 7. Sensitive Field Handling

Bind mode — ignore system fields:
```go
conf.WithIgnoreFields(admin.FieldCreatedAt, admin.FieldUpdatedAt)
```

Non-bind mode — mask sensitive fields:
```go
conf.WithIgnoreFields(admin.FieldPassword)
// Or in render:
target.Password = ""
```

---

## New Entity Checklist

1. Add Ent schema fields/indexes
2. Register in `createFilesConf`
3. Add `WithIgnoreFields` for timestamps/sensitive fields
4. Add DAO batch helpers using `IDIn(...)`
5. Verify render mapper consumes generated bind
6. Run `make gen/proto`
7. Validate generated diff consumed
