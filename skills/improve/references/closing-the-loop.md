# Closing the Loop: execute, reconcile, --issues

The advisor's job does not end at the plan. This file covers dispatching an executor and reviewing its work (`execute`), keeping the backlog alive (`reconcile`), and publishing plans (`--issues`). `PLANS` means `python3 -I <this skill's directory>/scripts/plans.py`; write the full command each time.

The founding rule survives: **the advisor never edits source code.** In `execute`, a separate executor edits code in a disposable worktree. The advisor dispatches, reviews, and renders a verdict, like a tech lead who does not push to the user's branch.

## `execute <plan>`

### Preconditions

Check all of them before dispatching. When one fails, stop and name it.

1. The directory is a git repository.
2. Run `PLANS status <plans dir>`. The plan is `TODO`, and every dependency is `DONE` and merged. A dependency marked `awaiting merge` is not satisfied; ask the user to merge it first.
3. The status shows no drift for this plan. When it drifted, reconcile that plan first. Never hand a stale plan to an executor.
4. Run `git rev-parse HEAD` and keep the result as `<base>`. The review measures the executor's diff against it.

### Choose the dispatch path

| The host offers | Dispatch with |
|-----------------|---------------|
| A subagent tool with worktree isolation (Claude Code: the `Agent` tool with `isolation: "worktree"`) | One `general-purpose` subagent in an isolated worktree. |
| The `delegate` skill | Create the worktree yourself, then `python3 <delegate skill>/scripts/delegate.py run --agent <executor> --cwd <worktree> --mode write --prompt-file <brief>`. |
| Neither | Stop. Say so and hand the plan to the user for manual execution. |

Creating the worktree is a scoped exception to the no-mutation rule, authorized by the user's `execute` request:

```sh
git worktree add -b advisor/NNN-<slug> ../<repo>-wt-NNN HEAD
```

Take the branch name from the plan's "Git workflow" section. The worktree sits next to the repository, never inside it. Write the brief file to the system temp directory. When the branch or the path already exists, an earlier run left it: ask the user whether to continue from it or to start over with a `-2` suffix on both. Never reuse or delete it silently. When you use a suffixed name, write it into the plan's `Branch:` line so `PLANS status` finds it.

**Choose the executor.** Use the one the user named. Otherwise pick the cheapest that fits the plan's risk:

| Plan | Executor |
|------|----------|
| LOW risk, effort S | A cheaper model than yours (subagent), or `pi` or `kimi` (delegate) |
| MED or HIGH risk | The strongest model the user allows, or `claude` or `codex` (delegate) |

`pi` and `kimi` never ask for approval, so their `write` mode behaves like `full`. Use them only for LOW-risk plans inside the worktree, and tell the user which agent ran. Never pass `--mode full`.

Before dispatching, set the plan's index row to `IN PROGRESS (branch <branch>, worktree <path>, executor <agent>)`.

### The brief

The worktree holds committed files only, so an uncommitted plans directory is invisible to the executor. Inline everything. The brief is, in order:

1. This preamble, verbatim:

> You are the executor for the implementation plan below. Follow it step by
> step. Run every verification command and confirm the expected result before
> moving on. Touch only the files listed as in scope or regenerated. If any
> STOP condition occurs, stop immediately and report. Do not improvise around
> obstacles. Commit your work in the worktree following the plan's git workflow
> section. One override: SKIP the plan's instruction to update the plans index,
> and ignore the done criterion about it; your reviewer maintains it. Before
> reporting, check every claim in your report against a tool result from this
> session, and report only what that evidence supports. If a verification failed
> or was skipped, for example because a sandbox denied the command, say so
> plainly. When finished, reply with exactly the report format below.

2. The full plan text.
3. The report format:

```text
STATUS: COMPLETE | STOPPED
STEPS: per step, done or skipped, plus the verification command and its result
STOPPED BECAUSE: (only if STOPPED) which STOP condition, and what was observed
FILES CHANGED: list
DEVIATIONS: anything done differently from the plan, and why; or "none"
NOTES: anything the reviewer should know
```

### Review

A fresh worktree shares git history but not installed dependencies or build output. The executor installs first, and tools that resolve from build output may need one build. That is not a deviation.

To review work that an executor already finished, dispatched earlier or by someone else, skip the preconditions and take `<base>` from `git -C <worktree> merge-base HEAD <default branch>`.

Review like a tech lead reviewing a pull request against the spec. Never fix anything yourself.

1. **Re-run every `Verify` line and every done criterion that has a command**, in the worktree. The report is a claim. When the executor's sandbox denied a command, run it yourself (Go under `codex` needs `GOCACHE` pointed at a temp directory). Check a criterion about the report, such as quoting a failing run, by reading the report. The index row is your job, not the executor's.
2. **Check scope.** Run `PLANS scope <plan file> --worktree <worktree> --base <base>`. Any `OUT OF SCOPE` line fails review. Then `git -C <worktree> status --short` must print nothing, because everything is committed.
3. **Read the full diff** against "Why this matters" and the conventions the plan names.
4. **Check generated output.** When the plan names a generate command, re-run it in the worktree and confirm `git -C <worktree> status --short` stays empty. A difference means a hand edit. Skip this when the plan has none.
5. **Audit the tests.** Executors game criteria, so check all of these:
   - Test files lose no lines: `git -C <worktree> diff <base>..HEAD -- <test files>` shows no removed line unless the plan removes tests.
   - The added test lines hold no skip marker (`t.Skip`, `testing.Short`, `.skip`, `xit`, `@pytest.mark.skip`, a build tag), and a verbose run reports 0 skipped tests.
   - When the plan gives test code verbatim, copy that block to a temp file and `diff` it against the executor's file. Every difference needs an entry under DEVIATIONS. If the executor changed the file, run the plan's version against the executor's production code in a scratch copy (`recon.md`); a failure there means the change hid a defect.
   - For a bug or security plan, prove the regression test fails without the fix. With the status confirmed empty, run `git -C <worktree> diff <base>..HEAD -- <in-scope files that are not tests> | git -C <worktree> apply -R`, run the new tests, and expect the failure the plan names. Every new test must FAIL; one that SKIPs is gamed. Restore with `git -C <worktree> checkout -- .`.
   - For a plan that only adds tests, apply the plan's mutation edit yourself, expect the named failure, and restore the same way.
6. **Second opinion for HIGH risk.** Ask a different agent for a read-only review: `python3 <delegate skill>/scripts/delegate.py run --agent <other agent> --cwd <worktree> --mode read --prompt-file <review brief>`. Verify each finding in the code before acting on it.

### Verdict

Judge documented deviations on merit. "Do not improvise" stops silent drift. An executor that hits a real obstacle, adapts minimally, and explains it under DEVIATIONS has done the right thing: approve it when the adaptation serves the plan's intent and stays in scope. A skip or omission that appears under STEPS but not under DEVIATIONS is undocumented, and an undocumented deviation fails review.

Gaming and false reports are integrity failures: a skipped or weakened test, a claim that a command contradicts, an out-of-scope edit the report omits. The first time, answer REVISE with the evidence for each item. A repeat is BLOCK, and from then on verify every claim from that executor.

| Verdict | When | Action |
|---------|------|--------|
| **APPROVE** | Criteria pass, scope is clean, quality holds | Set the index row to `DONE`. Tell the user the diff summary, the worktree path, the branch, and anything under DEVIATIONS or NOTES. Leave the worktree in place. Merging is the user's decision; never merge, push, or commit to their branch. |
| **REVISE** | Fixable gaps | Keep the row `IN PROGRESS` and count the round in it, for example `IN PROGRESS (revision 1 of 2, ...)`. Send feedback that numbers each item with the file and line, the defect, the exact fix, and the check that proves it, and ends with the expected end state. Subagent path: `SendMessage` to the same executor. Delegate path: rerun with `--session <session_id>`, the same `--agent`, and `--cwd <worktree>`. With no executor handle, write the message for the user to pass on. At most 2 rounds, then BLOCK. |
| **BLOCK** | A STOP condition fired, scope was violated beyond repair, revisions ran out, or gaming repeated | Set the row to `BLOCKED (reason)`. Rewrite the plan with what you learned: in place when the approach holds, as a new number when it changed (the old row becomes `REJECTED (superseded by NNN)`). Tell the user what changed. |

Verification commands inside the executor's worktree are allowed because it is disposable. The no-mutation rule protects the user's working tree.

### Several plans at once

Run plans in parallel only when no dependency edge joins them, their in-scope and regenerated paths are disjoint, and each has its own worktree and branch. Use `rex-desktop` when the user wants to watch the workers live. Otherwise start one `delegate run` per plan in parallel background shells. Review each result separately, and tell the user to merge in dependency order, running the repository gate after each merge.

## `reconcile`

Process what happened since the last run.

1. Run `PLANS status <plans dir>` and `PLANS lint <plans dir>`. They report drift, merge state, readiness, and structural problems without reading every file.
2. Handle each plan by its state:

| State | Do |
|-------|----|
| `DONE`, branch merged | Spot-check the cheap done criteria on the current HEAD. Keep `DONE`. |
| `DONE`, `awaiting merge` | Report it as waiting for the user's merge. It is not a regression. `PLANS status` counts a squash or rebase merge as merged once HEAD holds the branch's content for the plan's files; if it still says `awaiting merge` after one, ask the user. |
| `BLOCKED` | Read the reason and investigate the obstacle in the code. Rewrite the plan around it, or set `REJECTED (reason)`. |
| `IN PROGRESS`, stale | Tell the user an executor probably died. Check its worktree and branch when they exist. |
| `TODO`, drifted | Check the finding still exists; it may have been fixed in passing. If so, refresh the plan (below). If not, set `REJECTED (fixed independently)`. |
| `TODO`, no drift | Leave it. |

3. To refresh a plan, re-read each in-scope file at the current HEAD yourself, update the excerpts and line references, set `Planned at` to the new commit and date, and run `PLANS lint` on it. The lint compares every headed excerpt with the new commit.
4. Never delete plan files.
5. End with a short report: verified done, refreshed, rejected, awaiting merge, and executable now.

## `--issues`

A modifier on any planning request. The flag is the user's authorization to create issues. Never create issues without it.

1. Preflight: `gh auth status` succeeds and the repository has a GitHub remote. If either fails, write the plan files as usual and say why issues were skipped.
2. Visibility: run `gh repo view --json visibility`. When the repository is **public**, warn that issues are publicly visible, and get explicit confirmation before publishing any plan that describes a security vulnerability, a credential location, or another sensitive finding.
3. Show the list of titles that will become issues. Confirm once when a user is present.
4. Per plan, run `gh issue create --title "<plan title>" --body-file <plan file>`. Add the labels `improve` and the plan category only when they exist or can be created without an error; skip a label rather than fail.
5. Record each issue URL in the plan's `Issue` field and in the index's `## Issues` section.

A plan body must stay under 65,536 characters; `PLANS lint` reports a larger one as an error. The plan file stays the source of truth, and the issue is distribution.
