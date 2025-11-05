#!/usr/bin/env python3
"""
Validation Sovereignty System
Comprehensive validation framework for headers, configs, and system integrity
"""

import os
import re
import yaml
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path


class ValidationSovereignty:
    """
    Sovereign Validation Framework
    
    Provides comprehensive validation for:
    - HTTP headers
    - Configuration files
    - Network policies
    - System integrity
    """
    
    def __init__(self):
        self.validation_history = []
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules"""
        return {
            "headers": {
                "required": [
                    "X-Frame-Options",
                    "X-Content-Type-Options",
                    "Referrer-Policy"
                ],
                "recommended": [
                    "Strict-Transport-Security",
                    "Content-Security-Policy"
                ],
                "patterns": {
                    "X-Frame-Options": r"^(DENY|SAMEORIGIN|ALLOW-FROM .+)$",
                    "X-Content-Type-Options": r"^nosniff$",
                    "Referrer-Policy": r"^(no-referrer|no-referrer-when-downgrade|origin|origin-when-cross-origin|same-origin|strict-origin|strict-origin-when-cross-origin|unsafe-url)$"
                }
            },
            "netlify_config": {
                "required_sections": ["build", "headers"],
                "required_build_keys": ["command", "publish"],
                "security_headers": [
                    "X-Frame-Options",
                    "X-Content-Type-Options",
                    "Strict-Transport-Security"
                ]
            },
            "network_policies": {
                "required_keys": ["version", "domains"],
                "domain_pattern": r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
            }
        }
    
    def validate_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate HTTP security headers
        
        Args:
            headers: Dictionary of header name-value pairs
        
        Returns:
            Validation results
        """
        validation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        rules = self.validation_rules["headers"]
        
        # Check required headers
        for required_header in rules["required"]:
            if required_header not in headers:
                validation["errors"].append(f"Missing required header: {required_header}")
                validation["valid"] = False
        
        # Check recommended headers
        for recommended_header in rules["recommended"]:
            if recommended_header not in headers:
                validation["warnings"].append(f"Missing recommended header: {recommended_header}")
        
        # Validate header values against patterns
        for header_name, pattern in rules["patterns"].items():
            if header_name in headers:
                value = headers[header_name]
                if not re.match(pattern, value, re.IGNORECASE):
                    validation["errors"].append(
                        f"Invalid value for {header_name}: '{value}' does not match pattern"
                    )
                    validation["valid"] = False
        
        self.validation_history.append({
            "type": "headers",
            "timestamp": validation["timestamp"],
            "valid": validation["valid"]
        })
        
        return validation
    
    def validate_netlify_config(self, config_path: str) -> Dict[str, Any]:
        """
        Validate Netlify configuration file
        
        Args:
            config_path: Path to netlify.toml
        
        Returns:
            Validation results
        """
        validation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check if file exists
        if not Path(config_path).exists():
            validation["errors"].append(f"Configuration file not found: {config_path}")
            validation["valid"] = False
            return validation
        
        try:
            # Read TOML file (simple parsing for key sections)
            with open(config_path, 'r') as f:
                content = f.read()
            
            rules = self.validation_rules["netlify_config"]
            
            # Check for required sections
            for section in rules["required_sections"]:
                if f"[{section}]" not in content and f"[[{section}]]" not in content:
                    validation["errors"].append(f"Missing required section: [{section}]")
                    validation["valid"] = False
            
            # Check for security headers
            headers_found = False
            for security_header in rules["security_headers"]:
                if security_header in content:
                    headers_found = True
                else:
                    validation["warnings"].append(
                        f"Security header not found in config: {security_header}"
                    )
            
            if not headers_found:
                validation["errors"].append("No security headers configured")
                validation["valid"] = False
            
            # Check for build configuration
            if "[build]" in content:
                for key in rules["required_build_keys"]:
                    # Simple check - look for key = value pattern
                    if not re.search(rf'{key}\s*=\s*".+"', content):
                        validation["warnings"].append(f"Build key '{key}' may not be configured")
            
            self.validation_history.append({
                "type": "netlify_config",
                "timestamp": validation["timestamp"],
                "valid": validation["valid"]
            })
        
        except Exception as e:
            validation["errors"].append(f"Error reading configuration: {str(e)}")
            validation["valid"] = False
        
        return validation
    
    def validate_network_policies(self, policy_file: str) -> Dict[str, Any]:
        """
        Validate network policy configuration
        
        Args:
            policy_file: Path to network policy file
        
        Returns:
            Validation results
        """
        validation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        if not Path(policy_file).exists():
            validation["errors"].append(f"Policy file not found: {policy_file}")
            validation["valid"] = False
            return validation
        
        try:
            with open(policy_file, 'r') as f:
                if policy_file.endswith('.yaml') or policy_file.endswith('.yml'):
                    policies = yaml.safe_load(f)
                else:
                    policies = json.load(f)
            
            rules = self.validation_rules["network_policies"]
            
            # Check required keys
            for key in rules["required_keys"]:
                if key not in policies:
                    validation["errors"].append(f"Missing required key: {key}")
                    validation["valid"] = False
            
            # Validate domain format
            if "domains" in policies:
                domain_pattern = rules["domain_pattern"]
                for category, domains in policies["domains"].items():
                    if isinstance(domains, list):
                        for domain in domains:
                            if not re.match(domain_pattern, domain):
                                validation["warnings"].append(
                                    f"Domain '{domain}' in category '{category}' may have invalid format"
                                )
            
            self.validation_history.append({
                "type": "network_policies",
                "timestamp": validation["timestamp"],
                "valid": validation["valid"]
            })
        
        except yaml.YAMLError as e:
            validation["errors"].append(f"YAML parsing error: {str(e)}")
            validation["valid"] = False
        except json.JSONDecodeError as e:
            validation["errors"].append(f"JSON parsing error: {str(e)}")
            validation["valid"] = False
        except Exception as e:
            validation["errors"].append(f"Error validating policies: {str(e)}")
            validation["valid"] = False
        
        return validation
    
    def validate_all(self, config_paths: Dict[str, str]) -> Dict[str, Any]:
        """
        Perform comprehensive validation across all systems
        
        Args:
            config_paths: Dictionary of config type to file path
        
        Returns:
            Comprehensive validation results
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_valid": True,
            "validations": {}
        }
        
        # Validate Netlify config
        if "netlify_config" in config_paths:
            netlify_result = self.validate_netlify_config(config_paths["netlify_config"])
            results["validations"]["netlify_config"] = netlify_result
            if not netlify_result["valid"]:
                results["overall_valid"] = False
        
        # Validate network policies
        if "network_policies" in config_paths:
            policy_result = self.validate_network_policies(config_paths["network_policies"])
            results["validations"]["network_policies"] = policy_result
            if not policy_result["valid"]:
                results["overall_valid"] = False
        
        # Validate headers file
        if "headers_file" in config_paths:
            headers_result = self._validate_headers_file(config_paths["headers_file"])
            results["validations"]["headers_file"] = headers_result
            if not headers_result["valid"]:
                results["overall_valid"] = False
        
        return results
    
    def _validate_headers_file(self, headers_file: str) -> Dict[str, Any]:
        """Validate standalone headers file"""
        validation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not Path(headers_file).exists():
            validation["errors"].append(f"Headers file not found: {headers_file}")
            validation["valid"] = False
            return validation
        
        try:
            with open(headers_file, 'r') as f:
                content = f.read()
            
            # Check for security headers
            security_headers = self.validation_rules["headers"]["required"]
            for header in security_headers:
                if header not in content:
                    validation["warnings"].append(f"Missing header: {header}")
        
        except Exception as e:
            validation["errors"].append(f"Error reading headers file: {str(e)}")
            validation["valid"] = False
        
        return validation
    
    def auto_heal_validation_failures(
        self,
        validation_results: Dict[str, Any],
        config_paths: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Automatically heal validation failures where possible
        
        Args:
            validation_results: Results from validation
            config_paths: Paths to config files
        
        Returns:
            Healing results
        """
        healing_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "healed": [],
            "failed_to_heal": [],
            "no_action_needed": []
        }
        
        for config_type, validation in validation_results.get("validations", {}).items():
            if validation["valid"]:
                healing_results["no_action_needed"].append(config_type)
                continue
            
            # Attempt to heal based on config type
            if config_type == "netlify_config":
                # Auto-heal netlify config (add missing headers, etc.)
                try:
                    self._heal_netlify_config(
                        config_paths.get("netlify_config"),
                        validation["errors"]
                    )
                    healing_results["healed"].append(config_type)
                except Exception as e:
                    healing_results["failed_to_heal"].append({
                        "type": config_type,
                        "error": str(e)
                    })
        
        return healing_results
    
    def _heal_netlify_config(self, config_path: str, errors: List[str]) -> None:
        """
        Heal netlify configuration issues
        
        Args:
            config_path: Path to netlify.toml
            errors: List of errors to heal
        """
        if not Path(config_path).exists():
            return
        
        # Read current config
        with open(config_path, 'r') as f:
            content = f.read()
        
        healed = False
        
        # Check for missing security headers section
        if "Missing required section: [headers]" in errors or "Missing required section: [[headers]]" in errors:
            if "[[headers]]" not in content:
                # Add basic security headers section
                headers_section = """
# Security headers
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "no-referrer-when-downgrade"
"""
                content += headers_section
                healed = True
        
        # Check for missing build section
        if "Missing required section: [build]" in errors:
            if "[build]" not in content:
                # Add basic build section
                build_section = """
[build]
  command = "npm run build"
  publish = "dist"
"""
                content = build_section + "\n" + content
                healed = True
        
        # Write back if healed
        if healed:
            with open(config_path, 'w') as f:
                f.write(content)
    
    def export_validation_report(self, output_file: str, validation_results: Dict[str, Any]) -> None:
        """Export validation results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "validation_results": validation_results,
            "validation_history": self.validation_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """Main execution for validation sovereignty"""
    print("🔒 Validation Sovereignty System")
    print("=" * 70)
    
    validator = ValidationSovereignty()
    
    # Define config paths
    config_paths = {
        "netlify_config": "netlify.toml",
        "network_policies": "network_policies/sovereign_allowlist.yaml",
        "headers_file": "_headers"
    }
    
    print("\n🔍 Performing comprehensive validation...")
    results = validator.validate_all(config_paths)
    
    print(f"\n📊 Validation Results:")
    print(f"  Overall Valid: {'✅ YES' if results['overall_valid'] else '❌ NO'}")
    print(f"  Total Validations: {len(results['validations'])}")
    
    for config_type, validation in results["validations"].items():
        status = "✅" if validation["valid"] else "❌"
        print(f"\n  {status} {config_type.upper()}")
        
        if validation["errors"]:
            print(f"    Errors: {len(validation['errors'])}")
            for error in validation["errors"][:3]:  # Show first 3
                print(f"      - {error}")
        
        if validation["warnings"]:
            print(f"    Warnings: {len(validation['warnings'])}")
            for warning in validation["warnings"][:3]:  # Show first 3
                print(f"      - {warning}")
    
    # Export results
    output_file = "bridge_backend/diagnostics/validation_report.json"
    validator.export_validation_report(output_file, results)
    print(f"\n💾 Validation report exported to: {output_file}")
    
    print("\n" + "=" * 70)
    print("✅ Validation Sovereignty Check Complete")


if __name__ == "__main__":
    main()
