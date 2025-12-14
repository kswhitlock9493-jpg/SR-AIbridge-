"""BCSE Code Refactoring Module

Safe AST transforms + simple improvements (auto-fix available).
Note: This module is designed for targeted improvements only.
For general code quality, the improve command should be used sparingly
and changes should be reviewed carefully.
"""
import pathlib
from typing import List


def improve(paths: List[str]) -> int:
    """
    Improve code in all Python files under given paths
    
    Note: Currently disabled to prevent unwanted changes.
    Use manual code review and the fix command for style improvements.
    
    Args:
        paths: List of directories to scan
        
    Returns:
        Exit code (0 = success)
    """
    print("⚠️  BCSE improve command is available but disabled by default.")
    print("    AST transforms can make unwanted changes.")
    print("    For style fixes, use: make fix")
    print("    For targeted improvements, review and edit code manually.")
    print("\nBCSE refactor: 0 file(s) improved (command disabled)")
    return 0
