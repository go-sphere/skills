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

## 3. Execution Sequences

Run the sequence for the workflow you classified. Do not reorder the steps.

### Contract-first

1. Classify every target path against `.sphere/layout.json`.
2. Edit `proto/**`: service, rpc, message, HTTP annotation, validation, error changes.
3. Run `make gen/proto`.
4. Resolve the generated impact in `internal/service/**` (implement the generated server
   interface), `internal/pkg/dao/**` (query and mutation support), and non-generated files under
   `internal/pkg/render/**` (response shaping, error mapping).
5. Run `make gen/docs` when the HTTP contract or docs changed.
6. Run `make test`, then `make check` before delivery.
7. Verify every generated diff is consumed.

### Schema-first

1. Classify every target path against `.sphere/layout.json`. `schema/**` and `cmd/tools/**` are
   commonly `mixed` or `layout_owned`.
2. Edit `internal/pkg/database/schema/**`: fields, relations, indexes.
3. Verify bind/map registration in `cmd/tools/gen/entcrud/main.go` (`conf.NewFilesConf`).
4. Review `WithIgnoreFields` for sensitive and system fields.
5. Run `make gen/proto`.
6. Resolve the impact in `internal/service/**`, `internal/pkg/dao/**`, and
   `internal/pkg/render/**`. Extend `proto/**` only if the external contract needs new fields.
7. Run `make test`, then `make check` before delivery.
8. Verify query paths align with the index intent.

### Service-only

1. Edit only non-generated code: `internal/service/**` (orchestration),
   `internal/pkg/dao/**` (query composition), non-generated `internal/pkg/render/**` (masking,
   shaping), and optionally `internal/biz/**` (shared domain orchestration).
2. Keep proto and schema stable.
3. Run `make test`, then `make check` before delivery.
4. Verify there is no API regression.

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
