# Stage 0: Acquire, Resolve Latest Go, Baseline

Parameters, the latest-Go lookup, repository layout, and the baseline capture.
Recipes use `TM` and `TEL` as defined in SKILL.md step 1; set them again in every shell call.

## Parameters

| Parameter | Placeholder | Resolution |
|:--|:--|:--|
| Source input | `{codebase_path}` or `{github_url}` | GitHub URL or local path |
| Legacy language | `{legacy_language}` | Detect from extensions and build files: `CMakeLists.txt`, `Makefile`, `pom.xml`, `build.gradle`, `pyproject.toml`, `package.json`, `Cargo.toml`, `*.csproj`, `*.f90` |
| Baseline run command | `{baseline_run_command}` | `README.md`, `.github/workflows/*.yml`, `Makefile`, or test scripts |
| Go module path | `{module_path}` | Ask the user, or derive `github.com/{owner}/{repo}`; keep it unchanged when the project is already published |
| Telemetry ledger | `{workspace_dir}/migration_telemetry.json` | Created by `telemetry.py init` |

## Acquire and choose the layout

1. For a GitHub URL, run `git clone {github_url} ~/go_migrations/{repo_name}`, or clone
   into the current workspace when the user asks.
2. Put the Go port in a new `{repo_name}-go` module next to the source unless the user
   asks for in-place replacement. The original must stay runnable for A/B comparison.

## Resolve the latest stable Go

1. Run `go version` and `go env GOTOOLCHAIN`.
2. Fetch the newest stable release:

   ```bash
   curl -s 'https://go.dev/dl/?mode=json' | python3 -c "import json,sys; print(next(r['version'] for r in json.load(sys.stdin) if r['stable']))"
   ```

3. If the local toolchain is older, tell the user and offer one of: upgrade Go
   (`brew upgrade go` or the installer from `https://go.dev/dl/`), or set
   `GOTOOLCHAIN=auto` so the `go` command downloads the newer toolchain. When
   `GOTOOLCHAIN` is `local` the command never downloads, so the first option is the
   only one. Do not target an older release without the user's approval.
4. Record the resolved version (for example `go1.27.3`). Step 3 writes it to the
   `go` directive of `go.mod`.
5. Read the release notes for every release newer than your training knowledge, and at
   least the last two: `curl -s https://go.dev/doc/go1.N | python3 -c "import re,sys; print(re.sub(r'<[^>]+>', '', sys.stdin.read()))"`.
   Note new standard-library packages and language features the port can use, and
   removed or deprecated APIs to avoid.

## Initialize telemetry and census the legacy code (`discovery`)

```bash
python3 "$TM" init --telemetry "$TEL" \
  --project-name "{project_name}" --legacy-lang "{legacy_language}" \
  --go-version "$(go env GOVERSION)"
python3 "$TM" start-bucket --telemetry "$TEL" --bucket discovery
python3 "$TM" scan-codebase --telemetry "$TEL" \
  --phase before --dir "{legacy_src_dir}"
```

`scan-codebase` skips `.git`, `vendor`, `testdata`, build output, and files marked
`Code generated ... DO NOT EDIT`. Its comment % counts comment-only lines and trailing
`//` comments; trailing `/* */` comments are not counted.

## Confirm, build, and capture the baseline

1. Show the user the resolved build command, `{baseline_run_command}`, and working
   directory. Wait for confirmation when the code came from an external repository.
2. Build the legacy project in release mode (`-O3` or `Release`), even when a prebuilt
   binary exists, so the baseline and the golden files come from the same build.
3. Write the cases file for `scripts/ab_parity.sh`: one tab-separated argv per line.
   Use at least 20 fixed cases that cover normal inputs, boundaries, empty or missing
   arguments, and invalid input, plus 100 generated cases when a run is cheap. Pin RNG
   seeds, clocks, locale (`LC_ALL=C`), and time zone (`TZ=UTC`) first.
4. Capture the golden files. Each case stores stdout, stderr, and the exit code:

   ```bash
   bash "{skill_dir}/scripts/ab_parity.sh" capture \
     --legacy ./legacy-build/{binary} --cases {workspace_dir}/cases.tsv \
     --out {workspace_dir}/golden
   ```

5. Choose a timing workload that runs 1 to 10 seconds on the legacy build; a run that
   finishes instantly cannot show a speedup. Measure wall-clock time and peak RSS with
   `/usr/bin/time -l` (macOS, prints bytes: divide by 1048576) or `/usr/bin/time -v`
   (Linux, prints KB: divide by 1024), then log it in megabytes:

```bash
python3 "$TM" log-benchmark --telemetry "$TEL" \
  --stage legacy_baseline --label "1. Legacy {legacy_language} Baseline" \
  --wall-time-ms {legacy_ms} --peak-rss-mb {legacy_rss_mb} \
  --notes "Original implementation, release build."
```
