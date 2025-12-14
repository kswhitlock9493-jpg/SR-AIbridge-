"""Python Linting and Quality Runners"""
import subprocess
import json
import sys
from typing import List, Tuple


def run_black_check(targets: List[str]) -> int:
    """
    Run black in check mode (no modifications)
    
    Args:
        targets: List of paths to check
        
    Returns:
        Exit code (0 = success, non-zero = formatting needed)
    """
    try:
        return subprocess.call(["black", "--check", "--diff", *targets])
    except FileNotFoundError:
        print("⚠️  black not found, skipping")
        return 0


def run_black_fix(targets: List[str]) -> int:
    """
    Run black to auto-format code
    
    Args:
        targets: List of paths to format
        
    Returns:
        Exit code
    """
    try:
        return subprocess.call(["black", *targets])
    except FileNotFoundError:
        print("⚠️  black not found, skipping")
        return 0


def run_ruff(targets: List[str], select: str = "E,W,F") -> Tuple[int, str]:
    """
    Run ruff linter
    
    Args:
        targets: List of paths to check
        select: Ruff rule categories to check
        
    Returns:
        Tuple of (exit code, stdout JSON)
    """
    try:
        cmd = ["ruff", "check", "--select", select, "--output-format", "json", *targets]
        p = subprocess.run(cmd, capture_output=True, text=True)
        return p.returncode, p.stdout
    except FileNotFoundError:
        print("⚠️  ruff not found, skipping")
        return 0, "[]"


def run_mypy(targets: List[str], strict: bool = True) -> int:
    """
    Run mypy type checker
    
    Args:
        targets: List of paths to check
        strict: Whether to use strict mode
        
    Returns:
        Exit code
    """
    try:
        cmd = ["mypy", *targets] + (["--strict"] if strict else [])
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("⚠️  mypy not found, skipping")
        return 0


def cyclomatic(files: List[str], max_cyc: int) -> int:
    """
    Check cyclomatic complexity with radon
    
    Args:
        files: List of Python files to check
        max_cyc: Maximum allowed complexity
        
    Returns:
        Exit code (0 = pass, 1 = complexity violations)
    """
    try:
        cmd = ["radon", "cc", "-s", "-j", *files]
        p = subprocess.run(cmd, capture_output=True, text=True)
        breaches = 0
        try:
            data = json.loads(p.stdout)
            for f, entries in data.items():
                for e in entries:
                    if e.get("complexity", 0) > max_cyc:
                        breaches += 1
                        print(f"⚠️  Complexity breach in {f}: {e.get('name')} has complexity {e.get('complexity')}")
        except Exception as ex:
            print(f"⚠️  Failed to parse radon output: {ex}")
            pass
        return 1 if breaches else 0
    except FileNotFoundError:
        print("⚠️  radon not found, skipping")
        return 0
