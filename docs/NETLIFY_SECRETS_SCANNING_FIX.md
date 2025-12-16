# Netlify Secrets Scanning Configuration Fix

## Problem

The Netlify deployment was failing due to secrets scanning detecting `FORGE_DOMINION_ROOT` environment variable values throughout the codebase. The scanner incorrectly flagged the value "dominion://sovereign.bridge" as a secret, even though it's a non-sensitive configuration value used for bridge communication.

### Error Details

```
Secret env var "FORGE_DOMINION_ROOT"'s value detected:
  found value at line 16 in brh/README.md
  found value at line 24 in brh/consensus.py
  found value at line 34 in brh/examples/README.md
  [... 30+ more locations ...]
```

The error message stated:
> To prevent exposing secrets, the build will fail until these secret values are not found in build output or repo files.
> If these are expected, use SECRETS_SCAN_OMIT_PATHS, SECRETS_SCAN_OMIT_KEYS, or SECRETS_SCAN_ENABLED to prevent detecting.

## Solution

### 1. Configure Secrets Scanning Exclusions

Added `SECRETS_SCAN_OMIT_KEYS` and `SECRETS_SCAN_OMIT_PATHS` environment variables to the `netlify.toml` configuration file.

#### Configuration Added

```toml
[build]
  environment = { 
    FORGE_DOMINION_ROOT = "", 
    REVIEW_ID = "", 
    SECRETS_SCAN_OMIT_KEYS = "FORGE_DOMINION_ROOT", 
    SECRETS_SCAN_OMIT_PATHS = "brh/*,docs/*,codex/*,netlify/functions/forge-resolver.js,infra/*,netlify.toml" 
  }

[context.production.environment]
  FORGE_DOMINION_ROOT = "dominion://sovereign.bridge"
  GITHUB_REF_NAME = "main"
  SECRETS_SCAN_OMIT_KEYS = "FORGE_DOMINION_ROOT"
  SECRETS_SCAN_OMIT_PATHS = "brh/*,docs/*,codex/*,netlify/functions/forge-resolver.js,infra/*,netlify.toml"

[context.deploy-preview.environment]
  FORGE_DOMINION_ROOT = "dominion://sovereign.bridge?env=preview"
  SECRETS_SCAN_OMIT_KEYS = "FORGE_DOMINION_ROOT"
  SECRETS_SCAN_OMIT_PATHS = "brh/*,docs/*,codex/*,netlify/functions/forge-resolver.js,infra/*,netlify.toml"

[context.branch-deploy.environment]
  FORGE_DOMINION_ROOT = "dominion://sovereign.bridge?env=branch"
  SECRETS_SCAN_OMIT_KEYS = "FORGE_DOMINION_ROOT"
  SECRETS_SCAN_OMIT_PATHS = "brh/*,docs/*,codex/*,netlify/functions/forge-resolver.js,infra/*,netlify.toml"
```

### 2. Updated Engine Exports

Enhanced `bridge_backend/bridge_core/engines/__init__.py` to properly export all 34 engines including:

**Core Infrastructure Engines (6):**
- Blueprint Engine
- Cascade Engine  
- Truth Engine (via routes)
- Autonomy Engine
- Parser Engine
- HXO Nexus

**Super Engines (7):**
- Leviathan
- CalculusCore
- QHelmSingularity
- AuroraForge
- ChronicleLoom
- ScrollTongue
- CommerceForge

**Utility & Support Engines (14+):**
- Chimera Deployment Engine
- EnvSync Engine
- Filing Engine
- Screen Engine
- Speech Engines (TTS/STT)
- Recovery Orchestrator
- Creativity Bay
- Indoctrination Engine
- Umbra Lattice
- And more...

## Why This Works

1. **SECRETS_SCAN_OMIT_KEYS**: Tells Netlify to ignore the `FORGE_DOMINION_ROOT` environment variable when scanning for secrets. This is safe because the value is not a credential but a configuration URI.

2. **SECRETS_SCAN_OMIT_PATHS**: Excludes specific paths from scanning:
   - `brh/*` - Bridge Runtime Handler documentation and examples
   - `docs/*` - Documentation files
   - `codex/*` - Code repository metadata
   - `netlify/functions/forge-resolver.js` - Function that uses the env var
   - `infra/*` - Infrastructure configuration
   - `netlify.toml` - The config file itself

3. **Context-Specific Configuration**: Applied to all deployment contexts (production, deploy-preview, branch-deploy) to ensure consistent behavior.

## Security Considerations

### Why FORGE_DOMINION_ROOT is Safe to Exclude

- **Not a Secret**: The value is a URI scheme for bridge communication, not credentials
- **Public by Design**: Meant to be visible in documentation and examples
- **No Sensitive Data**: Contains no passwords, API keys, or tokens
- **Configuration Only**: Used for service discovery and routing

### What Should NOT Be Excluded

Never add these to `SECRETS_SCAN_OMIT_KEYS`:
- Database credentials (DATABASE_URL with passwords)
- API keys (DATADOG_API_KEY, etc.)
- Authentication tokens
- Private keys
- Federation sync keys with secrets

## Testing

To verify the configuration works:

1. **Local Build Test**:
   ```bash
   bash scripts/netlify_build.sh
   ```

2. **Netlify Deploy**: Push to a branch and verify the build succeeds without secrets scanning errors

3. **Check Logs**: Ensure no warnings about "Secrets scanning found secrets in build"

## References

- [Netlify Secrets Scanning Documentation](https://ntl.fyi/configure-secrets-scanning)
- Related PR: #353 - Bridge Harmony: Auto-wiring orchestration for 34 engines
- Bridge Harmony Summary: `/BRIDGE_HARMONY_SUMMARY.md`

## Maintenance

If you add new non-sensitive environment variables that get flagged by the scanner:

1. Add the variable name to `SECRETS_SCAN_OMIT_KEYS`
2. If it appears in documentation, add the path pattern to `SECRETS_SCAN_OMIT_PATHS`
3. Update this documentation

**Last Updated**: 2024-11-06  
**Status**: ✅ Deployment Fixed
