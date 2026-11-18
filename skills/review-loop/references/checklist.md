# Checklist

Language-neutral review prompts, rules for generated files, and how to find the validation gates. Read it for every `review` and before choosing gates in `fix`.

## Review prompts by perspective

Use the rows that match the requested `perspective`. With none requested, use `correctness` and `concurrency`.

| Perspective | Look for |
|-------------|----------|
| `correctness` | Errors swallowed, shadowed, or compared by identity instead of by type; null or zero values that mean both "unset" and "valid"; off-by-one and boundary cases; aliasing of shared collections; time zones and overflow; state left half-updated when a step fails |
| `concurrency` | A task or thread with no exit path or cancellation; shared state read without the lock that guards its writes; two locks taken in different orders; a channel or queue closed twice or by the wrong side; check-then-act on shared state; an unbounded number of tasks |
| `security` | Queries or commands built by string concatenation; paths or URLs taken from input without validation; weak randomness for tokens; secrets written to logs or responses; missing authentication or authorization on a new entry point; token validation that skips algorithm, expiry, or audience; non-constant-time secret comparison |
| `resources` | Files, connections, response bodies, and cursors not closed on every return path; a cleanup registered before the error check; unbounded reads of request data; missing timeouts |
| `api-compat` | A removed or renamed public symbol; a changed signature, default, or zero-value meaning; a new required member on a public interface; a changed wire format, schema, or error code; a raised minimum language or dependency version |
| `tests` | New branches with no test; a test that asserts an implementation detail; sleeps used for synchronization; tests that share mutable state; a skipped test with no reason |
| `maintainability` | A function that mixes two jobs; an abstraction with one implementation and no second consumer; a public symbol that should be private; duplicated logic that must change together |
| `docs` | A public symbol with a missing or stale doc comment; a changed behavior with an unchanged README or changelog |

Rules for findings:

1. Check the language and framework version before claiming a version-specific bug. A fixed-in-version behavior is not a finding on a newer version.
2. Check whether the project's own helper already handles the case before reporting a missing check.
3. A convention in `AGENTS.md`, `CLAUDE.md`, or `docs/` outranks a general habit. Read them before reviewing.
4. When the repository has a language reference in this skill's Reference Map, read it too.

## Generated and shared files

| File kind | Review action |
|-----------|---------------|
| Generated code: protobuf output, ORM or schema output, API clients, swagger or OpenAPI JSON, lockfiles | Do not review. Review the source that produced it. |
| Snapshot and golden files | Review only that the change is intended. Update them with the repository's own update command, never by hand. |
| Schema, protocol, and contract definitions | Review as contracts. A fix may need a generator rerun or changes in another repository. |
| A file the repository marks as identical to a file elsewhere | A fix changes both sides together. Name the other file in the finding. |
| Vendored code | Do not review. |

## Find the validation gates

Use the repository's own commands. Look in this order and stop at the first source that answers:

1. The user's `test_command`.
2. `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or `docs/` sections on testing.
3. CI configuration, such as `.github/workflows/` or `.gitlab-ci.yml`.
4. A `Makefile`, `justfile`, or `Taskfile`. Read a recipe before running it.
5. The fallback table below.

| Ecosystem | Detected by | Narrow test | Build or typecheck | Lint | Full tests |
|-----------|-------------|-------------|--------------------|------|------------|
| Go | `go.mod` | `go test <pkg> -run <Test>` | `go build ./...`, `go vet ./...` | `golangci-lint run` | `go test ./...` |
| Node | `package.json` | the `test` script with a path or name filter | `tsc --noEmit`, the `build` script | the `lint` script | the `test` script |
| Python | `pyproject.toml`, `setup.cfg` | `pytest <path>::<test>` | `mypy .` or `pyright` | `ruff check .` | `pytest` |
| Rust | `Cargo.toml` | `cargo test <name>` | `cargo build`, `cargo check` | `cargo clippy` | `cargo test` |
| Java | `pom.xml`, `build.gradle` | `mvn -Dtest=<Test> test`, `gradle test --tests <Test>` | `mvn compile`, `gradle build` | the configured checkstyle or spotbugs task | `mvn test`, `gradle test` |
| Other | none of the above | the project's documented test command | its build command | its lint command | its test suite |

Use a script from the project's own manifest in preference to a raw tool command, so project flags and configuration apply.

## Gate order

Run the gates in this order and stop at the first failure.

| Order | Gate | Run when |
|-------|------|----------|
| 1 | Narrow test for the touched behavior | Always |
| 2 | Build or typecheck | Always, for compiled or typed languages |
| 3 | Lint or static analysis | The repository defines it |
| 4 | Full tests of every package or module touched | Always |
| 5 | Race, sanitizer, or concurrency check | Touched code uses threads, tasks, locks, or shared state, and the toolchain offers one |
| 6 | Repository gate such as `make check` | The repository defines it and the recipe is safe to run |

Run each gate from the directory of the project or module that owns the touched files. A directory holding several repositories has one project per repository: run the gates once per project you touched. When `test_command` was given, run it in place of rows 3 to 6 and keep rows 1 and 2.

A sandboxed or headless agent may be unable to write its build cache. Point the cache at a directory in the system temp directory before reporting a gate as failed.
