#!/usr/bin/env python3
import os, sys

REQUIRED_ENV = [
    "PUBLIC_API_BASE",
    "VITE_API_BASE",
    "REACT_APP_API_URL",
    "CASCADE_MODE",
    "VAULT_URL"
]

def validate_env():
    missing = [v for v in REQUIRED_ENV if not os.getenv(v)]
    if missing:
        print("❌ Missing required Netlify environment variables:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    print("✅ All required environment variables present and valid.")
    sys.exit(0)

if __name__ == "__main__":
    print("🔍 Running Netlify pre-deploy validation…")
    validate_env()
