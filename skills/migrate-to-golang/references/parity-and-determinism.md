# A/B Parity and Determinism

How to prove the Go port behaves like the original, and the Go-specific causes of divergence.

Recipes use `TM` and `TEL` as defined in SKILL.md step 1; set them again in every shell call.

## Method and Go-specific divergences

Run the legacy binary and the Go binary side by side on `N` deterministic cases (a
"case" is an RNG seed, a fixture file, or a recorded request) and diff the outputs.
A golden case is stdout, stderr, and the exit code. `N` is the case count from Stage 0:
at least 20 fixed cases, plus 100 generated ones when a run is cheap.

Run the harness against the legacy and the Go binary with the same environment:

```bash
bash "{skill_dir}/scripts/ab_parity.sh" compare \
  --go ./bin/{binary} --cases {workspace_dir}/cases.tsv --golden {workspace_dir}/golden
```

It prints each differing case and exits 1 on any difference. Also replay the golden
files in a Go test: give `main` a `run(args []string, stdout, stderr io.Writer) int`
function and table-test it against `testdata/golden`. Derive every `Example` output from
the legacy binary, never from a guess.

Default to preserving legacy input-parsing quirks (for example C `atoi` saturating and
truncating) and list each one as an open question. Fix undefined behavior by choosing the
legacy build's observed result and log it as a latent bug.
Go-specific divergences to check *first*, in rough order of how often they bite:

- **Map iteration order is randomized.** Legacy code that printed or serialized a
  hash map in insertion or sorted order needs explicit ordering:
  `for _, k := range slices.Sorted(maps.Keys(m))`.
- **Integer semantics.** Go `/` and `%` truncate toward zero (like C and Java; the
  remainder takes the dividend's sign). Python and Ruby floor. Integers wrap on
  overflow, which matches C/Java but not Python (arbitrary precision — use
  `math/big` or a wider type) or JavaScript (all numbers are float64, bit ops are
  32-bit).
- **Fused multiply-add.** The Go spec lets the compiler fuse `x*y + z` into one
  rounding; arm64, ppc64, s390x, and riscv64 do, and amd64 does with `GOAMD64=v3`.
  If a float result differs in the last bits between machines or from the legacy
  build, force separate rounding with an explicit conversion: `float64(x*y) + z`.
- **Float formatting.** `strconv.FormatFloat(x, 'g', -1, 64)` gives the shortest
  round-trip form (like Python `repr` and JavaScript), which differs from C `printf`
  `%g`. Match the legacy format explicitly.
- **Strings are bytes.** `len(s)` and `s[i]` are byte-based; `for range s` yields runes.
  Java and JavaScript index UTF-16 code units, so non-BMP characters differ. Decide
  per call site which unit the legacy behavior actually needs.
- **PRNGs.** `math/rand/v2` is not seed-compatible with glibc `rand()`, Java's LCG, or
  Mersenne Twister. Reimplement the legacy generator exactly (it is usually a few
  lines), or dump its output to a golden file and test against that.
- **`encoding/json` defaults.** It escapes `<`, `>`, `&` (disable with
  `Encoder.SetEscapeHTML(false)`), emits `null` for nil slices (use an empty slice for
  `[]`), orders struct fields as declared, and sorts map keys.
- **Process behavior.** Compare exit codes, stderr text, and signal handling, not just
  stdout.

When a case diverges, bisect: compare intermediate state at each step until the first
difference, fix the root cause, re-run. Document the tolerance (`--max-abs-error`) and
justify any non-zero value.

## Log every parity iteration (`parity`)

```bash
python3 "$TM" start-bucket --telemetry "$TEL" --bucket parity
python3 "$TM" log-parity-run --telemetry "$TEL" \
  --iteration 1 --seeds-tested 100 --seeds-passed 96 --max-abs-error "4.2e-4" \
  --divergence-cause "4 cases drifted at step 380: FMA fusion on arm64 changed accumulator rounding." \
  --fix-applied "Forced separate rounding with float64(x*y) + z."
```

`--seeds-tested` counts deterministic cases of any kind. `--max-abs-error` defaults to
`0 (exact match)` for byte-identical comparisons.
