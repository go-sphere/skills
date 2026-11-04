---
name: rex-desktop
description: Coordinate coding agents (claude, codex, kimi, agy, pi) as live workers in Rex floating panes. Use when the user wants to dispatch, fan out, or orchestrate implementation, review, or investigation across several agents and watch them in Rex. Not for one headless task with a structured result — that is `delegate`.
---

# rex-desktop

You are the coordinator. Workers are interactive coding agents, each in its own floating pane over your Rex window. You plan, split work, dispatch, verify, and integrate; workers write the code. `scripts/rex-agent` (next to this file) controls workers. It adds wait-until-done on top of the `rex` CLI, and it asks the `delegate` skill for every agent-specific flag and executable path, so this skill holds no agent knowledge.

Workers are interactive TUIs because Rex reports their state (working, done, blocked, error), which is what `wait` listens to. A headless run reports nothing to Rex.

## Steps

1. Run `python3 <delegate skill>/scripts/delegate.py agents`. Use only installed agents. `rex-agent` finds `delegate.py` in the sibling `delegate` skill directory; set `DELEGATE_PY` if it lives elsewhere.
2. Choose agents with the routing table and modes with the mode table.
3. Create one git worktree and branch per writing worker (see Isolation).
4. Spawn one worker at a time: `R=<this skill's directory>/scripts/rex-agent`, then `$R spawn --name auth-fix --agent codex --cwd "$WORKTREE" --mode write --prompt "$(cat brief.md)"`.
5. Wait: `$R wait --name auth-fix --for 1800`. For several workers, run one `wait` per worker in parallel background shells.
6. Read the result with `$R capture --name auth-fix`. Ask workers for a compact fixed-format final report; the capture is a screen, not a transcript.
7. Follow up on the same worker with `$R send --name auth-fix "Also cover the empty-token case"`. It already holds the context.
8. Verify every result yourself (see Verify), then `$R close --name auth-fix`.

`wait` exit codes:

| Code | Meaning | Do |
|---|---|---|
| 0 | done | capture and verify |
| 3 | blocked: a permission, question, or login | capture, then `send` an answer or ask the user; credentials and judgment calls go to the user |
| 4 | error | capture and read the error |
| 5 | process exited | capture; respawn if needed |
| 6 | timeout | capture; if the state was `none`, look for a startup prompt |
| 7 | quiet: no state reported and the screen stopped changing | capture; the agent either finished or waits on a prompt |

`$R status` lists workers with their last reported state.

## Writing the Brief

A worker knows nothing you know. Each prompt needs the objective, the paths it owns, the paths it must not touch, the acceptance commands to run, and what to report (files changed, commands run, anything unresolved). A vague brief returns vague work.

## Isolation

Parallel workers that write code each get their own worktree and branch, otherwise they overwrite each other:

```sh
git worktree add ../wt-auth-fix -b task/auth-fix
```

Give workers disjoint file ownership and merge branches one at a time. Read-only workers share the main checkout. A worktree isolates files, not the machine; it is not a security sandbox.

## Routing

| Task | Agent | Why |
|---|---|---|
| Multi-file implementation, debugging, test fixes | `claude` or `codex` | strongest at sustained edits |
| Independent review of someone else's change | a different agent than the author, `--mode read` | avoids self-confirmation |
| Cheap bulk work: small edits, summaries, greps, drafts | `pi` or `kimi` | low cost |

Pass `--model` only when the user asked for one or the task needs it. Do not substitute a model silently when the requested one fails; report it.

## Modes

| Mode | Meaning |
|---|---|
| `read` (default) | no edits: plan mode, read-only sandbox, or a read-only tool list |
| `write` | edits in `--cwd`; riskier commands ask and show up as `blocked` |
| `full` | no sandbox, no approvals; only in a disposable worktree and only when the user asked |

`pi` has no permission system: its `write` and `full` never ask. Per-agent flags live in the `delegate` skill's `references/agents.md`. Start a new setup with one `read` worker to confirm the loop works before dispatching writers.

## Verify

Never relay a worker's "done" as fact. Inspect the diff (`git -C "$WORKTREE" diff`), run the acceptance commands yourself, and have a different agent review risky changes. Finish with what changed, how you verified it, and what is unresolved.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `wait` returns at once with an old `done` | `wait` compares against the state recorded at the last `spawn` or `send`; send follow-ups through `rex-agent send`, never by typing in the pane |
| `wait` times out with state `none` | First launch in a new directory may show a folder-trust prompt. `capture`; if the user would trust the directory, press enter with `rex send-key -b <block> enter`. Ask first for directories you did not create. agy reports this as `blocked` |
| `wait` returns exit 7 | The agent reports no state to Rex. In testing `claude` reported none; `codex`, `kimi`, `agy`, and `pi` did |
| agy or kimi finishes with `done (idle)` | They report `idle` between turns. `wait` accepts it after seeing `working`, or after 20 idle seconds |
| `blocked (auth)` right after spawn | May be transient when several workers start together; `capture` before acting |
| kimi's first prompt is missing | kimi has no startup-prompt argument, so `rex-agent` types it after the TUI reports a state; `capture` to confirm, then `send` it |
| A worker runs `rex ...` commands | Workers start without `REX_SESSION` and `REX_BLOCK`. If one still blocks on a `rex` command, decline it and tell it to stop using rex |
| Codex report loses its first findings | `rex-agent` starts codex with `--no-alt-screen` so `capture` includes scrollback; keep reports compact |
| Reviewer findings differ between runs | Verify each finding in the code before relaying it |
| Go tests fail in codex `write` | Its sandbox cannot bind localhost sockets or write the Go build cache; tell Go workers to set `GOCACHE=/tmp/...` and rerun the tests yourself |

Every worker runs in a floating pane (a Rex floating layer) over the window that holds the coordinator, never in a new tab. Panes open unfocused and cascade by worker count, so none hides another completely. `close` removes the pane with its worker. The registry is `~/.rex-agent/agents.json`; set `REX_AGENT_HOME` to move it. It has no lock, so spawn workers one at a time.

## Rules

1. Dispatch one worker per bounded task and one worktree per writer.
2. Never add `full` mode on your own judgment.
3. Never answer a worker's credential or login prompt yourself.
4. Close workers you no longer need.
5. If the task needs no watching or steering, use `delegate` directly instead of a floating pane.

## Related Skills

- Upstream — none. The user supplies the task list; without one, plan the split yourself.
- Downstream — none; the coordinator verifies and reports.
- Boundary — `delegate` owns a single headless run and every agent flag; this skill owns live panes, waiting, and integration.
- Companion — `delegate` is required for `rex-agent spawn`; the `rex` skill documents the underlying CLI.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
