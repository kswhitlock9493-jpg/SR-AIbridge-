#!/usr/bin/env python3
import os, requests, sys

NETLIFY_API_KEY = os.getenv("NETLIFY_API_KEY")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID")

ESSENTIAL_ENV = {
    "PUBLIC_API_BASE": "/api",
    "VITE_API_BASE": os.getenv("BACKEND_URL", "https://bridge.sr-aibridge.com") + "/api",
    "REACT_APP_API_URL": os.getenv("BACKEND_URL", "https://bridge.sr-aibridge.com") + "/api",
    "CASCADE_MODE": "production",
    "VAULT_URL": "https://sr-aibridge.netlify.app/api/vault"
}

def repair_env():
    if not NETLIFY_API_KEY or not NETLIFY_SITE_ID:
        print("⚠️  Missing Netlify API credentials. Cannot repair automatically.")
        sys.exit(1)
    headers = {"Authorization": f"Bearer {NETLIFY_API_KEY}"}
    url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/env"
    for key, val in ESSENTIAL_ENV.items():
        res = requests.post(url, headers=headers, json={"key": key, "value": val})
        if res.status_code in [200, 201]:
            print(f"✅ Restored {key}")
        else:
            print(f"⚠️  Failed to restore {key}: {res.status_code}")
    print("🔄 Netlify environment repair complete.")

if __name__ == "__main__":
    print("🧩 Checking and repairing Netlify environment if needed…")
    repair_env()
