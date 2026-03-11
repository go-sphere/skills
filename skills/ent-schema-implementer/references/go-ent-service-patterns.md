# Go + Ent Service Patterns

DAO and integration patterns for go-sphere projects.

## 1. ID De-duplication

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

## 3. Bind Registration

Register new entities in `cmd/tools/bind/main.go#createFilesConf`:

```go
conf.NewEntity(
    ent.Example{},
    entpb.Example{},
    []any{ent.ExampleCreate{}, ent.ExampleUpdateOne{}},
    conf.CheckOptions(bindMode,
        conf.WithIgnoreFields(example.FieldCreatedAt, example.FieldUpdatedAt)),
)
```

## 4. Sensitive Field Handling

Bind mode:

```go
conf.WithIgnoreFields(admin.FieldCreatedAt, admin.FieldUpdatedAt)
```

Render masking:

```go
target.Password = ""
```
