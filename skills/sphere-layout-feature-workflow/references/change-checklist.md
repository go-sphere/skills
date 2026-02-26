# Change Checklist (sphere-layout)

## Table of Contents

1. Pre-Change Checklist
2. In-Change Checklist
3. Post-Change Checklist
4. Common Blocking Issues

## 1. Pre-Change Checklist

- [ ] Identify change type (`Contract-first`, `Schema-first`, `Service-only`).
- [ ] Confirm impacted service namespace and route prefix.
- [ ] Confirm whether `proto` and `schema` both need updates.
- [ ] Identify backward compatibility constraints.
- [ ] Check whether `github.com/go-sphere/sphere` already provides the needed capability.

## 2. In-Change Checklist

- [ ] Modify only source-of-truth files first.
- [ ] Keep service-local errors in owning `.proto` file unless cross-service sharing is required.
- [ ] If schema evolves, update `cmd/tools/bind/main.go#createFilesConf`.
- [ ] Review ignore-field strategy for timestamps and secrets.
- [ ] Align DAO query shape with response shape to avoid N+1 paths.
- [ ] Reuse existing Sphere packages before introducing new framework-level abstractions.
- [ ] Do not edit generated render files (`internal/pkg/render/entbind/**`, `internal/pkg/render/entmap/**`).

## 3. Post-Change Checklist

- [ ] Run `make gen/proto` after any proto/schema change.
- [ ] Run `make gen/docs` when HTTP contract changed.
- [ ] Run `make gen/wire` when DI graph changed.
- [ ] Run tests (`go test ./...` or scoped suites).
- [ ] Confirm no manual edits inside generated files.
- [ ] Document reuse decision (selected Sphere packages and rationale).
- [ ] Summarize compatibility impact and residual risk.

## 4. Common Blocking Issues

1. Only schema updated; bind registration not updated.
2. Proto changed but generation commands not executed.
3. Generated diff exists but service/dao/render logic not aligned.
4. Sensitive fields accidentally exposed due to missing ignore policy.
5. Route wildcard or prefix drift creates runtime conflicts.

When any blocking issue appears, stop and return a fix plan before claiming completion.
