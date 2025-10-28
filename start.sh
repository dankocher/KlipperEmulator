#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate

# Variables por defecto (puedes cambiarlas)
export HOST=127.0.0.1
export PORT=8000

python -m uvicorn app.main:app --reload --host $HOST --port $PORT
