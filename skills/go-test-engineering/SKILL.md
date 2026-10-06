---
name: go-test-engineering
description: Audit, repair, or write Go tests so they enforce real API and behavior contracts. Use for reviewing unreliable or AI-generated tests, deleting duplicate tests, strengthening weak assertions, designing interface contract suites, judging when a golden test is justified, or fixing implementation bugs that valid tests expose. Not for Make targets or Make-driven CI — that is `go-sphere-makefiles`.
---

# Go Test Engineering

Make Go tests trustworthy, strict, and maintainable. Optimize for their value as behavioral
constraints — not for test count, coverage percentage, or a green `go test ./...` at any cost.

## Principles

1. Correctness outranks pass rate.
2. Establish the intended contract before judging either the test or the implementation.
3. Fix or delete an incorrect, obsolete, duplicate, or meaningless test.
4. Fix production code when a sound test exposes an implementation defect.
5. Never weaken an assertion merely to accommodate current behavior.
6. Test observable behavior and owned contracts, not incidental implementation details.
7. Prefer the standard `testing` package and the smallest useful test design.
8. Never add a test solely to increase coverage.

## Operating Mode

Infer the narrowest authorized mode from the request, then state it before changing files.

| Mode | Authorized by | What you may do |
|------|---------------|-----------------|
| Review only | "review", "diagnose", "look at" | Inspect tests and production code, report evidence-backed findings. Edit nothing. |
| Review and repair | "fix", "optimize", "refactor", "repair" | Repair or remove defective tests, fix production defects valid tests reveal, verify the result. |
| Write tests | "write tests", "add tests", "cover" | Define intended behavior and failure cases first, then add the smallest constraining test set. |

A request to review or diagnose does not by itself authorize edits.

## Steps

1. Read repository instructions and determine the supported Go version. Check the working tree and preserve unrelated user changes.
2. Inventory `*_test.go` files, shared test packages, fixtures, golden data, build tags, test flags, Make targets, and CI commands. Locate interfaces with multiple implementations and duplicated driver tests.
3. Run the repository's baseline test command before editing, when practical.
4. Establish the contract for the area under review (see below).
5. Read each test file together with its source file. Ordinary unit tests should be co-located and named after the source module: `name.go` and `name_test.go`. Classify every test as **keep**, **rewrite**, **move or consolidate**, or **delete**.
6. Classify every failure separately as a test defect, a production defect, a stale or ambiguous contract, or an environment/fixture defect.
7. Make surgical changes in the right test form.
8. Walk the verification ladder, then report using the Deliverable section.

### Establishing the contract

Read the tests together with the smallest set of sources that determines intended behavior, in
this order of authority:

1. Public API declarations, interfaces, exported comments, package documentation.
2. Protocol, schema, CLI, HTTP, storage, or serialization specifications the repository owns.
3. Call sites and other implementations of the same interface.
4. Existing fixtures and stable compatibility requirements.
5. The implementation — evidence, not automatic truth.

When these disagree, state the conflict explicitly. Do not silently side with the existing test or
the existing implementation. Ask the user only when the unresolved choice would materially change
the public contract.

For every important test, answer: what contract does it protect, what realistic regression would
make it fail, is the assertion strong enough to identify that regression, and does it survive a
behavior-preserving refactor? With no convincing answers, rewrite or remove the test.

## Reference Map

| Read | When |
|------|------|
| [references/test-forms.md](references/test-forms.md) | At step 7, to choose between unit, contract-suite, golden, integration, and concurrency forms |
| [references/assertion-standards.md](references/assertion-standards.md) | While judging or writing any assertion, and when classifying a weak test |
| [references/domain-guidance.md](references/domain-guidance.md) | When the code under test is generated protobuf, a code generator, a server, or a background task |

## Verification Ladder

Run the smallest useful check first, then broaden:

1. The changed test or package.
2. Related packages and reusable contract suites.
3. Formatting, vet, lint, or type checks the repository requires.
4. `go test ./...`, or the repository's canonical full test command.
5. `go test -race ./...` when changes touch concurrency, lifecycle, shared state, or runtime integration, or when the repository requires it.
6. Bounded repeated runs such as `go test -count=10` for tests with realistic flake risk.
7. Repository gates such as `make check` or `make verify`, when available.
8. `git diff --check` plus a final diff review for unrelated changes or accidentally weakened assertions.

Never claim success for a command you did not run. Report environmental blockers and pre-existing
failures separately from regressions your change caused.

## Deliverable

Conclude with:

- tests kept, rewritten, consolidated, or deleted, and why;
- production defects fixed because valid tests exposed them;
- the exact verification commands and their outcomes;
- any unverified integration paths, ambiguous contracts, or remaining risks.

For review-only work, report findings by severity with file and line evidence, then summarize
residual risk. For implementation work, lead with the achieved behavior rather than the mechanics
of editing.

## Related Skills

- Upstream — none; this skill applies after any implementation, or directly to existing suites.
- Downstream — none; the verification result and remaining-risk report are the deliverable.
- Boundary — use `go-sphere-makefiles` for Make targets and Make-driven CI, `protoc-plugin-engineering` for plugin golden-test infrastructure, `go-simplify` for behavior-neutral production-code simplification where the existing suite is the safety net, and `sphere-feature-workflow` for implementation work with no test scope.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
