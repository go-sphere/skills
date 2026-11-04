#!/usr/bin/env bash
# A/B differential harness: records the legacy program's stdout, stderr and exit
# code per case, then replays the same cases against the Go program.
#
#   ab_parity.sh capture --legacy BIN --cases FILE --out DIR
#   ab_parity.sh compare --go BIN --cases FILE --golden DIR
#
# FILE holds one case per line: tab-separated argv. Blank lines and lines
# starting with '#' are skipped; a line containing only '-' means no arguments.
# Exit status: 0 when every case is byte-identical, 1 on any difference, 2 on
# usage errors. Run the programs from the directory they expect (set the same
# env, e.g. LC_ALL=C TZ=UTC, for both).
set -uo pipefail

die() { echo "ab_parity: $*" >&2; exit 2; }

mode="${1:-}"; [ -n "$mode" ] && shift
bin="" cases="" dir=""
while [ $# -gt 0 ]; do
  case "$1" in
    --legacy|--go) bin="$2"; shift 2 ;;
    --cases) cases="$2"; shift 2 ;;
    --out|--golden) dir="$2"; shift 2 ;;
    *) die "unknown argument: $1" ;;
  esac
done
[ -n "$bin" ] && [ -x "$bin" ] || die "program missing or not executable: '$bin'"
[ -f "$cases" ] || die "cases file not found: '$cases'"
[ -n "$dir" ] || die "--out/--golden directory required"

each_case() { # each_case CALLBACK; callback gets index and argv
  local n=0 line argv
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|'#'*) continue ;; esac
    n=$((n + 1))
    if [ "$line" = "-" ]; then argv=(); else IFS=$'\t' read -r -a argv <<<"$line"; fi
    "$1" "$(printf '%04d' "$n")" "${argv[@]+"${argv[@]}"}"
  done <"$cases"
  echo "$n"
}

case "$mode" in
  capture)
    mkdir -p "$dir" || die "cannot create $dir"
    cb() { local id="$1"; shift; "$bin" "$@" >"$dir/$id.out" 2>"$dir/$id.err" </dev/null; echo $? >"$dir/$id.rc"; }
    total=$(each_case cb | tail -n 1)
    echo "captured $total cases into $dir"
    ;;
  compare)
    [ -d "$dir" ] || die "golden directory not found: $dir"
    work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
    fails="$work/fails"; : >"$fails"
    cb() {
      local id="$1"; shift
      "$bin" "$@" >"$work/$id.out" 2>"$work/$id.err" </dev/null; echo $? >"$work/$id.rc"
      for ext in out err rc; do
        cmp -s "$dir/$id.$ext" "$work/$id.$ext" || { echo "case $id ($*): $ext differs" >>"$fails"; break; }
      done
    }
    total=$(each_case cb | tail -n 1)
    bad=$(wc -l <"$fails" | tr -d ' ')
    cat "$fails"
    echo "parity: $((total - bad))/$total identical (stdout, stderr, exit code)"
    [ "$bad" -eq 0 ]
    ;;
  *) die "usage: ab_parity.sh capture|compare ..." ;;
esac
