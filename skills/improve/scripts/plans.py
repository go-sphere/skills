#!/usr/bin/env python3
"""Lint and track the plan files the improve skill writes.

    plans.py lint [PATH ...] [--no-git] [--root DIR]
    plans.py status [DIR] [--json] [--root DIR]
    plans.py scope PLAN --worktree DIR [--base SHA]

A PATH is a plan file or a plans directory. `lint` exits 1 when it reports an
ERROR; warnings never fail it, and it never prints a matched secret. `status`
reads git history to show drift, merge state, and readiness for every plan in
the index. `scope` lists the files an executor changed in a worktree and exits 1 when any
lies outside the plan's In scope and Regenerated paths. Standard library only. `lint --no-git`
skips every check that needs a repository; `status` and `scope` always need one.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Template order. Only the toolkit section may be absent.
ORDER = (
    "Status", "Why this matters", "Current state", "Commands you will need",
    "Suggested executor toolkit", "Scope", "Git workflow", "Steps", "Test plan",
    "Done criteria", "STOP conditions", "Report back", "Maintenance notes",
)
OPTIONAL_SECTIONS = {"Suggested executor toolkit"}
REQUIRED_FIELDS = ("Priority", "Effort", "Risk", "Depends on", "Category", "Finding", "Planned at")
CHOICES = {
    "Priority": {"P1", "P2", "P3"},
    "Effort": {"S", "M", "L"},
    "Risk": {"LOW", "MED", "HIGH"},
    "Category": {"bug", "security", "perf", "tests", "tech-debt", "migration", "dx", "docs", "direction"},
}
STATUSES = ("TODO", "IN PROGRESS", "DONE", "BLOCKED", "REJECTED")
# GitHub rejects an issue body over 65,536 characters; keep headroom.
MAX_CHARS = 60_000
# Prose lines exclude fenced code: verbatim code is content the executor needs.
WARN_PROSE_LINES = 250
WARN_TOTAL_LINES = 500
PLAN_DIRS = ("plans", "advisor-plans")

# Formats with a fixed shape are errors. The generic assignment pattern also matches
# placeholders, so it only warns.
SECRET_PATTERNS = (
    ("AWS access key ID", "ERROR", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", "ERROR", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("GitHub fine-grained token", "ERROR", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("Slack token", "ERROR", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe live key", "ERROR", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{16,}\b")),
    ("Google API key", "ERROR", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("API secret key", "ERROR", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("private key block", "ERROR", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("JWT", "ERROR", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ("hardcoded credential", "WARN",
     re.compile(r"""(?i)\b(?:password|passwd|secret|token|api[_-]?key)\b\s*[:=]\s*["'][^"'\s<{$]{12,}["']""")),
)

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FIELD = re.compile(r"^\s*[-*]\s+\*\*([^*:]+?):?\*\*:?\s*(.*?)\s*$")
BULLET = re.compile(r"^\s*[-*]\s+\S")
BULLET_TEXT = re.compile(r"^\s*[-*]\s+(.*)$")
PATH_TOKEN = re.compile(r"`([^`\s]+)`(\s*\(create\))?", re.IGNORECASE)
# A spaced dash separates the paths of a scope bullet from its description.
DESCRIPTION_DASH = re.compile(r"\s[\u2014\u2013-]\s")
EXCERPT_HEADER = re.compile(
    r"^\s*(?://|#|--|;|/\*|<!--)\s*([\w./@+~-]+):(\d+)(?:-(\d+))?\s*(?:\*/|-->)?\s*$")
CHECKBOX = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+(.*)$")
VERIFY = re.compile(r"\*\*Verify(?::\*\*|\*\*:)")
PLAN_FILE = re.compile(r"^(\d{3,})-[A-Za-z0-9][\w.-]*\.md$")
PLANNED_AT = re.compile(r"commit\s+`?([0-9a-f]{7,40})`?\s*,\s*(\d{4}-\d{2}-\d{2})")
DRIFT = re.compile(r"git diff --stat ([0-9a-f]{7,40})\.\.HEAD -- ([^`]+)")
DEPENDENCY = re.compile(r"((?:[\w.-]+/)*)(\d{3,})-[\w.-]+\.md")
GLOB_CHARS = set("*?[")


@dataclass(frozen=True)
class Issue:
    level: str  # "ERROR" or "WARN"
    message: str
    line: int = 0  # 1-based; 0 when the problem is not tied to one line


@dataclass
class Plan:
    path: Path
    lines: list[str]
    heads: list[tuple[int, str, int]]
    number: str | None = None
    title: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    field_lines: dict[str, int] = field(default_factory=dict)
    sha: str | None = None
    depends: list[str] = field(default_factory=list)
    external_depends: list[str] = field(default_factory=list)
    drift_sha: str | None = None
    drift_paths: list[str] = field(default_factory=list)
    in_scope: list[tuple[str, bool]] = field(default_factory=list)
    regenerated: list[str] = field(default_factory=list)
    has_scope_labels: dict[str, bool] = field(default_factory=dict)
    out_of_scope_count: int = 0
    branch: str | None = None


@dataclass
class Row:
    number: str
    title: str
    status: str
    note: str
    depends: str
    line: int


# ---------------------------------------------------------------- markdown helpers


def outside_fences(lines: list[str]):
    """Yield (index, line) for every line that is not part of a fenced code block."""
    marker = None
    for i, line in enumerate(lines):
        match = FENCE.match(line)
        if match:
            fence = match.group(1)
            if marker is None:
                marker = fence
            elif fence[0] == marker[0] and len(fence) >= len(marker) and not line.strip().strip(fence[0]):
                marker = None
            continue
        if marker is None:
            yield i, line


def fenced_blocks(lines: list[str]):
    """Yield (fence_index, body) for each fenced code block; body holds the lines between the fences."""
    marker = None
    start = 0
    body: list[str] = []
    for i, line in enumerate(lines):
        match = FENCE.match(line)
        if match:
            fence = match.group(1)
            if marker is None:
                marker, start, body = fence, i, []
                continue
            if fence[0] == marker[0] and len(fence) >= len(marker) and not line.strip().strip(fence[0]):
                yield start, body
                marker = None
                continue
        if marker is not None:
            body.append(line)


def find_headings(lines: list[str]) -> list[tuple[int, str, int]]:
    found = []
    for i, line in outside_fences(lines):
        match = HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2), i))
    return found


def section_bounds(lines, heads, name, level=2):
    """Return (start, end) line indexes of the body under heading `name`, or None."""
    for n, (lvl, text, idx) in enumerate(heads):
        if lvl == level and text == name:
            end = len(lines)
            for lvl2, _, idx2 in heads[n + 1:]:
                if lvl2 <= level:
                    end = idx2
                    break
            return idx + 1, end
    return None


def body_lines(plan: Plan, name: str):
    """Yield (index, line) for the non-fenced lines under the `## name` heading."""
    bounds = section_bounds(plan.lines, plan.heads, name)
    if not bounds:
        return
    for i, line in outside_fences(plan.lines):
        if bounds[0] <= i < bounds[1]:
            yield i, line


# ---------------------------------------------------------------- plan parsing


def normalize_path(path: str) -> str:
    path = path.strip()
    while path.startswith("./"):
        path = path[2:]
    return path.rstrip("/")


def covers(parent: str, child: str) -> bool:
    return child == parent or child.startswith(parent + "/")


def parse_dependencies(value: str) -> tuple[list[str], list[str]]:
    """Split a `Depends on` value into local plan numbers and external plan references."""
    if value.strip().lower() in ("", "none", "-", "—"):
        return [], []
    local, external = [], []
    for prefix, number in DEPENDENCY.findall(value):
        parts = [p for p in prefix.split("/") if p and p != "."]
        if len(parts) <= 1:
            local.append(number)
        else:
            external.append(f"{prefix}{number}")
    if not local and not external:
        local = re.findall(r"\b\d{3,}\b", value)
    return local, external


def bullet_paths(line: str) -> list[tuple[str, bool]] | None:
    """Return the (path, is_create) pairs a scope bullet names before its description.

    Returns None when the line is not a bullet. A lone path may carry "(create)" anywhere in
    the bullet; with several paths, only a marker right after a path applies to it.
    """
    match = BULLET_TEXT.match(line)
    if not match:
        return None
    text = match.group(1)
    tokens = list(PATH_TOKEN.finditer(DESCRIPTION_DASH.split(text, maxsplit=1)[0]))
    if len(tokens) == 1:
        return [(tokens[0].group(1), "(create)" in text.lower())]
    return [(token.group(1), bool(token.group(2))) for token in tokens]


def parse_scope(plan: Plan) -> None:
    buckets: dict[str, list[tuple[str, bool]]] = {"in": [], "regen": [], "out": []}
    current = None
    for _, line in body_lines(plan, "Scope"):
        label = line.strip().lower()
        for key, prefix in (("in", "**in scope"), ("regen", "**regenerated"), ("out", "**out of scope")):
            if label.startswith(prefix):
                current = key
                plan.has_scope_labels[key] = True
                break
        else:
            paths = bullet_paths(line)
            if paths is None or current is None:
                continue
            buckets[current] += paths or ([("", False)] if current == "out" else [])
    plan.in_scope = buckets["in"]
    plan.regenerated = [normalize_path(path) for path, _ in buckets["regen"] if path]
    plan.out_of_scope_count = len(buckets["out"])


def parse_plan(path: Path) -> Plan:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    plan = Plan(path=path, lines=lines, heads=find_headings(lines))
    for level, heading, _ in plan.heads:
        match = re.match(r"^Plan (\d+):\s*(\S.*)$", heading)
        if level == 1 and match:
            plan.number, plan.title = match.group(1), match.group(2)
            break
    for i, line in body_lines(plan, "Status"):
        match = FIELD.match(line)
        if match:
            name = match.group(1).strip()
            plan.fields.setdefault(name, match.group(2))
            plan.field_lines.setdefault(name, i + 1)
    planned = PLANNED_AT.search(plan.fields.get("Planned at", ""))
    plan.sha = planned.group(1) if planned else None
    plan.depends, plan.external_depends = parse_dependencies(plan.fields.get("Depends on", ""))
    status_heading = next((idx for lvl, text_, idx in plan.heads if lvl == 2 and text_ == "Status"), None)
    if status_heading is not None:
        header = " ".join(re.sub(r"^\s*>\s?", "", line) for line in lines[:status_heading])
        drift = DRIFT.search(header)
        if drift:
            plan.drift_sha = drift.group(1)
            try:
                plan.drift_paths = [normalize_path(p) for p in shlex.split(drift.group(2))]
            except ValueError:
                plan.drift_paths = [normalize_path(p) for p in drift.group(2).split()]
    parse_scope(plan)
    for _, line in body_lines(plan, "Git workflow"):
        match = re.search(r"Branch:\s*`([^`<>]+)`", line)
        if match:
            plan.branch = match.group(1)
            break
    return plan


# ---------------------------------------------------------------- git


class Git:
    def __init__(self, root: Path):
        self.root = root

    @classmethod
    def open(cls, start: Path) -> "Git | None":
        try:
            proc = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True, check=False)
        except OSError:
            return None
        return cls(Path(proc.stdout.strip())) if proc.returncode == 0 and proc.stdout.strip() else None

    def run(self, *args: str) -> tuple[int, str]:
        proc = subprocess.run(["git", "-c", "core.quotepath=false", "-C", str(self.root), *args],
                              capture_output=True, text=True, check=False)
        return proc.returncode, proc.stdout.strip()

    def show(self, sha: str, path: str) -> str | None:
        """Return the file's exact content at `sha`, or None when it does not exist there."""
        proc = subprocess.run(["git", "-C", str(self.root), "show", f"{sha}:{path}"],
                              capture_output=True, text=True, errors="replace", check=False)
        return proc.stdout if proc.returncode == 0 else None

    def commit_exists(self, sha: str) -> bool:
        return self.run("cat-file", "-e", f"{sha}^{{commit}}")[0] == 0

    def is_ancestor(self, ancestor: str, descendant: str = "HEAD") -> bool:
        return self.run("merge-base", "--is-ancestor", ancestor, descendant)[0] == 0

    def exists_at(self, sha: str, path: str) -> bool:
        return self.run("cat-file", "-e", f"{sha}:{path}")[0] == 0

    def changed_since(self, sha: str, paths: list[str]) -> list[str]:
        code, out = self.run("diff", "--name-only", f"{sha}..HEAD", "--", *paths)
        return out.splitlines() if code == 0 else []

    def head(self) -> str:
        return self.run("rev-parse", "--short=12", "HEAD")[1]

    def current_branch(self) -> str:
        return self.run("branch", "--show-current")[1]

    def branch_state(self, name: str, paths: list[str] | None = None) -> str:
        """Return "missing", "merged", or "unmerged" for a local branch relative to HEAD.

        A squash or rebase merge leaves the branch commits outside HEAD's history. The branch
        also counts as merged when it has commits touching `paths` and HEAD holds identical
        content there.
        """
        ref = f"refs/heads/{name}"
        if self.run("rev-parse", "--verify", "--quiet", ref)[0] != 0:
            return "missing"
        if self.is_ancestor(ref):
            return "merged"
        if paths:
            touched = self.run("log", "--oneline", f"HEAD..{ref}", "--", *paths)[1]
            identical = self.run("diff", "--quiet", ref, "HEAD", "--", *paths)[0] == 0
            if touched and identical:
                return "merged"
        return "unmerged"


