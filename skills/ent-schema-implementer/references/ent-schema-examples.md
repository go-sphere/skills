# Ent Schema Examples

Code examples with entproto annotations. Use these patterns when implementing Ent schemas.

## Quick Reference

| Component | Required Pattern |
|-----------|------------------|
| Schema | `entproto.Message()` in `Annotations()` |
| Primary Key | `field.Int64("id").Annotations(entproto.Field(1))` |
| Regular Field | `entproto.Field(n)` with sequential numbers |
| Enum Field | `entproto.Field(n)` + `entproto.Enum(map[string]int32{...})` |
| Enum Values | Start from `1` |

---

## Example 1: Order

```go
package schema

import (
    "time"

    "entgo.io/contrib/entproto"
    "entgo.io/ent"
    "entgo.io/ent/schema"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

type Order struct{ ent.Schema }

func (Order) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (Order) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        field.Int64("user_id").
            Comment("Owner user ID").
            Annotations(entproto.Field(2)),
        field.String("order_no").
            NotEmpty().
            Unique().
            Annotations(entproto.Field(3)),
        field.Enum("status").
            Values("pending", "paid", "canceled", "done").
            Default("pending").
            Annotations(
                entproto.Field(4),
                entproto.Enum(map[string]int32{
                    "pending": 1,
                    "paid": 2,
                    "canceled": 3,
                    "done": 4,
                }),
            ),
        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Annotations(entproto.Field(5)),
        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Annotations(entproto.Field(6)),
    }
}

func (Order) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("user_id", "status", "created_at"),
        index.Fields("order_no").Unique(),
    }
}
```

---

## Example 2: Manual ID

Use manual IDs only when explicitly required by the approved design:

```go
field.String("id").
    Unique().
    Immutable().
    Annotations(entproto.Field(1)).
    Comment("External natural key")
```

---

## Enum Mapping Rule

Good:

```go
entproto.Enum(map[string]int32{
    "pending": 1,
    "active": 2,
    "done": 3,
})
```

Bad:

```go
entproto.Enum(map[string]int32{
    "pending": 0,
    "active": 1,
})
```
