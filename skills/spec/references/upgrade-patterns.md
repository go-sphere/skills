# Upgrade Patterns

Use these patterns to turn a thin spec into a stronger, Symphony-grade spec.

## Pattern 1: Turn Concepts into Typed Objects

Thin:
- The service tracks retries and sessions.

Upgrade:
- Define `RetryEntry` with fields, identifiers, attempt numbering, due time, and error summary.
- Define `LiveSession` with identifiers, timestamps, token counters, and last event state.

**Example from Symphony:**
```markdown
#### Retry Entry

Fields:

- `issue_id`
- `identifier` (best-effort human ID for status surfaces/logs)
- `attempt` (integer, 1-based for retry queue)
- `due_at_ms` (monotonic clock timestamp)
- `timer_handle` (runtime-specific timer reference)
- `error` (string or null)
```

Rule: every important runtime noun should become an explicit object, not remain a loose concept.

## Pattern 2: Split User State from Internal State

Thin:
- The task can be in progress or done.

Upgrade:
- Define external task state separately from internal orchestration state.
- Explain which one drives dispatch, which one drives the UI, and how they interact.

Rule: if a system coordinates work, it usually needs an internal state model beyond the user-facing one.

## Pattern 3: Replace Feature Claims with Semantics

Thin:
- The system supports retries.

Upgrade:
- State when retries are created, how delay is calculated, what caps apply, when retries stop, and when a claim is released.

**Example from Symphony:**
```markdown
Backoff formula:
- Normal continuation retries after a clean worker exit use a short fixed delay of `1000` ms.
- Failure-driven retries use `delay = min(10000 * 2^(attempt - 1), agent.max_retry_backoff_ms)`.
- Power is capped by the configured max retry backoff (default `300000` / 5m).
```

Rule: continue writing until the behavior is mechanically understandable.

## Pattern 4: Make Config Operational

Thin:
- Config is read from `config.yaml`.

Upgrade:
- Define discovery order, path resolution, env variable expansion, defaults, coercion, validation, unknown-key behavior, dynamic reload behavior, and invalid reload behavior.

**Example from Symphony:**
```markdown
### 6.1 Source Precedence and Resolution Semantics

Configuration precedence:
1. Workflow file path selection (runtime setting -> cwd default).
2. YAML front matter values.
3. Environment indirection via `$VAR_NAME` inside selected YAML values.
4. Built-in defaults.

Value coercion semantics:
- Path/command fields support:
  - `~` home expansion
  - `$VAR` expansion for env-backed path values
```

Rule: config sections should feel like their own mini-spec.

## Pattern 5: Add Validation Gates

Thin:
- Validate the workflow before running.

Upgrade:
- Separate startup validation from per-dispatch validation.
- List exact checks.
- State whether failure blocks startup, blocks dispatch, or only emits warnings.

**Example from Symphony:**
```markdown
### 6.3 Dispatch Preflight Validation

Startup validation:
- Validate configuration before starting the scheduling loop.
- If startup validation fails, fail startup and emit an operator-visible error.

Per-tick dispatch validation:
- Re-validate before each dispatch cycle.
- If validation fails, skip dispatch for that tick, keep reconciliation active, and emit an operator-visible error.

Validation checks:
- Workflow file can be loaded and parsed.
- `tracker.kind` is present and supported.
- `tracker.api_key` is present after `$` resolution.
```

Rule: validation must have timing and consequences, not just existence.

## Pattern 6: Add Recovery and Cleanup

Thin:
- The service resumes after restart.

Upgrade:
- Define startup cleanup, how stale resources are found, which work is reconstructed from external truth, and what happens if reconciliation fails.

Rule: if the system is long-running, restart behavior is part of the contract.

## Pattern 7: Add Redundant Cheat Sheets

Thin:
- Long prose only.

Upgrade:
- Add a compact table or bullet summary of config fields, states, or error classes after the detailed section.

Rule: redundancy is valuable when it accelerates implementation and reduces ambiguity.

## Pattern 8: Add Extension Boundaries

Thin:
- Additional keys may be supported later.

Upgrade:
- State that unknown keys are ignored for forward compatibility, define which extensions are optional, and state whether they support live reload.

Rule: optional features still need explicit contract behavior.

## Pattern 9: Deepen Existing Sections Instead of Only Adding New Ones

When a draft feels weak, do not immediately add more headings. First ask whether each existing heading is too vague. The fix is often to add field-level and transition-level semantics inside the current structure.

## Pattern 10: Add a Final Implementer Check

Before finishing, read the spec as if you had to build it tomorrow.

If you still need to ask:
- what exactly are the states
- where does this config come from
- what happens on invalid input
- what happens on restart
- what gets retried or logged

then the spec is not done yet.