# ---------------------------------------------------------------- lint


def check_structure(plan: Plan) -> list[Issue]:
    issues = []
    if plan.number is None:
        issues.append(Issue("ERROR", "missing the '# Plan NNN: <title>' heading"))
    else:
        match = PLAN_FILE.match(plan.path.name)
        if match and int(match.group(1)) != int(plan.number):
            issues.append(Issue("ERROR", f"file name number {match.group(1)} does not match 'Plan {plan.number}'"))
    positions = {}
    for level, heading, idx in plan.heads:
        if level == 2 and heading in ORDER:
            positions.setdefault(heading, idx)
    for name in ORDER:
        if name not in positions and name not in OPTIONAL_SECTIONS:
            issues.append(Issue("ERROR", f"missing section '## {name}'"))
    present = [name for name in ORDER if name in positions]
    if sorted(present, key=lambda name: positions[name]) != present:
        issues.append(Issue("WARN", "sections are out of template order"))
    return issues


def check_status(plan: Plan) -> list[Issue]:
    if not any(level == 2 and heading == "Status" for level, heading, _ in plan.heads):
        return []  # check_structure already reports the missing section
    issues = []
    for name in REQUIRED_FIELDS:
        value = plan.fields.get(name)
        if value is None:
            issues.append(Issue("ERROR", f"Status is missing the '{name}' field"))
        elif name in CHOICES and value not in CHOICES[name]:
            issues.append(Issue("ERROR", f"'{name}' must be one of {', '.join(sorted(CHOICES[name]))}; found '{value}'",
                                plan.field_lines[name]))
    if "Planned at" in plan.fields and plan.sha is None:
        issues.append(Issue("ERROR", "'Planned at' must read: commit `<sha>`, YYYY-MM-DD", plan.field_lines["Planned at"]))
    depends = plan.fields.get("Depends on", "none")
    if not plan.depends and not plan.external_depends and depends.strip().lower() not in ("none", "-", "—"):
        issues.append(Issue("ERROR", "'Depends on' must be 'none' or list plans/NNN-<slug>.md files", plan.field_lines["Depends on"]))
    key = plan.fields.get("Finding", "").strip("` ")
    if key and not key.startswith("<"):
        parts = key.split(":", 2)
        if len(parts) < 3 or not all(parts):
            issues.append(Issue("WARN", "'Finding' should be a key of the form category:path:symbol", plan.field_lines["Finding"]))
        elif parts[0] != plan.fields.get("Category"):
            issues.append(Issue("WARN", "'Finding' key category differs from the 'Category' field", plan.field_lines["Finding"]))
    return issues


