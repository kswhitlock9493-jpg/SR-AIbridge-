#!/usr/bin/env python3
"""
Bridge Doctor CLI - Self-Diagnostic Tool
Runs comprehensive system checks and repairs
"""
import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from bridge_backend.runtime.heartbeat import ensure_httpx


def run_bridge_diagnostics():
    """
    Run comprehensive Bridge diagnostics
    Checks dependencies, database, network configuration
    """
    print("\n🔍 Running Bridge Doctor Diagnostics...\n")
    
    # Test 1: Check httpx dependency
    print("📦 Checking dependencies...")
    httpx_ok = ensure_httpx()
    if httpx_ok:
        print("  ✅ httpx: Available")
    else:
        print("  ❌ httpx: Failed to install")
    
    # Test 2: Verify database schema
    print("\n🗄️  Checking database schema...")
    try:
        from bridge_backend.models import Base
        from bridge_backend.db import engine
        
        # Synchronous schema creation for CLI tool
        Base.metadata.create_all(bind=engine)
        print("  ✅ Database schema verified and synced")
    except Exception as e:
        print(f"  ❌ Schema verification failed: {e}")
    
    # Test 3: Check network configuration
    print("\n🌐 Checking network configuration...")
    port = os.getenv("PORT", "8000")
    print(f"  📍 Network Port: {port}")
    
    database_url = os.getenv("DATABASE_URL", "Not set")
    if database_url != "Not set":
        # Mask password in URL for security
        if "@" in database_url:
            parts = database_url.split("@")
            masked_url = parts[0].rsplit(":", 1)[0] + ":****@" + parts[1]
        else:
            masked_url = database_url
        print(f"  📍 Database URL: {masked_url}")
    else:
        print(f"  ⚠️  Database URL: {database_url}")
    
    # Test 4: Check CORS configuration
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "Not set")
    print(f"  📍 CORS Origins: {allowed_origins}")
    
    print("\n🩺 Diagnostics complete.\n")


if __name__ == "__main__":
    run_bridge_diagnostics()
