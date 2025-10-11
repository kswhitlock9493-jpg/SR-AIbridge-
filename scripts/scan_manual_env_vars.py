#!/usr/bin/env python3
"""
Manual Environment Variable Scanner
Identifies environment variables that require manual configuration
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class EnvVarScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.env_files = []
        self.required_vars = set()
        self.configured_vars = set()
        self.missing_vars = set()
        self.api_credentials = set()
        self.deployment_vars = set()
        
    def scan_env_files(self):
        """Scan all .env files in repository"""
        print("🔍 Scanning environment files...")
        
        # Find all .env files
        env_patterns = ['.env', '.env.*']
        for pattern in env_patterns:
            self.env_files.extend(self.repo_path.glob(pattern))
        
        # Also check bridge_backend for .env files
        backend_path = self.repo_path / 'bridge_backend'
        if backend_path.exists():
            for pattern in env_patterns:
                self.env_files.extend(backend_path.glob(pattern))
        
        print(f"  Found {len(self.env_files)} environment files")
    
    def extract_env_vars_from_file(self, filepath: Path) -> Set[str]:
        """Extract environment variable names from a file"""
        vars_found = set()
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
                # Match VAR_NAME=value or VAR_NAME= patterns
                pattern = r'^([A-Z_][A-Z0-9_]*)='
                matches = re.findall(pattern, content, re.MULTILINE)
                vars_found.update(matches)
                
                # Also match os.getenv("VAR_NAME") patterns in Python files
                if filepath.suffix == '.py':
                    getenv_pattern = r'os\.getenv\(["\']([A-Z_][A-Z0-9_]*)["\']'
                    matches = re.findall(getenv_pattern, content)
                    vars_found.update(matches)
                    
                    # Match os.environ.get("VAR_NAME")
                    environ_pattern = r'os\.environ\.get\(["\']([A-Z_][A-Z0-9_]*)["\']'
                    matches = re.findall(environ_pattern, content)
                    vars_found.update(matches)
        
        except Exception as e:
            print(f"⚠️  Error reading {filepath}: {e}")
        
        return vars_found
    
    def scan_python_files_for_env_usage(self):
        """Scan Python files to find environment variable usage"""
        print("🔍 Scanning Python files for environment variable usage...")
        
        python_files = list(self.repo_path.rglob('*.py'))
        
        # Filter out excluded directories
        exclude_dirs = {'__pycache__', 'venv', 'env', '.venv', 'node_modules'}
        python_files = [
            f for f in python_files 
            if not any(ex in f.parts for ex in exclude_dirs)
        ]
        
        for py_file in python_files[:100]:  # Limit to prevent timeout
            vars_in_file = self.extract_env_vars_from_file(py_file)
            self.required_vars.update(vars_in_file)
        
        print(f"  Found {len(self.required_vars)} unique environment variables in use")
    
    def load_configured_vars(self):
        """Load variables that are already configured"""
        print("🔍 Loading configured variables from .env files...")
        
        for env_file in self.env_files:
            if env_file.name in ['.env', '.env.production', '.env.deploy']:
                vars_in_file = self.extract_env_vars_from_file(env_file)
                self.configured_vars.update(vars_in_file)
        
        print(f"  Found {len(self.configured_vars)} configured variables")
    
    def categorize_variables(self):
        """Categorize variables by type"""
        print("🔍 Categorizing environment variables...")
        
        api_patterns = [
            'API_KEY', 'API_TOKEN', 'TOKEN', 'SECRET', 'CLIENT_ID', 
            'CLIENT_SECRET', 'WEBHOOK', 'AUTH'
        ]
        
        deployment_patterns = [
            'RENDER_', 'NETLIFY_', 'GITHUB_', 'VERCEL_', 'AWS_',
            'SERVICE_ID', 'SITE_ID', 'REPO_', 'BRANCH'
        ]
        
        for var in self.required_vars:
            var_upper = var.upper()
            
            # Check if it's an API credential
            if any(pattern in var_upper for pattern in api_patterns):
                self.api_credentials.add(var)
            
            # Check if it's a deployment variable
            if any(pattern in var_upper for pattern in deployment_patterns):
                self.deployment_vars.add(var)
    
    def identify_missing_vars(self):
        """Identify variables that need manual configuration"""
        print("🔍 Identifying missing variables...")
        
        # Variables that are required but not configured
        self.missing_vars = self.required_vars - self.configured_vars
        
        print(f"  Found {len(self.missing_vars)} potentially missing variables")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive environment variable report"""
        
        # Categorize missing vars
        missing_api = self.missing_vars & self.api_credentials
        missing_deployment = self.missing_vars & self.deployment_vars
        missing_other = self.missing_vars - missing_api - missing_deployment
        
        report = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_required": len(self.required_vars),
                "configured": len(self.configured_vars),
                "missing": len(self.missing_vars),
                "missing_api_credentials": len(missing_api),
                "missing_deployment": len(missing_deployment)
            },
            "variables_requiring_manual_setup": {
                "api_credentials": sorted(list(missing_api)),
                "deployment_variables": sorted(list(missing_deployment)),
                "other_variables": sorted(list(missing_other))
            },
            "all_required_variables": sorted(list(self.required_vars)),
            "configured_variables": sorted(list(self.configured_vars)),
            "recommendations": self._generate_recommendations(
                missing_api, missing_deployment, missing_other
            )
        }
        
        return report
    
    def _generate_recommendations(self, missing_api, missing_deployment, missing_other) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if missing_api:
            recommendations.append({
                "category": "API Credentials",
                "priority": "HIGH",
                "action": "Obtain and configure API credentials",
                "variables": sorted(list(missing_api)),
                "description": "These are API keys, tokens, or secrets that must be obtained from third-party services"
            })
        
        if missing_deployment:
            recommendations.append({
                "category": "Deployment Configuration",
                "priority": "HIGH",
                "action": "Configure deployment platform variables",
                "variables": sorted(list(missing_deployment)),
                "description": "These variables configure deployment platforms like Render, Netlify, or GitHub"
            })
        
        if missing_other:
            recommendations.append({
                "category": "Application Configuration",
                "priority": "MEDIUM",
                "action": "Review and configure application settings",
                "variables": sorted(list(missing_other)),
                "description": "General application configuration variables"
            })
        
        return recommendations
    
    def print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("🔧 ENVIRONMENT VARIABLE SCAN SUMMARY")
        print("="*60)
        
        summary = report["summary"]
        print(f"\n📊 Overall Statistics:")
        print(f"  Total variables in use: {summary['total_required']}")
        print(f"  Currently configured: {summary['configured']}")
        print(f"  Missing/Not configured: {summary['missing']}")
        
        manual_vars = report["variables_requiring_manual_setup"]
        
        if manual_vars["api_credentials"]:
            print(f"\n🔑 API Credentials Requiring Manual Setup ({len(manual_vars['api_credentials'])}):")
            for var in manual_vars["api_credentials"][:15]:
                print(f"  ❌ {var}")
            if len(manual_vars["api_credentials"]) > 15:
                print(f"  ... and {len(manual_vars['api_credentials']) - 15} more")
        
        if manual_vars["deployment_variables"]:
            print(f"\n🚀 Deployment Variables Requiring Manual Setup ({len(manual_vars['deployment_variables'])}):")
            for var in manual_vars["deployment_variables"][:15]:
                print(f"  ❌ {var}")
            if len(manual_vars["deployment_variables"]) > 15:
                print(f"  ... and {len(manual_vars['deployment_variables']) - 15} more")
        
        if manual_vars["other_variables"]:
            print(f"\n⚙️  Other Variables ({len(manual_vars['other_variables'])}):")
            for var in manual_vars["other_variables"][:10]:
                print(f"  ❌ {var}")
            if len(manual_vars["other_variables"]) > 10:
                print(f"  ... and {len(manual_vars['other_variables']) - 10} more")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"\n  {i}. {rec['category']} (Priority: {rec['priority']})")
                print(f"     Action: {rec['action']}")
                print(f"     {rec['description']}")
        
        print("\n" + "="*60)


def main():
    repo_path = os.getenv("REPO_PATH", "/home/runner/work/SR-AIbridge-/SR-AIbridge-")
    
    scanner = EnvVarScanner(repo_path)
    
    # Run scans
    scanner.scan_env_files()
    scanner.scan_python_files_for_env_usage()
    scanner.load_configured_vars()
    scanner.categorize_variables()
    scanner.identify_missing_vars()
    
    # Generate and save report
    report = scanner.generate_report()
    
    # Save JSON report
    report_path = Path(repo_path) / "bridge_backend" / "diagnostics" / "env_scan_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    scanner.print_summary(report)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
