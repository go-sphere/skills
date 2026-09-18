---
name: go-simplify
description: Audit and safely simplify Go codebases for over-design, over-optimization, and over-defensive coding, then apply behavior-neutral cleanups that never break the exported API or the tests. Use whenever the user asks to simplify, slim down, or review Go code for leanness, over-engineering, dead defensive checks, or unnecessary complexity — including requests phrased as 精简/过度设计/过度优化/过度安全/过度防御/死代码清理 — or wants a "YAGNI / less is more" pass over a Go module, even without those exact words.
---

# Skill: go-simplify

Audit a Go codebase for three classes of excess — **over-design**, **over-optimization**, and **over-defensive coding** — and safely slim it down. Two deliverables: the applied behavior-neutral cleanups, and a written list of findings deliberately left alone.

## Hard Constraints (non-negotiable, in this order)

1. **Never break the exported API.** Change unexported internals only; even a dead exported symbol goes into the report, not the diff. If the repository ships a check such as `make api-compat`, it must run before you finish.
2. **Satisfy the tests.** The test suite is this skill's safety net, not an obstacle — see "Test-vetoed findings" below.
3. **Zero behavior change.** That includes behavior on invalid input: turning code that silently ignores a nil option into code that panics is a bug you introduced.
4. **A scan result is a hypothesis, not a fact.** Every "dead code" claim produced by a subagent or a first-pass scan must be verified by reading the source yourself, one finding at a time, before you touch anything. In practice roughly 5% of "dead code" claims are wrong.

## Test-vetoed Findings

A failing test means the "dead code" claim was wrong. **Roll back that change immediately**, record it in the legitimate-defense list, and move on. Two real cases to remember:

- `atomic.Pointer[T].Store(nil)` does **not** panic (only `atomic.Value` panics, and only on a nil interface). A seemingly unreachable nil fallback may be functionality pinned by a test that explicitly calls `Store(nil)` to simulate "use before initialization".
- An unexported helper may be referenced directly from `_test.go` — especially around `defer f.Close()`, because `defer _ = f.Close()` is not a legal statement and a tiny helper is the cleanest errcheck-safe spelling. Before deleting any unexported identifier, your grep must include test files.

## Workflow

### Step 1: Establish a green baseline

Run the full test suite first and confirm it passes. Record the result. If the baseline is not green, stop simplifying and report the baseline failure instead.

### Step 2: Scan by module, in parallel

For large repositories (more than ~50 Go files), dispatch several read-only exploration agents grouped by module (for example core/log/cache/server/storage). Give every agent the same pattern list (read [references/patterns.md](references/patterns.md)) and require it to report only findings whose surrounding context it actually read:

```
file:line | code excerpt (2-5 lines) | class (design/optimization/defense) | why it is excess | does the change touch the exported API
```

For small repositories, scan directly yourself. Before scanning, read [references/patterns.md](references/patterns.md); it also carries the **legitimate-defense whitelist** — code that looks excessive but carries a comment explaining a real reachable path. Do not report anything on that whitelist.

### Step 3: Verify every finding yourself (core step, never skipped)

For each candidate finding, complete four checks before editing:

1. **Prove the invariant.** Read the surrounding code and find the construct that makes the check dead: a paired assignment under the same mutex, a unique construction site, a range-index bound. No proof, no change.
2. **Grep the identifier across the whole repository**, including `*_test.go`.
3. **Check whether a test pins the behavior.** Be suspicious when a test name or comment mentions "fallback", "pins", or "uninitialized" — that is often deliberate functionality.
4. **Read the comment next to the code.** Defenses that explain a reachable path ("third-party impls can return zero", "prevents aliasing") are almost always legitimate. Do not report them.

### Step 4: Sort into three buckets

- **Change now**: unexported, proven dead or a provably equivalent simplification, and not referenced by tests.
- **Report only**: speculative surface on the exported API (interfaces, constructors, sentinel errors nobody uses) — list them as deprecation candidates for the next major version; do not delete them.
- **Keep**: legitimate defenses that survived verification. They go into the "deliberately untouched" section of the final report with their rationale.

### Step 5: Edit in small batches, verify immediately

Edit package by package in small batches and run that package's tests after each batch. When a change breaks a test, roll back only that change (`git checkout -- <file>`, or the reverse edit). Never adjust the test to accommodate the cleanup. (When a test merely names an identifier you removed and the change is semantically equivalent, rolling back is still the safer call.)

### Step 6: Run the full gate

- `go build ./...`
- `go test ./...`
- Add `go test -race` for files that touch concurrency (lifecycle, locks, channels)
- `make lint` or the equivalent (including nilaway / staticcheck-class tools, since lazy-allocation and nil-handling rewrites can trip static analysis)
- The api-compat script, if the repository has one

### Step 7: Write the report

The report must contain all three parts:

1. **What changed**, grouped by the three classes, each entry with file:line and a one-line reason.
2. **Deliberately untouched**: legitimate defenses plus exported-surface debt, each with its rationale. This list is what stops a future reader (or a future you) from damaging the same code again.
3. **Verification evidence**: the actual outcomes of the build, test, race, lint, and api-compat runs.

## Judgment Criteria

What separates the three classes:

- **Over-design**: structural cost paid for requirements that do not exist (injection points nobody injects, empty files reserved for the future, abstraction layers with zero callers, sentinel values behaviorally identical to the zero value).
- **Over-optimization**: complexity with no measurement behind it (wrong capacity hints, reuse tricks on cold paths, eager allocation that could be lazy). It has a mirror image: **failing to be lazy when laziness is possible** is also overpaying.
- **Over-defensive coding**: checks against states that cannot occur (nil under a paired-lock protocol, index bounds on a range index, re-validation of an already-normalized value, unreachable error branches).

Misclassifying a finding is not the problem. Being unsure **whether to delete it** is — when in doubt, put it under "report only".

## Related Skills

- Upstream — none; this skill applies after any implementation, or directly to an existing Go module. The test suite is the safety net, so run `go-test-engineering` first when that suite is unreliable or AI-generated.
- Downstream — none; the applied cleanups and the three-part report are the deliverable.
- Boundary — use `go-test-engineering` for test content, assertions, and coverage; this skill owns production-code simplification and never edits tests to make a cleanup pass. Use `sphere-feature-workflow` for feature delivery and `go-sphere-makefiles` for the Make targets it gates on.
- Companion — `go-test-engineering` when a "dead code" finding needs a pinning test before removal; if it is unavailable, record the finding under "report only" instead of deleting.
- If a referenced skill is not installed in this session, name it in the handoff message and continue with the current artifact; do not stall.