def check_drift_and_scope(plan: Plan) -> list[Issue]:
    issues = []
    if plan.drift_sha is None:
        issues.append(Issue("ERROR", "missing the drift-check line: `git diff --stat <sha>..HEAD -- <paths>`"))
    elif plan.sha and not (plan.drift_sha.startswith(plan.sha) or plan.sha.startswith(plan.drift_sha)):
        issues.append(Issue("ERROR", "the drift check and 'Planned at' name different commits"))
    elif not plan.drift_paths:
        issues.append(Issue("ERROR", "the drift check lists no paths"))
    if not plan.has_scope_labels.get("in"):
        issues.append(Issue("ERROR", "Scope is missing the '**In scope**' block"))
    elif not plan.in_scope:
        issues.append(Issue("ERROR", "'**In scope**' lists no files; put each path in backticks as a bullet"))
    if not plan.has_scope_labels.get("out"):
        issues.append(Issue("ERROR", "Scope is missing the '**Out of scope**' block"))
    elif not plan.out_of_scope_count:
        issues.append(Issue("WARN", "'**Out of scope**' lists nothing; name what looks related but must not change"))
    existing = [normalize_path(p) for p, create in plan.in_scope if not create and not (GLOB_CHARS & set(p))]
    if plan.drift_paths:
        for path in existing:
            if not any(covers(d, path) for d in plan.drift_paths):
                issues.append(Issue("ERROR", f"in-scope file '{path}' is not covered by the drift check"))
        scope_all = [normalize_path(p) for p, _ in plan.in_scope]
        for d in plan.drift_paths:
            if scope_all and not any(covers(d, s) or covers(s, d) for s in scope_all):
                issues.append(Issue("WARN", f"the drift check watches '{d}', which is not in scope"))
    return issues


