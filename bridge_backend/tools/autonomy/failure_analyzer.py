"""
Failure Pattern Analyzer for GitHub Actions Workflows

This tool analyzes workflow files and runtime logs to identify common failure patterns
and generate automated fix recommendations.
"""

import re
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone


class FailurePatternAnalyzer:
    """Analyzes GitHub Actions workflows for common failure patterns."""
    
    # Define common failure patterns
    FAILURE_PATTERNS = {
        "browser_download_blocked": {
            "detection": r"(googlechromelabs\.github\.io|storage\.googleapis\.com|ERR_CONNECTION|ETIMEDOUT.*chrome)",
            "solution": "use_playwright_system_browsers",
            "priority": "CRITICAL",
            "auto_fixable": True,
            "fix_template": {
                "add_step": {
                    "name": "Install Chrome Dependencies",
                    "run": "npx playwright install-deps\nnpx playwright install chromium"
                },
                "add_env": {
                    "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD": "true",
                    "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "false"
                }
            }
        },
        "forge_auth_failure": {
            "detection": r"(FORGE_DOMINION_ROOT.*missing|DOMINION_SEAL.*not.*found|FED_KEY.*required)",
            "solution": "inject_ephemeral_tokens",
            "priority": "HIGH",
            "auto_fixable": False,
            "fix_template": {
                "add_env": {
                    "FORGE_DOMINION_ROOT": "${{ secrets.FORGE_DOMINION_ROOT }}",
                    "DOMINION_SEAL": "${{ secrets.DOMINION_SEAL }}"
                }
            }
        },
        "container_health_timeout": {
            "detection": r"(health check.*failed|timeout.*waiting.*healthy|container.*not.*ready)",
            "solution": "adjust_health_check_intervals",
            "priority": "MEDIUM",
            "auto_fixable": True,
            "fix_template": {
                "add_timeout": "timeout-minutes: 15"
            }
        },
        "deprecated_actions": {
            "detection": r"(actions/upload-artifact@v3|actions/download-artifact@v3|actions/setup-node@v3)",
            "solution": "update_action_versions",
            "priority": "LOW",
            "auto_fixable": True,
            "fix_template": {
                "replacements": {
                    "actions/upload-artifact@v3": "actions/upload-artifact@v4",
                    "actions/download-artifact@v3": "actions/download-artifact@v4",
                    "actions/setup-node@v3": "actions/setup-node@v4"
                }
            }
        },
        "python_import_error": {
            "detection": r"(ModuleNotFoundError|ImportError|No module named)",
            "solution": "add_missing_dependencies",
            "priority": "HIGH",
            "auto_fixable": True,
            "fix_template": {
                "install_step": "pip install -r requirements.txt"
            }
        },
        "nodejs_dependency_error": {
            "detection": r"(Cannot find module|Module not found|npm ERR!)",
            "solution": "install_dependencies",
            "priority": "HIGH",
            "auto_fixable": True,
            "fix_template": {
                "install_step": "npm ci --legacy-peer-deps"
            }
        }
    }
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.issues: List[Dict[str, Any]] = []
        self.stats = {
            "total_workflows": 0,
            "workflows_with_issues": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "auto_fixable": 0
        }
    
    def analyze_workflows(self) -> Dict[str, Any]:
        """Analyze all workflow files for common patterns."""
        print(f"🔍 Analyzing workflows in {self.workflows_dir}...")
        
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        self.stats["total_workflows"] = len(workflow_files)
        
        for workflow_file in workflow_files:
            issues_found = self._analyze_workflow_file(workflow_file)
            if issues_found:
                self.stats["workflows_with_issues"] += 1
        
        return self._generate_report()
    
    def _analyze_workflow_file(self, workflow_file: Path) -> bool:
        """Analyze a single workflow file."""
        try:
            content = workflow_file.read_text()
            
            # Try to parse as YAML
            try:
                workflow_data = yaml.safe_load(content)
            except yaml.YAMLError:
                workflow_data = None
            
            issues_found = False
            
            # Get relative path if possible, otherwise use name
            try:
                file_path = str(workflow_file.relative_to("."))
            except ValueError:
                # If not in current dir, use relative to workflows_dir
                try:
                    file_path = str(workflow_file.relative_to(self.workflows_dir.parent))
                except ValueError:
                    # Fall back to just the name
                    file_path = str(workflow_file)
            
            # Check for each failure pattern
            for pattern_name, pattern_config in self.FAILURE_PATTERNS.items():
                if re.search(pattern_config["detection"], content, re.IGNORECASE):
                    issue = {
                        "file": file_path,
                        "pattern": pattern_name,
                        "severity": pattern_config["priority"],
                        "description": f"Detected {pattern_name.replace('_', ' ')}",
                        "solution": pattern_config["solution"],
                        "auto_fixable": pattern_config["auto_fixable"],
                        "fix_template": pattern_config.get("fix_template", {})
                    }
                    
                    self.issues.append(issue)
                    self.stats["total_issues"] += 1
                    issues_found = True
                    
                    # Update priority counters
                    priority = pattern_config["priority"].lower()
                    self.stats[f"{priority}_issues"] = self.stats.get(f"{priority}_issues", 0) + 1
                    
                    if pattern_config["auto_fixable"]:
                        self.stats["auto_fixable"] += 1
            
            # Check for missing browser setup in workflows that need it
            if "playwright" in content.lower() or "puppeteer" in content.lower():
                if "PUPPETEER_SKIP" not in content and "playwright install" not in content:
                    issue = {
                        "file": file_path,
                        "pattern": "missing_browser_setup",
                        "severity": "MEDIUM",
                        "description": "Browser tools without proper configuration",
                        "solution": "add_browser_setup",
                        "auto_fixable": True,
                        "fix_template": {
                            "add_step": "- name: Setup Browsers\n  run: |\n    npx playwright install-deps\n    npx playwright install chromium"
                        }
                    }
                    self.issues.append(issue)
                    self.stats["total_issues"] += 1
                    self.stats["medium_issues"] += 1
                    self.stats["auto_fixable"] += 1
                    issues_found = True
            
            return issues_found
            
        except Exception as e:
            print(f"⚠️ Error analyzing {workflow_file.name}: {e}")
            return False
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate analysis report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stats": self.stats,
            "issues": self.issues,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate fix recommendations based on detected issues."""
        recommendations = []
        
        # Group issues by pattern
        issues_by_pattern = {}
        for issue in self.issues:
            pattern = issue["pattern"]
            if pattern not in issues_by_pattern:
                issues_by_pattern[pattern] = []
            issues_by_pattern[pattern].append(issue)
        
        # Generate recommendations for each pattern
        for pattern, issues in issues_by_pattern.items():
            recommendation = {
                "pattern": pattern,
                "affected_files": [issue["file"] for issue in issues],
                "count": len(issues),
                "severity": issues[0]["severity"],
                "auto_fixable": issues[0]["auto_fixable"],
                "action": self._get_action_for_pattern(pattern, issues)
            }
            recommendations.append(recommendation)
        
        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: severity_order.get(x["severity"], 99))
        
        return recommendations
    
    def _get_action_for_pattern(self, pattern: str, issues: List[Dict]) -> str:
        """Get recommended action for a pattern."""
        if pattern == "browser_download_blocked":
            return "Add browser dependency resolution step to affected workflows"
        elif pattern == "deprecated_actions":
            return "Update action versions from v3 to v4"
        elif pattern == "forge_auth_failure":
            return "Configure FORGE_DOMINION_ROOT and DOMINION_SEAL secrets"
        elif pattern == "missing_browser_setup":
            return "Add Playwright/Puppeteer installation steps"
        else:
            return f"Review and fix {pattern.replace('_', ' ')}"
    
    def save_report(self, output_file: str = "bridge_backend/diagnostics/failure_analysis.json"):
        """Save analysis report to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self._generate_report()
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Analysis report saved to {output_path}")
        return output_path
    
    def print_summary(self):
        """Print analysis summary to console."""
        print("\n" + "=" * 70)
        print("🔍 FAILURE PATTERN ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"\n📊 Workflow Statistics:")
        print(f"  Total workflows analyzed: {self.stats['total_workflows']}")
        print(f"  Workflows with issues: {self.stats['workflows_with_issues']}")
        print(f"  Total issues found: {self.stats['total_issues']}")
        
        print(f"\n🎯 Issues by Severity:")
        print(f"  🔴 CRITICAL: {self.stats.get('critical_issues', 0)}")
        print(f"  🟠 HIGH: {self.stats.get('high_issues', 0)}")
        print(f"  🟡 MEDIUM: {self.stats.get('medium_issues', 0)}")
        print(f"  🟢 LOW: {self.stats.get('low_issues', 0)}")
        
        print(f"\n🤖 Auto-Fix Capability:")
        print(f"  Auto-fixable issues: {self.stats.get('auto_fixable', 0)}")
        print(f"  Manual intervention needed: {self.stats['total_issues'] - self.stats.get('auto_fixable', 0)}")
        
        print("\n" + "=" * 70 + "\n")


def main():
    """Main entry point for the failure analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Actions workflows for common failure patterns"
    )
    parser.add_argument(
        "--input",
        default=".github/workflows",
        help="Path to workflows directory (default: .github/workflows)"
    )
    parser.add_argument(
        "--output",
        default="bridge_backend/diagnostics/failure_analysis.json",
        help="Output file for analysis report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = FailurePatternAnalyzer(workflows_dir=args.input)
    
    # Run analysis
    report = analyzer.analyze_workflows()
    
    # Save report
    analyzer.save_report(output_file=args.output)
    
    # Print summary
    analyzer.print_summary()
    
    # Exit with appropriate code
    if analyzer.stats["total_issues"] > 0:
        print(f"⚠️ Found {analyzer.stats['total_issues']} issues that need attention")
        return 1
    else:
        print("✅ No issues detected!")
        return 0


if __name__ == "__main__":
    exit(main())
