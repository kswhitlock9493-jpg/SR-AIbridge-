#!/usr/bin/env python3
"""
Operation Synchrony: Unified Health Timeline Collector
Collects and merges triage reports from CI/CD, Endpoint, and API systems.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Files to collect and merge
TRIAGE_FILES = [
    "endpoint_report.json",
    "api_triage_report.json",
    "ci_cd_report.json"
]

def build_unified_timeline() -> List[Dict[str, Any]]:
    """
    Build a unified timeline from all triage report files.
    Returns a sorted list of events by timestamp (newest first).
    """
    timeline = []
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    # Go up to the bridge_backend directory
    base_dir = script_dir.parent
    
    for filename in TRIAGE_FILES:
        file_path = base_dir / filename
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    timeline.append(data)
                    print(f"✅ Loaded {filename}")
            except Exception as e:
                print(f"⚠️ Failed to parse {filename}: {e}")
        else:
            print(f"ℹ️ File not found: {filename}")
    
    # Sort by timestamp (newest first)
    def get_timestamp(event):
        return event.get("meta", {}).get("timestamp", "")
    
    sorted_timeline = sorted(timeline, key=get_timestamp, reverse=True)
    
    # Save unified timeline
    output_path = base_dir / "unified_timeline.json"
    try:
        with open(output_path, 'w') as f:
            json.dump(sorted_timeline, f, indent=2)
        print(f"\n🧭 Unified Health Timeline built with {len(sorted_timeline)} events.")
        print(f"📄 Saved to {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to save unified timeline: {e}")
    
    return sorted_timeline

if __name__ == "__main__":
    timeline = build_unified_timeline()
    
    # Print summary
    if timeline:
        print("\n📊 Timeline Summary:")
        for event in timeline:
            event_type = event.get("type", "UNKNOWN")
            status = event.get("status", "UNKNOWN")
            timestamp = event.get("meta", {}).get("timestamp", "N/A")
            print(f"  {event_type}: {status} @ {timestamp}")
    else:
        print("\n⚠️ No triage events found.")
