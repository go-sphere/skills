# Pipeline

Run these stages in order. The value of the skill comes from stabilizing upstream
understanding before any downstream planning.

## Stage 1 — Resolve the change boundary

Gather the mode inputs, then read the change itself.

Git diff mode: repository root, target spec path, diff base, supporting docs and
source-of-truth directories, declared or inferred surfaces.

Version comparison mode: repository root, version A path (older baseline), version B path
(newer target), supporting docs and source-of-truth directories, declared or inferred surfaces.

When the repo offers several possible supporting sources, prefer the ones closest to the spec
change and to the implementation source of truth.

In version mode, compute the semantic diff explicitly by comparing:

- added, removed, or modified sections
- changed requirements
- modified API contracts or data models
- updated workflows or behaviors

Answer before moving on:

- What changed semantically?
- Is the change additive, behavioral, breaking, deepening, or mixed?
- Which contracts, states, entities, or surfaces were touched?

## Stage 2 — `00-inputs.md`

Git diff mode records: spec path, diff base, files read, surface discovery result,
source-of-truth assumptions, missing evidence.

Version comparison mode records: version A path, version B path, files read, surface discovery
result, source-of-truth assumptions, missing evidence.

## Stage 3 — `01-spec-delta.md`

Summarize the semantic change set only. This file is the handoff contract for every downstream
artifact, so keep it free of implementation opinion.

## Stage 4 — `02-impact-map.md`

Trace the spec delta into downstream contract areas and affected surfaces. Cover:

- enums and states
- APIs and routes
- schemas and entities
- services and orchestration logic
- tests and validation
- affected surfaces
- compatibility risk

Point at concrete files or file groups, not only abstract layers. This file is the coordination
contract for API, schema, surface, and task planning.

## Stage 5 — Core deltas

Produce only what the change materially requires.

`03-api-delta.md`, when API or contract boundaries are affected, describes:

- new or changed service boundaries
- new or changed RPCs and routes
- request and response contract changes
- new or changed enums and errors
- compatibility notes

Keep it a planning contract. Do not write proto here unless the user explicitly asks.

`04-schema-delta.md`, when persistence or authoritative data shape is affected, describes:

- authoritative entities touched by the change
- field additions and removals
- enum or state persistence changes
- index and query-shape impact
- migration and rollout considerations
- authoritative versus derived state decisions

## Stage 6 — Surface artifacts

For each materially affected surface beyond the core delta set, write
`surface-<name>-impact.md` answering:

- why this surface is affected
- which modules or directories are likely touched
- which contract assumptions changed for it
- whether it consumes new data, states, actions, or errors
- what validation or review it needs

Surface artifacts focus on consumer impact, not source-of-truth redesign.

## Stage 7 — `05-task-plan.md`

Write it only after the relevant downstream artifacts are stable. Split work into executable
batches, normally in this order:

1. contract layer
2. schema layer
3. service layer
4. surface-specific consumer layers
5. test layer
6. generation and validation layer, if the repo has one

Each batch must be small enough that another agent can own it without rediscovering the whole
spec, and must depend on earlier artifacts rather than on fresh analysis.

## Stage 8 — `06-open-questions.md`

Write this only for unresolved items that matter to downstream changes. Keep each one bounded
and concrete.

## Handoff Logic

An agent consuming these artifacts reads them in this order:

1. `01-spec-delta.md`
2. `02-impact-map.md`
3. the relevant core and surface artifacts
4. `05-task-plan.md`
5. `06-open-questions.md`

## Stop Conditions

Stop and record a question instead of guessing when:

- the diff base is unclear and materially changes interpretation
- the spec references a missing contract file that is clearly authoritative
- the change might be breaking but current consumers are unknown
- the diff mixes unrelated features and cannot be described as one coherent change set
- the affected surfaces cannot be inferred safely from the repo or user input
