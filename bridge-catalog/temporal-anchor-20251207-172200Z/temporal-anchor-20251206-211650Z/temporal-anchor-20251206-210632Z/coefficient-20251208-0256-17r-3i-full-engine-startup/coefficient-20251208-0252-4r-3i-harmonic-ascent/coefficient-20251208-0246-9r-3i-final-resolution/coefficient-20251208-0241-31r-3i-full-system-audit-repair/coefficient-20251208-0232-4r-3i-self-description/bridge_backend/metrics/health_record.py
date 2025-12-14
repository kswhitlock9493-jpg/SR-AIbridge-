#!/usr/bin/env python3
"""
Bridge Health Record System
Aggregates Umbra + Self-Test results into JSON and Markdown
Maintains 90-day rolling history with auto-compression
"""

import click
import json
import sys
import os
import gzip
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional


def load_json_report(filepath: str) -> Dict[str, Any]:
    """Load JSON report file"""
    try:
        path = Path(filepath)
        if not path.exists():
            print(f"⚠️  Report file not found: {filepath}", file=sys.stderr)
            return {}
        
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load {filepath}: {e}", file=sys.stderr)
        return {}


def calculate_health_score(selftest: Dict[str, Any], umbra: Dict[str, Any]) -> int:
    """
    Calculate overall bridge health score (0-100)
    
    Factors:
    - Selftest pass rate (50%)
    - Umbra critical/warning count (30%)
    - Heal success rate (20%)
    """
    score = 100
    
    # Selftest pass rate (50%)
    if selftest:
        total_tests = selftest.get("total_tests", 0)
        passed_tests = selftest.get("passed_tests", 0)
        
        if total_tests > 0:
            pass_rate = (passed_tests / total_tests) * 50
            score = pass_rate
        else:
            score = 50  # No tests = neutral
    
    # Umbra issues (30%)
    if umbra:
        critical_count = umbra.get("critical_count", 0)
        warning_count = umbra.get("warning_count", 0)
        
        # Deduct points for issues
        issue_penalty = (critical_count * 10) + (warning_count * 3)
        score -= min(issue_penalty, 30)
    
    # Heal success rate (20%)
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


