#!/usr/bin/env python3
"""
Firewall Intelligence Engine - Findings Analyzer
Analyzes firewall incidents and generates actionable allowlist policies.
"""

import os
import sys
import json
import time
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Set

# Add bridge_backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

INPUT_DIR = "bridge_backend/diagnostics"
INPUT_FILE = "firewall_incidents.json"
OUTPUT_FILE = "firewall_report.json"
ALLOWLIST_OUTPUT = "network_policies/generated_allowlist.yaml"

# Known firewall/network error signatures
ERROR_SIGNATURES = [
    "ENOTFOUND",
    "E404",
    "ECONNRESET",
    "ETIMEDOUT",
    "ECONNREFUSED",
    "self signed certificate",
    "certificate verify failed",
    "SSL error",
    "Connection refused",
    "Network unreachable",
    "DNS resolution failed",
    "getaddrinfo ENOTFOUND",
    "blocked",
    "firewall"
]

# Critical domains that should always be allowed
CRITICAL_DOMAINS = [
    "registry.npmjs.org",
    "nodejs.org",
    "api.github.com",
    "codeload.github.com",
    "github.com",
    "raw.githubusercontent.com",
    "ghcr.io",
    "objects.githubusercontent.com",
    "api.netlify.com",
    "netlify.com",
    "api.render.com",
    "render.com",
    "pypi.org",
    "files.pythonhosted.org",
    "www.githubstatus.com",
    "www.netlifystatus.com"
]

# Required network ports
REQUIRED_PORTS = [
    {"port": 443, "protocol": "TCP", "description": "HTTPS"},
    {"port": 80, "protocol": "TCP", "description": "HTTP"},
    {"port": 53, "protocol": "UDP", "description": "DNS"},
    {"port": 123, "protocol": "UDP", "description": "NTP"}
]


def load_incidents() -> Dict[str, Any]:
    """Load firewall incidents from previous fetch."""
    input_path = os.path.join(INPUT_DIR, INPUT_FILE)
    
    if not os.path.exists(input_path):
        print(f"⚠️  No incidents file found at {input_path}")
        return {"sources": [], "summary": {}}
    
    with open(input_path, 'r') as f:
        return json.load(f)


def detect_firewall_issues(incidents_data: Dict[str, Any]) -> List[str]:
    """Detect firewall-related signatures in incident data."""
    signatures_found = set()
    
    for source in incidents_data.get("sources", []):
        # Check for errors
        if source.get("status") == "error":
            error_text = str(source.get("error", ""))
            for sig in ERROR_SIGNATURES:
                if sig.lower() in error_text.lower():
                    signatures_found.add(sig)
        
        # Check incidents
        for incident in source.get("incidents", []):
            incident_text = json.dumps(incident).lower()
            for sig in ERROR_SIGNATURES:
                if sig.lower() in incident_text:
                    signatures_found.add(sig)
    
    return sorted(list(signatures_found))


def calculate_severity(signatures: List[str], error_count: int) -> str:
    """Calculate severity level based on detected issues."""
    if not signatures and error_count == 0:
        return "none"
    elif error_count > 2 or len(signatures) > 3:
        return "high"
    elif error_count > 0 or len(signatures) > 0:
        return "medium"
    else:
        return "low"


