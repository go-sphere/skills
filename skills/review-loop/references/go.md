# Go

Go-specific additions to [checklist.md](checklist.md). Read it when the repository has `go.mod`.

## Extra prompts

| Perspective | Look for |
|-------------|----------|
| `correctness` | An error shadowed by `:=`; an error compared with `==` instead of `errors.Is` or `errors.As`; `%v` where `%w` is needed; a write to a nil map; slices that alias after `append`; `defer` inside a loop |
| `concurrency` | `sync.WaitGroup.Add` called inside the goroutine; a copied `sync.Mutex`; a `context.WithCancel` without `defer cancel()`; a goroutine that ignores `ctx.Done()`; a channel closed by the receiver |
| `security` | A file path used without `filepath.Clean` and a root check; `math/rand` used for tokens; `==` on secrets instead of `subtle.ConstantTimeCompare`; `exec.Command` fed unvalidated input; `fmt.Sprintf` building SQL |
| `resources` | `http.Response.Body` and `sql.Rows` not closed on every path; a `defer Close()` placed before the error check; an unbounded `io.ReadAll` on request data; an `http.Client` or server with no timeout |
| `api-compat` | A removed or renamed exported identifier; a new method on an exported interface; a raised `go` directive in `go.mod` |

Rules:

1. Read the `go` directive in `go.mod` before reporting a loop-variable capture. Loop variables are per-iteration from Go 1.22, so the bug applies only to older directives.
2. Treat `*.pb.go`, `*_grpc.pb.go`, and Ent generated output as generated. Review the `.proto` file or Ent schema instead.
3. Update golden files with the repository's own target, such as `make update-golden`, never by hand.

## Go gate commands

Use these in place of the Go row of the fallback table when the repository defines nothing better.

| Gate | Command |
|------|---------|
| Narrow test | `go test <pkg> -run <Test>` |
| Build and vet | `go build ./...` then `go vet ./...` |
| Full tests | `go test ./...` |
| Race | `go test -race <pkgs>` |
| Lint | `make lint`, or `golangci-lint run` |

Set `GOCACHE` to a directory in the system temp directory when a codex-sandboxed or headless agent runs Go.

## go-sphere projects

Read `.sphere/layout.json`, `AGENTS.md`, and `docs/LAYOUT_CONTRACT.md` before reviewing; they outrank a general Go habit. A fix that touches `.proto`, Ent schema, layout files, or generation commands goes through `sphere-feature`. A change in one repository that has a byte-identical twin elsewhere in the workspace needs both sides fixed together.
