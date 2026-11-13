# Modes

Details for the modes in the skill's Modes table, except `execute`, `reconcile`, and `--issues`, which are in `closing-the-loop.md`. `PLANS` means `python3 -I <this skill's directory>/scripts/plans.py`.

## Focus area

Run recon, audit only the named category, then continue with steps 3 to 6.

| The request says | Audit |
|------------------|-------|
| `bugs`, `correctness` | `## 1. Correctness / Bugs` |
| `security` | `## 2. Security` |
| `perf`, `performance` | `## 3. Performance` |
| `tests`, `coverage` | `## 4. Test Coverage` |
| `debt`, `architecture` | `## 5. Tech Debt & Architecture` |
| `deps`, `migrations` | `## 6. Dependencies & Migrations` |
| `dx`, `tooling` | `## 7. DX & Tooling` |
| `docs` | `## 8. Docs` |

`quick` and `deep` combine with every mode: `quick security`, `deep branch`.

## `branch`

Audit what the current branch changes, before a pull request.

1. Find the base. Run `git symbolic-ref --short refs/remotes/origin/HEAD`. When that prints nothing, use the first of `origin/main`, `origin/master`, `main`, `master` that `git rev-parse --verify --quiet` resolves. When none resolves, ask the user for the base.
2. Run `git merge-base <base> HEAD`, then `git rev-list --count <merge-base>..HEAD`. When the count is 0, or the branch is the default branch, say so and offer a full audit.
3. Scope the audit to `git diff --name-only <merge-base>..HEAD` plus the direct importers and callers of those files. Drop skip-list paths.
4. This mode covers committed changes only. When `git status --porcelain` shows edits, say they are not covered and offer to continue once the user commits.
5. Run light recon, cover all nine categories, and usually use no subagents.
6. Tag every finding. `introduced` means a line this branch added or changed; confirm against the diff hunks. `pre-existing` means the file was touched but the line was not. Add a column for the tag. Do not blame the branch for legacy debt, and do surface what the branch builds on top of.
7. Plan the `introduced` findings by default. Ask before planning `pre-existing` ones.

## `next`

Suggest where to take the project. Run recon, then audit only `## 9. Direction` in more depth.

1. Produce 4 to 6 grounded suggestions. Each has cited evidence, trade-offs in two or three sentences, and a coarse effort.
2. Present them as options, not as a ranked to-do list.
3. A selected suggestion becomes a design or spike plan with category `direction`. Its steps investigate, prototype, define the API, and list open questions. Its done criteria are artifacts such as a design note or a prototype behind a flag. They are never "feature shipped".
4. When the choice needs product judgment, hand to `interview-me`. When the user commits to a direction, the next stage is `prd` or `spec`, not a build plan.

## `plan <description>`

The user already knows what they want. Skip the audit and the findings table.

1. Run light recon.
2. Investigate only as far as needed to specify the change: open every file it touches, find an exemplar of the convention, find the tests that cover it.
3. Resolve each ambiguity from the codebase first. Turn what remains into questions for the user. Ask one at a time, each with a recommended answer, and wait for each reply.
4. When the change needs more than 8 steps or touches more than 8 files, propose a split and write the chain with `Depends on` links.
5. Write one plan (steps 5 and 6 of the skill). The finding key is `<category>:<path>:<symbol>` of the main target.

## `review-plan <file>`

Critique and tighten an existing plan. Edit only that plan and the index.

1. Run `PLANS lint <file>`. Fix every ERROR in the plan.
2. Check the plan against each line of the quality bar in `plan-template.md`.
3. Run the plan's drift check. When it prints output, refresh the "Current state" excerpts and the stamped commit as described under `reconcile` in `closing-the-loop.md`.
4. Run a cold read when you wrote the plan in this session. Give a fresh-context reader only the plan text and the repository, either a read-only subagent or `delegate run --mode read` with another agent. Ask it to list every step it could not follow without guessing, every file or symbol it could not find, and every verification whose expected result is unclear. Self-critique misses gaps you fill in from memory.
5. Apply the fixes. Report what changed and what remains uncertain.
