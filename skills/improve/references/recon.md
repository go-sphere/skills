# Recon

Map the repository before judging it. Recon produces the facts every later step reuses: how to verify, what to match, what to skip, and what is already decided. Finish with the **recon facts block** in section 8.

## 1. Read, in this order

| Read | Extract |
|------|---------|
| Agent guides: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`, `.github/copilot-instructions.md` | Required gates, forbidden actions, commit style. A project guide outranks this skill's defaults. |
| `README`, `CONTRIBUTING`, `CHANGELOG` | Setup steps, release process, recent breaking changes. |
| Root manifests: `go.mod`, `go.work`, `package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`, `justfile` | Languages, versions, workspaces, task names. |
| CI config: `.github/workflows/`, `.gitlab-ci.yml` | The commands CI runs are the verified commands. Prefer them to guesses. |
| Directory tree, two levels deep | Module boundaries, test layout, generated and vendored directories. |
| Intent and design docs: ADRs (`docs/adr/`, `docs/decisions/`), PRDs, `CONTEXT.md`, `DESIGN.md`, `PRODUCT.md`, roadmaps | Decided tradeoffs, product direction, domain vocabulary. Read what exists; skip silently what does not. |
| Prior audits: `code_review/`, `docs/archive/`, `ANALYSIS*`, `*.findings.json`, earlier plans directories | Leads only. Re-verify each claim against current code before reusing it. |

Then measure size and churn:

```sh
git ls-files | wc -l
git log --oneline -30
git log --since=6.months --name-only --format= | grep -v '^$' | sort | uniq -c | sort -rn | head -20
```

The first line is the size: under about 50 source files, audit directly with no subagents. The last line lists churn hotspots, which are audited first. When a decision has no ADR, cite the commit, the doc comment, or the README line that records it.

## 2. Find the verification commands

Record the exact command for each purpose, taken from CI, the Makefile, or the project guide. Never write one from memory.

| Purpose | Record |
|---------|--------|
| Install | The command, and whether it rewrites a lockfile. |
| Build or typecheck | The command. |
| Lint, in check mode | The command. It must not rewrite files. |
| Tests | The full command, a per-package command, and the rough duration. |
| Gate | The one target that means "everything is green", if the repository has one (for example `make check`). |

These rows become the "Commands you will need" table of every plan. When no test or build command works, record that. "Establish a verification baseline" is then finding 1 and precedes every risky plan.

## 3. What you may run

"Read-only" means the working tree is unchanged afterward. Caches and temp files outside it are fine.

| Class | Examples | Rule |
|-------|----------|------|
| Read-only | `git log`, `git diff`, `git show`, `git ls-files`, `grep`, directory listings | Run freely. |
| Checks that execute repository code | build, typecheck, lint, tests, `make` targets | Run in check mode only, and read a Makefile recipe before running its target. Skip slow suites and report them as unrun. |
| Network lookups | `npm audit`, `govulncheck`, `pip-audit`, `go list -m -u all` | Allowed; they send package names and versions only. Skip them when the user asked for offline work. |
| Anything that writes or has outside effects | installs, formatters, code generation, `git commit`, `git checkout`, `git stash`, tag, push, publish, deploy, dependency upgrades | Never. A Make target whose recipe calls `push`, `tag`, `deploy`, `ssh`, `scp`, `rsync`, or `rm -rf` belongs here. |

When the host sandbox blocks the default caches, point them at the system temp directory (`GOCACHE`, `GOLANGCI_LINT_CACHE`, `npm_config_cache`). After any check that executes repository code, run `git status --porcelain`. Only the plans directory may appear. When anything else does, tell the user what the command wrote and stop running checks.

**Whose repository is it?** Judge from `git log`: most recent commits under `git config user.email`, or a remote in the user's account. Confirm the commands with the user before running them in any other repository. When no user can answer, audit by reading, run nothing that executes repository code, and list those checks as unrun.

## 4. Scratch copies

A scratch copy lets you reproduce a finding or run a plan's code without touching the repository:

```sh
scratch=$(mktemp -d) && git archive HEAD | tar -x -C "$scratch"
```

Work only inside the copy, never copy anything back, and delete it when you finish. It holds tracked files at HEAD only, so secrets in untracked files stay behind. A copy cannot build when the project needs sibling directories (a relative `replace`, a `go.work`); then say the finding is unreproduced.

## 5. Working tree state

1. Run `git status --porcelain` and note every modified or untracked file.
2. Run `git rev-parse --short=12 HEAD`. Every plan stamps this commit.
3. A plan describes the stamped commit, and a worktree executor starts from it, so uncommitted edits are invisible to both. When an in-scope file has uncommitted edits, ask the user to commit or stash first. If they decline, excerpt from `git show HEAD:<path>` and say in the plan's "Why this matters" that the working tree differs.
4. When the directory is not a git repository, stop and report. A plan needs a commit to stamp.

## 6. Generated and vendored code

Build the skip list before auditing. It holds `vendor/`, `node_modules/`, build output, lockfiles, any file whose header says `Code generated ... DO NOT EDIT`, and every directory the project's ownership file marks as generated (`.sphere/layout.json` in go-sphere projects).

A defect in generated output belongs to its generator, schema, or template. Find that source and audit it instead. Go details are in `go-ecosystem.md`.

## 7. Workspaces and monorepos

| Situation | Do |
|-----------|----|
| The directory holds several independent git repositories | Ask which repositories to audit. Write each repository's plans in that repository's plans directory. A plan never spans two repositories, because its stamped commit belongs to one. |
| One repository with several modules or packages | Scope each subagent to modules. Record the modules left unaudited. |
| A change in one repository forces a change in another | Write one plan per repository. In the downstream plan's `Depends on` line, name the upstream plan by its repository path, for example `sphere/plans/003-fix-x.md`. State whether the downstream plan needs a released tag or a version bump. |

## 8. Recon facts block

Write it once and keep it in the session. Paste it into every subagent brief when you fan out, and reuse it in every plan.

- **Stack**: languages, frameworks, package manager, runtime versions.
- **Commands**: the table from section 2.
- **Conventions**: style, error handling, test layout, commit message style, each with one exemplar file.
- **Skip list**: generated, vendored, and out-of-audit paths.
- **Decided tradeoffs**: one line each, naming the document, commit, or comment that records it.
- **Risk hints**: what this kind of repository usually gets wrong, such as path handling and command construction in a CLI that writes user files.
- **Prior-audit leads**: unverified claims from earlier reviews.
- **State**: the HEAD commit and the uncommitted files.
