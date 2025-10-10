#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-.}:$(pwd)"

# Dynamic PORT binding (Render auto-assigns, default to 8000 for local)
export PORT="${PORT:-8000}"

echo "[INIT] 🚀 Launching SR-AIbridge Runtime..."
echo "[INIT] Using PORT=${PORT}"

# Verify imports before anything else
echo "🔍 Verifying critical imports..."
python3 bridge_backend/runtime/verify_imports.py || echo "⚠️ Import verification had warnings; continuing"

# Run self-repair before anything else
python3 bridge_backend/runtime/auto_repair.py

echo "🔧 DB URL Guard"
python3 bridge_backend/runtime/db_url_guard.py

echo "⏳ Waiting for DB readiness..."
python3 bridge_backend/runtime/wait_for_db.py --timeout 120 || echo "⚠️ DB readiness skipped"

python3 bridge_backend/runtime/run_migrations.py --safe
python3 bridge_backend/runtime/egress_canary.py --timeout 6 || echo "[warn] egress canary soft-fail; continuing"

# Warm simple caches / route manifest
python3 bridge_backend/runtime/health_probe.py --warm || echo "[warn] health probe warm failed; continuing"

echo "✅ Launching Uvicorn server on PORT=${PORT}..."
# Launch app (uvicorn)
exec uvicorn bridge_backend.main:app --host 0.0.0.0 --port "${PORT}"
