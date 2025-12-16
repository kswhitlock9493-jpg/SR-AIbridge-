#!/usr/bin/env python3
"""
Fix deprecated datetime.now(timezone.utc) calls
Replaces with datetime.now(timezone.utc)
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def fix_file(filepath: Path) -> Tuple[bool, int]:
    """
    Fix deprecated datetime usage in a single file
    Returns: (modified, count_of_fixes)
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Check if file uses datetime
        if 'datetime' not in content:
            return False, 0
        
        # Count occurrences
        count = content.count('datetime.now(timezone.utc)')
        if count == 0:
            return False, 0
        
        # Check if timezone is already imported
        has_timezone_import = 'from datetime import' in content and 'timezone' in content
        has_utc_import = 'datetime.UTC' in content or 'timezone.utc' in content
        
        # Fix the import statement if needed
        if not has_timezone_import:
            # Find datetime import line
            import_pattern = r'from datetime import ([^\n]+)'
            match = re.search(import_pattern, content)
            
            if match:
                imports = match.group(1)
                if 'timezone' not in imports:
                    # Add timezone to existing import
                    new_imports = imports.rstrip() + ', timezone'
                    content = re.sub(import_pattern, f'from datetime import {new_imports}', content, count=1)
        
        # Replace datetime.now(timezone.utc) with datetime.now(timezone.utc)
        content = content.replace('datetime.now(timezone.utc)', 'datetime.now(timezone.utc)')
        
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            return True, count
        
        return False, 0
        
    except Exception as e:
        print(f"  ⚠️  Error processing {filepath}: {e}")
        return False, 0


def main():
    repo_path = Path(os.getenv("REPO_PATH", "/home/runner/work/SR-AIbridge-/SR-AIbridge-"))
    backend_path = repo_path / "bridge_backend"
    scripts_path = repo_path / "scripts"
    
    if not backend_path.exists():
        print(f"❌ Backend path not found: {backend_path}")
        return 1
    
    print("🔧 Fixing deprecated datetime.now(timezone.utc) calls...")
    print("="*60)
    
    # Process all Python files
    paths_to_scan = [backend_path, scripts_path]
    total_files = 0
    total_fixes = 0
    modified_files: List[Path] = []
    
    for base_path in paths_to_scan:
        if not base_path.exists():
            continue
            
        py_files = list(base_path.glob("**/*.py"))
        
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            modified, count = fix_file(py_file)
            if modified:
                total_files += 1
                total_fixes += count
                modified_files.append(py_file)
                print(f"✅ Fixed {count} occurrences in {py_file.relative_to(repo_path)}")
    
    print("\n" + "="*60)
    print(f"📊 Summary:")
    print(f"  Files modified: {total_files}")
    print(f"  Total fixes: {total_fixes}")
    
    if modified_files:
        print(f"\n📝 Modified files:")
        for f in modified_files[:10]:
            print(f"  - {f.relative_to(repo_path)}")
        if len(modified_files) > 10:
            print(f"  ... and {len(modified_files) - 10} more")
    
    print("\n✅ All deprecated datetime.now(timezone.utc) calls have been fixed!")
    print("   Replaced with: datetime.now(timezone.utc)")
    
    return 0


if __name__ == "__main__":
    exit(main())
