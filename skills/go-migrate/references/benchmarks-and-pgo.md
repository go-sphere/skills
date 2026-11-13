# Benchmarks, Tuning and Go PGO

The four-stage performance staircase, how to measure it, and the PGO recipe.

Recipes use `TM` and `TEL` as defined in SKILL.md step 1; set them again in every shell call.

## Four-stage performance staircase

Measure four checkpoints so each technique's contribution is isolated:

1. **`legacy_baseline`** — the original build in release mode (`1.0x`).
2. **`idiomatic_go`** — the straightforward, idiomatic port with no tuning.
3. **`tuned_go`** — changes justified by `pprof` CPU and allocation profiles: removed
   allocations in hot loops (preallocated slices and maps, `strings.Builder`,
   `bytes.Buffer` reuse, avoiding interface boxing and `fmt` in hot paths), struct
   field ordering, data layout (Struct-of-Arrays only where a profile shows the cache
   misses), bounded parallelism for independent work, `sync.Pool` only for measured
   churn. Stay in pure Go: no assembly, `unsafe`, or cgo.
4. **`pgo`** — the same code rebuilt with a merged CPU profile (see Go PGO Workflow below).

Benchmarks use `testing.B` with `-benchmem` and `-count=10`, compared with
`benchstat` (`go install golang.org/x/perf/cmd/benchstat@latest` when missing), for
micro-level changes, and end-to-end wall time plus peak RSS (via
`/usr/bin/time -l` on macOS or `-v` on Linux) on the baseline workload for the
logged stages. Convert peak RSS to megabytes before logging (see Stage 0). A tuning stage
that did not help is logged as measured, not omitted.

## Log the idiomatic and tuned stages

```bash
python3 "$TM" start-bucket --telemetry "$TEL" --bucket rewrite
```

Benchmark the idiomatic port and the profile-driven tuning with `log-benchmark`, using
`--stage idiomatic_go` and `--stage tuned_go`.

## Go PGO Workflow

Start the bucket: `python3 "$TM" start-bucket --telemetry "$TEL" --bucket pgo_bench`. Go PGO needs no
extra tools: the `go` command reads a CPU profile named `default.pgo` in the main
package directory and, with the default `-pgo=auto`, uses it automatically.

1. **Collect representative CPU profiles** (3–5 workloads). The profile must come from a
   realistic run, not a micro-benchmark of one function:
   - CLI or batch program: add (or temporarily wire) `runtime/pprof` behind a
     `-cpuprofile` flag, or profile through a benchmark that drives the real entry
     point: `go test -bench=BenchmarkEndToEnd -cpuprofile=cpu1.pprof -o /tmp/{binary}.test ./cmd/{binary}`
     (`-o` keeps the test binary, which `go tool pprof` needs, out of the module).
     A benchmark on a smaller input of the same code path is acceptable; confirm the gain
     end to end on the timing workload.
   - Service: fetch from a loaded instance,
     `curl -o cpu1.pprof "http://localhost:6060/debug/pprof/profile?seconds=30"`.
2. **Merge and install**:

   ```bash
   go tool pprof -proto cpu1.pprof cpu2.pprof cpu3.pprof > merged.pprof
   cp merged.pprof cmd/{binary}/default.pgo
   ```

3. **Rebuild and confirm PGO applied**:

   ```bash
   go build -o bin/{binary}-pgo ./cmd/{binary}
   go version -m bin/{binary}-pgo | grep pgo
   ```

   Compare with `go build -pgo=off` on the same workload. Typical gains are single-digit
   to low-double-digit percent; a profile that does not represent real use can
   regress. Repeat each timing at least 3 times and take the median. Keep the profile only
   if the PGO binary is at least 2% faster than `-pgo=off` outside the run-to-run noise;
   otherwise delete `default.pgo`. Commit a kept `default.pgo` with the source, since it
   is a build input.
4. **Re-verify**: run the A/B parity harness against the PGO binary. `go test` does not
   apply `default.pgo` to test binaries, so only the built binary exercises PGO.
5. **Log the stage** only if you kept the profile; a stage logged for a binary that is not
   shipped misstates the final speedup. Otherwise write the result in the final summary:

   ```bash
   python3 "$TM" log-benchmark --telemetry "$TEL" \
     --stage pgo --label "4. Profile-Guided Optimization (default.pgo)" \
     --wall-time-ms {pgo_ms} --peak-rss-mb {pgo_rss_mb} \
     --notes "Merged CPU profiles from 3 workloads; confirmed via go version -m."
   ```

If the legacy baseline runs under 1 second or the program is I/O-bound, skip PGO, say so
in `--notes` of the previous stage, and let the infographic show three stages.
