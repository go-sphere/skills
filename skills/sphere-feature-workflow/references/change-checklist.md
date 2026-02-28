# Change Checklist (sphere-layout)

## Table of Contents

1. Pre-Change Checklist
2. In-Change Checklist
3. Workflow-Specific Checklist
4. Post-Change Checklist
5. Common Blocking Issues

## 1. Pre-Change Checklist

- [ ] Classify workflow (`Contract-first`, `Schema-first`, `Service-only`, or `Cross-layer`).
- [ ] Confirm impacted service namespace and route prefix ownership.
- [ ] Confirm whether both `proto` and `schema` layers are affected.
- [ ] Identify backward compatibility constraints.
- [ ] Check whether existing Sphere packages already provide the capability.

## 2. In-Change Checklist

- [ ] Modify source-of-truth files first.
- [ ] Keep service-local business errors in the owning `.proto` unless sharing is required.
- [ ] If schema evolves, review `cmd/tools/bind/main.go#createFilesConf` coverage.
- [ ] Review ignore-field strategy for timestamps, soft-delete fields, and secrets.
- [ ] Align DAO query shape with response shape to avoid N+1 paths.
- [ ] Reuse existing Sphere packages before introducing new abstractions.
- [ ] Do not edit generated render files (`internal/pkg/render/entbind/**`, `internal/pkg/render/entmap/**`).

## 3. Workflow-Specific Checklist

### Contract-first

- [ ] `proto/**` contract changes are complete and internally consistent.
- [ ] `make gen/proto` has been run after contract changes.
- [ ] Service/DAO/render code consumes generated contract changes.
- [ ] `make gen/docs` ran if HTTP/OpenAPI output changed.

### Schema-first

- [ ] Ent schema field/relation/index policy is complete.
- [ ] Bind/map registration impact is handled in `createFilesConf`.
- [ ] `WithIgnoreFields` policy covers sensitive/system-managed fields.
- [ ] `make gen/proto` has been run and downstream code is aligned.

### Service-only

- [ ] No unintended contract/schema changes were introduced.
- [ ] Business behavior changes are implemented in non-generated files only.
- [ ] Permission, transaction, and idempotency paths are validated where applicable.

## 4. Post-Change Checklist

- [ ] Required generation commands were run (`gen/proto`, `gen/docs`, `gen/wire` as applicable).
- [ ] Tests were run (`go test ./...` or scoped suites).
- [ ] No manual edits exist in generated files.
- [ ] Reuse decision is documented (selected Sphere packages and rationale).
- [ ] Compatibility impact and residual risks are reported.

## 5. Common Blocking Issues

1. Workflow type is not classified, causing partial updates.
2. Schema changed, but bind/map registration was not updated.
3. Proto changed, but generation commands were not executed.
4. Generated diffs exist, but service/dao/render logic was not aligned.
5. Sensitive fields are exposed due to missing ignore-field policy.
6. Route wildcard/prefix drift introduces runtime conflicts.

When any blocking issue appears, stop and return `Blocking Issues` with a fix plan before claiming completion.
