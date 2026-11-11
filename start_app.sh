#!/bin/bash
# MAPIMS Health Assessment System Linux startup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

export PORT="${PORT:-5001}"
export FLASK_ENV="${FLASK_ENV:-development}"

echo "Starting MAPIMS Health Assessment System on port $PORT..."
python app.py

