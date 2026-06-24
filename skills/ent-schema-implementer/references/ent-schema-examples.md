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

---

## Example 3: Typed JSON `extra` field

For an entity whose brief lists a few stable sub-keys but flags the structure as volatile, use a typed JSON struct. The struct lives in the domain package, not in `ent/schema`.

```go
// internal/domain/order/extra.go
package order

type Extra struct {
    MarketingTag string   `json:"marketing_tag,omitempty"`
    CampaignID   string   `json:"campaign_id,omitempty"`
    Experiment   string   `json:"experiment,omitempty"`
    Labels       []string `json:"labels,omitempty"`
}
```

```go
// ent/schema/order.go
import (
    domainorder "yourapp/internal/domain/order"
)

field.JSON("extra", domainorder.Extra{}).
    Optional().
    Comment("Low-frequency, non-core extensions. Promote stable sub-keys to real columns.").
    Annotations(entproto.Field(7)),
```

If the brief says "structure is unknown / passthrough", swap the struct for `json.RawMessage{}`. Do **not** use `field.Any` as the default.

---

## Example 4: Extension entity (one-to-one off a hot table)

When the design brief splits volatile module attributes into an extension entity so the hot main table doesn't churn:

```go
// ent/schema/order.go
func (Order) Edges() []ent.Edge {
    return []ent.Edge{
        edge.To("extension", OrderExtension.Type).Unique(),
    }
}
```

```go
// ent/schema/order_extension.go
type OrderExtension struct{ ent.Schema }

func (OrderExtension) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (OrderExtension) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        field.Int64("order_id").Unique().Annotations(entproto.Field(2)),
        field.JSON("marketing", domainorder.MarketingExtra{}).
            Optional().
            Annotations(entproto.Field(3)),
        field.JSON("risk", domainorder.RiskExtra{}).
            Optional().
            Annotations(entproto.Field(4)),
    }
}

func (OrderExtension) Edges() []ent.Edge {
    return []ent.Edge{
        edge.From("order", Order.Type).
            Ref("extension").
            Field("order_id").
            Unique().
            Required(),
    }
}
```

Use this only when the brief explicitly calls for an extension entity. Don't speculate one into existence to "leave room".

---

## Example 5: Deprecated field

A field being deprecated stays in the schema until the migration that drops it ships. Mark it; do not delete it.

```go
field.String("old_tag").
    Optional().
    Nillable().
    Comment("deprecated: use extra.marketing_tag instead").
    Annotations(entproto.Field(8)),
```

If the deprecated value is a JSON sub-key, mark it in the struct so call sites get a `Deprecated:` warning:

```go
type Extra struct {
    // Deprecated: use MarketingTag instead.
    OldTag       string `json:"old_tag,omitempty"`
    MarketingTag string `json:"marketing_tag,omitempty"`
}
```

The proto field number must not be reused or shifted while the field is in deprecation stages — keep it stable until the column is physically dropped.

---

## Example 6: Custom-fields model (`custom_field_def` + `custom_field_value`)

Only when the brief calls for a dynamic field model — typically SaaS custom fields, dynamic forms, surveys, or per-tenant attributes. Never for core transactional fields.

```go
type CustomFieldDef struct{ ent.Schema }

func (CustomFieldDef) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (CustomFieldDef) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        field.String("biz_type").Annotations(entproto.Field(2)),
        field.String("field_key").Annotations(entproto.Field(3)),
        field.String("field_name").Annotations(entproto.Field(4)),
        field.String("field_type").Annotations(entproto.Field(5)),
        field.Bool("required").Default(false).Annotations(entproto.Field(6)),
        field.Int("status").Default(1).Annotations(entproto.Field(7)),
        field.JSON("options", json.RawMessage{}).
            Optional().
            Comment("Enum choices, validation rules, etc.").
            Annotations(entproto.Field(8)),
    }
}

func (CustomFieldDef) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("biz_type", "field_key").Unique(),
    }
}
```

```go
type CustomFieldValue struct{ ent.Schema }

func (CustomFieldValue) Annotations() []schema.Annotation {
    return []schema.Annotation{entproto.Message()}
}

func (CustomFieldValue) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("id").Annotations(entproto.Field(1)),
        field.String("biz_type").Annotations(entproto.Field(2)),
        field.Int64("biz_id").Annotations(entproto.Field(3)),
        field.String("field_key").Annotations(entproto.Field(4)),
        field.String("value").Optional().Annotations(entproto.Field(5)),
        field.JSON("json_value", json.RawMessage{}).
            Optional().
            Annotations(entproto.Field(6)),
    }
}

func (CustomFieldValue) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("biz_type", "biz_id"),
        index.Fields("biz_type", "field_key"),
        index.Fields("biz_type", "biz_id", "field_key").Unique(),
    }
}
```
