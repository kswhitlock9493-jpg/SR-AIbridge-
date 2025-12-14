# 🌉 Bridge Deployment Infrastructure Guide

## Overview

This guide documents the Forge Dominion deployment infrastructure that enables sovereign, self-deploying bridge runtime with zero vendor lock-in.

## Architecture

```
GitHub Repository
    ↓
Bridge Deploy Workflow (.github/workflows/bridge-deploy.yml)
    ↓
Build Bridge Frontend (npm run build)
    ↓
Export Forge Runtime (bridge_backend/forge/export_runtime.py)
    ↓
Deploy to Netlify (via Netlify configuration)
    ↓
Notify Forge Dominion (webhook)
```

## Components

### 1. Netlify Configuration (`bridge-frontend/netlify.toml`)

The Netlify configuration file handles:
- **Build Process**: Compiles the bridge frontend and exports runtime context
- **Environment Linking**: Injects Sovereign Dominion Root dynamically per branch
- **API Federation**: Routes `/api/*` to the Forge Dominion Runtime
- **Webhook Notifications**: Posts deployment updates back to Sovereign Bridge

**Key Sections:**

- **Build**: Defines build command and publish directory
- **Functions**: Specifies Netlify functions directory
- **Environment**: Context-specific environment variables (production, preview, branch-deploy)
- **Redirects**: API routing to Forge Dominion
- **Plugins**: Deploy notification webhooks

### 2. GitHub Actions Workflow (`.github/workflows/bridge-deploy.yml`)

Automated deployment workflow triggered on:
- Push to `main` branch
- Manual workflow dispatch

**Workflow Steps:**

1. **Checkout Repository**: Gets latest code
2. **Setup Node.js**: Installs Node.js 20
3. **Install Frontend Dependencies**: Runs `npm ci`
4. **Build Bridge Frontend**: Compiles the UI
5. **Export Forge Runtime**: Generates runtime manifest
6. **Deploy to Netlify**: Deploys built artifacts
7. **Notify Forge Dominion**: Sends deployment confirmation

**Required Secrets:**

- `FORGE_DOMINION_ROOT`: Root dominion endpoint
- `DOMINION_SEAL`: Sovereign signature token
- `NETLIFY_AUTH_TOKEN`: Personal access token from Netlify
- `NETLIFY_SITE_ID`: Netlify site ID

### 3. Runtime Exporter (`bridge_backend/forge/export_runtime.py`)

Python script that exports runtime context for Forge Dominion handshake.

**Outputs:**
- Runtime manifest JSON file
- Deployment metadata
- Cryptographic signature

**Generated Manifest:**
```json
{
  "forge_id": "Σ–AIBR–FJ–553–COD–EX",
  "timestamp": "2025-11-04T11:34:03.133248+00:00",
  "environment": {
    "branch": "main",
    "run_id": "12345",
    "dominion_root": "dominion://sovereign.bridge"
  },
  "signature": "...",
  "status": "exported",
  "version": "5.5.3",
  "deployment": {
    "type": "sovereign",
    "platform": "netlify",
    "mode": "production"
  }
}
```

### 4. Dominion Seal (`assets/dominion-seal.svg`)

Custom animated SVG badge featuring:
- Forge ID: **Σ–AIBR–FJ–553–COD–EX**
- Rotating hex patterns
- Pulsing glow effects
- Version badge
- Sovereign branding

## Setup Instructions

### Step 1: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

```bash
# Navigate to: Settings → Secrets and variables → Actions → New repository secret

FORGE_DOMINION_ROOT="dominion://sovereign.bridge"
DOMINION_SEAL="your-sovereign-signature-token"
NETLIFY_AUTH_TOKEN="your-netlify-token"
NETLIFY_SITE_ID="your-site-id"
```

**How to get these values:**

