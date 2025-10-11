#!/usr/bin/env python3
"""
EnvSync Seed Manifest Validator

Validates the EnvSync Seed Manifest file structure and content.
Run this before deploying to ensure manifest integrity.

Usage:
    python3 scripts/validate_envsync_manifest.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def colored(text: str, color: str) -> str:
    """Add color to text for terminal output"""
    return f"{color}{text}{RESET}"

class ManifestValidator:
    """Validates the EnvSync Seed Manifest"""
    
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.variables: Dict[str, str] = {}
        self.metadata: Dict[str, str] = {}
    
    def validate(self) -> bool:
        """Run all validation checks"""
        print(colored("\n🔍 EnvSync Seed Manifest Validator", BLUE))
        print(colored("=" * 80, BLUE))
        
        checks = [
            ("File Exists", self._check_file_exists),
            ("File Format", self._check_file_format),
            ("Metadata Headers", self._check_metadata),
            ("Variable Format", self._check_variable_format),
            ("Required Variables", self._check_required_variables),
            ("Value Types", self._check_value_types),
            ("Security Check", self._check_security),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                passed = check_func()
                status = colored("✅ PASS", GREEN) if passed else colored("❌ FAIL", RED)
                print(f"\n{status}: {check_name}")
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"\n{colored('❌ ERROR', RED)}: {check_name}")
                print(f"   Exception: {e}")
                all_passed = False
        
        self._print_summary()
        return all_passed
    
    def _check_file_exists(self) -> bool:
        """Check if manifest file exists"""
        if not self.manifest_path.exists():
            self.errors.append(f"Manifest file not found at {self.manifest_path}")
            return False
        
        print(f"   Found: {self.manifest_path}")
        return True
    
    def _check_file_format(self) -> bool:
        """Check file can be parsed"""
        try:
            with open(self.manifest_path, 'r') as f:
                lines = f.readlines()
            
            print(f"   Total lines: {len(lines)}")
            return True
        except Exception as e:
            self.errors.append(f"Failed to read manifest: {e}")
            return False
    
    def _check_metadata(self) -> bool:
        """Check metadata headers are present"""
        required_metadata = [
            "Version:",
            "Purpose:",
            "AutoPropagate:",
            "SyncTarget:",
        ]
        
        with open(self.manifest_path, 'r') as f:
            content = f.read()
        
        found_metadata = {}
        for meta in required_metadata:
            if meta in content:
                # Extract value after the metadata key
                for line in content.split('\n'):
                    if meta in line and line.strip().startswith('#'):
                        value = line.split(meta, 1)[1].strip()
                        found_metadata[meta] = value
                        break
        
        missing = [m for m in required_metadata if m not in found_metadata]
        
        if missing:
            self.errors.append(f"Missing metadata headers: {', '.join(missing)}")
            return False
        
        print(f"   Found metadata:")
        for key, value in found_metadata.items():
            print(f"     {key} {value}")
        
        self.metadata = found_metadata
        return True
    
    def _check_variable_format(self) -> bool:
        """Check all variables follow KEY=VALUE format"""
        invalid_lines = []
        
        with open(self.manifest_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Check for KEY=VALUE format
                if '=' not in line:
                    invalid_lines.append((line_num, line))
                    continue
                
                # Parse variable
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Validate key format (alphanumeric and underscore only)
                if not key.replace('_', '').isalnum():
                    invalid_lines.append((line_num, f"{key} (invalid characters)"))
                    continue
                
                self.variables[key] = value
        
        if invalid_lines:
            self.errors.append(f"Invalid variable format on lines: {[ln for ln, _ in invalid_lines]}")
            for line_num, line in invalid_lines:
                print(f"   Line {line_num}: {line}")
            return False
        
        print(f"   Parsed {len(self.variables)} variables")
        return True
    
    def _check_required_variables(self) -> bool:
        """Check required variables are present"""
        required_vars = [
            "LINK_ENGINES",
            "BLUEPRINTS_ENABLED",
            "DB_ENABLED",
            "HEALTH_ENABLED",
            "FEDERATION_ENABLED",
            "GENESIS_PERSISTENCE_ENABLED",
        ]
        
        missing = [var for var in required_vars if var not in self.variables]
        
        if missing:
            self.errors.append(f"Missing required variables: {', '.join(missing)}")
            return False
        
        print(f"   All {len(required_vars)} required variables present")
        return True
    
    def _check_value_types(self) -> bool:
        """Check variable value types are valid"""
        boolean_vars = [
            "LINK_ENGINES",
            "BLUEPRINTS_ENABLED",
            "DB_ENABLED",
            "HEALTH_ENABLED",
            "FEDERATION_ENABLED",
            "WATCHDOG_ENABLED",
            "PREDICTIVE_STABILIZER_ENABLED",
            "GENESIS_PERSISTENCE_ENABLED",
        ]
        
        integer_vars = [
            "DB_POOL_SIZE",
            "DB_POOL_TIMEOUT",
            "DB_MAX_OVERFLOW",
            "HEALTH_PROBE_INTERVAL",
            "HEALTH_STATUS_OK",
            "FEDERATION_DISCOVERY_INTERVAL",
            "FEDERATION_SYNC_INTERVAL",
            "WATCHDOG_INTERVAL",
            "GENESIS_ECHO_DEPTH_LIMIT",
        ]
        
        invalid_values = []
        
        # Check booleans
        for var in boolean_vars:
            if var in self.variables:
                value = self.variables[var].lower()
                if value not in ["true", "false"]:
                    invalid_values.append(f"{var}={self.variables[var]} (expected true/false)")
        
        # Check integers
        for var in integer_vars:
            if var in self.variables:
                try:
                    int(self.variables[var])
                except ValueError:
                    invalid_values.append(f"{var}={self.variables[var]} (expected integer)")
        
        if invalid_values:
            self.errors.append("Invalid variable value types:")
            for iv in invalid_values:
                print(f"   {iv}")
            return False
        
        print(f"   All value types are valid")
        return True
    
    def _check_security(self) -> bool:
        """Check for potential security issues"""
        sensitive_patterns = [
            "password", "secret", "key", "token", "credential",
            "api_key", "private", "auth"
        ]
        
        suspicious_vars = []
        for var_name, var_value in self.variables.items():
            var_lower = var_name.lower()
            
            # Check if variable name contains sensitive patterns
            if any(pattern in var_lower for pattern in sensitive_patterns):
                # Make sure the value doesn't look like an actual secret
                if len(var_value) > 20 and not var_value.startswith("$"):
                    suspicious_vars.append(var_name)
        
        if suspicious_vars:
            self.warnings.append(
                f"Variables with potentially sensitive names found: {', '.join(suspicious_vars)}"
            )
            print(f"   {colored('⚠️  Warning:', YELLOW)} Ensure these don't contain actual secrets")
            for var in suspicious_vars:
                print(f"     {var}={self.variables[var][:20]}...")
        else:
            print(f"   No obvious security issues detected")
        
        return True
    
    def _print_summary(self) -> None:
        """Print validation summary"""
        print(colored("\n" + "=" * 80, BLUE))
        print(colored("Validation Summary", BLUE))
        print(colored("=" * 80, BLUE))
        
        if self.errors:
            print(colored(f"\n❌ {len(self.errors)} Error(s):", RED))
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(colored(f"\n⚠️  {len(self.warnings)} Warning(s):", YELLOW))
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print(colored("\n✅ Validation Passed!", GREEN))
            print(f"   {len(self.variables)} variables validated successfully")
        elif not self.errors:
            print(colored("\n⚠️  Validation Passed with Warnings", YELLOW))
        else:
            print(colored("\n❌ Validation Failed", RED))
        
        print(colored("=" * 80, BLUE))

def main():
    """Main entry point"""
    # Determine manifest path
    if len(sys.argv) > 1:
        manifest_path = Path(sys.argv[1])
    else:
        # Default path
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        manifest_path = project_root / "bridge_backend" / ".genesis" / "envsync_seed_manifest.env"
    
    validator = ManifestValidator(manifest_path)
    passed = validator.validate()
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
