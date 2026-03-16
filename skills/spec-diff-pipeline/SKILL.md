---
name: spec-diff-pipeline
description: Analyze a changed SPEC or other technical specification from git diff or two version files (v0, v1) and automatically produce downstream planning artifacts such as spec delta, impact map, API/proto delta, schema delta, surface-specific impact reports, task plan, and open questions. Use whenever the user has modified SPEC.md or another design/spec file and wants an AI-run pipeline that reads the diff (either from git or by comparing two version files), traces downstream impact, and prepares implementation-planning markdown outputs for whatever affected surfaces exist in the repo, even if they only say things like 根据 spec diff 分析影响, 刷新 proto/schema 规划, 生成 impact map, 拆 implementation tasks, 分析哪些端受影响, or 对比 v0 v1 版本差异.
---

# Spec Diff Pipeline

## Overview

Use this skill to turn a spec change into a stable set of planning artifacts that downstream agents can consume. The skill is intentionally pure AI-driven: it reads repository files and git diff, reasons about contract impact, and writes markdown outputs. It does not depend on custom automation scripts.

This skill is for planning and change analysis, not implementation. Do not edit proto, schema, service, generated files, or client code unless the user explicitly asks for that in a later step.

Read [references/pipeline.md](references/pipeline.md) for the stage order, [references/artifact-templates.md](references/artifact-templates.md) for exact output shapes, and [references/change-classification.md](references/change-classification.md) before drafting artifacts.

## When To Use

Use this skill when the user has already changed a spec or wants to analyze a spec diff and then:
- generate an impact map
- refresh API/proto planning
- refresh DB/Ent/schema planning
- identify which product surfaces are affected
- break implementation into tasks
- prepare a contract-first change bundle for other agents

This skill is especially appropriate when the user mentions:
- `SPEC.md`
- git diff
- version comparison (v0, v1, version A vs B)
- 版本对比
- impact map
- API delta
- proto delta
- schema delta
- implementation checklist
- task plan
- downstream planning after spec changes
- 哪些端受影响
- 哪些模块要跟着改

<HARD-GATE>
Do not start the pipeline until the mode-specific path inputs are confirmed:
- **Git Diff Mode**: `repo_root` and `spec_path` must be known.
- **Version Comparison Mode**: `repo_root`, `version_a_path`, and `version_b_path` must be known.

Ask the user for any missing path inputs one at a time before proceeding to Stage 1.
Supporting files (PRD, proto folders, schema docs, surface directories) can be provided later or inferred from the repository — record any gaps in `06-open-questions.md`.
</HARD-GATE>

## Required Inputs

Before starting, identify these inputs explicitly:

### Mode 1: Git Diff Mode

1. `repo_root`
2. `spec_path`
3. `diff_base`
   - Prefer the user-provided base.
   - If none is provided, default to `HEAD` and analyze the working tree diff.

### Mode 2: Version Comparison Mode

1. `repo_root`
2. `version_a_path` - The older version (e.g., v0.md, SPEC_v0.md, or baseline)
3. `version_b_path` - The newer version (e.g., v1.md, SPEC_v1.md, or target)
4. Both paths should be absolute or relative to `repo_root`

### Supporting Files (Both Modes)

- supporting files or directories that define current reality
  - nearby PRD or requirements docs
  - API docs or proto folders
  - schema or DDL docs
  - source-of-truth entity/schema folders
  - surface-specific directories if they exist, such as mobile, dashboard, web, backend, admin, bot, sdk, or CLI folders
- optional user-declared surfaces
  - If the user already names affected surfaces, use that as a strong hint.
  - If not, infer surfaces from the repository and the spec change.

If a required supporting source is missing, continue with the best available evidence and record the gap in `06-open-questions.md`.

## Surface Discovery Rule

Do not hard-code the number of product surfaces.

A `surface` is any downstream consumer or delivery boundary that may need coordinated changes because of the spec diff, for example:
- backend
- dashboard/admin
- mobile app
- web app
- bot
- SDK
- CLI
- batch worker
- partner-facing API

At the start of the pipeline, identify the impacted surfaces from:
- explicit user input
- repository structure
- spec semantics
- impact map evidence

Write the discovered set into `00-inputs.md`. Only produce surface-specific artifacts for surfaces that are materially affected.

## Output Contract

Write artifacts under:

`design/changes/<change-id>/`

**IMPORTANT**: Always create the output directory structure. Do NOT write files directly to the user's specified output directory or the current directory. The artifacts MUST be in `design/changes/<change-id>/`.

**How to choose `<change-id>`**:

For Git Diff Mode:
- Extract a short identifier from the spec filename or change purpose
- Example: `prd/SPEC.md` with payment retry changes → `payment-retry-v2`

For Version Comparison Mode:
- Use a combination of spec name and version identifiers
- Example: comparing `user-service-v0.md` and `user-service-v1.md` → `user-service-evolution`
- Example: comparing `SPEC_V0.md` and `SPEC_V1.md` → `payment-system-v0-to-v1`

If the user explicitly provides an output path like `design/changes/some-id/`, use that as the change-id. Otherwise, derive it from the spec content.

Always produce these core files in order:

1. `00-inputs.md`
2. `01-spec-delta.md`
3. `02-impact-map.md`
4. `03-api-delta.md` when API or contract surfaces are affected
5. `04-schema-delta.md` when persistence surfaces are affected
6. `05-task-plan.md`
7. `06-open-questions.md` only when needed

