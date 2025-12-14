# SR-AIBRIDGE: Environment Sync & Security Setup

## Render (Backend)
Use `.env.render` for backend services. Includes:
- `DATABASE_URL`
- `FEDERATION_SYNC_KEY`
- `RENDER_API_KEY`

## Netlify (Frontend)
Use `.env.netlify` for UI builds only. Includes:
- `PUBLIC_API_BASE`
- `CASCADE_MODE`
- `VAULT_URL`
- `VITE_API_BASE`

## Diagnostic Behavior
Render runs `scripts/deploy_diagnose.py` automatically on startup:
- Checks database, vault, cascade, and federation
- Summarizes health logs
- Optionally sends results to your webhook
