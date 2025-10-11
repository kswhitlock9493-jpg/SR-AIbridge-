"""
SR-AIbridge v1.9.6h — Render Port Parity Runner
Programmatic uvicorn runner that binds to Render $PORT with validation
"""
import os
import sys
import uvicorn


def main():
    """Main entry point for uvicorn with Render PORT binding"""
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
    
    print(f"[BOOT] 🚀 Starting uvicorn on {host}:{port} (Render $PORT={port})")
    uvicorn.run(app_path, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()
