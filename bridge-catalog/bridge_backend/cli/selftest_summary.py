"""
Self-Test Summary Generator
Generates PR health summary from selftest and Umbra reports
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime


def load_json_report(filepath: str) -> dict:
    """Load JSON report file"""
    try:
        path = Path(filepath)
        if not path.exists():
            return {}
        
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)
        return {}


def calculate_health_score(selftest: dict, umbra: dict) -> int:
    """
    Calculate overall health score (0-100)
    
    Factors:
    - Selftest pass rate (50%)
    - Umbra critical/warning count (30%)
    - Heal success rate (20%)
    """
    score = 100
    
    # Selftest pass rate
    if selftest:
        total_tests = selftest.get("total_tests", 0)
        passed_tests = selftest.get("passed_tests", 0)
        
        if total_tests > 0:
            pass_rate = (passed_tests / total_tests) * 50
            score = pass_rate
        else:
            score = 50  # No tests = neutral
    
    # Umbra issues
    if umbra:
        critical_count = umbra.get("critical_count", 0)
        warning_count = umbra.get("warning_count", 0)
        
        # Deduct points for issues
        issue_penalty = (critical_count * 10) + (warning_count * 3)
        score -= min(issue_penalty, 30)
    
    # Heal success rate
    if umbra:
        healed = umbra.get("tickets_healed", 0)
        failed = umbra.get("tickets_failed", 0)
        total_heal_attempts = healed + failed
        
        if total_heal_attempts > 0:
            heal_rate = (healed / total_heal_attempts) * 20
            score += heal_rate
        else:
            score += 20  # No heal attempts = full points
    
    return max(0, min(100, int(score)))


def generate_markdown_summary(selftest: dict, umbra: dict, health_score: int) -> str:
    """Generate markdown summary for PR comment"""
    
    # Header
    md = f"### 🤖 Bridge Health: {health_score}%\n\n"
    
    # Health indicator
    if health_score >= 95:
        md += "✅ **Excellent** - All systems nominal\n\n"
    elif health_score >= 80:
        md += "✅ **Good** - Minor issues detected\n\n"
    elif health_score >= 60:
        md += "⚠️ **Fair** - Some issues need attention\n\n"
    else:
        md += "❌ **Poor** - Critical issues detected\n\n"
    
    # Selftest results
    if selftest:
        total = selftest.get("total_tests", 0)
        passed = selftest.get("passed_tests", 0)
        failed = selftest.get("failed_tests", 0)
        
        md += f"**Self-Test Results:**\n"
        md += f"- Total: {total} tests\n"
        md += f"- Passed: {passed} ✅\n"
        
        if failed > 0:
            md += f"- Failed: {failed} ❌\n"
        
        # Engine certification
        engines_total = selftest.get("engines_total", 0)
        engines_active = selftest.get("engines_active", 0)
        
        if engines_total > 0:
            md += f"- Engines certified: {engines_active}/{engines_total} ✅\n"
        
        md += "\n"
    
    # Umbra results
    if umbra:
        critical = umbra.get("critical_count", 0)
        warnings = umbra.get("warning_count", 0)
        tickets_open = umbra.get("tickets_opened", 0)
        
        md += f"**Umbra Triage (last run):**\n"
        
        if critical == 0 and warnings == 0:
            md += f"- No incidents detected ✅\n"
        else:
            if critical > 0:
                md += f"- Critical incidents: {critical} ❌\n"
            if warnings > 0:
                md += f"- Warnings: {warnings} ⚠️\n"
        
        # Heal info
        heal_plans = umbra.get("heal_plans_generated", 0)
        healed = umbra.get("tickets_healed", 0)
        
        if heal_plans > 0:
            if healed > 0:
                md += f"- Auto-heals applied: {healed} 🩹\n"
            else:
                md += f"- Heal plans generated: {heal_plans} (intent-mode)\n"
        
        md += "\n"
    
    # Truth certification
    truth_certified = True
    if selftest.get("truth_certification_failed"):
        truth_certified = False
    
    md += f"**Truth Certification:** {'✅' if truth_certified else '❌'}\n\n"
    
    # Rollbacks
    rollbacks = umbra.get("rollbacks", 0) if umbra else 0
    md += f"**Rollbacks:** {rollbacks}\n\n"
    
    # Artifacts
    md += "**Artifacts:** `bridge_diagnostic_bundle`\n"
    
    return md


def generate_json_summary(selftest: dict, umbra: dict, health_score: int) -> dict:
    """Generate JSON summary"""
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "health_score": health_score,
        "selftest": {
            "total_tests": selftest.get("total_tests", 0),
            "passed_tests": selftest.get("passed_tests", 0),
            "failed_tests": selftest.get("failed_tests", 0),
            "engines_total": selftest.get("engines_total", 0),
            "engines_active": selftest.get("engines_active", 0)
        },
        "umbra": {
            "critical_count": umbra.get("critical_count", 0),
            "warning_count": umbra.get("warning_count", 0),
            "tickets_opened": umbra.get("tickets_opened", 0),
            "tickets_healed": umbra.get("tickets_healed", 0),
            "tickets_failed": umbra.get("tickets_failed", 0),
            "heal_plans_generated": umbra.get("heal_plans_generated", 0),
            "heal_plans_applied": umbra.get("heal_plans_applied", 0),
            "rollbacks": umbra.get("rollbacks", 0)
        }
    }


@click.command()
@click.option("--selftest", required=True, help="Path to selftest JSON report")
@click.option("--umbra", required=True, help="Path to Umbra JSON report")
@click.option("--out-md", required=True, help="Output path for markdown summary")
@click.option("--out-json", required=True, help="Output path for JSON summary")
def main(selftest, umbra, out_md, out_json):
    """Generate PR health summary from selftest and Umbra reports"""
    
    # Load reports
    selftest_data = load_json_report(selftest)
    umbra_data = load_json_report(umbra)
    
    # Calculate health score
    health_score = calculate_health_score(selftest_data, umbra_data)
    
    # Generate markdown
    md_content = generate_markdown_summary(selftest_data, umbra_data, health_score)
    
    # Generate JSON
    json_content = generate_json_summary(selftest_data, umbra_data, health_score)
    
    # Write outputs
    try:
        # Ensure output directories exist
        Path(out_md).parent.mkdir(parents=True, exist_ok=True)
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)
        
        # Write markdown
        with open(out_md, 'w') as f:
            f.write(md_content)
        
        # Write JSON
        with open(out_json, 'w') as f:
            json.dump(json_content, f, indent=2)
        
        print(f"✅ Summary generated:")
        print(f"   Markdown: {out_md}")
        print(f"   JSON: {out_json}")
        print(f"   Health Score: {health_score}%")
        
    except Exception as e:
        print(f"❌ Failed to write output: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