def check_steps(plan: Plan) -> list[Issue]:
    bounds = section_bounds(plan.lines, plan.heads, "Steps")
    if not bounds:
        return []
    steps = []
    for level, heading, idx in plan.heads:
        match = re.match(r"^Step (\d+):\s*\S", heading)
        if level == 3 and match and bounds[0] <= idx < bounds[1]:
            steps.append((int(match.group(1)), idx))
    if not steps:
        return [Issue("ERROR", "Steps has no '### Step N: <title>' headings")]
    issues = []
    if [number for number, _ in steps] != list(range(1, len(steps) + 1)):
        issues.append(Issue("ERROR", "steps must be numbered 1, 2, 3 in order", steps[0][1] + 1))
    ends = [idx for _, idx in steps[1:]] + [bounds[1]]
    for (number, start), end in zip(steps, ends):
        verify = [(i, line) for i, line in outside_fences(plan.lines) if start < i < end and VERIFY.search(line)]
        if not verify:
            issues.append(Issue("ERROR", f"step {number} has no '**Verify**:' line", start + 1))
        elif "`" not in verify[0][1]:
            issues.append(Issue("WARN", f"step {number} verification has no command in backticks", verify[0][0] + 1))
    if plan.fields.get("Category") in ("bug", "security"):
        # The Verify line names a test command in every plan, so it says nothing about step 1's intent.
        first = [line for line in plan.lines[steps[0][1]:ends[0]] if not VERIFY.search(line)]
        if "test" not in " ".join(first).lower():
            issues.append(Issue("WARN", "a bug or security plan should start with a failing regression test", steps[0][1] + 1))
    return issues


