#!/usr/bin/env python3
"""Run one coding agent headless, or print the command that opens it interactively.

Agents: claude, codex, kimi, agy, pi. Executables are found on PATH; nothing is
installed or configured. Per-run artifacts go under $DELEGATE_HOME (default ~/.delegate).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

CONTRACT_VERSION = 1
AGENTS = ("claude", "codex", "kimi", "agy", "pi")
ALIASES = {
    "cc": "claude",
    "claude-code": "claude",
    "antigravity": "agy",
    "anti": "agy",
    "kimi-code": "kimi",
}
MODES = ("read", "write", "full")
DEFAULT_TIMEOUT = 3600
EXIT_FAILED = 1
EXIT_USAGE = 2
EXIT_TIMEOUT = 124
# Workers must not act on the coordinator's Rex session or pane.
DROPPED_ENV = ("REX_SESSION", "REX_BLOCK")
# Agents whose installers add a directory that a non-login shell may not have on PATH.
FALLBACK_DIRS = ("bin", ".local/bin", ".bun/bin", ".kimi-code/bin")
SYSTEM_DIRS = ("/opt/homebrew/bin", "/usr/local/bin")
READ_TOOLS = "read,grep,find,ls"


class DelegateError(Exception):
    pass


def canonical(name: str) -> str:
    agent = ALIASES.get(name.strip().lower(), name.strip().lower())
    if agent not in AGENTS:
        raise DelegateError(f"Unsupported agent '{name}'. Choose from: {', '.join(AGENTS)}")
    return agent


def is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def find_binary(agent: str) -> dict[str, str] | None:
    """Locate the agent executable: $DELEGATE_<AGENT>_BIN, then PATH, then common install dirs."""
    env_key = f"DELEGATE_{agent.upper()}_BIN"
    override = os.environ.get(env_key)
    if override:
        path = Path(override).expanduser()
        if not is_executable(path):
            raise DelegateError(f"{env_key} is not an executable file: {path}")
        return {"path": str(path.resolve()), "source": env_key}
    found = shutil.which(agent)
    if found:
        return {"path": found, "source": "PATH"}
    home = Path.home()
    for directory in [home / d for d in FALLBACK_DIRS] + [Path(d) for d in SYSTEM_DIRS]:
        candidate = directory / agent
        if is_executable(candidate):
            return {"path": str(candidate), "source": "known-dir"}
    return None


def require_binary(agent: str) -> str:
    found = find_binary(agent)
    if not found:
        raise DelegateError(
            f"'{agent}' not found. Install it, put it on PATH, or set DELEGATE_{agent.upper()}_BIN."
        )
    return found["path"]


def probe_version(path: str) -> str | None:
    try:
        proc = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    lines = (proc.stdout or proc.stderr or "").strip().splitlines()
    return lines[0][:200] if lines else None


def lead_safe(prompt: str) -> str:
    # A prompt that begins with '-' would be parsed as a flag by several of the CLIs.
    prompt = prompt.strip()
    return f"Task: {prompt}" if prompt.startswith("-") else prompt


def resume_command(agent: str, binary: str, session_id: str | None) -> str | None:
    """The command that reopens a headless session in the agent's own TUI."""
    if not session_id:
        return None
    name = Path(binary).name if Path(binary).name == agent else binary
    parts = {
        "claude": [name, "--resume", session_id],
        "codex": [name, "resume", session_id],
        "kimi": [name, "-S", session_id],
        "agy": [name, "--conversation", session_id],
        "pi": [name, "--session", session_id],
    }[agent]
    return shlex.join(parts)


