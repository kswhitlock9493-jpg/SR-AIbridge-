"""
Umbra Core - Pipeline Self-Healing Engine
Detects anomalies and telemetry changes, autonomously applies repairs
"""

from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

VAULT_DIR = Path("vault/umbra")
VAULT_DIR.mkdir(parents=True, exist_ok=True)


class UmbraCore:
    """
    Umbra Core - Pipeline Self-Healing Intelligence
    
    Observes anomalies & telemetry changes and generates autonomous repairs
    """
    
    def __init__(self, memory=None, truth=None, genesis_bus=None):
        self.memory = memory
        self.truth = truth
        self.genesis_bus = genesis_bus
        self.enabled = os.getenv("UMBRA_ENABLED", "true").lower() == "true"
        
        # Tracking
        self.repairs_applied = []
        self.anomalies_detected = []
        
        logger.info("🌑 Umbra Core initialized - Pipeline self-healing active")
    
    async def detect_anomaly(self, telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect anomalies from telemetry data
        
        Args:
            telemetry: System telemetry data
            
        Returns:
            Anomaly detection result or None if no anomaly
        """
        if not self.enabled:
            return None
        
        anomaly = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "telemetry_anomaly",
            "severity": "info",
            "telemetry": telemetry,
            "detected_by": "umbra_core"
        }
        
        # Check for common anomalies
        if "error_rate" in telemetry and telemetry["error_rate"] > 0.1:
            anomaly["severity"] = "high"
            anomaly["type"] = "high_error_rate"
            anomaly["message"] = f"Error rate {telemetry['error_rate']*100:.1f}% exceeds threshold"
            
        elif "response_time" in telemetry and telemetry["response_time"] > 5000:
            anomaly["severity"] = "medium"
            anomaly["type"] = "high_latency"
            anomaly["message"] = f"Response time {telemetry['response_time']}ms exceeds threshold"
        
        elif "memory_usage" in telemetry and telemetry["memory_usage"] > 0.9:
            anomaly["severity"] = "high"
            anomaly["type"] = "high_memory"
            anomaly["message"] = f"Memory usage {telemetry['memory_usage']*100:.1f}% critical"
        
        else:
            return None  # No anomaly detected
        
        self.anomalies_detected.append(anomaly)
        logger.warning(f"🌑 Umbra detected anomaly: {anomaly['message']}")
        
        # Publish to Genesis Bus
        if self.genesis_bus:
            await self.genesis_bus.publish("umbra.anomaly.detected", anomaly)
        
        return anomaly
    
    async def generate_repair(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate repair action for detected anomaly
        
        Args:
            anomaly: Anomaly data from detection
            
        Returns:
            Repair plan
        """
        repair = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "anomaly_id": anomaly.get("type"),
            "repair_type": "auto",
            "actions": [],
            "confidence": 0.0
        }
        
        # Generate repair actions based on anomaly type
        if anomaly["type"] == "high_error_rate":
            repair["actions"].append({
                "action": "restart_service",
                "target": "backend",
                "reason": "High error rate detected"
            })
            repair["confidence"] = 0.85
            
        elif anomaly["type"] == "high_latency":
            repair["actions"].append({
                "action": "scale_up",
                "target": "workers",
                "reason": "High response times detected"
            })
            repair["confidence"] = 0.75
            
        elif anomaly["type"] == "high_memory":
            repair["actions"].append({
                "action": "clear_cache",
                "target": "memory",
                "reason": "Critical memory usage"
            })
            repair["confidence"] = 0.90
        
        logger.info(f"🌑 Umbra generated repair plan: {len(repair['actions'])} actions, confidence {repair['confidence']:.2f}")
        
        return repair
    
    async def apply_repair(self, repair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply repair actions (simulated for safety)
        
        Args:
            repair: Repair plan to execute
            
        Returns:
            Repair result
        """
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repair_id": repair.get("anomaly_id"),
            "success": True,
            "actions_applied": [],
            "certified": False
        }
        
        # In a real implementation, this would execute actual repairs
        # For now, we simulate and log
        for action in repair["actions"]:
            logger.info(f"🌑 Umbra applying repair: {action['action']} on {action['target']}")
            result["actions_applied"].append({
                "action": action["action"],
                "target": action["target"],
                "applied": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Record to memory
        if self.memory:
            await self.memory.record("repair", repair, result)
        
        # Certify with Truth Engine
        if self.truth:
            certified = await self.truth.certify({
                "type": "umbra_repair",
                "repair": repair,
                "result": result
            })
            result["certified"] = certified.get("certified", False)
            result["signature"] = certified.get("signature")
        
        # Publish to Genesis Bus
        if self.genesis_bus:
            await self.genesis_bus.publish("umbra.pipeline.repaired", result)
        
        self.repairs_applied.append(result)
        logger.info(f"🌑 Umbra repair applied successfully - certified: {result['certified']}")
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Umbra Core metrics"""
        return {
            "enabled": self.enabled,
            "anomalies_detected": len(self.anomalies_detected),
            "repairs_applied": len(self.repairs_applied),
            "success_rate": len([r for r in self.repairs_applied if r["success"]]) / max(len(self.repairs_applied), 1)
        }
