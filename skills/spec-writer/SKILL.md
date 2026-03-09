---
name: spec-writer
description: "Write or revise implementation-ready specifications for products, systems, APIs, workflows, runtime services, and technical designs. Use when asked to create a new spec from requirements, rewrite an ambiguous PRD or design doc into an executable SPEC.md, deepen an existing specification that feels too thin or hand-wavy, update a spec after scope changes, or modify a specification without leaving contradictions. Trigger on requests such as write spec, rewrite PRD as spec, improve this SPEC.md, make the spec more complete, modify spec, 修改规范, 写技术规格, 改 SPEC, 补技术细节, or 整理实现方案."
---

# Spec Writer

## Overview

Use this skill to produce specs that engineers and coding agents can implement from directly. Treat the spec as an execution contract: it should define boundaries, typed concepts, rules, runtime behavior, validation, recovery, and failure surfaces, not just explain intent.

Use a Symphony-like style when the system has components, configuration, state transitions, background behavior, retries, or operator concerns. Symphony feels strong not only because it has sections, but because each section keeps going until the runtime semantics are unambiguous. Read [references/symphony-style.md](references/symphony-style.md) for the structural model, [references/completeness-rubric.md](references/completeness-rubric.md) for the deepening checklist, and [references/spec-editing.md](references/spec-editing.md) when revising an existing document.

## Workflow Decision Tree

1. Identify the job type.
   **Creating a new spec?** Follow `New Spec Workflow`.
   **Modifying an existing spec?** Follow `Revision Workflow`.
   **User says the current spec feels thin, vague, or less complete than a strong reference?** Follow `Deepening Pass` after drafting or editing.

2. Size the spec.
   **Local feature or narrow change?** Use only the sections that materially matter.
   **System, platform, workflow, agent service, or multi-component runtime?** Use the full section structure and the completeness rubric.

3. Choose the output mode.
   **Full spec requested?** Return a full document.
   **Existing file should be updated?** Edit the file directly when possible and keep numbering stable.
   **Exploratory request?** Provide the proposed section map, major assumptions, and what details are still missing.

## New Spec Workflow

1. Distill the request into the initial contract anchors:
   - problem
   - goals
   - non-goals
   - constraints
   - operating environment
   - external dependencies

2. Define system boundaries before mechanisms.
   State what the system owns, what adjacent systems own, what inputs it consumes, what outputs it emits, and which actors interact with it.

3. Choose the section stack.
   - For substantial systems, start from the template in `references/symphony-style.md`.
   - For smaller scopes, collapse sections but preserve the same logic.

4. Expand every runtime noun into a typed contract.
   If the spec mentions a component, config object, state, workflow step, file, entity, queue, worker, retry entry, or event, define it precisely enough that two implementers would build compatible behavior.

5. Convert fuzzy requirements into normative rules.
   - Prefer `must`, `should`, and `may` when the distinction matters.
   - Turn vague statements into triggers, guards, limits, defaults, and side effects.
   - Replace "support retries" with retry triggers, backoff semantics, stop conditions, and release behavior.
   - Replace "dynamic config" with source precedence, coercion rules, validation rules, and reload semantics.

6. Run the `Deepening Pass`.
   This is mandatory for any spec that resembles a service, platform, daemon, orchestration system, workflow engine, or stateful backend.

7. Finish with conformance clarity.
   Include validation strategy, test expectations, migration or compatibility notes, implementation notes when needed, and explicit open questions.

## Revision Workflow

1. Read the current spec end to end before editing.
   Do not patch one paragraph in isolation. Build an impact map first.

2. Classify the change.
   - additive: new capability or section without changing existing semantics
   - behavioral: existing semantics change
   - structural: section layout or ownership model changes
   - breaking: external contract, state model, compatibility, or data shape changes
   - deepening: semantics stay similar, but the spec must become more explicit and operational

3. Trace impacted sections before writing.
   At minimum check these links:
   - problem/goals -> non-goals, validation, rollout
   - components -> workflows, dependencies, observability
   - entities/schemas -> contracts, examples, migration, tests
   - configuration -> defaults, precedence, validation, reload behavior
   - lifecycle/state -> retries, cancellation, cleanup, recovery, status surfaces
   - failure handling -> error classes, operator actions, logging, retry rules

4. Preserve stability where possible.
   - keep headings and numbering stable unless the structure is actively harmful
   - keep defined terminology stable
   - prefer explicit replacements over semantic drift hidden in prose

5. Update all affected contracts.
   If one section changes behavior, update every downstream section that relies on that behavior. Remove contradictions rather than letting new text outvote old text.

6. Run the `Deepening Pass` on the revised document.
   This is how to avoid the common failure mode where a spec has the right headings but still feels shallow.

7. Mark compatibility and rollout impact.
   State whether the change is backward compatible, what migration is required, and whether operators, clients, or data stores must change.

