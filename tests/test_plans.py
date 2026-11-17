#!/usr/bin/env python3
"""Unit tests for skills/improve/scripts/plans.py. They build throwaway git repositories."""
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "improve"
spec = importlib.util.spec_from_file_location("plans", SKILL / "scripts" / "plans.py")
assert spec is not None and spec.loader is not None
plans = importlib.util.module_from_spec(spec)
sys.modules["plans"] = plans
spec.loader.exec_module(plans)

SHA = "abcdef123456"


def plan_text(number="001", sha=SHA, depends="none", category="bug", drift="src/a.go", in_scope="- `src/a.go`"):
    return f"""\
# Plan {number}: Fix the thing

> **Executor instructions**: Follow this plan step by step.
>
> **Drift check (run first)**: `git diff --stat {sha}..HEAD -- {drift}`
> Expected: no output.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: {depends}
- **Category**: {category}
- **Finding**: `{category}:src/a.go:Run`
- **Planned at**: commit `{sha}`, 2026-11-13

## Why this matters

Because.

## Current state

- `src/a.go` — the file.

## Commands you will need

| Purpose | Command | Expected |
|---------|---------|----------|
| Tests | `go test ./...` | ok |

## Scope

**In scope** (the only files you may modify):
{in_scope}

**Out of scope** (do NOT touch):
- `src/b.go` — unrelated.

## Git workflow

- Branch: `advisor/{number}-fix-the-thing`

## Steps

### Step 1: Add a failing test

Write the test.

**Verify**: `go test ./...` → FAIL

### Step 2: Fix it

Fix it.

**Verify**: `go test ./...` → ok

## Test plan

- One test.

## Done criteria

- [ ] `go test ./...` exits 0
- [ ] `git status --short` lists only in-scope files

## STOP conditions

- The code does not match.
- A step fails twice.

## Report back

Reply with the status.

## Maintenance notes

- None.
"""


def index_text(rows):
    body = "\n".join(f"| {n} | Title {n} | P2 | S | {dep} | {status} |" for n, dep, status in rows)
    return ("# Implementation Plans\n\n## Execution order & status\n\n"
            "| Plan | Title | Priority | Effort | Depends on | Status |\n"
            "|------|-------|----------|--------|------------|--------|\n" + body + "\n")


def messages(issues, level):
    return [issue.message for issue in issues if issue.level == level]


def git(root, *args, check=True):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false",
         "-C", str(root), *args],
        check=check, capture_output=True, text=True).stdout.strip()


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def lint(self, text, git_handle=None, name="001-fix-the-thing.md"):
        path = self.root / name
        path.write_text(text)
        return plans.lint_plan(plans.parse_plan(path), git_handle)


class GitTempCase(TempCase):
    TEMPLATE_FILES = {"src/a.go": "package a\n"}
    TEMPLATE_DIRS = ()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._template_tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._template_tmp.cleanup)
        tpl = Path(cls._template_tmp.name)
        for rel in cls.TEMPLATE_DIRS:
            (tpl / rel).mkdir(parents=True, exist_ok=True)
        for rel, content in cls.TEMPLATE_FILES.items():
            path = tpl / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        git(tpl, "init", "-q", "-b", "main")
        git(tpl, "add", "-A")
        git(tpl, "commit", "-q", "-m", "init")
        cls._template_root = tpl
        cls._template_sha = git(tpl, "rev-parse", "--short=12", "HEAD")

    def setUp(self):
        super().setUp()
        shutil.copytree(self._template_root, self.root, dirs_exist_ok=True, symlinks=True)
        self.sha = self._template_sha
        self.handle = plans.Git.open(self.root)


