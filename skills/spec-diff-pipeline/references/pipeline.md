# Pipeline

Use this sequence exactly. The value of the skill comes from stabilizing upstream understanding before downstream planning.

## 1. Resolve Inputs

Identify the mode and gather inputs:

### Git Diff Mode:
- repository root
- target spec file path
- diff base (git ref or description)
- supporting docs and source-of-truth directories
- declared or inferred affected surfaces

### Version Comparison Mode:
- repository root
- version A path (older version, baseline)
- version B path (newer version, target)
- supporting docs and source-of-truth directories
- declared or inferred affected surfaces

If the repo contains multiple possible supporting sources, prefer the ones closest to the spec change and the implementation source of truth.

## 2. Generate `00-inputs.md`

### Git Diff Mode:
Document:
- spec path
- diff base
- files read
- surface discovery result
- assumptions about source-of-truth files
- missing evidence

### Version Comparison Mode:
Document:
- version A path (baseline/older)
- version B path (target/newer)
- files read
- surface discovery result
- assumptions about source-of-truth files
- missing evidence

## 3. Generate `01-spec-delta.md`

Summarize the semantic change set only. This file is the handoff contract for all downstream artifacts.

## 4. Generate `02-impact-map.md`

Trace the spec delta into downstream contract areas and affected surfaces. This file is the coordination contract for API, schema, surface, and task planning.

## 5. Generate downstream artifacts

These can be created in parallel after the impact map exists.

### Core artifacts
- `03-api-delta.md` when contract boundaries are affected
- `04-schema-delta.md` when persistence boundaries are affected

### Surface artifacts
For each materially affected surface:
- `surface-<name>-impact.md`

Surface artifacts focus on consumer impact, not source-of-truth redesign.

## 6. Generate `05-task-plan.md`

Split implementation into ordered batches. Each batch should depend on earlier artifacts, not on fresh rediscovery.

## 7. Generate `06-open-questions.md` when needed

Write this only for unresolved items that matter to downstream changes.

## Handoff Logic

When another agent consumes these artifacts, the expected reading order is:
1. `01-spec-delta.md`
2. `02-impact-map.md`
3. any relevant core and surface artifacts
4. `05-task-plan.md`
5. `06-open-questions.md`

## Stop Conditions

Stop and record questions instead of guessing when:
- the diff base is unclear and materially changes interpretation
- the spec references a missing contract file that is clearly authoritative
- the change might be breaking but current consumers are unknown
- the spec diff mixes multiple unrelated features and cannot be described coherently as one change set
- the set of affected surfaces cannot be inferred safely from the repo or user input
