#!/usr/bin/env python3
"""
Database readiness checker
Waits for database to be accessible before starting the application
"""
import os
import sys
import time
import argparse

def wait_for_db(url, timeout):
    """Wait for database to become ready"""
    if not url:
        print("[wait_for_db] No DATABASE_URL provided, skipping DB wait")
        return 0
    
    # Skip for SQLite
    if url.startswith("sqlite"):
        print("[wait_for_db] Using SQLite, skipping DB wait")
        return 0
    
    # Skip for non-postgres databases
    if not url.startswith("postgres"):
        print(f"[wait_for_db] Non-PostgreSQL database detected, skipping DB wait")
        return 0
    
    try:
        import psycopg2
    except ImportError:
        print("[wait_for_db] psycopg2 not installed, skipping DB wait")
        return 0
    
    # Try to import telemetry
    try:
        from bridge_backend.runtime.telemetry import TELEMETRY
    except ImportError:
        try:
            from runtime.telemetry import TELEMETRY
        except ImportError:
            TELEMETRY = None
    
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            conn = psycopg2.connect(url)
            conn.close()
            elapsed_ms = int((time.time() - t0) * 1000)
            print("[wait_for_db] DB ready")
            if TELEMETRY:
                TELEMETRY.mark("db_ready", True, ms=elapsed_ms, note="postgres_ok")
            return 0
        except Exception as e:
            print(f"[wait_for_db] DB not ready: {e}")
            time.sleep(3)
    
    elapsed_ms = int((time.time() - t0) * 1000)
    print(f"[wait_for_db] DB not ready after {timeout}s")
    if TELEMETRY:
        TELEMETRY.mark("db_ready", False, ms=elapsed_ms, note="timeout_or_conn_error")
    return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    
    url = os.getenv("DATABASE_URL", "")
    if not url:
        print("[wait_for_db] DATABASE_URL missing, assuming SQLite")
        sys.exit(0)
    
    sys.exit(wait_for_db(url, args.timeout))
