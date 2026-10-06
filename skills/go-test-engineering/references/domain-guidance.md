# Domain-Specific Test Guidance

## Generated Protobuf Code

When the repository owns `.proto` contracts or generated descriptors, test stable schema facts:
field numbers, enum values, extension numbers, extendees, types, cardinality, and a minimal
wire-level integration when compatibility matters.

Do not spend repository tests on generated getter nil behavior, clone correctness, or protobuf
runtime thread safety. Do not treat values documented as invalid or reserved as valid boundary
cases.

## Code Generators

Generated output is an appropriate golden contract. Also test meaningful parser and configuration
inputs, error and no-output branches, and empty components when valid.

Generated Go should be formatted and compile-checked when the repository's normal toolchain makes
that practical.

## Servers and Background Tasks

Use bounded contexts and deterministic readiness signals. Never rely on an arbitrary sleep.

During shutdown, accept only documented normal errors — for example
`errors.Is(err, http.ErrServerClosed)` when that is the server contract. Fail on unrelated errors
and on timeouts.
