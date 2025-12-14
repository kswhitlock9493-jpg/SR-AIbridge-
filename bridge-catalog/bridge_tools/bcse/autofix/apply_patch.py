"""BCSE Autofix - Patch Application

Safe patch application with validation.
"""
import subprocess
import pathlib
from typing import Optional


def apply_patch(patch_file: str, dry_run: bool = False) -> bool:
    """
    Apply a patch file to the repository
    
    Args:
        patch_file: Path to patch file
        dry_run: If True, only check if patch can be applied
        
    Returns:
        True if successful, False otherwise
    """
    if not pathlib.Path(patch_file).exists():
        print(f"❌ Patch file not found: {patch_file}")
        return False
        
    cmd = ["patch", "-p1"]
    if dry_run:
        cmd.append("--dry-run")
        
    cmd.extend(["-i", patch_file])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            if dry_run:
                print(f"✅ Patch can be applied: {patch_file}")
            else:
                print(f"✅ Patch applied: {patch_file}")
            return True
        else:
            print(f"❌ Patch failed: {patch_file}")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ 'patch' command not found. Please install patch utility.")
        return False
