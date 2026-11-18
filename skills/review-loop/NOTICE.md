# Notice

This skill is adapted from [`review-forge`](https://github.com/vikingmute/review-forge) by
Viking Zhang (`vikingmute`). The four-command loop (review, synthesize, fix, verify), the
feature-folder artifact layout, the checkbox approval boundary, and the status enum names
derive from that work. The upstream repository carried no license file at commit `743b229`
(2026-05-29), the revision this version was adapted from.

Changes in this version: the skill is renamed `review-loop` and restructured to this
repository's progressive-loading contract; reviewers number findings locally and
`synthesize` assigns stable `RF-NNN` IDs, so IDs no longer collide across review files;
`synthesize` vets every finding against the code, keeps rejected findings visible, and
preserves earlier IDs and ticks on re-runs; the default target includes untracked files, any path or repository can be reviewed without a diff, and
resolves the base from `origin/HEAD`; `target_rev`, `fix_base`, and `pre_dirty_files` detect
stale reviews and out-of-scope edits; other reviewers and the independent verifier run
through the `delegate` skill; `fix` writes a reproducing test first and `verify` checks scope,
test gaming, and that the new test fails on the pre-fix revision; the status model gains
`rejected` and `stale`, transitions, and localized labels; language-neutral review prompts and
gate discovery are added, with a separate Go reference; legacy aliases and timestamped file names are dropped; and `scripts/review_lint.py`
checks the artifacts.