Additionally, produce one file per materially affected non-core surface using this pattern:

- `surface-<name>-impact.md`

Examples:
- `surface-mobile-impact.md`
- `surface-dashboard-impact.md`
- `surface-web-impact.md`
- `surface-sdk-impact.md`

Use the templates in [references/artifact-templates.md](references/artifact-templates.md).

## Execution Modes

### Default Sequential Mode

Run the stages in order yourself.

### Parallel Agent Mode

If subagents are available, use them only after the change boundary is stable:
- Create `01-spec-delta.md` and `02-impact-map.md` locally first.
- Then create `03-api-delta.md`, `04-schema-delta.md`, and any `surface-*-impact.md` files in parallel when appropriate.
- Create `05-task-plan.md` only after the relevant downstream artifacts are complete.

Do not fan out before the impact map exists.

## Workflow

### Stage 1: Resolve the change boundary

#### For Git Diff Mode:

1. Read the target spec file.
2. Read the git diff for that spec against `diff_base`.
3. Read only the nearby documents needed to understand the changed semantics.
4. Discover the likely impacted surfaces.
5. Write `00-inputs.md` and `01-spec-delta.md`.

#### For Version Comparison Mode:

1. Read both version files (`version_a_path` and `version_b_path`).
2. Compute the semantic diff between the two versions by comparing:
   - Added, removed, or modified sections
   - Changed requirements or specifications
   - Modified API contracts or data models
   - Updated workflows or behaviors
3. Read only the nearby documents needed to understand the changed semantics.
4. Discover the likely impacted surfaces.
5. Write `00-inputs.md` and `01-spec-delta.md`.

At this stage, answer:
- What changed semantically?
- Is the change additive, behavioral, breaking, deepening, or mixed?
- Which contracts, states, entities, or surfaces were touched?

### Stage 2: Build the impact map

Read the changed spec sections and current source-of-truth files.

Write `02-impact-map.md` with concrete downstream implications for:
- enums and states
- APIs and routes
- schemas and entities
- services and orchestration logic
- tests and validation
- affected surfaces
- compatibility risk

The impact map must point to concrete files or file groups, not only abstract layers.

### Stage 3: Refresh core planning artifacts

Produce only the core artifacts that the spec change materially requires.

#### API planning

Use the spec delta and impact map to write `03-api-delta.md` when API or contract boundaries are affected.

This artifact should describe:
- new or changed service boundaries
- new or changed RPCs/routes
- request/response contract changes
- new or changed enums and errors
- compatibility notes

Do not generate actual proto code here unless explicitly requested. Keep this artifact as a planning contract.

#### Schema planning

Use the spec delta and impact map to write `04-schema-delta.md` when persistence or authoritative data shape is affected.

This artifact should describe:
- authoritative entities touched by the spec change
- field additions or removals
- enum or state persistence changes
- index or query-shape impact
- migration or rollout considerations
- authoritative versus derived state decisions

### Stage 4: Generate surface-specific impact artifacts

For each materially affected surface beyond the core spec/api/schema planning set, create `surface-<name>-impact.md`.

A surface impact artifact should answer:
- why this surface is affected
- which modules or directories are likely touched
- what contract assumptions changed for that surface
- whether the surface consumes new data, new states, new actions, or new errors
- what validation or review is needed on that surface

Do not create a surface artifact just because the repo contains the folder. Create it only if the spec diff materially affects that surface.

### Stage 5: Split implementation tasks

Write `05-task-plan.md` only after the relevant downstream artifacts are stable.

Split work into executable batches, usually in this order:
1. contract layer
2. schema layer
3. service layer
4. surface-specific consumer layers
5. test layer
6. generation/validation layer if the repo uses them

Tasks should be small enough that another agent can own one batch without rediscovering the whole spec.

### Stage 6: Record uncertainty explicitly

If anything is unresolved, write `06-open-questions.md`.

Do not bury uncertainty inside the other artifacts. Open questions should be bounded and concrete.

## Writing Rules

- Prefer concrete semantic change statements over prose summaries.
- Always distinguish these categories when relevant:
  - additive
  - behavioral
  - breaking
  - deepening
- Tie every downstream effect to an explicit spec change.
- Separate authoritative state from derived/read-model state.
- Name concrete files, directories, modules, or surface owners whenever local evidence exists.
- If the spec diff is editorial only, say so and keep the downstream impact minimal.
- If the spec introduced a stronger contract without changing intended behavior, classify it as `deepening` and explain which layers may still need tightening.
- Do not write implementation code in these artifacts.
- Do not silently assume migrations are safe; say why you believe they are safe.
- Do not hard-code surface count. Infer it from the repo and the change.

## Completion Check

Before finishing, confirm:
- the spec diff was read directly (from git diff OR from version comparison), not inferred from memory
- each artifact points back to concrete spec changes
- API and schema deltas are consistent with each other
- surface-specific artifacts exist only for materially affected surfaces
- the task plan depends on the deltas instead of re-analyzing the spec from scratch
- open questions are isolated rather than mixed into the main artifacts

For Version Comparison Mode specifically, also confirm:
- `00-inputs.md` documents both version file paths
- The diff between versions is explicitly computed and described in `01-spec-delta.md`

## Resources

- Read [references/pipeline.md](references/pipeline.md) for the agent pipeline order and handoff logic.
- Read [references/artifact-templates.md](references/artifact-templates.md) for exact markdown sections.
- Read [references/change-classification.md](references/change-classification.md) to classify spec changes correctly.