class MarkdownHelpers(unittest.TestCase):
    def test_fenced_blocks_hide_their_lines_including_longer_fences(self):
        lines = ["a", "```", "## inside", "```", "b", "````", "```", "## deeper", "````", "c"]
        self.assertEqual([line for _, line in plans.outside_fences(lines)], ["a", "b", "c"])

    def test_headings_ignore_fenced_lines(self):
        lines = ["# T", "## Real", "```md", "## Fake", "```", "### Step 1: x"]
        self.assertEqual([(lvl, text) for lvl, text, _ in plans.find_headings(lines)],
                         [(1, "T"), (2, "Real"), (3, "Step 1: x")])

    def test_fenced_blocks_return_bodies_and_skip_unterminated_ones(self):
        lines = ["x", "```go", "a", "b", "```", "y", "````", "```", "inner", "````", "```", "open"]
        self.assertEqual(list(plans.fenced_blocks(lines)), [(1, ["a", "b"]), (6, ["```", "inner"])])

    def test_scope_bullets_name_every_path_before_the_description(self):
        self.assertEqual(plans.bullet_paths("- `a.go`, `b.go` — see `c.go` for the pattern"),
                         [("a.go", False), ("b.go", False)])
        self.assertEqual(plans.bullet_paths("- `a_test.go` — a new file (create)"), [("a_test.go", True)])
        self.assertEqual(plans.bullet_paths("- `a.go` (create), `b.go`"), [("a.go", True), ("b.go", False)])
        self.assertEqual(plans.bullet_paths("- Any change to the public shape."), [])
        self.assertEqual(plans.bullet_paths("- `go test` is not a path"), [])
        self.assertIsNone(plans.bullet_paths("not a bullet"))

    def test_dependencies_split_local_from_external(self):
        local, external = plans.parse_dependencies("plans/001-a.md, sphere/plans/003-b.md")
        self.assertEqual((local, external), (["001"], ["sphere/plans/003"]))
        self.assertEqual(plans.parse_dependencies("none"), ([], []))
        self.assertEqual(plans.parse_dependencies("./plans/004-x.md")[0], ["004"])


