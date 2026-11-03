---
name: rex-desktop
description: Coordinate coding agents (Claude Code, Codex, pi) as workers in Rex tabs. Use when the user wants to delegate implementation, review, or investigation to other coding agents, run several agents in parallel, route tasks to codex/pi/claude, or "orchestrate"/"dispatch"/"fan out" work across Rex panes, even if they don't name this skill. You plan and review; workers implement.
---

# rex-desktop

You are the coordinator. Workers are interactive coding agents, each in its own Rex tab. You plan, split work, dispatch, verify, and integrate; workers write the code. Use `scripts/rex-agent` (next to this file) for all worker control. It sits on top of the `rex` skill's primitives and adds what Rex lacks: wait-until-done.

Workers must be interactive TUIs, not `claude -p` / `codex exec` / `pi -p`. Only interactive agents report their state (Rex OSC 7501: working, done, blocked, error), which is what `wait` listens to. Headless runs never report, so waiting on them would hang.

## Loop

```sh
R=~/.claude/skills/rex-desktop/scripts/rex-agent
$R spawn --name auth-fix --agent codex --cwd "$WORKTREE" --mode write --prompt "$(cat brief.md)"
$R wait  --name auth-fix --for 1800     # blocks until the worker settles
$R capture --name auth-fix              # read what it said
$R send  --name auth-fix "Also cover the empty-token case"   # follow-up, same context
$R close --name auth-fix                # when finished; records stay in git, not the tab
```

`wait` exit codes: 0 done, 3 blocked, 4 error, 5 process exited, 6 timeout. Blocked means the worker is asking something (permission, question, login): `capture` to see it, then `send` an answer, or tell the user if it needs credentials or a judgment call. Use the same worker for follow-ups instead of spawning a new one; it already holds the context.

Run several workers by spawning each, then waiting on them in turn (or in parallel background shells). `rex-agent status` lists all workers and their last reported state.

## Writing the task brief

A worker knows nothing you know. Each prompt needs: the objective, the paths it owns, paths it must not touch, the acceptance command(s) to run, and what to report back (files changed, commands run, anything unresolved). Vague briefs return vague work, and the worker's "done" is a claim, not evidence.

## Isolation

Parallel workers that write code each get their own git worktree and branch, otherwise they overwrite each other:

```sh
git worktree add ../wt-auth-fix -b task/auth-fix
```

Give workers disjoint file ownership where possible, and merge branches one at a time. Read-only workers (review, investigation) can share the main checkout. A worktree isolates files, not the machine: it is not a security sandbox.

## Routing: which agent and model

Decide per task, and keep it simple:

| Task | Agent | Why |
|---|---|---|
| Multi-file implementation, debugging, test fixes | `claude` (opus) or `codex` | strongest at sustained edits |
| Independent review of someone else's change | a different agent than the author, `--mode readonly` | avoids self-confirmation |
| Cheap bulk work: small edits, summaries, greps, drafts | `pi` with a fast model (e.g. `deepseek/deepseek-flash`) | low cost |

Pass `--model` only when the user asked for one or the task needs it; otherwise the agent's own default applies. List pi models with `pi --list-models`. Do not silently substitute a model if the requested one fails: report it.

## Modes and permissions

`--mode readonly` (default) maps to plan mode for claude, `-s read-only` for codex, and a read-only tool allowlist for pi. `--mode write` allows edits in the worker's `--cwd`: claude uses acceptEdits, codex uses workspace-write. Both still ask for approval on riskier commands, which shows up as `blocked`. Do not add dangerous skip-permission flags unless the user explicitly asks and the worktree is disposable.

Start new setups with one read-only worker to confirm the loop works before dispatching writers.

## Verify before reporting

Never relay a worker's "done" as fact. Inspect the diff (`git -C "$WORKTREE" diff`), run the acceptance commands yourself, and have a different agent review risky changes. Finish with: what changed, how you verified it, what is unresolved. Close workers you no longer need.

## Troubleshooting

- `wait` returns immediately with `done` from an old run: it compares against the state captured at the last `send`/`spawn`, so make sure you send follow-ups through `rex-agent send`, not by typing in the pane.
- First launch in a new directory shows a folder-trust prompt. Codex does not report it as `blocked`, so `wait` just times out with state `none` (exit 6): `capture`, and if it is a trust prompt for a directory the user would trust, press enter with `rex send-key -b <block> enter`. Ask the user first for directories you did not create.
- Codex runs with `--no-alt-screen` so `capture` includes scrollback. Without it, only the visible screen is captured and long reports lose their first findings. Ask workers for a compact fixed-format final report.
- To wait on many workers, run one `rex-agent wait` per worker in parallel background subshells, then `capture` each. Spawn workers one at a time: the registry has no lock yet.
- `--mode write` (codex workspace-write) was verified on two parallel workers editing disjoint files in one checkout: no collisions, no commits. Codex's sandbox cannot bind localhost sockets or write the Go build cache, so tell Go workers to use `GOCACHE=/tmp/...`; they may retry network-bound tests with escalated permission on their own, so re-run tests yourself.
- Reviewer output varies between runs of the same prompt (a finding can appear in one run and not the next). Verify findings in the code before relaying them.
- Workers are launched without `REX_SESSION`/`REX_BLOCK`. Codex otherwise inherited them, read the rex skill, and tried to rename the coordinator's session. If a worker blocks on a `rex ...` command, decline it (escape) and tell it to stop using rex.
- A tab opened with `--focus=false`, so the user's current tab is undisturbed; the user can watch workers in Rex's tab list.
- Registry lives in `~/.rex-agent/agents.json`; set `REX_AGENT_HOME` to relocate it.
