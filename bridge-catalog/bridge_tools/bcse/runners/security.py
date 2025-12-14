"""Security Scanning Runners"""
import subprocess
import os
from typing import List


def run_bandit(paths: List[str], min_sev: str = "MEDIUM") -> int:
    """
    Run bandit security scanner
    
    Args:
        paths: List of paths to scan
        min_sev: Minimum severity (LOW, MEDIUM, HIGH)
        
    Returns:
        Exit code
    """
    try:
        severity_flag = "-ll" if min_sev == "HIGH" else "-l"
        return subprocess.call(["bandit", "-q", "-r", *paths, severity_flag])
    except FileNotFoundError:
        print("⚠️  bandit not found, skipping")
        return 0


def run_semgrep(config: str = "bridge_tools/bcse/rules/semgrep.yaml") -> int:
    """
    Run semgrep with custom rules
    
    Args:
        config: Path to semgrep config file
        
    Returns:
        Exit code
    """
    if not os.path.exists(config):
        print(f"⚠️  Semgrep config not found at {config}, skipping")
        return 0
    
    try:
        return subprocess.call(["semgrep", "--error", "-q", "--config", config])
    except FileNotFoundError:
        print("⚠️  semgrep not found, skipping")
        return 0
