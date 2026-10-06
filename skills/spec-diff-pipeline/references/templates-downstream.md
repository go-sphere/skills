# Templates — Downstream Planning Artifacts

Exact section shapes for the delta, surface, task-plan, and open-questions artifacts.
The change-boundary shapes live in `templates-upstream.md`.

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
