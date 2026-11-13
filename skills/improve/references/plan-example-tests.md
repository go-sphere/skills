> **Illustrative example.** The repository, paths, and code below are constructed
> to show a plan that only adds tests, with a mutation check in place of a failing
> first step. Do not copy paths or code from it into a real plan.

# Plan 002: Pin the size-limit boundary of fetch.Get with tests

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before the next step.
> If anything in "STOP conditions" occurs, stop and report; do not improvise.
> When done, update this plan's row in `plans/README.md`, unless a reviewer
> dispatched you and said they maintain the index.
>
> **Drift check (run first)**: `git diff --stat 3f9c2a7d41be..HEAD -- internal/fetch/fetch.go internal/fetch/limit_test.go`
> Expected: no output. Output means an in-scope file changed since this plan
> was written. Compare "Current state" with the live code; a mismatch is a STOP
> condition. If `3f9c2a7d41be` is not in the repository, that is also a STOP condition.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: tests
- **Finding**: `tests:internal/fetch/fetch.go:Get`
- **Planned at**: commit `3f9c2a7d41be`, 2026-11-13

## Why this matters

`fetch.Get` rejects a body larger than `WithMaxBytes`, but no test sends a body at
or just over the limit. `go test ./internal/fetch -cover` reports 71.4% and the
overflow branch at `fetch.go:56-58` never runs. Changing `>` to `>=` there would
reject bodies of exactly the limit, and nothing would fail. After this plan both
sides of the boundary are pinned, and a mutation check proves the tests can fail.

## Current state

- `internal/fetch/fetch.go` — `Get` reads the body through `io.LimitReader(resp.Body, maxBytes+1)` and compares the length with the limit.
- `internal/fetch/fetch_test.go` — existing tests; none uses `WithMaxBytes`.
- Tests in this package are `package fetch`, build servers with `httptest.NewServer`, and fail with `t.Fatalf`.

```go
// internal/fetch/fetch.go:52-58
	body, err := io.ReadAll(io.LimitReader(resp.Body, c.maxBytes+1))
	if err != nil {
		return nil, fmt.Errorf("read body: %w", err)
	}
	if int64(len(body)) > c.maxBytes {
		return nil, ErrTooLarge
	}
```

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| New tests | `go test ./internal/fetch -run LimitBoundary -count=1` | `ok` |
| Package with race | `go test -race ./internal/fetch -count=1` | `ok` |
| Coverage | `go test ./internal/fetch -cover -count=1` | `ok`, coverage above 71.4% |
| Gate | `make check` | exit 0 |

Never run `make fmt` or `make tidy`: they rewrite files.

## Scope

**In scope** (the only files you may modify):
- `internal/fetch/limit_test.go` (create)
- `internal/fetch/fetch.go` — temporary edit in step 2, reverted in step 3

**Out of scope** (do NOT touch, even though they look related):
- `internal/fetch/fetch_test.go` — existing tests stay as they are.
- Any permanent change to `fetch.go`; this plan adds tests only.

## Git workflow

- Branch: `advisor/002-pin-fetch-limit-boundary`
- One commit after step 4, for example `test(fetch): pin the body size limit boundary`.
- Do NOT push or open a pull request unless the operator said so.

## Steps

### Step 1: Add the boundary tests

Create `internal/fetch/limit_test.go` with exactly this content. The handler
flushes first, so the response is chunked and carries no `Content-Length`; only
the read-then-compare check can see the size.

```go
package fetch

import (
	"context"
	"errors"
	nethttp "net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func serveBytes(t *testing.T, n int) *httptest.Server {
	t.Helper()
	srv := httptest.NewServer(nethttp.HandlerFunc(func(w nethttp.ResponseWriter, _ *nethttp.Request) {
		w.(nethttp.Flusher).Flush()
		_, _ = w.Write([]byte(strings.Repeat("x", n)))
	}))
	t.Cleanup(srv.Close)
	return srv
}

func TestFetchLimitBoundaryAtLimitSucceeds(t *testing.T) {
	body, err := Get(context.Background(), serveBytes(t, 8).URL, WithMaxBytes(8))
	if err != nil || len(body) != 8 {
		t.Fatalf("expected 8 bytes and no error, got %d bytes, err %v", len(body), err)
	}
}

func TestFetchLimitBoundaryOneOverFails(t *testing.T) {
	_, err := Get(context.Background(), serveBytes(t, 9).URL, WithMaxBytes(8))
	if !errors.Is(err, ErrTooLarge) {
		t.Fatalf("expected ErrTooLarge, got %v", err)
	}
}
```

**Verify**: `go test ./internal/fetch -run LimitBoundary -count=1` → `ok`. Both tests pass on the unmodified code.

### Step 2: Prove the tests can fail

In `internal/fetch/fetch.go` line 56, change `>` to `>=` in `if int64(len(body)) > c.maxBytes {`. Change nothing else.

**Verify**: `go test ./internal/fetch -run LimitBoundary -count=1` → FAIL, and the failure names `TestFetchLimitBoundaryAtLimitSucceeds` with `expected 8 bytes and no error`.

### Step 3: Revert the edit

Restore the file exactly.

**Verify**: `git status --short` → exactly one line, `?? internal/fetch/limit_test.go`.

### Step 4: Run the checks

**Verify**: `go test -race ./internal/fetch -cover -count=1` → `ok`, with coverage above 71.4%.

## Test plan

- Two new tests, modeled on the server helpers in `internal/fetch/fetch_test.go`: a body of exactly the limit succeeds, and a body one byte over fails with `ErrTooLarge`.
- The mutation in step 2 is the proof that the first test constrains the boundary.
- Verification: `go test ./internal/fetch -count=1` → `ok`, including both new tests.

## Done criteria

All must hold:

- [ ] `go test ./internal/fetch -run LimitBoundary -count=1` exits 0 on the final tree
- [ ] your report quotes the FAIL output of `go test ./internal/fetch -run LimitBoundary -count=1` from step 2
- [ ] `go test -race ./internal/fetch -count=1` exits 0
- [ ] `git diff --stat HEAD -- internal/fetch/fetch.go` prints nothing
- [ ] `git diff --stat 3f9c2a7d41be..HEAD` lists only `internal/fetch/limit_test.go`
- [ ] `git status --short` prints nothing: everything is committed
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back, without improvising, if:

- The code at `internal/fetch/fetch.go:52-58` does not match the excerpt.
- A new test fails at step 1. The code does not behave as this plan says; report what you observed.
- No test fails at step 2. The tests do not pin the boundary; report it and do not weaken or delete them.
- `git status --short` after step 3 lists `fetch.go`. Run `git checkout -- internal/fetch/fetch.go` and check again before going on.

## Report back

Reply with: STATUS (`COMPLETE` or `STOPPED`); per step, done or skipped plus its
verification result; if `STOPPED`, which condition and what you observed; the files
changed; deviations and judgment calls. State only what a command result from
this session supports. Say plainly when a verification failed or was skipped.

## Maintenance notes

- If the limit semantics change (for example "at least", not "more than"), update both tests together.
- Reviewer: confirm the final diff contains only `limit_test.go`, and that the quoted step 2 failure names the at-limit test.
- Deferred: a test for a body with a `Content-Length` header over the limit, which takes the fast-fail path.
