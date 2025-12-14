"""BCSE Placeholder & Stub Detection Module

Detects "safe placeholder mode," stubs, dummy credentials, and inert flags.
Forces production check to fail if any unsafe patterns are detected.
"""
import re
import pathlib
from typing import List, Tuple

# Patterns that force a hard fail in prod check
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b", r"\bFIXME\b", r"\bTBD\b",
    r"raise\s+NotImplementedError", r"\bpass\b\s*(#\s*stub)?",
    r"\bmock(ed)?\b", r"\bstub(s)?\b", r"\bplaceholder\b",
    r"changeme", r"default(_|-)password", r"dummy(key|token|secret)",
    r"http://localhost(:\d+)?", r"https?://example\.com",
    r"ENABLE_SAFE_PLACEHOLDER\s*=\s*True",
    r"SAFE_MODE\s*=\s*True",
]

ALLOWLIST_EXT = {".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml", ".toml"}


def scan(root: str = ".") -> List[Tuple[str, int, str]]:
    """
    Scan for placeholder patterns in source files
    
    Args:
        root: Root directory to scan
        
    Returns:
        List of tuples (file_path, line_number, snippet)
    """
    hits = []
    for path in pathlib.Path(root).rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWLIST_EXT:
            continue
        
        # Skip common directories that should be ignored
        if any(part in path.parts for part in ['.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build']):
            continue
            
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
            
        for pat in PLACEHOLDER_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                line_no = text.count("\n", 0, m.start()) + 1
                snippet = text[max(0, m.start()-40):m.end()+40].replace("\n", " ")
                hits.append((str(path), line_no, snippet))
                
    return hits


def scan_and_report(root: str = ".") -> int:
    """
    Scan and report placeholder findings
    
    Args:
        root: Root directory to scan
        
    Returns:
        0 if no placeholders found, 1 otherwise
    """
    hits = scan(root)
    
    if not hits:
        print("✅ No placeholder patterns detected")
        return 0
        
    print(f"❌ Found {len(hits)} placeholder/stub pattern(s):")
    for f, ln, snip in hits[:50]:  # Limit output
        print(f"  {f}:{ln} :: {snip[:120]}")
        
    if len(hits) > 50:
        print(f"  ... and {len(hits) - 50} more")
        
    return 1