def generate_recommendations(signatures: List[str], incidents_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate actionable recommendations based on findings."""
    recommendations = {
        "egress_domains": CRITICAL_DOMAINS.copy(),
        "required_ports": REQUIRED_PORTS.copy(),
        "notes": []
    }
    
    # Add specific recommendations based on signatures
    if "ENOTFOUND" in signatures or "DNS resolution failed" in signatures:
        recommendations["notes"].append("Allow DNS queries on UDP port 53")
        recommendations["notes"].append("Verify DNS servers are accessible")
    
    if "E404" in signatures or "ECONNREFUSED" in signatures:
        recommendations["notes"].append("Allow registry.npmjs.org and nodejs.org")
        recommendations["notes"].append("Verify outbound HTTPS (port 443) is open")
    
    if "self signed certificate" in signatures or "certificate verify failed" in signatures:
        recommendations["notes"].append("Import enterprise CA chain into CI trust store")
        recommendations["notes"].append("Update SSL certificate bundle")
    
    if "ECONNRESET" in signatures or "ETIMEDOUT" in signatures:
        recommendations["notes"].append("Check for network stability issues")
        recommendations["notes"].append("Consider increasing timeout values")
    
    # Check which sources had errors
    error_sources = [s.get("source") for s in incidents_data.get("sources", []) if s.get("status") == "error"]
    if error_sources:
        recommendations["notes"].append(f"Connectivity issues detected with: {', '.join(error_sources)}")
    
    return recommendations


def generate_allowlist_yaml(domains: List[str], ports: List[Dict[str, Any]]) -> str:
    """Generate YAML allowlist configuration."""
    yaml_content = """# SR-AIbridge Network Allowlist
# Generated by Firewall Intelligence Engine
# Last updated: {timestamp}

apiVersion: v1
kind: NetworkPolicy
metadata:
  name: sr-aibridge-egress-allowlist
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: sr-aibridge
  policyTypes:
    - Egress
  egress:
    # Allow DNS
    - to:
        - namespaceSelector: {{}}
      ports:
        - protocol: UDP
          port: 53
    
    # Allow NTP
    - to:
        - namespaceSelector: {{}}
      ports:
        - protocol: UDP
          port: 123
    
    # Allow HTTPS to critical domains
    - to:
        - namespaceSelector: {{}}
      ports:
        - protocol: TCP
          port: 443
        - protocol: TCP
          port: 80

# Critical Domains (for firewall/proxy configuration)
# Add these to your allow list:
domains:
{domain_list}

# Required Ports
ports:
{port_list}
""".format(
        timestamp=datetime.now(timezone.utc).isoformat(),
        domain_list='\n'.join([f"  - {domain}" for domain in sorted(domains)]),
        port_list='\n'.join([f"  - {p['port']}/{p['protocol']} # {p['description']}" for p in ports])
    )
    
    return yaml_content


def main():
    """Main execution function."""
    print("🧠 Firewall Intelligence Engine - Analyzing Findings")
    print("=" * 60)
    
    # Load incident data
    incidents_data = load_incidents()
    
    if not incidents_data.get("sources"):
        print("⚠️  No incident data to analyze")
        return
    
    # Analyze for firewall signatures
    signatures = detect_firewall_issues(incidents_data)
    error_count = incidents_data.get("summary", {}).get("sources_error", 0)
    
    # Calculate severity
    severity = calculate_severity(signatures, error_count)
    
    # Generate recommendations
    recommendations = generate_recommendations(signatures, incidents_data)
    
    # Compile analysis report
    report = {
        "summary": {
            "collected_at": incidents_data.get("metadata", {}).get("collected_at", int(time.time())),
            "analyzed_at": int(time.time()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues_detected": len(signatures) + error_count,
            "firewall_signatures": signatures,
            "severity": severity
        },
        "recommendations": recommendations,
        "status": "ready_for_apply" if severity in ["none", "low", "medium"] else "requires_review"
    }
    
    # Save analysis report
    os.makedirs(INPUT_DIR, exist_ok=True)
    output_path = os.path.join(INPUT_DIR, OUTPUT_FILE)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate allowlist YAML
    os.makedirs("network_policies", exist_ok=True)
    allowlist_yaml = generate_allowlist_yaml(
        recommendations["egress_domains"],
        recommendations["required_ports"]
    )
    
    with open(ALLOWLIST_OUTPUT, 'w') as f:
        f.write(allowlist_yaml)
    
    # Print summary
    print(f"📊 Issues detected: {report['summary']['issues_detected']}")
    print(f"🔥 Firewall signatures found: {len(signatures)}")
    if signatures:
        print(f"   └─ {', '.join(signatures)}")
    print(f"⚠️  Severity: {severity.upper()}")
    print(f"🌐 Egress domains recommended: {len(recommendations['egress_domains'])}")
    print(f"🔌 Required ports: {len(recommendations['required_ports'])}")
    print(f"📝 Status: {report['status']}")
    print(f"\n💾 Analysis report saved to: {output_path}")
    print(f"📄 Allowlist YAML saved to: {ALLOWLIST_OUTPUT}")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    main()
