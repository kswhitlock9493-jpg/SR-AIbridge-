# Deploy & Diagnose Companion

The Deploy-and-Diagnose Companion automatically reviews Render and Netlify logs after every SR-AIbridge deployment.

## ✅ Features
- Fetches last 3 Render + Netlify deploy logs
- Filters Bridge-specific keywords (Vault, Cascade, Federation, etc.)
- Outputs clean diagnostic summary
- Optionally sends webhook notifications

## 🔧 Environment Variables
| Variable | Description | Required |
|-----------|-------------|-----------|
| RENDER_API_KEY | Your Render API token | ✅ |
| RENDER_SERVICE_ID | ID of the Render backend service | ✅ |
| NETLIFY_API_KEY | Netlify API key | ⚙️ optional |
| NETLIFY_SITE_ID | ID of your Netlify site | ⚙️ optional |
| AUTO_DIAGNOSE | Enable automatic diagnostics | default: true |
| DIAGNOSE_WEBHOOK_URL | Webhook to forward logs (Discord, dashboard, etc.) | optional |

## 🚀 Manual Run
```bash
python3 scripts/deploy_diagnose.py
```

## 🧩 Output Example
```
🧠 SR-AIbridge Deploy Diagnostics Summary:
=======================================================
✅ Database connection verified
🟢 Vault: Sync OK
🟢 Cascade: Stable
🟢 Federation: Linked
=======================================================
✅ Diagnostic pass complete.
```

## 🛰️ Webhook Mode
Set `DIAGNOSE_WEBHOOK_URL` to any endpoint (Discord, Slack, dashboard).
Diagnostics will auto-post after every successful deploy.
