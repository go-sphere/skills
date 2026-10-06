---
name: sphere-layout-sync
description: Update a generated go-sphere project to a newer layout revision, or adopt a legacy project into the layout contract. Use to pull upstream layout changes into a project, resolve layout drift, set up `.sphere/layout.lock.json` for a pre-contract project, or diagnose why a layout upgrade conflicts. Not for ordinary feature work — that is `sphere-feature-workflow`.
---

# Sphere Layout Sync

A generated go-sphere project keeps receiving upstream layout changes. This skill performs that
merge without destroying project code, and without silently reverting layout fixes.

## Inputs

Do not modify any file until all three are established:

1. `.sphere/layout.lock.json` exists and its `schema_version` is one you understand.
2. The target upstream revision is resolved to a concrete commit SHA.
3. The working tree is clean, or the user explicitly accepted syncing over local changes.

If `schema_version` is unknown to you, stop and report it. Never guess the lock format.

If there is no lock file at all, this is a legacy adoption. Read
`references/legacy-adoption.md` and do not start a normal sync.

Read the project's own contract first, in this order. These copies outrank this skill wherever they
disagree:

1. `.sphere/layout.lock.json` — which layout, which ref, which base revision.
2. `.sphere/layout.json` — ownership patterns for this layout.
3. `docs/LAYOUT_CONTRACT.md` — the authoritative protocol.
4. `AGENTS.md` — layout profile and extension seams.

## Steps

1. **Resolve.** Read the contract and the lock. Resolve the requested target revision; with none specified, resolve the current commit of the recorded `ref`.
2. **Materialize.** Check out the base and target upstream commits into separate temporary directories. Never run their code just to compute a diff.
3. **Normalize the module path.** Rewrite both snapshots from `upstream_module` to the project's current Go module path *before* comparing. Skipping this makes every import line look changed and buries the real diff.
4. **Merge by ownership class**, using the table below. Exclude generated files before you compare — diffing them is wasted work at best and a source of bogus conflicts at worst.
5. **Resolve deletions and renames carefully.** When a file was deleted or renamed both locally and upstream, settle ownership before recreating it. Never resolve a conflict by discarding project code.
6. **Regenerate and verify.** Regenerate through the layout Makefile, then run formatting, dependency checks, tests, lint, and build — typically `make gen/all`, `make check`, `make build`. Review the complete diff.
7. **Commit the lock last.** Update `base_revision` only after every conflict is resolved and verification succeeds. If blocked, leave the lock unchanged and report the affected paths.

Step 7 is the safety property. A lock still pointing at the old base means "this sync did not
finish", which is recoverable. A prematurely advanced lock loses that information permanently.

Patterns in `.sphere/layout.json` are evaluated in this order, first match wins: `generated`, then
`layout_owned`, then `mixed`, then the default `project_owned`.

| Class | Sync action |
|-------|-------------|
| `generated` | Ignore upstream contents entirely. Regenerate from the merged handwritten sources afterwards. |
| `layout_owned` | Apply the upstream change directly when the local copy still equals the recorded base. Otherwise three-way merge. |
| `mixed` | Always perform a semantic three-way merge of base, local, and target. |
| `project_owned` | Never replace merely because upstream changed. |

## Reference Map

| Read | When |
|------|------|
| [references/legacy-adoption.md](references/legacy-adoption.md) | The project has no `.sphere/layout.lock.json` — read this instead of starting a sync |
| [references/layout-release-checklist.md](references/layout-release-checklist.md) | The change is to a layout repository itself, not to a generated project |

## Rules

Stop and report instead of improvising when any of these is true:

1. `schema_version` is unrecognized.
2. The recorded `base_revision` is not reachable in the upstream repository.
3. A `project_owned` file would have to be overwritten to make the merge succeed.
4. Generated output still drifts after a full regeneration.
5. Tests or the build fail and the cause is a merge decision rather than a pre-existing issue.

In every case, report the affected paths and the decision you could not make, and leave the lock
untouched.

## Output

State all of these:

1. The layout variant and the lock status.
2. The base and target revisions.
3. A per-class summary of what was applied, merged, ignored, and left alone.
4. Every conflict and how it was resolved.
5. The regeneration and verification commands run, with their results.
6. Whether `base_revision` was advanced — and if not, why.

## Related Skills

- Upstream — none; this skill is event-driven, triggered by layout drift, a new layout revision, or adopting a project that predates the lock contract.
- Downstream — `sphere-feature-workflow` once the lock has advanced and the project is back inside the contract; `go-sphere-makefiles` when the layout-repository checklist is in scope. Hand off after reporting the per-class summary and verification results.
- Boundary — use `sphere-feature-workflow` for ordinary feature work inside a project; this skill owns layout revision movement, drift resolution, and legacy adoption.
- Companion — `go-sphere-makefiles` for Make and CI correctness across layout repositories; if it is unavailable, report the Makefile concerns instead of editing them here.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
