#!/usr/bin/env python3
"""
Comprehensive Repository Scanner
Identifies duplicate, redundant, and dead files
"""

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'dist', 'build', 
    '.cache', 'venv', 'env', '.venv', 'vault', 'logs'
}

# File extensions to scan
SCAN_EXTENSIONS = {
    '.py', '.md', '.txt', '.json', '.yaml', '.yml', '.js', '.ts'
}

class RepoScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.duplicate_groups: List[List[Path]] = []
        self.redundant_docs: List[Path] = []
        self.dead_files: List[Path] = []
        
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file content"""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            print(f"⚠️  Error hashing {filepath}: {e}")
            return ""
    
    def should_scan(self, filepath: Path) -> bool:
        """Check if file should be scanned"""
        # Skip if in excluded directory
        for part in filepath.parts:
            if part in EXCLUDE_DIRS:
                return False
        
        # Only scan specific extensions
        if filepath.suffix not in SCAN_EXTENSIONS:
            return False
        
        # Skip very large files (>5MB)
        try:
            if filepath.stat().st_size > 5 * 1024 * 1024:
                return False
        except:
            return False
        
        return True
    
    def scan_for_duplicates(self):
        """Scan repository for duplicate files"""
        print("🔍 Scanning for duplicate files...")
        
        for filepath in self.repo_path.rglob('*'):
            if not filepath.is_file() or not self.should_scan(filepath):
                continue
            
            file_hash = self.calculate_file_hash(filepath)
            if file_hash:
                self.file_hashes[file_hash].append(filepath)
        
        # Identify duplicate groups (same hash, multiple files)
        for file_hash, files in self.file_hashes.items():
            if len(files) > 1:
                self.duplicate_groups.append(files)
        
        print(f"  Found {len(self.duplicate_groups)} duplicate file groups")
    
    def identify_redundant_docs(self):
        """Identify redundant documentation files"""
        print("🔍 Scanning for redundant documentation...")
        
        # Patterns that indicate summary/completion/implementation docs
        redundant_patterns = [
            'SUMMARY', 'COMPLETE', 'IMPLEMENTATION', 'PR_SUMMARY',
            'VERIFICATION', 'DEPLOYMENT_CHECKLIST', 'INTEGRATION_COMPLETE'
        ]
        
        doc_files = list(self.repo_path.glob('*.md'))
        
        for doc in doc_files:
            name_upper = doc.name.upper()
            # Check if it matches redundant patterns
            if any(pattern in name_upper for pattern in redundant_patterns):
                # Check if it's a versioned completion doc (V1.9.x format)
                if 'V1' in name_upper or 'V2' in name_upper or name_upper.startswith('V'):
                    self.redundant_docs.append(doc)
                # Or generic summaries
                elif 'SUMMARY' in name_upper or 'COMPLETE' in name_upper:
                    self.redundant_docs.append(doc)
        
        print(f"  Found {len(self.redundant_docs)} potentially redundant docs")
    
    def identify_dead_files(self):
        """Identify potentially dead/unused files"""
        print("🔍 Scanning for dead/unused files...")
        
        # Look for old verification scripts
        dead_patterns = [
            'verify_v196', 'validate_anchorhold', 'verify_autonomy_deployment',
            'verify_autonomy_integration', 'verify_communication', 'verify_netlify_build'
        ]
        
        for pattern in dead_patterns:
            matches = list(self.repo_path.glob(f'**/{pattern}*.py'))
            # Only mark as dead if in root (not in active directories)
            for match in matches:
                if match.parent == self.repo_path:
                    self.dead_files.append(match)
        
        print(f"  Found {len(self.dead_files)} potentially dead files")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive scan report"""
        report = {
            "scan_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "repo_path": str(self.repo_path),
            "summary": {
                "duplicate_groups": len(self.duplicate_groups),
                "total_duplicates": sum(len(group) - 1 for group in self.duplicate_groups),
                "redundant_docs": len(self.redundant_docs),
                "dead_files": len(self.dead_files)
            },
            "duplicates": [],
            "redundant_documentation": [],
            "dead_files": []
        }
        
        # Add duplicate details
        for group in self.duplicate_groups:
            report["duplicates"].append({
                "files": [str(f.relative_to(self.repo_path)) for f in group],
                "size_bytes": group[0].stat().st_size if group else 0,
                "recommendation": f"Keep one, remove {len(group) - 1} duplicate(s)"
            })
        
        # Add redundant docs
        for doc in self.redundant_docs:
            report["redundant_documentation"].append({
                "file": str(doc.relative_to(self.repo_path)),
                "size_bytes": doc.stat().st_size,
                "recommendation": "Archive or remove if content is captured elsewhere"
            })
        
        # Add dead files
        for dead in self.dead_files:
            report["dead_files"].append({
                "file": str(dead.relative_to(self.repo_path)),
                "size_bytes": dead.stat().st_size,
                "recommendation": "Remove if no longer needed"
            })
        
        return report
    
    def print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📊 REPOSITORY SCAN SUMMARY")
        print("="*60)
        
        summary = report["summary"]
        print(f"\n🔍 Scan Results:")
        print(f"  Duplicate file groups: {summary['duplicate_groups']}")
        print(f"  Total duplicate files: {summary['total_duplicates']}")
        print(f"  Redundant documentation: {summary['redundant_docs']}")
        print(f"  Dead/unused files: {summary['dead_files']}")
        
        if report["duplicates"]:
            print(f"\n📋 Duplicate Files (Top 10):")
            for i, dup in enumerate(report["duplicates"][:10], 1):
                print(f"  {i}. {len(dup['files'])} copies:")
                for f in dup['files'][:3]:
                    print(f"     - {f}")
                if len(dup['files']) > 3:
                    print(f"     ... and {len(dup['files']) - 3} more")
        
        if report["redundant_documentation"]:
            print(f"\n📄 Redundant Documentation (Top 10):")
            for i, doc in enumerate(report["redundant_documentation"][:10], 1):
                print(f"  {i}. {doc['file']}")
        
        if report["dead_files"]:
            print(f"\n💀 Dead/Unused Files:")
            for i, dead in enumerate(report["dead_files"], 1):
                print(f"  {i}. {dead['file']}")
        
        print("\n" + "="*60)


def main():
    repo_path = os.getenv("REPO_PATH", "/home/runner/work/SR-AIbridge-/SR-AIbridge-")
    
    scanner = RepoScanner(repo_path)
    
    # Run scans
    scanner.scan_for_duplicates()
    scanner.identify_redundant_docs()
    scanner.identify_dead_files()
    
    # Generate and save report
    report = scanner.generate_report()
    
    # Save JSON report
    report_path = Path(repo_path) / "bridge_backend" / "diagnostics" / "repo_scan_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    scanner.print_summary(report)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
