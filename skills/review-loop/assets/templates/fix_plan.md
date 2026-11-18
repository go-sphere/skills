# Fix Plan

- `command`: `fix`
- `feature`: <!-- feature folder name -->
- `target`: <!-- working tree | branch | PR | commit range | paths: a/, b.go | repository -->
- `base`: <!-- comparison ref, or none for the working tree, paths, or repository -->
- `summary_file`: `summary.md`
- `fix_base`: <!-- HEAD commit when fixing started -->
- `pre_dirty_files`: <!-- files already modified before fixing, or none -->
- `report_language`: <!-- auto | en | zh-CN | ... -->
- `created_at`: <!-- ISO 8601 timestamp -->

## Selected Items

<!-- Only items ticked [x] in summary.md and confirmed with the user. -->

- `RF-001`
  - `status`: `approved_for_fix`
  - `status_label`: <!-- localized label -->
  - `planned_change`: <!-- the approach -->
  - `expected_files`: <!-- files the fix may touch -->
  - `required_tests`: <!-- the test that reproduces the finding, plus regression checks -->
  - `rollback_notes`: <!-- how to back the change out -->

## Out Of Scope

<!-- Unticked items and deferred risks. -->

## Test Commands

<!-- Gate commands in order, including any user override. -->
