---
name: go-test-engineering
description: Audit, repair, or write Go tests so they enforce real API and behavior contracts. Use for reviewing unreliable or AI-generated tests, removing duplicate or low-value tests, strengthening weak assertions, designing reusable interface contract suites, deciding when golden tests are justified, fixing implementation bugs exposed by valid tests, or adding focused unit and integration tests. Do not use for ordinary Go implementation work that does not involve tests.
---

# Go Test Engineering

Make Go tests trustworthy, strict, and maintainable. Optimize for their value as behavioral constraints, not for test count, coverage percentage, or a green `go test ./...` at any cost.

## Non-Negotiable Principles

1. Correctness outranks pass rate.
2. Establish the intended contract before judging either the test or implementation.
3. Fix or delete an incorrect, obsolete, duplicate, or meaningless test.
4. Fix production code when a sound test exposes an implementation defect.
5. Never weaken an assertion merely to accommodate current behavior.
6. Test observable behavior and owned contracts, not incidental implementation details.
7. Prefer the standard `testing` package and the smallest useful test design.
8. Do not add tests solely to increase coverage.

## Choose the Operating Mode

Infer the narrowest authorized mode from the request and state it before changing files.

- **Review only**: inspect tests and relevant production code, then report evidence-backed findings. Do not edit files.
- **Review and repair**: audit tests, repair or remove defective tests, fix production defects revealed by valid tests, and verify the result.
- **Write tests**: define the intended behavior and meaningful failure cases first, then add the smallest test set that constrains them.

A request to review or diagnose does not by itself authorize edits. A request to optimize, fix, refactor, or write tests normally does.

## Establish the Contract

Read tests together with the smallest set of sources needed to determine intended behavior:

1. Public API declarations, interfaces, exported comments, and package documentation.
2. Protocol, schema, CLI, HTTP, storage, or serialization specifications owned by the repository.
3. Call sites and other implementations of the same interface.
4. Existing fixtures and stable compatibility requirements.
5. The implementation, treated as evidence rather than automatic truth.

When these sources disagree, identify the conflict explicitly. Do not silently choose the existing test or implementation. Ask the user only when the unresolved choice would materially change the public contract.

For every important test, be able to answer:

- What behavior or contract does this protect?
- What realistic regression would make it fail?
- Is the assertion strong enough to identify that regression?
- Does the test remain valid after an internal refactor that preserves behavior?

If those questions have no convincing answers, rewrite or remove the test.

## Audit Workflow

### 1. Inspect the Repository

- Read repository instructions and determine the supported Go version.
- Check the working tree before editing; preserve unrelated user changes.
- Inventory `*_test.go` files, shared test packages, fixtures, golden data, build tags, test flags, Make targets, and CI commands.
- Locate interfaces with multiple implementations and duplicated driver tests.
- Run the repository's baseline test command before edits when practical.

### 2. Review by Behavior Area

Read each test file with its corresponding source file and contract. Ordinary unit tests should normally be co-located and named after the source module, such as `name.go` and `name_test.go`.

Classify each test as:

- **Keep**: protects meaningful behavior with appropriate assertions.
- **Rewrite**: intent is useful, but setup, isolation, naming, or assertions are defective.
- **Move or consolidate**: useful behavior belongs in a table, helper, contract suite, or better-matched test file.
- **Delete**: duplicate, meaningless, obsolete, unreachable in normal runs, or coupled only to implementation details.

Classify each failure separately as:

- test defect;
- production defect;
- stale or ambiguous contract;
- environment or fixture defect.

### 3. Make Surgical Changes

- Preserve repository style and supported Go idioms.
- Prefer table-driven tests when cases share setup and assertion shape.
- Use subtests when their names make failures easier to diagnose.
- Call `t.Helper()` in assertion and setup helpers.
- Use `t.Cleanup()` for resources whose lifetime belongs to the test.
- Keep fixtures deterministic and failures locally diagnosable.
- Avoid abstractions that serve only one trivial test.

Do not mix unrelated production refactors into a test cleanup. When a valid test reveals a production bug, make the smallest contract-correct fix and call it out separately.

## Select the Right Test Form

### Unit Tests

Use unit tests for a single function, component, or behavior with controlled dependencies. Assert outputs, state transitions, stable errors, and externally visible side effects.

Do not test:

- Go language or standard-library behavior;
- third-party library behavior the repository does not wrap as its own contract;
- mocks, fakes, or hand-written synchronization instead of repository code;
- private call order or internal fields unless they are the only observable contract.

### Interface Contract Suites

When several implementations satisfy one public interface, define one reusable contract suite and register every implementation through a factory or harness.

The suite should:

- express only guarantees shared by the interface;
- create isolated state for each implementation or subtest;
- accept implementation-specific setup and cleanup without weakening shared assertions;
- run implementation-specific behavior in separate driver tests;
- use parallel subtests only when factories, fixtures, ports, and external state are isolated.

