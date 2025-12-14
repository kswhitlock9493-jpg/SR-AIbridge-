# Bridge Network Diagnostics v1.7.2
Verifies external connectivity and TLS trust chains for all core Bridge domains.

## Run Locally
```bash
python3 bridge_backend/tools/network_diagnostics/check_copilot_access.py
```

## Outputs
- `bridge_backend/diagnostics/copilot_network_report.json` – full status log  
- Artifacts uploaded via GitHub Actions → copilot_network_report

## Indicators
- 🟢 **BRIDGE NETWORK STABLE** – all domains resolving and TLS verified  
- 🟡 **PARTIAL CONNECTIVITY** – some domains timeout or reject TLS  
- 🔴 **CRITICAL FAILURE** – majority of domains unreachable or blocked  

## Why It Matters
Ensures Copilot and CI/CD agents maintain trusted network channels.  
Guarantees the Bridge can self-diagnose and report before deployments fail.

## Tested Domains
The diagnostic suite verifies connectivity to:
- GitHub API and CDN endpoints
- Netlify and Render APIs
- Bridge service endpoints
- Package registries (npm, PyPI)
- Node.js infrastructure
- Status pages

## Workflow Automation
The network diagnostics run automatically:
- Daily at 06:00 UTC via scheduled workflow
- On-demand via workflow_dispatch
- Results are uploaded as GitHub Actions artifacts for 30-90 days

## Report Schema
```json
{
  "summary": {
    "reachable": 17,
    "total": 17,
    "timestamp": 1234567890.123
  },
  "status": "🟢 BRIDGE NETWORK STABLE",
  "tls": [
    {
      "domain": "https://api.github.com",
      "status": "reachable",
      "latency": 0.15,
      "subject": [...]
    }
  ],
  "http": [
    {
      "domain": "https://api.github.com",
      "http_status": 200,
      "ok": true
    }
  ]
}
```

## Integration with Other Tools
This diagnostic suite complements:
- **Firewall Watchdog** (`scripts/firewall_watchdog.py`) - DNS resolution monitoring
- **Firewall Intelligence Engine** (`bridge_backend/tools/firewall_intel/`) - Incident analysis
- **Parity Engine** (`bridge_backend/tools/parity_engine.py`) - Environment verification
- **Deploy Diagnostics** (`bridge_backend/scripts/deploy_diagnose.py`) - Post-deployment checks
