#!/usr/bin/env python3
"""
Autonomyctl - CLI for Autonomy Decision Layer

Usage:
    autonomyctl incident --kind deploy.netlify.preview_failed
    autonomyctl status
    autonomyctl circuit --open
    autonomyctl circuit --close
"""

import sys
import os
import argparse
import asyncio
import json
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.autonomy.governor import AutonomyGovernor
from engines.autonomy.models import Incident, Decision


async def submit_incident(kind: str, source: str = "cli", details: dict = None):
    """Submit an incident to the autonomy engine"""
    incident = Incident(
        kind=kind,
        source=source,
        details=details or {}
    )
    
    print(f"📋 Submitting incident: {kind}")
    
    gov = AutonomyGovernor()
    decision = await gov.decide(incident)
    
    print(f"🧠 Decision: {decision.action} ({decision.reason})")
    
    if decision.action != "NOOP":
        result = await gov.execute(decision)
        print(f"✅ Result: {result.get('status')}")
        if result.get('certified'):
            print(f"🔐 Certified: {result['certified'].get('ok')}")
    else:
        print(f"⏸️  No action taken: {decision.reason}")


async def get_status():
    """Get autonomy engine status"""
    enabled = os.getenv("AUTONOMY_ENABLED", "true").lower() == "true"
    
    status = {
        "enabled": enabled,
        "config": {
            "max_actions_per_hour": int(os.getenv("AUTONOMY_MAX_ACTIONS_PER_HOUR", "6")),
            "cooldown_minutes": int(os.getenv("AUTONOMY_COOLDOWN_MINUTES", "5")),
            "fail_streak_trip": int(os.getenv("AUTONOMY_FAIL_STREAK_TRIP", "3"))
        }
    }
    
    print("🤖 Autonomy Engine Status")
    print(json.dumps(status, indent=2))


async def control_circuit(action: str):
    """Control circuit breaker"""
    if action not in ["open", "close"]:
        print(f"❌ Invalid action: {action} (must be 'open' or 'close')")
        sys.exit(1)
    
    print(f"🔌 Circuit breaker {action}d")
    print("⚠️  Note: Persistent circuit state not yet implemented")


def main():
    parser = argparse.ArgumentParser(description="Autonomy Decision Layer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # incident command
    incident_parser = subparsers.add_parser("incident", help="Submit an incident")
    incident_parser.add_argument("--kind", required=True, help="Incident kind (e.g., deploy.netlify.preview_failed)")
    incident_parser.add_argument("--source", default="cli", help="Incident source")
    incident_parser.add_argument("--details", help="Incident details (JSON)")
    
    # status command
    subparsers.add_parser("status", help="Get autonomy engine status")
    
    # circuit command
    circuit_parser = subparsers.add_parser("circuit", help="Control circuit breaker")
    circuit_group = circuit_parser.add_mutually_exclusive_group(required=True)
    circuit_group.add_argument("--open", action="store_true", help="Open circuit breaker")
    circuit_group.add_argument("--close", action="store_true", help="Close circuit breaker")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "incident":
        details = json.loads(args.details) if args.details else None
        asyncio.run(submit_incident(args.kind, args.source, details))
    
    elif args.command == "status":
        asyncio.run(get_status())
    
    elif args.command == "circuit":
        action = "open" if args.open else "close"
        asyncio.run(control_circuit(action))


if __name__ == "__main__":
    main()
