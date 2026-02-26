# Ent Schema Best-Practice Examples (sphere-layout)

Use these examples as templates. They focus on:
- business comments on schema/fields
- explicit optional/constraint decisions
- weak relation IDs (`xxx_id`)
- query-driven indexes
- default policy: do not define `id` manually in schema
- enum fields use Ent native enum
- prefer array fields by default; avoid JSON unless no typed alternative works

---

## Example 1: Order (default ID managed by ent codegen)

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
            Comment("下单用户ID（弱关联，不强制外键）"),

        field.String("order_no").
            NotEmpty().
            Unique().
            Comment("订单号，全局唯一"),

        field.Enum("status").
            Values("pending", "paid", "canceled", "done").
            Default("pending").
            Comment("订单状态"),

        field.Int64("paid_at").
            Optional().
            Nillable().
            Comment("支付时间，未支付时为空"),

        field.String("user_name_snapshot").
            Default("").
            Comment("用户名称快照，避免历史展示受用户改名影响"),

        field.Strings("tags").
            Optional().
            Default([]string{}).
            Comment("订单标签（数据库支持数组类型时使用）"),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Comment("创建时间（秒）"),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Comment("更新时间（秒）"),
    }
}

func (Order) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("user_id", "status", "created_at"),
        index.Fields("order_no").Unique(),
    }
}
```

### 与本仓库生成链路的关系

- `id` 默认不手写，优先复用 `cmd/tools/ent/main.go` 的统一 `IDType` 配置。
- 若新增 `Order` 实体，必须在 `cmd/tools/bind/main.go#createFilesConf` 注册 `conf.NewEntity(...)`。
- 生成后必须检查 `entpb/proto/bind/map` 变化是否被 render/service 消费。

---

## Example 2: OrderItem (weak relation IDs + array candidates)

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
        field.Int64("order_id").Comment("订单ID"),
        field.Int64("product_id").Comment("商品ID"),

        field.String("product_title_snapshot").
            NotEmpty().
            Comment("商品标题快照"),

        field.Int64("price_snapshot").
            NonNegative().
            Comment("下单时商品价格快照（分）"),

        field.Int32("quantity").
            Positive().
            Default(1).
            Comment("购买数量"),

        field.Strings("coupon_codes").
            Optional().
            Default([]string{}).
            Comment("命中的优惠券编码列表（数据库支持数组类型时使用）"),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Comment("创建时间（秒）"),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Comment("更新时间（秒）"),
    }
}

func (OrderItem) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("order_id"),
        index.Fields("product_id"),
    }
}
```

### 与本仓库生成链路的关系

- 优先弱关联 ID 字段，不强制 edge/join。
- 新实体接入后，必须补 DAO 批量查询 helper 与 service 映射消费点。
- 如 `coupon_codes` 走数组，需在目标 DB 方言与迁移链路下确认可用性。

---

## Example 3: CouponGrant (enum + soft-delete)

```go
package schema

import (
    "time"

    "entgo.io/ent"
    "entgo.io/ent/schema/field"
    "entgo.io/ent/schema/index"
)

// CouponGrant represents a coupon assignment to user.
type CouponGrant struct {
    ent.Schema
}

func (CouponGrant) Fields() []ent.Field {
    return []ent.Field{
        field.Int64("coupon_id").Comment("优惠券ID"),
        field.Int64("user_id").Comment("用户ID"),

        field.Enum("status").
            Values("unused", "used", "expired").
            Default("unused").
            Comment("状态"),

        field.Int64("used_at").
            Optional().
            Nillable().
            Comment("使用时间，未使用时为空"),

        field.Int64("deleted_at").
            Optional().
            Nillable().
            Comment("软删时间，为空表示未删除"),

        field.Int64("created_at").
            Immutable().
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            Comment("创建时间（秒）"),

        field.Int64("updated_at").
            DefaultFunc(func() int64 { return time.Now().Unix() }).
            UpdateDefault(func() int64 { return time.Now().Unix() }).
            Comment("更新时间（秒）"),
    }
}

func (CouponGrant) Indexes() []ent.Index {
    return []ent.Index{
        index.Fields("coupon_id", "user_id").Unique(),
        index.Fields("user_id", "status", "created_at"),
    }
}
```

### 与本仓库生成链路的关系

- 状态字段必须使用 `field.Enum`，避免散落 magic number。
- 若涉及敏感字段，需在 bind/render 层补 `WithIgnoreFields` 与脱敏处理说明。
- 生成后必须验证 bind/map 变更已被 API/Dash 服务消费。

---

## 何时必须手写 `id`

默认不手写 `id`。仅在业务明确要求非默认主键策略时手写，并额外说明：
- 为什么 generator-managed ID 不满足需求。
- 对 bind/proto 类型与调用方兼容性的影响。

```go
field.String("id").
    Unique().
    Immutable().
    Comment("业务侧自定义主键（例如外部系统自然键）")
```

---

## 数组字段可用性判定流程

1. DB 方言与迁移链路确认支持数组字段：使用 `field.Strings/field.Ints/field.Int64s`。
2. 若不支持或跨库不可移植：优先 relation-entity 或 join table。
3. 若结构仍无法 typed 表达：最后才允许 JSON，并在方案中写明理由。

---

## Post-Change Reminder

After schema changes, run:

```bash
make gen/proto
go test ./...
```

Then verify generated diff is fully consumed.
