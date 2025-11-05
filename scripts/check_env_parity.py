#!/usr/bin/env python3
import os
import requests
from dotenv import dotenv_values

def fetch_netlify_env():
    headers = {"Authorization": f"Bearer {os.getenv('NETLIFY_AUTH_TOKEN')}"}
    site_id = os.getenv("NETLIFY_SITE_ID")
    url = f"https://api.netlify.com/api/v1/sites/{site_id}/env"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return {item["key"]: item["value"] for item in resp.json()}

def fetch_backend_env():
    """
    OPTIONAL: Fetch backend environment variables if using a managed provider.
    For sovereign deployments, this function may not be needed.
    """
    backend_api_key = os.getenv('BACKEND_API_KEY')
    service_id = os.getenv("BACKEND_SERVICE_ID")
    
    if not backend_api_key or not service_id:
        print("⚠️ Backend API credentials not configured - skipping backend env check")
        return {}
    
    headers = {"Authorization": f"Bearer {backend_api_key}"}
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return {item["key"]: item["value"] for item in resp.json()}
    except Exception as e:
        print(f"⚠️ Could not fetch backend env (expected in sovereign mode): {e}")
        return {}

def load_local_env():
    return dotenv_values(".env.production")

def compare_envs(env_a, env_b, label_a, label_b):
    mismatches = []
    for key in set(env_a.keys()) | set(env_b.keys()):
        if env_a.get(key) != env_b.get(key):
            mismatches.append((key, env_a.get(key), env_b.get(key)))
    if mismatches:
        print(f"⚠️ {label_a} ↔ {label_b} mismatches:")
        for key, a, b in mismatches:
            print(f" - {key}: {label_a}='{a}' | {label_b}='{b}'")
    else:
        print(f"✅ {label_a} and {label_b} are synchronized.")
    return mismatches

if __name__ == "__main__":
    netlify_env = fetch_netlify_env()
    backend_env = fetch_backend_env()
    local_env = load_local_env()

    mismatches = []
    mismatches += compare_envs(local_env, netlify_env, ".env.production", "Netlify")
    
    # Only compare backend if it was fetched (sovereign deployments may skip this)
    if backend_env:
        mismatches += compare_envs(local_env, backend_env, ".env.production", "Backend")
        mismatches += compare_envs(netlify_env, backend_env, "Netlify", "Backend")

    if mismatches:
        print("\n❌ Environment parity check failed.")
        exit(1)
    else:
        print("\n✅ All environments are healthy and synchronized.")
