# Diagnostics Federation (v1.6.8)

This document explains the telemetry pipeline.

## Components
- Netlify Function `/api/health`: First-party summarized health.
- Netlify Function `/api/telemetry`: Signed webhook relay for Slack/Discord/Custom.
- Bridge Badge `public/bridge_sync_badge.json`: Live sync status for shields.io.
- GitHub Action `diagnostics_federation.yml`: Runs every 30 minutes and on push.

## Environment Variables
Required (set in Netlify & GitHub Actions secrets):
- TELEMETRY_SIGNING_SECRET: HMAC secret for payload signing.
- DIAGNOSTICS_WEBHOOK_URL: Slack/Discord/custom endpoint (Netlify env).
- RENDER_HEALTH_URL, FRONTEND_HEALTH_URL, SITE_URL: Health URLs.

## Security
All telemetry POSTs require `X-Bridge-Signature: sha256=<hmac>`.

## Test Commands
- Curl health:
  ```bash
  curl -s https://<site>/.netlify/functions/health | jq
  ```
- Send a signed event:
  ```bash
  python3 bridge_backend/scripts/report_bridge_event.py
  ```
