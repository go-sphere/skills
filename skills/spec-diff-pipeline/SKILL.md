---
name: spec-diff-pipeline
description: Turn a changed spec into downstream planning artifacts — spec delta, impact map, API delta, schema delta, per-surface impact, task plan, open questions. Use when a SPEC.md changed, when comparing two version files (v0/v1), or on 分析 spec diff 影响, 生成 impact map, 刷新 proto/schema 规划, 拆 implementation tasks, 哪些端受影响. Not for writing or repairing the spec itself — that is `spec-writer`.
---

# Spec Diff Pipeline

Turn one spec change into a stable set of planning artifacts that other agents can execute
from. This skill only plans. Never edit proto, schema, service, generated, or client code here.

## Inputs

Confirm the paths before step 1. Ask for a missing path one question at a time.

| Mode | Required paths |
|------|----------------|
| Git diff | `repo_root`, `spec_path`, `diff_base` (default `HEAD`, read the working-tree diff) |
| Version comparison | `repo_root`, `version_a_path` (older), `version_b_path` (newer) |

Supporting evidence — nearby PRD, proto folders, schema docs, surface directories — may be
inferred from the repository. Record every gap in `06-open-questions.md` rather than stalling.

## Steps

1. Read the change directly. Git diff mode: read the spec, then read `git diff <diff_base> -- <spec_path>`. Version mode: read both files and compare them section by section. Never work from memory of the spec.
2. Identify the affected surfaces, then write `00-inputs.md`.
3. Write `01-spec-delta.md`: the semantic change set plus its classification.
4. Write `02-impact-map.md`: downstream implications, each pointing at a concrete file or file group.
5. Write `03-api-delta.md` when contract boundaries moved. Write `04-schema-delta.md` when persistence moved. Skip either file when nothing material changed there.
6. Write one `surface-<name>-impact.md` per materially affected surface beyond the core three.
7. Write `05-task-plan.md` from the artifacts above, then `06-open-questions.md` if anything is unresolved.

Run steps 1-4 yourself in order. Steps 5 and 6 may fan out to subagents, but only after
`02-impact-map.md` exists.

## Reference Map

| Read | When |
|------|------|
| [references/pipeline.md](references/pipeline.md) | Always, before step 1 — stage order, per-artifact content, stop conditions |
| [references/change-classification.md](references/change-classification.md) | Before step 3, to label the change |
| [references/templates-upstream.md](references/templates-upstream.md) | Before writing `00-inputs.md`, `01-spec-delta.md`, `02-impact-map.md` |
| [references/templates-downstream.md](references/templates-downstream.md) | Before writing any delta, surface, task-plan, or open-questions file |

## Rules

1. A surface is any downstream consumer or delivery boundary: backend, dashboard/admin, mobile app, web app, bot, SDK, CLI, batch worker, partner-facing API. Infer the set from user input, repository structure, and spec semantics. Never hard-code how many there are.
2. Create a `surface-*` artifact only when the diff materially affects that surface. The folder existing in the repo is not a reason.
3. Tie every downstream effect to an explicit spec change. No effect without a cited cause.
4. Classify every change as additive, behavioral, breaking, deepening, or mixed. For mixed, enumerate the parts separately.
5. Separate authoritative state from derived or read-model state.
6. Name concrete files, directories, modules, or surface owners whenever local evidence exists.
7. If the diff is editorial only, say so and keep downstream impact minimal.
8. Write no implementation code, and no proto, in these artifacts.
9. Never call a migration safe without saying why it is safe.
10. Keep uncertainty in `06-open-questions.md`. Do not bury it inside the other artifacts.

## Output

Write every artifact under `design/changes/<change-id>/`. Create the directory. Do not write
into the current directory or straight into a path the user named for something else.

Choose `<change-id>` like this:

- The user gave a path such as `design/changes/payment-retry-v2/` — use that id.
- Git diff mode — derive it from the change purpose: a payment retry change in `prd/SPEC.md` becomes `payment-retry-v2`.
- Version mode — combine the spec name and the versions: `SPEC_V0.md` vs `SPEC_V1.md` becomes `payment-system-v0-to-v1`.

Produce the core files in this order: `00-inputs.md`, `01-spec-delta.md`, `02-impact-map.md`,
`03-api-delta.md`, `04-schema-delta.md`, `05-task-plan.md`, `06-open-questions.md`. Add
`surface-<name>-impact.md` files alongside them, for example `surface-mobile-impact.md`.

Before finishing, confirm all of these:

1. The diff was read from git or from the two version files, not recalled.
2. Each artifact points back to concrete spec changes.
3. The API and schema deltas agree with each other.
4. Surface artifacts exist only for materially affected surfaces.
5. The task plan depends on the deltas instead of re-analyzing the spec.
6. In version mode, `00-inputs.md` records both paths and `01-spec-delta.md` states the computed diff.

## Related Skills

- Upstream — `spec-writer` must have produced a changed SPEC or a v0/v1 pair; this skill reads the diff directly instead of inferring it from memory.
- Downstream — the task plan fans out to `proto-api-generator` and `db-schema-designer` to refresh contracts and schemas, to `sphere-feature-workflow` to execute the batches, and to `frontend-crud-generator` once the frontend surface has a generated client. Hand off when `05-task-plan.md` is complete and open questions are isolated.
- Boundary — use `spec-writer` to write or repair the spec itself; this skill never edits the spec, it only traces downstream impact.
- Companion — none.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
