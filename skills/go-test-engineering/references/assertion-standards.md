# Assertion Standards and False Confidence

## Assert the Narrowest Stable Result

Assert the narrowest stable result that expresses the contract.

- Prefer an exact expected HTTP status over `status != 200`.
- Prefer `errors.Is`, `errors.As`, a stable error code, or an exact public error over `err != nil`.
- Compare complete small values when every field is contractual.
- For large values, compare the meaningful fields and say why the rest are irrelevant.
- Fail immediately when a success-path response cannot be decoded. Never let a parse failure
  become a zero value that can accidentally pass.
- Treat a cleanup failure as a test failure, unless it matches a documented normal shutdown condition.
- Use `t.Log` for diagnostics, never as a substitute for an assertion.

Avoid a broad substring assertion when an exact stable value, a structured decode, or a typed
error is available. Avoid an exact comparison for deliberately unstable details — timestamps,
random IDs, map order, environment-specific paths. Control or normalize those values instead.

## Common False Confidence Patterns

Remove or repair tests that match any of these:

- They only execute code, print output, or log values without asserting behavior.
- They accept any error or any non-success status when one specific failure is required.
- They reproduce the implementation algorithm inside the expected-value calculation.
- They verify generated getters, protobuf cloning, or runtime marshal concurrency rather than
  repository-owned schema or integration contracts.
- They repeat a pure function hundreds of times and call it a concurrency test.
- They lock around a test-owned map, exercising the test's lock instead of production synchronization.
- They are skipped by default or hidden behind a flag, leaving the normal suite with no relevant assertion.
- They duplicate a golden file through numerous weak `contains` checks.
- They assert a private field, a helper call count, or an internal sequence that can change
  without changing behavior.
- Their name describes the function being called rather than the behavior being guaranteed.

## Surgical Change Habits

- Preserve repository style and supported Go idioms.
- Prefer table-driven tests when cases share setup and assertion shape.
- Use subtests when their names make failures easier to diagnose.
- Call `t.Helper()` in assertion and setup helpers.
- Use `t.Cleanup()` for resources whose lifetime belongs to the test.
- Keep fixtures deterministic and failures locally diagnosable.
- Avoid an abstraction that serves only one trivial test.

Never mix an unrelated production refactor into a test cleanup. When a valid test reveals a
production bug, make the smallest contract-correct fix and call it out separately.
