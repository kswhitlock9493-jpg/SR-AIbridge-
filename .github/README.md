# SR-AIbridge CI/CD Infrastructure

This directory contains the GitHub Actions workflows that power the continuous integration and deployment pipeline for SR-AIbridge.

## 🚀 Workflows

### `deploy.yml` - Main Deployment Pipeline

Automatically deploys both frontend and backend when changes are pushed to the main branch.

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**Jobs:**
1. **Frontend Deployment** (`deploy-frontend`)
   - Builds React frontend with production API URL
   - Deploys to Netlify using GitHub integration
   - Supports both automatic and manual deployments

2. **Backend Deployment** (`deploy-backend`)
   - Validates Python backend code
   - Triggers Render deployment via webhook (optional)
   - Render auto-deploys on main branch push by default

3. **Build Verification** (`verify-build`)
   - Tests complete build process for both frontend and backend
   - Validates syntax and dependencies
   - Ensures self-test script is executable

### `self-test.yml` - Automated Health Monitoring

Comprehensive health checks and system monitoring after deployments.

**Triggers:**
- After successful completion of `deploy.yml`
- Manual dispatch with configurable parameters
- Scheduled runs every 4 hours
- Can be triggered with custom backend URL for testing

**Jobs:**
1. **Wait for Deployment** (`wait-for-deployment`)
   - Waits for backend to be responsive
   - Determines target URL based on trigger source

2. **Backend Health Tests** (`backend-health-tests`)
   - Runs comprehensive self-test suite against production backend
   - Tests all API endpoints, Guardian daemon, WebSocket functionality
   - Generates detailed JSON reports and summaries
   - Uploads test artifacts for historical analysis

3. **Frontend Connectivity Test** (`frontend-connectivity-test`)
   - Verifies frontend accessibility
   - Tests basic frontend-backend connectivity

4. **Results Notification** (`notify-results`)
   - Aggregates test results
   - Creates comprehensive status summaries
   - Provides actionable feedback for issues

## 🔧 Configuration

### Required Secrets

For full functionality, configure these GitHub repository secrets:

```bash
# Netlify Deployment
NETLIFY_AUTH_TOKEN=your_netlify_auth_token
NETLIFY_SITE_ID=your_netlify_site_id

# Optional: Custom URLs
BACKEND_URL=https://your-backend.onrender.com
FRONTEND_URL=https://your-frontend.netlify.app

# Optional: Render webhook for manual deployment trigger
RENDER_DEPLOY_HOOK=https://api.render.com/deploy/your-service-id
```

### Default Configuration

If secrets are not configured, the workflows use these defaults:
- **Backend URL**: `https://sr-aibridge-backend.onrender.com`
- **Frontend URL**: `https://sr-aibridge.netlify.app`

## 🧪 Self-Test Script Enhancement

The `bridge-backend/self_test.py` script has been enhanced for production use:

### New Features
- **Configurable Timeouts**: `--timeout` (default: 30s)
- **Retry Logic**: `--retries` (default: 3 attempts)
- **Server Readiness Wait**: `--wait-ready` (default: 60s)
- **JSON Output**: `--json` for machine-readable results
- **Robust Error Handling**: Exponential backoff, detailed error reporting

### Usage Examples

```bash
# Basic health check against production
python3 self_test.py --url https://sr-aibridge-backend.onrender.com

# CI/CD optimized run with JSON output
python3 self_test.py --url $BACKEND_URL --json --timeout 45 --retries 5

# Quick local development check
python3 self_test.py --timeout 10 --wait-ready 30
```

### Test Coverage

The self-test suite validates:
- ✅ Health and status endpoints
- ✅ Guardian daemon functionality
- ✅ Agent management CRUD operations
- ✅ Mission/task management
- ✅ Vault logs and doctrine endpoints
- ✅ WebSocket statistics
- ✅ Utility endpoints (activity, reseed)

## 📊 Monitoring & Observability

### GitHub Actions Insights
- View workflow runs in the **Actions** tab
- Download test artifacts for detailed analysis
- Monitor success rates and performance trends

### Self-Test Artifacts
- JSON test results with timestamps
- Pass/fail statistics with success rates
- Detailed error messages for failed tests
- Historical test data (30-day retention)

### Manual Testing
Trigger manual health checks anytime:

1. Go to **Actions** → **Self-Test SR-AIbridge**
2. Click **Run workflow**
3. Optionally specify custom backend URL
4. Review results in workflow summary

## 🔄 Integration with Existing Infrastructure

The CI/CD system seamlessly integrates with existing deployment configurations:

- **`render.yaml`**: Backend deployment configuration
- **`netlify.toml`**: Frontend deployment and redirect rules
- **`bridge-backend/self_test.py`**: Enhanced health monitoring
- **Package configurations**: Respects existing dependencies and build processes

## 🚨 Failure Handling

### Automatic Recovery
- Retry logic for transient network issues
- Exponential backoff to avoid overwhelming services
- Graceful degradation with detailed error reporting

### Alerting
- Failed workflows appear in GitHub notifications
- Detailed step-by-step logs for troubleshooting
- Artifact uploads for post-mortem analysis

### Manual Intervention
- Manual workflow dispatch for immediate testing
- Configurable parameters for debugging
- Direct access to self-test script for local debugging

## 🛡️ Security Considerations

- **Secrets Management**: All sensitive data stored in GitHub secrets
- **Network Security**: HTTPS-only communication
- **Minimal Permissions**: Workflows use least-privilege access
- **Audit Trail**: Complete CI/CD history in GitHub Actions logs

## 📈 Performance Optimization

- **Efficient Caching**: NPM and Python dependency caching
- **Parallel Execution**: Frontend/backend jobs run concurrently
- **Resource Management**: Appropriate timeouts and resource limits
- **Smart Scheduling**: Avoid peak usage times for scheduled jobs

---

This CI/CD infrastructure ensures reliable, automated deployments with comprehensive health monitoring, making SR-AIbridge production-ready with enterprise-grade reliability.