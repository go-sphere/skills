# Change Checklist (go-sphere layouts)

## Quick Checklist

### Before Starting
- [ ] `.sphere/layout.json`, `AGENTS.md`, `docs/LAYOUT_CONTRACT.md` read
- [ ] Layout variant identified (standard / simple / bun / telegram / pre-contract)
- [ ] Every target path classified (generated / layout_owned / mixed / project_owned)
- [ ] Workflow classified (Contract/Schema/Service/Cross)
- [ ] Service namespace + route ownership confirmed
- [ ] Proto + schema impact confirmed
- [ ] Backward compatibility identified
- [ ] Existing packages checked for reuse

### During Change
- [ ] Source-of-truth edited first
- [ ] Business errors stay in owning proto
- [ ] `cmd/tools/gen/entcrud/main.go` updated if schema changed
- [ ] `WithIgnoreFields` covers timestamps/soft-delete/secrets
- [ ] DAO query shape avoids N+1
- [ ] NO edits to `entbind/**` or `entmap/**`
- [ ] New product code lives in `project_owned` paths
- [ ] Any `layout_owned` / `mixed` edit justified in writing

### After Change
- [ ] Generation commands run
- [ ] `make test` passes, `make check` clean
- [ ] No generated files manually edited
- [ ] Reuse decision documented
- [ ] Ownership classification of edited paths reported
- [ ] Compatibility impact reported

---

## 1. Pre-Change Checklist

- [ ] Read `.sphere/layout.json`, `AGENTS.md`, and `docs/LAYOUT_CONTRACT.md`
- [ ] Identify the layout variant and its capabilities
- [ ] Classify every target path against the ownership patterns
- [ ] Classify workflow (Contract/Schema/Service/Cross)
- [ ] Confirm service namespace and route prefix ownership
- [ ] Confirm proto + schema layer impact
- [ ] Identify backward compatibility constraints
- [ ] Check existing Sphere packages first

## 2. In-Change Checklist

- [ ] Modify source-of-truth files first
- [ ] Keep business errors in owning proto unless sharing required
- [ ] Update `cmd/tools/gen/entcrud/main.go` if schema changes
- [ ] Review `WithIgnoreFields` for timestamps, soft-delete, secrets
- [ ] Align DAO query shape with response (avoid N+1)
- [ ] Reuse existing Sphere packages before new abstractions
- [ ] DO NOT edit `entbind/**` or `entmap/**`
- [ ] Place new contracts/logic in `project_owned` domain paths
- [ ] Preserve both layout wiring and project additions in `mixed` files
- [ ] Do not add provider SDKs to a layout that does not declare that capability

## 3. Workflow-Specific Checklist

### Contract-first
- [ ] `proto/**` complete and consistent
- [ ] `make gen/proto` ran
- [ ] Service/DAO/render consumes generated changes
- [ ] `make gen/docs` if HTTP changed

### Schema-first
- [ ] Schema field/relation/index complete
- [ ] `cmd/tools/gen/entcrud/main.go` updated
- [ ] `WithIgnoreFields` covers sensitive fields
- [ ] `make gen/proto` ran, downstream aligned

### Service-only
- [ ] No proto/schema changes introduced
- [ ] Changes in non-generated files only
- [ ] Permission/transaction/idempotency validated

## 4. Post-Change Checklist

- [ ] Generation commands run (gen/proto, gen/docs, gen/wire)
- [ ] Tests pass (`make test`)
- [ ] Delivery gate clean (`make check`; plus `make build` if the project ships a binary)
- [ ] Tracked generated files show no unexplained drift
- [ ] NO manual edits in generated files
- [ ] Reuse decision documented
- [ ] Ownership classification reported for every edited path
- [ ] Compatibility + risks reported

## 5. Common Blocking Issues

| Issue | Fix |
|-------|-----|
| Workflow not classified | Classify before proceeding |
| Schema changed, bind/map not | Register the entity in `cmd/tools/gen/entcrud/main.go` |
| Proto changed, no gen | Run `make gen/proto` |
| Generated diffs not consumed | Update service/dao/render |
| Sensitive fields exposed | Add to `WithIgnoreFields` |
| Route conflicts | Check route prefixes |
| Product logic in a `layout_owned` file | Move it to a `project_owned` domain path |
| Bot/Telegram code added to the standard layout | Use the Telegram layout, or keep it in project-owned paths with its own proto contract |
| Ent guidance applied to the simple or bun layout | Re-read the layout capabilities; those layouts have no Ent schema layer |

**When blocking → output `Blocking Issues` + fix plan**
