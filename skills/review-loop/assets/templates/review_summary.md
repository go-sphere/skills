# Review Summary

- `command`: `synthesize`
- `feature`: <!-- feature folder name -->
- `target`: <!-- working tree | branch | PR | commit range | paths: a/, b.go | repository -->
- `base`: <!-- comparison ref, or none for the working tree, paths, or repository -->
- `target_rev`: <!-- HEAD commit, plus +dirty when the tree has uncommitted changes -->
- `feature_dir`: `code_review/<feature>/`
- `report_language`: <!-- auto | en | zh-CN | ... -->
- `updated_at`: <!-- ISO 8601 timestamp -->
- `source_reports`: <!-- review files used, for example claude.md, codex.md -->

## Fix Approval Checklist

<!-- Ticked [x] means approved for fixing; only the user ticks. Unticked [ ] means do not fix. -->
<!-- Keep earlier RF IDs, ticks, and statuses when updating this file. -->

- [ ] `RF-001` <!-- short title -->
  - `status`: `open`
  - `status_label`: <!-- localized label -->
  - `severity`: <!-- critical | high | medium | low | note -->
  - `vetted`: <!-- confirmed | unconfirmed -->
  - `sources`: <!-- claude#F1, codex#F3 -->
  - `reviewer_agreement`: <!-- for example 2/3 -->
  - `affected_files`: <!-- path:line -->
  - `summary`: <!-- the merged issue -->
  - `rationale`: <!-- why it matters -->
  - `proposed_fix`: <!-- the specific intended change -->
  - `suggested_tests`: <!-- tests to run after fixing -->

## Rejected Findings

<!-- One line each: source ID, and why vetting rejected it. -->

## Common Themes

<!-- Repeated patterns or shared root causes. -->

## Disagreements And Deferrals

<!-- Severity disputes, pre-existing problems, and findings deferred with the reason. -->
