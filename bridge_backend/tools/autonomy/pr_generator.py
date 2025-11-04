"""
Auto-Fix PR Generator for Workflow Failures

This tool generates automated fixes for common workflow failure patterns
and can create fix scripts or recommendations.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone


class PRGenerator:
    """Generates automated fixes for workflow issues."""
    
    def __init__(self, plan_file: str):
        self.plan_file = Path(plan_file)
        self.fixes_applied = []
        self.fixes_failed = []
    
    def load_plan(self) -> Dict[str, Any]:
        """Load the fix plan from JSON file."""
        if not self.plan_file.exists():
            raise FileNotFoundError(f"Fix plan not found: {self.plan_file}")
        
        with open(self.plan_file) as f:
            return json.load(f)
    
    def generate_fixes(self, dry_run: bool = True) -> Dict[str, Any]:
        """Generate fixes based on the plan."""
        print(f"🔧 Loading fix plan from {self.plan_file}...")
        plan = self.load_plan()
        
        print(f"\n📋 Fix Plan Summary:")
        print(f"  Total issues: {len(plan.get('issues', []))}")
        print(f"  Auto-fixable: {sum(1 for issue in plan.get('issues', []) if issue.get('auto_fixable', False))}")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be applied")
        
        # Group fixes by file
        fixes_by_file = {}
        for issue in plan.get("issues", []):
            if not issue.get("auto_fixable", False):
                continue
            
            file_path = issue.get("file")
            if file_path not in fixes_by_file:
                fixes_by_file[file_path] = []
            fixes_by_file[file_path].append(issue)
        
        # Generate fixes for each file
        for file_path, issues in fixes_by_file.items():
            self._generate_file_fixes(file_path, issues, dry_run)
        
        return self._generate_summary()
    
    def _generate_file_fixes(self, file_path: str, issues: List[Dict], dry_run: bool):
        """Generate fixes for a specific file."""
        print(f"\n📝 Processing {file_path}...")
        
        file = Path(file_path)
        if not file.exists():
            print(f"  ⚠️ File not found: {file_path}")
            self.fixes_failed.append({
                "file": file_path,
                "reason": "File not found"
            })
            return
        
        try:
            content = file.read_text()
            modified_content = content
            changes_made = []
            
            for issue in issues:
                issue_type = issue.get("issue_type", "unknown")
                
                # Apply fixes based on issue type
                if issue_type == "deprecated_actions":
                    modified_content, changed = self._fix_deprecated_actions(modified_content)
                    if changed:
                        changes_made.append("Updated deprecated action versions")
                
                elif issue_type == "browser_config":
                    modified_content, changed = self._add_browser_env_vars(modified_content)
                    if changed:
                        changes_made.append("Added browser configuration")
            
            if changes_made:
                if not dry_run:
                    file.write_text(modified_content)
                    print(f"  ✅ Applied fixes: {', '.join(changes_made)}")
                else:
                    print(f"  🔍 Would apply: {', '.join(changes_made)}")
                
                self.fixes_applied.append({
                    "file": file_path,
                    "changes": changes_made,
                    "applied": not dry_run
                })
            else:
                print(f"  ℹ️ No automatic fixes available")
        
        except Exception as e:
            print(f"  ❌ Error processing file: {e}")
            self.fixes_failed.append({
                "file": file_path,
                "reason": str(e)
            })
    
    def _fix_deprecated_actions(self, content: str) -> tuple[str, bool]:
        """Fix deprecated GitHub Actions versions."""
        replacements = {
            "actions/upload-artifact@v3": "actions/upload-artifact@v4",
            "actions/download-artifact@v3": "actions/download-artifact@v4",
            "actions/setup-node@v3": "actions/setup-node@v4",
            "actions/setup-python@v4": "actions/setup-python@v5"
        }
        
        modified = content
        changed = False
        
        for old, new in replacements.items():
            if old in modified:
                modified = modified.replace(old, new)
                changed = True
        
        return modified, changed
    
    def _add_browser_env_vars(self, content: str) -> tuple[str, bool]:
        """Add browser-related environment variables."""
        # This is a simple implementation - in production, you'd want more sophisticated YAML parsing
        
        if "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD" in content:
            return content, False  # Already has the config
        
        # Look for env: section and add if not present
        # This is a placeholder - actual implementation would need proper YAML manipulation
        return content, False
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of fixes."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fixes_applied": len(self.fixes_applied),
            "fixes_failed": len(self.fixes_failed),
            "applied_details": self.fixes_applied,
            "failed_details": self.fixes_failed
        }
    
    def save_summary(self, output_file: str = "bridge_backend/diagnostics/fix_summary.json"):
        """Save fix summary to file."""
        summary = self._generate_summary()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Fix summary saved to {output_path}")
    
    def print_summary(self):
        """Print fix summary."""
        print("\n" + "=" * 70)
        print("🔧 FIX GENERATION SUMMARY")
        print("=" * 70)
        print(f"\n✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"  • {fix['file']}")
            for change in fix['changes']:
                print(f"    - {change}")
        
        if self.fixes_failed:
            print(f"\n❌ Fixes Failed: {len(self.fixes_failed)}")
            for fix in self.fixes_failed:
                print(f"  • {fix['file']}: {fix['reason']}")
        
        print("\n" + "=" * 70 + "\n")
    
    def generate_recommendations(self) -> str:
        """Generate human-readable recommendations."""
        recommendations = []
        recommendations.append("# Workflow Fix Recommendations\n")
        recommendations.append(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
        recommendations.append("\n## Auto-Applied Fixes\n")
        
        if self.fixes_applied:
            for fix in self.fixes_applied:
                recommendations.append(f"### {fix['file']}\n")
                for change in fix['changes']:
                    recommendations.append(f"- {change}\n")
                recommendations.append("\n")
        else:
            recommendations.append("No fixes were auto-applied.\n\n")
        
        recommendations.append("## Manual Actions Required\n")
        recommendations.append("\n### Configure GitHub Secrets\n")
        recommendations.append("Add the following secrets in GitHub repository settings:\n")
        recommendations.append("- `FORGE_DOMINION_ROOT`: Forge dominion root path\n")
        recommendations.append("- `DOMINION_SEAL`: Dominion authentication seal\n")
        recommendations.append("- `NETLIFY_AUTH_TOKEN`: Netlify authentication token\n")
        recommendations.append("- `NETLIFY_SITE_ID`: Netlify site identifier\n")
        
        return "".join(recommendations)


def main():
    """Main entry point for PR generator."""
    parser = argparse.ArgumentParser(
        description="Generate automated fixes for workflow issues"
    )
    parser.add_argument(
        "--plan",
        required=True,
        help="Path to fix plan JSON file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry run mode (default: True)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually apply fixes (disables dry-run)"
    )
    parser.add_argument(
        "--output",
        default="bridge_backend/diagnostics/fix_summary.json",
        help="Output file for fix summary"
    )
    
    args = parser.parse_args()
    
    # Determine if we should actually apply fixes
    dry_run = not args.apply
    
    # Create generator
    generator = PRGenerator(plan_file=args.plan)
    
    # Generate fixes
    generator.generate_fixes(dry_run=dry_run)
    
    # Save summary
    generator.save_summary(output_file=args.output)
    
    # Print summary
    generator.print_summary()
    
    # Generate recommendations
    recommendations = generator.generate_recommendations()
    rec_file = Path("bridge_backend/diagnostics/recommendations.md")
    rec_file.parent.mkdir(parents=True, exist_ok=True)
    rec_file.write_text(recommendations)
    print(f"📝 Recommendations saved to {rec_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
