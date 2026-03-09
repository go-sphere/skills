# Symphony-Style Spec Structure

Reference style: https://github.com/openai/symphony/blob/main/SPEC.md

Use this structure when the document must guide implementation across components, runtime state, configuration, background work, retries, and operational behavior. The key idea is to write a spec as an operational contract, not as a product essay.

## Why Symphony Feels Complete

Symphony feels stronger than a typical design doc because it does all of these at once:

- It separates problem, goals, non-goals, and system boundaries early.
- It names components and abstraction layers before discussing behavior.
- It defines runtime entities as typed objects with fields and normalization rules.
- It distinguishes internal service state from external tracker or user-visible state.
- It specifies configuration as a real contract: schema, defaults, precedence, coercion, reload behavior, and validation.
- It describes workflows as state transitions with triggers, guards, retries, and release behavior.
- It includes startup cleanup, restart recovery, and reconciliation instead of assuming a clean world.
- It documents optional extensions and forward-compatibility behavior explicitly.
- It adds redundant cheat-sheet sections when they help implementation.

That is the bar to aim for.

## Recommended Section Stack

Use as many of these sections as the task needs.

### 1. Problem Statement

State the operational problem, the user or system pain, and the exact system boundary. Say what the spec covers and what it intentionally leaves to other layers.

### 2. Goals and Non-Goals

Use separate lists. Goals define required outcomes. Non-goals prevent accidental scope creep.

### 3. System Overview

Describe the main components, abstraction levels, and external dependencies.

Useful subsections:
- Main components
- Abstraction or architecture layers
- External dependencies
- Trust, safety, or operational assumptions

### 4. Core Domain Model

Define implementation-facing entities and runtime objects.

For each entity or runtime object, include:
- canonical identifier
- required fields
- normalization rules
- ownership boundary
- whether it is authoritative state, derived state, or optional surface

### 5. Contract or Repository Specification

Use this section when the system consumes or publishes a structured contract such as:
- repository-owned workflow file
- API contract
- file format
- message schema
- plugin contract
- prompt template contract

This section should say how the contract is discovered, parsed, validated, and versioned.

### 6. Configuration Specification

This is one of the biggest differences between a shallow spec and a strong one.

For each config group or top-level object, include:
- field names and types
- defaults
- precedence and source resolution
- normalization and coercion semantics
- validation checks
- dynamic reload versus restart-required behavior
- how invalid config affects runtime behavior

If helpful, include a redundant config cheat sheet.

### 7. Workflows and State Changes

Describe behavior over time.

For every important lifecycle, include:
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

This is where the spec becomes truly executable.

### 8. Failure Handling and Observability

Document:
- error classes
- causes
- operator-visible symptoms
- retry, block, continue, or release behavior
- logs, metrics, status surfaces, or audit trails

If the system can partially succeed, say what happens next.

### 9. Validation and Testing

State how an implementation proves compliance.

Examples:
- validation rules
- startup or preflight checks
- required integration tests
- invariants that must hold
- restart or reconciliation scenarios

### 10. Migration, Rollout, Compatibility

Include when the change affects existing consumers, files, workspaces, data, or operators.

State:
- backward compatibility status
- migration steps
- rollout sequence
- cleanup behavior
- mixed-version assumptions if relevant

### 11. Implementation Notes or Optional Extensions

Use this section when some capabilities are optional or extension-specific. Symphony does this well by explicitly calling out extensibility and restart requirements.

Include:
- optional extensions
- forward-compatibility behavior
- unknown key handling
- implementation-defined areas
- what can vary safely between implementations

### 12. Open Questions

Keep unresolved items explicit and bounded. Do not bury them inside the main contract.

## Signature Patterns To Reuse

### Separate Internal and External State

If the system coordinates work, define its own orchestration or runtime states even when an external system already has states.

**Example from Symphony:**
> "This is not the same as tracker states (`Todo`, `In Progress`, etc.). This is the service's internal claim state."

Then defines: `Unclaimed`, `Claimed`, `Running`, `RetryQueued`, `Released`.

### Specify Source Precedence

When configuration can come from files, defaults, environment variables, or CLI flags, define the exact precedence order.

**Example from Symphony:**
> "Configuration precedence:
> 1. Workflow file path selection (runtime setting -> cwd default).
> 2. YAML front matter values.
> 3. Environment indirection via `$VAR_NAME` inside selected YAML values.
> 4. Built-in defaults."

### Specify Dynamic Reload Semantics

Say which changes apply immediately, which affect future work only, and which require restart.

