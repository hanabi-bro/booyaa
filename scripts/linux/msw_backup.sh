#!/usr/bin/env bash
set -euo pipefail

PYTHON="$HOME/.local/booyaa/.venv/bin/python"
script="$HOME/.local/booyaa/msw_backup.py"

exec "$PYTHON" "$script" "$@"
