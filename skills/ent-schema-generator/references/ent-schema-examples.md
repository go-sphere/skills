# Ent Schema Examples (sphere-layout)

Code examples with entproto annotations. All schemas MUST use these patterns.

## Quick Reference

| Component | Required Pattern |
|-----------|------------------|
| Schema | `entproto.Message()` in `Annotations()` |
| Primary Key | `field.Int64("id").Annotations(entproto.Field(1))` |
| Regular Field | `entproto.Field(n)` — sequential numbers |
| Enum Field | `entproto.Field(n)` + `entproto.Enum(map[string]int32{...})` |
| Enum Values | Must start from **1** (0 is reserved) |

---

## Example 1: Order (Generator-Managed ID)

```go
package schema

import (
    "time"

    "entgo.io/contrib/entproto"
    "entgo.io/ent"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

// Order stores purchase order snapshots and lifecycle.
type Order struct{ ent.Schema }

func (Order) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (Order) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),

        field.Int64("user_id").
            Comment("Owner user ID (weak relation)").
            Annotations(entproto.Field(2)),

        field.String("order_no").
            NotEmpty().Unique().
            Annotations(entproto.Field(3)),

        field.Enum("status").
            Values("pending", "paid", "canceled", "done").
            Default("pending").
            Annotations(
                entproto.Field(4),
                entproto.Enum(map[string]int32{
                    "pending":  1, "paid": 2, "canceled": 3, "done": 4,
                }),
            ),

        field.Int64("paid_at").Default(0).Annotations(entproto.Field(5)),
        field.String("user_name_snapshot").Default("").Annotations(entproto.Field(6)),
        field.Strings("tags").Optional().Default([]string{}).Annotations(entproto.Field(7)),

        field.Int64("created_at").
            Immutable().DefaultFunc(func() int64 { return time.Now().Unix() }).
            Annotations(entproto.Field(8)),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Annotations(entproto.Field(9)),
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

## Example 2: OrderItem (Weak Relation)

```go
package schema

import (
    "time"

    "entgo.io/contrib/entproto"
    "entgo.io/ent"
    "entgo.io/ent/schema/field"
)

type OrderItem struct{ ent.Schema }

func (OrderItem) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (OrderItem) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        field.Int64("order_id").Annotations(entproto.Field(2)),
        field.Int64("product_id").Annotations(entproto.Field(3)),
        field.String("product_title_snapshot").NotEmpty().Annotations(entproto.Field(4)),
        field.Int64("price_snapshot").NonNegative().Annotations(entproto.Field(5)),
        field.Int32("quantity").Positive().Default(1).Annotations(entproto.Field(6)),
        field.Strings("coupon_codes").Optional().Default([]string{}).Annotations(entproto.Field(7)),
        field.Int64("created_at").Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).Annotations(entproto.Field(8)),
        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).Annotations(entproto.Field(9)),
    }
}
```

---

## Example 3: CouponGrant (Enum + Soft-Delete)

```go
package schema

import (
    "time"

    "entgo.io/contrib/entproto"
    "entgo.io/ent"
    "entgo.io/ent/schema/field"
)

type CouponGrant struct{ ent.Schema }

func (CouponGrant) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (CouponGrant) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        field.Int64("coupon_id").Annotations(entproto.Field(2)),
        field.Int64("user_id").Annotations(entproto.Field(3)),
        field.Enum("status").
            Values("unused", "used", "expired").
            Default("unused").
            Annotations(
                entproto.Field(4),
                entproto.Enum(map[string]int32{
                    "unused":  1, "used": 2, "expired": 3,
                }),
            ),
        field.Int64("used_at").Default(0).Annotations(entproto.Field(5)),
        field.Int64("deleted_at").Default(0).Annotations(entproto.Field(6)), // soft-delete
        field.Int64("created_at").Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).Annotations(entproto.Field(7)),
        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).Annotations(entproto.Field(8)),
    }
}
```

---

## Manual ID Example

Only define manual ID when business explicitly requires:

```go
field.String("id").
    Unique().Immutable().
    Annotations(entproto.Field(1)).
    Comment("External natural key (e.g., ISBN, SKU)")
```

---

## Array Fields

Use `field.Strings/field.Ints/field.Int64s` for typed arrays:

```go
field.Strings("tags").
    Optional().Default([]string{}).
    Annotations(entproto.Field(n))

field.Int64s("product_ids").
    Optional().Default([]int64{}).
    Annotations(entproto.Field(n))
```

**Note**: Confirm target DB supports arrays (PostgreSQL: yes, MySQL: limited)

---

## Enum Mapping Rules

```
Values MUST start from 1 — 0 is reserved for "unknown"

Good:  {"pending": 1, "active": 2, "done": 3}
Bad:   {"pending": 0, "active": 1, "done": 2}   // 0 is reserved!
```

---

## Post-Change Validation

```bash
make gen/proto
go test ./...
```

Verify:
- [ ] All fields have `entproto.Field(n)`
- [ ] Primary key uses field number 1
- [ ] Schema has `entproto.Message()`
- [ ] Enum fields have `entproto.Enum` mapping
