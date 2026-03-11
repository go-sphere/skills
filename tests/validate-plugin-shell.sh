#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

pass() {
  echo "[PASS] $1"
}

display_path() {
  local path="$1"
  echo "${path#"$ROOT_DIR"/}"
}

require_file() {
  local path="$1"
  [ -f "$path" ] || fail "missing file: $path"
  pass "found $(display_path "$path")"
}

require_contains() {
  local path="$1"
  local pattern="$2"
  grep -Eq "$pattern" "$path" || fail "$path does not match pattern: $pattern"
  pass "content check passed for $(display_path "$path")"
}

require_file "$ROOT_DIR/skills/using-sphere-workflow/SKILL.md"
require_contains "$ROOT_DIR/skills/using-sphere-workflow/SKILL.md" '^name:\s*using-sphere-workflow$'
require_contains "$ROOT_DIR/skills/using-sphere-workflow/SKILL.md" 'sphere-feature-workflow'
require_contains "$ROOT_DIR/skills/using-sphere-workflow/SKILL.md" 'proto-api-generator'

require_file "$ROOT_DIR/.codex/INSTALL.md"
require_contains "$ROOT_DIR/.codex/INSTALL.md" 'sphere-workflow'
require_contains "$ROOT_DIR/.codex/INSTALL.md" '~/.agents/skills/sphere-workflow'

require_file "$ROOT_DIR/.claude-plugin/plugin.json"
require_file "$ROOT_DIR/.claude-plugin/marketplace.json"
python3 - <<'PY' "$ROOT_DIR/.claude-plugin/plugin.json" "$ROOT_DIR/.claude-plugin/marketplace.json"
import json
import pathlib
import sys

plugin = json.loads(pathlib.Path(sys.argv[1]).read_text())
marketplace = json.loads(pathlib.Path(sys.argv[2]).read_text())

assert plugin["name"] == "sphere-workflow"
assert "go-sphere" in plugin["description"].lower()
assert "claude-code" in plugin["keywords"]
assert marketplace["name"] == "sphere-workflow-marketplace"
assert marketplace["plugins"][0]["name"] == "sphere-workflow"
PY
pass "Claude plugin manifests are valid JSON and use the public sphere-workflow marketplace name"

require_file "$ROOT_DIR/.cursor-plugin/plugin.json"
python3 - <<'PY' "$ROOT_DIR/.cursor-plugin/plugin.json"
import json
import pathlib
import sys

plugin = json.loads(pathlib.Path(sys.argv[1]).read_text())

assert plugin["name"] == "sphere-workflow"
assert plugin["displayName"] == "sphere-workflow"
assert plugin["skills"] == "./skills/"
assert plugin["hooks"] == "./hooks/hooks.json"
PY
pass "Cursor plugin manifest is valid JSON and points to local skills and hooks"

require_file "$ROOT_DIR/.opencode/INSTALL.md"
require_contains "$ROOT_DIR/.opencode/INSTALL.md" 'sphere-workflow'
require_contains "$ROOT_DIR/.opencode/INSTALL.md" '\.opencode/plugins/sphere-workflow\.js'

require_file "$ROOT_DIR/.opencode/plugins/sphere-workflow.js"
plugin_url="file://$ROOT_DIR/.opencode/plugins/sphere-workflow.js"
node --input-type=module -e "import(process.argv[1]).catch((error) => { console.error(error); process.exit(1); })" "$plugin_url" >/dev/null 2>&1 || fail "OpenCode plugin has syntax errors"
pass "OpenCode plugin syntax is valid"

require_file "$ROOT_DIR/hooks/hooks.json"
require_contains "$ROOT_DIR/hooks/hooks.json" 'session-start'
require_file "$ROOT_DIR/hooks/run-hook.cmd"
require_file "$ROOT_DIR/hooks/session-start"

hook_output="$(bash "$ROOT_DIR/hooks/session-start")"
export HOOK_OUTPUT="$hook_output"
python3 - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["HOOK_OUTPUT"])
ctx = payload.get("additional_context", "")
hook_ctx = payload.get("hookSpecificOutput", {}).get("additionalContext", "")

if "using-sphere-workflow" not in ctx:
    sys.exit("additional_context missing using-sphere-workflow bootstrap content")
if "using-sphere-workflow" not in hook_ctx:
    sys.exit("hookSpecificOutput.additionalContext missing using-sphere-workflow bootstrap content")
PY
pass "Claude hook bootstrap output is valid JSON and includes using-sphere-workflow"

require_file "$ROOT_DIR/README.md"
require_contains "$ROOT_DIR/README.md" '^# sphere-workflow$'
require_contains "$ROOT_DIR/README.md" 'npx skills add https://github.com/go-sphere/skills'
require_contains "$ROOT_DIR/README.md" 'OpenCode'
require_contains "$ROOT_DIR/README.md" 'Codex'
require_contains "$ROOT_DIR/README.md" 'Claude'
require_contains "$ROOT_DIR/README.md" 'Cursor'
require_contains "$ROOT_DIR/README.md" '/plugin marketplace add tbxark/skills'
require_contains "$ROOT_DIR/README.md" '/plugin install sphere-workflow@sphere-workflow-marketplace'
require_contains "$ROOT_DIR/README.md" '\.claude-plugin/plugin\.json'
require_contains "$ROOT_DIR/README.md" '\.cursor-plugin/plugin\.json'

echo "All plugin shell checks passed."
