"""
SR-AIbridge v1.9.6i — Render Port Parity Runner with TDB
Programmatic uvicorn runner with Temporal Deploy Buffer integration
"""
import os
import sys
import uvicorn


def main():
    """Main entry point for uvicorn with Render PORT binding and TDB support"""
    app_path = os.environ.get("APP_IMPORT", "bridge_backend.main:app")
    port_str = os.environ.get("PORT")
    
    if not port_str:
        print("[BOOT] ❌ PORT not set. On Render this is injected. Aborting to avoid loop.", file=sys.stderr)
        sys.exit(1)
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"[BOOT] ❌ Invalid PORT value: {port_str!r}", file=sys.stderr)
        sys.exit(1)
    
    host = os.environ.get("HOST", "0.0.0.0")
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    
    # Set BRIDGE_PORT for internal logic
    os.environ["BRIDGE_PORT"] = str(port)
    
    # TDB status
    tdb_enabled = os.environ.get("TDB_ENABLED", "true").lower() not in ("0", "false", "no")
    tdb_status = "ENABLED" if tdb_enabled else "DISABLED"
    
    print(f"[BOOT] 🚀 Starting uvicorn on {host}:{port} (Render $PORT={port})")
    print(f"[BOOT] 🌊 Temporal Deploy Buffer: {tdb_status}")
    if tdb_enabled:
        print(f"[BOOT] ⚡ Stage 1 will respond to health checks immediately")
        print(f"[BOOT] 🔧 Stages 2-3 will complete in background")
    
    uvicorn.run(app_path, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()
