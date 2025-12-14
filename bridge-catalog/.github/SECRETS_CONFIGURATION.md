# Required GitHub Secrets Configuration

This document describes the GitHub Secrets required for the SR-AIBridge workflows to function properly.

## Required Secrets

These secrets must be added via GitHub Repository Settings → Secrets and variables → Actions → Repository secrets:

### 1. FED_KEY (Federation Key)
- **Description**: Federation access token for quantum federation security
- **Required by**: Various federation workflows
- **Example value**: `quantum_federation`
- **How to set**: Use any placeholder value - the Sovereign Dominion Token Forge (SDTF) will handle actual token management

### 2. DOM_TOKEN (Dominion Token)
- **Description**: Ephemeral dominion token for quantum dominion security layer
- **Required by**: Forge Dominion workflows, deployment processes
- **Example value**: `ephemeral_dominion`
- **How to set**: Use any placeholder value - tokens are ephemeral and managed by SDTF

### 3. NETLIFY_AUTH_TOKEN
- **Description**: Netlify API authentication token
- **Required by**: Netlify deployment and validation workflows
- **How to obtain**: 
  1. Log in to Netlify
  2. Go to User Settings → Applications → Personal Access Tokens
  3. Generate new access token
- **How to set**: Add the actual token from Netlify

### 4. BRIDGE_ENV
- **Description**: Bridge environment identifier
- **Required by**: Environment configuration workflows
- **Example value**: `sovereign`
- **How to set**: Set to `sovereign` for default sovereign state

## Required Variables

These should be added as Repository variables (not secrets) via GitHub Repository Settings → Secrets and variables → Actions → Variables:

### 1. FORGE_DOMINION_MODE
- **Description**: Operating mode for Forge Dominion
- **Default value**: `sovereign`

### 2. FORGE_DOMINION_VERSION
- **Description**: Version of Forge Dominion system
- **Default value**: `1.9.7s`

## How to Add Secrets

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

## Important Notes

- **FED_KEY** and **DOM_TOKEN**: These can be set to placeholder values as shown. The Sovereign Dominion Token Forge (SDTF) system will override or manage these during runtime.
- **NETLIFY_AUTH_TOKEN**: This must be a real Netlify API token for deployments to work.
- **BRIDGE_ENV**: Set to `sovereign` to maintain the default sovereign state of the system.

## Security Considerations

- Never commit secrets directly to the repository
- Rotate tokens regularly, especially for production environments
- The quantum dominion security layer operates independently of these placeholder values
- The SDTF system handles actual security token lifecycle management

## Troubleshooting

If you see errors like:
- `No dominion token provided via --dominion or DOM_TOKEN env var` → Add DOM_TOKEN secret
- `Netlify API 401 Unauthorized` → Check NETLIFY_AUTH_TOKEN is valid
- `Git push 403 - Write access not granted` → Check repository permissions

For more information, see:
- BRIDGE_FEDERATION_SECRETS.md
- FORGE_DOMINION_DEPLOYMENT_GUIDE.md
