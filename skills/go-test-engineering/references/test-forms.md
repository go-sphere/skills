# Choosing the Test Form

Pick the smallest form that constrains the behavior. One behavior normally needs one form.

## Unit Tests

Use a unit test for a single function, component, or behavior with controlled dependencies.
Assert outputs, state transitions, stable errors, and externally visible side effects.

Do not test:

- Go language or standard-library behavior.
- Third-party library behavior the repository does not wrap as its own contract.
- Mocks, fakes, or hand-written synchronization instead of repository code.
- Private call order or internal fields, unless they are the only observable contract.

## Interface Contract Suites

When several implementations satisfy one public interface, define one reusable contract suite and
register every implementation through a factory or harness.

The suite should:

- express only guarantees shared by the interface;
- create isolated state for each implementation or subtest;
- accept implementation-specific setup and cleanup without weakening shared assertions;
- leave implementation-specific behavior to separate driver tests;
- use parallel subtests only when factories, fixtures, ports, and external state are isolated.

Never copy the same contract cases into every driver package.

## Golden Tests

A golden test is the last resort, not a convenient way to assert a lot at once. Default to a unit
test. Admit a golden test only when **both** gates pass:

1. **Environment gate.** Producing the output requires something a unit test cannot construct or
   control in-process: an external process or toolchain (`protoc`, `buf`, `wire`, `go generate`,
   `go build`/`go list`, a CLI binary run as a subprocess), a loaded Go package graph, compiled
   descriptors, or a filesystem tree written by such a tool. Typical qualifying cases:
   `google/wire` injector generation, a protoc plugin run through `protoc`/`buf`, ent codegen that
   loads packages, a scaffolder that emits a multi-file project.
2. **Contract gate.** The exact bytes of the whole output are a reviewed contract: generated source
   or files that users commit, or a stable on-disk or wire format that other tools consume.

If either gate fails, write unit tests instead. These never justify a golden file:

- Pure functions, parsers, formatters, validators, and string builders.
- `json.Marshal`/`proto.Marshal` of a struct, response bodies from `httptest` handlers, error
  messages, log lines, SQL strings, and config rendering that can be built from in-memory input.
- Template rendering or code generation that can be driven in-process from a small literal input —
  assert the specific fragments, ordering, or compile-ability that matter.
- Any output whose shape is incidental, or that changes whenever unrelated code changes.

Before adding or keeping a golden file, state in one line which external dependency forces it. If
you cannot name one, convert it to a unit test. A golden file is also wrong when a table-driven
test with explicit expected values would be just as readable.

A sound golden test:

- keeps the external-dependency part minimal: a few small fixtures, each isolating one feature,
  rather than one large kitchen-sink fixture;
- makes inputs deterministic and pins tool versions, or skips with an explicit reason when the tool
  is unavailable — never silently passes;
- normalizes only genuinely irrelevant variability (paths, versions, timestamps);
- shows a useful first difference on failure;
- provides an explicit, opt-in update mechanism (flag or Make target), never auto-updating;
- requires humans to review golden changes as contract changes.

Do not duplicate a full golden comparison with many substring assertions, unless a substring checks
an independent semantic boundary or produces a materially clearer failure. Logic that surrounds the
external call (option parsing, error branches, name mapping) stays in ordinary unit tests; only the
end-to-end output belongs in the golden.

## Integration Tests

Use an integration test for behavior that exists only across real boundaries. Prefer local,
deterministic infrastructure: `httptest`, temporary directories, embedded services, or
repository-supported test containers.

Tests requiring credentials, public networks, or unavailable external services may be opt-in, but:

- keep their activation explicit;
- never imply that skipped tests protect the default CI path;
- retain meaningful default tests with local substitutes where possible.

## Concurrency Tests

A concurrency test is justified only when concurrent access, cancellation, ordering, or shared
state is part of the contract. Use the race detector to find data races. Never replace it with a
fake load loop or a repeated call to a pure function.