1. **FORGE_DOMINION_ROOT**: Your sovereign dominion endpoint
2. **DOMINION_SEAL**: Generate with: `python3 -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("="))'`
3. **NETLIFY_AUTH_TOKEN**: Generate at [Netlify User Settings → Applications](https://app.netlify.com/user/applications)
4. **NETLIFY_SITE_ID**: Found in Netlify Site Settings → General → Site ID

### Step 2: Update README Badge

Replace `YOUR_NETLIFY_SITE_ID` in README.md with your actual Netlify Site ID:

```markdown
<img src="https://img.shields.io/netlify/YOUR_NETLIFY_SITE_ID?label=Bridge%20Frontend&logo=netlify&style=for-the-badge&color=00ffaa" />
```

### Step 3: Enable Workflow

The workflow is automatically enabled and will trigger on:
- Every push to `main` branch
- Manual trigger via GitHub Actions UI

### Step 4: Deploy

```bash
# Make a commit to main branch
git add .
git commit -m "feat: enable bridge deployment infrastructure"
git push origin main

# Or trigger manually in GitHub Actions UI
```

## Deployment Flow

1. **Code Push**: Developer pushes to `main` branch
2. **Workflow Trigger**: `bridge-deploy.yml` starts automatically
3. **Build Phase**: Frontend built with `npm run build`
4. **Runtime Export**: Forge runtime context generated
5. **Netlify Deploy**: Built assets deployed to Netlify
6. **Notification**: Forge Dominion notified of deployment
7. **Status Update**: GitHub Actions badge updates

## Status Badges

### Forge Dominion Badge
```markdown
![FORGE DOMINION](https://img.shields.io/badge/FORGE%20DOMINION-LIVE-%2300ffaa?style=for-the-badge&logo=netlify&logoColor=white)
```
Always shows "LIVE" — acts as your Sovereign seal badge.

### Bridge Deploy Badge
```markdown
![Bridge Deploy](https://img.shields.io/github/actions/workflow/status/kswhitlock9493-jpg/SR-AIbridge-/bridge-deploy.yml?label=Bridge%20Deploy&logo=githubactions&style=for-the-badge&color=00ffaa)
```
Displays live GitHub Actions workflow status.

### Bridge Frontend Badge
```markdown
![Bridge Frontend](https://img.shields.io/netlify/YOUR_NETLIFY_SITE_ID?label=Bridge%20Frontend&logo=netlify&style=for-the-badge&color=00ffaa)
```
Shows Netlify deployment status.

## Troubleshooting

### Workflow Fails at "Export Forge Runtime"

**Solution**: Ensure Python 3 is available in the workflow:
```yaml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.x'
```

### Netlify Deployment Fails

**Possible Causes:**
1. Missing `NETLIFY_AUTH_TOKEN` or `NETLIFY_SITE_ID` secrets
2. Incorrect build command in `netlify.toml`
3. Build directory doesn't exist

**Solution**: Verify secrets and build output directory.

### Runtime Manifest Not Generated

**Check:**
1. Script has execute permissions: `chmod +x bridge_backend/forge/export_runtime.py`
2. Script runs successfully: `python3 bridge_backend/forge/export_runtime.py`
3. Output directory exists

### Badge Not Updating

**For GitHub Actions Badge:**
- Wait a few minutes for cache to clear
- Workflow must complete at least once

**For Netlify Badge:**
- Verify `NETLIFY_SITE_ID` is correct
- Check Netlify deployment status

## Advanced Configuration

### Custom Webhook Endpoint

Update the Netlify notification webhook in `netlify.toml`:

```toml
[[plugins.inputs]]
  webhook_url = "https://your-custom-endpoint.com/api/forge/deploy"
  secret = "${DOMINION_SEAL}"
```

### Multiple Environments

Configure different environments in `netlify.toml`:

```toml
[context.staging.environment]
  FORGE_DOMINION_ROOT = "dominion://sovereign.bridge?env=staging"

[context.development.environment]
  FORGE_DOMINION_ROOT = "dominion://sovereign.bridge?env=dev"
```

### Custom Build Command

Modify the build command in `netlify.toml`:

```toml
[build]
  command = "npm run build && npm run custom-script && python3 ../bridge_backend/forge/export_runtime.py"
```

## Security Considerations

1. **Secrets Management**: All sensitive values stored as GitHub Secrets
2. **Ephemeral Tokens**: Environment variables dynamically injected at build time
3. **Signature Verification**: Runtime manifest includes cryptographic signature
4. **HTTPS Only**: All deployments use secure connections

## Maintenance

### Updating Forge ID

Update the Forge ID in `bridge_backend/forge/export_runtime.py`:

```python
runtime_context = {
    "forge_id": "Σ–AIBR–FJ–553–COD–EX",  # Update here
    # ...
}
```

Also update the Dominion Seal SVG in `assets/dominion-seal.svg`.

### Version Updates

Update version in `export_runtime.py`:

```python
"version": "5.5.3",  # Update version here
```

## Support

For issues or questions:
- Check GitHub Actions logs
- Review Netlify deployment logs
- Verify all secrets are configured
- Ensure all files are committed to the repository

## References

- [Netlify Documentation](https://docs.netlify.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Forge Dominion Guide](FORGE_DOMINION_DEPLOYMENT_GUIDE.md)

---

**Status:** ✅ Deployment Infrastructure Active  
**Version:** 5.5.3  
**Forge ID:** Σ–AIBR–FJ–553–COD–EX
