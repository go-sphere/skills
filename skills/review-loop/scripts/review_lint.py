#!/usr/bin/env python3
"""Lint the artifacts of one review-loop feature folder.

Usage: review_lint.py lint <feature_dir>

Prints one `ERROR` or `WARN` line per problem. Exit status is 0 without errors,
1 with any error, and 2 on a usage error. Reads only; never writes.
The checks are documented in references/status-model.md.
"""
import re
import subprocess
import sys
from pathlib import Path

STATUSES = {
    "open", "approved_for_fix", "fixed", "partially_fixed", "wont_fix", "risk_accepted",
    "verified", "verification_failed", "test_blocked", "rejected", "stale",
}
FIX_STATES = {"approved_for_fix", "fixed", "partially_fixed", "verified", "verification_failed", "test_blocked"}
NEEDS_PASSING_TEST = {"fixed", "verified"}
ARTIFACTS = ("summary.md", "fix-plan.md", "status.md", "verify.md")

CHECKLIST = re.compile(r"^- \[([ xX])\] `(RF-\d+)`")
PLAN_ITEM = re.compile(r"^- `(RF-\d+)`")
TABLE_ROW = re.compile(r"^\|\s*`(RF-\d+)`\s*\|([^|]*)\|")
STATUS_FIELD = re.compile(r"^\s*- `status`:\s*(.+?)\s*$")
VERIFY_ITEM = re.compile(r"^### Item (RF-\d+)")
TARGET_REV = re.compile(r"^- `target_rev`:\s*(.+?)\s*$", re.M)


def section(text, heading):
    """Return the lines under `## heading`, up to the next `## ` heading."""
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip() == heading
        elif inside:
            lines.append(line)
    return lines


def cell(value):
    return value.strip().strip("`").strip()


def read(folder, name):
    path = folder / name
    return path.read_text(encoding="utf-8") if path.is_file() else None


def lint(folder):
    """Return a list of (level, file, message) for the feature folder."""
    problems = []

    def add(level, name, message):
        problems.append((level, name, message))

    texts = {name: read(folder, name) for name in ARTIFACTS}
    summary, plan, status, verify = (texts[name] for name in ARTIFACTS)

    ticked, seen = {}, set()
    for line in (summary or "").splitlines():
        match = CHECKLIST.match(line)
        if not match:
            continue
        item = match.group(2)
        if item in seen:
            add("ERROR", "summary.md", f"{item} appears more than once")
        seen.add(item)
        ticked[item] = match.group(1) in "xX"

    if status is not None and summary is None:
        add("ERROR", "status.md", "exists without summary.md; run synthesize first")

    for name, text in texts.items():
        if text is None:
            continue
        for line in text.splitlines():
            match = STATUS_FIELD.match(line)
            value = cell(match.group(1)) if match else None
            if value and not value.startswith("<!--") and value not in STATUSES:
                add("ERROR", name, f"unknown status value '{value}'")
        if "<!--" in text:
            add("WARN", name, f"{text.count('<!--')} template comment(s) remain; replace or delete them")

    for line in section(plan or "", "Selected Items"):
        match = PLAN_ITEM.match(line)
        if match and not ticked.get(match.group(1), False):
            add("ERROR", "fix-plan.md", f"{match.group(1)} is selected but not ticked in summary.md")

    rows = {}
    for line in section(status or "", "Status Table"):
        match = TABLE_ROW.match(line)
        if not match:
            continue
        item, value = match.group(1), cell(match.group(2))
        rows[item] = value
        if value not in STATUSES and not value.startswith("<!--"):
            add("ERROR", "status.md", f"{item} has unknown status '{value}'")
        if value in FIX_STATES and not ticked.get(item, False):
            add("ERROR", "status.md", f"{item} is {value} but not ticked in summary.md")

    passed = False
    for line in section(status or "", "Test Evidence"):
        parts = line.split("|")
        if line.startswith("|") and len(parts) > 2 and cell(parts[2]).lower() == "passed":
            passed = True
    verified = {}
    current = None
    for line in (verify or "").splitlines():
        match = VERIFY_ITEM.match(line)
        if match:
            current = match.group(1)
            continue
        match = STATUS_FIELD.match(line)
        if current and match:
            verified[current] = cell(match.group(1))

    for item, value in rows.items():
        if value in NEEDS_PASSING_TEST and not passed:
            add("ERROR", "status.md", f"{item} is {value} but Test Evidence has no passed row; use test_blocked")
        if value == "verified" and verified.get(item) != "verified":
            add("ERROR", "status.md", f"{item} is verified but verify.md has no verified result for it")

    for item, is_ticked in ticked.items():
        if is_ticked and item not in rows:
            add("WARN", "status.md", f"{item} is ticked but has no row; run fix or untick it")

    revision = TARGET_REV.search(summary or "")
    if revision and not revision.group(1).startswith("<!--"):
        try:
            head = subprocess.run(
                ["git", "-C", str(folder), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
            ).stdout.strip()
        except FileNotFoundError:
            head = ""
        recorded = revision.group(1).split("+")[0].strip()
        if head and recorded and not (head.startswith(recorded) or recorded.startswith(head)):
            add("WARN", "summary.md", f"target_rev {recorded[:12]} differs from HEAD {head[:12]}; the review may be stale")
    return problems


def main(argv):
    if len(argv) != 3 or argv[1] != "lint":
        print("Usage: review_lint.py lint <feature_dir>", file=sys.stderr)
        return 2
    folder = Path(argv[2])
    if not folder.is_dir():
        print(f"not a directory: {folder}", file=sys.stderr)
        return 2
    problems = lint(folder)
    for level, name, message in problems:
        print(f"{level} {name}: {message}")
    errors = sum(1 for level, _, _ in problems if level == "ERROR")
    print(f"{errors} error(s), {len(problems) - errors} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
