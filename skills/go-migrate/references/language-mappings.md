# Per-Language Construct Mappings

Read the section for `{legacy_language}` while writing the blueprint. Each section
lists how the language's main constructs land in Go and the behaviors most likely to
break A/B parity. General standards live in
[go-standards.md](go-standards.md).

## Table of Contents

- [C and C++](#c-and-c)
- [Java, Kotlin, and C#](#java-kotlin-and-c)
- [Python](#python)
- [JavaScript and TypeScript (Node)](#javascript-and-typescript-node)
- [Rust](#rust)
- [Ruby and PHP](#ruby-and-php)
- [Fortran and numeric kernels](#fortran-and-numeric-kernels)
- [Shell scripts](#shell-scripts)
- [Cross-language: dependencies and I/O](#cross-language-dependencies-and-io)

## C and C++

| Source | Go |
|:--|:--|
| `malloc`/`free`, `new`/`delete`, RAII | Values and garbage collection; `defer` for files, locks, and other non-memory resources |
| Raw pointer + length | Slice (`[]T`); bounds are checked, so out-of-range reads become panics, not silent corruption |
| `char*` strings, `std::string` | `string` (immutable bytes) and `[]byte`; `strings.Builder` for assembly |
| `struct` with function pointers, virtual methods | Struct plus interface; method values for callbacks |
| Templates | Generics for real type-parameter reuse; otherwise a concrete type or interface |
| `std::vector`/`map`/`unordered_map` | Slice / `map` (unordered; sort keys when the C++ code used `std::map` order) |
| Out-parameters, error codes | Multiple return values with `error` |
| `std::thread`, mutex, condvar | Goroutines, `sync.Mutex`, channels, `context` |
| Preprocessor macros, `#ifdef` | Constants, small functions, build tags only for real platform differences |

Parity traps: signed overflow and uninitialized reads are undefined in C but defined
(wrapping, zero values) in Go, so a "working" C program may have relied on either; log
them as latent bugs. Struct padding and `sizeof` disappear. `float` is 32-bit: port as
`float32` when the output depends on single-precision rounding. Avoid cgo to "keep"
a C library; port it or find a pure-Go equivalent.

C command-line programs add these traps, all of which affect output parity:
`atoi`/`strtol` return 0 silently on junk and saturate or overflow on large values (copy
the observed behavior with an explicit parser, and fuzz it against the C binary);
`printf` formats (`%.6f`, `%u`, `%x` of negative values) differ from `fmt` verbs, so
test each format string; unsigned arithmetic wraps and `(unsigned)` casts of negative
ints must become explicit `uint32` conversions; `argc` checks and exit codes are part of
the contract. `for i := range n` runs zero times for negative `n`, like `i < n` in C.

## Java, Kotlin, and C#

| Source | Go |
|:--|:--|
| Class + inheritance | Struct + embedding for reuse, interface for polymorphism; flatten hierarchies |
| Abstract class / interface | Interface at the consumer, kept to a few methods |
| Checked/unchecked exceptions | `error` values, sentinel errors (`var ErrX = errors.New(...)`) or typed errors, checked with `errors.Is`/`errors.AsType` |
| `try/finally`, `using` | `defer` |
| Generics with bounds | Type parameters with constraints; drop generics that existed only to avoid casts |
| Streams / LINQ | `for` loops, `slices` and `maps` helpers, `iter` pipelines |
| `Optional<T>`, nullable types | Zero value plus `ok` bool, or pointer when absence matters |
| Annotations, reflection, DI containers | Struct tags only where needed (JSON, DB); explicit wiring |
| `synchronized`, executors, `CompletableFuture` | Mutex, goroutines, `errgroup`/`sync.WaitGroup.Go`, `context` |
| Spring/ASP.NET controllers | `net/http` handlers with pattern-based `ServeMux`; `log/slog` for logging |

Parity traps: `String`/`char` are UTF-16, so lengths and indices differ for non-BMP
text; `HashMap` order is unspecified (Go's is randomized); `int` is 32-bit in Java/C#
(use `int32` where overflow behavior is observable); `BigDecimal` needs `math/big` or a
decimal library; default locale and time zone leak into formatting.

## Python

| Source | Go |
|:--|:--|
| Duck typing | Interfaces defined by the consumer; concrete types elsewhere |
| `dict`, `list`, `set`, tuples | `map`, slice, `map[T]struct{}`, small structs |
| Dataclasses, `TypedDict`, pydantic | Structs with tags and explicit validation functions |
| Exceptions, context managers | `error` returns, `defer` |
| Generators, comprehensions | `iter.Seq` / loops; build slices with preallocated capacity |
| `asyncio`, threads | Goroutines and channels; no event loop needed |
| `*args`, `**kwargs`, default arguments | Functional options or an options struct |
| `numpy` vectorization | Plain loops over slices (profile first); consider layout changes only when measured |
| `argparse`/`click`, `logging` | `flag` (or a small CLI library), `log/slog` |

Parity traps: integers are arbitrary precision (`math/big` or overflow analysis);
`//` and `%` floor, Go truncates; `dict` preserves insertion order, Go maps do not;
`round()` is banker's rounding (`math.RoundToEven`), Go's `math.Round` rounds half away
from zero; `random.seed(n)` uses Mersenne Twister and is not reproducible with
`math/rand/v2`; `str` is code points while Go `string` is bytes; `repr(float)` matches
`strconv.FormatFloat(x, 'g', -1, 64)` closely but check exponent formatting.

## JavaScript and TypeScript (Node)

| Source | Go |
|:--|:--|
| `Promise`/`async`/`await`, callbacks | Plain blocking code in goroutines; `context` for cancellation and timeouts |
| Event emitters, streams | Channels, `io.Reader`/`io.Writer` pipelines |
| Objects as records / maps | Structs for known shapes, `map[string]T` for dynamic keys, `json.RawMessage` for pass-through |
| TypeScript unions | Interface with a small closed set of implementers, or a struct with a `Kind` field |
| `npm` dependencies | Standard library first (`net/http`, `encoding/json`, `crypto/*`, `embed`) |
| Express/Fastify routes | `http.ServeMux` patterns (`"GET /users/{id}"`), middleware as `func(http.Handler) http.Handler` |

Parity traps: every number is a float64 (ints above 2^53 lose precision; use `int64`
only if the legacy code never exceeded 2^53, otherwise reproduce the float rounding);
bit operators are 32-bit; `undefined` vs `null` vs missing JSON keys (use pointers or
`omitzero`); `Array.prototype.sort` default is lexicographic; JSON key order follows
insertion order in JS but struct order or sorted order in Go; string length is UTF-16.

## Rust

| Source | Go |
|:--|:--|
| `Result`/`?` | `error` returns with `if err != nil { return ..., fmt.Errorf("...: %w", err) }` |
| `Option<T>` | Pointer, or value plus `ok` bool |
| Traits, enums with data | Interfaces; closed enums as a typed `int`/`string` constant set, data-carrying variants as an interface with concrete structs and a type switch |
| Ownership and lifetimes | GC; decide explicitly who closes resources (`defer`) and who may mutate shared data |
| `Arc<Mutex<T>>`, channels, `rayon` | Mutex next to the guarded fields, channels, bounded worker pools |
| `serde` | Struct tags with `encoding/json` |

Parity traps: Rust integer overflow panics in debug and wraps in release, Go always
wraps; `HashMap` order is random in both but `BTreeMap` order must be reproduced; Rust
`f32`/`f64` fusion is off by default, Go's may fuse (see [parity-and-determinism.md](parity-and-determinism.md)). Expect the
Go port to be slower in tight numeric loops and to use more memory; the staircase
benchmarks should report this honestly rather than hide it.

## Ruby and PHP

Dynamic dispatch and metaprogramming become explicit interfaces and generated or
hand-written code; do not port `method_missing`, `__get`, or monkey patching, redesign
the feature they implemented. Parity traps: loose comparison and type juggling (PHP
`==`, Ruby truthiness), associative-array ordering (insertion-ordered in both, random
in Go maps), integer-to-float promotion, default encodings, and `Time` / `DateTime`
time-zone defaults. Frameworks (Rails, Laravel) map to `net/http` plus a few focused
libraries, with the schema and routes as the source of truth.

## Fortran and numeric kernels

| Source | Go |
|:--|:--|
| Column-major arrays, `COMMON`, `EQUIVALENCE` | Row-major slices with an explicit indexing helper; a struct replacing `COMMON` blocks |
| 1-based indexing | Convert at the boundary and keep Go code 0-based; document the offset |
| `REAL*8` / `DOUBLE PRECISION` | `float64`; `REAL` is `float32` |
| `DO` loops, array expressions | `for` loops; avoid per-element function-call overhead in hot loops |

Parity traps: column-major vs row-major traversal order changes both performance and
floating-point summation order (and so the last bits); compiler flags like `-ffast-math`
or x87 extended precision in the legacy build make bit-exact comparison impossible, so
choose and document an epsilon. Fusion on arm64 is the Go-side counterpart ([parity-and-determinism.md](parity-and-determinism.md)). Use flat `[]float64` with an index helper for matrices; `[][]float64`
costs an allocation and a pointer chase per row.

## Shell scripts

Replace `grep | awk | sed` pipelines with typed parsing in Go, `os/exec` only for tools
that genuinely have no Go equivalent (always `exec.CommandContext`, always check
errors, never build commands by string concatenation). Parity traps: exit codes and
stderr text, word splitting and globbing that the script relied on, environment
variable inheritance, locale-dependent sorting (`LC_ALL=C` vs UTF-8), and temp-file
cleanup on signals (`signal.NotifyContext`).

## Cross-language: dependencies and I/O

- Map each legacy dependency in the blueprint table: standard library first, then a
  maintained Go module (check recent commits, license, and run `govulncheck`), then a
  small in-tree port. Never wrap the original library via cgo or a subprocess just to
  avoid porting it, unless the user approved that as an explicit exception.
- Databases: keep the schema and migrations; use `database/sql` with a driver, or the
  project's chosen query layer, and prepared statements. Compare query results in the
  parity harness, not just application output.
- Serialization: pin formats (JSON, protobuf, CSV) with golden files produced by the
  legacy program, then assert byte equality or a documented semantic equality.
- Time: inject a clock (`func() time.Time`) so parity runs and tests are deterministic.
- Configuration: environment variables and flags parsed once into a typed struct in
  `main`.
