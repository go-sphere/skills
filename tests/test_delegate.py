#!/usr/bin/env python3
"""Unit tests for skills/delegate/scripts/delegate.py. They never start an agent."""
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "delegate" / "scripts" / "delegate.py"
spec = importlib.util.spec_from_file_location("delegate", SCRIPT)
delegate = importlib.util.module_from_spec(spec)
sys.modules["delegate"] = delegate
spec.loader.exec_module(delegate)

BIN = "/bin/agent"


class Aliases(unittest.TestCase):
    def test_aliases_resolve_to_canonical_names(self):
        self.assertEqual(delegate.canonical("CC"), "claude")
        self.assertEqual(delegate.canonical("antigravity"), "agy")
        self.assertEqual(delegate.canonical("kimi-code"), "kimi")

    def test_unknown_agent_is_rejected(self):
        with self.assertRaises(delegate.DelegateError):
            delegate.canonical("gemini")


class FindBinary(unittest.TestCase):
    def test_env_override_wins_and_must_be_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "pi"
            exe.write_text("#!/bin/sh\n")
            os.environ["DELEGATE_PI_BIN"] = str(exe)
            try:
                with self.assertRaises(delegate.DelegateError):
                    delegate.find_binary("pi")
                exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
                self.assertEqual(delegate.find_binary("pi")["source"], "DELEGATE_PI_BIN")
            finally:
                del os.environ["DELEGATE_PI_BIN"]


class HeadlessCommands(unittest.TestCase):
    def build(self, agent, mode="read", model=None, session=None, prompt="do it"):
        return delegate.headless_command(agent, BIN, prompt, mode, model, session)

    def test_every_agent_has_a_command_in_every_writable_mode(self):
        for agent in delegate.AGENTS:
            for mode in ("write", "full"):
                cmd, _ = self.build(agent, mode)
                self.assertEqual(cmd[0], BIN)

    def test_read_mode_flags(self):
        self.assertIn("plan", self.build("claude")[0])
        self.assertIn("read-only", self.build("codex")[0])
        self.assertIn("plan", self.build("agy")[0])
        self.assertIn(delegate.READ_TOOLS, self.build("pi")[0])

    def test_kimi_rejects_read(self):
        with self.assertRaises(delegate.DelegateError):
            self.build("kimi", "read")

    def test_full_mode_uses_bypass_flags(self):
        self.assertIn("--dangerously-skip-permissions", self.build("claude", "full")[0])
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", self.build("codex", "full")[0])
        self.assertIn("--dangerously-skip-permissions", self.build("agy", "full")[0])

    def test_codex_sends_prompt_on_stdin_and_resumes_with_config_override(self):
        cmd, stdin = self.build("codex", "read", session="abc")
        self.assertEqual(stdin, "do it")
        self.assertEqual(cmd[1:3], ["exec", "resume"])
        self.assertIn('sandbox_mode="read-only"', cmd)
        self.assertEqual(cmd[-2:], ["abc", "-"])

    def test_session_and_model_flags(self):
        expected = {
            "claude": (["--resume", "s1"], ["--model", "m"]),
            "kimi": (["-S", "s1"], ["-m", "m"]),
            "agy": (["--conversation", "s1"], ["--model", "m"]),
            "pi": (["--session", "s1"], ["--model", "m"]),
        }
        for agent, (session_flags, model_flags) in expected.items():
            cmd, _ = self.build(agent, "write", model="m", session="s1")
            for flags in (session_flags, model_flags):
                idx = cmd.index(flags[0])
                self.assertEqual(cmd[idx:idx + 2], flags, agent)

    def test_leading_dash_prompt_is_not_parsed_as_a_flag(self):
        cmd, _ = self.build("claude", "read", prompt="- fix it")
        self.assertEqual(cmd[2], "Task: - fix it")


