---
name: protoc-plugin-engineering
description: Write, refactor, or review Go `protoc-gen-*` plugins in the go-sphere organization. Use when adding a plugin, changing generated output, reworking plugin config or templates, hardening plugin tests, or reviewing a plugin PR for determinism, immutability, and golden-file discipline. Not for authoring `.proto` contracts — that is `proto-api-generator`.
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

## Reference Map

| Read | When |
|------|------|
| [references/plugin-conventions.md](references/plugin-conventions.md) | Always, before writing code — directory layout, entrypoint, config model, generator contract |
| [references/plugin-output-rules.md](references/plugin-output-rules.md) | Before changing a template, generated output, an AST rewrite, or an exported API |
| [references/plugin-testing.md](references/plugin-testing.md) | Whenever you add or change tests, touch `testdata/`, or update golden files |
| [references/review-checklist.md](references/review-checklist.md) | At review time, and before delivering any plugin change |

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

## Reporting

State: plugin and kind; whether output changed and whether that change is
semantic or presentational; compatibility impact on exported API/flags/template
data; which test layers were exercised; golden files updated and reviewed; the
quality-gate commands actually run, with any skipped step named explicitly.

If a plugin must deviate from these conventions, record the deviation, the
reason, its blast radius, and the condition for returning to the common shape in
that plugin's README.

## Related Skills

- Upstream — none; this skill starts from an existing plugin, its generated output, or a golden-file failure.
- Downstream — `go-test-engineering` when plugin tests need redesign beyond golden discipline, and `go-sphere-makefiles` when the quality-gate targets above are missing or weakened. Hand off after reporting which gates actually ran.
- Boundary — use `proto-api-generator` for the `.proto` contracts; this skill owns the `protoc-gen-*` plugins that consume them. Use `go-test-engineering` for general Go test value outside plugin golden discipline.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
