#!/usr/bin/env python3
"""
Firewall Intelligence Engine - Incident Fetcher
Fetches live incident data from GitHub Status, npm, Render, and Netlify.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any

# Add bridge_backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

OUTPUT_DIR = "bridge_backend/diagnostics"
OUTPUT_FILE = "firewall_incidents.json"

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
    "getaddrinfo",
    "blocked",
    "firewall"
]


def fetch_github_status() -> Dict[str, Any]:
    """Fetch GitHub status incidents."""
    try:
        response = requests.get("https://www.githubstatus.com/api/v2/incidents.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        incidents = []
        for incident in data.get("incidents", [])[:5]:  # Last 5 incidents
            incidents.append({
                "name": incident.get("name"),
                "status": incident.get("status"),
                "impact": incident.get("impact"),
                "created_at": incident.get("created_at"),
                "resolved_at": incident.get("resolved_at"),
                "components": [c.get("name") for c in incident.get("components", [])]
            })
        
        return {
            "source": "GitHub Status",
            "status": "online",
            "incidents": incidents,
            "count": len(incidents)
        }
    except Exception as e:
        return {
            "source": "GitHub Status",
            "status": "error",
            "error": str(e),
            "incidents": [],
            "count": 0
        }


def fetch_npm_status() -> Dict[str, Any]:
    """Fetch npm registry status."""
    try:
        response = requests.get("https://registry.npmjs.org/", timeout=10)
        response.raise_for_status()
        
        return {
            "source": "npm Registry",
            "status": "online",
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "incidents": []
        }
    except Exception as e:
        return {
            "source": "npm Registry",
            "status": "error",
            "error": str(e),
            "incidents": [{"type": "connectivity", "detail": str(e)}]
        }


def fetch_render_status() -> Dict[str, Any]:
    """Fetch Render status."""
    try:
        response = requests.get("https://api.render.com/", timeout=10)
        # Render API may return various status codes
        
        return {
            "source": "Render",
            "status": "reachable" if response.status_code < 500 else "degraded",
            "status_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "incidents": []
        }
    except Exception as e:
        return {
            "source": "Render",
            "status": "error",
            "error": str(e),
            "incidents": [{"type": "connectivity", "detail": str(e)}]
        }


def fetch_netlify_status() -> Dict[str, Any]:
    """Fetch Netlify status."""
    try:
        response = requests.get("https://www.netlifystatus.com/api/v2/status.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "source": "Netlify Status",
            "status": data.get("status", {}).get("description", "unknown"),
            "indicator": data.get("status", {}).get("indicator", "unknown"),
            "incidents": []
        }
    except Exception as e:
        return {
            "source": "Netlify Status",
            "status": "error",
            "error": str(e),
            "incidents": [{"type": "connectivity", "detail": str(e)}]
        }


def detect_firewall_signatures(text: str) -> List[str]:
    """Detect known firewall/network error signatures in text."""
    found = []
    text_lower = text.lower()
    for signature in ERROR_SIGNATURES:
        if signature.lower() in text_lower:
            found.append(signature)
    return list(set(found))  # Remove duplicates


def main():
    """Main execution function."""
    print("🔍 Firewall Intelligence Engine - Fetching Incidents")
    print("=" * 60)
    
    # Collect data from all sources
    sources = [
        fetch_github_status(),
        fetch_npm_status(),
        fetch_render_status(),
        fetch_netlify_status()
    ]
    
    # Compile report
    report = {
        "metadata": {
            "collected_at": int(time.time()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        },
        "sources": sources,
        "summary": {
            "total_sources": len(sources),
            "sources_online": sum(1 for s in sources if s.get("status") in ["online", "reachable"]),
            "sources_error": sum(1 for s in sources if s.get("status") == "error"),
            "total_incidents": sum(s.get("count", 0) for s in sources)
        }
    }
    
    # Save report
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Incident data collected from {report['summary']['total_sources']} sources")
    print(f"📊 Sources online: {report['summary']['sources_online']}")
    print(f"⚠️  Sources with errors: {report['summary']['sources_error']}")
    print(f"📝 Total incidents: {report['summary']['total_incidents']}")
    print(f"💾 Report saved to: {output_path}")
    print("=" * 60)
    
    return report


if __name__ == "__main__":
    main()
