"""BCSE Configuration and Policy Management"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Policy:
    """Quality gate policy configuration"""
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
