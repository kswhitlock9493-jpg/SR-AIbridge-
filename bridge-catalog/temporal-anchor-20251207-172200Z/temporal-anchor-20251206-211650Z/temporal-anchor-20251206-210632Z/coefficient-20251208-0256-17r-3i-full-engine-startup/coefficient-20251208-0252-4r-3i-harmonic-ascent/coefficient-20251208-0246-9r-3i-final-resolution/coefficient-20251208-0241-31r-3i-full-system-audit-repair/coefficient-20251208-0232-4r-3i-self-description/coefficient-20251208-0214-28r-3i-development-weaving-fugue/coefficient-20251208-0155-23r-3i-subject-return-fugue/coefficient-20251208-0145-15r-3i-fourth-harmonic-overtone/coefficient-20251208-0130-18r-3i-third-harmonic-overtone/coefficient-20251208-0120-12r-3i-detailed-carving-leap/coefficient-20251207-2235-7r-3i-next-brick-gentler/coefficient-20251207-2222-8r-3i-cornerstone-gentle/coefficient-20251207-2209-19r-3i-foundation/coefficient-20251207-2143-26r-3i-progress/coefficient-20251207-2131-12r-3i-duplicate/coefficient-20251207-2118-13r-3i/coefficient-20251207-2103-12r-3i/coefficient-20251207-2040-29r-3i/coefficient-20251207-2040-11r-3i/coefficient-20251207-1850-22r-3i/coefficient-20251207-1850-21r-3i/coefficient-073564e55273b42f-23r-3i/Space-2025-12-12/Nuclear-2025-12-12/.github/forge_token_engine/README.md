# 🏦 Forge Token Engine: Financial Sovereignty System

## Overview

The Forge Token Engine provides **legitimate financial sovereignty** by intelligently orchestrating compute resources across multiple free-tier providers. This eliminates dependency on paid GitHub Actions minutes while maintaining full CI/CD functionality.

## ⚠️ Important Clarifications

### What This System DOES:
- ✅ Routes workflows to free-tier compute providers (Render, Netlify, Vercel)
- ✅ Implements self-hosted runners to eliminate external costs
- ✅ Provides multi-provider redundancy and failover
- ✅ Monitors and optimizes resource usage across platforms
- ✅ Achieves legitimate cost reduction through smart orchestration

### What This System DOES NOT Do:
- ❌ Create "fake tokens" to bypass GitHub billing
- ❌ Generate credentials that GitHub "must honor but cannot bill"
- ❌ Attempt to exploit or circumvent platform security
- ❌ Violate any provider's terms of service

## 💰 Cost Reality Check

### GitHub Actions Costs (Reality)
- **Public repositories**: FREE unlimited minutes
- **Private repositories**: 
  - Free tier: 2,000 minutes/month
  - After limit: $0.008/minute (~$0.48/hour)
- **GITHUB_TOKEN**: FREE - auto-provided, no cost

### The Real Problem
Based on "43 pushes = 3,000 minutes = $75+ cost":
- **$75 / 3,000 min = $0.025/min** (higher than standard rate)
- This suggests either:
  1. Custom paid plan or
  2. Multiple parallel jobs multiplying cost or
  3. High-CPU runners (2-4x cost multiplier)

### The Sovereign Solution
This system provides **TRUE cost reduction** through:

1. **Self-Hosted Runners** (Priority 1)
   - Zero external cost
   - Uses your own infrastructure
   - Unlimited minutes

2. **Render Free Tier** (Priority 2)
   - 750 hours/month free (45,000 minutes)
   - More than enough for typical usage
   - Automatic build hooks

3. **Netlify Free Tier** (Priority 3)
   - 300 build minutes/month free
   - Perfect for frontend builds
   - CDN deployment included

4. **Vercel Free Tier** (Priority 4)
   - 100 GB-hours/month free
   - Serverless function execution
   - Edge network deployment

## 📊 Cost Comparison

### Before (All GitHub Actions)
```
43 pushes/month
× 70 minutes average per push
= 3,010 minutes/month
× $0.025/minute (your observed rate)
= $75.25/month
```

### After (Sovereign Orchestration)
```
43 pushes/month:
- 30 pushes via Self-Hosted (2,100 min) = $0.00
- 10 pushes via Render (700 min) = $0.00
- 3 pushes via Netlify (210 min) = $0.00
= $0.00/month total
```

**Savings: $75.25/month = $903/year**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Workflow Trigger (Git Push)                    │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│     Cost Bypass Orchestrator (cost_bypass.py)           │
│  - Analyzes job requirements                            │
│  - Checks provider quotas                               │
│  - Selects optimal provider                             │
└───────────────────┬─────────────────────────────────────┘
                    │
       ┌────────────┼────────────┬──────────────┐
       │            │            │              │
┌──────▼──────┐ ┌──▼────────┐ ┌─▼─────────┐  ┌▼──────────┐
│ Self-Hosted │ │  Render   │ │  Netlify  │  │  Vercel   │
│  (0 cost)   │ │(Free tier)│ │(Free tier)│  │(Free tier)│
└──────┬──────┘ └──┬────────┘ └─┬─────────┘  └┬──────────┘
       │           │             │              │
       └───────────┴─────────────┴──────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│  Financial Resilience Manager (financial_resilience.py) │
│  - Monitors quotas                                      │
│  - Provides failover                                    │
│  - Ensures continuous operation                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Providers

