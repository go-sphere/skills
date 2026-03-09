# Completeness Rubric

Use this rubric when a draft has the right structure but still feels less complete than a high-quality operational spec.

## 1. Problem and Scope

A strong section answers:
- What operational pain exists now?
- Why does this system or feature exist?
- What is in scope?
- What is explicitly out of scope?
- What other layer owns the adjacent concerns?

If this section only says what to build, it is too thin.

## 2. System Overview

A strong section answers:
- What are the main components?
- Which component owns which responsibility?
- What abstraction layers exist?
- What external systems are required?
- What trust or safety assumptions matter?

If the section is just an architecture slogan, it is too thin.

## 3. Domain Model

For each entity or runtime object, confirm:
- canonical identifier is defined
- required fields are listed
- normalization or coercion rules are listed
- ownership boundary is clear
- authoritative versus derived state is clear
- relationships to other entities are clear

If the draft uses nouns that never become typed objects, it is too thin.

## 4. Contract Specification

For each contract, file, schema, or API surface, confirm:
- discovery/path resolution behavior
- schema or structure
- parsing rules
- unknown key or unknown field behavior
- validation and error classes
- versioning or extension behavior

If the draft says "reads config from a file" without these details, it is too thin.

## 5. Configuration Semantics

For each config object or field group, confirm:
- type
- default
- precedence
- environment indirection rules if relevant
- normalization/coercion rules
- invalid value handling
- dynamic reload semantics
- restart-required semantics

This is one of the most common missing sections in weak specs.

## 6. State Machine Depth

For each workflow or lifecycle, confirm:
- internal states are enumerated
- external states are enumerated if different
- legal transitions are listed
- triggers are listed
- guard conditions are listed
- side effects are listed
- retry behavior is listed
- cancellation behavior is listed
- cleanup/release behavior is listed
- reconciliation or restart recovery is listed when relevant

If a workflow is just a numbered list of happy-path steps, it is too thin.

## 7. Failure Model

For each failure surface, confirm:
- error classes exist
- causes are described
- operator-visible symptom is described
- retry, block, continue, or release behavior is described
- logs/metrics/status surfaces are described

If the section only says "handle errors gracefully", it is too thin.

## 8. Observability and Operations

A strong operational section answers:
- what gets logged
- what gets measured
- what humans can inspect
- which failures are visible to operators
- how startup, restart, cleanup, and drift are handled

If the system runs continuously and the draft says nothing about operations, it is too thin.

## 9. Validation and Conformance

A strong section answers:
- what is validated at startup
- what is validated before dispatch or execution
- what tests are required
- what invariants must hold
- what scenarios prove recovery or reconciliation behavior

If the draft says only "write tests", it is too thin.

## 10. Compatibility and Rollout

A strong section answers:
- is the change backward compatible
- what existing clients or data are affected
- what migration is required
- what rollout order is safe
- what cleanup must happen later

If the draft changes contracts but never says who breaks, it is too thin.

## 11. Extension and Implementation Variance

When optional capabilities exist, confirm:
- what is core versus optional
- what is implementation-defined
- how unknown keys or extension fields behave
- whether extension changes require restart

If the draft implies optionality without defining the boundary, it is too thin.

## 12. Finish Check

Before calling the spec done, ask:
- Could two independent implementers build materially compatible behavior from this document?
- Does the document explain failure, recovery, and operator behavior, not just success?
- Does the document say what happens when inputs are missing, invalid, stale, or reordered?
- Does the document feel executable rather than aspirational?
