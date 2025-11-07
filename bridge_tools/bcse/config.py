"""BCSE Configuration and Policy Management

This module implements the Bridge Code Super-Engine configuration with:
- Sovereign Git integration (always enabled)
- Placeholder mode with revealed gates
- Dynamic policy loading from Forge Dominion
"""
from dataclasses import dataclass
from typing import List, Optional


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
    """
    coverage_min: float
    mypy_strict: bool
    ruff_severity: str           # "E,W,F" etc
    bandit_min_severity: str     # "LOW","MEDIUM","HIGH"
    max_cyclomatic: int
    fail_on_vuln: bool
    allowed_licenses: List[str]


DEFAULT_POLICY = Policy(
    coverage_min=0.80,
    mypy_strict=True,
    ruff_severity="E,W,F",
    bandit_min_severity="MEDIUM",
    max_cyclomatic=10,
    fail_on_vuln=True,
    allowed_licenses=["MIT", "BSD-3-Clause", "Apache-2.0", "ISC"]
)
