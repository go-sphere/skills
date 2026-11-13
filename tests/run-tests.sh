#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

bash "$SCRIPT_DIR/validate-plugin-shell.sh"
bash "$SCRIPT_DIR/validate-skill-references.sh"
python3 "$SCRIPT_DIR/test_delegate.py"
python3 "$SCRIPT_DIR/test_plans.py"