8. Finish with a delta check.
   Confirm the revised spec still tells one coherent story from goals through conformance.

## Deepening Pass

If the draft feels weaker than a strong reference such as Symphony, the problem is usually missing semantic depth rather than missing section titles. Run this pass deliberately.

1. For every major section, ask: did I define behavior or only describe intent?

2. For each configuration surface, make the following explicit:
   - field names and types
   - defaults
   - source precedence
   - environment-variable indirection if relevant
   - coercion or normalization semantics
   - invalid value handling
   - whether changes apply dynamically or require restart

3. For each lifecycle or workflow, make the following explicit:
   - internal states versus external/user-visible states
   - legal transitions
   - transition triggers
   - guard conditions
   - side effects
   - retry and cancellation rules
   - cleanup and release behavior
   - restart recovery or reconciliation behavior when relevant

4. For each core entity or runtime object, make the following explicit:
   - canonical identifier
   - required fields
   - normalization rules
   - ownership boundary
   - whether it is authoritative state, derived state, or an optional surface

5. For each failure surface, make the following explicit:
   - error classes
   - what causes each class
   - operator-visible symptom
   - whether the system retries, releases, blocks, or continues
   - what gets logged or surfaced

6. For each extension point or optional subsystem, make the following explicit:
   - whether it is core or optional
   - what unknown keys or values should do
   - forward-compatibility behavior
   - whether restart is required when it changes

7. Add a cheat-sheet or summary section when it helps implementation.
   Symphony uses intentionally redundant summaries for fast implementation. Redundancy is good when it reduces ambiguity.

8. Read [references/completeness-rubric.md](references/completeness-rubric.md) and [references/upgrade-patterns.md](references/upgrade-patterns.md) if the draft still feels thin.

## Writing Rules

- Lead with scope, ownership, and boundaries before implementation details.
- Prefer precise nouns and field names over generic words like "data", "info", or "metadata".
- Define canonical identifiers and normalization rules when names or IDs can drift.
- Separate internal state from external or user-facing state when both exist.
- Use lists or tables for schemas, config fields, enum values, states, error classes, and precedence rules.
- State defaults, invariants, and guard conditions wherever ambiguity could cause implementation drift.
- Make dynamic behavior explicit: reload semantics, retries, cleanup, reconciliation, restart recovery, or eventual consistency.
- Use short rationale only where it clarifies a design choice. Spend most of the document on the contract itself.
- Prefer normative examples, cheat sheets, and summary tables when they make implementation faster.
- Do not stop at "supports X". Continue until the spec says how X behaves.

## Writing Patterns

### Configuration Section

For each config field, always specify:
- **Type**: string, integer, boolean, object, etc.
- **Required/Optional**: Is it required or optional?
- **Default**: What is the default value?
- **Source**: Can it come from environment variables? What is the precedence?
- **Validation**: Any constraints or validation rules?
- **Reloading**: Does it support dynamic reload or require restart?

Example format:
```markdown
- `poll_interval_ms` (integer or string integer)
  - Default: `30000`
  - Changes should be re-applied at runtime and affect future tick scheduling without restart.
```

### State Machine

Define:
1. **States**: List all possible states
2. **Transitions**: What triggers each transition
3. **Guard conditions**: What must be true for a transition
4. **Side effects**: What happens when entering/exiting a state

### Entity Definition

For each entity:
- Canonical identifier field
- Required fields
- Optional fields with defaults
- Normalization/coercion rules
- Ownership boundary

### Error Handling

For each error:
- Error name/identifier
- What triggers it
- Operator-visible symptom
- Retry/block/continue behavior
- What gets logged

## Output Expectations

Use this default order for substantial specs unless the user requests a different format:

1. Problem Statement
2. Goals and Non-Goals
3. System Overview
4. Core Domain Model
5. Contract or Repository Specification
6. Configuration Specification
7. Workflows and State Changes
8. Failure Handling and Observability
9. Validation and Testing
10. Migration, Rollout, or Compatibility Notes
11. Implementation Notes or Optional Extensions
12. Open Questions

Notes:
- Sections 5 and 6 may collapse into a single `Contracts and Configuration` section for simpler systems.
- Include `Normative Examples` or `Cheat Sheet` subsections when they materially reduce ambiguity.
- For local edits, keep the existing document shape when possible and add a short change summary after editing.

## Resources

- Read [references/symphony-style.md](references/symphony-style.md) to mirror the structural strengths of OpenAI's Symphony spec without copying it.
- Read [references/completeness-rubric.md](references/completeness-rubric.md) when the output needs to feel more complete, operational, or implementation-ready.
- Read [references/upgrade-patterns.md](references/upgrade-patterns.md) when upgrading a thin spec into a stronger one.
- Read [references/spec-editing.md](references/spec-editing.md) when updating an existing spec or checking change completeness.
