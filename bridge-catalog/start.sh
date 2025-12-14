#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-10000}"
echo "[BOOT] Binding uvicorn to PORT=${PORT}"
exec uvicorn bridge_backend.main:app --host 0.0.0.0 --port "${PORT}"
