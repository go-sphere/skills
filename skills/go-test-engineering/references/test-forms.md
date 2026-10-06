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

Use golden files only when the exact output is itself a reviewed contract: generated source,
serialization, formatted documents, or stable CLI output.

A sound golden test:

- makes inputs deterministic;
- normalizes only genuinely irrelevant variability;
- shows a useful first difference on failure;
- provides an explicit, opt-in update mechanism;
- requires humans to review golden changes as contract changes.

Do not use a golden file for an opaque snapshot whose exact shape has no contractual value. Do not
duplicate a full golden comparison with many substring assertions, unless a substring checks an
independent semantic boundary or produces a materially clearer failure.

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
