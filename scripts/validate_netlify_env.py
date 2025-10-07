#!/usr/bin/env python3
import os, sys
import subprocess

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

def verify_vite_installation():
    # Change to the bridge-frontend directory since that's where the build happens
    original_dir = os.getcwd()
    try:
        # Determine the correct directory - if running from scripts/, go to bridge-frontend
        if os.path.basename(os.getcwd()) == 'SR-AIbridge-':
            os.chdir('bridge-frontend')
        
        result = subprocess.run(["npm", "list", "vite"], capture_output=True)
        if result.returncode == 0:
            print("✅ Vite detected in dependency tree.")
        else:
            print("⚠️ Vite not found. Installing dev dependencies...")
            subprocess.run(["npm", "install", "--include=dev"], check=True)
            print("✅ Dev dependencies installed successfully.")
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    print("🔍 Running Netlify pre-deploy validation…")
    validate_env()
    verify_vite_installation()
    sys.exit(0)
