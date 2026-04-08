#!/usr/bin/env bash
set -euo pipefail
set +o histexpand

PYTHON="$HOME/.local/booyaa/.venv/bin/python"
script="$HOME/.local/booyaa/booyaa/mping/mping.py"

exec "$PYTHON" "$script" "$@"

trap cleanup EXIT
