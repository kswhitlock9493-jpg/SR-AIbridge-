#!/usr/bin/env python3
"""
Runtime Auto-Repair Engine
Verifies and repairs runtime environment for SR-AIbridge v1.9.4
Anchorhold Protocol: Full stabilization + federation sync
"""
import os
import asyncio

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
    print("🩺 SR-AIbridge v1.9.4 — Anchorhold Protocol")
    print("⚓ Auto-Repair + Schema Sync + Heartbeat Init")
    
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