def headless_command(
    agent: str, binary: str, prompt: str, mode: str, model: str | None, session: str | None
) -> tuple[list[str], str | None]:
    """Build the one-shot command. Returns argv and the stdin text (None when the prompt is in argv)."""
    prompt = lead_safe(prompt)
    if agent == "claude":
        cmd = [binary, "-p", prompt, "--output-format", "json"]
        if model:
            cmd += ["--model", model]
        if session:
            cmd += ["--resume", session]
        cmd += {
            "read": ["--permission-mode", "plan"],
            "write": ["--permission-mode", "acceptEdits"],
            "full": ["--dangerously-skip-permissions"],
        }[mode]
        return cmd, None

    if agent == "codex":
        if session:
            # `exec resume` takes no --sandbox/--cd, so the policy goes through config overrides.
            sandbox = {
                "read": ["-c", 'sandbox_mode="read-only"'],
                "write": ["-c", 'sandbox_mode="workspace-write"'],
                "full": ["--dangerously-bypass-approvals-and-sandbox"],
            }[mode]
            cmd = [binary, "exec", "resume", "--json", "--skip-git-repo-check", *sandbox]
            if model:
                cmd += ["-m", model]
            return cmd + [session, "-"], prompt
        sandbox = {
            "read": ["--sandbox", "read-only"],
            "write": ["--sandbox", "workspace-write"],
            "full": ["--dangerously-bypass-approvals-and-sandbox"],
        }[mode]
        cmd = [binary, "exec", "--json", "--skip-git-repo-check", *sandbox]
        if model:
            cmd += ["-m", model]
        return cmd + ["-"], prompt

    if agent == "kimi":
        if mode == "read":
            raise DelegateError(
                "kimi -p always auto-approves, so it cannot run read-only. "
                "Use --mode write, or open it interactively with --plan via `launch`."
            )
        cmd = [binary, "-p", prompt, "--output-format", "stream-json"]
        if model:
            cmd += ["-m", model]
        if session:
            cmd += ["-S", session]
        return cmd, None

    if agent == "agy":
        cmd = [binary, "-p", prompt, "--output-format", "json"]
        if model:
            cmd += ["--model", model]
        if session:
            cmd += ["--conversation", session]
        cmd += {
            "read": ["--mode", "plan"],
            "write": ["--mode", "accept-edits"],
            "full": ["--dangerously-skip-permissions"],
        }[mode]
        return cmd, None

    # pi has no permission system: write and full are identical, read removes the mutating tools.
    cmd = [binary, "-p", "--mode", "json"]
    if model:
        cmd += ["--model", model]
    if session:
        cmd += ["--session", session]
    if mode == "read":
        cmd += ["--tools", READ_TOOLS]
    return cmd + [prompt], None


def interactive_command(
    agent: str, binary: str, mode: str, model: str | None, prompt: str | None
) -> tuple[list[str], str]:
    """Build the TUI command. Returns argv and how the first prompt travels: "argv", "send" or "none"."""
    prompt = lead_safe(prompt) if prompt else None
    if agent == "claude":
        cmd = [binary]
        if model:
            cmd += ["--model", model]
        cmd += {
            "read": ["--permission-mode", "plan"],
            "write": ["--permission-mode", "acceptEdits"],
            "full": ["--dangerously-skip-permissions"],
        }[mode]
        return (cmd + [prompt], "argv") if prompt else (cmd, "none")

    if agent == "codex":
        # --no-alt-screen keeps scrollback, so a later capture sees the whole report.
        cmd = [binary, "--no-alt-screen"]
        if model:
            cmd += ["-m", model]
        cmd += {
            "read": ["-s", "read-only", "-a", "on-request"],
            "write": ["-s", "workspace-write", "-a", "on-request"],
            "full": ["--dangerously-bypass-approvals-and-sandbox"],
        }[mode]
        return (cmd + [prompt], "argv") if prompt else (cmd, "none")

    if agent == "kimi":
        # kimi has no initial-prompt argument; the caller types it after startup.
        cmd = [binary]
        if model:
            cmd += ["-m", model]
        cmd += {"read": ["--plan"], "write": ["--yolo"], "full": ["--auto"]}[mode]
        return cmd, "send" if prompt else "none"

    if agent == "agy":
        cmd = [binary]
        if model:
            cmd += ["--model", model]
        cmd += {
            "read": ["--mode", "plan"],
            "write": ["--mode", "accept-edits"],
            "full": ["--dangerously-skip-permissions"],
        }[mode]
        return (cmd + ["-i", prompt], "argv") if prompt else (cmd, "none")

    cmd = [binary]
    if model:
        cmd += ["--model", model]
    if mode == "read":
        cmd += ["--tools", READ_TOOLS]
    return (cmd + [prompt], "argv") if prompt else (cmd, "none")