def check_done_and_stop(plan: Plan) -> list[Issue]:
    issues = []
    criteria = [(i, m.group(1)) for i, line in body_lines(plan, "Done criteria") if (m := CHECKBOX.match(line))]
    if not criteria:
        issues.append(Issue("ERROR", "Done criteria has no '- [ ]' checkboxes"))
    for i, text in criteria:
        if "`" not in text:
            issues.append(Issue("WARN", "a done criterion without a command is not machine-checkable", i + 1))
    stops = [i for i, line in body_lines(plan, "STOP conditions") if BULLET.match(line)]
    if not stops:
        issues.append(Issue("ERROR", "STOP conditions lists nothing"))
    elif len(stops) < 2:
        issues.append(Issue("WARN", "STOP conditions has one entry; name each real risk of this plan"))
    return issues


def check_secrets_and_size(plan: Plan) -> list[Issue]:
    issues = []
    for number, line in enumerate(plan.lines, start=1):
        for label, level, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                issues.append(Issue(level, f"possible {label}; name the location and credential type instead", number))
                break
    chars = sum(len(line) + 1 for line in plan.lines)
    prose = sum(1 for _ in outside_fences(plan.lines))
    if chars > MAX_CHARS:
        issues.append(Issue("ERROR", f"{chars} characters is too large for an issue body and a weak executor; split the plan"))
    elif prose > WARN_PROSE_LINES:
        issues.append(Issue("WARN", f"{prose} lines of prose (code blocks excluded); one plan should fit one reviewable pull request, so consider splitting"))
    elif len(plan.lines) > WARN_TOTAL_LINES:
        issues.append(Issue("WARN", f"{len(plan.lines)} lines in total; one plan should fit one reviewable pull request, so consider splitting"))
    return issues


def check_command_table(plan: Plan) -> list[Issue]:
    # A pipe escaped for a table cell becomes a literal backslash-pipe when the command is pasted into a shell.
    return [Issue("WARN", "an escaped pipe in a table cell breaks when pasted into a shell; move that command out of the table", i + 1)
            for i, line in body_lines(plan, "Commands you will need") if "\\|" in line]


def check_git(plan: Plan, git: Git) -> list[Issue]:
    issues = []
    if plan.sha is None:
        return issues
    if not git.commit_exists(plan.sha):
        return [Issue("ERROR", f"'Planned at' commit {plan.sha} does not exist in this repository")]
    if not git.is_ancestor(plan.sha):
        issues.append(Issue("WARN", f"commit {plan.sha} is not an ancestor of HEAD; was history rewritten?"))
    for path, create in plan.in_scope:
        path = normalize_path(path)
        if GLOB_CHARS & set(path):
            continue
        exists = git.exists_at(plan.sha, path)
        if create and exists:
            issues.append(Issue("WARN", f"'{path}' is marked (create) but already exists at {plan.sha}"))
        elif not create and not exists:
            issues.append(Issue("ERROR", f"in-scope path '{path}' does not exist at {plan.sha}; mark new files '(create)'"))
    return issues