**Example from Symphony:**
> "Dynamic reload is required:
> - The software should watch `WORKFLOW.md` for changes.
> - On change, it should re-read and re-apply workflow config and prompt template without restart.
> - ...Reloaded config applies to future dispatch, retry scheduling, reconciliation decisions...
> - Invalid reloads should not crash the service; keep operating with the last known good effective configuration and emit an operator-visible error."

### Specify Preflight Validation

Say what is validated at startup or before dispatch, and whether invalid configuration blocks dispatch, blocks startup, or merely logs warnings.

**Example from Symphony:**
> "Startup validation:
> - Validate configuration before starting the scheduling loop.
> - If startup validation fails, fail startup and emit an operator-visible error.
>
> Per-tick dispatch validation:
> - Re-validate before each dispatch cycle.
> - If validation fails, skip dispatch for that tick..."

### Specify Recovery Behavior

State what happens on restart, on missed watch events, on partial failure, and on terminal cleanup.

**Example from Symphony:**
> "Startup terminal workspace cleanup:
> 1. Query tracker for issues in terminal states.
> 2. For each returned issue identifier, remove the corresponding workspace directory.
> 3. If the terminal-issues fetch fails, log a warning and continue startup."

### Use Redundant Summary Sections When Helpful

If a long section is dense, add a compact summary or cheat sheet. This is good spec writing, not wasted space.

**Example from Symphony (Config Cheat Sheet):**
> "This section is intentionally redundant so a coding agent can implement the config layer quickly."

Then provides a table with all config fields.

## Chapter Writing Patterns

### Configuration Section Pattern

For each config group, write:

```markdown
#### 5.3.1 `tracker` (object)

Fields:

- `kind` (string)
  - Required for dispatch.
  - Current supported value: `linear`
- `endpoint` (string)
  - Default for `tracker.kind == "linear"`: `https://api.linear.app/graphql`
- `api_key` (string)
  - May be a literal token or `$VAR_NAME`.
  - Canonical environment variable for `tracker.kind == "linear"`: `LINEAR_API_KEY`.
  - If `$VAR_NAME` resolves to an empty string, treat the key as missing.
```

Key elements:
1. Field name and type
2. Whether required or optional
3. Default value
4. Environment variable indirection if applicable
5. Validation/constraint rules
6. Edge case handling

### State Machine Pattern

Define states first, then transitions:

```markdown
### 7.1 Issue Orchestration States

1. `Unclaimed`
   - Issue is not running and has no retry scheduled.

2. `Claimed`
   - Orchestrator has reserved the issue to prevent duplicate dispatch.

3. `Running`
   - Worker task exists and the issue is tracked in `running` map.

4. `RetryQueued`
   - Worker is not running, but a retry timer exists.

5. `Released`
   - Claim removed because issue is terminal or no longer eligible.
```

Then define triggers for each transition.

### Error Class Pattern

```markdown
Error classes:

- `missing_workflow_file`
- `workflow_parse_error`
- `template_render_error`

Dispatch gating behavior:
- Workflow file read/YAML errors block new dispatches until fixed.
- Template errors fail only the affected run attempt.
```

### Entity Definition Pattern

```markdown
#### 4.1.1 Issue

Normalized issue record used by orchestration, prompt rendering, and observability output.

Fields:

- `id` (string)
  - Stable tracker-internal ID.
- `identifier` (string)
  - Human-readable ticket key (example: `ABC-123`).
- `priority` (integer or null)
  - Lower numbers are higher priority in dispatch sorting.
```

### Hook/Callback Pattern

```markdown
#### 9.4 Workspace Hooks

Supported hooks:
- `hooks.after_create`
- `hooks.before_run`

Execution contract:
- Execute in a local shell context with the workspace directory as `cwd`.
- Hook timeout uses `hooks.timeout_ms`; default: `60000 ms`.

Failure semantics:
- `after_create` failure or timeout is fatal to workspace creation.
- `before_run` failure or timeout is fatal to the current run attempt.

## Thin vs Strong

Thin:
- Support retries.
- Read config from YAML.
- Watch for file changes.

Strong:
- Failure-driven retries use exponential backoff capped at a configured maximum.
- YAML values may reference environment variables via `$VAR_NAME`; empty expansion counts as missing.
- Invalid reloads do not crash the service; the runtime keeps the last known good config and emits an operator-visible error.

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

Collapse sections when the work is local and does not need full operational treatment. Even then, keep these concepts explicit:
- scope
- success criteria
- data or contract changes
- workflow impact
- failure behavior
- validation