def aggregate_health_record(selftest: Dict[str, Any], umbra: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate selftest and Umbra results into health record
    """
    health_score = calculate_health_score(selftest, umbra)
    
    # Determine truth certification
    truth_certified = True
    if selftest.get("truth_certification_failed") or umbra.get("truth_certification_failed"):
        truth_certified = False
    
    # Determine status
    if health_score >= 95:
        status = "passing"
    elif health_score >= 80:
        status = "warning"
    else:
        status = "critical"
    
    # Calculate auto-heals
    auto_heals = umbra.get("tickets_healed", 0) if umbra else 0
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bridge_health_score": health_score,
        "auto_heals": auto_heals,
        "truth_certified": truth_certified,
        "status": status,
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


def generate_markdown_record(record: Dict[str, Any]) -> str:
    """
    Generate Markdown summary of health record
    """
    health_score = record["bridge_health_score"]
    status = record["status"]
    truth_certified = record["truth_certified"]
    auto_heals = record["auto_heals"]
    
    # Header with status emoji
    if status == "passing":
        emoji = "🟢"
        status_text = "Passing"
    elif status == "warning":
        emoji = "🟡"
        status_text = "Warning"
    else:
        emoji = "🔴"
        status_text = "Critical"
    
    md = f"# {emoji} Bridge Health Report\n\n"
    md += f"**Health Score:** {health_score}% ({status_text})\n\n"
    md += f"**Truth Certified:** {'✅ Yes' if truth_certified else '❌ No'}\n\n"
    md += f"**Auto-Heals:** {auto_heals}\n\n"
    md += f"**Timestamp:** {record['timestamp']}\n\n"
    
    # Self-test details
    selftest = record["selftest"]
    md += "## Self-Test Results\n\n"
    md += f"- Total Tests: {selftest['total_tests']}\n"
    md += f"- Passed: {selftest['passed_tests']} ✅\n"
    md += f"- Failed: {selftest['failed_tests']} ❌\n"
    md += f"- Engines: {selftest['engines_active']}/{selftest['engines_total']} certified\n\n"
    
    # Umbra details
    umbra = record["umbra"]
    md += "## Umbra Triage\n\n"
    md += f"- Critical Issues: {umbra['critical_count']} ❌\n"
    md += f"- Warnings: {umbra['warning_count']} ⚠️\n"
    md += f"- Tickets Opened: {umbra['tickets_opened']}\n"
    md += f"- Tickets Healed: {umbra['tickets_healed']} 🩹\n"
    md += f"- Heal Plans Generated: {umbra['heal_plans_generated']}\n"
    md += f"- Rollbacks: {umbra['rollbacks']}\n\n"
    
    return md


def write_health_history(record: Dict[str, Any], output_dir: str):
    """
    Write health record to history directory with timestamped filename
    Also write as 'latest.json' for easy reference
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Timestamped filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    history_file = output_path / f"health_{timestamp}.json"
    
    # Write timestamped record
    with open(history_file, 'w') as f:
        json.dump(record, f, indent=2)
    
    # Write latest.json for easy access
    latest_file = output_path / "latest.json"
    with open(latest_file, 'w') as f:
        json.dump(record, f, indent=2)
    
    print(f"✅ Health record written:")
    print(f"   History: {history_file}")
    print(f"   Latest: {latest_file}")
    
    return history_file, latest_file


def compress_old_records(output_dir: str, days: int = 90):
    """
    Compress health records older than specified days
    Delete records older than 90 days
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    compress_date = datetime.now(timezone.utc) - timedelta(days=7)  # Compress after 7 days
    
    compressed_count = 0
    deleted_count = 0
    
    for file in output_path.glob("health_*.json"):
        # Skip if already compressed
        if file.suffix == '.gz':
            continue
        
        # Get file modification time
        mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
        
        # Delete if older than 90 days
        if mtime < cutoff_date:
            file.unlink()
            deleted_count += 1
            print(f"🗑️  Deleted old record: {file.name}")
        # Compress if older than 7 days
        elif mtime < compress_date:
            # Read and compress
            with open(file, 'rb') as f_in:
                with gzip.open(f"{file}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            file.unlink()
            compressed_count += 1
            print(f"📦 Compressed: {file.name} → {file.name}.gz")
    
    if compressed_count > 0 or deleted_count > 0:
        print(f"\n🧹 Cleanup: {compressed_count} compressed, {deleted_count} deleted")


@click.command()
@click.option("--selftest", required=True, help="Path to selftest JSON report")
@click.option("--umbra", required=True, help="Path to Umbra JSON report")
@click.option("--output-dir", required=True, help="Output directory for health history")
def main(selftest: str, umbra: str, output_dir: str):
    """
    Generate and publish Bridge health record
    Aggregates Umbra + Self-Test results
    """
    try:
        print("🩺 Generating Bridge Health Record...")
        
        # Load reports
        selftest_data = load_json_report(selftest)
        umbra_data = load_json_report(umbra)
        
        # Aggregate health record
        health_record = aggregate_health_record(selftest_data, umbra_data)
        
        # Generate markdown
        markdown = generate_markdown_record(health_record)
        
        # Write health history
        history_file, latest_file = write_health_history(health_record, output_dir)
        
        # Write markdown report
        md_file = Path(output_dir) / "latest.md"
        with open(md_file, 'w') as f:
            f.write(markdown)
        print(f"   Markdown: {md_file}")
        
        # Compress old records
        compress_old_records(output_dir)
        
        # Display summary
        print(f"\n📊 Health Summary:")
        print(f"   Score: {health_record['bridge_health_score']}%")
        print(f"   Status: {health_record['status']}")
        print(f"   Truth Certified: {health_record['truth_certified']}")
        print(f"   Auto-Heals: {health_record['auto_heals']}")
        
    except Exception as e:
        print(f"❌ Failed to generate health record: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
