# 🚀 Sovereign Financial Independence Setup Guide

## Quick Start: Achieving Zero GitHub Actions Costs

This guide will help you achieve **legitimate financial sovereignty** by reducing GitHub Actions costs from ~$75/month to $0/month through smart orchestration and self-hosted infrastructure.

## Prerequisites

- Python 3.11+
- Access to your repository settings
- (Optional) A server/VM for self-hosted runners
- (Optional) Render.com account (free tier)
- (Optional) Netlify account (free tier)

## Step 1: Install Dependencies

```bash
cd /path/to/SR-AIbridge-
pip install -r requirements.txt
```

This installs PyYAML which is needed for workflow analysis.

## Step 2: Analyze Current Workflow Costs

Run the workflow consolidation analyzer to understand your current usage:

```bash
python3 .github/forge_token_engine/workflow_consolidation.py
```

Output example:
```
SUMMARY
======================================================================
Total Workflows: 61
Monthly Minutes: 3,010
Estimated Cost: $75.25

💰 Potential Savings: 900 minutes/month = $7.20/month
```

This shows you:
- How many workflows you have
- Total monthly compute usage
- Where the biggest costs are
- Quick wins for optimization

## Step 3: Set Up Self-Hosted Runner (Recommended - Zero Cost)

A self-hosted runner eliminates GitHub Actions costs entirely by using your own infrastructure.

### Option A: Use Existing Server

If you have Render.com hosting (which you do for the backend):

1. **SSH into your Render service** (if available) or use any Linux server/VM you have access to

2. **Download GitHub Actions runner:**
```bash
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
```

3. **Configure the runner:**
```bash
# Get token from: https://github.com/kswhitlock9493-jpg/SR-AIbridge-/settings/actions/runners/new
./config.sh --url https://github.com/kswhitlock9493-jpg/SR-AIbridge- \
  --token YOUR_RUNNER_TOKEN \
  --labels self-hosted,linux,x64,sovereign \
  --name sovereign-runner-1
```

4. **Run as a service:**
```bash
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status  # Verify it's running
```

5. **Create runner config file:**
```bash
cat > /home/runner/work/SR-AIbridge-/SR-AIbridge-/.github/self-hosted-runner.json <<EOF
{
  "enabled": true,
  "healthy": true,
  "labels": ["self-hosted", "linux", "x64", "sovereign"],
  "runners": [
    {
      "name": "sovereign-runner-1",
      "status": "online"
    }
  ]
}
EOF
```

### Option B: Use Docker Container (Easier)

Run a self-hosted runner in Docker on any machine:

```bash
docker run -d \
  --name github-runner \
  --restart unless-stopped \
  -e REPO_URL="https://github.com/kswhitlock9493-jpg/SR-AIbridge-" \
  -e RUNNER_TOKEN="YOUR_RUNNER_TOKEN" \
  -e RUNNER_NAME="sovereign-docker-runner" \
  -e LABELS="self-hosted,docker,sovereign" \
  myoung34/github-runner:latest
```

## Step 4: Configure Provider Credentials

Create `.github/forge_token_engine/config.json`:

```json
{
  "providers": {
    "self_hosted": {
      "enabled": true,
      "priority": 1
    },
    "render": {
      "enabled": true,
      "priority": 2,
      "deploy_hook": "https://api.render.com/deploy/srv-YOUR_SERVICE_ID"
    },
    "netlify": {
      "enabled": true,
      "priority": 3
    }
  },
  "alerts": {
    "warning_threshold": 70,
    "critical_threshold": 90
  }
}
```

Set GitHub Secrets (optional, if not already set):
- `RENDER_DEPLOY_HOOK` - Your Render deploy hook URL
- `NETLIFY_AUTH_TOKEN` - Your Netlify auth token (if using Netlify builds)

## Step 5: Update Workflows to Use Self-Hosted Runner

Modify your main workflows to use the self-hosted runner:

### Example: `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  # Route to self-hosted runner for zero cost
  build-and-test:
    runs-on: self-hosted  # Changed from 'ubuntu-latest'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest
      
      - name: Record usage (for tracking)
        run: |
          python .github/forge_token_engine/cost_bypass.py \
            --record \
            --provider self_hosted \
            --minutes 5
