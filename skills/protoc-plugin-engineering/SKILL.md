---
name: protoc-plugin-engineering
description: Write, refactor, or review Go protoc-gen-* plugins in the go-sphere organization. Use when adding a new plugin, changing generated output, reworking plugin config or templates, hardening plugin tests, or reviewing a plugin PR for structure, determinism, immutability, and golden-file discipline. Covers both new-file generators (protoc-gen-sphere, protoc-gen-route, protoc-gen-sphere-errors) and in-place AST rewriters (protoc-gen-sphere-binding). Do not use for authoring .proto API contracts — that is proto-api-generator.
---

# Protoc Plugin Engineering

Keep go-sphere's `protoc-gen-*` plugins structurally consistent so they share one
reading path, one calling convention, and one maintenance model — without forcing
their domain logic to be identical.

<HARD-GATE>
Before writing or changing plugin code, confirm:
- Which plugin, and whether it is a **new-file generator** or an **in-place AST rewriter** (they differ in no-output semantics and header handling)
- Whether the change alters **generated output** (semantic vs. presentational), **exported API**, **flags**, or **template data** — each has a compatibility cost
- Whether `workspace/docs/PROTOC_PLUGIN_GUIDELINES.md` and `TESTING.md` are available in this checkout; if so, they are authoritative and this skill is the summary

If the change touches generated output, state up front whether it is a semantic
or a presentational change. Do not bundle both in one commit.
</HARD-GATE>

## Scope

| Plugin | Kind |
|--------|------|
| `protoc-gen-sphere` | new-file generator (service → interfaces + helpers) |
| `protoc-gen-route` | new-file generator (service + HTTP rules → routes) |
| `protoc-gen-sphere-errors` | new-file generator (enum → error definitions) |
| `protoc-gen-sphere-binding` | in-place AST rewriter (retags `protoc-gen-go` output) |

## Non-Negotiable Principles

1. **Consistent structure and contract, not consistent business logic.** Same
   entrypoint, config validation, generator lifecycle, and test entry. Domain
   logic may differ. Do not invent abstractions just to make filenames match.
2. **Immutable config, file-local state.** Flags are parsed and validated once at
   startup; the generator holds its own snapshot. Per-file state (imports,
   services, enums) stays in the current call — never in package-level variables.
3. **Same input, same output.** No map iteration order, wall-clock time,
   randomness, machine paths, or state left over from the previous file.
4. **Default templates are read-only.** Embedded templates are package-level
   read-only resources. Custom templates load into a separate renderer instance.
   No `ReplaceTemplateIfNeed`-style package-level mutation.
5. **Generated files are a stable interface.** They land in version control, code
   review, and downstream builds. Do not create large golden diffs without cause.

## Required Reading

1. **[references/plugin-conventions.md](references/plugin-conventions.md)** — directory layout, entrypoint, config, generator contract, templates, output rules, AST-rewriter specifics, compatibility
2. **[references/plugin-testing.md](references/plugin-testing.md)** — the three test layers, fixture management, golden discipline, and the pitfalls that bite every plugin suite

Load the testing reference whenever you add or change tests, touch `testdata/`,
or update golden files.

## Working Order for a New Plugin

1. Decide: new-file generator or in-place rewriter.
2. Create the standard directory and a minimal `Config`.
3. Implement `Validate`, `NewGenerator`, and no-output semantics **first**.
4. Then the domain model and generation logic.
5. Introduce an immutable `Renderer` only if the plugin needs templates.
6. Add unit, descriptor, golden, CLI, and isolation tests.
7. Confirm output determinism and API compatibility.
8. Pass the full local quality gate before release.

## Local Quality Gate

Run inside each plugin module before delivering:

```sh
find . -type f -name '*.go' -not -path './vendor/*' -exec gofmt -w {} +
git diff --check
GOWORK=off go mod tidy -diff
GOWORK=off go test -race ./...
GOWORK=off go vet ./...
golangci-lint run --no-config
nilaway ./...
```

`GOWORK=off` proves the module builds independently of the local workspace.
`go mod tidy -diff` checks without mutating. Golden updates run as a separate
explicit command, followed by a full test rerun. A project Makefile may wrap
these, but must not weaken their semantics — see the `go-sphere-makefiles` skill
for the target contract (`test`, `lint`, `check`, `update-golden`, `generate`).

## Review Checklist

**Structure**
- [ ] `main.go` only adapts the protoc protocol and assembles objects
- [ ] `Config`, `Generator`, template, and domain logic have clear boundaries
- [ ] Files named by responsibility; no mixed `utils.go` / `common.go` / `helper.go`
- [ ] Deviations in special plugins have a stated justification

**Config and state**
- [ ] `DefaultConfig()` equals the real CLI defaults and returns independent objects
- [ ] `Validate` is nil-safe and its error text is order-stable
- [ ] Generator deep-copies reference-typed config
- [ ] No mutable package-level templates or cross-file state
- [ ] A custom template affects only its own instance

**Output**
- [ ] Non-applicable files produce no output — never a header-only shell
- [ ] Filename, header, package, and imports are stable
- [ ] Map-derived output is sorted; repeated lists deduped and ordered
- [ ] Dynamic strings pass through `strconv.Quote`
- [ ] The generated diff contains only what this change requires
- [ ] AST rewrites are idempotent and preserve non-target content

**Compatibility**
- [ ] Changes to exported API, flags, defaults, or template data are identified
- [ ] Compatible old APIs keep a `Deprecated:` wrapper
- [ ] Breaking changes have migration notes and a release plan

**Verification**
- [ ] Unit, descriptor, golden, and CLI tests cover this change
- [ ] Golden diffs were reviewed by a human, not just made green
- [ ] `go test -race`, `go vet`, lint, and nilaway pass
- [ ] Module verifies independently under `GOWORK=off`

## Reporting

State: plugin and kind; whether output changed and whether that change is
semantic or presentational; compatibility impact on exported API/flags/template
data; which test layers were exercised; golden files updated and reviewed; the
quality-gate commands actually run, with any skipped step named explicitly.

If a plugin must deviate from these conventions, record the deviation, the
reason, its blast radius, and the condition for returning to the common shape in
that plugin's README.
