#!/usr/bin/env python3
"""
SR-AIbridge Lines of Code (LOC) Counter
Generates a comprehensive LOC report for the entire project
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Directories to exclude
EXCLUDE_DIRS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build', 
    '.venv', 'venv', '.pytest_cache', '.mypy_cache', 
    'dock_day_exports', '.copilot'
}

# File extensions to count
FILE_EXTENSIONS = {
    'Python': ['.py'],
    'JavaScript/TypeScript': ['.js', '.jsx', '.ts', '.tsx'],
    'Markdown': ['.md'],
    'YAML': ['.yml', '.yaml'],
    'JSON': ['.json'],
    'Shell': ['.sh', '.bash'],
    'SQL': ['.sql'],
    'TOML': ['.toml'],
    'CSS': ['.css'],
    'HTML': ['.html'],
    'Other': ['.txt', '.env', '.gitignore', '.ini', '.cfg']
}

def should_exclude_dir(path):
    """Check if directory should be excluded"""
    parts = Path(path).parts
    return any(excluded in parts for excluded in EXCLUDE_DIRS)

def count_lines(file_path):
    """Count lines in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return 0

def get_file_category(file_path):
    """Get category for a file based on extension"""
    ext = Path(file_path).suffix.lower()
    for category, extensions in FILE_EXTENSIONS.items():
        if ext in extensions:
            return category
    return 'Unknown'

def generate_loc_report(root_dir):
    """Generate comprehensive LOC report"""
    
    stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'file_list': []})
    total_files = 0
    total_lines = 0
    
    print(f"Scanning directory: {root_dir}")
    print("=" * 80)
    
    # Walk through directory tree
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        if should_exclude_dir(dirpath):
            continue
            
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(file_path, root_dir)
            
            # Count lines
            line_count = count_lines(file_path)
            if line_count == 0:
                continue
                
            # Categorize file
            category = get_file_category(file_path)
            
            # Update stats
            stats[category]['files'] += 1
            stats[category]['lines'] += line_count
            stats[category]['file_list'].append((relative_path, line_count))
            
            total_files += 1
            total_lines += line_count
    
    return stats, total_files, total_lines

def print_report(stats, total_files, total_lines):
    """Print formatted LOC report"""
    
    print("\n" + "=" * 80)
    print("SR-AIbridge PROJECT - LINES OF CODE REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    print("\n📊 SUMMARY BY FILE TYPE")
    print("-" * 80)
    print(f"{'Category':<30} {'Files':<10} {'Lines':<15} {'% of Total':<10}")
    print("-" * 80)
    
    # Sort by line count descending
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['lines'], reverse=True)
    
    for category, data in sorted_stats:
        percentage = (data['lines'] / total_lines * 100) if total_lines > 0 else 0
        print(f"{category:<30} {data['files']:<10} {data['lines']:<15,} {percentage:>6.2f}%")
    
    print("-" * 80)
    print(f"{'TOTAL':<30} {total_files:<10} {total_lines:<15,} {'100.00%':>10}")
    print("=" * 80)
    
    # Detailed breakdown by category
    print("\n📁 DETAILED BREAKDOWN BY CATEGORY")
    print("=" * 80)
    
    for category, data in sorted_stats:
        print(f"\n{category} ({data['files']} files, {data['lines']:,} lines)")
        print("-" * 80)
        
        # Sort files by line count
        sorted_files = sorted(data['file_list'], key=lambda x: x[1], reverse=True)
        
        # Show top 10 files per category
        for file_path, line_count in sorted_files[:10]:
            print(f"  {line_count:>6,}  {file_path}")
        
        if len(sorted_files) > 10:
            remaining = len(sorted_files) - 10
            remaining_lines = sum(f[1] for f in sorted_files[10:])
            print(f"  ... and {remaining} more files ({remaining_lines:,} lines)")
    
    print("\n" + "=" * 80)

def save_report_to_file(stats, total_files, total_lines, output_file):
    """Save report to a markdown file"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# SR-AIbridge - Lines of Code Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Files:** {total_files:,}\n")
        f.write(f"- **Total Lines:** {total_lines:,}\n\n")
        
        f.write("## Breakdown by File Type\n\n")
        f.write("| Category | Files | Lines | % of Total |\n")
        f.write("|----------|-------|-------|------------|\n")
        
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['lines'], reverse=True)
        
        for category, data in sorted_stats:
            percentage = (data['lines'] / total_lines * 100) if total_lines > 0 else 0
            f.write(f"| {category} | {data['files']:,} | {data['lines']:,} | {percentage:.2f}% |\n")
        
        f.write(f"| **TOTAL** | **{total_files:,}** | **{total_lines:,}** | **100.00%** |\n\n")
        
        # Detailed breakdown
        f.write("## Detailed File List by Category\n\n")
        
        for category, data in sorted_stats:
            f.write(f"### {category} ({data['files']} files, {data['lines']:,} lines)\n\n")
            
            sorted_files = sorted(data['file_list'], key=lambda x: x[1], reverse=True)
            
            f.write("| Lines | File |\n")
            f.write("|-------|------|\n")
            
            for file_path, line_count in sorted_files:
                f.write(f"| {line_count:,} | `{file_path}` |\n")
            
            f.write("\n")
        
        f.write("\n---\n")
        f.write("*Generated by count_loc.py - SR-AIbridge LOC Counter*\n")
    
    print(f"\n✅ Report saved to: {output_file}")

def main():
    """Main function"""
    
    # Get root directory (where script is located)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"🚀 SR-AIbridge LOC Counter")
    print(f"Root directory: {root_dir}\n")
    
    # Generate report
    stats, total_files, total_lines = generate_loc_report(root_dir)
    
    # Print to console
    print_report(stats, total_files, total_lines)
    
    # Save to file
    output_file = os.path.join(root_dir, "LOC_REPORT.md")
    save_report_to_file(stats, total_files, total_lines, output_file)
    
    print(f"\n✨ Total Lines of Code: {total_lines:,}")
    print(f"📦 Total Files: {total_files:,}\n")

if __name__ == "__main__":
    main()
