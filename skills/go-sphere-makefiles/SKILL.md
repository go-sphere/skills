---
name: go-sphere-makefiles
description: Standardize, review, or repair Makefiles and Make-driven CI across go-sphere repositories. Use when adding common dependency, formatting, test, lint, check, build, generation, or root batch targets while preserving repository-specific workflows, including multi-module and layout repositories.
---

# Go-Sphere Makefiles

Keep go-sphere repositories consistent at their public Make target boundary without forcing their internal build graphs to be identical.

## Desired Contract

Every Go repository should expose these common targets when they apply:

- `deps-update`: update direct, non-replaced dependencies and tidy the module.
- `tidy`: tidy without depending on a surrounding workspace.
- `fmt`: apply repository-owned formatting.
- `test`: run the repository's complete default test path.
- `lint`: run non-mutating formatting checks and applicable analyzers.
- `check`: perform the normal non-release green gate.

Repositories may retain `build`, `verify`, generation, compatibility, release, benchmark, deployment, or other specialized targets. Do not delete or flatten them merely to make files look identical.

## Inspect Before Editing

1. Read repository instructions, its Makefile, all `go.mod` and `go.work` files, CI workflows, generation scripts, and working-tree status.
2. Determine whether it is a single module, explicit multi-module repository, generator/protocol repository, executable, or layout/template.
3. Record what CI and developers already treat as the complete test, build, and generation paths.
4. Preserve unrelated changes and repository-specific targets.

Use explicit module and repository lists. Do not discover execution targets with a broad recursive `find`: vendor trees, fixtures, examples, or intentionally independent modules may require different treatment.

## Apply the Smallest Appropriate Pattern

### Single-module libraries

Use direct commands and the common target names. `check` normally verifies tidy state, lint, and tests. Do not add `build` just for uniformity when tests already compile all packages and no binary or generated artifact is delivered.

### Multi-module repositories

Maintain an explicit ordered module list and execute module-scoped commands in subshells. Run dependency maintenance with `GOWORK=off` so every module remains independently valid. A `go.work` file may still be used for local cross-module testing.

Separate the module list from the package/test list when a module exists only for fixtures or when the repository root has no Go packages.

### Generator and protocol repositories

Keep fixture generation, golden updates, Buf validation, breaking checks, and generator builds as repository-specific targets. Let `test` prepare only the fixtures required for reliable tests; do not hide release publishing inside a common target.

### Executables and layout repositories

Retain `build` and the established generation dependency graph. Layout repositories are clean-checkout generators, not ordinary libraries: CI generally needs `make init`, then `make build`, then `make test`. Do not replace their generation, asset, Docker, deployment, or help targets with a minimal library Makefile.

## Behavioral Rules

- Use overridable tool variables such as `GO ?= go`; add tool variables only for tools the repository actually uses.
- Exclude `.Main`, `.Indirect`, and `.Replace` modules when updating direct dependencies.
- Guard an empty dependency list before invoking `go get -u`.
- Use `GOWORK=off` for `go list -m`, `go get`, `go mod tidy`, and `go mod tidy -diff` when validating individual modules.
- Keep `fmt` mutating and `lint` non-mutating. A lint target may check formatting with `golangci-lint fmt --diff`, but must not silently rewrite files.
- Include only applicable analyzers: normally `go vet` and `golangci-lint`, plus NilAway, Buf, or repository-specific checks where already part of the contract.
- Make `check` a predictable composition target. Put slower race, API compatibility, breaking, or release-oriented checks in `verify` unless the repository intentionally requires them for every check.
- Use `.PHONY` for command targets and simple progress labels for loops.
- Prefer readable repetition over abstractions that obscure which directory or tool failed.

For canonical snippets and CI alignment, read [references/makefile-patterns.md](references/makefile-patterns.md) when implementing or reviewing changes.

## Root Organization Makefile

At the organization checkout root, keep a curated `REPOS ?=` list and dispatch only the common targets with `$(MAKE) --no-print-directory -C`. Allow `REPOS="..."` overrides for focused runs and fail clearly when a listed Makefile is missing.

Do not add a root `build`, `init`, or generation target unless every listed repository has the same safe meaning. Those operations are intentionally repository-specific.

An optional root `go-version` target may update every non-vendored `go.mod` and `go.work`, but must validate the requested version and require an explicit `GO_VERSION`.

## Keep CI Behind Make

CI should call the repository's Make targets instead of duplicating their command bodies:

- ordinary libraries: `make test`;
- binaries and generators that deliver buildable commands: `make build` and `make test`;
- layout repositories: `make init`, `make build`, and `make test` in separate steps.

For multi-module repositories, configure setup-go from a module declaring the highest required Go version and cache `**/go.sum`. If a pinned CI tool requires newer Go than the project under test, enable `GOTOOLCHAIN=auto` only for the tool-install step rather than silently raising the whole test job's minimum version.

Keep distinct compatibility workflows when they protect a separate contract. An organization status table may show only the primary test badge to stay readable.

## Verification

Run checks proportional to the change:

1. Run each changed common target, starting with the narrowest relevant repository or module.
2. Confirm `lint` and dependency verification do not leave unintended tracked changes.
3. For multi-module repositories, verify every listed module was exercised.
4. For layout/generator CI, test from a clean Git snapshot so ignored generated files cannot mask a missing initialization step.
5. Validate changed workflows with `actionlint` when available.
6. Finish with `git diff --check`, working-tree inspection, and a diff review in every touched repository.

Do not commit, push, tag, publish, or rerun remote workflows unless the user asks. Report commands actually run, any unverified path, and pre-existing failures separately.
