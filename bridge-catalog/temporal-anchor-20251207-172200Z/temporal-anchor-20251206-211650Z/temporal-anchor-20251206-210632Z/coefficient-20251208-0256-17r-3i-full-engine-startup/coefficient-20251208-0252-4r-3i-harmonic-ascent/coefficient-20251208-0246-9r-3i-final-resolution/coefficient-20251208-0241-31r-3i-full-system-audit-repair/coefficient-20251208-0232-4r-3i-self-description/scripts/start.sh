#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
APP="${APP:-bridge_backend.main:app}"

echo "INFO[start.sh] Launching uvicorn on ${HOST}:${PORT} -> ${APP}"
exec uvicorn "${APP}" --host "${HOST}" --port "${PORT}"