class InteractiveCommands(unittest.TestCase):
    def test_prompt_transport_per_agent(self):
        via = {a: delegate.interactive_command(a, BIN, "read", None, "hi")[1] for a in delegate.AGENTS}
        self.assertEqual(via, {"claude": "argv", "codex": "argv", "kimi": "send", "agy": "argv", "pi": "argv"})

    def test_no_prompt_means_none(self):
        for agent in delegate.AGENTS:
            self.assertEqual(delegate.interactive_command(agent, BIN, "read", None, None)[1], "none")

    def test_agy_uses_interactive_prompt_flag(self):
        argv, _ = delegate.interactive_command("agy", BIN, "write", None, "hi")
        self.assertEqual(argv[-2:], ["-i", "hi"])

    def test_codex_keeps_scrollback(self):
        argv, _ = delegate.interactive_command("codex", BIN, "read", None, None)
        self.assertIn("--no-alt-screen", argv)


def lines(*events):
    return "\n".join(json.dumps(e) for e in events)


class ParseOutput(unittest.TestCase):
    def test_claude(self):
        out = json.dumps({"session_id": "c1", "result": "ok", "is_error": False, "subtype": "success"})
        self.assertEqual(delegate.parse_output("claude", out, None), {"session_id": "c1", "response": "ok", "error": None})
        bad = json.dumps({"session_id": "c1", "result": "boom", "is_error": True})
        self.assertEqual(delegate.parse_output("claude", bad, None)["error"], "boom")

    def test_agy_requires_success_status(self):
        ok = json.dumps({"conversation_id": "a1", "status": "SUCCESS", "response": "ok\n"})
        self.assertIsNone(delegate.parse_output("agy", ok, None)["error"])
        bad = json.dumps({"conversation_id": "a1", "status": "FAILED", "response": ""})
        self.assertEqual(delegate.parse_output("agy", bad, None)["error"], "FAILED")

    def test_codex_takes_last_agent_message(self):
        out = lines(
            {"type": "thread.started", "thread_id": "t1"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "first"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "last"}},
        )
        self.assertEqual(delegate.parse_output("codex", out, None), {"session_id": "t1", "response": "last", "error": None})

    def test_kimi_joins_assistant_chunks_and_reads_resume_hint(self):
        out = lines(
            {"role": "assistant", "content": "a"},
            {"role": "assistant", "content": [{"type": "text", "text": "b"}]},
            {"type": "session.resume_hint", "session_id": "k1"},
        )
        self.assertEqual(delegate.parse_output("kimi", out, None), {"session_id": "k1", "response": "a\nb", "error": None})

    def test_pi_reads_session_and_final_assistant_message(self):
        out = lines(
            {"type": "session", "id": "p1"},
            {"type": "agent_end", "messages": [
                {"role": "user", "content": [{"type": "text", "text": "q"}]},
                {"role": "assistant", "content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": "ok"}],
                 "stopReason": "stop"},
            ]},
        )
        self.assertEqual(delegate.parse_output("pi", out, None), {"session_id": "p1", "response": "ok", "error": None})

    def test_pi_error_stop_reason_is_a_failure(self):
        out = lines({"type": "agent_end", "messages": [
            {"role": "assistant", "content": [], "stopReason": "error", "errorMessage": "no key"}]})
        self.assertEqual(delegate.parse_output("pi", out, None)["error"], "no key")

    def test_garbage_output_is_an_error_not_a_crash(self):
        self.assertIsNotNone(delegate.parse_output("claude", "not json", None)["error"])
        self.assertIsNotNone(delegate.parse_output("pi", "not json", None)["error"])

    def test_previous_session_is_kept_when_output_has_none(self):
        out = lines({"type": "agent_end", "messages": [{"role": "assistant", "content": "ok"}]})
        self.assertEqual(delegate.parse_output("pi", out, "keep")["session_id"], "keep")


class ResumeCommand(unittest.TestCase):
    def test_standard_name_stays_short_and_custom_path_is_kept(self):
        self.assertEqual(delegate.resume_command("codex", "/opt/x/codex", "s"), "codex resume s")
        self.assertEqual(delegate.resume_command("pi", "/opt/x/mypi", "s"), "/opt/x/mypi --session s")
        self.assertIsNone(delegate.resume_command("pi", "/opt/x/pi", None))


if __name__ == "__main__":
    unittest.main(verbosity=1)
