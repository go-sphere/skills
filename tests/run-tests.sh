#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

bash "$SCRIPT_DIR/validate-skill-references.sh"
python3 -B "$SCRIPT_DIR/test_delegate.py"
python3 -B "$SCRIPT_DIR/test_plans.py"