def check_excerpts(plan: Plan, git: Git) -> list[Issue]:
    """Compare every excerpt headed `// path:start-end` with the file at the stamped commit."""
    issues = []
    if plan.sha is None or not git.commit_exists(plan.sha):
        return issues
    for fence, body in fenced_blocks(plan.lines):
        header = EXCERPT_HEADER.match(body[0]) if body else None
        if not header:
            continue
        path, first = header.group(1), int(header.group(2))
        last = int(header.group(3) or first)
        header_line = fence + 2  # 1-based number of the line after the opening fence
        source = git.show(plan.sha, path)
        if source is None:
            issues.append(Issue("ERROR", f"excerpt path '{path}' does not exist at {plan.sha}", header_line))
            continue
        source_lines = source.splitlines()
        if not 1 <= first <= last <= len(source_lines):
            issues.append(Issue("ERROR", f"excerpt range {first}-{last} is outside '{path}' ({len(source_lines)} lines) at {plan.sha}", header_line))
            continue
        expected = [line.rstrip() for line in source_lines[first - 1:last]]
        actual = [line.rstrip() for line in body[1:]]
        for side in (expected, actual):
            while side and not side[-1]:
                side.pop()
        if actual != expected:
            at = next((n for n, (a, e) in enumerate(zip(actual, expected)) if a != e), min(len(actual), len(expected)))
            issues.append(Issue("ERROR", f"excerpt of {path}:{first}-{last} differs from {plan.sha} at excerpt line {at + 1}; copy the lines exactly",
                                header_line + 1 + at))
    return issues


def lint_plan(plan: Plan, git: Git | None) -> list[Issue]:
    issues = check_structure(plan) + check_status(plan) + check_drift_and_scope(plan)
    issues += check_steps(plan) + check_done_and_stop(plan) + check_command_table(plan)
    issues += check_secrets_and_size(plan)
    if git is not None:
        issues += check_git(plan, git) + check_excerpts(plan, git)
    return issues


# ---------------------------------------------------------------- index


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_status(cell: str) -> tuple[str | None, str]:
    match = re.match(r"^(TODO|IN PROGRESS|DONE|BLOCKED|REJECTED)\b\s*(.*)$", cell.strip().strip("*`"), re.IGNORECASE)
    if not match:
        return None, cell.strip()
    return match.group(1).upper(), match.group(2).strip()


def cell_at(cells: list[str], column: int | None) -> str:
    return cells[column] if column is not None and column < len(cells) else ""


