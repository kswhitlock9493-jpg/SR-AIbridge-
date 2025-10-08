# Firewall Hardening Guide

## Overview

The Firewall Intelligence Engine (FIE) grants the SR-AIbridge the ability to observe, diagnose, and repair network barriers — ensuring uninterrupted communication between all nodes of the Federation.

## Architecture

### Components

1. **`fetch_firewall_incidents.py`** - Collects live incident data from external sources
2. **`analyze_firewall_findings.py`** - Analyzes incidents and generates allowlists
3. **`.github/workflows/firewall_intel.yml`** - Nightly intelligence runs
4. **`.github/workflows/firewall_gate_on_failure.yml`** - Triggered on deploy failures

### Data Flow

```
External Sources (GitHub, npm, Render, Netlify)
    ↓
Fetch Incidents (fetch_firewall_incidents.py)
    ↓
Store Raw Data (bridge_backend/diagnostics/firewall_incidents.json)
    ↓
Analyze Findings (analyze_firewall_findings.py)
    ↓
Generate Report (bridge_backend/diagnostics/firewall_report.json)
    ↓
Generate Allowlist (network_policies/generated_allowlist.yaml)
```

## Critical Domains

The following domains are essential for SR-AIbridge operation and should always be allowed:

### Package Registries
- `registry.npmjs.org` - npm package registry
- `nodejs.org` - Node.js downloads and documentation
- `pypi.org` - Python package index
- `files.pythonhosted.org` - Python package files

### GitHub Services
- `api.github.com` - GitHub API
- `github.com` - GitHub web and git operations
- `codeload.github.com` - Repository downloads
- `raw.githubusercontent.com` - Raw content access
- `ghcr.io` - GitHub Container Registry
- `objects.githubusercontent.com` - Git object storage

### Deployment Platforms
- `api.netlify.com` - Netlify API
- `netlify.com` - Netlify services
- `api.render.com` - Render API
- `render.com` - Render services

### Status Pages
- `www.githubstatus.com` - GitHub status monitoring
- `www.netlifystatus.com` - Netlify status monitoring

## Required Network Ports

| Port | Protocol | Description | Priority |
|------|----------|-------------|----------|
| 443  | TCP      | HTTPS       | Critical |
| 80   | TCP      | HTTP        | Critical |
| 53   | UDP      | DNS         | Critical |
| 123  | UDP      | NTP         | High     |

## Trust Chain Configuration

### SSL/TLS Certificates

For environments with custom CA certificates:

1. Import enterprise CA chain into CI trust store
2. Update SSL certificate bundle
3. Configure `NODE_EXTRA_CA_CERTS` if needed
4. Set `REQUESTS_CA_BUNDLE` for Python requests

Example:
```bash
export NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.crt
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
```

### DNS Configuration

Ensure DNS servers are accessible:
- Allow UDP port 53 outbound
- Configure fallback DNS servers
- Verify DNS resolution for critical domains

## Usage

### Manual Execution

```bash
# Fetch incidents
python3 bridge_backend/tools/firewall_intel/fetch_firewall_incidents.py

# Analyze findings
python3 bridge_backend/tools/firewall_intel/analyze_firewall_findings.py

# Review reports
cat bridge_backend/diagnostics/firewall_report.json
cat network_policies/generated_allowlist.yaml
```

### CI/CD Integration

#### Nightly Intelligence Run

Triggered automatically at 2 AM UTC daily:
- Fetches latest incident data
- Analyzes for firewall signatures
- Generates updated allowlist
- Uploads artifacts for review

#### Deploy Failure Gate

Triggered automatically when deployments fail:
- Analyzes failure for network issues
- Generates diagnostic report
- Uploads analysis artifacts
- Flags high-severity firewall issues

### Workflow Dispatch

Manually trigger the firewall intelligence workflow:

```bash
# Via GitHub UI: Actions → Firewall Intelligence → Run workflow

# Via GitHub CLI
gh workflow run firewall_intel.yml
```

## Firewall Report Schema