Do not copy the same contract cases into every driver package.

### Golden Tests

Use golden files only when the exact output is itself a reviewed contract, such as generated source, serialization, formatted documents, or stable CLI output.

A sound golden test should:

- make inputs deterministic;
- normalize only genuinely irrelevant variability;
- show a useful first difference on failure;
- provide an explicit, opt-in update mechanism;
- require humans to review golden changes as contract changes.

Do not use a golden file for opaque snapshots whose exact shape has no contractual value. Avoid duplicating a full golden comparison with many substring assertions unless a substring checks an independent semantic boundary or produces a materially clearer failure.

### Integration Tests

Use integration tests for behavior that exists only across real boundaries. Prefer local, deterministic infrastructure such as `httptest`, temporary directories, embedded services, or repository-supported test containers.

Tests requiring credentials, public networks, or unavailable external services may be opt-in, but:

- keep their activation explicit;
- never imply that skipped tests protect the default CI path;
- retain meaningful default tests with local substitutes where possible.

## Assertion Standards

Assert the narrowest stable result that expresses the contract.

- Prefer an exact expected HTTP status over `status != 200`.
- Prefer `errors.Is`, `errors.As`, a stable error code, or an exact public error over merely `err != nil`.
- Compare complete small values when all fields are contractual.
- For large values, compare the meaningful fields and explain why other fields are irrelevant.
- Fail immediately when a success-path response cannot be decoded; never convert parse failure into a zero value that can accidentally pass.
- Treat cleanup failures as test failures unless they match a documented normal shutdown condition.
- Use `t.Log` for diagnostics, never as a substitute for an assertion.

Avoid broad substring assertions when an exact stable value, structured decode, or typed error is available. Avoid exact comparisons for deliberately unstable details such as timestamps, random IDs, map order, or environment-specific paths; control or normalize those values instead.

## Common False Confidence Patterns

Remove or repair tests with these patterns:

- They only execute code, print output, or log values without asserting behavior.
- They accept any error or any non-success status when one specific failure is required.
- They reproduce the implementation algorithm inside the expected-value calculation.
- They verify generated getters, protobuf cloning, or runtime marshal concurrency rather than repository-owned schema or integration contracts.
- They repeat a pure function hundreds of times and call it a concurrency test.
- They lock around a test-owned map and therefore exercise the test's lock, not production synchronization.
- They are skipped by default or hidden behind a flag, leaving the normal suite with no relevant assertion.
- They duplicate a golden file through numerous weak `contains` checks.
- They assert a private field, helper call count, or internal sequence that can change without changing behavior.
- Their name describes the function being called rather than the behavior being guaranteed.

Concurrency tests are justified only when concurrent access, cancellation, ordering, or shared state is part of the contract. Use the race detector to find data races; do not replace it with fake load loops.

## Domain-Specific Guidance

### Generated Protobuf Code

When the repository owns `.proto` contracts or generated descriptors, test stable schema facts such as field numbers, enum values, extension numbers, extendees, types, cardinality, and a minimal wire-level integration when compatibility matters.

Do not spend repository tests on generated getter nil behavior, clone correctness, or protobuf runtime thread safety. Do not treat values documented as invalid or reserved as valid boundary cases.

### Code Generators

Generated output is an appropriate golden contract. Also test meaningful parser and configuration inputs, error and no-output branches, and empty components when valid. Generated Go should be formatted and compile-checked when the repository's normal toolchain makes that practical.

### Servers and Background Tasks

Use bounded contexts and deterministic readiness signals. Do not rely on arbitrary sleeps. During shutdown, accept only documented normal errors, for example `errors.Is(err, http.ErrServerClosed)` when that is the server contract; fail on unrelated errors and timeouts.

## Verification Ladder

Run the smallest useful checks first, then broaden:

1. The changed test or package.
2. Related packages and reusable contract suites.
3. Formatting, vet, lint, or type checks required by the repository.
4. `go test ./...` or the repository's canonical full test command.
5. `go test -race ./...` when changes touch concurrency, lifecycle, shared state, or runtime integration, or when the repository requires it.
6. Bounded repeated runs such as `go test -count=10` for tests with realistic flake risk.
7. Repository gates such as `make check` or `make verify` when available.
8. `git diff --check` and a final diff review for unrelated changes or accidentally weakened assertions.

Do not claim success for a command that was not run. Report environmental blockers and pre-existing failures separately from regressions caused by the change.

## Deliverable

Conclude with:

- tests kept, rewritten, consolidated, or deleted and why;
- production defects fixed because valid tests exposed them;
- the exact verification commands and outcomes;
- any unverified integration paths, ambiguous contracts, or remaining risks.

For review-only work, report findings by severity with file and line evidence, then summarize residual risk. For implementation work, lead with the achieved behavior rather than the mechanics of editing.