def parse_index(path: Path) -> tuple[list[Row], list[Issue]]:
    """Read the first table with Plan and Status columns. A row with an unknown status keeps the raw cell and gets an ERROR."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = header = None
    for n, line in enumerate(lines):
        if line.lstrip().startswith("|"):
            lowered = [cell.lower() for cell in split_row(line)]
            if "plan" in lowered and "status" in lowered:
                start, header = n, lowered
                break
    if start is None or header is None:
        return [], [Issue("ERROR", "no status table with 'Plan' and 'Status' columns")]
    plan_col, status_col = header.index("plan"), header.index("status")
    title_col = header.index("title") if "title" in header else None
    depends_col = next((n for n, name in enumerate(header) if name.startswith("depends")), None)
    rows, issues = [], []
    for i in range(start + 1, len(lines)):
        if not lines[i].lstrip().startswith("|"):
            break
        cells = split_row(lines[i])
        if set("".join(cells)) <= set("-: "):
            continue
        number = re.match(r"^[\[`*\s]*(\d{3,})", cell_at(cells, plan_col))
        if not number:
            issues.append(Issue("ERROR", "index row does not start with a plan number", i + 1))
            continue
        raw = cell_at(cells, status_col)
        word, note = parse_status(raw)
        if word is None:
            issues.append(Issue("ERROR", f"unknown status '{raw}'; use {', '.join(STATUSES)}", i + 1))
            word, note = raw, ""
        elif word in ("BLOCKED", "REJECTED") and not note:
            issues.append(Issue("WARN", f"{word} should carry a one-line reason in parentheses", i + 1))
        rows.append(Row(number.group(1), cell_at(cells, title_col), word, note, cell_at(cells, depends_col), i + 1))
    return rows, issues


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if nxt in graph and state.get(nxt) is None:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node) is None:
            found = visit(node)
            if found:
                return found
    return None


def plan_files(directory: Path) -> list[tuple[str, Path]]:
    """Return (number, path) for every NNN-<slug>.md file, sorted by file name."""
    found = []
    for path in sorted(directory.iterdir()):
        match = PLAN_FILE.match(path.name)
        if match and path.is_file():
            found.append((match.group(1), path))
    return found


def lint_directory(directory: Path, git: Git | None) -> list[tuple[Path, Issue]]:
    found: list[tuple[Path, Issue]] = []
    files = plan_files(directory)
    plans: dict[str, Plan] = {}
    for number, path in files:
        plan = parse_plan(path)
        found += [(path, issue) for issue in lint_plan(plan, git)]
        if number in plans:
            found.append((path, Issue("ERROR", f"plan number {number} is used by two files")))
        plans[number] = plan
    index = directory / "README.md"
    if not files:
        found.append((directory, Issue("ERROR", "no plan files named NNN-<slug>.md")))
        return found
    if not index.is_file():
        found.append((directory, Issue("ERROR", "missing the index README.md")))
    else:
        rows, issues = parse_index(index)
        found += [(index, issue) for issue in issues]
        listed = {row.number: row for row in rows}
        for number in sorted(set(plans) - set(listed)):
            found.append((index, Issue("ERROR", f"plan {number} has no row in the index")))
        for number in sorted(set(listed) - set(plans)):
            found.append((index, Issue("ERROR", f"index row {number} has no plan file", listed[number].line)))
    graph = {}
    for number, plan in plans.items():
        graph[number] = [n for n in plan.depends if n in plans]
        for dep in plan.depends:
            if dep not in plans:
                found.append((plan.path, Issue("ERROR", f"depends on plan {dep}, which does not exist here")))
    cycle = find_cycle(graph)
    if cycle:
        found.append((directory, Issue("ERROR", "dependency cycle: " + " -> ".join(cycle))))
    return found


def command_lint(args: argparse.Namespace) -> int:
    targets = [Path(p) for p in args.paths] or [d for d in map(Path, PLAN_DIRS) if d.is_dir()][:1]
    if not targets:
        print("plans.py: no plans directory found; pass a path", file=sys.stderr)
        return 2
    results: list[tuple[Path, Issue]] = []
    git_warned = False
    for target in targets:
        if not target.exists():
            print(f"plans.py: {target} does not exist", file=sys.stderr)
            return 2
        git = None
        if not args.no_git:
            git = Git.open(Path(args.root) if args.root else (target if target.is_dir() else target.parent))
            if git is None and not git_warned:
                git_warned = True
                results.append((target, Issue("WARN", "not a git repository; skipped commit and path checks")))
        if target.is_dir():
            results += lint_directory(target, git)
        else:
            results += [(target, issue) for issue in lint_plan(parse_plan(target), git)]
    for path, issue in results:
        where = f"{path}:{issue.line}" if issue.line else str(path)
        print(f"{where}: {issue.level}: {issue.message}")
    errors = sum(1 for _, i in results if i.level == "ERROR")
    print(f"{errors} error(s), {len(results) - errors} warning(s)")
    return 1 if errors else 0


# ---------------------------------------------------------------- status


def build_status(directory: Path, git: Git) -> list[dict]:
    files = {number: parse_plan(path) for number, path in plan_files(directory)}
    index = directory / "README.md"
    rows = {row.number: row for row in parse_index(index)[0]} if index.is_file() else {}
    entries: dict[str, dict] = {}
    for number in sorted(set(files) | set(rows)):
        plan, row = files.get(number), rows.get(number)
        entry = {
            "number": number,
            "title": plan.title if plan else (row.title if row else ""),
            "status": row.status if row else "UNLISTED",
            "note": row.note if row else "",
            "depends": list(plan.depends) if plan else [],
            "external_depends": list(plan.external_depends) if plan else [],
            "branch": plan.branch if plan else None,
            "branch_state": git.branch_state(plan.branch, plan.drift_paths) if plan and plan.branch else None,
            "drift": None,
            "stale": False,
        }
        if plan is None:
            entry["status"] = f"{entry['status']} (no file)"
        elif entry["status"] in ("TODO", "BLOCKED", "IN PROGRESS", "UNLISTED"):
            if not plan.sha or not git.commit_exists(plan.sha):
                entry["stale"] = True
            else:
                entry["drift"] = git.changed_since(plan.sha, plan.drift_paths) if plan.drift_paths else []
        entries[number] = entry
    for entry in entries.values():
        unmet = []
        for dep in entry["depends"]:
            other = entries.get(dep)
            if other is None or other["status"] != "DONE" or other["branch_state"] == "unmerged":
                unmet.append(dep)
        entry["waiting_on"] = unmet
        entry["ready"] = (entry["status"] == "TODO" and not unmet and not entry["stale"] and not entry["drift"])
    return list(entries.values())


def describe(entry: dict) -> str:
    notes = []
    if entry["status"] == "DONE" and entry["branch_state"] == "unmerged":
        notes.append(f"awaiting merge ({entry['branch']})")
    if entry["status"] == "IN PROGRESS" and entry["branch"]:
        notes.append(f"branch {entry['branch']} is {entry['branch_state']}")
    if entry["waiting_on"]:
        notes.append("waits for " + ", ".join(entry["waiting_on"]))
    if entry["external_depends"]:
        notes.append("needs " + ", ".join(entry["external_depends"]))
    if entry["stale"]:
        notes.append("planned-at commit not found")
    elif entry["drift"]:
        shown = ", ".join(entry["drift"][:3]) + (f" (+{len(entry['drift']) - 3})" if len(entry["drift"]) > 3 else "")
        notes.append(f"drift: {shown}")
    if entry["note"]:
        notes.append(entry["note"].strip("()"))
    return "; ".join(notes) or "-"


def command_status(args: argparse.Namespace) -> int:
    directory = Path(args.dir) if args.dir else next((Path(d) for d in PLAN_DIRS if Path(d).is_dir()), None)
    if directory is None or not directory.is_dir():
        print("plans.py: no plans directory found; pass one", file=sys.stderr)
        return 2
    git = Git.open(Path(args.root) if args.root else directory)
    if git is None:
        print("plans.py: status needs a git repository", file=sys.stderr)
        return 2
    entries = build_status(directory, git)
    if args.json:
        print(json.dumps(entries, indent=2))
        return 0
    print(f"{directory} at {git.head()} ({git.current_branch() or 'detached'})")
    print(f"{'PLAN':<6}{'STATUS':<13}{'READY':<7}{'NOTES'}")
    for entry in entries:
        ready = "yes" if entry["ready"] else ("-" if entry["status"] != "TODO" else "no")
        print(f"{entry['number']:<6}{entry['status']:<13}{ready:<7}{describe(entry)}  [{entry['title']}]")
    ready_now = [e["number"] for e in entries if e["ready"]]
    print("Executable now: " + (", ".join(ready_now) if ready_now else "none"))
    return 0


# ---------------------------------------------------------------- scope


def glob_regex(pattern: str) -> re.Pattern[str]:
    """Translate a path glob: `**` crosses directories, `*` and `?` stay inside one."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        else:
            char = pattern[i]
            out.append("[^/]*" if char == "*" else "[^/]" if char == "?" else re.escape(char))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def in_paths(path: str, allowed: list[str]) -> bool:
    for entry in allowed:
        if GLOB_CHARS & set(entry):
            if glob_regex(entry).match(path):
                return True
        elif covers(entry, path):
            return True
    return False


