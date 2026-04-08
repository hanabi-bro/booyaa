#!/usr/bin/env bash
set -euo pipefail

PYTHON="$HOME/.local/booyaa/.venv/bin/python"
script="$HOME/.local/booyaa/mping.py"

exec "$PYTHON" "$script" "$@"
