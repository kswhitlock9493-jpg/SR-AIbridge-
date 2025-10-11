#!/usr/bin/env python3
"""
Repository Cleanup Script
Removes duplicate, redundant, and dead files identified by comprehensive scan
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime


class RepoCleanup:
    def __init__(self, repo_path: str, dry_run: bool = True):
        self.repo_path = Path(repo_path)
        self.dry_run = dry_run
        self.removed_files = []
        self.removed_dirs = []
        self.archived_files = []
        
    def load_scan_report(self) -> dict:
        """Load the repo scan report"""
        report_path = self.repo_path / "bridge_backend" / "diagnostics" / "repo_scan_report.json"
        
        if not report_path.exists():
            print("❌ Scan report not found. Run comprehensive_repo_scan.py first.")
            return {}
        
        with open(report_path, 'r') as f:
            return json.load(f)
    
    def create_archive_dir(self) -> Path:
        """Create archive directory for redundant docs"""
        archive_path = self.repo_path / "docs" / "archive"
        
        if self.dry_run:
            print(f"[DRY RUN] Would create directory: {archive_path}")
        else:
            archive_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created archive directory: {archive_path}")
        
        return archive_path
    
    def remove_dead_files(self, dead_files: list):
        """Remove dead/unused verification scripts"""
        print("\n🗑️  Removing dead/unused files...")
        
        for file_info in dead_files:
            file_path = self.repo_path / file_info["file"]
            
            if not file_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
            
            if self.dry_run:
                print(f"[DRY RUN] Would remove: {file_path}")
            else:
                file_path.unlink()
                self.removed_files.append(str(file_path))
                print(f"✅ Removed: {file_path}")
    
    def archive_redundant_docs(self, redundant_docs: list):
        """Archive redundant documentation to docs/archive/"""
        print("\n📦 Archiving redundant documentation...")
        
        archive_path = self.create_archive_dir()
        
        for doc_info in redundant_docs:
            doc_path = self.repo_path / doc_info["file"]
            
            if not doc_path.exists():
                print(f"⚠️  File not found: {doc_path}")
                continue
            
            # Determine archive destination
            dest_path = archive_path / doc_path.name
            
            if self.dry_run:
                print(f"[DRY RUN] Would move: {doc_path} -> {dest_path}")
            else:
                shutil.move(str(doc_path), str(dest_path))
                self.archived_files.append(str(doc_path))
                print(f"✅ Archived: {doc_path.name}")
    
    def remove_duplicate_exports(self, duplicates: list):
        """Remove duplicate public_keys.json from exports"""
        print("\n🗑️  Removing duplicate files...")
        
        for dup_group in duplicates:
            files = dup_group["files"]
            
            # Skip the __init__.py duplicates (they're intentional)
            if any("__init__.py" in f for f in files):
                print(f"⏭️  Skipping intentional package markers: __init__.py files")
                continue
            
            # For public_keys.json, keep final_demo, remove test_export
            if "public_keys.json" in files[0]:
                for file_rel in files:
                    if "test_export" in file_rel:
                        file_path = self.repo_path / file_rel
                        
                        if not file_path.exists():
                            continue
                        
                        if self.dry_run:
                            print(f"[DRY RUN] Would remove duplicate: {file_path}")
                        else:
                            file_path.unlink()
                            self.removed_files.append(str(file_path))
                            print(f"✅ Removed duplicate: {file_path}")
    
    def generate_cleanup_report(self) -> dict:
        """Generate cleanup summary report"""
        return {
            "cleanup_timestamp": datetime.utcnow().isoformat() + "Z",
            "dry_run": self.dry_run,
            "summary": {
                "removed_files": len(self.removed_files),
                "archived_files": len(self.archived_files),
                "removed_directories": len(self.removed_dirs)
            },
            "removed_files": self.removed_files,
            "archived_files": self.archived_files,
            "removed_directories": self.removed_dirs
        }
    
    def save_cleanup_report(self, report: dict):
        """Save cleanup report"""
        report_path = self.repo_path / "bridge_backend" / "diagnostics" / "cleanup_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Cleanup report saved to: {report_path}")
    
    def print_summary(self, report: dict):
        """Print cleanup summary"""
        print("\n" + "="*60)
        print("📊 CLEANUP SUMMARY")
        print("="*60)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No files were actually modified")
        
        summary = report["summary"]
        print(f"\n✅ Files removed: {summary['removed_files']}")
        print(f"📦 Files archived: {summary['archived_files']}")
        print(f"📁 Directories removed: {summary['removed_directories']}")
        
        total = summary['removed_files'] + summary['archived_files']
        print(f"\n🎯 Total files processed: {total}")
        
        print("\n" + "="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up redundant repository files")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually perform cleanup (default is dry-run)")
    parser.add_argument("--repo-path", default="/home/runner/work/SR-AIbridge-/SR-AIbridge-",
                       help="Path to repository")
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("🔍 Running in DRY RUN mode. Use --execute to actually remove files.")
    else:
        print("⚠️  EXECUTING CLEANUP - Files will be removed/archived!")
        response = input("Are you sure? Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("❌ Cleanup cancelled.")
            return 1
    
    cleanup = RepoCleanup(args.repo_path, dry_run=dry_run)
    
    # Load scan report
    scan_report = cleanup.load_scan_report()
    if not scan_report:
        return 1
    
    # Perform cleanup
    cleanup.remove_dead_files(scan_report.get("dead_files", []))
    cleanup.archive_redundant_docs(scan_report.get("redundant_documentation", []))
    cleanup.remove_duplicate_exports(scan_report.get("duplicates", []))
    
    # Generate and save report
    cleanup_report = cleanup.generate_cleanup_report()
    cleanup.save_cleanup_report(cleanup_report)
    cleanup.print_summary(cleanup_report)
    
    if dry_run:
        print("\n💡 To execute cleanup, run: python3 scripts/repo_cleanup.py --execute")
    
    return 0


if __name__ == "__main__":
    exit(main())