class LintPlan(TempCase):
    def test_a_well_formed_plan_has_no_issues(self):
        self.assertEqual(self.lint(plan_text()), [])

    def test_missing_section_is_an_error(self):
        errors = messages(self.lint(plan_text().replace("## Report back", "## Something else")), "ERROR")
        self.assertIn("missing section '## Report back'", errors)

    def test_toolkit_section_is_optional_but_allowed(self):
        with_toolkit = plan_text().replace("## Scope", "## Suggested executor toolkit\n\n- `go-test`\n\n## Scope", 1)
        self.assertEqual(self.lint(with_toolkit), [])

    def test_sections_out_of_order_warn(self):
        text = plan_text().replace("## Test plan", "## Maintenance notes\n\n- x\n\n## Test plan", 1)
        self.assertIn("sections are out of template order", messages(self.lint(text), "WARN"))

    def test_invalid_field_values_are_errors(self):
        text = plan_text().replace("**Priority**: P2", "**Priority**: P1 | P2 | P3")
        self.assertTrue(any("'Priority' must be one of" in m for m in messages(self.lint(text), "ERROR")))
        text = plan_text().replace("**Category**: bug", "**Category**: chore")
        self.assertTrue(any("'Category' must be one of" in m for m in messages(self.lint(text), "ERROR")))

    def test_planned_at_must_carry_a_commit_and_date(self):
        text = plan_text().replace(f"commit `{SHA}`, 2026-11-13", "recently")
        self.assertTrue(any("'Planned at'" in m for m in messages(self.lint(text), "ERROR")))

    def test_depends_on_must_name_plans(self):
        text = plan_text(depends="the other one")
        self.assertTrue(any("'Depends on'" in m for m in messages(self.lint(text), "ERROR")))

    def test_file_name_must_match_the_plan_number(self):
        issues = self.lint(plan_text(number="002"), name="001-fix-the-thing.md")
        self.assertTrue(any("does not match 'Plan 002'" in m for m in messages(issues, "ERROR")))

    def test_every_step_needs_a_verify_line(self):
        text = plan_text().replace("**Verify**: `go test ./...` → ok", "Run the tests.")
        self.assertIn("step 2 has no '**Verify**:' line", messages(self.lint(text), "ERROR"))

    def test_verify_without_a_command_warns(self):
        text = plan_text().replace("**Verify**: `go test ./...` → ok", "**Verify**: it works")
        self.assertIn("step 2 verification has no command in backticks", messages(self.lint(text), "WARN"))

    def test_steps_must_be_numbered_in_order(self):
        text = plan_text().replace("### Step 2:", "### Step 3:")
        self.assertIn("steps must be numbered 1, 2, 3 in order", messages(self.lint(text), "ERROR"))

    def test_verify_inside_a_code_fence_does_not_count(self):
        text = plan_text().replace("Fix it.\n\n**Verify**: `go test ./...` → ok",
                                   "Fix it.\n\n```\n**Verify**: `go test ./...`\n```")
        self.assertIn("step 2 has no '**Verify**:' line", messages(self.lint(text), "ERROR"))

    def test_bug_plan_should_start_with_a_failing_test(self):
        text = plan_text().replace("Add a failing test", "Edit the code").replace("Write the test.", "Edit.")
        self.assertTrue(any("failing regression test" in m for m in messages(self.lint(text), "WARN")))
        self.assertEqual(self.lint(text.replace("**Category**: bug", "**Category**: dx")
                                   .replace("`bug:src/a.go:Run`", "`dx:src/a.go:Run`")), [])

    def test_done_criteria_need_checkboxes_and_commands(self):
        prose = plan_text().replace("- [ ] `git status --short` lists only in-scope files", "- [ ] nothing else changed")
        self.assertIn("a done criterion without a command is not machine-checkable", messages(self.lint(prose), "WARN"))
        bare = plan_text().replace("- [ ] `go test ./...` exits 0", "- tests pass").replace(
            "- [ ] `git status --short` lists only in-scope files", "- nothing else")
        self.assertIn("Done criteria has no '- [ ]' checkboxes", messages(self.lint(bare), "ERROR"))

    def test_stop_conditions_are_required(self):
        text = plan_text().replace("- The code does not match.\n- A step fails twice.", "")
        self.assertIn("STOP conditions lists nothing", messages(self.lint(text), "ERROR"))
        one = plan_text().replace("- A step fails twice.\n", "")
        self.assertTrue(any("one entry" in m for m in messages(self.lint(one), "WARN")))

    def test_scope_blocks_are_required(self):
        text = plan_text().replace("**Out of scope** (do NOT touch):\n- `src/b.go` — unrelated.\n", "")
        self.assertIn("Scope is missing the '**Out of scope**' block", messages(self.lint(text), "ERROR"))
        empty = plan_text(in_scope="")
        self.assertTrue(any("lists no files" in m for m in messages(self.lint(empty), "ERROR")))

    def test_drift_check_must_match_planned_commit_and_scope(self):
        other = plan_text().replace(f"git diff --stat {SHA}..HEAD", "git diff --stat 1234567..HEAD")
        self.assertIn("the drift check and 'Planned at' name different commits", messages(self.lint(other), "ERROR"))
        uncovered = plan_text(in_scope="- `src/a.go`\n- `src/c.go`")
        self.assertIn("in-scope file 'src/c.go' is not covered by the drift check", messages(self.lint(uncovered), "ERROR"))
        extra = plan_text(drift="src/a.go docs/")
        self.assertIn("the drift check watches 'docs', which is not in scope", messages(self.lint(extra), "WARN"))
        missing = plan_text().replace("`git diff --stat", "`git log")
        self.assertTrue(any("missing the drift-check line" in m for m in messages(self.lint(missing), "ERROR")))

    def test_directory_in_drift_check_covers_files_under_it(self):
        text = plan_text(drift="src/", in_scope="- `src/a.go`")
        self.assertEqual(self.lint(text), [])

    def test_created_files_need_no_drift_coverage(self):
        text = plan_text(in_scope="- `src/a.go`\n- `src/a_test.go` (create)")
        self.assertEqual(self.lint(text), [])

    def test_secret_shaped_values_are_errors_and_are_never_echoed(self):
        key = "AKIA" + "ABCDEFGHIJKLMNOP"
        issues = self.lint(plan_text().replace("Because.", f"The key is {key}."))
        found = [i for i in issues if "AWS access key ID" in i.message]
        self.assertEqual([i.level for i in found], ["ERROR"])
        self.assertTrue(all(key not in i.message for i in issues))
        token = "gh" + "p_" + "A" * 36
        self.assertTrue(any("GitHub token" in m for m in messages(self.lint(plan_text().replace("Because.", token)), "ERROR")))
        pem = "-----BEGIN " + "RSA PRIVATE KEY-----"
        self.assertTrue(any("private key" in m for m in messages(self.lint(plan_text().replace("Because.", pem)), "ERROR")))

    def test_secret_scan_covers_code_fences(self):
        key = "AKIA" + "ABCDEFGHIJKLMNOP"
        text = plan_text().replace("Because.", f"```go\nkey := \"{key}\"\n```")
        self.assertTrue(any("AWS access key ID" in m for m in messages(self.lint(text), "ERROR")))

    def test_generic_credential_assignment_only_warns(self):
        text = plan_text().replace("Because.", 'cfg.password = "correct-horse-battery"')
        issues = self.lint(text)
        self.assertEqual(messages(issues, "ERROR"), [])
        self.assertTrue(any("hardcoded credential" in m for m in messages(issues, "WARN")))
        placeholder = plan_text().replace("Because.", 'cfg.password = "<your-password-here>"')
        self.assertEqual(self.lint(placeholder), [])

    def test_bold_colon_inside_the_field_name_is_accepted(self):
        text = plan_text().replace("**Priority**: P2", "**Priority:** P2")
        self.assertEqual(self.lint(text), [])

    def test_scope_bullet_with_several_paths_counts_each_one(self):
        text = plan_text(in_scope="- `src/a.go`, `src/c.go` — both change; compare with `src/zzz.go`")
        errors = messages(self.lint(text), "ERROR")
        self.assertIn("in-scope file 'src/c.go' is not covered by the drift check", errors)
        self.assertFalse(any("zzz" in m for m in errors))
        self.assertEqual(self.lint(plan_text(in_scope="- `src/a.go`, `src/c.go`", drift="src/a.go src/c.go")), [])

    def test_code_blocks_do_not_count_toward_the_prose_limit(self):
        code = "```go\n" + "\n".join(["x := 1"] * 300) + "\n```"
        self.assertEqual(self.lint(plan_text().replace("Because.", code)), [])
        prose = self.lint(plan_text().replace("Because.", "\n".join(["line"] * 260)))
        self.assertTrue(any("lines of prose" in m for m in messages(prose, "WARN")))
        huge_code = "```go\n" + "\n".join(["x := 1"] * 520) + "\n```"
        self.assertTrue(any("lines in total" in m for m in messages(self.lint(plan_text().replace("Because.", huge_code)), "WARN")))

    def test_escaped_pipe_in_the_commands_table_warns(self):
        text = plan_text().replace("| Tests | `go test ./...` | ok |", "| Tests | `go test -run 'A\\|B'` | ok |")
        self.assertTrue(any("escaped pipe" in m for m in messages(self.lint(text), "WARN")))

    def test_oversized_plans_are_rejected_and_long_ones_warn(self):
        huge = plan_text().replace("Because.", "x" * 61_000)
        self.assertTrue(any("too large" in m for m in messages(self.lint(huge), "ERROR")))
        long = plan_text().replace("Because.", "\n".join(["line"] * 260))
        self.assertTrue(any("consider splitting" in m for m in messages(self.lint(long), "WARN")))

    def test_a_missing_status_section_reports_one_error_not_many(self):
        errors = messages(self.lint(plan_text().replace("## Status", "## Stat")), "ERROR")
        self.assertIn("missing section '## Status'", errors)
        self.assertFalse(any("Status is missing" in m for m in errors))


