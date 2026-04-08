#!/usr/bin/env bash
set -euo pipefail

PYTHON="$HOME/.local/booyaa/.venv/bin/python"
module="booyaa.ipcalc"

exec "$PYTHON" -m "$module" "$@"

trap cleanup EXIT
