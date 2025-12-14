#!/usr/bin/env python3
"""
Triage Pre-Seed Generator
Seeds all diagnostic and triage systems with initial baseline data.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Import utility function
try:
    from utils import now
except ImportError:
    from scripts.utils import now

SEED_EVENTS = [
    {"type": "CI_CD_TRIAGE", "status": "HEALTHY"},
    {"type": "ENDPOINT_TRIAGE", "status": "HEALTHY"},
    {"type": "API_TRIAGE", "status": "HEALTHY"},
    {"type": "HOOKS_TRIAGE", "status": "HEALTHY"},
]


def seed_reports() -> None:
    """
    Generate baseline triage report files for all triage systems.
    """
    print("🌱 Seeding baseline triage reports...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    # Go up to the bridge_backend directory
    base_dir = script_dir.parent
    
    for ev in SEED_EVENTS:
        report = {
            "type": ev["type"],
            "status": ev["status"],
            "source": "PreSeed",
            "meta": {
                "timestamp": now(),
                "note": "Baseline initialization seed",
                "results": [],
                "environment": "backend"
            },
        }
        # Create filename from event type
        filename = f"{ev['type'].lower()}_report.json".replace("_triage", "")
        
        # Special handling for different report types
        if ev["type"] == "ENDPOINT_TRIAGE":
            filename = "endpoint_report.json"
        elif ev["type"] == "API_TRIAGE":
            filename = "api_triage_report.json"
        elif ev["type"] == "HOOKS_TRIAGE":
            filename = "hooks_triage_report.json"
        elif ev["type"] == "CI_CD_TRIAGE":
            filename = "ci_cd_report.json"
        
        file_path = base_dir / filename
        
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"  ✅ Created {filename}")
        except Exception as e:
            print(f"  ⚠️ Failed to create {filename}: {e}")
    
    print("✅ Triage seed reports generated.")


def build_unified_baseline() -> List[Dict[str, Any]]:
    """
    Build a unified baseline timeline from seeded events.
    """
    print("📡 Building unified baseline timeline...")
    
    unified = []
    for ev in SEED_EVENTS:
        unified.append({
            "type": ev["type"],
            "status": ev["status"],
            "source": "PreSeed",
            "meta": {
                "timestamp": now(),
                "note": "Baseline initialization seed",
                "environment": "backend"
            }
        })
    
    # Save unified timeline
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    output_path = base_dir / "unified_timeline.json"
    
    try:
        with open(output_path, 'w') as f:
            json.dump(unified, f, indent=2)
        print(f"📡 Unified baseline timeline seeded with {len(unified)} events.")
        print(f"📄 Saved to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to save unified timeline: {e}")
    
    return unified


if __name__ == "__main__":
    print("🚀 Operation Genesis: Triage Pre-Seed Initialization")
    print("=" * 60)
    
    seed_reports()
    print()
    build_unified_baseline()
    
    print("=" * 60)
    print("✅ Pre-seed initialization complete!")
