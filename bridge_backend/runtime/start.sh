#!/usr/bin/env bash
set -e

echo "🚀 Starting Bridge Runtime Bootstrap..."

# Run self-repair before anything else
python3 bridge_backend/runtime/auto_repair.py

echo "⏳ Waiting for DB readiness..."
python3 bridge_backend/runtime/wait_for_db.py --timeout 120 || echo "⚠️ DB readiness skipped"

python3 bridge_backend/runtime/run_migrations.py --safe
python3 bridge_backend/runtime/egress_canary.py --timeout 6 || echo "[warn] egress canary soft-fail; continuing"

# Warm simple caches / route manifest
python3 bridge_backend/runtime/health_probe.py --warm || echo "[warn] health probe warm failed; continuing"

echo "✅ Launching Uvicorn server..."
# Launch app (uvicorn)
exec uvicorn bridge_backend.main:app --host 0.0.0.0 --port "${PORT:-10000}"