def json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    for candidate in [stripped, *reversed(stripped.splitlines())]:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def json_events(text: str) -> list[dict[str, Any]]:
    events = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def message_text(value: Any) -> str:
    """Join the text blocks of a message content, which is a string or a list of typed blocks."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(
            str(block["text"]) for block in value
            if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
        )
    return ""


def parse_output(agent: str, out: str, previous: str | None) -> dict[str, Any]:
    """Extract session_id, response and error from an agent's machine-readable stdout."""
    session_id, response, error = previous, "", None

    if agent in ("claude", "agy"):
        obj = json_object(out)
        if obj is None:
            return {"session_id": session_id, "response": "", "error": "CLI did not return a JSON result"}
        if agent == "claude":
            session_id = obj.get("session_id") or session_id
            response = str(obj.get("result") or "")
            if obj.get("is_error") or str(obj.get("subtype", "success")).startswith("error"):
                error = response or str(obj.get("subtype") or "CLI reported an error")
        else:
            session_id = obj.get("conversation_id") or session_id
            response = str(obj.get("response") or "")
            if obj.get("status") != "SUCCESS":
                error = str(obj.get("error") or obj.get("status") or "agy did not report SUCCESS")

    elif agent == "codex":
        messages = []
        for event in json_events(out):
            kind = event.get("type")
            if kind == "thread.started":
                session_id = event.get("thread_id") or session_id
            elif kind == "item.completed":
                item = event.get("item") or {}
                if item.get("type") == "agent_message" and item.get("text"):
                    messages.append(str(item["text"]))
            elif kind in ("turn.failed", "error"):
                detail = event.get("error") or event.get("message")
                error = (detail.get("message") if isinstance(detail, dict) else detail) or "Codex turn failed"
        response = messages[-1] if messages else ""

    elif agent == "kimi":
        chunks = []
        for event in json_events(out):
            if event.get("type") == "session.resume_hint" and event.get("session_id"):
                session_id = str(event["session_id"])
            elif event.get("role") == "assistant":
                chunks.append(message_text(event.get("content")))
            elif event.get("type") == "error" or event.get("role") == "error":
                error = str(event.get("content") or event.get("message") or event)
        response = "\n".join(chunk for chunk in chunks if chunk).strip()

    else:  # pi
        last: dict[str, Any] | None = None
        for event in json_events(out):
            if event.get("type") == "session" and event.get("id"):
                session_id = str(event["id"])
            elif event.get("type") == "agent_end":
                for message in event.get("messages") or []:
                    if isinstance(message, dict) and message.get("role") == "assistant":
                        last = message
        if last is None:
            error = "pi finished without an assistant message"
        else:
            response = message_text(last.get("content"))
            if last.get("stopReason") in ("error", "aborted"):
                error = str(last.get("errorMessage") or last["stopReason"])

    return {"session_id": session_id, "response": response, "error": error}


def terminate(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
            proc.wait(timeout=3)
            return
        except ProcessLookupError:
            return
        except subprocess.TimeoutExpired:
            continue


def state_dir() -> Path:
    return Path(os.environ.get("DELEGATE_HOME") or Path.home() / ".delegate").expanduser()


def read_prompt(args: argparse.Namespace, required: bool) -> str | None:
    if args.prompt is not None:
        text = args.prompt
    elif args.prompt_file is not None:
        text = sys.stdin.read() if args.prompt_file == "-" else Path(args.prompt_file).read_text(encoding="utf-8")
    elif required:
        raise DelegateError("Provide --prompt or --prompt-file")
    else:
        return None
    if not text.strip():
        raise DelegateError("The prompt is empty")
    return text


def with_entry_files(prompt: str, cwd: Path, files: list[str]) -> str:
    resolved = []
    for raw in files:
        path = Path(raw).expanduser()
        path = path if path.is_absolute() else cwd / path
        if not path.is_file():
            raise DelegateError(f"Entry file does not exist: {path}")
        resolved.append(str(path.resolve()))
    return f"{prompt.strip()}\n\nStart with these files: {', '.join(resolved)}" if resolved else prompt


def resolve_cwd(raw: str) -> Path:
    cwd = Path(raw).expanduser().resolve()
    if not cwd.is_dir():
        raise DelegateError(f"Not a directory: {cwd}")
    return cwd


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps({"contract_version": CONTRACT_VERSION, **payload}, ensure_ascii=False, indent=2))


def cmd_agents(args: argparse.Namespace) -> int:
    rows = []
    for agent in AGENTS:
        try:
            found = find_binary(agent)
            error = None
        except DelegateError as exc:
            found, error = None, str(exc)
        rows.append({
            "agent": agent,
            "installed": found is not None,
            "path": found["path"] if found else None,
            "source": found["source"] if found else None,
            "version": probe_version(found["path"]) if found else None,
            "aliases": sorted(a for a, target in ALIASES.items() if target == agent),
            "error": error,
        })
    if args.json:
        emit({"status": "OK", "agents": rows})
    else:
        for row in rows:
            state = f"{row['path']}  {row['version'] or ''}  ({row['source']})" if row["installed"] else (
                row["error"] or "not installed")
            print(f"{row['agent']:<7}{state}")
    return 0


