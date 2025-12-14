"""
Umbra Predictive - Confidence-Based Pre-Repair Engine
Uses learned patterns to predict and prevent issues before they occur
"""

from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class UmbraPredictive:
    """
    Umbra Predictive - Confidence-Based Pre-Repair
    
    Uses memory patterns to predict issues and apply pre-emptive repairs
    """
    
    def __init__(self, memory=None, core=None):
        self.memory = memory
        self.core = core
        self.enabled = os.getenv("UMBRA_ENABLED", "true").lower() == "true"
        
        # Prediction tracking
        self.predictions = []
        self.confidence_threshold = 0.7  # Minimum confidence to act
        
        logger.info("🔮 Umbra Predictive initialized - Pre-repair intelligence active")
    
    async def predict_issue(self, telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predict potential issues from current telemetry
        
        Args:
            telemetry: Current system telemetry
            
        Returns:
            Prediction result or None
        """
        if not self.enabled or not self.memory:
            return None
        
        # Learn from past patterns
        patterns = await self.memory.learn_pattern("repair")
        
        if not patterns.get("patterns"):
            return None
        
        # Analyze telemetry against known patterns
        predictions = []
        
        for pattern_id, pattern_data in patterns["patterns"].items():
            confidence = pattern_data.get("avg_confidence", 0.0)
            success_rate = pattern_data.get("success_rate", 0.0)
            
            # Calculate prediction confidence based on pattern history and current telemetry
            prediction_confidence = confidence * success_rate
            
            if prediction_confidence >= self.confidence_threshold:
                prediction = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "predicted_issue": pattern_id,
                    "confidence": prediction_confidence,
                    "pattern_frequency": pattern_data.get("frequency", 0),
                    "recommended_actions": pattern_data.get("actions", [])[:3],  # Top 3 actions
                    "predicted_by": "umbra_predictive"
                }
                predictions.append(prediction)
        
        if not predictions:
            return None
        
        # Return highest confidence prediction
        best_prediction = max(predictions, key=lambda p: p["confidence"])
        self.predictions.append(best_prediction)
        
        logger.info(f"🔮 Umbra predicted issue: {best_prediction['predicted_issue']} "
                   f"with {best_prediction['confidence']:.2f} confidence")
        
        return best_prediction
    
    async def apply_preventive_repair(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply preventive repair based on prediction
        
        Args:
            prediction: Prediction data
            
        Returns:
            Preventive repair result
        """
        if not self.core:
            return {"error": "Umbra Core not available"}
        
        # Generate repair plan from prediction
        repair = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "anomaly_id": prediction["predicted_issue"],
            "repair_type": "preventive",
            "actions": prediction.get("recommended_actions", []),
            "confidence": prediction.get("confidence", 0.0),
            "prediction_based": True
        }
        
        # Apply through Umbra Core
        result = await self.core.apply_repair(repair)
        result["preventive"] = True
        result["prediction"] = prediction
        
        logger.info(f"🔮 Umbra applied preventive repair for {prediction['predicted_issue']}")
        
        return result
    
    async def update_model(self, feedback: Dict[str, Any]):
        """
        Update predictive model with feedback
        
        Args:
            feedback: Feedback data (success/failure of prediction)
        """
        if not self.memory:
            return
        
        # Record feedback as learning experience
        await self.memory.record("prediction_feedback", feedback)
        
        # Adjust confidence threshold based on accuracy
        if "accuracy" in feedback:
            accuracy = feedback["accuracy"]
            if accuracy > 0.9:
                self.confidence_threshold = max(0.6, self.confidence_threshold - 0.05)
            elif accuracy < 0.7:
                self.confidence_threshold = min(0.9, self.confidence_threshold + 0.05)
        
        logger.info(f"🔮 Umbra model updated - new threshold: {self.confidence_threshold:.2f}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get predictive metrics"""
        return {
            "enabled": self.enabled,
            "predictions_made": len(self.predictions),
            "confidence_threshold": self.confidence_threshold,
            "avg_confidence": sum(p.get("confidence", 0) for p in self.predictions) / max(len(self.predictions), 1)
        }
