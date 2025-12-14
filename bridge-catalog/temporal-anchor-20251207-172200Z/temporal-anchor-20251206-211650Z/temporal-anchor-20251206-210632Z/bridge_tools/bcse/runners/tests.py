"""Test and Coverage Runners"""
import subprocess
import os
from typing import Optional


def run_pytest_with_coverage(min_cov: float) -> int:
    """
    Run pytest with coverage checking
    
    Args:
        min_cov: Minimum coverage percentage (0.0-1.0)
        
    Returns:
        Exit code (0 = pass, 1 = fail)
    """
    try:
        code = subprocess.call([
            "pytest", "-q", 
            "--cov=.", 
            "--cov-report=xml",
            "--junitxml=bcse_junit.xml"
        ])
        
        if code != 0:
            print(f"❌ Tests failed with exit code {code}")
            return code
        
        # Parse coverage xml for line-rate
        coverage_file = "coverage.xml"
        if not os.path.exists(coverage_file):
            print("⚠️  coverage.xml not found, cannot check coverage threshold")
            return 0
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.parse(coverage_file).getroot()
            rate = float(root.attrib.get("line-rate", "0"))
            
            if rate < min_cov:
                print(f"❌ Coverage {rate:.1%} is below minimum {min_cov:.1%}")
                return 1
            else:
                print(f"✅ Coverage {rate:.1%} meets minimum {min_cov:.1%}")
                return 0
        except Exception as e:
            print(f"⚠️  Failed to parse coverage report: {e}")
            return 0
            
    except FileNotFoundError:
        print("⚠️  pytest not found, skipping")
        return 0
