# Final Census, Story and Infographic

The closing sequence (step 8): release hygiene, census, spotlight, narrative, render.

Recipes use `TM` and `TEL` as defined in SKILL.md step 1; set them again in every shell call.

## Closing sequence

1. **Release hygiene**: `go fix ./...`, `go mod tidy`, `govulncheck ./...`, then re-run
   the gate commands in [verification-crucible.md](verification-crucible.md) on the final tree.
2. **Scan the Go source** (test files and generated files are excluded from LOC;
   `Example` functions are counted):

   ```bash
   python3 "$TM" scan-codebase --telemetry "$TEL" \
     --phase after --dir "{go_module_dir}" \
     --coverage-pct {final_coverage_pct} --lint-issues {final_lint_issues}
   ```

3. **Before/after spotlight** — pick the transformation that best shows what changed:

   ```bash
   python3 "$TM" log-spotlight --telemetry "$TEL" \
     --explanation "How the callback-heavy legacy loop became a context-aware Go pipeline." \
     --legacy-file "{legacy_file_path}" --legacy-code-file "{legacy_snippet_file}" \
     --go-file "{go_file_path}" --go-code-file "{go_snippet_file}"
   ```

4. **First-person narrative chapters** ("I found...", "On my first test run, X% failed...",
   "I fixed...", "At the end I ran PGO..."). Use only numbers present in the telemetry:

   ```bash
   python3 "$TM" set-story --telemetry "$TEL" \
     --headline "“I inherited a {legacy_lang} codebase, uncovered {N} latent bugs, healed through {X}% initial test failures, and delivered a {S}x faster Go port.”" \
     --intro "{2-3 sentence executive summary}" \
     --ch1-narrative "{What I found: census, opportunities, latent bugs}" \
     --ch2-narrative "{How I reorganized the architecture and documentation}" \
     --ch3-narrative "{The test crucible: initial failure %, diagnoses, fixes}" \
     --ch4-narrative "{Proving parity across N cases}" \
     --ch5-narrative "{The speedup staircase through PGO}"
   ```

5. **End the final bucket and render**:

   ```bash
   python3 "$TM" end-bucket --telemetry "$TEL" --bucket pgo_bench
   python3 "$TM" render-infographic --telemetry "$TEL" \
     --out "{output_dir}/migration_infographic.html" \
     --scope-summary "{short_summary_of_ported_scope}"
   ```
