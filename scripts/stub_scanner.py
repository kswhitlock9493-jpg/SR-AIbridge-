#!/usr/bin/env python3
"""
Comprehensive Stub Scanner
Scans repository for stubbed files that may cause deployment issues
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class StubScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.issues = {
            "frontend_stubs_with_todos": [],
            "backend_stub_routes": [],
            "incomplete_engines": [],
            "missing_route_registrations": [],
            "deprecated_warnings": []
        }
        
    def scan_frontend_stubs(self):
        """Scan frontend auto-generated stubs for TODO markers"""
        print("🔍 Scanning frontend auto-generated stubs...")
        
        auto_gen_dir = self.repo_path / "bridge-frontend" / "src" / "api" / "auto_generated"
        if not auto_gen_dir.exists():
            print(f"  ⚠️  Auto-generated directory not found: {auto_gen_dir}")
            return
        
        stub_files = list(auto_gen_dir.glob("*.js"))
        total = len(stub_files)
        todos = 0
        
        for stub_file in stub_files:
            try:
                content = stub_file.read_text(encoding='utf-8')
                if "TODO: Review and integrate this auto-generated stub" in content:
                    todos += 1
                    self.issues["frontend_stubs_with_todos"].append({
                        "file": str(stub_file.relative_to(self.repo_path)),
                        "issue": "Contains TODO comment for stub review"
                    })
            except Exception as e:
                print(f"  ⚠️  Error reading {stub_file}: {e}")
        
        print(f"  Found {total} stub files, {todos} with TODO markers")
    
    def scan_backend_stubs(self):
        """Scan backend for stub implementations"""
        print("🔍 Scanning backend for stub implementations...")
        
        stub_patterns = [
            r'return.*"not_implemented"',
            r'status.*not_implemented',
            r'stub.*implementation',
            r'placeholder.*implementation',
            r'TODO.*implement.*endpoint',
            r'def.*stub_'
        ]
        
        backend_path = self.repo_path / "bridge_backend"
        if not backend_path.exists():
            print(f"  ⚠️  Backend directory not found: {backend_path}")
            return
        
        py_files = list(backend_path.glob("**/*.py"))
        stub_count = 0
        
        for py_file in py_files:
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in stub_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        stub_count += 1
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues["backend_stub_routes"].append({
                            "file": str(py_file.relative_to(self.repo_path)),
                            "line": line_num,
                            "pattern": pattern,
                            "match": match.group(0)[:50]
                        })
            except Exception as e:
                pass  # Skip files we can't read
        
        print(f"  Found {stub_count} potential stub implementations")
    
    def scan_engine_completeness(self):
        """Check if all engines have proper implementations"""
        print("🔍 Scanning engine completeness...")
        
        engines_path = self.repo_path / "bridge_backend" / "bridge_core" / "engines"
        if not engines_path.exists():
            print(f"  ⚠️  Engines directory not found: {engines_path}")
            return
        
        # Expected engine components
        expected_files = ["routes.py", "__init__.py"]
        
        engine_dirs = [d for d in engines_path.iterdir() if d.is_dir() and not d.name.startswith("_")]
        
        for engine_dir in engine_dirs:
            missing = []
            for expected in expected_files:
                if not (engine_dir / expected).exists():
                    missing.append(expected)
            
            if missing:
                self.issues["incomplete_engines"].append({
                    "engine": engine_dir.name,
                    "missing_files": missing
                })
        
        print(f"  Checked {len(engine_dirs)} engines")
    
    def scan_route_registrations(self):
        """Check if all engine routes are registered in main.py"""
        print("🔍 Scanning route registrations...")
        
        main_py = self.repo_path / "bridge_backend" / "main.py"
        if not main_py.exists():
            print(f"  ⚠️  main.py not found")
            return
        
        # Get all engine routes
        engines_path = self.repo_path / "bridge_backend" / "bridge_core" / "engines"
        if not engines_path.exists():
            return
        
        engine_routes = []
        for engine_dir in engines_path.iterdir():
            if engine_dir.is_dir() and (engine_dir / "routes.py").exists():
                engine_routes.append(engine_dir.name)
        
        # Check main.py for registrations
        main_content = main_py.read_text(encoding='utf-8')
        
        for engine in engine_routes:
            # Skip special cases
            if engine in ["__pycache__", "adapters"]:
                continue
            
            # Check if registered
            pattern = f"engines.{engine}.routes"
            if pattern not in main_content:
                self.issues["missing_route_registrations"].append({
                    "engine": engine,
                    "expected_import": f"bridge_backend.bridge_core.engines.{engine}.routes"
                })
        
        print(f"  Checked {len(engine_routes)} engine route registrations")
    
    def scan_deprecated_code(self):
        """Scan for deprecated warnings that could cause issues"""
        print("🔍 Scanning for deprecation warnings...")
        
        backend_path = self.repo_path / "bridge_backend"
        if not backend_path.exists():
            return
        
        # Look for common deprecation issues
        deprecated_patterns = [
            (r'datetime\.utcnow\(\)', 'datetime.utcnow() is deprecated, use datetime.now(datetime.UTC)'),
        ]
        
        py_files = list(backend_path.glob("**/*.py"))
        dep_count = 0
        
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern, message in deprecated_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        dep_count += 1
                        line_num = content[:match.start()].count('\n') + 1
                        self.issues["deprecated_warnings"].append({
                            "file": str(py_file.relative_to(self.repo_path)),
                            "line": line_num,
                            "issue": message,
                            "code": match.group(0)
                        })
            except Exception:
                pass
        
        print(f"  Found {dep_count} potential deprecation warnings")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive stub scan report"""
        total_issues = sum(len(v) for v in self.issues.values())
        
        report = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "repo_path": str(self.repo_path),
            "summary": {
                "total_issues": total_issues,
                "frontend_stubs_with_todos": len(self.issues["frontend_stubs_with_todos"]),
                "backend_stub_routes": len(self.issues["backend_stub_routes"]),
                "incomplete_engines": len(self.issues["incomplete_engines"]),
                "missing_route_registrations": len(self.issues["missing_route_registrations"]),
                "deprecated_warnings": len(self.issues["deprecated_warnings"])
            },
            "issues": self.issues,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if self.issues["frontend_stubs_with_todos"]:
            recommendations.append({
                "priority": "low",
                "category": "frontend_cleanup",
                "action": "Remove TODO comments from production-ready auto-generated stubs",
                "affected_files": len(self.issues["frontend_stubs_with_todos"]),
                "details": "These stubs are functional but contain TODO markers that should be removed"
            })
        
        if self.issues["backend_stub_routes"]:
            recommendations.append({
                "priority": "high",
                "category": "backend_implementation",
                "action": "Review and implement backend stub routes",
                "affected_files": len(self.issues["backend_stub_routes"]),
                "details": "Backend routes with stub implementations may need proper implementation"
            })
        
        if self.issues["incomplete_engines"]:
            recommendations.append({
                "priority": "medium",
                "category": "engine_completion",
                "action": "Complete missing engine files",
                "affected_engines": len(self.issues["incomplete_engines"]),
                "details": "Some engines are missing expected files (routes.py, __init__.py)"
            })
        
        if self.issues["missing_route_registrations"]:
            recommendations.append({
                "priority": "high",
                "category": "route_registration",
                "action": "Register missing engine routes in main.py",
                "affected_engines": len(self.issues["missing_route_registrations"]),
                "details": "Engine routes exist but are not registered in the main application"
            })
        
        if self.issues["deprecated_warnings"]:
            recommendations.append({
                "priority": "medium",
                "category": "deprecation_fix",
                "action": "Fix deprecated code patterns",
                "affected_files": len(self.issues["deprecated_warnings"]),
                "details": "Code uses deprecated patterns that may cause warnings or future failures"
            })
        
        return recommendations
    
    def print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📊 STUB SCAN SUMMARY")
        print("="*60)
        
        summary = report["summary"]
        print(f"\n🔍 Issues Found: {summary['total_issues']}")
        
        if summary["frontend_stubs_with_todos"] > 0:
            print(f"\n📝 Frontend Stubs with TODOs: {summary['frontend_stubs_with_todos']}")
            for item in report["issues"]["frontend_stubs_with_todos"][:5]:
                print(f"  - {item['file']}")
            if summary["frontend_stubs_with_todos"] > 5:
                print(f"  ... and {summary['frontend_stubs_with_todos'] - 5} more")
        
        if summary["backend_stub_routes"] > 0:
            print(f"\n🔧 Backend Stub Routes: {summary['backend_stub_routes']}")
            for item in report["issues"]["backend_stub_routes"][:5]:
                print(f"  - {item['file']}:{item['line']} - {item['match']}")
            if summary["backend_stub_routes"] > 5:
                print(f"  ... and {summary['backend_stub_routes'] - 5} more")
        
        if summary["incomplete_engines"] > 0:
            print(f"\n⚠️  Incomplete Engines: {summary['incomplete_engines']}")
            for item in report["issues"]["incomplete_engines"]:
                print(f"  - {item['engine']}: missing {', '.join(item['missing_files'])}")
        
        if summary["missing_route_registrations"] > 0:
            print(f"\n🚫 Missing Route Registrations: {summary['missing_route_registrations']}")
            for item in report["issues"]["missing_route_registrations"]:
                print(f"  - {item['engine']}")
        
        if summary["deprecated_warnings"] > 0:
            print(f"\n⏰ Deprecated Code Patterns: {summary['deprecated_warnings']}")
            for item in report["issues"]["deprecated_warnings"][:5]:
                print(f"  - {item['file']}:{item['line']} - {item['issue']}")
            if summary["deprecated_warnings"] > 5:
                print(f"  ... and {summary['deprecated_warnings'] - 5} more")
        
        print("\n📋 Recommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
            print(f"  {i}. {priority_emoji} [{rec['priority'].upper()}] {rec['action']}")
            print(f"     {rec['details']}")
        
        print("\n" + "="*60)


def main():
    repo_path = os.getenv("REPO_PATH", "/home/runner/work/SR-AIbridge-/SR-AIbridge-")
    
    scanner = StubScanner(repo_path)
    
    # Run scans
    scanner.scan_frontend_stubs()
    scanner.scan_backend_stubs()
    scanner.scan_engine_completeness()
    scanner.scan_route_registrations()
    scanner.scan_deprecated_code()
    
    # Generate and save report
    report = scanner.generate_report()
    
    # Save JSON report
    report_path = Path(repo_path) / "bridge_backend" / "diagnostics" / "stub_scan_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    scanner.print_summary(report)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
