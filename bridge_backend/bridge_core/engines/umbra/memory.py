"""
Umbra Memory - Experience Graph & Recall Engine
Stores and recalls Umbra experiences, integrates with ChronicleLoom
"""

from __future__ import annotations
import logging
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

MEMORY_FILE = Path("vault/umbra/umbra_memory.json")
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)


class UmbraMemory:
    """
    Umbra Memory - Experience Graph & Recall
    
    Stores repair sequences, learns from patterns, and provides recall capabilities
    """
    
    def __init__(self, truth=None, chronicle_loom=None):
        self.truth = truth
        self.chronicle_loom = chronicle_loom
        self.enabled = os.getenv("UMBRA_MEMORY_ENABLED", "true").lower() == "true"
        
        # Load existing memory
        self.experiences: List[Dict[str, Any]] = []
        self._load_memory()
        
        logger.info("🧠 Umbra Memory initialized - Experience graph active")
    
    def _load_memory(self):
        """Load memory from persistent storage"""
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    self.experiences = data.get("experiences", [])
                    logger.info(f"🧠 Loaded {len(self.experiences)} experiences from memory")
            except Exception as e:
                logger.error(f"🧠 Failed to load memory: {e}")
                self.experiences = []
    
    def _save_memory(self):
        """Save memory to persistent storage"""
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump({
                    "version": "1.9.7d",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "experiences": self.experiences
                }, f, indent=2)
            logger.debug(f"🧠 Saved {len(self.experiences)} experiences to memory")
        except Exception as e:
            logger.error(f"🧠 Failed to save memory: {e}")
    
    async def record(self, category: str, data: Dict[str, Any], result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record an experience to memory
        
        Args:
            category: Experience category (e.g., 'repair', 'anomaly', 'echo')
            data: Experience data
            result: Optional result/outcome
            
        Returns:
            Memory entry
        """
        if not self.enabled:
            return {"error": "Memory disabled"}
        
        entry = {
            "id": f"exp_{len(self.experiences)}_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": category,
            "data": data,
            "result": result,
            "certified": False
        }
        
        # Certify with Truth Engine
        if self.truth:
            cert_result = await self.truth.certify({
                "type": f"umbra_memory_{category}",
                "entry": entry
            })
            entry["certified"] = cert_result.get("certified", False)
            entry["signature"] = cert_result.get("signature")
        
        # Store in ChronicleLoom if available
        if self.chronicle_loom:
            try:
                chronicle = self.chronicle_loom.record_chronicle(
                    title=f"Umbra {category.title()} Memory",
                    content=json.dumps(entry, indent=2),
                    category="umbra_memory",
                    tags=["umbra", category, "memory"]
                )
                entry["chronicle_id"] = chronicle.get("chronicle_id")
            except Exception as e:
                logger.warning(f"🧠 Failed to record to ChronicleLoom: {e}")
        
        self.experiences.append(entry)
        self._save_memory()
        
        logger.info(f"🧠 Recorded {category} experience - certified: {entry['certified']}")
        
        return entry
    
    async def recall(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recall experiences from memory
        
        Args:
            category: Optional category filter
            limit: Maximum number of experiences to return
            
        Returns:
            List of experiences
        """
        if not self.enabled:
            return []
        
        experiences = self.experiences
        
        if category:
            experiences = [e for e in experiences if e.get("category") == category]
        
        # Return most recent first
        experiences = sorted(experiences, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return experiences[:limit]
    
    async def learn_pattern(self, pattern_type: str = "repair") -> Dict[str, Any]:
        """
        Learn patterns from stored experiences
        
        Args:
            pattern_type: Type of pattern to learn
            
        Returns:
            Learned patterns
        """
        if not self.enabled:
            return {"error": "Memory disabled"}
        
        # Filter experiences by type
        relevant = [e for e in self.experiences if e.get("category") == pattern_type]
        
        if not relevant:
            return {
                "pattern_type": pattern_type,
                "patterns": [],
                "message": "No experiences found for learning"
            }
        
        # Simple pattern analysis
        patterns = {}
        for exp in relevant:
            # Extract pattern keys
            if "data" in exp and "anomaly_id" in exp["data"]:
                anomaly_id = exp["data"]["anomaly_id"]
                if anomaly_id not in patterns:
                    patterns[anomaly_id] = {
                        "frequency": 0,
                        "success_rate": 0,
                        "avg_confidence": 0.0,
                        "actions": []
                    }
                
                patterns[anomaly_id]["frequency"] += 1
                
                if exp.get("result", {}).get("success"):
                    patterns[anomaly_id]["success_rate"] += 1
                
                if "confidence" in exp["data"]:
                    patterns[anomaly_id]["avg_confidence"] += exp["data"]["confidence"]
                
                if "actions" in exp["data"]:
                    patterns[anomaly_id]["actions"].extend(exp["data"]["actions"])
        
        # Calculate averages
        for pattern_id, pattern_data in patterns.items():
            if pattern_data["frequency"] > 0:
                pattern_data["success_rate"] = pattern_data["success_rate"] / pattern_data["frequency"]
                pattern_data["avg_confidence"] = pattern_data["avg_confidence"] / pattern_data["frequency"]
        
        logger.info(f"🧠 Learned {len(patterns)} patterns from {len(relevant)} experiences")
        
        return {
            "pattern_type": pattern_type,
            "total_experiences": len(relevant),
            "patterns": patterns,
            "learned_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get memory metrics"""
        categories = {}
        for exp in self.experiences:
            cat = exp.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "enabled": self.enabled,
            "total_experiences": len(self.experiences),
            "categories": categories,
            "certified_count": len([e for e in self.experiences if e.get("certified", False)])
        }
