#!/usr/bin/env python3
import os, requests, time

# === ENVIRONMENT CONFIG ===
RENDER_API_KEY = os.getenv("RENDER_API_KEY")
NETLIFY_API_KEY = os.getenv("NETLIFY_API_KEY")
RENDER_SERVICE_ID = os.getenv("RENDER_SERVICE_ID")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID")
DIAGNOSE_WEBHOOK_URL = os.getenv("DIAGNOSE_WEBHOOK_URL")

KEYWORDS = [
    "Database connection verified", "vault", "cascade", "autonomy",
    "federation", "connection failed", "error", "traceback"
]

# === FETCH LOGS ===
def fetch_render_logs():
    if not RENDER_API_KEY or not RENDER_SERVICE_ID:
        return []
    url = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
    headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        logs = []
        for deploy in res.json()[:3]:
            log_url = deploy.get("logUrl")
            if log_url:
                logs.append(requests.get(log_url, headers=headers, timeout=10).text)
        return logs
    except Exception as e:
        return [f"[Render log fetch error: {e}]"]

def fetch_netlify_logs():
    if not NETLIFY_API_KEY or not NETLIFY_SITE_ID:
        return []
    url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"
    headers = {"Authorization": f"Bearer {NETLIFY_API_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        logs = []
        for deploy in res.json()[:3]:
            deploy_id = deploy.get("id")
            if deploy_id:
                log_url = f"https://api.netlify.com/api/v1/deploys/{deploy_id}/log"
                logs.append(requests.get(log_url, headers=headers, timeout=10).text)
        return logs
    except Exception as e:
        return [f"[Netlify log fetch error: {e}]"]

# === FILTER / SUMMARIZE ===
def highlight_logs(raw_logs):
    matches = []
    for text in raw_logs:
        for line in text.splitlines():
            if any(k.lower() in line.lower() for k in KEYWORDS):
                matches.append(line.strip())
    if not matches:
        return "No relevant Bridge entries found."
    return "\n".join(matches)

# === OPTIONAL WEBHOOK FORWARD ===
def send_webhook(summary):
    if not DIAGNOSE_WEBHOOK_URL:
        return
    payload = {
        "username": "Bridge Diagnostics",
        "content": f"🧠 **SR-AIbridge Deploy Summary**\n```\n{summary}\n```"
    }
    try:
        requests.post(DIAGNOSE_WEBHOOK_URL, json=payload, timeout=10)
        print("📡 Diagnostic summary sent via webhook.")
    except Exception as e:
        print(f"⚠️ Webhook send failed: {e}")

# === MAIN EXECUTION ===
def main():
    print("🔍 Fetching logs from Render and Netlify...")
    render_logs = fetch_render_logs()
    netlify_logs = fetch_netlify_logs()
    all_logs = render_logs + netlify_logs
    summary = highlight_logs(all_logs)
    print("\n🧠 SR-AIbridge Deploy Diagnostics Summary:")
    print("=" * 55)
    print(summary)
    print("=" * 55)
    print("✅ Diagnostic pass complete.")
    send_webhook(summary)

if __name__ == "__main__":
    main()
