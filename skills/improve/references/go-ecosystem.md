# Go and go-sphere Notes

These notes sharpen recon, the audit, and the plans for Go work. A project's own guide (`AGENTS.md`, `CLAUDE.md`) outranks them wherever they disagree.

## 1. Recon for Go

| Look at | Learn |
|---------|-------|
| The `go` directive and `toolchain` line in `go.mod` | The language version. Loop-variable semantics differ before 1.22, so some findings depend on it. |
| `find . -name go.mod -not -path '*/vendor/*'` and `go.work` | The module list. Audit and plan per module. |
| The `Makefile` (`make help` when it exists) | The repository's gate. Plans use it in preference to raw `go` commands. |
| `.golangci.yml` and `.github/workflows/` | The lint set and what CI really runs. |
| `buf.yaml`, `buf.gen.yaml`, `*.proto`, an Ent `schema/` directory | The sources of truth behind generated code. |
| `.sphere/layout.json`, `AGENTS.md`, `docs/LAYOUT_CONTRACT.md` | go-sphere ownership rules and workflow. |

Read-only checks, cheapest first: `go build ./...`, `go vet ./...`, `go test ./...` (per package when slow), `golangci-lint run` in check mode, then the repository gate (`make lint`, `make test`, `make check`). Go writes its build cache, telemetry, and test temp directories outside the repository, which is fine. Add `go test -race` when you vet a concurrency finding or a race-freedom claim, and in plans that change concurrency. Network lookups: `govulncheck ./...`, `go list -m -u all`.

Check-mode forms are allowed: `go mod tidy -diff`, `gofmt -l .`, `golangci-lint fmt --diff`, and the targets that wrap them (for example `make tidy-check`). Their write-mode twins are not: `go mod tidy`, `gofmt -w`, `go generate`, `go get`, `make fmt`, `make tidy`, and any target that tags, pushes, deploys, or upgrades dependencies. In go-sphere repositories that includes `make add-tags`, `make tag`, `make deps-update`, `make generate` in the proto-option repositories (it ends with `buf push`), and `devops/deploy/deploy.sh`. Read the Makefile; the list changes.

## 2. Generated code

A Go file is generated when a line before its first code matches `^// Code generated .* DO NOT EDIT\.$`. List them with `grep -rlE '^// Code generated .* DO NOT EDIT\.$' --include='*.go' .`. Typical outputs are `*.pb.go`, `*_gen.go`, `wire_gen.go`, Ent output, swagger files, and generated TypeScript clients.

| The defect is in | Do |
|------------------|----|
| Generated output | Trace it to the source of truth: the `.proto`, the Ent schema, the template, or the generator. Audit and plan against that source. The plan names the generate command and lists the outputs under "Regenerated". |
| A `layout_owned` path of a generated go-sphere project | The fix belongs upstream in the layout repository. Report it there. Do not write a local plan that edits it. |
| A `mixed` path | Plan it, and tell the executor to preserve both the layout wiring and the project's additions. |

`.sphere/layout.json` classifies every path as `generated`, `layout_owned`, `mixed`, or the default `project_owned`; the first matching pattern wins. Product code lives in `project_owned` paths: `proto/<domain>/v1`, `internal/biz/<domain>`, `internal/service/<domain>`, and in Ent layouts `internal/pkg/database/schema`. A project without `.sphere/` predates the contract: treat every path as `project_owned` except generated outputs, and say ownership could not be verified.

Read `name` in `.sphere/layout.json` for the layout variant. The variants (`standard`, `simple`, `bun`, `telegram`) have different capabilities, so never plan Ent work for a layout without Ent. The `sphere-feature` skill documents each.

## 3. Several repositories

When modules live in sibling repositories, as the go-sphere organization does:

- Each repository has its own `go.mod`, tags, and CI. A downstream repository sees an upstream change only after the upstream is tagged and the downstream `go.mod` is bumped. Order plans the same way: the upstream plan first, then a downstream plan that names the tag to bump to.
- Contracts shared across repositories are pinned by tests on both sides. A plan that changes one side must list the other side and its test, in the same dependency chain.
- Read the workspace guide beside the repositories for the repository map, the release order, and the side-effect targets.

