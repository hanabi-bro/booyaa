#!/usr/bin/env bash
set -euo pipefail
set +o histexpand


PYTHON="$HOME/.local/booyaa/.venv/bin/python"
script="$HOME/.local/booyaa/booyaa/ftnt/fgt_backup.py"

exec "$PYTHON" "$script" "$@"

trap cleanup EXIT
