"""BCSE Code Patch Proposal Module

Creates signed patch proposals to exit placeholder mode (never auto-commits).
"""
import difflib
import pathlib
import time
import os


SEAL = os.getenv("DOMINION_SEAL", "Σ–DEV–UNSIGNED")


def propose_patch(
    path: str, 
    original: str, 
    updated: str, 
    out_dir: str = "bcse_autofixes"
) -> str:
    """
    Generate a diff patch and save it for human review
    
    Args:
        path: File path being patched
        original: Original file content
        updated: Updated file content
        out_dir: Output directory for patches
        
    Returns:
        Path to generated patch file
    """
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    stamp = int(time.time())
    patch_name = f"{out_dir}/{path.replace('/', '_')}.{stamp}.patch"
    
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        updated.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}"
    )
    
    with open(patch_name, "w", encoding="utf-8") as f:
        f.writelines(diff)
        f.write(f"\n# Dominion-Signature: {SEAL}\n")
        
    print(f"🔧 Patch proposed -> {patch_name}")
    return patch_name


def list_patches(patch_dir: str = "bcse_autofixes") -> list:
    """
    List all available patches
    
    Args:
        patch_dir: Directory containing patches
        
    Returns:
        List of patch file paths
    """
    patch_path = pathlib.Path(patch_dir)
    if not patch_path.exists():
        return []
        
    return sorted(patch_path.glob("*.patch"))
