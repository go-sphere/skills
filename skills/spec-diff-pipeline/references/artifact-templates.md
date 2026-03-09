# Artifact Templates

Use these exact section shapes unless the repository has an established local variant.

## `00-inputs.md`

### Git Diff Mode

```md
# Inputs

## Repo Root
- `<path>`

## Target Spec
- `<path>`

## Diff Base
- `<git ref or description>`

## Files Read
- `<path>`
- `<path>`

## Affected Surfaces
- `<surface>`
- `<surface>`

## Source-of-Truth Assumptions
- `<assumption>`

## Missing Evidence
- `<gap>`
```

### Version Comparison Mode

```md
# Inputs

## Repo Root
- `<path>`

## Version A (Baseline)
- `<path to older version>`

## Version B (Target)
- `<path to newer version>`

## Files Read
- `<path>`
- `<path>`

## Affected Surfaces
- `<surface>`
- `<surface>`

## Source-of-Truth Assumptions
- `<assumption>`

## Missing Evidence
- `<gap>`
```

## `01-spec-delta.md`

```md
# Spec Delta

## Change Summary
- `<one-sentence semantic summary>`

## Change Classification
- `<additive|behavioral|breaking|deepening|mixed>`

## Changed Semantics
- `<semantic change>`
- `<semantic change>`

## Affected Contract Areas
- enums and states: `<summary>`
- APIs and routes: `<summary>`
- schema and entities: `<summary>`
- services and orchestration: `<summary>`
- affected surfaces: `<summary>`
- tests and validation: `<summary>`

## Notes
- `<important caveat>`
```

## `02-impact-map.md`

```md
# Impact Map

## Enums and States
- `<impact>`

## APIs and Routes
- `<impact>`

## Schemas and Entities
- `<impact>`

## Services and Orchestration
- `<impact>`

## Surface Impact Summary
- `<surface>: <impact>`

## Tests and Validation
- `<impact>`

## Compatibility Risk
- `<risk>`

## Blocking Questions
- `<question>`
```

## `03-api-delta.md`

```md
# API Delta

## Service Boundary Changes
- `<change>`

## Route or RPC Changes
- `<change>`

## Message Contract Changes
- `<change>`

## Enum and Error Changes
- `<change>`

## Compatibility Notes
- `<note>`

## Candidate Files
- `<path or directory>`
```

## `04-schema-delta.md`

```md
# Schema Delta

## Entity Changes
- `<change>`

## Field Changes
- `<change>`

## State Persistence Changes
- `<change>`

## Index or Query Impact
- `<change>`

## Authoritative vs Derived
- `<decision>`

## Migration Notes
- `<note>`

## Candidate Files
- `<path or directory>`
```

## `surface-<name>-impact.md`

```md
# Surface Impact: <name>

## Why This Surface Is Affected
- `<reason>`

## Contract Changes Consumed By This Surface
- `<change>`

## Likely Touched Modules
- `<path or module>`

## UX or Consumer Behavior Impact
- `<impact>`

## Validation or Review Needs
- `<check>`
```

## `05-task-plan.md`

```md
# Task Plan

## Phase 1: Contract Layer
- `<task>`

## Phase 2: Schema Layer
- `<task>`

## Phase 3: Service Layer
- `<task>`

## Phase 4: Surface Layers
- `<task>`

## Phase 5: Test Layer
- `<task>`

## Validation and Generation
- `<command or check>`

## Dependency Notes
- `<ordering or ownership note>`
```

## `06-open-questions.md`

```md
# Open Questions

## Questions
- `<question>`

## Why It Matters
- `<impact>`

## Suggested Resolution Path
- `<next step>`
```
