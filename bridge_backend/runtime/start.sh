#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1
export PORT="${PORT:-10000}"
export LOG_LEVEL="${LOG_LEVEL:-info}"
export ENVIRONMENT="${ENVIRONMENT:-production}"

echo "[start] python=$(python3 --version)  PORT=$PORT  ENV=$ENVIRONMENT"

python3 bridge_backend/runtime/wait_for_db.py --timeout 120
python3 bridge_backend/runtime/run_migrations.py --safe
python3 bridge_backend/runtime/egress_canary.py --timeout 6 || echo "[warn] egress canary soft-fail; continuing"

# Warm simple caches / route manifest
python3 bridge_backend/runtime/health_probe.py --warm || echo "[warn] health probe warm failed; continuing"

# Launch app (uvicorn)
exec uvicorn bridge_backend.main:app --host 0.0.0.0 --port "$PORT" --log-level "$LOG_LEVEL"
