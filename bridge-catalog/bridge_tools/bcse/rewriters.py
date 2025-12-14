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


def scan_localhost_refs(paths: list) -> list:
    """
    Scan for localhost references without modifying files
    
    Args:
        paths: List of directories to scan
        
    Returns:
        List of tuples (file_path, line_number, snippet)
    """
    hits = []
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
                
                for pat in LOCALHOST_PATTERNS:
                    for m in re.finditer(pat, text):
                        line_no = text.count("\n", 0, m.start()) + 1
                        snippet = text[max(0, m.start()-40):m.end()+40].replace("\n", " ")
                        hits.append((str(file), line_no, snippet))
            except Exception:
                continue
                
    return hits


def rewrite_localhost_to_forge(paths: list, forge_root: str = None, dry_run: bool = True) -> int:
    """
    Rewrite localhost URLs to Forge Dominion root
    
    Args:
        paths: List of directories to scan
        forge_root: Forge root URL (defaults to env var)
        dry_run: If True, only report what would change (default)
        
    Returns:
        Number of files that would be changed (dry_run) or were changed
    """
    forge_root = forge_root or os.getenv("FORGE_DOMINION_ROOT", "").strip()
    
    if not forge_root:
        print("⚠️ No FORGE_DOMINION_ROOT available. Skipping rewrite.")
        return 0
        
    if dry_run:
        print(f"🔍 Scanning for localhost references (dry run mode)...")
        print(f"    Target: {forge_root}")
        
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
                    if dry_run:
                        print(f"📝 Would rewrite: {file}")
                    else:
                        file.write_text(new_text, encoding="utf-8")
                        print(f"🔁 Rewrote localhost -> Forge in {file}")
                    changed += 1
            except Exception:
                continue
    
    if dry_run:
        print(f"\n✅ Found {changed} file(s) with localhost references.")
        print("    To apply changes, set environment variable BCSE_REWRITE_APPLY=true")
    else:
        print(f"✅ Done. Updated {changed} file(s).")
        
    return changed
