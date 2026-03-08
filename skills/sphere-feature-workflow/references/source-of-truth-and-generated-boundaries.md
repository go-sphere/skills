# Source of Truth and Generated Boundaries

## Quick Reference

| Category | Editable? | Location |
|----------|------------|----------|
| Proto contracts | ✅ YES | `proto/**` |
| Ent schemas | ✅ YES | `internal/pkg/database/schema/**` |
| Service logic | ✅ YES | `internal/service/**` |
| DAO queries | ✅ YES | `internal/pkg/dao/**` |
| Generated API | ❌ NO | `api/**/*.pb.go`, `api/**/*.sphere.go` |
| Generated Ent | ❌ NO | `internal/pkg/database/ent/**` |
| Generated bind/map | ❌ NO | `internal/pkg/render/entbind/**`, `entmap/**` |
| Wire gen | ❌ NO | `cmd/app/wire_gen.go` |

---

## 1. Editable Source of Truth

**Edit these files directly:**

| Layer | Path | What Goes Here |
|-------|------|----------------|
| API Contract | `proto/**` | Service definitions, RPCs, messages, errors |
| Proto Imports | `proto/**/sphere/*.proto` | Binding, errors, options packages |
| DB Schema | `internal/pkg/database/schema/**` | Ent schema definitions |
| Bind/Map | `cmd/tools/bind/main.go#createFilesConf` | Entity exposure policy |
| Service | `internal/service/**` | Business API implementation |
| DAO | `internal/pkg/dao/**` | Query/mutation orchestration |
| Render | `internal/pkg/render/**` non-generated | Response conversion, masking |

## 2. Generated Outputs (NEVER Edit)

**These are auto-generated - edit the source-of-truth instead:**

| Generated | Path Pattern |
|-----------|-------------|
| Proto Go | `api/**/*.{pb,sphere,errors}.go` |
| Ent code | `internal/pkg/database/ent/**` |
| Bind/Map | `internal/pkg/render/{entbind,entmap}/**` |
| entpb proto | `proto/entpb/entpb.proto` |
| Swagger | `swagger/**` |
| Wire DI | `cmd/app/wire_gen.go` |

**Rule**: If you think you need to edit generated files → edit source-of-truth and regenerate.

## 3. Generation Entrypoints

```bash
# 1. Ent + autoproto
make gen/db

# 2. Proto + bind/map (MOST COMMON)
make gen/proto

# 3. OpenAPI/Swagger
make gen/docs

# 4. Dependency injection
make gen/wire

# 5. TypeScript types
make gen/dts

# 6. Run all generators
make gen/all
```

## 4. Boundary Rules

1. **Protocol-first**: Define contract/schema → regenerate → consume
2. **Never patch generated**: Fix source-of-truth instead
3. **Complete bind coverage**: Every exposed entity needs `createFilesConf`
4. **Ignore sensitive fields**: Use `WithIgnoreFields` for timestamps, soft-delete, secrets
5. **Stable ownership**: Keep route/error ownership at service scope

## 5. Conflict Resolution

When generated ≠ manual code:

1. Identify which source-of-truth should own the change
2. Edit source-of-truth only
3. Re-run generation commands
4. Fix compile errors in manual code (service/dao/render)
5. Re-run tests
