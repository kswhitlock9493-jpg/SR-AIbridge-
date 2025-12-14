#!/usr/bin/env python3
"""
Database URL Guard & Normalizer
Validates and normalizes DATABASE_URL before engine initialization
Prevents common foot-guns:
- Malformed URLs with %40 glued to host
- Missing scheme or netloc
- Invalid port parsing
- Unsafe fallback to SQLite
"""
import os
import sys
import re
from urllib.parse import urlsplit


def normalize(url: str) -> str:
    """Validate and normalize DATABASE_URL"""
    # Read environment variable dynamically for testing
    allow_sqlite = os.getenv("DB_FALLBACK_TO_SQLITE", "false").lower() == "true"
    
    if not url:
        if allow_sqlite:
            print("⚠️  Using SQLite fallback.")
            return "sqlite+aiosqlite:///./bridge_local.db"
        print("❌ DATABASE_URL required.  Set DB_FALLBACK_TO_SQLITE=true to bypass.")
        sys.exit(12)

    # Check for %40 glued to host (common Render misconfiguration)
    if re.search(r":[^/@:%]+%40[^/]+:\d+/", url):
        print("❌ DATABASE_URL password glued to host via %40.")
        print("   Correct: postgresql+asyncpg://user:pass@host:5432/dbname")
        sys.exit(13)

    # Normalize postgres:// to postgresql+asyncpg://
    url = url.replace("postgres://", "postgresql+asyncpg://").replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    # Validate URL structure
    parts = urlsplit(url)
    if not parts.scheme:
        print("❌ Malformed DATABASE_URL.")
        sys.exit(14)

    # SQLite URLs are valid with just scheme and path
    if parts.scheme.startswith("sqlite"):
        print(f"✅ DATABASE_URL OK → SQLite")
        return url
    
    # For non-SQLite databases, validate netloc exists
    if not parts.netloc:
        print("❌ Malformed DATABASE_URL.")
        sys.exit(14)

    # Validate PostgreSQL URLs have required components
    # Check for @ and port after the @
    if "@" not in parts.netloc:
        print("❌ DATABASE_URL missing '@'.")
        sys.exit(15)
    
    # Split by @ and check if the host part has a port
    # Handle multiple @ in password by splitting from the right
    host_part = parts.netloc.rsplit("@", 1)[-1]
    if ":" not in host_part:
        print("❌ DATABASE_URL missing ':port'.")
        sys.exit(15)
    
    print(f"✅ DATABASE_URL OK → {parts.hostname}:{parts.port}")
    return url

if __name__ == "__main__":
    os.environ["DATABASE_URL"] = normalize(os.getenv("DATABASE_URL", ""))
