# Source of Truth and Generated Boundaries

`.sphere/layout.json` is authoritative for the project you are in; this file is
the fallback and the explanation. When the two disagree, follow the project.
The editable/generated split below is orthogonal to the ownership split in
[layout-contract-and-ownership.md](layout-contract-and-ownership.md): a file can be
editable *and* `mixed`, which means edit it carefully rather than freely.

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
| Bind/Map | `cmd/tools/gen/entcrud/main.go` | Entity exposure policy (`conf.NewFilesConf`) |
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
| Resolved config | `config_gen.json`, `config.json` |
| Build output | `build/**`, `var/**` |
| Dep locks | `buf.lock`, `go.sum` |

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

# 7. Delivery gate (deps, format, lint, tests)
make check
```

`make gen/proto` depends on `gen/db`, so it also refreshes Ent. `gen/all` runs
the full chain and then tidies. Use `make help` to confirm what a given layout
actually exposes rather than assuming this list.

## 4. Boundary Rules

1. **Protocol-first**: Define contract/schema → regenerate → consume
2. **Never patch generated**: Fix source-of-truth instead
3. **Complete bind coverage**: Every exposed entity needs a `conf.NewEntity` entry in `cmd/tools/gen/entcrud/main.go`
4. **Ignore sensitive fields**: Use `WithIgnoreFields` for timestamps, soft-delete, secrets
5. **Stable ownership**: Keep route/error ownership at service scope
6. **Layout ownership**: New product code goes in `project_owned` paths; `mixed` paths are seams to merge into, not to rewrite

## 5. Conflict Resolution

When generated ≠ manual code:

1. Identify which source-of-truth should own the change
2. Edit source-of-truth only
3. Re-run generation commands
4. Fix compile errors in manual code (service/dao/render)
5. Re-run tests
