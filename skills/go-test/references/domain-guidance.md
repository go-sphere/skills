# Domain-Specific Test Guidance

## Generated Protobuf Code

When the repository owns `.proto` contracts or generated descriptors, test stable schema facts:
field numbers, enum values, extension numbers, extendees, types, cardinality, and a minimal
wire-level integration when compatibility matters.

Do not spend repository tests on generated getter nil behavior, clone correctness, or protobuf
runtime thread safety. Do not treat values documented as invalid or reserved as valid boundary
cases.

## Code Generators

Generated output is a golden contract only when the generator runs through an external tool or
loaded environment (a protoc plugin driven by `protoc`/`buf`, `wire`, ent codegen loading
packages) and the whole output is committed by users. See the two gates in
[test-forms.md](test-forms.md#golden-tests). A generator that can be called in-process with a small
literal input gets unit tests on the fragments that matter, not a golden file.

Always unit-test, without golden files: parser and configuration inputs, option handling, name
mapping and helper functions, error and no-output branches, and empty components when valid.

Generated Go should be formatted and compile-checked when the repository's normal toolchain makes
that practical.

## Servers and Background Tasks

Use bounded contexts and deterministic readiness signals. Never rely on an arbitrary sleep.

During shutdown, accept only documented normal errors — for example
`errors.Is(err, http.ErrServerClosed)` when that is the server contract. Fail on unrelated errors
and on timeouts.
