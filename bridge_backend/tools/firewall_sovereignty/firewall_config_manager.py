#!/usr/bin/env python3
"""
Firewall Configuration Manager
Sovereign control over firewall rules and network policies at architectural level
"""

import os
import json
import yaml
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path


class FirewallConfigManager:
    """
    Centralized Firewall Configuration Management
    
    Provides sovereign control over:
    - Firewall rule configuration
    - Network egress policies
    - Allowlist/blocklist management
    - Policy validation and enforcement
    """
    
    def __init__(self, config_dir: str = "network_policies"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.allowlist_file = self.config_dir / "sovereign_allowlist.yaml"
        self.egress_policy_file = self.config_dir / "egress_policies.yaml"
        self.firewall_rules_file = self.config_dir / "firewall_rules.yaml"
        
        self.allowlist = self._load_allowlist()
        self.egress_policies = self._load_egress_policies()
        self.firewall_rules = self._load_firewall_rules()
    
    def _load_allowlist(self) -> Dict[str, Any]:
        """Load sovereign allowlist configuration"""
        if self.allowlist_file.exists():
            with open(self.allowlist_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Initialize with default sovereign allowlist
        default_allowlist = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "domains": {
                "critical": [
                    "api.netlify.com",
                    "bridge.sr-aibridge.com",
                    "diagnostics.sr-aibridge.com"
                ],
                "infrastructure": [
                    "github.com",
                    "api.github.com",
                    "registry.npmjs.org",
                    "pypi.org"
                ],
                "monitoring": [
                    "sentry.io"
                ],
                "browser_downloads": [
                    "googlechromelabs.github.io",
                    "storage.googleapis.com",
                    "edgedl.me.gvt1.com",
                    "playwright.azureedge.net"
                ]
            },
            "ip_ranges": {
                "netlify": ["44.211.0.0/16", "52.2.0.0/15"],
                "github": ["140.82.112.0/20", "143.55.64.0/20"]
            }
        }
        
        self._save_allowlist(default_allowlist)
        return default_allowlist
    
    def _save_allowlist(self, allowlist: Dict[str, Any]) -> None:
        """Save allowlist configuration"""
        allowlist["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.allowlist_file, 'w') as f:
            yaml.dump(allowlist, f, default_flow_style=False, sort_keys=False)
    
    def _load_egress_policies(self) -> Dict[str, Any]:
        """Load network egress policies"""
        if self.egress_policy_file.exists():
            with open(self.egress_policy_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Initialize with default egress policies
        default_policies = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "policies": {
                "default_action": "deny",
                "allowed_protocols": ["https", "http"],
                "allowed_ports": [80, 443, 8080, 3000],
                "dns_resolution": {
                    "primary": ["8.8.8.8", "8.8.4.4"],
                    "fallback": ["1.1.1.1", "1.0.0.1"]
                },
                "retry_policy": {
                    "max_retries": 3,
                    "backoff_multiplier": 2,
                    "initial_delay_ms": 1000
                },
                "timeout_policy": {
                    "connection_timeout_s": 10,
                    "read_timeout_s": 30,
                    "total_timeout_s": 60
                }
            }
        }
        
        self._save_egress_policies(default_policies)
        return default_policies
    
    def _save_egress_policies(self, policies: Dict[str, Any]) -> None:
        """Save egress policies"""
        policies["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.egress_policy_file, 'w') as f:
            yaml.dump(policies, f, default_flow_style=False, sort_keys=False)
    
    def _load_firewall_rules(self) -> Dict[str, Any]:
        """Load firewall rules configuration"""
        if self.firewall_rules_file.exists():
            with open(self.firewall_rules_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Initialize with default firewall rules
        default_rules = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "rules": [
                {
                    "id": "allow_critical_domains",
                    "action": "allow",
                    "priority": 100,
                    "source": "any",
                    "destination": "critical_domains",
                    "protocol": "https",
                    "enabled": True
                },
                {
                    "id": "allow_infrastructure",
                    "action": "allow",
                    "priority": 90,
                    "source": "any",
                    "destination": "infrastructure_domains",
                    "protocol": "https",
                    "enabled": True
                },
                {
                    "id": "allow_browser_downloads",
                    "action": "allow",
                    "priority": 85,
                    "source": "any",
                    "destination": "browser_download_domains",
                    "protocol": "https",
                    "enabled": True,
                    "description": "Allow browser downloads for Playwright/Puppeteer (Chrome, Chromium, etc.)"
                },
                {
                    "id": "block_unknown",
                    "action": "log_and_notify",
                    "priority": 10,
                    "source": "any",
                    "destination": "unknown",
                    "protocol": "any",
                    "enabled": True
                }
            ]
        }
        
        self._save_firewall_rules(default_rules)
        return default_rules
    
    def _save_firewall_rules(self, rules: Dict[str, Any]) -> None:
        """Save firewall rules"""
        rules["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.firewall_rules_file, 'w') as f:
            yaml.dump(rules, f, default_flow_style=False, sort_keys=False)
    
    def add_domain_to_allowlist(self, domain: str, category: str = "infrastructure") -> bool:
        """Add a domain to the allowlist"""
        if category not in self.allowlist.get("domains", {}):
            self.allowlist.setdefault("domains", {})[category] = []
        
        if domain not in self.allowlist["domains"][category]:
            self.allowlist["domains"][category].append(domain)
            self._save_allowlist(self.allowlist)
            return True
        return False
    
    def remove_domain_from_allowlist(self, domain: str, category: Optional[str] = None) -> bool:
        """Remove a domain from the allowlist"""
        removed = False
        
        if category:
            categories = [category]
        else:
            categories = self.allowlist.get("domains", {}).keys()
        
        for cat in categories:
            if domain in self.allowlist.get("domains", {}).get(cat, []):
                self.allowlist["domains"][cat].remove(domain)
                removed = True
        
        if removed:
            self._save_allowlist(self.allowlist)
        
        return removed
    
    def is_domain_allowed(self, domain: str) -> bool:
        """Check if a domain is in the allowlist"""
        for category in self.allowlist.get("domains", {}).values():
            if domain in category:
                return True
        return False
    
    def get_all_allowed_domains(self) -> List[str]:
        """Get all allowed domains"""
        domains = []
        for category in self.allowlist.get("domains", {}).values():
            domains.extend(category)
        return list(set(domains))
    
    def validate_firewall_config(self) -> Dict[str, Any]:
        """Validate current firewall configuration"""
        validation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check allowlist
        if not self.allowlist.get("domains"):
            validation["errors"].append("No domains in allowlist")
            validation["valid"] = False
        
        # Check egress policies
        if not self.egress_policies.get("policies"):
            validation["errors"].append("No egress policies defined")
            validation["valid"] = False
        
        # Check firewall rules
        if not self.firewall_rules.get("rules"):
            validation["errors"].append("No firewall rules defined")
            validation["valid"] = False
        
        return validation
    
    def export_config(self, output_file: str) -> None:
        """Export complete firewall configuration"""
        config = {
            "version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "allowlist": self.allowlist,
            "egress_policies": self.egress_policies,
            "firewall_rules": self.firewall_rules
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate configuration summary"""
        total_domains = sum(len(domains) for domains in self.allowlist.get("domains", {}).values())
        total_rules = len(self.firewall_rules.get("rules", []))
        
        return {
            "total_allowed_domains": total_domains,
            "domain_categories": len(self.allowlist.get("domains", {})),
            "total_firewall_rules": total_rules,
            "egress_default_action": self.egress_policies.get("policies", {}).get("default_action", "unknown"),
            "last_updated": self.allowlist.get("last_updated", "unknown")
        }


def main():
    """Main execution for firewall configuration management"""
    print("🛡️ Firewall Configuration Manager - Sovereign Edition")
    print("=" * 70)
    
    manager = FirewallConfigManager()
    
    # Validate configuration
    validation = manager.validate_firewall_config()
    print(f"\n✅ Configuration Validation: {'PASSED' if validation['valid'] else 'FAILED'}")
    
    if validation['errors']:
        print("\n❌ Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("\n⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Display summary
    summary = manager.generate_summary()
    print("\n📊 Configuration Summary:")
    print(f"  Total Allowed Domains: {summary['total_allowed_domains']}")
    print(f"  Domain Categories: {summary['domain_categories']}")
    print(f"  Firewall Rules: {summary['total_firewall_rules']}")
    print(f"  Default Egress Action: {summary['egress_default_action'].upper()}")
    print(f"  Last Updated: {summary['last_updated']}")
    
    # Export configuration
    export_file = "network_policies/firewall_config_export.json"
    manager.export_config(export_file)
    print(f"\n💾 Configuration exported to: {export_file}")
    
    print("\n" + "=" * 70)
    print("✅ Firewall Configuration Management Complete")


if __name__ == "__main__":
    main()
