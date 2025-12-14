"""BCSE Configuration and Policy Management

This module implements the Bridge Code Super-Engine configuration with:
- Sovereign Git integration (always enabled)
- Placeholder mode with revealed gates
- Dynamic policy loading from Forge Dominion
- Branch-aware, environment-aware, and federation-aware policies
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


# BCSE Engine Status: ALWAYS ENABLED
# In placeholder mode, all quality gates are revealed and configurable
BCSE_ALWAYS_ENABLED = True
PLACEHOLDER_MODE = True  # Reveals all gates for inspection and configuration


@dataclass
class Policy:
    """
    Quality gate policy configuration
    
    In placeholder mode, all gates are revealed (accessible and configurable):
    - coverage_min: Minimum test coverage threshold
    - mypy_strict: Enable mypy strict type checking
    - ruff_severity: Ruff linter severity levels
    - bandit_min_severity: Bandit security minimum severity
    - max_cyclomatic: Maximum cyclomatic complexity
    - fail_on_vuln: Fail on dependency vulnerabilities
    - allowed_licenses: Permitted dependency licenses
    - js_audit_level: NPM audit level (high, moderate, low, critical)
    """
    coverage_min: float
    mypy_strict: bool
    ruff_severity: str           # "E,W,F" etc
    bandit_min_severity: str     # "LOW","MEDIUM","HIGH"
    max_cyclomatic: int
    fail_on_vuln: bool
    allowed_licenses: List[str]
    js_audit_level: str = "high"  # npm audit level


DEFAULT_POLICY = Policy(
    coverage_min=0.80,
    mypy_strict=True,
    ruff_severity="E,W,F",
    bandit_min_severity="MEDIUM",
    max_cyclomatic=10,
    fail_on_vuln=True,
    allowed_licenses=["MIT", "BSD-3-Clause", "Apache-2.0", "ISC", "Python-2.0"],
    js_audit_level="high"
)


def policy_from_dict(data: Dict[str, Any]) -> Policy:
    """
    Create a Policy object from a dictionary
    
    Args:
        data: Dictionary containing policy configuration
        
    Returns:
        Policy object with values from the dictionary or defaults
    """
    return Policy(
        coverage_min=data.get("coverage_min", DEFAULT_POLICY.coverage_min),
        mypy_strict=data.get("mypy_strict", DEFAULT_POLICY.mypy_strict),
        ruff_severity=data.get("ruff_severity", DEFAULT_POLICY.ruff_severity),
        bandit_min_severity=data.get("bandit_min_severity", DEFAULT_POLICY.bandit_min_severity),
        max_cyclomatic=data.get("max_cyclomatic", DEFAULT_POLICY.max_cyclomatic),
        fail_on_vuln=data.get("fail_on_vuln", DEFAULT_POLICY.fail_on_vuln),
        allowed_licenses=data.get("allowed_licenses", DEFAULT_POLICY.allowed_licenses),
        js_audit_level=data.get("js", {}).get("audit_level", DEFAULT_POLICY.js_audit_level) 
                       if isinstance(data.get("js"), dict) 
                       else data.get("js_audit_level", DEFAULT_POLICY.js_audit_level)
    )
