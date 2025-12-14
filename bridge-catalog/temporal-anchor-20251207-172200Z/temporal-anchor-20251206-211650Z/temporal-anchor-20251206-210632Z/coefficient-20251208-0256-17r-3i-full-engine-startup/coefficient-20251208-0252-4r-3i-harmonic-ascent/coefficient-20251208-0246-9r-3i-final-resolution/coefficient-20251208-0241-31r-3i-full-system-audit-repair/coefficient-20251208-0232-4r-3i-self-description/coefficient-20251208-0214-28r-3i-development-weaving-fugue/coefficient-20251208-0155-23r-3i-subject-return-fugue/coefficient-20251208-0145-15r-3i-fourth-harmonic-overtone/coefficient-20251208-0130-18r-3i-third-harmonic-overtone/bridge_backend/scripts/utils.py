#!/usr/bin/env python3
"""
Utility functions for triage scripts
"""

from datetime import datetime, timezone


def now() -> str:
    """
    Get current timestamp in ISO format
    Returns ISO 8601 timestamp string
    """
    return datetime.now(timezone.utc).isoformat()
