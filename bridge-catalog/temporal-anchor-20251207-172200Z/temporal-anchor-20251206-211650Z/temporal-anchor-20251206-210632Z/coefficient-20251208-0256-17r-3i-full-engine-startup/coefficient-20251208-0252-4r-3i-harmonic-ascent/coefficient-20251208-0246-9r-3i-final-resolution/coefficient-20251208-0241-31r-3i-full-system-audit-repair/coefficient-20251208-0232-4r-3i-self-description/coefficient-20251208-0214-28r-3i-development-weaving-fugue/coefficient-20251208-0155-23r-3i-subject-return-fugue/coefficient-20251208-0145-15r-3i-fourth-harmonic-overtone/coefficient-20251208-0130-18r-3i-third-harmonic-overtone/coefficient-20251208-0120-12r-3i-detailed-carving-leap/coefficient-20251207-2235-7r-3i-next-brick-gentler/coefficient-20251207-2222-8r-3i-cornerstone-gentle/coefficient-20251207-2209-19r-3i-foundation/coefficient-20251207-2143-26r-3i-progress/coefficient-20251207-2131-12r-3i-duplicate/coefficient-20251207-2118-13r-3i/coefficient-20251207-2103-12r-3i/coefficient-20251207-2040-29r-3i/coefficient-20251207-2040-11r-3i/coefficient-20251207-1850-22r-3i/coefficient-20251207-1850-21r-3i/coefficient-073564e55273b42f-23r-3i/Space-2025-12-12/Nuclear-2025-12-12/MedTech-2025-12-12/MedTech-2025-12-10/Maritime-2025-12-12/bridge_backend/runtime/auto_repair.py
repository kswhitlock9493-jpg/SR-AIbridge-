#!/usr/bin/env python3
"""
Runtime Auto-Repair Engine
Verifies and repairs runtime environment for SR-AIbridge v1.9.4
Anchorhold Protocol: Full stabilization + federation sync
"""
import os
import sys
import asyncio
import logging

# Add repository root to path for imports (parent of bridge_backend)
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)

logging.basicConfig(level=logging.INFO)

async def verify_imports():
    """Validate critical imports are available"""
    print("🔍 Verifying critical imports...")
    try:
        from bridge_backend.runtime.verify_imports import check_critical_imports
        results = check_critical_imports()
        failed = [m for m, s in results.items() if "❌" in s]
        if failed:
            print(f"⚠️  Import validation failed for: {', '.join(failed)}")
            return False
        print("✅ All critical imports validated.")
        return True
    except Exception as e:
        print(f"⚠️  Import validation error: {e}")
        return False

async def verify_runtime():
    """Check runtime environment consistency"""
    print("🔍 Checking runtime environment consistency...")
    await asyncio.sleep(1)
    required = ["DATABASE_URL", "PYTHON_VERSION", "PORT"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"⚠️  Missing env vars: {', '.join(missing)}")
        return False
    print("✅ All core environment variables found.")
    return True

async def repair_runtime():
    """Attempt to repair runtime environment"""
    print("🩺 SR-AIbridge v1.9.5 — Unified Runtime & Autonomic Homeostasis")
    print("⚓ Auto-Repair + Schema Sync + Heartbeat Init + Parity Alignment")
    
    # Check imports first
    import_ok = await verify_imports()
    if not import_ok:
        print("⚠️  Import verification incomplete - continuing with caution")
    
    ok = await verify_runtime()
    if not ok:
        print("🛠️ Attempting self-repair...")
        os.environ.setdefault("PYTHON_VERSION", "3.11.9")
        # Dynamic port binding - defaults to 8000 for local, Render sets PORT
        os.environ.setdefault("PORT", "8000")
        if not os.getenv("DATABASE_URL"):
            os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./bridge_auto_repair.db"
        print("✅ Runtime environment repaired successfully.")
    
    # CORS validation
    cors_origins = os.getenv("ALLOWED_ORIGINS", "")
    if cors_origins:
        print(f"🌐 CORS Origins: {cors_origins}")
    else:
        print("⚠️  No CORS origins configured, using defaults")
    
    print("🩺 Verification complete. Proceeding to app bootstrap.")

if __name__ == "__main__":
    asyncio.run(repair_runtime())

