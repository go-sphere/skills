# Status Model

The machine-readable status values, who may set them, and the checks the lint command applies.

## Values

Use these exact English values in every artifact. Each entry also carries a `status_label` in the report language.

| `status` | Meaning | English label | 简体中文 label |
|----------|---------|---------------|----------------|
| `open` | Found and not yet approved | Open | 待处理 |
| `approved_for_fix` | Ticked by the user and planned | Approved for fix | 已批准修复 |
| `fixed` | Changed, with passing test evidence | Fixed ✅ | 已修复 ✅ |
| `partially_fixed` | Only part of the finding is addressed | Partially fixed ⚠️ | 部分修复 ⚠️ |
| `wont_fix` | The user decided not to fix it | Won't fix | 不修复 |
| `risk_accepted` | The user accepted the risk | Risk accepted | 已接受风险 |
| `verified` | An independent check confirmed the fix | Verified ✅ | 已验证 ✅ |
| `verification_failed` | The independent check found the fix wrong | Verification failed ❌ | 验证失败 ❌ |
| `test_blocked` | Tests could not run | Test blocked | 测试受阻 |
| `rejected` | Synthesis found the finding invalid | Rejected | 已驳回 |
| `stale` | The cited code changed or vanished since `target_rev` | Stale | 已过期 |

For another language, translate the English label and keep the same ✅, ⚠️, and ❌ marks.

## Transitions

| From | To | Set by | Condition |
|------|----|--------|-----------|
| none | `open` | `synthesize` | A cluster survives vetting |
| none | `rejected` | `synthesize` | Vetting proves the finding invalid |
| `open` | `approved_for_fix` | `fix` | The item is ticked and the scope is confirmed |
| `approved_for_fix` | `fixed` | `fix` | Passing test evidence is recorded |
| `approved_for_fix` | `partially_fixed` | `fix` | Part of the finding remains or a gate failed |
| `approved_for_fix` | `test_blocked` | `fix` | No gate could run |
| `approved_for_fix`, `open` | `wont_fix`, `risk_accepted` | `fix` | The user said so; record when and why |
| `fixed` | `verified` | `verify` | The verification checks pass |
| `fixed`, `partially_fixed` | `verification_failed` | `verify` | A check fails |
| `verification_failed`, `partially_fixed`, `test_blocked` | `approved_for_fix` | `fix` | The user asks to retry |
| any | `stale` | `synthesize`, `fix` | The evidence no longer matches the code |

Only the user decides `wont_fix` and `risk_accepted`. Never infer them.

## Lint checks

The lint command reads `summary.md`, `fix-plan.md`, `status.md`, and `verify.md`.

| Level | Check | Fix |
|-------|-------|-----|
| ERROR | An `RF-NNN` appears twice in `summary.md` | Merge or renumber the new one; keep the older ID |
| ERROR | A status value is not in the table above | Use an exact value |
| ERROR | `fix-plan.md` selects an item that is not ticked in `summary.md` | Remove it, or ask the user to tick it |
| ERROR | `status.md` has a fix-stage status for an item that is not ticked | Same as above |
| ERROR | `fixed` or `verified` with no `passed` row under Test Evidence | Run the gates, or use `test_blocked` |
| ERROR | `verified` with no matching `verified` item in `verify.md` | Run `verify`, or lower the status |
| ERROR | `status.md` exists without `summary.md` | Run `synthesize` first |
| WARN | A ticked item has no row in `status.md` | Run `fix`, or untick it |
| WARN | `<!--` template comments remain in an artifact | Replace each with content or delete it |
| WARN | `target_rev` in `summary.md` differs from HEAD | Re-read the evidence; the review may be stale |

The fix-stage statuses are `approved_for_fix`, `fixed`, `partially_fixed`, `verified`, `verification_failed`, and `test_blocked`.
