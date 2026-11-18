# Verification Report

- `command`: `verify`
- `feature`: <!-- feature folder name -->
- `target`: <!-- working tree | branch | PR | commit range | paths: a/, b.go | repository -->
- `base`: <!-- comparison ref, or none for the working tree, paths, or repository -->
- `summary_file`: `summary.md`
- `fix_plan_file`: `fix-plan.md`
- `fix_base`: <!-- from fix-plan.md -->
- `verifier`: <!-- the agent or person verifying -->
- `independent`: <!-- yes | no: a different agent than the fixer -->
- `report_language`: <!-- auto | en | zh-CN | ... -->
- `created_at`: <!-- ISO 8601 timestamp -->

## Verification Results

### Item RF-001

- `status`: <!-- verified | verification_failed | partially_fixed | test_blocked -->
- `status_label`: <!-- localized label -->
- `expected_fix`: <!-- what should have changed -->
- `observed_result`: <!-- what changed, and whether every touched path was in scope -->
- `test_evidence`: <!-- commands rerun and their results -->
- `regression_risk`: <!-- callers, error paths, or shared state near the fix -->
- `next_action`: <!-- none | retry fix | ask user | accept risk -->

## Test Log Summary

<!-- Commands, results, and important failures. Do not paste long logs. -->

## Residual Risks

<!-- Anything not fully verified or left unresolved. -->
