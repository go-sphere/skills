---
name: sphere-layout-sync
description: Update a generated go-sphere project to a newer layout revision, or adopt a legacy project into the layout contract. Use when the user wants to pull upstream layout changes into an existing project, resolve layout drift, set up .sphere/layout.lock.json for a project created before the contract existed, or diagnose why a layout upgrade conflicts. Do not use for ordinary feature work inside a project — that is sphere-feature-workflow.
---

# Sphere Layout Sync

A generated go-sphere project keeps receiving upstream layout changes. This skill
performs that merge without destroying project code, and without silently
reverting layout fixes.

<HARD-GATE>
Do not modify any file until all of these are established:
- The project's `.sphere/layout.lock.json` exists and its `schema_version` is understood
- The target upstream revision is resolved to a concrete commit SHA
- The working tree is clean, or the user has explicitly accepted syncing over local changes

If `schema_version` is unknown to you, **stop** and report it. Do not guess the
lock format.

If there is no lock file, this is a legacy adoption — go to section 5 and do not
start a normal sync.
</HARD-GATE>

## 1. Read the Contract

Read, in this order:

1. `.sphere/layout.lock.json` — which layout, which ref, which base revision
2. `.sphere/layout.json` — ownership patterns for this layout
3. `docs/LAYOUT_CONTRACT.md` — the authoritative protocol
4. `AGENTS.md` — layout profile and extension seams

The project's own copies outrank this skill wherever they disagree.

Lock shape:

```json
{
  "schema_version": 1,
  "name": "standard",
  "repository": "https://github.com/go-sphere/sphere-layout.git",
  "ref": "master",
  "upstream_module": "github.com/go-sphere/sphere-layout",
  "base_revision": "full-git-commit-sha"
}
```

Unknown JSON fields are forward-compatible — preserve them. Layout source
repositories themselves contain no lock file; only generated projects do.

## 2. Ownership Classes Drive the Merge

Patterns in `.sphere/layout.json` are evaluated in this order, first match wins:
`generated` → `layout_owned` → `mixed` → default `project_owned`.

| Class | Sync action |
|-------|-------------|
| `generated` | **Ignore upstream contents entirely.** Regenerate from the merged handwritten sources afterwards. |
| `layout_owned` | Apply the upstream change **directly** when the local copy still equals the recorded base. Otherwise three-way merge. |
| `mixed` | **Always** semantic three-way merge of base, local, and target. |
| `project_owned` | **Never** replace merely because upstream changed. |

Diffing generated files is wasted work at best and a source of bogus conflicts at
worst. Exclude them before you compare.

## 3. Update Procedure

1. **Resolve.** Read the contract and lock. Resolve the requested target
   revision; with none specified, resolve the current commit of the recorded
   `ref`.
2. **Materialize.** Check out the base and target upstream commits into separate
   temporary directories. **Do not run their code** merely to compute a diff.
3. **Normalize the module path.** Rewrite both snapshots from `upstream_module`
   to the project's current Go module path *before* comparing. Skipping this makes
   every import line look like a change and buries the real diff.
4. **Merge by class.** Ignore `generated`. Leave `project_owned` alone. Apply
   `layout_owned` directly only where local equals base, else three-way merge.
   Always semantically three-way merge `mixed`.
5. **Resolve deletions and renames carefully.** If a file is deleted or renamed
   both locally and upstream, settle ownership before recreating it. **Never
   resolve a conflict by discarding project code.**
6. **Regenerate and verify.** Regenerate through the layout Makefile, then run
   formatting, dependency checks, tests, lint, and build — typically
   `make gen/all`, `make check`, `make build`. Review the complete diff.
7. **Commit the lock last.** Update `base_revision` **only** after every conflict
   is resolved and verification succeeds. If blocked, leave the lock unchanged
   and report the affected paths.

Step 7 is the safety property: a lock that still points at the old base means
"this sync did not finish", which is recoverable. A prematurely advanced lock
loses that information permanently.

## 4. Failure Handling

Stop and report, rather than improvising, when:

- `schema_version` is unrecognized
- The recorded `base_revision` is not reachable in the upstream repository
- A `project_owned` file would have to be overwritten to make the merge succeed
- Generated output still drifts after a full regeneration
- Tests or build fail and the cause is a merge decision rather than a pre-existing issue

Report the affected paths and the decision you could not make. Leave the lock
untouched.

## 5. Adopting a Legacy Project

A project created before the contract has no `.sphere/`. To adopt it:

1. Inspect the project's earliest template commit.
2. Compare its Git tree against commits from the likely upstream layout.
3. Record a revision **only when exactly one upstream tree matches.**
4. If there is no unique match, **ask the user** for the originating revision. Do
   not infer a convenient base — a wrong base silently corrupts every future
   three-way merge.
5. Once confirmed, write the version-1 lock and follow the normal update flow.

Identifying the layout variant (standard / simple / bun / telegram) is part of
this step; their trees differ substantially.

## 6. Layout Release Checklist

When the change is to a **layout repository itself** rather than a generated
project:

- [ ] README capabilities and `make help` output are accurate
- [ ] `.sphere/layout.json` ownership patterns do not overlap
- [ ] All derived outputs regenerated after schema, proto, or Wire changes
- [ ] `make check` and `make build` pass from a clean checkout
- [ ] Provider-specific dependencies exist only in provider-specific layouts
- [ ] Breaking template changes documented
- [ ] No database deletion migration is applied automatically to downstream apps

## Reporting

State: layout variant and lock status; base and target revisions; per-class
summary of what was applied, merged, ignored, and left alone; every conflict and
how it was resolved; regeneration and verification commands run with results;
whether `base_revision` was advanced, and if not, why.
