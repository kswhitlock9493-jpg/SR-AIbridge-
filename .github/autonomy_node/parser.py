"""
Parser Sentinel - Repository scanner for the Embedded Autonomy Node
"""
import os
import re


def scan_repo():
    """
    Scan repository for potential issues
    
    Returns:
        Dictionary of findings with file names as keys
    """
    print("📜 Parsing repository...")
    findings = {}
    
    for root, _, files in os.walk("."):
        # Skip hidden directories and common non-code directories
        if "/.git" in root or "/node_modules" in root or "/__pycache__" in root:
            continue
            
        for f in files:
            if f.endswith(".py"):
                try:
                    file_path = os.path.join(root, f)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if "print(" in content:
                            findings[f] = {
                                "status": "warn",
                                "reason": "debug print",
                                "path": file_path
                            }
                except Exception as e:
                    # Skip files that can't be read
                    pass
    
    return findings
