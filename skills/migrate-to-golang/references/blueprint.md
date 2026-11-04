# Stage 1 Architectural Blueprint

What the six-section blueprint contains and how to log opportunities and latent bugs.

Recipes use `TM` and `TEL` as defined in SKILL.md step 1; set them again in every shell call.

## The six sections

1. **Codebase audit, legacy census & latent bugs**
   - The automated census from `migration_telemetry.json` (total LOC, comment %, max
     file LOC, nesting depth, hazards).
   - **Latent bugs and undefined behavior** found in the original, each with an exact
     file and line (uninitialized memory, unchecked division, signed overflow,
     off-by-one reads, data races, leaked handles). State for each whether the Go port
     preserves the bug for parity or fixes it, and why.
2. **Target Go architecture & module graph**
   - Module path, resolved Go release, package layout (`cmd/`, `internal/`), and the
     reason for each package boundary.
   - **Mapping table**:

     | Legacy file & symbol (`{legacy_language}`) | Target Go package & type/func | Transformation |
     |:--|:--|:--|
     | `src/sim/Engine.java::Engine` | `internal/sim/engine.go::Engine` | Class hierarchy to struct + interface; exceptions to errors |

   - **Dependency map**: each legacy dependency to its Go replacement, preferring the
     standard library; for third-party Go modules, note maintenance status and license.
3. **API ergonomics & call-site modernization**: concrete Before (`{legacy_language}`)
   and After (Go) examples taken from real call sites.
4. **Test, fuzz & parity strategy**: which legacy tests are translated, where table-
   driven tests, `Example` functions, and fuzz targets go, the `N` deterministic cases,
   and the comparison rule and tolerance for the A/B harness.
5. **Benchmark & PGO plan**: the four stages, the representative workload, how peak
   RSS is measured, and which profiling method collects `default.pgo` (see [benchmarks-and-pgo.md](benchmarks-and-pgo.md)).
6. **Phased execution roadmap**: ordered milestones with a verification command each,
   plus **open questions** for the user.

## Log opportunities and latent bugs

```bash
python3 "$TM" start-bucket --telemetry "$TEL" --bucket blueprint
python3 "$TM" log-opportunity --telemetry "$TEL" \
  --category latent_bug --title "Unchecked divisor on empty window" \
  --file "src/stats.cpp:142" \
  --description "mean() divides by window.size() without a zero check."
```

Valid `--category` values: `latent_bug`, `performance`, `safety`, `hygiene`,
`architecture`. Entries cannot be edited or removed, so choose the category before logging.
The census counts `latent_bug` entries as `latent_bugs_found`.
