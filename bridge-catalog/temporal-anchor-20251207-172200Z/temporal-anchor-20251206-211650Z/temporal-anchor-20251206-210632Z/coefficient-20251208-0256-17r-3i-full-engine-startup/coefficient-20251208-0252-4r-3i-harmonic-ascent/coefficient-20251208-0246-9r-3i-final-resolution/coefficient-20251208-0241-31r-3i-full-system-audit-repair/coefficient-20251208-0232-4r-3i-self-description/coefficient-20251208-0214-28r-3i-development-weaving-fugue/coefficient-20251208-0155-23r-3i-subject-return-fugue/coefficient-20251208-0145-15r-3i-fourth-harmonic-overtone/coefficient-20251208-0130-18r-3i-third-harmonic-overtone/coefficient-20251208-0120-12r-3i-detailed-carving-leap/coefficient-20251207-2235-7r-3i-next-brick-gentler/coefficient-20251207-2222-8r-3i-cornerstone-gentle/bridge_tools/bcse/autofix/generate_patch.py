"""BCSE Autofix - Patch Generator

Deterministic, diff-based patch generation.
"""
from difflib import unified_diff


def generate_patch(old: str, new: str, path: str) -> str:
    """
    Generate a unified diff patch between old and new content
    
    Args:
        old: Original content
        new: Updated content
        path: File path for context
        
    Returns:
        Patch as a string in unified diff format
    """
    diff = unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
    )
    return "".join(diff)
