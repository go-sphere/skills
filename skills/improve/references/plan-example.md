> **Illustrative example.** The repository, paths, and code below are constructed
> to show the format of a finished plan. Do not copy paths or code from it into a
> real plan; read the real repository.

# Plan 001: Reject an invalid PORT instead of silently listening on a random port

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before the next step.
> If anything in "STOP conditions" occurs, stop and report; do not improvise.
> When done, update this plan's row in `plans/README.md`, unless a reviewer
> dispatched you and said they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 3f9c2a7d41be..HEAD -- internal/config/load.go internal/config/load_test.go`
> Expected: no output. Output means an in-scope file changed since this plan
> was written. Compare "Current state" with the live code; a mismatch is a STOP
> condition. If `3f9c2a7d41be` is not in the repository, that is also a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Finding**: `bug:internal/config/load.go:Load`
- **Planned at**: commit `3f9c2a7d41be`, 2026-11-13

## Why this matters

`config.Load` parses the `PORT` environment variable with `strconv.Atoi` and
discards the error. A value such as `80a0` parses to 0, and `net.Listen` treats
port 0 as "pick any free port", so the service boots, looks healthy, and
receives no traffic. The failure shows up in production as a silent outage
instead of a startup error. After this plan an invalid `PORT` stops the process
at boot with a message that names the variable.

## Current state

- `internal/config/load.go` — builds `Config` from the environment; the discarded error is at line 40.
- `internal/config/load_test.go` — table-driven tests for `Load`.
- `cmd/app/main.go:19` — calls `config.Load()` and already exits on a non-nil error.

```go
// internal/config/load.go:38-43
func Load() (*Config, error) {
	cfg := &Config{Host: getenv("HOST", "0.0.0.0")}
	port, _ := strconv.Atoi(getenv("PORT", "8080"))
	cfg.Port = port
	return cfg, nil
}
```

- Convention: errors wrap with `%w` and name the input. Match
  `internal/config/file.go:27`: `return nil, fmt.Errorf("read %s: %w", path, err)`.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Package tests | `go test ./internal/config/... -count=1` | `ok` |
| Vet | `go vet ./...` | exit 0, no output |
| Format check | `gofmt -l internal/config` | no output |
| Gate | `make check` | exit 0 |

## Suggested executor toolkit

- `go-test`, when available, for the table cases in step 1.

## Scope

**In scope** (the only files you may modify):
- `internal/config/load.go`
- `internal/config/load_test.go`

**Out of scope** (do NOT touch, even though they look related):
- `internal/config/schema.go` — other packages read the `Config` shape; this plan changes no field.
- `cmd/app/main.go` — it already handles the error returned by `Load`.

## Git workflow

- Branch: `advisor/001-reject-invalid-port`
- One commit per step, in the repository's style, for example `fix(config): reject an invalid PORT`.
- Do NOT push or open a pull request unless the operator said so.

## Steps

### Step 1: Add a failing regression test

In `internal/config/load_test.go`, add three cases to the table in `TestLoad`:
`PORT=80a0`, `PORT=-1`, and `PORT=70000`. Each expects a non-nil error whose
text contains `PORT`. Set the variable with `t.Setenv`. Copy the structure of
the existing "invalid HOST" case.

**Verify**: `go test ./internal/config/... -run TestLoad -count=1` → FAIL, and the failures name the three new cases (today `Load` returns no error).

### Step 2: Return an error for an invalid PORT

In `Load`, replace the discarded error with:

```go
raw := getenv("PORT", "8080")
port, err := strconv.Atoi(raw)
if err != nil {
	return nil, fmt.Errorf("invalid PORT %q: %w", raw, err)
}
if port < 1 || port > 65535 {
	return nil, fmt.Errorf("invalid PORT %q: want 1..65535", raw)
}
cfg.Port = port
```

**Verify**: `go test ./internal/config/... -count=1` → `ok`

### Step 3: Confirm every caller handles the error

Read each match of the search below and confirm it checks the returned `err`.

**Verify**: `grep -rn "config.Load(" --include='*.go' .` → exactly one match, `cmd/app/main.go:19`

## Test plan

- Three new cases from step 1, in `internal/config/load_test.go`, modeled on the existing table in `TestLoad`.
- The existing cases (`HOST` default, valid `PORT=9000`) stay green.
- Verification: `go test ./internal/config/... -count=1` → `ok`, including the 3 new cases.

## Done criteria

All must hold:

- [ ] `go test ./internal/config/... -count=1` exits 0; the three invalid-`PORT` cases exist and pass
- [ ] `go vet ./...` exits 0
- [ ] `gofmt -l internal/config` prints nothing
- [ ] `make check` exits 0
- [ ] `grep -n "port, _ :=" internal/config/load.go` returns no matches
- [ ] `git diff --stat 3f9c2a7d41be..HEAD` lists only the two in-scope files
- [ ] `git status --short` prints nothing: everything is committed
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back, without improvising, if:

- The code at `internal/config/load.go:38-43` does not match the excerpt.
- Step 3 finds a caller of `Load` that ignores the returned error. Report it; do not edit the caller.
- An existing test sets `PORT=0` to request any free port and now fails. That may be intentional; report it.

## Report back

Reply with: STATUS (`COMPLETE` or `STOPPED`); per step, done or skipped plus its
verification result; if `STOPPED`, which condition and what you observed; the files
changed; deviations and judgment calls. State only what a command result from
this session supports. Say plainly when a verification failed or was skipped.

## Maintenance notes

- A new environment variable parsed in `Load` should follow the same pattern: wrap the parse error and name the variable.
- Reviewer: confirm the new cases fail on the base commit, and that nothing relied on the old port-0 fallback.
- Deferred: validating `HOST`. Any string is accepted today and `net.Listen` reports a bad value at boot, which is acceptable.
