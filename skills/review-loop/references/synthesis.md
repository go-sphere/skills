# Synthesis

How to run the `synthesize` command: turn several review files into one `summary.md` that a human can approve line by line.

## Steps

1. List the folder. Every `*.md` file except `summary.md`, `fix-plan.md`, `verify.md`, and `status.md` is a review file. Read them all.
2. Read `summary.md` if it exists. Its `RF-NNN` IDs, ticks, and statuses are the state to preserve.
3. Cluster findings by root cause. Two findings are one cluster when they name the same defect in the same function, or the same missing check on the same path.
4. Vet each cluster as the next section says.
5. Match each cluster to an existing `RF-NNN` by affected file and root cause. Give a new cluster the next unused number. Never renumber and never reuse a number.
6. Order the checklist by severity, then by reviewer agreement.
7. Write `summary.md` from [assets/templates/review_summary.md](../assets/templates/review_summary.md).
8. Run the lint command from `SKILL.md` and fix its ERRORs.

## Vet every cluster

A reviewer's claim is a lead, not a fact. Open each cited location at `target_rev` yourself.

| Result | Action |
|--------|--------|
| The code does what the finding says | `vetted: confirmed`. Enter it in the checklist. |
| The code is plausible but you cannot trace the trigger | `vetted: unconfirmed`. Enter it, and say what confirms it. `fix` must confirm it before editing. |
| The behavior is by design, documented, or the attribution is wrong | Move it to Rejected Findings with a one-line reason. |
| The problem exists but the diff did not cause it (`diff` target only) | Move it to Disagreements And Deferrals as pre-existing. |
| The problem is outside the target scope (`paths` or `repository`) | Move it to Disagreements And Deferrals as out of scope. |
| The cited file is generated | Trace it to the source of truth and cite that, or defer it with the reason. |

Never drop a finding silently. Every finding from every review file ends up in the checklist, in Rejected Findings, or in Disagreements And Deferrals.

## Merge rules

1. Keep the highest severity only when you agree with it. When reviewers disagree on severity and you cannot settle it from the code, keep the lower one and record both under Disagreements And Deferrals.
2. Record `reviewer_agreement` as the number of reviewers who raised the cluster over the number of review files, for example `2/3`.
3. Record `sources` as each file and local ID, for example `codex#F2, claude#F1`.
4. Preserve real disagreement. A finding one reviewer rejected explicitly goes to Disagreements And Deferrals with both views.
5. Combine `suggested_tests` into the smallest set that would fail before the fix.

## Overwriting an existing summary

`summary.md` is the only artifact a human edits, through the ticks. Overwriting it must not lose their decisions.

1. Carry over the `[x]` or `[ ]` state and the `status` of every existing `RF-NNN`.
2. Add new clusters unticked with status `open`.
3. When an existing item's cited code no longer matches `target_rev` and you cannot find it again, set its status to `stale` and keep it listed.
4. Update `target_rev` and `source_reports` in the header.
5. Never tick a checkbox yourself. Approval belongs to the user.

## Stale review check

Before vetting, compare `target_rev` in each review file with the current HEAD. When they differ, run `git diff <target_rev> --stat -- <affected files>`. Re-read any finding whose file changed. When most findings moved, tell the user the review is stale and suggest rerunning `review`.
