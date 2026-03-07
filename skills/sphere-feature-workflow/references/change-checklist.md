# Change Checklist (sphere-layout)

## Quick Checklist

### Before Starting
- [ ] Workflow classified (Contract/Schema/Service/Cross)
- [ ] Service namespace + route ownership confirmed
- [ ] Proto + schema impact confirmed
- [ ] Backward compatibility identified
- [ ] Existing packages checked for reuse

### During Change
- [ ] Source-of-truth edited first
- [ ] Business errors stay in owning proto
- [ ] `createFilesConf` updated if schema changed
- [ ] `WithIgnoreFields` covers timestamps/soft-delete/secrets
- [ ] DAO query shape avoids N+1
- [ ] NO edits to `entbind/**` or `entmap/**`

### After Change
- [ ] Generation commands run
- [ ] Tests pass
- [ ] No generated files manually edited
- [ ] Reuse decision documented
- [ ] Compatibility impact reported

---

## 1. Pre-Change Checklist

- [ ] Classify workflow (Contract/Schema/Service/Cross)
- [ ] Confirm service namespace and route prefix ownership
- [ ] Confirm proto + schema layer impact
- [ ] Identify backward compatibility constraints
- [ ] Check existing Sphere packages first

## 2. In-Change Checklist

- [ ] Modify source-of-truth files first
- [ ] Keep business errors in owning proto unless sharing required
- [ ] Update `cmd/tools/bind/main.go#createFilesConf` if schema changes
- [ ] Review `WithIgnoreFields` for timestamps, soft-delete, secrets
- [ ] Align DAO query shape with response (avoid N+1)
- [ ] Reuse existing Sphere packages before new abstractions
- [ ] DO NOT edit `entbind/**` or `entmap/**`

## 3. Workflow-Specific Checklist

### Contract-first
- [ ] `proto/**` complete and consistent
- [ ] `make gen/proto` ran
- [ ] Service/DAO/render consumes generated changes
- [ ] `make gen/docs` if HTTP changed

### Schema-first
- [ ] Schema field/relation/index complete
- [ ] `createFilesConf` updated
- [ ] `WithIgnoreFields` covers sensitive fields
- [ ] `make gen/proto` ran, downstream aligned

### Service-only
- [ ] No proto/schema changes introduced
- [ ] Changes in non-generated files only
- [ ] Permission/transaction/idempotency validated

## 4. Post-Change Checklist

- [ ] Generation commands run (gen/proto, gen/docs, gen/wire)
- [ ] Tests pass (`go test ./...`)
- [ ] NO manual edits in generated files
- [ ] Reuse decision documented
- [ ] Compatibility + risks reported

## 5. Common Blocking Issues

| Issue | Fix |
|-------|-----|
| Workflow not classified | Classify before proceeding |
| Schema changed, bind/map not | Update `createFilesConf` |
| Proto changed, no gen | Run `make gen/proto` |
| Generated diffs not consumed | Update service/dao/render |
| Sensitive fields exposed | Add to `WithIgnoreFields` |
| Route conflicts | Check route prefixes |

**When blocking → output `Blocking Issues` + fix plan**
