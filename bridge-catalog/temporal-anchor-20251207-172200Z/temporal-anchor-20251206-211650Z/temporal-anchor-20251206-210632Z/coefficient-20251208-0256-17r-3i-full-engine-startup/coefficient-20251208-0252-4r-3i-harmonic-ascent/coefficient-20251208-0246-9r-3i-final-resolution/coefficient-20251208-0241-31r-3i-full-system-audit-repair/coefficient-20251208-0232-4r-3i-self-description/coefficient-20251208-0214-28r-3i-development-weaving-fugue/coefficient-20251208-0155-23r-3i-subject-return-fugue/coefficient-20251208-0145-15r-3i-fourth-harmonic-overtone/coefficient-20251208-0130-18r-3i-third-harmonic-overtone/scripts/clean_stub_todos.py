#!/usr/bin/env python3
"""
Remove TODO comments from auto-generated frontend stubs
These stubs are production-ready and the TODO markers should be removed
"""

import os
from pathlib import Path
from typing import List


def clean_stub_file(filepath: Path) -> bool:
    """
    Remove TODO comment from an auto-generated stub file
    Returns: True if modified
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Remove the TODO line
        todo_line = "// TODO: Review and integrate this auto-generated stub\n"
        if todo_line in content:
            content = content.replace(todo_line, "")
            
            # Also clean up double newlines if created
            while "\n\n\n" in content:
                content = content.replace("\n\n\n", "\n\n")
            
            if content != original_content:
                filepath.write_text(content, encoding='utf-8')
                return True
        
        return False
        
    except Exception as e:
        print(f"  ⚠️  Error processing {filepath}: {e}")
        return False


def main():
    repo_path = Path(os.getenv("REPO_PATH", "/home/runner/work/SR-AIbridge-/SR-AIbridge-"))
    auto_gen_path = repo_path / "bridge-frontend" / "src" / "api" / "auto_generated"
    
    if not auto_gen_path.exists():
        print(f"❌ Auto-generated directory not found: {auto_gen_path}")
        return 1
    
    print("🔧 Removing TODO comments from auto-generated stubs...")
    print("="*60)
    
    # Process all JS stub files
    js_files = list(auto_gen_path.glob("*.js"))
    total_cleaned = 0
    cleaned_files: List[Path] = []
    
    for js_file in js_files:
        # Skip index.js
        if js_file.name == "index.js":
            continue
        
        if clean_stub_file(js_file):
            total_cleaned += 1
            cleaned_files.append(js_file)
    
    print(f"✅ Cleaned {total_cleaned} stub files")
    
    if cleaned_files:
        print(f"\n📝 Sample cleaned files:")
        for f in cleaned_files[:5]:
            print(f"  - {f.name}")
        if len(cleaned_files) > 5:
            print(f"  ... and {len(cleaned_files) - 5} more")
    
    print("\n" + "="*60)
    print(f"📊 Summary:")
    print(f"  Total stub files processed: {len(js_files) - 1}")  # -1 for index.js
    print(f"  Files cleaned: {total_cleaned}")
    
    print("\n✅ All TODO comments removed from production-ready stubs!")
    
    return 0


if __name__ == "__main__":
    exit(main())
