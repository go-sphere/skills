# Code Review Report

- `model`: <!-- claude | codex | kimi | agy | pi -->
- `perspective`: <!-- correctness | security | concurrency | tests | ... | all -->
- `command`: `review`
- `feature`: <!-- feature folder name -->
- `target`: <!-- working tree | branch | PR | commit range | paths: a/, b.go | repository -->
- `base`: <!-- comparison ref, or none for the working tree, paths, or repository -->
- `target_rev`: <!-- HEAD commit, plus +dirty when the tree has uncommitted changes -->
- `report_language`: <!-- auto | en | zh-CN | ... -->
- `created_at`: <!-- ISO 8601 timestamp -->

## Scope

<!-- The reviewed diff or files, the files read for context, and any slice or area you skipped. -->

## Findings

<!-- Number findings F1, F2, ... Write `No findings` and what you checked when there are none. -->

### F1: <!-- short title -->

- `severity`: <!-- critical | high | medium | low | note -->
- `confidence`: <!-- high | medium | low -->
- `affected_files`: <!-- path:line, one per entry -->
- `evidence`: <!-- the code or behavior that proves it, at most five quoted lines -->
- `risk`: <!-- who or what breaks, under which input or state -->
- `suggested_fix`: <!-- a concrete change -->
- `suggested_tests`: <!-- the test that fails before the fix and passes after -->

## Reviewer Notes

<!-- Problems outside the target scope, assumptions, and areas that need another reviewer. -->