def cmd_launch(args: argparse.Namespace) -> int:
    agent = canonical(args.agent)
    binary = require_binary(agent)
    prompt = read_prompt(args, required=False)
    argv, prompt_via = interactive_command(agent, binary, args.mode, args.model, prompt)
    emit({"status": "OK", "agent": agent, "mode": args.mode, "argv": argv, "prompt_via": prompt_via,
          "prompt": prompt if prompt_via == "send" else None})
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    agent = canonical(args.agent)
    if args.timeout <= 0:
        raise DelegateError("--timeout must be greater than zero")
    cwd = resolve_cwd(args.cwd)
    prompt = with_entry_files(read_prompt(args, required=True) or "", cwd, args.file or [])
    binary = require_binary(agent)
    command, stdin_text = headless_command(agent, binary, prompt, args.mode, args.model, args.session)
    shown = ["<prompt>" if part == lead_safe(prompt) else part for part in command]

    if args.dry_run:
        emit({"status": "DRY_RUN", "agent": agent, "cwd": str(cwd), "mode": args.mode,
              "session_id": args.session, "command": shown, "stdin": stdin_text is not None})
        return 0

    run_id = f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    run_dir = state_dir() / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    env = {k: v for k, v in os.environ.items() if k not in DROPPED_ENV}
    started = time.monotonic()
    out = err = ""
    exit_code = 1
    try:
        proc = subprocess.Popen(
            command, cwd=str(cwd), env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
            start_new_session=True,
        )
        try:
            out, err = proc.communicate(input=stdin_text, timeout=args.timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            terminate(proc)
            out, err = proc.communicate()
            exit_code = EXIT_TIMEOUT
            err = f"{err}\nTimed out after {args.timeout}s".strip()
    except OSError as exc:
        err, exit_code = str(exc), 127
    (run_dir / "stdout.log").write_text(out or "", encoding="utf-8")
    (run_dir / "stderr.log").write_text(err or "", encoding="utf-8")

    parsed = parse_output(agent, out or "", args.session)
    error = parsed["error"]
    completed = exit_code == 0 and not error and bool(parsed["response"].strip())
    if not completed:
        error = error or ("Agent returned an empty response" if exit_code == 0 else f"Agent exited with code {exit_code}")
        tail = (err or "").strip()[-2000:]
        if tail and tail not in error:
            error = f"{error}\n{tail}"
    result = {
        "status": "completed" if completed else "failed",
        "agent": agent,
        "session_id": parsed["session_id"],
        "response": parsed["response"],
        "error": None if completed else error,
        "exit_code": exit_code,
        "cwd": str(cwd),
        "mode": args.mode,
        "model": args.model,
        "resume_command": resume_command(agent, binary, parsed["session_id"]),
        "run_dir": str(run_dir),
        "elapsed_seconds": round(time.monotonic() - started, 1),
    }
    (run_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        emit(result)
    else:
        for key in ("status", "agent", "session_id", "run_dir", "elapsed_seconds"):
            print(f"{key}={result[key] or ''}")
        print("---")
        print(result["response"] if completed else result["error"])
    if completed:
        return 0
    return EXIT_TIMEOUT if exit_code == EXIT_TIMEOUT else EXIT_FAILED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a coding agent headless or print its interactive command")
    sub = parser.add_subparsers(dest="command", required=True)

    agents = sub.add_parser("agents", help="List supported agents and whether each is installed")
    agents.add_argument("--json", action="store_true")

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--agent", required=True, help=f"{', '.join(AGENTS)} (aliases: {', '.join(ALIASES)})")
        p.add_argument("--mode", choices=MODES, default="read",
                       help="read: no edits; write: edits in the workspace; full: no sandbox or approvals")
        p.add_argument("--model", help="Model name passed through to the agent; omit to use its default")
        prompt = p.add_mutually_exclusive_group()
        prompt.add_argument("--prompt")
        prompt.add_argument("--prompt-file", help="Read the prompt from this file, or '-' for stdin")

    launch = sub.add_parser("launch", help="Print the JSON command that opens the agent's TUI")
    common(launch)

    run = sub.add_parser("run", help="Run or resume one headless task")
    common(run)
    run.add_argument("--cwd", default=os.getcwd())
    run.add_argument("--session", help="Session ID from an earlier run of the same agent")
    run.add_argument("--file", action="append", help="Entry file to look at first (repeatable)")
    run.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--json", action="store_true", help="Print one JSON object instead of key=value lines")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return {"agents": cmd_agents, "launch": cmd_launch, "run": cmd_run}[args.command](args)
    except DelegateError as exc:
        if getattr(args, "json", False) or args.command == "launch":
            emit({"status": "ERROR", "error": str(exc)})
        else:
            sys.stderr.write(f"[ERROR] {exc}\n")
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
