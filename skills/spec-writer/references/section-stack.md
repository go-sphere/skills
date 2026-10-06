# Spec Section Stack

Reference style: https://github.com/openai/symphony/blob/main/SPEC.md

Use this structure when the document must guide implementation across components, runtime state,
configuration, background work, retries, and operational behavior. Write the spec as an
operational contract, not as a product essay. Section-level writing shapes live in
`spec-patterns.md`.

## Why Symphony Feels Complete

It does all of these at once:

- It separates problem, goals, non-goals, and system boundaries early.
- It names components and abstraction layers before discussing behavior.
- It defines runtime entities as typed objects with fields and normalization rules.
- It distinguishes internal service state from external tracker or user-visible state.
- It specifies configuration as a real contract: schema, defaults, precedence, coercion, reload behavior, validation.
- It describes workflows as state transitions with triggers, guards, retries, and release behavior.
- It includes startup cleanup, restart recovery, and reconciliation instead of assuming a clean world.
- It documents optional extensions and forward-compatibility behavior explicitly.
- It adds redundant cheat-sheet sections when they help implementation.

That is the bar to aim for.

## Recommended Section Stack

Use as many of these as the task needs.

### 1. Problem Statement

State the operational problem, the user or system pain, and the exact system boundary. Say what
the spec covers and what it leaves to other layers.

### 2. Goals and Non-Goals

Separate lists. Goals define required outcomes. Non-goals prevent scope creep.

### 3. System Overview

Describe the main components, abstraction levels, and external dependencies. Useful subsections:
main components, abstraction or architecture layers, external dependencies, and trust, safety,
or operational assumptions.

### 4. Core Domain Model

Define implementation-facing entities and runtime objects. For each one, include:

- canonical identifier
- required fields
- normalization rules
- ownership boundary
- whether it is authoritative state, derived state, or an optional surface

### 5. Contract or Repository Specification

Use this section when the system consumes or publishes a structured contract: a
repository-owned workflow file, an API contract, a file format, a message schema, a plugin
contract, or a prompt template contract.

Say how the contract is discovered, parsed, validated, and versioned.

### 6. Configuration Specification

This is the biggest difference between a shallow spec and a strong one. For each config group or
top-level object, include:

- field names and types
- defaults
- precedence and source resolution
- normalization and coercion semantics
- validation checks
- dynamic reload versus restart-required behavior
- how invalid config affects runtime behavior

Add a redundant config cheat sheet when the section is dense.

### 7. Workflows and State Changes

Describe behavior over time. For every important lifecycle, include:

- internal states
- external or user-facing states, if different
- legal transitions
- transition triggers
- guard conditions
- side effects
- retry or continuation behavior
- cancellation behavior
- cleanup or release behavior
- reconciliation or restart recovery when relevant

This is where the spec becomes executable.

### 8. Failure Handling and Observability

Document error classes, causes, operator-visible symptoms, retry/block/continue/release
behavior, and logs, metrics, status surfaces, or audit trails. If the system can partially
succeed, say what happens next.

### 9. Validation and Testing

State how an implementation proves compliance: validation rules, startup or preflight checks,
required integration tests, invariants that must hold, and restart or reconciliation scenarios.

### 10. Migration, Rollout, Compatibility

Include when the change affects existing consumers, files, workspaces, data, or operators. State
backward compatibility status, migration steps, rollout sequence, cleanup behavior, and
mixed-version assumptions when relevant.

### 11. Implementation Notes or Optional Extensions

Use when some capabilities are optional or extension-specific. Include optional extensions,
forward-compatibility behavior, unknown key handling, implementation-defined areas, and what can
vary safely between implementations.

### 12. Open Questions

Keep unresolved items explicit and bounded. Do not bury them inside the main contract.

## Compact Template

```markdown
# [Name] Specification

## 1. Problem Statement

## 2. Goals and Non-Goals
### 2.1 Goals
### 2.2 Non-Goals

## 3. System Overview
### 3.1 Main Components
### 3.2 Abstraction Levels
### 3.3 External Dependencies

## 4. Core Domain Model
### 4.1 Entities and Runtime Objects
### 4.2 Stable Identifiers and Normalization Rules

## 5. Contract Specification
### 5.1 Discovery and Resolution
### 5.2 File or Interface Format
### 5.3 Validation and Error Surface

## 6. Configuration Specification
### 6.1 Source Precedence and Resolution
### 6.2 Dynamic Reload Semantics
### 6.3 Validation Rules
### 6.4 Config Cheat Sheet

## 7. Workflows and State Changes
### 7.1 Internal States
### 7.2 Lifecycle Phases
### 7.3 Transition Triggers
### 7.4 Idempotency and Recovery Rules

## 8. Failure Handling and Observability

## 9. Validation and Testing

## 10. Migration and Compatibility

## 11. Implementation Notes or Optional Extensions

## 12. Open Questions
```

## When to Use a Smaller Shape

Collapse sections when the work is local and does not need full operational treatment. Even
then, keep these explicit: scope, success criteria, data or contract changes, workflow impact,
failure behavior, and validation.
