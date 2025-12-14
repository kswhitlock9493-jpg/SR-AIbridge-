"""BCSE Autofix - Patch Explanation

Provides context and explanation for generated patches.
"""
import pathlib
from typing import Optional


def explain_patch(patch_file: str) -> Optional[str]:
    """
    Generate explanation for a patch
    
    Args:
        patch_file: Path to patch file
        
    Returns:
        Explanation text or None if patch not found
    """
    patch_path = pathlib.Path(patch_file)
    if not patch_path.exists():
        return None
        
    content = patch_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    # Count changes
    additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
    
    # Extract affected files
    files = set()
    for line in lines:
        if line.startswith("---") or line.startswith("+++"):
            parts = line.split()
            if len(parts) > 1:
                files.add(parts[1])
                
    explanation = f"""
Patch: {patch_path.name}
Files affected: {len(files)}
Changes: +{additions} -{deletions}

Affected files:
"""
    for f in sorted(files):
        explanation += f"  • {f}\n"
        
    # Look for signature
    for line in lines:
        if line.startswith("# Dominion-Signature:"):
            sig = line.split(":", 1)[1].strip()
            explanation += f"\nSignature: {sig}\n"
            
    return explanation


def print_patch_summary(patch_file: str) -> None:
    """
    Print a human-readable summary of the patch
    
    Args:
        patch_file: Path to patch file
    """
    explanation = explain_patch(patch_file)
    if explanation:
        print(explanation)
    else:
        print(f"❌ Patch not found: {patch_file}")
