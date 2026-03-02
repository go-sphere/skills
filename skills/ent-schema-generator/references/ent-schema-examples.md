# Ent Schema Best-Practice Examples (sphere-layout)

Use these examples as templates. They emphasize:
- business comments on schema and key fields
- explicit optional/constraint decisions
- weak relation IDs (`xxx_id`)
- query-driven indexes
- **entproto annotations** for all schemas and fields (REQUIRED)
- enum fields with Ent native `field.Enum` + entproto.Enum mapping
- typed fields first (including arrays when dialect support is confirmed)

> **IMPORTANT**: All schemas MUST include entproto annotations. See Section 7 for entproto requirements.

## Table of Contents

1. Example 1: Order (generator-managed ID)
2. Example 2: OrderItem (weak relation IDs + array candidates)
3. Example 3: CouponGrant (enum + soft-delete)
4. When to Define `id` Manually
5. Array Field Support Decision Flow
6. EntProto Full Example (User with all annotation patterns)
7. Post-Change Reminder

---

## 1. Example 1: Order (generator-managed ID)

```go
package schema

import (
    "time"

    "entgo.io/ent"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

// Order stores purchase order snapshots and status lifecycle.
type Order struct {
    ent.Schema
}

func (Order) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("user_id").
            Comment("Order owner user ID (weak relation, no hard foreign key)"),

        field.String("order_no").
            NotEmpty().
            Unique().
            Comment("Global unique order number"),

        field.Enum("status").
            Values("pending", "paid", "canceled", "done").
            Default("pending").
            Comment("Order lifecycle status"),

        field.Int64("paid_at").
            Optional().
            Nillable().
            Comment("Payment timestamp; nil when unpaid"),

        field.String("user_name_snapshot").
            Default("").
            Comment("User name snapshot for historical consistency"),

        field.Strings("tags").
            Optional().
            Default([]string{}).
            Comment("Order tags (use only when target DB supports arrays)"),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Comment("Creation time in Unix seconds"),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Comment("Last update time in Unix seconds"),
    }
}

func (Order) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("user_id", "status", "created_at"),
        index.Fields("order_no").Unique(),
    }
}
```

### Repository integration notes

- Keep `id` generator-managed by default through centralized ent tool config (`cmd/tools/ent/main.go`).
- If `Order` is introduced, register it in `cmd/tools/bind/main.go#createFilesConf`.
- After generation, ensure `entpb/proto/bind/map` changes are consumed by render and service code.

---

## 2. Example 2: OrderItem (weak relation IDs + array candidates)

```go
package schema

import (
    "time"

    "entgo.io/ent"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

// OrderItem stores order line snapshots.
type OrderItem struct {
    ent.Schema
}

func (OrderItem) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("order_id").Comment("Order ID"),
        field.Int64("product_id").Comment("Product ID"),

        field.String("product_title_snapshot").
            NotEmpty().
            Comment("Product title snapshot"),

        field.Int64("price_snapshot").
            NonNegative().
            Comment("Unit price snapshot at order time in cents"),

        field.Int32("quantity").
            Positive().
            Default(1).
            Comment("Purchased quantity"),

        field.Strings("coupon_codes").
            Optional().
            Default([]string{}).
            Comment("Applied coupon codes (only when array is dialect-safe)"),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Comment("Creation time in Unix seconds"),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Comment("Last update time in Unix seconds"),
    }
}

func (OrderItem) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("order_id"),
        index.Fields("product_id"),
    }
}
```

### Repository integration notes

- Prefer weak relation IDs; do not force edge/join modeling by default.
- If a new entity is introduced, add DAO batch helpers and service mapping consumption points.
- If arrays are used (`coupon_codes`), confirm target dialect and migration support first.

---

## 3. Example 3: CouponGrant (enum + soft-delete)

