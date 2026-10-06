# Section Writing Patterns

Concrete shapes for the sections that most often come out thin. The overall structure lives in
`section-stack.md`. Examples quoted from https://github.com/openai/symphony/blob/main/SPEC.md.

## Thin vs Strong

Thin:

- Support retries.
- Read config from YAML.
- Watch for file changes.

Strong:

- Failure-driven retries use exponential backoff capped at a configured maximum.
- YAML values may reference environment variables via `$VAR_NAME`; empty expansion counts as missing.
- Invalid reloads do not crash the service; the runtime keeps the last known good config and emits an operator-visible error.

## Separate Internal and External State

If the system coordinates work, define its own orchestration states even when an external system
already has states.

> "This is not the same as tracker states (`Todo`, `In Progress`, etc.). This is the service's
> internal claim state."

Then it defines: `Unclaimed`, `Claimed`, `Running`, `RetryQueued`, `Released`.

## Specify Source Precedence

When configuration can come from files, defaults, environment variables, or CLI flags, define the
exact precedence order.

> "Configuration precedence:
> 1. Workflow file path selection (runtime setting -> cwd default).
> 2. YAML front matter values.
> 3. Environment indirection via `$VAR_NAME` inside selected YAML values.
> 4. Built-in defaults."

## Specify Dynamic Reload Semantics

Say which changes apply immediately, which affect future work only, and which require restart.

> "Dynamic reload is required:
> - The software should watch `WORKFLOW.md` for changes.
> - On change, it should re-read and re-apply workflow config and prompt template without restart.
> - ...Reloaded config applies to future dispatch, retry scheduling, reconciliation decisions...
> - Invalid reloads should not crash the service; keep operating with the last known good
>   effective configuration and emit an operator-visible error."

## Specify Preflight Validation

Say what is validated at startup or before dispatch, and whether invalid configuration blocks
dispatch, blocks startup, or only logs a warning.

> "Startup validation:
> - Validate configuration before starting the scheduling loop.
> - If startup validation fails, fail startup and emit an operator-visible error.
>
> Per-tick dispatch validation:
> - Re-validate before each dispatch cycle.
> - If validation fails, skip dispatch for that tick..."

## Specify Recovery Behavior

State what happens on restart, on missed watch events, on partial failure, and on terminal
cleanup.

> "Startup terminal workspace cleanup:
> 1. Query tracker for issues in terminal states.
> 2. For each returned issue identifier, remove the corresponding workspace directory.
> 3. If the terminal-issues fetch fails, log a warning and continue startup."

## Use Redundant Summary Sections When Helpful

If a long section is dense, add a compact summary or cheat sheet. That is good spec writing, not
wasted space.

> "This section is intentionally redundant so a coding agent can implement the config layer
> quickly."

Then it provides a table of all config fields.

## Configuration Section Pattern

For each config group, write:

```markdown
#### 5.3.1 `tracker` (object)

Fields:

- `kind` (string)
  - Required for dispatch.
  - Current supported value: `linear`
- `endpoint` (string)
  - Default for `tracker.kind == "linear"`: `https://api.linear.app/graphql`
- `api_key` (string)
  - May be a literal token or `$VAR_NAME`.
  - Canonical environment variable for `tracker.kind == "linear"`: `LINEAR_API_KEY`.
  - If `$VAR_NAME` resolves to an empty string, treat the key as missing.
```

Always include: field name and type, required or optional, default value, environment variable
indirection when applicable, validation and constraint rules, and edge case handling.

## State Machine Pattern

Define states first, then triggers for each transition.

```markdown
### 7.1 Issue Orchestration States

1. `Unclaimed`
   - Issue is not running and has no retry scheduled.

2. `Claimed`
   - Orchestrator has reserved the issue to prevent duplicate dispatch.

3. `Running`
   - Worker task exists and the issue is tracked in `running` map.

4. `RetryQueued`
   - Worker is not running, but a retry timer exists.

5. `Released`
   - Claim removed because issue is terminal or no longer eligible.
```

## Entity Definition Pattern

```markdown
#### 4.1.1 Issue

Normalized issue record used by orchestration, prompt rendering, and observability output.

Fields:

- `id` (string)
  - Stable tracker-internal ID.
- `identifier` (string)
  - Human-readable ticket key (example: `ABC-123`).
- `priority` (integer or null)
  - Lower numbers are higher priority in dispatch sorting.
```

## Error Class Pattern

```markdown
Error classes:

- `missing_workflow_file`
- `workflow_parse_error`
- `template_render_error`

Dispatch gating behavior:
- Workflow file read/YAML errors block new dispatches until fixed.
- Template errors fail only the affected run attempt.
```

## Hook or Callback Pattern

```markdown
#### 9.4 Workspace Hooks

Supported hooks:
- `hooks.after_create`
- `hooks.before_run`

Execution contract:
- Execute in a local shell context with the workspace directory as `cwd`.
- Hook timeout uses `hooks.timeout_ms`; default: `60000 ms`.

Failure semantics:
- `after_create` failure or timeout is fatal to workspace creation.
- `before_run` failure or timeout is fatal to the current run attempt.
```
