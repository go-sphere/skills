# Agent Reference

Per-agent behavior of `scripts/delegate.py`, checked against claude 2.1.309, codex 0.166, kimi 2.4.1, agy 1.4.12, pi 1.5.0. Flags change between releases; run `DELEGATE run --dry-run` to see the exact command before trusting this table.

## Executable lookup

Order: `DELEGATE_<AGENT>_BIN` (for example `DELEGATE_CLAUDE_BIN`), then `PATH`, then `~/bin`, `~/.local/bin`, `~/.bun/bin`, `~/.kimi-code/bin`, `/opt/homebrew/bin`, `/usr/local/bin`. A set `DELEGATE_<AGENT>_BIN` that is not executable is an error, not a fallthrough.

## Headless command per mode

| Agent | Command core | `read` | `write` | `full` | Resume |
|---|---|---|---|---|---|
| claude | `claude -p PROMPT --output-format json` | `--permission-mode plan` | `--permission-mode acceptEdits` | `--dangerously-skip-permissions` | `--resume ID` |
| codex | `codex exec --json --skip-git-repo-check -` (prompt on stdin) | `--sandbox read-only` | `--sandbox workspace-write` | `--dangerously-bypass-approvals-and-sandbox` | `codex exec resume ... ID -` with `-c sandbox_mode=...` |
| kimi | `kimi -p PROMPT --output-format stream-json` | rejected | same as `full` | `-p` already auto-approves | `-S ID` |
| agy | `agy -p PROMPT --output-format json` | `--mode plan` | `--mode accept-edits` | `--dangerously-skip-permissions` | `--conversation ID` |
| pi | `pi -p --mode json PROMPT` | `--tools read,grep,find,ls` | default tools | default tools | `--session ID` |

`--model` maps to `--model` (claude, agy, pi) or `-m` (codex, kimi). Omit it to use the agent's own default.

## What `write` cannot do

Headless runs cannot answer an approval prompt, so anything outside the mode's allowance is denied or fails.

| Agent | Consequence in `write` |
|---|---|
| claude | Bash commands that are not pre-allowed are denied; the agent usually reports it cannot run tests |
| codex | Sandboxed: no localhost sockets, no writes outside the workspace; Go workers need `GOCACHE=/tmp/...` |
| agy | A denied command ends the run with `failed` and a message naming the permission; rerun in `full` or add an allow rule in its settings |
| kimi | Never prompts; effectively `full` |
| pi | Never prompts; effectively `full` |

Re-run the acceptance commands yourself when the agent says it could not.

## Result parsing

| Agent | Session ID | Response | Failure signal |
|---|---|---|---|
| claude | `session_id` | `result` | `is_error` or a `subtype` starting with `error` |
| codex | `thread.started.thread_id` | last `agent_message` item | `turn.failed` or `error` event |
| kimi | `session.resume_hint.session_id` | `assistant` message content | `error` event |
| agy | `conversation_id` | `response` | `status` other than `SUCCESS` |
| pi | `session` event `id` | last assistant message in `agent_end` | `stopReason` of `error` or `aborted` |

A run is `completed` only when the exit code is 0, no failure signal fired, and the response is non-empty. The session ID may be absent on a completed run; then it cannot be resumed.

## Interactive launch (`launch`)

| Agent | Command | First prompt |
|---|---|---|
| claude | `claude [--model M] <permission flag>` | argv |
| codex | `codex --no-alt-screen [-m M] <sandbox flags>` | argv |
| kimi | `kimi [-m M]` plus `--plan` / `--yolo` / `--auto` | typed after startup (`prompt_via: send`) |
| agy | `agy [--model M] <mode flag>` | `-i PROMPT` |
| pi | `pi [--model M]` plus `--tools read,grep,find,ls` for `read` | argv |

Interactive mode names: claude `plan` / `acceptEdits` / skip-permissions; codex `read-only` / `workspace-write` with `-a on-request` / bypass; kimi plan / "ask when needed" / "never ask"; agy `plan` / `accept-edits` / skip-permissions. `--no-alt-screen` keeps codex scrollback readable by `rex capture`.

## Environment

The child process never receives `REX_SESSION` or `REX_BLOCK`. Codex otherwise inherited them, read the rex skill, and tried to rename the coordinator's session.

## Failure handling

| Symptom | Action |
|---|---|
| `'<agent>' not found` | Install it, or set `DELEGATE_<AGENT>_BIN`; ask the user before installing |
| Sign-in or quota error in `error` | Stop and tell the user; a higher mode cannot fix a login |
| Empty response, exit 0 | Read `stderr.log` in `run_dir`; usually a denied permission |
| `Timed out` | Shrink the task or raise `--timeout`; do not rerun unchanged |
| Resume fails | Check the agent matches the session, and that `--cwd` is the original directory |