```

### Example: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: self-hosted  # Zero cost
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: bridge-frontend/package-lock.json
      
      - name: Build frontend
        run: |
          cd bridge-frontend
          npm ci
          npm run build
      
      - name: Deploy to Netlify (uses Netlify free tier minutes)
        uses: nwtgck/actions-netlify@v3.0
        with:
          publish-dir: bridge-frontend/dist
          production-deploy: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## Step 6: Consolidate Redundant Workflows

Based on the analysis output, consolidate workflows that run on the same triggers.

### Before (Redundant):
- `workflow-a.yml` - Runs on push, does linting
- `workflow-b.yml` - Runs on push, does tests  
- `workflow-c.yml` - Runs on push, does build

### After (Consolidated):
- `ci.yml` - Runs on push, does linting + tests + build

This reduces overhead and saves ~30% of compute time.

Example consolidated workflow:

```yaml
name: CI (Consolidated)

on:
  push:
    branches: [main]

jobs:
  all-checks:
    runs-on: self-hosted
    
    steps:
      - uses: actions/checkout@v4
      
      # Lint
      - name: Lint
        run: |
          flake8 .
          eslint bridge-frontend/src
      
      # Test
      - name: Test
        run: |
          pytest
          npm test
      
      # Build
      - name: Build
        run: |
          cd bridge-frontend
          npm run build
```

## Step 7: Monitor and Verify Savings

Run the cost reporting tool:

```bash
python3 .github/forge_token_engine/cost_bypass.py --report
python3 .github/forge_token_engine/financial_resilience.py
```

Check your GitHub Actions usage:
1. Go to https://github.com/kswhitlock9493-jpg/SR-AIbridge-/settings/billing
2. View Actions usage
3. Verify it's dropping month-over-month

## Step 8: Set Up Automated Monitoring

Create `.github/workflows/cost-monitor.yml`:

```yaml
name: Cost Monitoring

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  monitor:
    runs-on: self-hosted  # Free!
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate cost report
        run: |
          python3 .github/forge_token_engine/cost_bypass.py --report > cost-report.txt
          python3 .github/forge_token_engine/financial_resilience.py >> cost-report.txt
      
      - name: Show report
        run: cat cost-report.txt
      
      - name: Alert if costs increasing
        run: |
          # Add your alert logic here (Slack, Discord, email, etc.)
          echo "Review cost report above"
```

## Expected Results

### Month 1 (Current)
- Total Minutes: 3,010
- GitHub Actions: 3,010 minutes
- Cost: **$75.25**

### Month 2 (After Self-Hosted Setup)
- Total Minutes: 3,010
- Self-Hosted: 2,700 minutes ($0)
- Render Free: 200 minutes ($0)
- Netlify Free: 110 minutes ($0)
- GitHub Actions: 0 minutes ($0)
- Cost: **$0.00**

### Savings
- **$75.25/month = $903/year**
- **100% cost reduction**
- **Zero vendor lock-in**

## Troubleshooting

### Runner not appearing
- Check firewall allows outbound HTTPS
- Verify token hasn't expired
- Check runner logs: `./run.sh` output

### Workflows still using ubuntu-latest
- Update `runs-on:` to `self-hosted` in workflow files
- Commit and push changes
- Verify in Actions tab that jobs show "self-hosted" label

### Self-hosted runner offline
```bash
# Check status
sudo ./svc.sh status

# Restart
sudo ./svc.sh restart

# View logs
journalctl -u actions.runner.* -n 50
```

## Advanced: Multi-Provider Failover

For maximum reliability, set up failover across providers:

```yaml
jobs:
  resilient-build:
    # Try self-hosted first
    runs-on: ${{ github.event_name == 'push' && 'self-hosted' || 'ubuntu-latest' }}
    
    steps:
      - name: Route via cost bypass
        run: |
          python .github/forge_token_engine/cost_bypass.py \
            --job "build" \
            --estimated-minutes 10 \
            --can-run-self-hosted \
            --can-run-render \
            --can-run-netlify
```

## Support

Questions? Issues?
1. Check the main README: `.github/forge_token_engine/README.md`
2. Review cost reports: Run the analyzer scripts
3. Check runner status: GitHub repo settings > Actions > Runners

## Next Steps

1. ✅ Set up self-hosted runner (biggest impact)
2. ✅ Update workflows to use self-hosted
3. ✅ Consolidate redundant workflows
4. ✅ Monitor and verify savings
5. 🎯 Achieve $0/month GitHub Actions costs

**Goal: Financial sovereignty through legitimate optimization, not exploitation!**
