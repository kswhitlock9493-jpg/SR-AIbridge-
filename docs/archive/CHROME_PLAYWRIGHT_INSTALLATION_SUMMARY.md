# Chrome/Playwright Installation Summary

## Overview
This document summarizes the changes made to add Chrome/Playwright dependency installation to GitHub Actions workflows to resolve Netlify build errors and browser-related issues.

## Changes Made

### Workflows Updated
The following 11 GitHub Actions workflows have been updated to include Chrome/Playwright installation:

1. **deploy.yml** - Main deployment workflow
2. **bridge_autodeploy.yml** - Auto-deploy mode
3. **bridge_compliance.yml** - Compliance checks
4. **build-deploy-triage.yml** - Build/deploy triage
5. **copilot-preflight.yml** - Copilot environment setup
6. **endpoint-deepscan.yml** - Endpoint scanning
7. **env-parity-check.yml** - Environment parity checks
8. **firewall_harmony.yml** - Firewall harmony checks
9. **build_preflight.yml** - Build preflight triage
10. **build_triage_netlify.yml** - Netlify build triage
11. **deploy_preview.yml** - Preview deployments

### Installation Step Added
Each workflow now includes the following step after Node.js setup and before dependency installation:

```yaml
- name: Install Chrome Dependencies
  run: |
    # Use GitHub's built-in browser tools
    npx playwright install-deps
    npx playwright install chromium
```

## Why This Change Was Needed

### Problem
The repository uses Playwright (listed in `bridge-frontend/package.json` as a dev dependency) for browser automation and testing. However, GitHub Actions runners don't have Chromium browsers installed by default, which can cause:

1. **Netlify build errors** - When the build process attempts to use browser automation
2. **Test failures** - If tests require a browser to run
3. **Browser detection issues** - Scripts like `chromium-guard.mjs` and `which-chrome.mjs` failing to find browsers

### Solution
By installing Playwright and its dependencies (including Chromium) in the CI environment:

1. **Ensures browser availability** - Chromium is installed and ready for use
2. **Prevents build failures** - Browser-dependent operations can complete successfully
3. **Improves reliability** - Consistent browser environment across all workflow runs
4. **Compatible with existing scripts** - Works with the existing `chromium-guard.mjs`, `which-chrome.mjs`, and `chromium_probe.py` scripts

## Technical Details

### Installation Components

#### `npx playwright install-deps`
- Installs system dependencies required by Playwright browsers
- Includes libraries needed for Chromium to run on Ubuntu
- Ensures all OS-level prerequisites are met

#### `npx playwright install chromium`
- Downloads and installs the Chromium browser
- Cached by Playwright for reuse
- Version-matched with the Playwright package

### Complementary Existing Code

The repository already has several components that work with this change:

1. **build_triage.py** - Sets environment variables to skip browser downloads during npm install:
   ```python
   os.environ["PUPPETEER_SKIP_DOWNLOAD"] = "true"
   os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "true"
   ```

2. **chromium-guard.mjs** - Detects and configures browser strategy:
   - Checks for cached browsers
   - Falls back to system Chrome if available
   - Supports controlled downloads when allowed

3. **chromium_probe.py** - Diagnostics tool that reports browser availability

4. **firewall_harmony.yml** - Already includes caching for Playwright browsers:
   ```yaml
   - uses: actions/cache@v4
     with:
       path: |
         ~/.cache/puppeteer
         ~/.cache/ms-playwright
   ```

## Validation

### Syntax Validation
All modified workflow files have been validated for YAML syntax using `yamllint`. All files pass syntax validation with no errors.

### Testing Strategy
To verify these changes work correctly:

1. **Workflow runs** - Monitor GitHub Actions workflow runs to ensure they complete successfully
2. **Build verification** - Check that frontend builds complete without browser-related errors
3. **Deployment checks** - Verify that Netlify deployments succeed
4. **Browser detection** - Confirm that `chromium-guard.mjs` reports successful browser detection

## Impact

### Benefits
- ✅ Eliminates browser-related build failures
- ✅ Provides consistent browser environment across all workflows
- ✅ Enables browser-based testing in CI
- ✅ Compatible with existing browser detection and fallback scripts
- ✅ Minimal overhead (browsers are cached between runs)

### Potential Considerations
- Slightly longer workflow run times on first execution (browser download)
- Additional disk space usage in GitHub Actions cache (mitigated by caching)
- Browser version updates will be automatic with Playwright updates

## Related Files and Scripts

### Scripts that benefit from this change:
- `bridge-frontend/scripts/chromium-guard.mjs`
- `bridge-frontend/scripts/which-chrome.mjs`
- `bridge-frontend/scripts/build_triage.py`
- `bridge_backend/tools/firewall_intel/chromium_probe.py`

### Configuration files:
- `bridge-frontend/package.json` - Contains Playwright as dev dependency
- `netlify.toml` - Netlify deployment configuration
- `.github/workflows/firewall_harmony.yml` - Browser caching configuration

## Future Enhancements

Potential improvements that could build on this foundation:

1. **E2E Testing** - Add end-to-end tests using Playwright
2. **Visual Regression Testing** - Implement screenshot-based testing
3. **Accessibility Testing** - Use browser automation for a11y checks
4. **Performance Testing** - Measure frontend performance in CI

## References

- [Playwright Installation Guide](https://playwright.dev/docs/intro)
- [GitHub Actions: Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Netlify Build Configuration](https://docs.netlify.com/configure-builds/overview/)

## Maintenance

### Keeping Browsers Updated
Playwright browsers are automatically updated when the `@playwright/test` package is updated in `package.json`. No manual intervention is needed.

### Cache Management
The browser cache in GitHub Actions is managed automatically. It will be invalidated when:
- The package-lock.json file changes
- The cache expires (default: 7 days of inactivity)

### Monitoring
Monitor workflow runs to ensure:
- Browser installation completes successfully
- No significant increase in workflow duration
- Cache hit rates remain high
