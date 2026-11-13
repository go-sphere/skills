---
name: delegate
description: Hand one bounded task to another coding agent (claude, codex, kimi, agy, pi) headless, get a structured result, and resume its session. Use when the user says delegate, 交给 codex/kimi/pi 做, 让另一个 agent 评审, or wants a second opinion. Not for coordinating several live agents in Rex floating panes — that is `rex-desktop`.
---

# Delegate

Run one task in another coding agent's non-interactive mode and read back its answer. One script, `scripts/delegate.py`, owns every agent-specific flag, executable lookup, output parser, and resume command. Supported agents: `claude` (alias `cc`), `codex`, `kimi`, `agy` (aliases `antigravity`, `anti`), `pi`.

`DELEGATE` below means `python3 <this skill's directory>/scripts/delegate.py`. Resolve the directory from where this file was loaded; never copy an absolute path into a brief or a script.

## Steps

1. Run `DELEGATE agents`. It lists which of the five agents are installed and their versions. Use only installed agents; never install or log in for the user.
2. Pick the agent. Use the one the user named. Otherwise follow the routing table.
3. Pick the mode with the permission table. Default to `read`.
4. Write the brief: objective, paths it owns, paths it must not touch, the exact acceptance commands, and the report format you want. The agent knows nothing you know.
5. Preview once when the setup is new: `DELEGATE run --agent <name> --mode <mode> --prompt-file brief.md --dry-run`.
6. Run it: `DELEGATE run --agent <name> --cwd <dir> --mode <mode> --prompt-file brief.md`. Long tasks block until the agent exits; the default timeout is 3600 seconds.
7. Read the printed response. A `failed` status prints the error; fix the cause (login, permission, scope) before retrying.
8. Verify the work yourself: inspect `git diff`, rerun the acceptance commands, and read any claimed file. The agent's report is a claim, not evidence.
9. For rework, resume with `--session <session_id>` and send only the new information. Resume works only with the same agent.

## Routing

| Task | Agent | Why |
|---|---|---|
| Multi-file implementation, debugging, test fixes | `claude` or `codex` | strongest at sustained edits |
| Independent review of someone else's change | an agent other than the author, `--mode read` | avoids self-confirmation |
| Cheap bulk work: small edits, summaries, greps, drafts | `pi` or `kimi` | low cost |

Pass `--model` only when the user asked for one. Do not substitute a model silently when the requested one fails; report it.

## Modes

| Mode | Meaning | When |
|---|---|---|
| `read` (default) | no file edits | review, investigation, planning |
| `write` | edits inside `--cwd`; actions that need approval are denied because headless cannot ask | implementation whose checks need no extra permission |
| `full` | no sandbox, no approvals | only in a disposable worktree, and only when the user agreed |

`kimi` cannot run read-only headless. `pi` has no permission system, so `write` and `full` are the same for it. Read [references/agents.md](references/agents.md) before relying on any mode.

## Output

Default output is `status=`, `agent=`, `session_id=`, `run_dir=`, `elapsed_seconds=`, then `---` and the response. `--json` prints one object with the same fields plus `resume_command`, `exit_code`, and `error`. Exit codes: 0 completed, 1 failed, 2 usage or missing agent, 124 timeout. Each run keeps `prompt.txt`, `stdout.log`, `stderr.log`, and `result.json` under `$DELEGATE_HOME/runs/<id>` (default `~/.delegate`).

`DELEGATE launch --agent <name> --mode <mode> [--prompt ...]` prints the JSON argv that opens the agent's interactive UI. `rex-desktop` uses it; call it directly only to build your own terminal launcher.

## Reference Map

| Read | When |
|---|---|
| [references/agents.md](references/agents.md) | Before choosing `write` or `full`, when an agent fails, or when changing the script |

## Rules

1. Delegate one bounded task per run; split larger work yourself.
2. Never put secrets in a prompt. Agents use their own logins.
3. Use `--cwd` to set the workspace; run parallel writers in separate git worktrees.
4. Do not retry blindly after a failure; read the error and change something first.
5. Set `DELEGATE_<AGENT>_BIN` (for example `DELEGATE_PI_BIN`) when an executable is not on PATH.
6. Report to the user what changed, how you verified it, and what is unresolved.

## Related Skills

- Upstream — none. Any skill may hand a bounded task to this one.
- Downstream — none; the caller verifies the result itself.
- Boundary — `rex-desktop` owns live, parallel agents in Rex floating panes; this skill owns one headless run.
- Companion — `rex-desktop` calls the launch subcommand of this skill to open agents without knowing their flags.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