class LintWithGit(GitTempCase):
    TEMPLATE_FILES = {
        "src/a.go": "package a\n",
        "src/b.go": "package b\nfunc One() int {\n\treturn 1\n}\n",
    }

    def test_valid_plan_passes_the_git_checks(self):
        self.assertEqual(self.lint(plan_text(sha=self.sha), self.handle), [])

    def test_unknown_commit_is_an_error(self):
        errors = messages(self.lint(plan_text(sha="deadbeef1234"), self.handle), "ERROR")
        self.assertTrue(any("does not exist in this repository" in m for m in errors))

    def test_missing_in_scope_path_is_an_error_unless_marked_create(self):
        bad = plan_text(sha=self.sha, in_scope="- `src/a.go`\n- `src/new.go`", drift="src/a.go src/new.go")
        self.assertTrue(any("'src/new.go' does not exist" in m for m in messages(self.lint(bad, self.handle), "ERROR")))
        ok = plan_text(sha=self.sha, in_scope="- `src/a.go`\n- `src/new.go` (create)")
        self.assertEqual(self.lint(ok, self.handle), [])

    def test_create_marker_on_an_existing_file_warns(self):
        text = plan_text(sha=self.sha, in_scope="- `src/a.go` (create)")
        self.assertTrue(any("already exists" in m for m in messages(self.lint(text, self.handle), "WARN")))

    def test_commit_outside_head_history_warns(self):
        git(self.root, "checkout", "-q", "-b", "side")
        (self.root / "side.txt").write_text("x\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "side")
        side = git(self.root, "rev-parse", "--short=12", "HEAD")
        git(self.root, "checkout", "-q", "main")
        self.assertTrue(any("not an ancestor" in m for m in
                            messages(self.lint(plan_text(sha=side), self.handle), "WARN")))

    def excerpt_plan(self, header, body, sha=None):
        block = f"```go\n{header}\n{body}\n```"
        return plan_text(sha=sha or self.sha).replace("- `src/a.go` — the file.", f"- `src/a.go` — the file.\n\n{block}\n")

    def test_excerpt_matching_the_stamped_commit_passes(self):
        text = self.excerpt_plan("// src/b.go:2-3", "func One() int {\n\treturn 1")
        self.assertEqual(self.lint(text, self.handle), [])
        trailing = self.excerpt_plan("// src/b.go:2-3", "func One() int {\n\treturn 1   \n")
        self.assertEqual(self.lint(trailing, self.handle), [])
        single = self.excerpt_plan("// src/b.go:1", "package b")
        self.assertEqual(self.lint(single, self.handle), [])

    def test_excerpt_that_differs_is_an_error_naming_the_line(self):
        text = self.excerpt_plan("// src/b.go:2-3", "func One() int {\n\treturn 2")
        issues = [i for i in self.lint(text, self.handle) if "excerpt" in i.message]
        self.assertEqual(len(issues), 1)
        self.assertIn("differs from", issues[0].message)
        self.assertIn("excerpt line 2", issues[0].message)
        self.assertEqual(text.splitlines()[issues[0].line - 1], "\treturn 2")

    def test_excerpt_with_indentation_changes_or_elisions_is_an_error(self):
        spaced = self.excerpt_plan("// src/b.go:2-3", "func One() int {\n    return 1")
        self.assertTrue(any("differs from" in m for m in messages(self.lint(spaced, self.handle), "ERROR")))
        elided = self.excerpt_plan("// src/b.go:2-4", "func One() int {\n\t// ...\n}")
        self.assertTrue(any("differs from" in m for m in messages(self.lint(elided, self.handle), "ERROR")))

    def test_excerpt_range_and_path_must_exist_at_the_commit(self):
        outside = self.excerpt_plan("// src/b.go:3-40", "x")
        self.assertTrue(any("is outside 'src/b.go'" in m for m in messages(self.lint(outside, self.handle), "ERROR")))
        missing = self.excerpt_plan("// src/nope.go:1-2", "x")
        self.assertTrue(any("excerpt path 'src/nope.go' does not exist" in m for m in messages(self.lint(missing, self.handle), "ERROR")))

    def test_blocks_without_an_excerpt_header_are_ignored_and_other_comment_styles_work(self):
        plain = self.excerpt_plan("// the fix", "return 1")
        self.assertEqual(self.lint(plain, self.handle), [])
        hashed = f"```sh\n# src/b.go:1\npackage b\n```"
        text = plan_text(sha=self.sha).replace("- `src/a.go` — the file.", f"- `src/a.go` — the file.\n\n{hashed}\n")
        self.assertEqual(self.lint(text, self.handle), [])

    def test_excerpts_are_not_checked_without_git(self):
        text = self.excerpt_plan("// src/b.go:2-3", "wrong\nwrong")
        self.assertEqual(self.lint(text), [])

    def test_directory_paths_exist_as_trees(self):
        text = plan_text(sha=self.sha, in_scope="- `src/`", drift="src/")
        self.assertEqual(self.lint(text, self.handle), [])


class LintDirectory(TempCase):
    def write(self, plan_specs, index_rows, index=True):
        for number, kwargs in plan_specs.items():
            (self.root / f"{number}-fix-the-thing.md").write_text(plan_text(number=number, **kwargs))
        if index:
            (self.root / "README.md").write_text(index_text(index_rows))

    def issues(self):
        return [(p.name, i) for p, i in plans.lint_directory(self.root, None)]

    def test_consistent_directory_has_no_issues(self):
        self.write({"001": {}, "002": {"depends": "plans/001-fix-the-thing.md"}},
                   [("001", "none", "DONE"), ("002", "001", "TODO")])
        self.assertEqual(self.issues(), [])

    def test_plan_and_index_must_agree(self):
        self.write({"001": {}, "002": {}}, [("001", "none", "TODO"), ("003", "none", "TODO")])
        errors = [i.message for _, i in self.issues() if i.level == "ERROR"]
        self.assertIn("plan 002 has no row in the index", errors)
        self.assertIn("index row 003 has no plan file", errors)

    def test_missing_index_is_an_error(self):
        self.write({"001": {}}, [], index=False)
        self.assertIn("missing the index README.md", [i.message for _, i in self.issues()])

    def test_unknown_status_is_an_error_and_missing_reason_warns(self):
        self.write({"001": {}, "002": {}}, [("001", "none", "FINISHED"), ("002", "none", "BLOCKED")])
        issues = [i for _, i in self.issues()]
        self.assertTrue(any(i.level == "ERROR" and "unknown status 'FINISHED'" in i.message for i in issues))
        self.assertTrue(any(i.level == "WARN" and "BLOCKED should carry" in i.message for i in issues))
        (self.root / "002-fix-the-thing.md").unlink()
        self.write({"001": {}}, [("001", "none", "BLOCKED (needs a decision)")])
        self.assertEqual(self.issues(), [])

    def test_missing_dependency_and_cycles_are_errors(self):
        self.write({"001": {"depends": "plans/009-x.md"}}, [("001", "009", "TODO")])
        self.assertTrue(any("depends on plan 009" in i.message for _, i in self.issues()))
        (self.root / "009-x.md").unlink(missing_ok=True)
        self.write({"001": {"depends": "plans/002-a.md"}, "002": {"depends": "plans/001-a.md"}},
                   [("001", "002", "TODO"), ("002", "001", "TODO")])
        self.assertTrue(any(i.message.startswith("dependency cycle") for _, i in self.issues()))

    def test_duplicate_numbers_and_empty_directories_are_errors(self):
        self.write({"001": {}}, [("001", "none", "TODO")])
        (self.root / "001-other.md").write_text(plan_text(number="001"))
        self.assertTrue(any("used by two files" in i.message for _, i in self.issues()))
        empty = self.root / "empty"
        empty.mkdir()
        self.assertTrue(any("no plan files" in i.message for _, i in plans.lint_directory(empty, None)))

    def test_index_without_a_table_is_an_error(self):
        self.write({"001": {}}, [("001", "none", "TODO")])
        (self.root / "README.md").write_text("# Plans\n\nnothing yet\n")
        self.assertTrue(any("no status table" in i.message for _, i in self.issues()))

    def test_plan_numbers_may_be_links_or_code(self):
        self.write({"001": {}}, [])
        (self.root / "README.md").write_text(
            "| Plan | Status |\n|---|---|\n| [001](001-fix-the-thing.md) | TODO |\n| `002` | DONE |\n")
        rows, issues = plans.parse_index(self.root / "README.md")
        self.assertEqual((issues, [r.number for r in rows]), ([], ["001", "002"]))

    def test_index_columns_are_found_by_header_name(self):
        self.write({"001": {}}, [])
        (self.root / "README.md").write_text(
            "| Status | Plan | Title |\n|---|---|---|\n| DONE (merged) | 001 | Fix |\n")
        rows, issues = plans.parse_index(self.root / "README.md")
        self.assertEqual((issues, [(r.number, r.status, r.note) for r in rows]), ([], [("001", "DONE", "(merged)")]))


class Status(GitTempCase):
    def setUp(self):
        super().setUp()
        self.plans = self.root / "plans"
        self.plans.mkdir()

    def write(self, specs, rows):
        for number, kwargs in specs.items():
            (self.plans / f"{number}-fix-the-thing.md").write_text(plan_text(number=number, sha=self.sha, **kwargs))
        (self.plans / "README.md").write_text(index_text(rows))

    def entries(self):
        return {e["number"]: e for e in plans.build_status(self.plans, self.handle)}

    def test_untouched_todo_plan_is_ready(self):
        self.write({"001": {}}, [("001", "none", "TODO")])
        entry = self.entries()["001"]
        self.assertEqual((entry["ready"], entry["drift"], entry["stale"]), (True, [], False))

    def test_drift_lists_changed_in_scope_files_and_blocks_readiness(self):
        self.write({"001": {}}, [("001", "none", "TODO")])
        (self.root / "src" / "a.go").write_text("package a\n// changed\n")
        git(self.root, "commit", "-q", "-am", "change")
        entry = self.entries()["001"]
        self.assertEqual((entry["ready"], entry["drift"]), (False, ["src/a.go"]))
        self.assertIn("drift: src/a.go", plans.describe(entry))

    def test_unrelated_changes_are_not_drift(self):
        self.write({"001": {}}, [("001", "none", "TODO")])
        (self.root / "other.txt").write_text("x\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "other")
        self.assertEqual(self.entries()["001"]["drift"], [])

    def test_unknown_planned_commit_is_stale(self):
        (self.plans / "001-fix-the-thing.md").write_text(plan_text(sha="deadbeef1234"))
        (self.plans / "README.md").write_text(index_text([("001", "none", "TODO")]))
        entry = self.entries()["001"]
        self.assertEqual((entry["stale"], entry["ready"]), (True, False))

    def test_dependency_needs_done_and_merged(self):
        self.write({"001": {}, "002": {"depends": "plans/001-fix-the-thing.md"}},
                   [("001", "none", "DONE"), ("002", "001", "TODO")])
        git(self.root, "checkout", "-q", "-b", "advisor/001-fix-the-thing")
        (self.root / "src" / "a.go").write_text("package a\n// fixed\n")
        git(self.root, "commit", "-q", "-am", "fix")
        git(self.root, "checkout", "-q", "main")
        first, second = self.entries()["001"], self.entries()["002"]
        self.assertEqual(first["branch_state"], "unmerged")
        self.assertIn("awaiting merge", plans.describe(first))
        self.assertEqual((second["waiting_on"], second["ready"]), (["001"], False))
        git(self.root, "merge", "-q", "--ff-only", "advisor/001-fix-the-thing")
        entries = self.entries()
        self.assertEqual(entries["001"]["branch_state"], "merged")
        self.assertEqual(entries["002"]["waiting_on"], [])

    def test_squash_merged_branch_counts_as_merged_but_unrelated_branch_does_not(self):
        self.write({"001": {}, "002": {"depends": "plans/001-fix-the-thing.md"}},
                   [("001", "none", "DONE"), ("002", "001", "TODO")])
        git(self.root, "checkout", "-q", "-b", "advisor/001-fix-the-thing")
        (self.root / "src" / "a.go").write_text("package a\n// fixed\n")
        git(self.root, "commit", "-q", "-am", "fix")
        git(self.root, "checkout", "-q", "main")
        self.assertEqual(self.entries()["001"]["branch_state"], "unmerged")
        git(self.root, "merge", "-q", "--squash", "advisor/001-fix-the-thing")
        git(self.root, "commit", "-q", "-m", "squash")
        entries = self.entries()
        self.assertEqual(entries["001"]["branch_state"], "merged")
        self.assertEqual(entries["002"]["waiting_on"], [])
        # A branch that never touched the plan's files must not look merged just because they match HEAD.
        git(self.root, "checkout", "-q", "-b", "advisor/elsewhere", "main~1")
        (self.root / "docs.txt").write_text("x\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "docs")
        git(self.root, "checkout", "-q", "main")
        self.assertEqual(self.handle.branch_state("advisor/elsewhere", ["src/a.go"]), "unmerged")

    def test_dependency_on_a_todo_plan_waits(self):
        self.write({"001": {}, "002": {"depends": "plans/001-fix-the-thing.md"}},
                   [("001", "none", "TODO"), ("002", "001", "TODO")])
        entries = self.entries()
        self.assertEqual((entries["001"]["ready"], entries["002"]["ready"]), (True, False))
        self.assertEqual(entries["002"]["waiting_on"], ["001"])

    def test_external_dependencies_are_reported_not_resolved(self):
        self.write({"001": {"depends": "sphere/plans/003-fix-x.md"}}, [("001", "sphere/plans/003", "TODO")])
        entry = self.entries()["001"]
        self.assertEqual(entry["external_depends"], ["sphere/plans/003"])
        self.assertTrue(entry["ready"])

    def test_listed_plan_without_a_file_is_flagged(self):
        self.write({"001": {}}, [("001", "none", "TODO"), ("002", "none", "TODO")])
        self.assertEqual(self.entries()["002"]["status"], "TODO (no file)")

    def test_command_prints_a_table_and_json(self):
        self.write({"001": {}}, [("001", "none", "TODO")])
        out = io.StringIO()
        with redirect_stdout(out):
            code = plans.main(["status", str(self.plans)])
        self.assertEqual(code, 0)
        self.assertIn("Executable now: 001", out.getvalue())
        out = io.StringIO()
        with redirect_stdout(out):
            plans.main(["status", str(self.plans), "--json"])
        self.assertEqual(json.loads(out.getvalue())[0]["number"], "001")

    def test_status_outside_a_repository_exits_2(self):
        with tempfile.TemporaryDirectory() as bare:
            code = plans.main(["status", bare])
        self.assertEqual(code, 2)


class Scope(GitTempCase):
    TEMPLATE_FILES = {
        "src/a.go": "package a\n",
        "src/b.go": "package b\n",
    }
    TEMPLATE_DIRS = ("gen/v1",)

    def setUp(self):
        super().setUp()
        self.base = self.sha
        text = plan_text(sha=self.base, in_scope="- `src/a.go`\n- `src/new_test.go` (create)",
                         drift="src/a.go src/new_test.go")
        text = text.replace("**Out of scope**", "**Regenerated** (never hand-edit):\n- `gen/**/*.pb.go`\n\n**Out of scope**")
        # The plan lives outside the worktree, as the real one does.
        plan_dir = tempfile.TemporaryDirectory()
        self.addCleanup(plan_dir.cleanup)
        self.plan = Path(plan_dir.name) / "001-fix-the-thing.md"
        self.plan.write_text(text)

    def scope(self, *extra):
        out = io.StringIO()
        with redirect_stdout(out):
            code = plans.main(["scope", str(self.plan), "--worktree", str(self.root), *extra])
        return code, out.getvalue()

    def commit(self, files):
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "work")

    def test_changes_inside_in_scope_and_regenerated_paths_pass(self):
        self.commit({"src/a.go": "package a\n// fix\n", "src/new_test.go": "package a\n", "gen/v1/x.pb.go": "x\n"})
        code, out = self.scope()
        self.assertEqual(code, 0, out)
        self.assertIn("ok           src/a.go (committed)", out)
        self.assertIn("ok           gen/v1/x.pb.go (committed)", out)
        self.assertIn("0 out-of-scope file(s), 0 uncommitted file(s)", out)

    def test_files_outside_scope_fail_whether_committed_or_not(self):
        self.commit({"src/a.go": "package a\n// fix\n", "src/b.go": "package b\n// sneaky\n"})
        (self.root / "src" / "extra.go").write_text("package a\n")
        code, out = self.scope("--base", self.base)
        self.assertEqual(code, 1)
        self.assertIn("OUT OF SCOPE src/b.go (committed)", out)
        self.assertIn("OUT OF SCOPE src/extra.go (uncommitted)", out)
        self.assertIn("2 out-of-scope file(s), 1 uncommitted file(s)", out)

    def test_regenerated_glob_does_not_cover_other_files_in_the_directory(self):
        self.commit({"src/a.go": "package a\n// fix\n", "gen/v1/x.go": "not generated by the plan\n"})
        code, out = self.scope()
        self.assertEqual(code, 1)
        self.assertIn("OUT OF SCOPE gen/v1/x.go", out)

    def test_in_scope_files_that_never_changed_are_reported(self):
        self.commit({"src/a.go": "package a\n// fix\n"})
        _, out = self.scope()
        self.assertIn("not changed  src/new_test.go (create): the file was never created", out)

    def test_uncommitted_edits_to_tracked_files_are_listed(self):
        self.commit({"src/a.go": "package a\n// fix\n"})
        (self.root / "src" / "a.go").write_text("package a\n// more\n")
        code, out = self.scope()
        self.assertEqual(code, 0)
        self.assertIn("src/a.go (uncommitted)", out)
        self.assertIn("1 uncommitted file(s)", out)

    def test_unknown_base_or_plan_exits_2(self):
        self.assertEqual(self.scope("--base", "deadbeef1234")[0], 2)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(plans.main(["scope", str(self.root / "nope.md"), "--worktree", str(self.root)]), 2)

    def test_glob_translation(self):
        match = lambda pattern, path: bool(plans.glob_regex(pattern).match(path))
        self.assertTrue(match("api/**/*.pb.go", "api/v1/x.pb.go"))
        self.assertTrue(match("api/**/*.pb.go", "api/x.pb.go"))
        self.assertFalse(match("api/**/*.pb.go", "api/v1/x.go"))
        self.assertTrue(match("gen/**", "gen/a/b/c.go"))
        self.assertFalse(match("gen/*", "gen/a/b.go"))
        self.assertTrue(match("docs/?.md", "docs/a.md"))
        self.assertFalse(match("docs/?.md", "docs/ab.md"))
        self.assertTrue(plans.in_paths("src/pkg/a.go", ["src/pkg"]))
        self.assertFalse(plans.in_paths("src/pkgx/a.go", ["src/pkg"]))


class Cli(TempCase):
    def run_main(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = plans.main(list(argv))
        return code, out.getvalue()

    def test_lint_exit_codes_and_summary(self):
        good = self.root / "001-fix-the-thing.md"
        good.write_text(plan_text())
        code, out = self.run_main("lint", str(good), "--no-git")
        self.assertEqual((code, out.strip()), (0, "0 error(s), 0 warning(s)"))
        good.write_text(plan_text().replace("## Report back", "## Other"))
        code, out = self.run_main("lint", str(good), "--no-git")
        self.assertEqual(code, 1)
        self.assertIn("ERROR: missing section '## Report back'", out)

    def test_missing_path_exits_2(self):
        self.assertEqual(self.run_main("lint", str(self.root / "nope.md"), "--no-git")[0], 2)

    def test_lint_outside_a_repository_warns_and_skips_git_checks(self):
        path = self.root / "001-fix-the-thing.md"
        path.write_text(plan_text())
        code, out = self.run_main("lint", str(path))
        self.assertEqual(code, 0)
        self.assertIn("not a git repository", out)


class ShippedExamples(unittest.TestCase):
    def test_every_example_plan_passes_lint_without_warnings(self):
        examples = sorted((SKILL / "references").glob("plan-example*.md"))
        self.assertEqual([p.name for p in examples], ["plan-example-tests.md", "plan-example.md"])
        for example in examples:
            out = io.StringIO()
            with redirect_stdout(out):
                code = plans.main(["lint", str(example), "--no-git"])
            self.assertEqual((code, out.getvalue().strip()), (0, "0 error(s), 0 warning(s)"), example.name)


if __name__ == "__main__":
    unittest.main(verbosity=1)
