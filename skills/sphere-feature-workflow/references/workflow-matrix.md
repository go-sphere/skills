# Workflow Matrix (sphere-layout)

## Quick Decision Guide

| Question | Answer | Workflow |
|----------|--------|----------|
| Changes external API/validation/error contract? | Yes | **Contract-first** |
| Changes persisted fields/relations/indexes? | Yes | **Schema-first** |
| Only changes orchestration/query/render? | Yes | **Service-only** |
| Multiple "yes" answers? | - | **Cross-layer** |

> **Tip**: Start with `Contract-first` for Cross-layer unless the primary change is clearly schema-related.

---

## 1. Preflight Classification

Run these checks **before** editing any files:

1. **API/Contract impact?**
   - Changes to route shape, validation, error contracts → `Contract-first`

2. **Schema/Database impact?**
   - Changes to fields, relations, indexes, queries → `Schema-first`

3. **Service-only?**
   - Orchestration/query/render changes only, no contract/schema → `Service-only`

4. **Cross-layer?**
   - Two or more "yes" → pick entry point, complete all layers

## 2. Change Type → Workflow Mapping

| Change Type | Start Point | Source of Truth | Workflow |
|-------------|-------------|-----------------|----------|
| API contract | `proto/**` | `.proto` files | **Contract-first** |
| DB model | `internal/pkg/database/schema/**` | Ent schema files | **Schema-first** |
| Business behavior only | `internal/service/**` / `internal/pkg/dao/**` | Service/DAO code | **Service-only** |
| Cross-layer | `proto/**` + `schema/**` + service | Proto + schema | **Cross-layer** |

## 3. Minimal File Touchpoints

### Contract-first
1. `proto/**` - service/rpc/message/error changes
2. `internal/service/**` - implement generated server interface
3. `internal/pkg/dao/**` - query/mutation for contract behavior
4. `internal/pkg/render/**` non-generated - response shaping, error mapping

### Schema-first
1. `internal/pkg/database/schema/**` - fields/indexes/relations
2. `cmd/tools/bind/main.go#createFilesConf` - bind/map registration
3. `internal/service/**` + `dao/**` + `render/**` - consume generated types
4. `proto/**` (optional) - if external contract needs new fields

### Service-only
1. `internal/service/**` - API behavior orchestration
2. `internal/pkg/dao/**` - query composition
3. `internal/pkg/render/**` non-generated - masking, shaping
4. `internal/biz/**` (optional) - shared domain orchestration

## 4. Command Policy

| Trigger | Command | Expected Result |
|---------|---------|-----------------|
| Proto/schema change | `make gen/proto` | Ent/proto/bind/map synchronized |
| HTTP/OpenAPI impact | `make gen/docs` | Swagger refreshed |
| DI signature change | `make gen/wire` | `wire_gen.go` updated |
| Validation | `go test ./...` | Behavior safety check |

## 5. Delivery Gate (All Must Pass)

- [ ] Workflow type explicitly stated
- [ ] Source-of-truth edits complete and consistent
- [ ] Required generation commands ran successfully
- [ ] Generated changes consumed by service/dao/render
- [ ] NO manual edits in generated files
- [ ] Validation results and risks reported

**If any gate fails → output `Blocking Issues` + fix plan**
