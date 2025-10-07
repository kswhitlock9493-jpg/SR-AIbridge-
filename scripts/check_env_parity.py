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

def fetch_render_env():
    headers = {"Authorization": f"Bearer {os.getenv('RENDER_API_KEY')}"}
    service_id = os.getenv("RENDER_SERVICE_ID")
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return {item["key"]: item["value"] for item in resp.json()}

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
    render_env = fetch_render_env()
    local_env = load_local_env()

    mismatches = []
    mismatches += compare_envs(local_env, netlify_env, ".env.production", "Netlify")
    mismatches += compare_envs(local_env, render_env, ".env.production", "Render")
    mismatches += compare_envs(netlify_env, render_env, "Netlify", "Render")

    if mismatches:
        print("\n❌ Environment parity check failed.")
        exit(1)
    else:
        print("\n✅ All environments are healthy and synchronized.")