## 4. Go audit signals

These are signals, not verdicts. Read the code before reporting.

| Category | Look for |
|----------|----------|
| Correctness | Ignored `error` results; `defer` inside loops; `err` shadowed in an inner scope; writes to a nil map; a typed nil returned as an interface; `context.Background()` in a request path instead of the caller's context; goroutines with no stop signal; `sync.WaitGroup` or channel misuse; unsynchronized shared state; `rows.Err()` unchecked or `Rows` and `resp.Body` never closed; loop variables captured by closures when `go.mod` says a version before 1.22; errors compared as strings instead of `errors.Is` or `errors.As`; a `recover` that hides a panic. |
| Security | SQL built by concatenation or `fmt.Sprintf`; `os/exec` arguments or file paths built from request data (look for `filepath.IsLocal`, and `os.Root` on Go 1.24 or later); `math/rand` used for tokens; `InsecureSkipVerify: true`; JWT validation that does not pin the algorithm or check expiry; outbound requests to user-supplied URLs without an allowlist; request bodies read without `http.MaxBytesReader`; an `http.Server` without timeouts; secrets in logs. |
| Performance | Ent or SQL queries inside loops (eager loading with `With<Edge>()` or batching with `IDIn` instead); `regexp.MustCompile` inside a hot function; unbounded goroutine fan-out; list endpoints without pagination; an `http.Client` or `sql.DB` built per request. A micro-optimization without a benchmark or profile is not a finding. |
| Tests | Tests that use the network or the wall clock, order-dependent tests, a golden file no external process justifies, interface drivers without a shared contract suite. Plans for these hand the work to `go-test`. |
| Tech debt | Over-design, over-optimization, and over-defensive checks belong to `go-simplify`. Report them as one finding that names that skill. Do not list them one by one. |
| Dependencies | An old `go` directive, leftover `replace` directives, deprecated APIs such as `io/ioutil`, and `govulncheck` results that reach called code. Report only reachable vulnerabilities. |
| DX | A missing single-command gate, no linter config, CI without a module cache, no agent guide. |
| Docs | Exported API without doc comments, or examples that no longer compile. Plans for these hand the work to `godoc`. |

## 5. Plans for Go repositories

- In "Commands you will need", put the repository gate first (`make check`, `make test`). Fall back to `go build ./...`, `go vet ./...`, `go test ./...`.
- Scope a test with `go test ./path/to/pkg -run '^TestName$' -count=1`. The `-count=1` disables the test cache, so a pass is real.
- Add `go test -race ./path/to/pkg` to plans that change concurrency.
- Check formatting without writing: `gofmt -l .` must print nothing.
- A generator or schema change ends with the generate command, then `git status --short` showing only the listed Regenerated paths.
- Edit `go.mod` only in dependency plans, followed by `go mod tidy` and `git diff --stat go.mod go.sum`.
- Tell executors that run in a `codex` sandbox to set `GOCACHE` to a temp directory, because the sandbox cannot write the default cache or bind localhost sockets. The reviewer re-runs those commands.
- Follow the repository's commit style. go-sphere repositories use Conventional Commits, such as `fix(cache): close the redis client on shutdown`.

## 6. Executor toolkit by category

The executor may not have these skills, so the plan must stand alone. A toolkit line only adds a better way to do a step the plan already specifies.

| The plan touches | Name this skill |
|------------------|-----------------|
| Go tests or test strategy | `go-test` |
| Dead code, defensive checks, over-design in Go | `go-simplify` |
| Doc comments and examples for exported Go API | `godoc` |
| Makefile targets or Make-driven CI | `sphere-make` |
| `.proto` contracts or HTTP API shape | `sphere-api` |
| Ent schema | `sphere-ent` |
| Proto, schema, service, and generation across layers | `sphere-feature` |
| Pulling layout changes into a project | `sphere-sync` |
| Porting another language to Go | `go-migrate` |
| A direction plan that needs a spec first | `spec` or `prd` |

For a missing agent guide in a go-sphere project, point the executor at `CLAUDE.TEMPLATE.md` in `https://github.com/go-sphere/skills`.