def command_scope(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan)
    if not plan_path.is_file():
        print(f"plans.py: {plan_path} does not exist", file=sys.stderr)
        return 2
    plan = parse_plan(plan_path)
    git = Git.open(Path(args.worktree))
    base = args.base or plan.sha
    if git is None or not base or not git.commit_exists(base):
        print("plans.py: scope needs a worktree that is a git repository and a base commit it contains "
              "(pass --base, or stamp 'Planned at')", file=sys.stderr)
        return 2
    committed = git.run("diff", "--name-only", f"{base}..HEAD")[1].splitlines()
    uncommitted = sorted(set(git.run("diff", "--name-only", "HEAD")[1].splitlines()
                             + git.run("ls-files", "--others", "--exclude-standard")[1].splitlines()))
    allowed = [normalize_path(path) for path, _ in plan.in_scope if path] + plan.regenerated
    print(f"{plan_path.name}: {git.root} against base {base[:12]}")
    outside = 0
    for path in sorted(set(committed) | set(uncommitted)):
        inside = in_paths(path, allowed)
        outside += not inside
        state = "uncommitted" if path in uncommitted else "committed"
        print(f"  {'ok          ' if inside else 'OUT OF SCOPE'} {path} ({state})")
    touched = set(committed) | set(uncommitted)
    for path, create in plan.in_scope:
        path = normalize_path(path)
        if path and not any(covers(path, other) or covers(other, path) for other in touched):
            print(f"  not changed  {path}{' (create): the file was never created' if create else ''}")
    print(f"{outside} out-of-scope file(s), {len(uncommitted)} uncommitted file(s)")
    return 1 if outside else 0


# ---------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint and track improve plans.")
    sub = parser.add_subparsers(dest="command", required=True)
    lint = sub.add_parser("lint", help="check plan files and the index")
    lint.add_argument("paths", nargs="*", help="plan files or plans directories (default: plans, then advisor-plans)")
    lint.add_argument("--no-git", action="store_true", help="skip checks that need a git repository")
    lint.add_argument("--root", help="repository root for git checks (default: the plans path's repository)")
    status = sub.add_parser("status", help="show drift, merge state, and readiness per plan")
    status.add_argument("dir", nargs="?", help="plans directory (default: plans, then advisor-plans)")
    status.add_argument("--json", action="store_true", help="print machine-readable output")
    status.add_argument("--root", help="repository root (default: the plans directory's repository)")
    scope = sub.add_parser("scope", help="list files an executor changed outside the plan's scope")
    scope.add_argument("plan", help="the plan file")
    scope.add_argument("--worktree", required=True, help="the executor's worktree")
    scope.add_argument("--base", help="commit the worktree started from (default: the plan's 'Planned at')")
    args = parser.parse_args(argv)
    return {"lint": command_lint, "status": command_status, "scope": command_scope}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
