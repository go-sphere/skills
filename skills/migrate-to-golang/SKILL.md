---
name: migrate-to-golang
description: Migrate a legacy or foreign-language codebase (C, C++, Java, Python, Node, Rust) from a GitHub URL or local path to idiomatic Go on the latest release, proving parity with A/B runs and recording telemetry and PGO results. Use when asked to port, rewrite, or migrate to Go, or 迁移到 Go, 用 Go 重写. Not for tidying existing Go — that is `go-simplify`.
---

# Migrate Codebases to Idiomatic Go

Translate a codebase into idiomatic Go that targets the latest stable Go release directly,
prove it behaves like the original, and record measured telemetry plus a first-person
report. A migration preserves behavior; it does not copy structure. Port what the program
does, in the shape Go programmers write it.

## Inputs

- `{github_url}` or `{codebase_path}`: the source to migrate. Ask for it when missing.
- Whether the Go port lives in a new `{repo_name}-go` module (default) or replaces the source tree.
- The Go module path. Derive `github.com/{owner}/{repo}` from the git remote and confirm it. With no remote, ask; if you cannot ask, use `example.com/{repo_name}-go` and list it as an open question.

## Steps

1. **Stage 0.** Set the shell variables below. Clone the repository. Resolve the latest stable Go. Initialize telemetry and census the legacy code. State the legacy build and run commands; wait for confirmation before running code cloned from an external repository. Rebuild the baseline in release mode even if a binary exists, capture golden outputs with `scripts/ab_parity.sh`, and log `legacy_baseline`. Follow [references/stage0-acquire-and-baseline.md](references/stage0-acquire-and-baseline.md).

   ```bash
   TM="{skill_dir}/scripts/telemetry.py"   # {skill_dir} is the directory holding this SKILL.md
   TEL="{workspace_dir}/migration_telemetry.json"
   ```

2. **Stage 1: blueprint.** Start the `blueprint` bucket. Log every opportunity and latent legacy bug. Write the six-section blueprint to `{workspace_dir}/BLUEPRINT.md`. Continue into step 3 unless the user asked for a plan only.
3. **Scaffold and port.** Start the `rewrite` bucket. Run `go mod init {module_path}`, then `go mod edit -go={X.Y.Z}` for the resolved release; add no `toolchain` line. Port modules leaves first, each with passing tests before the next. Log the first `go test` run of the port as iteration 1 with `log-test-run`; step 5 continues the numbering. Log `idiomatic_go`.
4. **Tune from profiles.** Time a workload that runs 1 to 10 seconds on the legacy build. Collect `pprof` CPU and allocation profiles on it, or on a `testing.B` benchmark of the same code path. Fix only what the profile shows. Log `tuned_go`, or log that no change was justified.
5. **Verification crucible.** Start the `test_heal` bucket. Run the gate commands, heal failures for at most 5 iterations, and log each iteration with `log-test-run`.
6. **A/B parity.** Start the `parity` bucket. Run the legacy and Go programs on the same `N` deterministic cases with `scripts/ab_parity.sh`, and log each iteration with `log-parity-run`. Heal divergences for at most 5 iterations.
7. **Go PGO.** Start the `pgo_bench` bucket. Build with a merged `default.pgo`, re-run parity on that binary, and log `pgo` only when you keep the profile. Skip PGO with a stated reason when the legacy baseline runs under 1 second or the workload is I/O-bound.
8. **Release hygiene and report.** Run `go fix ./...`, `go mod tidy`, and `govulncheck ./...`. Scan the Go source, log the spotlight and story, and render `migration_infographic.html`.
9. **Summarize.** Report the Go version used, the measured before/after numbers, the infographic path, and every gap left open.

## Reference Map

Load the smallest set that answers the question in front of you.

| Read | When |
|------|------|
| [references/stage0-acquire-and-baseline.md](references/stage0-acquire-and-baseline.md) | Always, before step 1 |
| [references/language-mappings.md](references/language-mappings.md) | Before designing the package layout in step 2; read only the section for `{legacy_language}` |
| [references/blueprint.md](references/blueprint.md) | Before writing the blueprint in step 2 |
| [references/go-standards.md](references/go-standards.md) | Before writing the first Go file in step 3, and again when a design choice is unclear |
| [references/benchmarks-and-pgo.md](references/benchmarks-and-pgo.md) | Before the first benchmark in step 3, and in steps 4 and 7 |
| [references/verification-crucible.md](references/verification-crucible.md) | Before writing tests in step 5 |
| [references/parity-and-determinism.md](references/parity-and-determinism.md) | Before building the A/B harness in step 6, and whenever a case diverges |
| [references/report-and-infographic.md](references/report-and-infographic.md) | Before step 8 |

`scripts/telemetry.py` records every bucket and iteration. `scripts/ab_parity.sh` captures golden outputs and runs the A/B comparison. `references/infographic_template.html` is the report template. Do not edit any of them while migrating.

## Rules

1. Resolve the latest stable Go from `https://go.dev/dl/?mode=json` instead of trusting memory, and never target an older release without the user's approval.
2. Never compile or run code cloned from an external repository before the user confirms the commands. Local code the user asked you to migrate needs no second confirmation.
3. Port behavior, not structure. A line-by-line transliteration that keeps class hierarchies, exceptions as panics, or `utils` packages has failed the migration.
4. Prefer the standard library. Add a dependency only when the blueprint justifies it, and run `govulncheck` after adding one.
5. Keep migrated code free of `unsafe`, cgo, and `//go:linkname`, because they remove the memory safety that justified the migration.
6. Measure before tuning. A profile, not intuition, decides every optimization.
7. Stop each heal loop after 5 iterations or 15 minutes. Record the remaining gap in telemetry and the final report instead of looping.
8. Log failures as they happen, including iteration 1 when it failed. Telemetry numbers must come from commands you ran.
9. Do not push, tag, or publish the migrated module unless the user asks.

## Output

The migration is done only when each item below is verified by running its command:

- `go build ./...`, `go vet ./...`, and `golangci-lint run` (or `staticcheck ./...`) report 0 issues.
- `go test -race ./...` passes, with statement coverage of 90% or more on migrated packages.
- `go fix -diff ./...` is empty and `govulncheck ./...` is clean or each finding is documented.
- A/B parity holds on all `N` cases within the documented tolerance.
- Benchmarks for `legacy_baseline`, `idiomatic_go`, `tuned_go`, and `pgo` are logged, or a stage is omitted with a reason.
- `migration_telemetry.json`, `BLUEPRINT.md`, and `migration_infographic.html` exist in the output directory.

State any item that is not met, with the reason, in the final summary.

## Related Skills

- Upstream — none; start here with a legacy or foreign-language codebase. Use `interview-me` first when the migration scope or success criteria are vague.
- Downstream — `go-simplify` for a leanness pass over the finished port, `godoc` to add verified usage examples to exported APIs, and `go-test-engineering` to harden the generated tests.
- Boundary — this skill owns translating a non-Go codebase into Go and proving parity. Use `go-simplify` for existing Go, `go-test-engineering` for test content alone, and `sphere-feature-workflow` when the target is a go-sphere project with proto, Ent, and layout contracts.
- Companion — `delegate` to hand independent modules to parallel headless agents once the blueprint fixes the package boundaries.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
