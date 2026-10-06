---
name: spec-writer
description: "Write or revise implementation-ready specifications for systems, APIs, workflows, and runtime services. Use to turn requirements or a vague PRD into an executable SPEC.md, to deepen a spec that reads too thin, or to revise one without leaving contradictions — including 写技术规格, 改 SPEC, 修改规范, 补技术细节, 整理实现方案. Not for tracing downstream proto or schema impact — that is `spec-diff-pipeline`."
---

# Spec Writer

Produce specs that engineers and coding agents implement from directly. A spec is an execution
contract: boundaries, typed concepts, rules, runtime behavior, validation, recovery, and failure
surfaces. Explaining intent is not enough.

## Inputs

Do not write `prd/SPEC.md` or any spec section until these are known:

- The problem being specified. "Write a spec for X" with no further context is not enough.
- New spec — the problem statement, the system boundaries, and at least one constraint.
- Revision — the path of the existing spec and what is changing.

Ask one question at a time until they are known. When a decision has several valid approaches,
present the options with a recommendation. Never pick one silently.

## Steps

First choose the job, then follow that column.

| Job | Trigger |
|-----|---------|
| New spec | No spec exists yet |
| Revision | A spec file exists and must change |
| Deepening pass | The user says the spec feels thin, vague, or weaker than a reference — run it after either job above |

### New spec

1. Fix the contract anchors: problem, goals, non-goals, constraints, operating environment, external dependencies.
2. Define boundaries before mechanisms. State what this system owns, what adjacent systems own, what it consumes, what it emits, and which actors touch it.
3. Pick the section stack. Substantial system: start from the stack in the Reference Map. Narrow change: collapse sections but keep the same logic.
4. Turn every runtime noun into a typed contract. A component, config object, state, workflow step, file, entity, queue, worker, retry entry, or event must be defined precisely enough that two implementers build compatible behavior.
5. Turn fuzzy requirements into normative rules with `must`, `should`, and `may`. Replace "support retries" with triggers, backoff, stop conditions, and release behavior. Replace "dynamic config" with source precedence, coercion, validation, and reload semantics.
6. Run the deepening pass.
7. Close with conformance: validation strategy, test expectations, migration and compatibility notes, and explicit open questions.
8. Write the file to `prd/SPEC.md`, creating the directory if needed. Report the path and ask for review before any implementation handoff.

### Revision

1. Read the whole spec before editing. Build the change map first; never patch one paragraph in isolation.
2. Classify the change as additive, behavioral, structural, breaking, or deepening.
3. Trace impacted sections with the impact matrix in `references/spec-editing.md`.
4. Keep headings, numbering, and defined terms stable unless the structure actively blocks clarity.
5. Update every downstream section the change affects. Delete contradicting text instead of letting new text outvote old text.
6. Run the deepening pass on the revised document.
7. State compatibility and rollout impact: backward compatible or not, migration required, and who must change.
8. Write the file to disk and confirm the path with the user.

### Deepening pass

A draft feels weak because semantics are missing, not because headings are missing. Walk
`references/completeness-rubric.md` section by section. For every major section, answer one
question: did I define behavior, or only describe intent? Where the answer is "intent", use the
patterns in `references/spec-patterns.md` to make config, lifecycle, entity, and failure
semantics explicit. Add a cheat-sheet section when it speeds up implementation — redundancy is
good when it removes ambiguity.

## Reference Map

| Read | When |
|------|------|
| [references/section-stack.md](references/section-stack.md) | At step 3 of a new spec, to choose the section structure and template |
| [references/spec-patterns.md](references/spec-patterns.md) | While writing a config, state-machine, entity, error, or hook section |
| [references/completeness-rubric.md](references/completeness-rubric.md) | During every deepening pass |
| [references/upgrade-patterns.md](references/upgrade-patterns.md) | When the draft still feels thin after the rubric |
| [references/spec-editing.md](references/spec-editing.md) | Before editing an existing spec, for the impact matrix and coherence check |

## Rules

1. Lead with scope, ownership, and boundaries. Implementation details come after.
2. Use precise nouns and real field names. Never "data", "info", or "metadata" alone.
3. Define canonical identifiers and normalization rules wherever names or IDs can drift.
4. Separate internal state from external or user-facing state when both exist.
5. Use lists or tables for schemas, config fields, enum values, states, error classes, and precedence rules.
6. State defaults, invariants, and guard conditions anywhere ambiguity could cause drift.
7. Make dynamic behavior explicit: reload, retries, cleanup, reconciliation, restart recovery, eventual consistency.
8. Keep rationale short. Spend the document on the contract.
9. Never stop at "supports X". Continue until the spec says how X behaves.

## Output

Default section order for a substantial spec, unless the user asks for another format:

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

Sections 5 and 6 may merge into `Contracts and Configuration` for simpler systems. Add
`Normative Examples` or `Cheat Sheet` subsections when they materially reduce ambiguity. For a
local edit, keep the existing document shape and append a short change summary.

## Related Skills

- Upstream — `prd` and `ux-analyst` supply product and behavior context; use `interview-me` when key decisions are still unresolved. When those artifacts are missing, write from what the user provides and record assumptions rather than inventing context.
- Downstream — `db-schema-designer` for the data model and `proto-api-generator` for contracts; hand off once the spec tells one coherent story from goals through conformance. Use `spec-diff-pipeline` after the spec is edited again.
- Boundary — use `prd` for product framing and success metrics; this skill owns the engineering contract. Use `spec-diff-pipeline` to analyze downstream impact; this skill performs the edit.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
