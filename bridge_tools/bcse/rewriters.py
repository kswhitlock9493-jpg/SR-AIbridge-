"""BCSE Localhost to Forge Runtime Rewriter

Detects localhost/127.0.0.1 references and replaces them with FORGE_DOMINION_ROOT.
"""
import pathlib
import os
import re

LOCALHOST_PATTERNS = [
    r"http://localhost(:\d+)?",
    r"http://127\.0\.0\.1(:\d+)?",
    r"http://0\.0\.0\.0(:\d+)?",
]


def rewrite_localhost_to_forge(paths: list, forge_root: str = None) -> int:
    """
    Rewrite localhost URLs to Forge Dominion root
    
    Args:
        paths: List of directories to scan
        forge_root: Forge root URL (defaults to env var)
        
    Returns:
        Number of files changed
    """
    forge_root = forge_root or os.getenv("FORGE_DOMINION_ROOT", "").strip()
    
    if not forge_root:
        print("⚠️ No FORGE_DOMINION_ROOT available. Skipping rewrite.")
        return 0
        
    changed = 0
    for root in paths:
        root_path = pathlib.Path(root)
        if not root_path.exists():
            continue
            
        for file in root_path.rglob("*.*"):
            if file.suffix.lower() not in {".py", ".ts", ".tsx", ".js", ".json"}:
                continue
                
            # Skip common directories
            if any(part in file.parts for part in ['.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build']):
                continue
                
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
                new_text = text
                
                for pat in LOCALHOST_PATTERNS:
                    new_text = re.sub(pat, forge_root, new_text)
                    
                if new_text != text:
                    file.write_text(new_text, encoding="utf-8")
                    changed += 1
                    print(f"🔁 Rewrote localhost -> Forge in {file}")
            except Exception:
                continue
                
    print(f"✅ Done. Updated {changed} file(s).")
    return changed
