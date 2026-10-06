# Templates — Change Boundary Artifacts

Exact section shapes for the first three artifacts, unless the repository has an
established local variant. Downstream shapes live in `templates-downstream.md`.

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