```go
package schema

import (
    "time"

    "entgo.io/ent"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

// CouponGrant represents a coupon assignment to a user.
type CouponGrant struct {
    ent.Schema
}

func (CouponGrant) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("coupon_id").Comment("Coupon ID"),
        field.Int64("user_id").Comment("User ID"),

        field.Enum("status").
            Values("unused", "used", "expired").
            Default("unused").
            Comment("Grant status"),

        field.Int64("used_at").
            Optional().
            Nillable().
            Comment("Usage timestamp; nil when unused"),

        field.Int64("deleted_at").
            Optional().
            Nillable().
            Comment("Soft-delete timestamp; nil when active"),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Comment("Creation time in Unix seconds"),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Comment("Last update time in Unix seconds"),
    }
}

func (CouponGrant) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("coupon_id", "user_id").Unique(),
        index.Fields("user_id", "status", "created_at"),
    }
}
```

### Repository integration notes

- Use `field.Enum` for status fields to avoid scattered magic values.
- For sensitive fields, include `WithIgnoreFields` and masking notes in bind/render planning.
- Verify generated bind/map changes are consumed by API and dashboard service code.

---

## 4. When to Define `id` Manually

Default behavior is generator-managed `id`. Define `id` manually only when business
requirements explicitly require a non-default primary key strategy.

Always explain:
- why generator-managed ID is insufficient
- compatibility impact on bind/proto and call sites

```go
field.String("id").
    Unique().
    Immutable().
    Comment("Business-defined primary key, for example external natural key")
```

---

## 5. Array Field Support Decision Flow

1. Confirm array support in target DB dialect and migration chain.
2. If supported, use typed arrays (`field.Strings/field.Ints/field.Int64s`) where appropriate.
3. If unsupported or non-portable, prefer relation-entity or join table.
4. Use JSON only as the final fallback, and document why typed models are not viable.

---

## 6. EntProto Full Example (User with all annotation patterns)

This example demonstrates all entproto annotation patterns:

```go
package schema

import (
    "time"

    "entgo.io/contrib/entproto"
    "entgo.io/ent"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

// User represents a system user entity.
type User struct {
    ent.Schema
}

func (User) Annotations() []schema.Annotation {
    return []schema.Annotation{
        entproto.Message(),
    }
}

func (User) Fields() []ent.Field {
    return []ent.Field{
        // Primary key MUST use field number 1
        field.Int64("id").
            Annotations(entproto.Field(1)),

        field.String("name").
            NotEmpty().
            Annotations(entproto.Field(2)),

        field.String("email").
            Unique().
            NotEmpty().
            Annotations(entproto.Field(3)),

        // Enum field with entproto.Enum mapping
        field.Enum("status").
            Values("active", "inactive", "suspended").
            Default("active").
            Annotations(
                entproto.Field(4),
                entproto.Enum(map[string]int32{
                    "active":    0,
                    "inactive":  1,
                    "suspended": 2,
                }),
            ),

        field.Int64("role_id").
            Default(0).
            Annotations(entproto.Field(5)),

        field.Strings("tags").
            Optional().
            Default([]string{}).
            Annotations(entproto.Field(6)),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Annotations(entproto.Field(7)),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Annotations(entproto.Field(8)),
    }
}

func (User) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("email").Unique(),
        index.Fields("status", "created_at"),
    }
}
```

### Key entproto Patterns

| Pattern | Example |
|---------|---------|
| Schema annotation | `entproto.Message()` in `Annotations()` |
| Primary key | `entproto.Field(1)` |
| Regular field | `entproto.Field(2)`, `entproto.Field(3)` |
| Enum field | `entproto.Field(n)` + `entproto.Enum(map[string]int32{...})` |
| Import | `"entgo.io/contrib/entproto"` |

### Enum Value Mapping Rules

- Always start enum mapping from 0
- Use meaningful numeric values that can be extended later
- Document the mapping in schema comments

```go
// Good: starts from 0, extensible
entproto.Enum(map[string]int32{
    "pending":  0,
    "active":   1,
    "done":     2,
})

// Avoid: gap in numbering
entproto.Enum(map[string]int32{
    "pending":  0,
    "active":   2,  // Bad: gap
    "done":     3,
})
```

---

## 7. Post-Change Reminder

After schema changes, run:

```bash
make gen/proto
go test ./...
```

Then verify:
1. All fields have `entproto.Field(n)` annotations
2. Primary key uses field number 1
3. Enum fields have `entproto.Enum` mapping
4. Schema has `entproto.Message()` annotation
