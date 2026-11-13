# Verification Crucible

How to test the port, heal failures within the 5-iteration budget, and log each run.

Recipes use `TM` and `TEL` as defined in SKILL.md step 1; set them again in every shell call.

## Gate commands

Run, in this order, and log each iteration:

```bash
go build ./...
go vet ./...
golangci-lint run          # or: staticcheck ./...
go test -race -cover -coverprofile=cover.out ./...
go tool cover -func=cover.out | tail -1
```

`-race` needs cgo enabled and a C compiler on most platforms; if the machine cannot run
it, say so in the log rather than skipping silently. Add fuzz targets (`func FuzzXxx(f
*testing.F)`) for parsers, decoders, and anything fed untrusted input, and run each
for a bounded `-fuzztime` (for example `30s`). Target `>= 90%` statement coverage on
migrated packages. Log the `total:` line of `go tool cover -func` as `--coverage-pct`.
Never reconstruct a run after the fact; log counts printed by the command you ran. If failures remain after 5 iterations, log them honestly.

Translate the legacy test suite where it exists (its assertions are a free oracle),
but rewrite it as table-driven Go tests rather than mimicking the source framework.

## Log every run (`test_heal`)

```bash
python3 "$TM" start-bucket --telemetry "$TEL" --bucket test_heal
python3 "$TM" log-test-run --telemetry "$TEL" \
  --iteration 1 --total 42 --passed 34 --failed 8 \
  --coverage-pct 83.5 --lint-issues 3 \
  --failures-summary "19.0% failed (8/42): window boundary off-by-one; -race flagged an unguarded counter." \
  --fix-applied "Corrected the inclusive upper bound; guarded the counter with the owning mutex."
```

Repeat per rebuild/re-test (max 5), targeting `--failed 0`, `--lint-issues 0`,
`--coverage-pct` `>= 90`. Log Iteration 1 honestly even when everything passed.
