#!/usr/bin/env python3
"""Unit tests for skills/review-loop/scripts/review_lint.py. Folders are built in a temp directory."""
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "review-loop"
spec = importlib.util.spec_from_file_location("review_lint", SKILL / "scripts" / "review_lint.py")
assert spec is not None and spec.loader is not None
review_lint = importlib.util.module_from_spec(spec)
sys.modules["review_lint"] = review_lint
spec.loader.exec_module(review_lint)

SUMMARY = """\
# Review Summary

- `target_rev`: {rev}

## Fix Approval Checklist

- [{a}] `RF-001` first
  - `status`: `open`
- [{b}] `RF-002` second
  - `status`: `open`
"""

PLAN = """\
# Fix Plan

## Selected Items

- `RF-001`
  - `status`: `approved_for_fix`

## Out Of Scope
"""

STATUS = """\
# Review Status

## Status Table

| Item | Status | Status Label | Evidence | Updated At |
| --- | --- | --- | --- | --- |
| `RF-001` | `{status}` | label | evidence | now |

## Test Evidence

| Command | Result | Notes |
| --- | --- | --- |
| go test ./... | {result} | ok |
"""

VERIFY = """\
# Verification Report

## Verification Results

### Item RF-001

- `status`: `{status}`
"""


class LintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, text):
        (self.dir / name).write_text(text, encoding="utf-8")

    def problems(self):
        return [(level, name, message) for level, name, message in review_lint.lint(self.dir)]

    def errors(self):
        return [p for p in self.problems() if p[0] == "ERROR"]

    def test_clean_folder_has_no_errors(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b=" "))
        self.write("fix-plan.md", PLAN)
        self.write("status.md", STATUS.format(status="fixed", result="passed"))
        self.assertEqual(self.errors(), [])

    def test_duplicate_id_is_an_error(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b=" ") + "- [ ] `RF-001` again\n")
        self.assertTrue(any("more than once" in m for _, _, m in self.errors()))

    def test_unticked_item_in_fix_plan_is_an_error(self):
        self.write("summary.md", SUMMARY.format(rev="none", a=" ", b=" "))
        self.write("fix-plan.md", PLAN)
        self.assertTrue(any("not ticked" in m for _, n, m in self.errors() if n == "fix-plan.md"))

    def test_fix_stage_status_on_unticked_item_is_an_error(self):
        self.write("summary.md", SUMMARY.format(rev="none", a=" ", b=" "))
        self.write("status.md", STATUS.format(status="fixed", result="passed"))
        self.assertTrue(any("not ticked" in m for _, n, m in self.errors() if n == "status.md"))

    def test_unknown_status_is_an_error(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b=" "))
        self.write("status.md", STATUS.format(status="done", result="passed"))
        self.assertTrue(any("'done'" in m for _, _, m in self.errors()))

    def test_fixed_without_passing_test_is_an_error(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b=" "))
        self.write("status.md", STATUS.format(status="fixed", result="blocked"))
        self.assertTrue(any("no passed row" in m for _, _, m in self.errors()))

    def test_test_blocked_needs_no_passing_test(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b=" "))
        self.write("status.md", STATUS.format(status="test_blocked", result="blocked"))
        self.assertEqual(self.errors(), [])

    def test_verified_requires_a_verify_result(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b=" "))
        self.write("status.md", STATUS.format(status="verified", result="passed"))
        self.assertTrue(any("no verified result" in m for _, _, m in self.errors()))
        self.write("verify.md", VERIFY.format(status="verification_failed"))
        self.assertTrue(any("no verified result" in m for _, _, m in self.errors()))
        self.write("verify.md", VERIFY.format(status="verified"))
        self.assertEqual(self.errors(), [])

    def test_status_without_summary_is_an_error(self):
        self.write("status.md", STATUS.format(status="open", result="passed"))
        self.assertTrue(any("without summary.md" in m for _, _, m in self.errors()))

    def test_ticked_item_without_status_row_warns(self):
        self.write("summary.md", SUMMARY.format(rev="none", a="x", b="x"))
        self.write("status.md", STATUS.format(status="fixed", result="passed"))
        warnings = [m for level, _, m in self.problems() if level == "WARN"]
        self.assertTrue(any("RF-002" in m for m in warnings))

    def test_placeholder_comments_warn(self):
        self.write("summary.md", SUMMARY.format(rev="none", a=" ", b=" ") + "<!-- left over -->\n")
        self.assertTrue(any("template comment" in m for level, _, m in self.problems() if level == "WARN"))

    def test_stale_target_rev_warns(self):
        subprocess.run(["git", "init", "-q", str(self.dir)], check=True)
        subprocess.run(
            ["git", "-C", str(self.dir), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"],
            check=True,
        )
        head = subprocess.run(
            ["git", "-C", str(self.dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        self.write("summary.md", SUMMARY.format(rev=head + "+dirty", a=" ", b=" "))
        self.assertFalse(any("stale" in m for _, _, m in self.problems()))
        self.write("summary.md", SUMMARY.format(rev="0" * 12, a=" ", b=" "))
        self.assertTrue(any("stale" in m for _, _, m in self.problems()))

    def test_main_exit_codes(self):
        self.write("summary.md", SUMMARY.format(rev="none", a=" ", b=" "))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(review_lint.main(["x", "lint", str(self.dir)]), 0)
            self.write("status.md", STATUS.format(status="done", result="passed"))
            self.assertEqual(review_lint.main(["x", "lint", str(self.dir)]), 1)
        self.assertEqual(review_lint.main(["x", "lint"]), 2)
        self.assertEqual(review_lint.main(["x", "lint", str(self.dir / "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
