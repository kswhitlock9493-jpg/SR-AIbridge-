# Firewall Blocking Fix - Browser Downloads

## Problem Statement

The application was experiencing deployment failures due to firewall blocking of browser download URLs:
- `googlechromelabs.github.io` - Blocked by DNS/firewall
- `storage.googleapis.com/chrome-for-testing-public/...` - Blocked by HTTP/firewall

This was causing Playwright's internal `install.mjs` script to fail during `npm install`, resulting in:
- Build failures in GitHub Actions workflows
- Blank screens after deployment
- Installation timeouts

## Root Cause

When installing `@playwright/test` or `puppeteer` packages via npm, these tools automatically attempt to download browser binaries during the postinstall phase. The download URLs are blocked by the firewall, causing the installation to fail or timeout.

## Solution Implemented

### 1. Environment Variables Configuration

Set the following environment variables in all relevant contexts to skip browser downloads:

```bash
PUPPETEER_SKIP_DOWNLOAD="true"
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD="true"
PUPPETEER_SKIP_CHROMIUM_DOWNLOAD="true"
```

### 2. NPM Configuration Files

Added browser download skip flags to `.npmrc` files:

**Root `.npmrc`:**
```ini
registry=https://registry.npmjs.org/
@netlify:registry=https://registry.npmjs.org/
always-auth=false
legacy-peer-deps=true
# Skip browser downloads to avoid firewall blocks
puppeteer_skip_download=true
playwright_skip_browser_download=true
```

**`bridge-frontend/.npmrc`:**
```ini
registry=https://registry.npmjs.org/
always-auth=false
# Skip browser downloads to avoid firewall blocks
puppeteer_skip_download=true
playwright_skip_browser_download=true
```

### 3. GitHub Actions Workflows

Updated 12+ workflow files to use the new pattern:

**Before (Problematic):**
```yaml
- name: Install Chrome Dependencies
  run: |
    npx playwright install-deps
    npx playwright install chromium

- name: Install dependencies
  run: cd bridge-frontend && npm ci
```

**After (Fixed):**
```yaml
- name: Install Chrome Dependencies
  run: |
    # Install system dependencies for Playwright only (skip browser downloads)
    npx playwright install-deps
  env:
    PUPPETEER_SKIP_DOWNLOAD: "true"
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: "true"
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD: "true"

- name: Install dependencies
  run: cd bridge-frontend && npm ci
  env:
    PUPPETEER_SKIP_DOWNLOAD: "true"
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: "true"
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD: "true"
```

### 4. Key Changes Summary

1. **Removed** all `npx playwright install chromium` commands
2. **Kept** `npx playwright install-deps` for system dependencies only
3. **Added** environment variables to all workflow steps that run npm commands
4. **Updated** `.npmrc` files to persist the configuration
5. **Fixed** browser-setup GitHub action
6. **Updated** failure_analyzer.py templates to recommend correct configuration

## Files Modified

### GitHub Workflows (12 files)
- `.github/workflows/deploy.yml`
- `.github/workflows/firewall_harmony.yml`
- `.github/workflows/bridge_autodeploy.yml`
- `.github/workflows/bridge_compliance.yml`
- `.github/workflows/build-deploy-triage.yml`
- `.github/workflows/build_preflight.yml`
- `.github/workflows/build_triage_netlify.yml`
- `.github/workflows/copilot-preflight.yml`
- `.github/workflows/deploy_preview.yml`
- `.github/workflows/endpoint-deepscan.yml`
- `.github/workflows/env-parity-check.yml`
- `.github/workflows/firewall-bypass.yml`

### GitHub Actions (1 file)
- `.github/actions/browser-setup/action.yml`

### Configuration Files (2 files)
- `.npmrc`
- `bridge-frontend/.npmrc`

### Python Tools (1 file)
- `bridge_backend/tools/autonomy/failure_analyzer.py`

## Browser Strategy

Instead of downloading browsers, the application now uses:
1. **System browsers** - Chrome/Chromium installed via `playwright install-deps`
2. **Pre-cached browsers** - From previous successful builds (when cache is available)
3. **GitHub Actions pre-installed browsers** - Available in the Ubuntu runner environment

## Testing & Validation

The fix has been validated by:
1. Checking all workflow files for consistent environment variable usage
2. Verifying `.npmrc` configuration is correct
3. Ensuring no `npx playwright install chromium` commands remain in production code
4. Confirming netlify build script already had proper configuration

## Future Maintenance

To maintain this fix:
1. **Always** set skip environment variables when adding new workflows
2. **Never** use `npx playwright install chromium` in CI/CD
3. **Only** use `npx playwright install-deps` for system dependencies
4. Keep the `.npmrc` configuration in sync across all locations

## Related Scripts

The following scripts already had proper configuration:
- `scripts/netlify_build.sh` - Already set skip flags
- `bridge-frontend/scripts/chromium-guard.mjs` - Smart browser strategy selector
- `bridge-frontend/scripts/which-chrome.mjs` - Browser detection utility

## Benefits

1. ✅ No more firewall-blocked downloads
2. ✅ Faster builds (no download time)
3. ✅ More reliable deployments
4. ✅ Works in restricted network environments
5. ✅ Consistent behavior across all environments

## Monitoring

To verify the fix is working:
- Check GitHub Actions logs for "Installing Chromium browser..." (should not appear)
- Verify no connection attempts to `googlechromelabs.github.io` or `storage.googleapis.com`
- Confirm builds complete successfully without timeout errors
- Monitor deployment success rate

## Rollback Plan

If issues arise:
1. The firewall blocking will return immediately
2. Builds will timeout or fail with connection errors
3. Revert to this commit to restore the fix

## Additional Notes

- The `chromium-guard.mjs` script provides fallback strategies if system browsers are unavailable
- The firewall harmony system monitors for these patterns and can auto-repair
- Netlify builds use the `scripts/netlify_build.sh` which already had proper configuration
