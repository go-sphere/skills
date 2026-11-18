# Reviewer Brief

How to run the `review` command, alone or fanned out to other agents.

## One reviewer

1. Get the code for the target kind:

   | Kind | How |
   |------|-----|
   | `diff`, uncommitted | `git diff HEAD`, then `git ls-files --others --exclude-standard` and read each untracked file. `git diff` alone misses untracked files. |
   | `diff`, range or PR | `git diff <merge-base>...HEAD` |
   | `paths` | `git ls-files -- <paths>`, then read the files. Outside a git repository, list the paths directly. |
   | `repository` | `git ls-files`, minus generated and vendored files, grouped into the confirmed slices. |

2. Read the project's own instructions first: `AGENTS.md`, `CLAUDE.md`, `docs/`, and the build and test configuration. A finding that contradicts a documented convention is wrong.
3. Read enough surrounding code to judge each hunk or file. A hunk read alone produces false findings.
4. Write one file from [assets/templates/review_report.md](../assets/templates/review_report.md): `<model>.md`, or `<model>-<perspective>.md` when a perspective was requested.
5. Number findings `F1`, `F2`, and so on inside the file. `synthesize` assigns the global `RF-NNN` IDs; reviewers never do.

## Finding quality bar

Every finding states all of these. Delete a finding that cannot.

| Field | Requirement |
|-------|-------------|
| `evidence` | A `file:line` and the code or behavior that proves the claim. Quote at most five lines. |
| `risk` | Who or what breaks, and under which input or state. |
| `suggested_fix` | A concrete change, not "consider refactoring". |
| `suggested_tests` | The test that would fail before the fix and pass after it. |

Rules for the content:

1. One root cause per finding. Two symptoms of one cause are one finding.
2. For a `diff` target, review only what the diff changes or newly exposes; pre-existing problems go under Reviewer Notes. For `paths` and `repository` targets, every defect inside the scope is a finding; problems outside it go under Reviewer Notes.
3. Skip style preferences unless they affect maintainability or user-visible behavior.
4. Skip generated files. Report a defect found in generated output against its source of truth.
5. Write `No findings` under Findings when you found none, and say what you checked. An empty file is invalid.

## Severity and confidence

| `severity` | Meaning |
|------------|---------|
| `critical` | Data loss, security breach, or a crash on a common path. Blocks merge. |
| `high` | Wrong behavior on a realistic path, or a race or leak. Should block merge. |
| `medium` | Wrong behavior on an uncommon path, or a missing test for risky logic. |
| `low` | Small defect or maintainability cost with a limited blast radius. |
| `note` | Observation that needs no change. |

| `confidence` | Meaning |
|--------------|---------|
| `high` | You traced the code path and can name the triggering input. |
| `medium` | The path looks reachable but you did not trace all callers. |
| `low` | A suspicion. Say what would confirm it. |

## Large scopes

A `repository` target is always sliced. For any other target that covers more than 30 files or 1500 lines, split it by package or module too. Review the slices one after another. Still write one file per model. List each slice under Scope. State any slice you skipped.

## Fan out to other agents

Use this when the user asks for several models, a second opinion, or an independent review.

1. Locate the `delegate` skill: `python3 <skills directory>/delegate/scripts/delegate.py`. Run its `agents` subcommand and use only installed agents. When `delegate` is not installed, tell the user to run `review` in the other agents themselves and drop their files into the feature folder.
2. Write your own review first, or in parallel, so the other agents do not see it.
3. For each other agent, write a brief file in the system temp directory. It must hold the target kind and base, the commands to get the code, the perspective, the quality bar and severity tables above, the exact file shape from the template, and this line: "Read-only. Do not edit any file. Return the whole report as your final message."
4. Run `delegate run --agent <name> --cwd <repo> --mode read --prompt-file <brief>`. Use the agent's name as the model name.
5. `kimi` cannot run read-only headless. Skip it unless the user accepts `write` mode, then run `git status --porcelain` afterwards. When it shows changes the tree did not already have, stop and tell the user.
6. Save the response as `<agent>.md` in the feature folder. Reject a response that does not start with `# Code Review Report` or lacks findings and a Scope section. Resume once with `--session` and ask for the missing parts. Then record the failure in your reply and go on without it.
7. Never put the other reviewers' files into a later reviewer's brief. Independence is the point.
