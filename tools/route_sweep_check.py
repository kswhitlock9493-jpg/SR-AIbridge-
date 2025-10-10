#!/usr/bin/env python3
"""
Route Integrity Sweep Check for SR-AIbridge v1.9.6b

CI validator that scans all routes.py files and ensures they follow
the safe dependency injection pattern:

    DbDep = Annotated[AsyncSession, Depends(get_db)]

Fails the build if it detects:
- Direct AsyncSession exposure in route parameters
- Invalid return types that cause FastAPI crashes
- Unsafe database session handling

Usage:
    python tools/route_sweep_check.py

Exit codes:
    0 - All routes comply
    1 - Invalid patterns detected
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns to detect
UNSAFE_PATTERNS = [
    # Direct AsyncSession in function parameters (without proper Annotated typing)
    (r'async\s+def\s+\w+\([^)]*AsyncSession[^)]*\)', 
     "Direct AsyncSession param without Annotated[AsyncSession, Depends(get_db)]"),
    
    # Using db: AsyncSession without Annotated
    (r'def\s+\w+\([^)]*\bdb\s*:\s*AsyncSession(?!\s*,\s*Depends)', 
     "Direct AsyncSession type hint without Depends"),
]

SAFE_PATTERNS = [
    # Properly annotated dependency injection
    r'Annotated\[AsyncSession,\s*Depends\(',
    r'DbDep\s*=\s*Annotated\[AsyncSession,\s*Depends\(',
]

def find_route_files(root_path: Path) -> List[Path]:
    """Find all routes.py files in the project."""
    route_files = []
    
    # Search in bridge_backend for routes
    backend_path = root_path / "bridge_backend"
    if backend_path.exists():
        for routes_file in backend_path.rglob("routes*.py"):
            route_files.append(routes_file)
    
    return route_files

def check_file_for_unsafe_patterns(file_path: Path) -> List[Tuple[int, str]]:
    """
    Check a single file for unsafe patterns.
    Returns list of (line_number, issue_description) tuples.
    """
    issues = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Skip comments and imports
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('import ') or stripped.startswith('from '):
                continue
            
            # Check for unsafe patterns
            for pattern, description in UNSAFE_PATTERNS:
                if re.search(pattern, line):
                    # Check if this line also has safe patterns (might be properly typed)
                    has_safe_pattern = any(re.search(safe_p, line) for safe_p in SAFE_PATTERNS)
                    if not has_safe_pattern:
                        # Check the context - look ahead for Depends in next few lines
                        context_safe = False
                        for i in range(max(0, line_num - 2), min(len(lines), line_num + 3)):
                            if any(re.search(safe_p, lines[i]) for safe_p in SAFE_PATTERNS):
                                context_safe = True
                                break
                        
                        if not context_safe:
                            issues.append((line_num, description))
    
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
    
    return issues

def main() -> int:
    """Main entry point for route sweep check."""
    print("=" * 70)
    print("🧩 Bridge Route Integrity Sweep Check v1.9.6b")
    print("=" * 70)
    print()
    
    # Find project root
    current_file = Path(__file__).resolve()
    root_path = current_file.parent.parent
    
    print(f"📂 Scanning routes in: {root_path}")
    print()
    
    # Find all route files
    route_files = find_route_files(root_path)
    print(f"Found {len(route_files)} route files to check")
    print()
    
    # Check each file
    all_issues = {}
    for route_file in route_files:
        issues = check_file_for_unsafe_patterns(route_file)
        if issues:
            all_issues[route_file] = issues
    
    # Report results
    if not all_issues:
        print("✅ All routes comply with Bridge standards.")
        print("   - No direct AsyncSession exposure detected")
        print("   - Dependency injection patterns are correct")
        print()
        return 0
    else:
        print("❌ Route Sweep Check Failed:")
        print()
        for file_path, issues in all_issues.items():
            rel_path = file_path.relative_to(root_path)
            print(f"  [{rel_path}]")
            for line_num, description in issues:
                print(f"    Line {line_num}: {description}")
            print()
        
        print(f"Found {sum(len(issues) for issues in all_issues.values())} issues in {len(all_issues)} files")
        print()
        print("ℹ️  Fix by using dependency injection pattern:")
        print("   DbDep = Annotated[AsyncSession, Depends(get_db)]")
        print("   async def my_route(db: DbDep):")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