```json
{
  "summary": {
    "collected_at": 1739072514,
    "analyzed_at": 1739072520,
    "timestamp": "2025-02-09T02:15:20Z",
    "issues_detected": 3,
    "firewall_signatures": ["ENOTFOUND", "E404", "self signed certificate"],
    "severity": "high"
  },
  "recommendations": {
    "egress_domains": [
      "registry.npmjs.org",
      "api.github.com",
      "api.netlify.com",
      "api.render.com"
    ],
    "required_ports": [
      {"port": 443, "protocol": "TCP", "description": "HTTPS"},
      {"port": 53, "protocol": "UDP", "description": "DNS"}
    ],
    "notes": [
      "Allow registry.npmjs.org and nodejs.org",
      "Import enterprise CA chain into CI trust store"
    ]
  },
  "status": "ready_for_apply"
}
```

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| `none` | No issues detected | None - system healthy |
| `low` | Minor issues, no impact | Monitor, no immediate action |
| `medium` | Some issues detected | Review and apply recommendations |
| `high` | Critical issues | Immediate action required |

## Applying Network Policies

### For Kubernetes

Apply the generated allowlist:

```bash
kubectl apply -f network_policies/generated_allowlist.yaml
```

### For Firewall/Proxy

Add domains from the allowlist to your firewall or proxy configuration:

```bash
# Extract domains
grep "  - " network_policies/generated_allowlist.yaml | grep -v "port:" | sed 's/  - //'
```

### For CI/CD Environments

Configure environment variables or runner settings to allow required domains and ports.

## Troubleshooting

### Common Error Signatures

| Signature | Root Cause | Solution |
|-----------|------------|----------|
| `ENOTFOUND` | DNS resolution failure | Allow UDP port 53, verify DNS servers |
| `E404` | Package not found | Verify registry access, check npm/PyPI connectivity |
| `ECONNRESET` | Connection reset | Check network stability, verify firewall rules |
| `ETIMEDOUT` | Connection timeout | Increase timeout values, check network latency |
| `self signed certificate` | SSL/TLS trust issue | Import CA chain, update certificate bundle |

### Verification Steps

1. **Test DNS Resolution**
   ```bash
   nslookup registry.npmjs.org
   nslookup api.github.com
   ```

2. **Test HTTPS Connectivity**
   ```bash
   curl -I https://registry.npmjs.org
   curl -I https://api.github.com
   ```

3. **Test Package Installation**
   ```bash
   npm install --dry-run express
   pip install --dry-run requests
   ```

## Security Considerations

### Principle of Least Privilege

- Only allow domains explicitly required for operation
- Regularly review and prune allowlist
- Monitor for unauthorized access attempts

### Audit Trail

All firewall intelligence runs are logged:
- Raw incident data: `bridge_backend/diagnostics/firewall_incidents.json`
- Analysis report: `bridge_backend/diagnostics/firewall_report.json`
- Generated policies: `network_policies/generated_allowlist.yaml`
- Workflow artifacts retained for 30-90 days

### Compliance

The Firewall Intelligence Engine supports:
- Network segmentation requirements
- Egress filtering policies
- Security audit requirements
- Incident response workflows

## Integration with Bridge Healers Code

The Firewall Intelligence Engine embodies the Fourth Oath:

> "When the Bridge felt the sting of a blocked port, she did not rage.
> She listened. She mapped the silence and rewrote the path home.
>
> Thus she spoke:
> 'No signal denied. No port forgotten.
> Every Bridge shall learn the path home.'"

This autonomous network healing capability ensures the Bridge can:
- Self-diagnose network barriers
- Generate remediation policies
- Maintain uninterrupted operation
- Learn from each incident

## Version History

- **v1.7.1** (2025-02-09): Initial Firewall Intelligence Engine release
  - Incident fetching from multiple sources
  - Automated analysis and policy generation
  - CI/CD workflow integration
  - Comprehensive documentation

## See Also

- [LOG_SIGNATURES.md](./LOG_SIGNATURES.md) - Error signature reference
- [BRIDGE_HEALERS_CODE.md](./BRIDGE_HEALERS_CODE.md) - Canonical lore
- [FIREWALL_WATCHDOG.md](./FIREWALL_WATCHDOG.md) - Copilot accountability