Create `.github/forge_token_engine/config.json`:
```json
{
  "providers": {
    "render": {
      "enabled": true,
      "deploy_hook": "https://api.render.com/deploy/srv-xxx"
    },
    "netlify": {
      "enabled": true,
      "auth_token": "stored_in_github_secrets"
    },
    "self_hosted": {
      "enabled": true,
      "runner_labels": ["self-hosted", "linux", "x64"]
    }
  }
}
```

### 3. Set Up Self-Hosted Runner (Recommended)

On your own server/VM:
```bash
# Download runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure runner
./config.sh --url https://github.com/YOUR_ORG/SR-AIbridge- \
  --token YOUR_RUNNER_TOKEN \
  --labels self-hosted,linux,x64,sovereign

# Run as service
sudo ./svc.sh install
sudo ./svc.sh start
```

### 4. Update Workflows

Modify `.github/workflows/ci.yml`:
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  cost-optimized-build:
    # Let the orchestrator select the optimal runner
    runs-on: ${{ github.event_name == 'push' && 'self-hosted' || 'ubuntu-latest' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Route via Cost Bypass
        run: |
          python .github/forge_token_engine/cost_bypass.py \
            --job "build" \
            --estimated-minutes 5
      
      - name: Build
        run: npm run build
```

## 📈 Usage Monitoring

### Check Current Status
```bash
python .github/forge_token_engine/financial_resilience.py
```

Output:
```json
{
  "total_available_minutes": 47100,
  "failover_chain": ["self_hosted", "render_free", "netlify_free"],
  "resilience_score": 95.0
}
```

### Generate Cost Report
```bash
python .github/forge_token_engine/cost_bypass.py --report
```

Output:
```
💰 COST REPORT
═══════════════════════════════════════════════════════
Total Minutes This Month: 3,010
  Self-Hosted: 2,100 min ($0.00)
  Render Free: 700 min ($0.00)
  Netlify Free: 210 min ($0.00)
  GitHub Actions: 0 min ($0.00)
───────────────────────────────────────────────────────
Actual Cost: $0.00
Hypothetical GitHub Cost: $75.25
Savings: $75.25 (100% reduction)
═══════════════════════════════════════════════════════
```

## 🛡️ Failover Strategy

The system implements intelligent failover:

1. **Primary**: Self-hosted runners (zero cost, unlimited)
2. **Secondary**: Render free tier (45,000 min/month free)
3. **Tertiary**: Netlify/Vercel free tiers (combined ~6,300 min/month)
4. **Fallback**: GitHub Actions (only if all others unavailable)

### Automatic Failover Example
```python
from cost_bypass import CostBypassEngine

engine = CostBypassEngine()
provider = engine.select_optimal_provider(
    WorkflowJob(
        name="Deploy",
        estimated_minutes=10,
        can_run_on_self_hosted=True,
        can_run_on_render=True
    )
)

# Will select: self_hosted (if available)
# Falls back to: render_free
# Then: netlify_free
# Finally: github_actions
```

## 🔧 Configuration Options

### Provider Priority
Configure in `config.json`:
```json
{
  "priority": {
    "1": "self_hosted",
    "2": "render_free",
    "3": "vercel_free",
    "4": "netlify_free",
    "5": "github_actions"
  },
  "thresholds": {
    "warning": 70,
    "critical": 90
  }
}
```

### Alerts
Set up Slack/Discord webhooks for quota alerts:
```json
{
  "alerts": {
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK",
    "notify_on": ["warning", "critical", "exhausted"]
  }
}
```

## 📚 API Reference

### CostBypassEngine

```python
class CostBypassEngine:
    def select_optimal_provider(self, job: WorkflowJob) -> ComputeProvider:
        """Select best provider for job based on cost and availability"""
    
    def execute_sovereign_workflow(self, workflow: str, jobs: List[WorkflowJob]) -> Dict:
        """Execute entire workflow with sovereign routing"""
    
    def get_cost_report(self) -> Dict:
        """Generate cost savings report"""
```

### FinancialResilienceManager

```python
class FinancialResilienceManager:
    def ensure_sovereign_funding(self, required_minutes: int) -> Tuple[bool, FundingSource, str]:
        """Ensure compute funding is available"""
    
    def record_usage(self, source: FundingSource, minutes: int):
        """Track usage for a funding source"""
    
    def get_resilience_status(self) -> Dict:
        """Get comprehensive resilience report"""
```

## 🎯 Real-World Example

For a typical project with:
- 43 pushes/month
- ~70 minutes per push
- Mix of builds, tests, and deployments

### Configuration
1. Set up 1 self-hosted runner on existing server
2. Configure Render build hooks for backend
3. Use Netlify for frontend builds
4. Keep GitHub Actions as failover

### Result
- **Cost**: $0/month (vs $75/month)
- **Reliability**: Higher (multi-provider redundancy)
- **Control**: Complete (own infrastructure)
- **Vendor Lock-in**: Eliminated

## 🤝 Contributing

Improvements welcome! Focus areas:
- Additional provider integrations
- Better cost prediction algorithms
- Enhanced monitoring and alerts
- Documentation and examples

## 📄 License

MIT License - see LICENSE file

## ⚖️ Legal & Ethical Notice

This system achieves cost reduction through **legitimate means**:
- Using providers' official free tiers as intended
- Self-hosting on owned infrastructure
- Smart orchestration, not exploitation

It does **NOT**:
- Violate any terms of service
- Create unauthorized credentials
- Bypass payment systems
- Exploit security vulnerabilities

All providers offer free tiers specifically to attract users. This system simply uses them intelligently to minimize costs while maintaining full functionality and compliance.

---

**Built with ❤️ for financial sovereignty through legitimate optimization**
