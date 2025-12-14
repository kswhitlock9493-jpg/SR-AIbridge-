"""
Umbra Echo - Human-Informed Adaptive Learning Engine
Observes manual edits and Admiral actions, mirrors them into experience graph
"""

from __future__ import annotations
import logging
import os
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class UmbraEcho:
    """
    Umbra Echo - Human-Informed Adaptive Learning
    
    Bridges human command intuition with machine learning fabric
    Observes manual edits and automatically mirrors them into Umbra's Experience Graph
    """
    
    def __init__(self, memory=None, truth=None, genesis_bus=None):
        self.memory = memory
        self.truth = truth
        self.genesis_bus = genesis_bus
        self.enabled = os.getenv("UMBRA_ECHO_ENABLED", "true").lower() == "true"
        self.reflect_on_commit = os.getenv("UMBRA_REFLECT_ON_COMMIT", "true").lower() == "true"
        
        # Tracking
        self.echo_events = []
        self.watched_paths = [
            ".github/workflows/",
            ".env",
            "/config/",
            "bridge_backend/bridge_core/engines/"
        ]
        
        logger.info("🪶 Umbra Echo initialized - Human-guided learning active")
    
    async def capture_edit(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture and record a manual edit/change
        
        Args:
            change: Change data with file, diff, intent
            
        Returns:
            Echo entry
        """
        if not self.enabled:
            return {"error": "Echo disabled"}
        
        # Create echo entry
        entry = {
            "actor": change.get("actor", "Admiral"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file": change.get("file"),
            "intent": self._classify_intent(change),
            "diff": change.get("diff", ""),
            "commit_hash": change.get("commit_hash"),
            "metadata": {
                "lines_added": change.get("lines_added", 0),
                "lines_removed": change.get("lines_removed", 0),
                "affected_subsystems": self._detect_subsystems(change.get("file", ""))
            }
        }
        
        # Certify with Truth Engine
        if self.truth:
            cert_result = await self.truth.certify({
                "type": "umbra_echo_capture",
                "entry": entry
            })
            entry["certified"] = cert_result.get("certified", False)
            entry["signature"] = cert_result.get("signature")
        
        # Record to memory
        if self.memory:
            await self.memory.record("echo", entry)
        
        # Publish to Genesis Bus
        if self.genesis_bus:
            await self.genesis_bus.publish("umbra.echo.recorded", entry)
        
        self.echo_events.append(entry)
        
        logger.info(f"🪶 Umbra Echo recorded Admiral action on {entry['file']}")
        
        return entry
    
    def _classify_intent(self, change: Dict[str, Any]) -> str:
        """
        Classify the intent of a change
        
        Args:
            change: Change data
            
        Returns:
            Intent classification (fix, optimize, override, feature)
        """
        file = change.get("file", "").lower()
        diff = change.get("diff", "").lower()
        
        # Simple intent classification based on keywords
        if "fix" in diff or "bug" in diff or "error" in diff:
            return "intent:fix"
        elif "optim" in diff or "improve" in diff or "perf" in diff:
            return "intent:optimize"
        elif "override" in diff or "disable" in diff or "skip" in diff:
            return "intent:override"
        elif "feat" in diff or "add" in diff or "new" in diff:
            return "intent:feature"
        else:
            return "intent:maintenance"
    
    def _detect_subsystems(self, filepath: str) -> List[str]:
        """
        Detect affected subsystems from file path
        
        Args:
            filepath: Path to changed file
            
        Returns:
            List of affected subsystems
        """
        subsystems = []
        
        if ".github/workflows/" in filepath:
            subsystems.append("ci_cd")
        if ".env" in filepath:
            subsystems.append("configuration")
        if "/engines/" in filepath:
            subsystems.append("engines")
            # Detect specific engine
            if "/umbra/" in filepath:
                subsystems.append("umbra")
            elif "/truth/" in filepath:
                subsystems.append("truth")
            elif "/hxo/" in filepath:
                subsystems.append("hxo")
        if "/routes" in filepath:
            subsystems.append("api")
        if "test_" in filepath:
            subsystems.append("tests")
        
        return subsystems if subsystems else ["general"]
    
    async def observe_commit(self, commit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Observe a git commit and capture all changes
        
        Args:
            commit_data: Commit data with files, diffs, hash
            
        Returns:
            List of echo entries
        """
        if not self.enabled or not self.reflect_on_commit:
            return []
        
        entries = []
        
        for file_change in commit_data.get("files", []):
            change = {
                "actor": commit_data.get("author", "Admiral"),
                "file": file_change.get("path"),
                "diff": file_change.get("diff", ""),
                "commit_hash": commit_data.get("hash"),
                "lines_added": file_change.get("additions", 0),
                "lines_removed": file_change.get("deletions", 0)
            }
            
            # Only capture changes to watched paths
            if any(watched in change["file"] for watched in self.watched_paths):
                entry = await self.capture_edit(change)
                entries.append(entry)
        
        if entries:
            # Publish learning event
            if self.genesis_bus:
                await self.genesis_bus.publish("umbra.memory.learned", {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "commit": commit_data.get("hash"),
                    "changes_learned": len(entries),
                    "actor": commit_data.get("author", "Admiral")
                })
            
            logger.info(f"🪶 Umbra Echo observed commit {commit_data.get('hash', '')[:8]} - "
                       f"learned from {len(entries)} changes")
        
        return entries
    
    async def sync_to_hxo(self, echo_entry: Dict[str, Any]):
        """
        Signal HXO to regenerate schemas or adapt builds based on Echo data
        
        Args:
            echo_entry: Echo entry to sync
        """
        if not self.genesis_bus:
            return
        
        # Publish to HXO for schema regeneration
        await self.genesis_bus.publish("hxo.echo.sync", {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "echo_entry_id": echo_entry.get("timestamp"),
            "affected_subsystems": echo_entry.get("metadata", {}).get("affected_subsystems", []),
            "intent": echo_entry.get("intent"),
            "action": "regenerate_schema"
        })
        
        logger.info(f"🪶 Umbra Echo synced to HXO for subsystems: "
                   f"{echo_entry.get('metadata', {}).get('affected_subsystems', [])}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Echo metrics"""
        intents = {}
        for event in self.echo_events:
            intent = event.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1
        
        return {
            "enabled": self.enabled,
            "reflect_on_commit": self.reflect_on_commit,
            "echo_events": len(self.echo_events),
            "intents": intents,
            "watched_paths": len(self.watched_paths)
        }
