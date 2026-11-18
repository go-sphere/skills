# Fix And Verify

How to run the `fix` and `verify` commands.

## Fix

1. Read `summary.md`. List the items ticked `[x]` whose status is `open`, `approved_for_fix`, `partially_fixed`, `verification_failed`, or `test_blocked`. Items ticked but already `fixed` or `verified` are done; skip them.
2. Confirm the scope with the user unless they already named the items: show each ID, its severity, and its files. Wait for the answer.
3. Check for staleness. Run `git diff <target_rev> --stat -- <affected files>`. When a file changed, re-read the evidence. When the problem is gone, set the item `stale` and skip it. For a `vetted: unconfirmed` item, confirm the evidence now; when you cannot, stop on that item and ask.
4. Write `fix-plan.md` from [assets/templates/fix_plan.md](../assets/templates/fix_plan.md). Record `fix_base` as the current HEAD commit and `pre_dirty_files` as the files `git status --porcelain` already shows. `verify` needs both.
5. Fix one item at a time, most severe first. For each item:
   1. Write a test that reproduces the finding and watch it fail, when a test is feasible. Follow the project's existing test style; in a Go repository, `go-test` governs test content.
   2. Make the smallest change that fixes the root cause.
   3. Run the narrowest test for the touched behavior.
6. Run the gates once after the batch. Gate order and per-language commands are in [checklist.md](checklist.md); Go commands are in [go.md](go.md). Stop at the first failing gate and report it.
7. Write `status.md` from [assets/templates/status.md](../assets/templates/status.md). Record every command, its result, and the items it covers.
8. Set each item's status from the evidence, using [status-model.md](status-model.md). Never set `verified` in `fix`.

Stop and ask the user, without widening scope, when:

| Situation | Why |
|-----------|-----|
| The fix needs a change outside the item's files | The user approved a bounded change. |
| The fix changes a public signature, format, or behavior | It breaks consumers. |
| The fix touches schema, protocol, or contract definitions | A generator rerun or another repository may be involved. In a go-sphere project, use `sphere-feature`. |
| The only fix is to a generated file | Trace the defect to its source first. |
| Tests cannot run | Record `test_blocked`; do not claim `fixed`. |

Leave the changes uncommitted unless the user asks for a commit.

## Verify

1. Pick the verifier. Prefer a different agent than the fixer: run the `delegate` skill with `--mode read` and a brief holding `summary.md`, `fix-plan.md`, `fix_base`, and the gates. When none is available, re-read the diff cold from `fix-plan.md` alone, without relying on memory of the fix. Record `verifier` and `independent: yes` or `no` in `verify.md`.
2. For each item in `fix-plan.md`, compare what should have changed with what changed: `git diff <fix_base> -- <expected files>`.
3. Check scope. Run `git diff <fix_base> --name-only`. Every path must be in the item's `expected_files` or in `pre_dirty_files`. Report any other path as out of scope.
4. Check for test gaming. Flag a deleted or skipped test, a weakened assertion, a loosened timeout, or a golden file edited by hand.
5. For `critical` and `high` items, check that the new test catches the bug: create a scratch worktree at `fix_base` in the system temp directory, copy the new test in, and confirm it fails there. Remove the worktree afterwards.
6. Rerun the gates yourself. A fixer's report is a claim, not evidence.
7. Look for regressions near the fix: callers of each changed function, error paths, and concurrency around changed shared state.
8. Write `verify.md` from [assets/templates/verify_report.md](../assets/templates/verify_report.md) and update `status.md`.

Set the status by evidence:

| Evidence | Status |
|----------|--------|
| Fix matches the plan, scope holds, gates pass | `verified` |
| Gates fail, scope broke, or the new test does not catch the bug | `verification_failed`, with the reason and `next_action` |
| Gates cannot run | `test_blocked`, with the command and the blocking reason |
| Only part of the finding is addressed | `partially_fixed` |

Verification never edits product code. When a fix is wrong, record it and let the user choose `fix` again.
