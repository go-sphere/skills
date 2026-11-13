# Plan Template

Every plan is written for an executor with **zero context**. It has not seen this session, the audit, the other plans, or this skill. It may be a smaller, cheaper model. Assume it follows explicit instructions well, and fills gaps, recovers from ambiguity, and knows when to stop poorly.

Three properties make a plan executable by a weak model:

1. **Self-contained.** Everything needed is in the file: paths, code excerpts, conventions, commands. The plan never points at this skill's files, because the executor does not have them.
2. **Verification gates.** Every step ends with a command and its expected result. The executor never judges whether it succeeded.
3. **Hard boundaries and escape hatches.** An explicit out-of-scope list, and "stop and report" conditions in place of improvisation.

File name: `NNN-short-slug.md` in the plans directory, numbered in recommended execution order. `PLANS lint` checks the headings and fields below, so keep them exactly.

## Template

````markdown
# Plan NNN: <Imperative title: what will be true after this plan>

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before the next step.
> If anything in "STOP conditions" occurs, stop and report; do not improvise.
> When done, update this plan's row in `plans/README.md`, unless a reviewer
> dispatched you and said they maintain the index.
>
> **Drift check (run first)**: `git diff --stat <sha>..HEAD -- <in-scope paths>`
> Expected: no output. Output means an in-scope file changed since this plan
> was written. Compare "Current state" with the live code; a mismatch is a STOP
> condition. If `<sha>` is not in the repository, that is also a STOP condition.

## Status

- **Priority**: P1 | P2 | P3
- **Effort**: S | M | L
- **Risk**: LOW | MED | HIGH
- **Depends on**: plans/NNN-<slug>.md, or none
- **Category**: bug | security | perf | tests | tech-debt | migration | dx | docs | direction
- **Finding**: <the finding key>
- **Planned at**: commit `<sha>`, <YYYY-MM-DD>
- **Issue**: <GitHub issue URL; add only after publishing with --issues>

## Why this matters

Two to five sentences: the problem, its concrete cost, and what improves when
this lands. Intent lets the executor make a correct call when a detail is off.

## Current state

- Each relevant file with one line on its role, for example
  `src/orders/api.ts` — order-list endpoint; the N+1 is at lines 130–160.
- Short excerpts of today's code with `file:line` markers, copied from your own
  read of the stamped commit, enough to confirm the executor is in the right place.
- The conventions that apply, each with one exemplar file: "Errors follow the
  Result pattern; see `src/lib/result.ts` and its use at `src/users/api.ts:40-60`."
- Vocabulary or design constraints from the intent docs, quoted: `CONTEXT.md`
  terms to use in names, `DESIGN.md` tokens to reuse, the ADR this work must honor.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Typecheck | `pnpm typecheck` | exit 0, no errors |
| Tests | `pnpm test -- <filter>` | all pass |
| Gate | `pnpm check` | exit 0 |

Exact commands from recon. Only commands without side effects outside the
working tree: no publish, push, deploy, or tag. Under the table, name each
command the executor must not run (a target that rewrites files or deploys),
and a fallback for any gate tool the executor may lack.

## Suggested executor toolkit

Optional. Include it only when a skill below plausibly exists in the executor's
environment. Skills to invoke and when, and reference docs by path or URL.

## Scope

**In scope** (the only files you may modify):
- `src/orders/api.ts`
- `src/orders/api.test.ts` (create)

**Regenerated** (optional; expected to change when you run `<generate command>`; never hand-edit):
- `api/orders/**`

**Out of scope** (do NOT touch, even though they look related):
- `src/orders/legacy-api.ts` — deprecated; changing it risks the v1 clients pinned to it.
- Any change to the public response shape.

## Git workflow

- Branch: `advisor/NNN-<slug>`, or the repository's own convention.
- Commit per step or logical unit, in the repository's message style, for example `fix(orders): batch item queries`. Commit a regression test together with its fix, so no commit leaves the suite failing.
- Do NOT push or open a pull request unless the operator said so.

## Steps

### Step 1: <imperative title>

What to do, precisely, naming exact files and symbols. Show the target shape
when it is load-bearing.

**Verify**: `<command>` → <expected output>

### Step 2: ...

## Test plan

- New tests: file, cases (happy path, the regression this plan fixes, named edges).
- The existing test to copy structurally: "model after `src/users/api.test.ts`".
- Verification: `<test command>` → all pass, including the N new tests.

