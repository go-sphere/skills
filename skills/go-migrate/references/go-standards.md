# Go Engineering Standards

Rules for how the ported code looks. Apply them to every module you write from step 3 onward.

## Target the latest Go directly

The point of "migrate straight to the latest Go" is that nothing in the new code
needs to apologize for an old toolchain. Concretely:

- The `go` directive in `go.mod` is the release resolved in Stage 0 (for example
  `go 1.27.3`). Do not lower it to widen compatibility, and do not add build tags or
  fallbacks for older releases.
- Prefer the standard library over dependencies. Before adding a module, check whether
  the release already ships the capability: `net/http` pattern-based `ServeMux`,
  `log/slog`, `slices`, `maps`, `cmp`, `iter`, `math/rand/v2`, `errors`, `embed`,
  `os.Root`, `testing/synctest`. A dependency that the legacy code needed only because
  its language lacked something (a thread pool library, a collections library, a JSON
  library) usually disappears.
- Use current idioms rather than the ones from memory. Run `go doc` on the packages
  you are about to use, read the release notes for every release since the last one
  you know well, and run `go fix -diff ./...` after each ported package: the Go
  toolchain ships modernizers (`any`, `rangeint`, `minmax`, `forvar`, `mapsloop`,
  `omitzero`, `newexpr`, `errorsastype`, and more — `go tool fix help` lists the
  installed set) that rewrite stale patterns. If the Modern Go Guidelines tooling
  (`use-modern-go`) is available, run it as well.
- Patterns worth reaching for first: range over integers and iterators
  (`for i := range n`, `iter.Seq`, `slices.Collect`, `maps.Keys`), `min`/`max`/`clear`
  builtins, `errors.Is`/`errors.AsType` with `%w` wrapping, `context.Context` as the
  first parameter of anything that blocks, `sync.WaitGroup.Go` for fan-out,
  `testing.B.Loop` for benchmarks, `t.Context()` in tests, `cmp.Or` for defaults, and
  `omitzero` for JSON struct tags. Verify each against the resolved release with
  `go doc` before depending on it.

## Write Go, not the source language in Go syntax

| Source habit | Go form |
|:--|:--|
| Class hierarchy, inheritance | Small structs, composition, and interfaces declared by the *consumer* (one to three methods) |
| Exceptions | `error` return values, wrapped with `fmt.Errorf("...: %w", err)`; `panic` only for programmer errors; no `recover` for control flow |
| Getters and setters | Exported fields, or a method named for the behavior |
| Constructors with many arguments, builders | A struct literal, or functional options when there are many optional settings |
| Null / None / nil objects | The useful zero value; `nil` only for pointers, slices, maps, interfaces, funcs |
| Dependency-injection frameworks | Explicit constructor parameters wired in `main` |
| `utils`, `helpers`, `common` packages | Name packages for what they provide (`retry`, `lineparse`); keep unexported helpers next to their caller |
| Global mutable state, singletons | A struct that owns the state, passed explicitly |
| Threads and shared mutable state | Goroutines with a clear owner, communicating via channels or guarded by one mutex (see Concurrency below) |
| Stringly-typed config | A typed config struct loaded once in `main` |

## Simplify call sites and cognitive load

Audit the legacy code's convoluted call trees, deep nesting, out-parameters, and
global state. Prefer early returns over nesting, multiple return values over
out-parameters, and small functions with explicit dependencies. Average function
length and maximum nesting depth are measured by `scan-codebase`; they should drop for real codebases. A program under
about 200 lines usually grows once it gains error handling, a testable `run` function, and
godoc. Report that regression honestly instead of contorting the code.

## File and package hygiene

Keep files cohesive: target `<= 400` code lines per file (hard ceiling `600`) by
splitting along responsibility, not along arbitrary line counts — never split a file
just to hit the number. Every package gets a package comment; every exported
identifier gets a godoc comment that states the contract (what it does, errors,
concurrency, lifecycle), and key entry points get runnable `Example` functions.

## Concurrency

Every goroutine needs an owner that waits for it or cancels it via `context`. Prefer
passing data over sharing it; where sharing is simpler, guard it with one mutex stated
next to the fields it protects. Bound parallelism (worker pool or a semaphore) rather
than spawning per item. Do not port a thread pool, future/promise, or actor library:
goroutines and channels replace them. Time-dependent tests use `testing/synctest`
rather than `time.Sleep`. `-race` clean is part of done.
