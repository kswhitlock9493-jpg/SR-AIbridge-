"""BCSE Autofix - Patch Reviewers

Human-in-the-loop review queue for patches.
"""
import pathlib
from typing import List, Dict, Any


def list_pending_patches(queue_dir: str = "bridge_tools/bcse/autofix/patch_queue") -> List[str]:
    """
    List all pending patches in the queue
    
    Args:
        queue_dir: Directory containing patch queue
        
    Returns:
        List of patch file paths
    """
    queue_path = pathlib.Path(queue_dir)
    if not queue_path.exists():
        return []
        
    return sorted([str(p) for p in queue_path.glob("*.patch")])


def review_patch(patch_file: str) -> Dict[str, Any]:
    """
    Display patch for human review
    
    Args:
        patch_file: Path to patch file
        
    Returns:
        Dictionary with patch metadata
    """
    patch_path = pathlib.Path(patch_file)
    if not patch_path.exists():
        return {"error": "Patch file not found"}
        
    content = patch_path.read_text(encoding="utf-8")
    
    # Extract metadata
    lines = content.split("\n")
    metadata = {
        "file": patch_file,
        "size": len(content),
        "lines": len(lines),
        "signature": None
    }
    
    # Look for Dominion signature
    for line in lines:
        if line.startswith("# Dominion-Signature:"):
            metadata["signature"] = line.split(":", 1)[1].strip()
            
    return metadata


def approve_patch(patch_file: str, target_dir: str = "bcse_autofixes") -> bool:
    """
    Approve a patch and move it to the approved directory
    
    Args:
        patch_file: Path to patch file
        target_dir: Directory for approved patches
        
    Returns:
        True if successful, False otherwise
    """
    patch_path = pathlib.Path(patch_file)
    if not patch_path.exists():
        print(f"❌ Patch file not found: {patch_file}")
        return False
        
    target_path = pathlib.Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    approved_file = target_path / patch_path.name
    patch_path.rename(approved_file)
    
    print(f"✅ Patch approved: {approved_file}")
    return True
