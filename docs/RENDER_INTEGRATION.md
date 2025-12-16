# Render.com Service Configuration for SR-AIbridge Heavy Compute

# This configuration allows running heavy GitHub Actions workloads on Render's free tier
# to reduce GitHub Actions minutes consumption

## Services to Deploy on Render.com

### 1. Quantum Security Service (Web Service - Free Tier)

**Purpose**: Run quantum security checks triggered by GitHub webhooks

**Configuration**:
- **Name**: sr-aibridge-quantum-security
- **Environment**: Docker
- **Plan**: Free
- **Auto-Deploy**: No (webhook triggered)

**Environment Variables**:
```
FORGE_DOMINION_ROOT=<from_github_secrets>
FORGE_DOMINION_MODE=sovereign
FORGE_DOMINION_VERSION=1.9.7s
GITHUB_TOKEN=<github_pat_with_repo_access>
```

**Build Command**: 
```bash
pip install -r bridge_backend/requirements.txt
```

**Start Command**:
```bash
bash runtime/render_quantum_security.sh
```

**Dockerfile** (if using Docker):
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install git for cloning
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY bridge_backend/requirements.txt /app/bridge_backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r bridge_backend/requirements.txt

# Copy runtime scripts
COPY runtime/render_quantum_security.sh /app/runtime/
RUN chmod +x /app/runtime/render_quantum_security.sh

# Copy application code
COPY . /app/

EXPOSE 8080

# Health check endpoint
CMD ["python", "-m", "http.server", "8080"]
```

### 2. Token Rotation Service (Cron Job - Free Tier)

**Purpose**: Run token rotation on schedule without using GitHub Actions minutes

**Configuration**:
- **Name**: sr-aibridge-token-rotation
- **Environment**: Python
- **Plan**: Free
- **Schedule**: Every 6 hours (0 */6 * * *)

**Command**:
```bash
cd /app && python -m bridge_backend.bridge_core.token_forge_dominion.bootstrap
```

### 3. Self-Hosted Runner (Web Service - Free Tier)

**Purpose**: Run GitHub Actions on Render infrastructure

**Configuration**:
- **Name**: sr-aibridge-gh-runner
- **Environment**: Docker
- **Plan**: Free
- **Auto-Deploy**: Yes

**Dockerfile**:
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl git sudo && \
    rm -rf /var/lib/apt/lists/*

# Create runner user
RUN useradd -m runner && \
    usermod -aG sudo runner && \
    echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER runner
WORKDIR /home/runner

# Download and setup GitHub Actions runner
RUN curl -o actions-runner-linux.tar.gz -L \
    https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz && \
    tar xzf actions-runner-linux.tar.gz && \
    rm actions-runner-linux.tar.gz

# Configure and run (use environment variables for registration)
CMD ["bash", "-c", "./config.sh --url $GITHUB_REPO --token $RUNNER_TOKEN --labels bridge-native --unattended && ./run.sh"]
```

## GitHub Workflow Integration

### Trigger Render Services from GitHub Actions

Add this to workflows that need heavy compute:

```yaml
jobs:
  trigger-render-quantum:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Quantum Check on Render
        run: |
          curl -X POST "${{ secrets.RENDER_QUANTUM_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -d '{
              "github_repo": "${{ github.repository }}",
              "github_ref": "${{ github.ref }}",
              "github_sha": "${{ github.sha }}",
              "callback_url": "${{ github.api_url }}/repos/${{ github.repository }}/statuses/${{ github.sha }}"
            }'
      
      - name: Wait for Render completion
        run: |
          # Poll GitHub commit status until Render reports back
          for i in {1..30}; do
            sleep 10
            STATUS=$(curl -s "${{ github.api_url }}/repos/${{ github.repository }}/commits/${{ github.sha }}/status" | jq -r '.state')
            if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ]; then
              break
            fi
          done
```

## Setup Instructions

### 1. Create Render Account
- Sign up at https://render.com
- Free tier includes:
  - 750 hours/month of runtime
  - Multiple web services
  - Cron jobs

### 2. Deploy Services
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Use configurations above
4. Add environment variables
5. Deploy

### 3. Configure Webhooks
1. Get your Render service URL
2. Add to GitHub secrets as `RENDER_QUANTUM_WEBHOOK_URL`
3. Update workflows to trigger Render services

### 4. Update GitHub Workflows
- Disable quantum_dominion.yml on push (keep manual trigger)
- Disable forge_dominion.yml scheduled runs
- Add Render trigger to main CI workflow

## Expected Cost Savings

**Before Optimization**:
- 43 pushes × 70 minutes = 3,010 minutes/month
- 1,010 billable minutes (after 2,000 free tier)
- Cost: ~$8/month

**After Optimization**:
- GitHub Actions: 43 pushes × 20 minutes = 860 minutes/month
- All within free tier (0 billable minutes)
- Render.com: Free tier (750 hours available)
- **Total Cost: $0/month**

**Savings**: $8/month → $0/month (100% reduction, $96/year saved)

## Monitoring

Monitor your Render services:
- Dashboard: https://dashboard.render.com
- Logs: Available in service details
- Metrics: Free tier includes basic metrics

For GitHub Actions:
- Go to Settings → Billing → Actions
- Monitor minutes usage
- Set up budget alerts
