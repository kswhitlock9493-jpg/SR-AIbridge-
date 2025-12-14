# Bridge Federation Build - Required Secrets Configuration

## Overview

The `bridge_federation_build.yml` workflow requires specific GitHub repository secrets to be configured for proper operation. This document outlines the required secrets and their purpose.

## Required Secrets

### FED_KEY
- **Purpose**: Active federation access token for inter-service communication
- **Type**: Secret token
- **Required**: Yes (optional for basic builds, required for federation heartbeat)
- **Description**: Provides authentication for federation-level operations and heartbeat coordination
- **Configuration**: Set in GitHub repository settings → Secrets and variables → Actions → Repository secrets

### DOM_TOKEN
- **Purpose**: Active dominion token for quantum security validation
- **Type**: Ephemeral security token
- **Required**: Yes (optional for basic builds, required for quantum dominion security)
- **Description**: Validates ephemeral token lifespan and ensures secure deployment
- **Note**: Token should be freshly generated and rotated regularly
- **Configuration**: Set in GitHub repository settings → Secrets and variables → Actions → Repository secrets

### BRIDGE_ENV
- **Purpose**: Deployment environment identifier
- **Type**: Environment variable
- **Required**: No (defaults to "sovereign")
- **Allowed Values**: `sovereign`, `staging`, `development`
- **Description**: Determines the target environment for deployment
- **Configuration**: Set in GitHub repository settings → Secrets and variables → Actions → Variables

## Workflow Environment Variables

The workflow also uses the following environment variables that are set in the workflow file:

- `PYTHON_VERSION`: "3.11" - Python version for build and validation
- `NODE_VERSION`: "20" - Node.js version (reserved for future use)

## Setting Up Secrets

### Using GitHub UI

1. Navigate to your repository on GitHub
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add each required secret:
   - **Name**: `FED_KEY`
   - **Value**: Your federation key
   - Click "Add secret"
5. Repeat for `DOM_TOKEN`
6. For `BRIDGE_ENV`, use "Variables" tab instead of "Secrets"

### Using GitHub CLI

```bash
# Set FED_KEY
gh secret set FED_KEY --body "your-federation-key"

# Set DOM_TOKEN
gh secret set DOM_TOKEN --body "your-dominion-token"

# Set BRIDGE_ENV (as a variable)
gh variable set BRIDGE_ENV --body "sovereign"
```

## Security Best Practices

1. **Rotate Tokens Regularly**: DOM_TOKEN should be rotated frequently as it's an ephemeral token
2. **Least Privilege**: Only grant necessary permissions to each token
3. **Audit Access**: Regularly review who has access to modify secrets
4. **Environment Separation**: Use different tokens for staging vs. production environments

## Workflow Behavior Without Secrets

- **Without FED_KEY**: Federation heartbeat will skip or use default behavior
- **Without DOM_TOKEN**: Quantum dominion security validation will fail
- **Without BRIDGE_ENV**: Defaults to "sovereign" environment

## Troubleshooting

### "No dominion token provided" Error
- Ensure `DOM_TOKEN` is set in repository secrets
- Verify the secret name matches exactly (case-sensitive)

### Federation Heartbeat Timeout
- Check `FED_KEY` is valid and not expired
- Verify network connectivity to federation services
- Increase timeout if necessary in workflow file

### Token Validation Failed
- Generate a new `DOM_TOKEN`
- Ensure token meets minimum length requirements (10+ characters)
- Check token hasn't expired

## Related Files

- Workflow: `.github/workflows/bridge_federation_build.yml`
- Validation Module: `bridge_core/security/validate_token.py`
- Heartbeat Module: `bridge_core/lattice/heartbeat.py`
- Guard Module: `bridge_core/self_heal/guard.py`
- Path Check Module: `bridge_core/lattice/pathcheck.py`

## Support

For issues or questions about secret configuration, refer to:
- GitHub Actions Secrets documentation
- Repository maintainers
- Security team for token generation and rotation policies
