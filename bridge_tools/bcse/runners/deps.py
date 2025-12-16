"""Dependency Vulnerability Scanning"""
import subprocess
import os
from typing import List


def pip_audit(fail_on_vuln: bool = True) -> int:
    """
    Run pip-audit to check for dependency vulnerabilities
    
    Args:
        fail_on_vuln: Whether to fail on vulnerabilities
        
    Returns:
        Exit code
    """
    if not os.path.exists("requirements.txt"):
        print("⚠️  requirements.txt not found, skipping pip-audit")
        return 0
    
    try:
        code = subprocess.call(["pip-audit", "-r", "requirements.txt", "-f", "cyclonedx"])
        return code if fail_on_vuln else 0
    except FileNotFoundError:
        print("⚠️  pip-audit not found, skipping")
        return 0


def npm_audit(path: str = "bridge-frontend", fail_on_vuln: bool = True) -> int:
    """
    Run npm audit to check for JS dependency vulnerabilities
    
    Args:
        path: Path to frontend directory
        fail_on_vuln: Whether to fail on vulnerabilities
        
    Returns:
        Exit code
    """
    if not os.path.exists(path):
        print(f"⚠️  Frontend path {path} not found, skipping npm audit")
        return 0
    
    if not os.path.exists(os.path.join(path, "package.json")):
        print(f"⚠️  package.json not found in {path}, skipping npm audit")
        return 0
    
    cwd = os.getcwd()
    try:
        os.chdir(path)
        code = subprocess.call(["npm", "audit", "--audit-level", "high"])
        return code if fail_on_vuln else 0
    except FileNotFoundError:
        print("⚠️  npm not found, skipping")
        return 0
    finally:
        os.chdir(cwd)
