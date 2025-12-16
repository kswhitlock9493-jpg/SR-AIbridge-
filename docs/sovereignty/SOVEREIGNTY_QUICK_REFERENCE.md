# Sovereignty Quick Reference

## One-Line Commands

### Execute Complete Sovereignty Protocol
```bash
python3 bridge_backend/tools/firewall_sovereignty/sovereign_orchestrator.py
```

### Individual Systems

#### Firewall Configuration
```bash
python3 bridge_backend/tools/firewall_sovereignty/firewall_config_manager.py
```

#### Network Health Check
```bash
python3 bridge_backend/tools/firewall_sovereignty/network_resilience.py
```

#### Validation Check
```bash
python3 bridge_backend/tools/firewall_sovereignty/validation_sovereignty.py
```

#### Script Execution Check
```bash
python3 bridge_backend/tools/firewall_sovereignty/script_execution.py
```

### Run All Tests
```bash
python3 -m pytest bridge_backend/tests/test_firewall_sovereignty.py -v
```

## View Reports

### Latest Sovereignty Report
```bash
cat bridge_backend/diagnostics/sovereignty_report_latest.json | python3 -m json.tool
```

### Network Health
```bash
cat bridge_backend/diagnostics/network_health_report.json | python3 -m json.tool
```

### Validation Results
```bash
cat bridge_backend/diagnostics/validation_report.json | python3 -m json.tool
```

## Key Metrics Quick Check

```bash
python3 << 'EOF'
import json

with open('bridge_backend/diagnostics/sovereignty_report_latest.json') as f:
    report = json.load(f)
    
summary = report['summary']
systems = report['systems']

print("🎯 SOVEREIGNTY STATUS")
print("=" * 50)
print(f"Overall Status: {summary['overall_status'].upper()}")
print(f"\n🛡️  Firewall: {systems['firewall']['summary']['total_allowed_domains']} domains")
print(f"🌐 Network: {systems['network']['health_check']['successful']}/{systems['network']['health_check']['total_checked']} healthy")
print(f"🔒 Validation: {len(systems['validation']['validation_results']['validations'])} systems")
print(f"⚙️  Scripts: {systems['script_execution']['script_health']['accessible']}/{systems['script_execution']['script_health']['total_scripts']} ready")

print("\n📋 RECOMMENDATIONS:")
for i, rec in enumerate(summary['recommendations'], 1):
    print(f"{i}. {rec}")
EOF
```

## Configuration Files

### Allowlist
```bash
cat network_policies/sovereign_allowlist.yaml
```

### Egress Policies
```bash
cat network_policies/egress_policies.yaml
```

### Firewall Rules
```bash
cat network_policies/firewall_rules.yaml
```

## GitHub Actions

### Trigger Sovereignty Check
```bash
gh workflow run sovereign_architecture.yml
```

### View Latest Run
```bash
gh run list --workflow=sovereign_architecture.yml --limit 1
```

## Common Tasks

### Add Domain to Allowlist
```bash
python3 << 'EOF'
from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager

manager = FirewallConfigManager()
manager.add_domain_to_allowlist("example.com", "infrastructure")
print("✅ Domain added to allowlist")
EOF
```

### Check if Domain is Allowed
```bash
python3 << 'EOF'
from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager

manager = FirewallConfigManager()
domain = "api.github.com"
allowed = manager.is_domain_allowed(domain)
print(f"{'✅' if allowed else '❌'} {domain}: {'ALLOWED' if allowed else 'BLOCKED'}")
EOF
```

### Test Single Endpoint
```bash
python3 << 'EOF'
from bridge_backend.tools.firewall_sovereignty.network_resilience import NetworkResilienceLayer

resilience = NetworkResilienceLayer()
result = resilience.test_connection("https://api.github.com")
if result['success']:
    print(f"✅ Connection successful: {result['status_code']} ({result['response_time_ms']:.0f}ms)")
else:
    print(f"❌ Connection failed: {result.get('error', 'unknown')}")
EOF
```

## Troubleshooting

### Check System Status
```bash
python3 bridge_backend/tools/firewall_sovereignty/sovereign_orchestrator.py 2>&1 | grep -E "(✅|❌|⚠️)"
```

### View Error Details
```bash
python3 -c "
import json
with open('bridge_backend/diagnostics/sovereignty_report_latest.json') as f:
    report = json.load(f)
    for system_name, system_data in report['systems'].items():
        if 'validation' in system_data and not system_data['validation']['valid']:
            print(f'❌ {system_name}:')
            for error in system_data['validation'].get('errors', []):
                print(f'  - {error}')
"
```

### Reset and Regenerate All Configs
```bash
rm -rf network_policies/*.yaml network_policies/*.json
python3 bridge_backend/tools/firewall_sovereignty/firewall_config_manager.py
```

## Architecture Summary

```
👑 Sovereign Orchestrator
    │
    ├─ 🛡️  Firewall Config Manager
    │   ├─ Allowlist management
    │   ├─ Egress policies
    │   └─ Firewall rules
    │
    ├─ 🌐 Network Resilience Layer
    │   ├─ Connection retry
    │   ├─ DNS fallback
    │   └─ Health monitoring
    │
    ├─ 🔒 Validation Sovereignty
    │   ├─ Header validation
    │   ├─ Config validation
    │   └─ Auto-healing
    │
    └─ ⚙️  Script Execution Sovereignty
        ├─ Environment detection
        ├─ Dependency validation
        └─ Script health checks
```

## Success Criteria

✅ All tests passing (22/22)
✅ All endpoints healthy (4/4)
✅ All validations passing
✅ All scripts accessible
✅ Overall status: HEALTHY

**SOVEREIGN AUTHORITY ESTABLISHED!**
