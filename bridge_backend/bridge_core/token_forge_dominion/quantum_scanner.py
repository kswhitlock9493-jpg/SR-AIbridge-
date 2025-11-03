"""
Quantum Scanner - Token Forge Dominion v1.9.7s-SOVEREIGN

Entropy analysis and ML-based secret detection for codebase scanning.
Implements quantum-grade secret detection with behavioral analysis.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from .zero_trust_validator import ZeroTrustValidator


class QuantumScanner:
    """
    Quantum-grade scanner for secrets, entropy, and security vulnerabilities.
    Uses ML-inspired heuristics and pattern matching for detection.
    """
    
    # File extensions to scan
    SCANNABLE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml',
        '.env', '.env.example', '.sh', '.bash', '.conf', '.config',
        '.toml', '.ini', '.properties', '.xml', '.md', '.txt'
    }
    
    # Paths to exclude from scanning
    # Note: 'tests' excluded by default to avoid false positives from test fixtures
    # For comprehensive scanning including tests, instantiate with custom exclude list
    EXCLUDE_PATHS = {
        'node_modules', '.git', '__pycache__', '.cache', 'dist', 'build',
        '.venv', 'venv', 'env', '.pytest_cache', 'coverage', '.alik', 'tests'
    }
    
    # High-confidence secret patterns
    SECRET_PATTERNS = {
        "aws_access_key": {
            "pattern": r'(?i)(AKIA[0-9A-Z]{16})',
            "severity": "critical",
            "description": "AWS Access Key ID"
        },
        "aws_secret_key": {
            "pattern": r'(?i)aws_secret_access_key\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
            "severity": "critical",
            "description": "AWS Secret Access Key"
        },
        "github_token": {
            "pattern": r'(?i)(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}',
            "severity": "critical",
            "description": "GitHub Personal Access Token"
        },
        "slack_token": {
            "pattern": r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}',
            "severity": "critical",
            "description": "Slack Token"
        },
        "stripe_key": {
            "pattern": r'(?i)(sk|pk)_(live|test)_[a-zA-Z0-9]{24,}',
            "severity": "critical",
            "description": "Stripe API Key"
        },
        "private_key": {
            "pattern": r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----',
            "severity": "critical",
            "description": "Private Key"
        },
        "generic_api_key": {
            "pattern": r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{32,})["\']',
            "severity": "high",
            "description": "Generic API Key"
        },
        "generic_secret": {
            "pattern": r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{32,})["\']',
            "severity": "high",
            "description": "Generic Secret Key"
        },
        "password_assignment": {
            "pattern": r'(?i)(password|passwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
            "severity": "medium",
            "description": "Hardcoded Password"
        },
        "jwt_token": {
            "pattern": r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
            "severity": "high",
            "description": "JWT Token"
        }
    }
    
    def __init__(self, root_path: Optional[str] = None):
        """
        Initialize quantum scanner.
        
        Args:
            root_path: Root path to scan (default: current directory)
        """
        self.root_path = Path(root_path or ".")
        self.validator = ZeroTrustValidator()
        self.scan_results: Dict[str, Any] = {}
    
    def should_scan_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be scanned.
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if file should be scanned
        """
        # Check if path contains excluded directories
        for exclude in self.EXCLUDE_PATHS:
            if exclude in file_path.parts:
                return False
        
        # Check file extension
        if file_path.suffix not in self.SCANNABLE_EXTENSIONS:
            return False
        
        # Skip very large files (>10MB)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except OSError:
            return False
        
        return True
    
    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Scan a single file for secrets and vulnerabilities.
        
        Args:
            file_path: Path to file
            
        Returns:
            dict: Scan results for file
        """
        results = {
            "file": str(file_path.relative_to(self.root_path)),
            "findings": [],
            "entropy_warnings": [],
            "line_count": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                results["line_count"] = len(lines)
            
            # Scan for secret patterns
            for pattern_name, pattern_config in self.SECRET_PATTERNS.items():
                matches = re.finditer(pattern_config["pattern"], content)
                for match in matches:
                    # Get line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Check if this looks like an example or template
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    is_example = any(keyword in line_content.lower() for keyword in 
                                   ['example', 'template', 'placeholder', 'your-', 'xxx', '***'])
                    
                    finding = {
                        "pattern": pattern_name,
                        "description": pattern_config["description"],
                        "severity": pattern_config["severity"],
                        "line": line_num,
                        "match_preview": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        "likely_example": is_example
                    }
                    
                    results["findings"].append(finding)
            
            # Check entropy of values that look like secrets
            secret_like_pattern = r'(?i)(key|secret|token|password)\s*[:=]\s*["\']([^"\']{16,})["\']'
            for match in re.finditer(secret_like_pattern, content):
                value = match.group(2)
                is_valid, reason = self.validator.validate_secret_entropy(value, min_entropy=3.5)
                
                if not is_valid:
                    line_num = content[:match.start()].count('\n') + 1
                    results["entropy_warnings"].append({
                        "line": line_num,
                        "reason": reason,
                        "value_preview": value[:20] + "..."
                    })
        
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def quantum_scan(
        self,
        path: Optional[str] = None,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Perform quantum scan of codebase.
        
        Args:
            path: Path to scan (default: root_path)
            recursive: Whether to scan recursively
            
        Returns:
            dict: Comprehensive scan report
        """
        scan_path = Path(path) if path else self.root_path
        
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "scan_path": str(scan_path),
            "version": "1.9.7s-SOVEREIGN",
            "files_scanned": 0,
            "files_with_findings": 0,
            "total_findings": 0,
            "findings_by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "files": []
        }
        
        # Collect files to scan
        if recursive and scan_path.is_dir():
            files_to_scan = [
                f for f in scan_path.rglob('*')
                if f.is_file() and self.should_scan_file(f)
            ]
        elif scan_path.is_file():
            files_to_scan = [scan_path] if self.should_scan_file(scan_path) else []
        else:
            files_to_scan = []
        
        # Scan each file
        for file_path in files_to_scan:
            file_results = self.scan_file(file_path)
            report["files_scanned"] += 1
            
            if file_results["findings"] or file_results["entropy_warnings"]:
                report["files_with_findings"] += 1
                report["files"].append(file_results)
                
                # Count findings by severity
                for finding in file_results["findings"]:
                    severity = finding["severity"]
                    report["findings_by_severity"][severity] += 1
                    report["total_findings"] += 1
        
        # Calculate risk score
        report["risk_score"] = (
            report["findings_by_severity"]["critical"] * 10 +
            report["findings_by_severity"]["high"] * 5 +
            report["findings_by_severity"]["medium"] * 2 +
            report["findings_by_severity"]["low"] * 1
        )
        
        # Determine overall status
        if report["findings_by_severity"]["critical"] > 0:
            report["status"] = "CRITICAL"
        elif report["findings_by_severity"]["high"] > 0:
            report["status"] = "HIGH_RISK"
        elif report["findings_by_severity"]["medium"] > 0:
            report["status"] = "MEDIUM_RISK"
        elif report["total_findings"] > 0:
            report["status"] = "LOW_RISK"
        else:
            report["status"] = "CLEAN"
        
        self.scan_results = report
        return report
    
    def generate_remediation_report(self) -> Dict[str, Any]:
        """
        Generate remediation guidance for found issues.
        
        Returns:
            dict: Remediation report
        """
        if not self.scan_results:
            return {"error": "No scan results available"}
        
        remediation = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_issues": self.scan_results["total_findings"],
            "recommendations": []
        }
        
        # Generate recommendations based on findings
        if self.scan_results["findings_by_severity"]["critical"] > 0:
            remediation["recommendations"].append({
                "priority": "CRITICAL",
                "action": "Immediately rotate all exposed credentials",
                "details": f"Found {self.scan_results['findings_by_severity']['critical']} critical secrets"
            })
        
        if self.scan_results["findings_by_severity"]["high"] > 0:
            remediation["recommendations"].append({
                "priority": "HIGH",
                "action": "Move hardcoded secrets to environment variables",
                "details": "Use FORGE_DOMINION for secure token management"
            })
        
        remediation["recommendations"].append({
            "priority": "MEDIUM",
            "action": "Enable pre-commit hooks for secret scanning",
            "details": "Prevent secrets from being committed"
        })
        
        return remediation
