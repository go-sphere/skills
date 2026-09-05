# Workflow Matrix (go-sphere layouts)

Paths below use the standard layout. The simple layout has no Ent/schema layer
and the bun layout uses Bun instead of Ent — confirm the variant via
[layout-contract-and-ownership.md](layout-contract-and-ownership.md) before applying
a Schema-first workflow.

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

0. **Ownership check (first, always)**
   - Read `.sphere/layout.json`, `AGENTS.md`, `docs/LAYOUT_CONTRACT.md`
   - Identify the layout variant and classify every path you plan to touch
   - A `layout_owned` or `mixed` target changes the plan, not just the diff

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
2. `cmd/tools/gen/entcrud/main.go` - bind/map registration (`conf.NewFilesConf`)
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
| Validation | `make test` | Behavior safety check |
| Delivery gate | `make check` | Dependency, format, lint, and test state clean |
| Binary-delivering projects | `make build` | Project still builds |

## 5. Delivery Gate (All Must Pass)

- [ ] Layout variant identified and edited paths classified
- [ ] Every `layout_owned` / `mixed` edit justified
- [ ] Workflow type explicitly stated
- [ ] Source-of-truth edits complete and consistent
- [ ] Required generation commands ran successfully
- [ ] Generated changes consumed by service/dao/render
- [ ] NO manual edits in generated files
- [ ] Validation results and risks reported

**If any gate fails → output `Blocking Issues` + fix plan**