## Done criteria

All must hold:

- [ ] `<gate command>` exits 0
- [ ] `<test command>` passes; the new tests for <X> exist
- [ ] `grep -rn "<old pattern>" src/` returns no matches
- [ ] `git diff --stat <sha>..HEAD` lists only in-scope and regenerated files
- [ ] `git status --short` prints nothing: everything is committed
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back, without improvising, if:

- The code at the "Current state" locations does not match the excerpts.
- A step's verification fails twice after a reasonable fix attempt.
- The fix needs an out-of-scope file.
- <the plan's own key assumption> turns out to be false.

## Report back

Reply with: STATUS (`COMPLETE` or `STOPPED`); per step, done or skipped plus its
verification result; if `STOPPED`, which condition and what you observed; the files
changed; deviations and judgment calls. State only what a command result from
this session supports. Say plainly when a verification failed or was skipped.

## Maintenance notes

- What future changes interact with this ("if the endpoint gains pagination, revisit step 2").
- What the reviewer should scrutinize.
- Anything deliberately deferred, and why.
````

## Writing rules

| Rule | Why |
|------|-----|
| Write the plans directory's real name wherever the template says `plans/`, for example `advisor-plans/`. | The executor must find the index and the sibling plans. |
| Copy every excerpt from your own read of the stamped commit, under a first line `// path:start-end` in the file's comment style (`git show <sha>:<path>` for a dirty file). To skip lines, write two excerpts. | `PLANS lint` compares each headed excerpt with the commit, and a wrong one becomes a plan that fails its own drift check. |
| Stamp the date with `date +%F`, and the commit with `git rev-parse --short=12 HEAD`. | Guessed dates and short hashes drift. |
| Fit one plan to one reviewable pull request: at most 8 steps, 8 in-scope files, and about 250 lines of prose (code blocks do not count). Split larger work into a chain with `Depends on`. | A weak executor loses the thread in a long plan, and an issue body cannot exceed 65,536 characters. |
| Under Scope, write one path per bullet in backticks, then ` — ` and the reason. | `PLANS lint` reads the paths before the dash. |
| Never put a command that contains a pipe character in a table cell. Put it in a fenced block under the table, or name the tests with a shared prefix for `-run`. | A pipe escaped for the table is pasted into a shell as a backslash and a pipe, which silently matches nothing. |
| Order steps so the code builds after each one: add the new path, switch callers, remove the old path. | The executor can stop after any step without leaving the repository broken. |
| Bug and security plans start with a failing regression test. Step 1's Verify names the expected failure, a done criterion has the report quote that failing run, and the last Verify shows it passing. | A test that never failed proves nothing. |
| A plan that only adds tests has no failing phase, so give it a mutation check: one step makes one exact edit to the code under test, runs the new test, expects a named failure, and reverts with `git checkout -- <file>`. List that file under In scope as "temporary edit, reverted in the same step". See `plan-example-tests.md`. | It proves the test can fail, and the final diff stays test-only. |
| At standard and deep depth, run a bug or security plan's new test in a scratch copy of the stamped commit (`recon.md`). It must fail for the stated reason. When the fix is a few lines, apply it there and confirm the test passes. | The executor never receives a plan whose premise is false. |
| Never list generated files under "In scope". Change the source of truth, name the generate command, and list the outputs under "Regenerated". | A hand-edit of generated output is overwritten on the next generation. |
| Put findings that live in layout-owned or vendored code in a report to the upstream, not in a local plan. | The local fix is lost at the next sync. |
| A direction plan's done criteria are artifacts: a design note, a prototype, answered questions. | The plan scopes an investigation, not a build. |
| For Go and go-sphere work, name executor skills by category from the table in `go-ecosystem.md`. Elsewhere, name only skills you know the executor has. | The executor reuses a proven workflow instead of improvising. |

## Quality bar

Check each item before a plan is finished:

- Could a model that has never seen this repository execute it with only the plan and the repository? Inline anything that needs knowledge from this session.
- Is every verification a command with an expected result, never "make sure it works"?
- Does every step name exact files and symbols, never "the relevant module"?
- Are the STOP conditions specific to this plan's real risks, never boilerplate?
- Would a reviewer reading only "Why this matters" and "Done criteria" know what they are approving?
- Is the file free of secret values, naming only locations and credential types?
- Are the stamped commit and date filled in, and do the drift-check paths match the Scope section?
