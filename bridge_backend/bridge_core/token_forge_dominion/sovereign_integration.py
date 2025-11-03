"""
Sovereign Integration - Token Forge Dominion v1.9.7s-SOVEREIGN

Bridge-native integration with Dominion resonance policies.
Implements resonance-aware security and policy enforcement.
"""
import os
import json
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path


class SovereignIntegration:
    """
    Sovereign integration layer for bridge resonance and policy enforcement.
    Adapts security policies based on bridge health and resonance metrics.
    """
    
    # TTL ranges based on resonance scores
    TTL_RANGES = {
        "critical": (60, 120),      # 1-2 minutes for critical (resonance < 30)
        "degraded": (120, 300),     # 2-5 minutes for degraded (30-60)
        "normal": (300, 1800),      # 5-30 minutes for normal (60-80)
        "optimal": (1800, 3600)     # 30-60 minutes for optimal (80+)
    }
    
    # Resonance score thresholds
    RESONANCE_THRESHOLDS = {
        "critical": 30,
        "degraded": 60,
        "normal": 80,
        "optimal": 100
    }
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize sovereign integration.
        
        Args:
            state_file: Path to forge state file
        """
        self.state_file = state_file or ".alik/forge_state.json"
        self.policies: Dict[str, Any] = {}
        self.load_policies()
    
    def load_policies(self) -> None:
        """Load sovereign policies from configuration."""
        # Default policies
        self.policies = {
            "min_ttl_seconds": 60,
            "max_ttl_seconds": 3600,
            "require_resonance_check": True,
            "enable_auto_rotation": True,
            "audit_all_issuance": True,
            "enforce_zero_trust": True
        }
        
        # Override from environment if specified
        policy_override = os.getenv("FORGE_DOMINION_POLICIES")
        if policy_override:
            try:
                overrides = json.loads(policy_override)
                self.policies.update(overrides)
            except json.JSONDecodeError:
                pass
    
    def get_resonance_score(self) -> Tuple[float, str]:
        """
        Get current bridge resonance score.
        
        Returns:
            tuple: (resonance_score, health_status)
        """
        # Try to get resonance from bridge state
        try:
            # Check for bridge health indicators
            state_path = Path(self.state_file)
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    resonance = state.get("resonance_score", 75.0)
                    status = state.get("health_status", "normal")
                    return resonance, status
        except Exception:
            pass
        
        # Default to normal if no state available
        return 75.0, "normal"
    
    def classify_resonance(self, resonance_score: float) -> str:
        """
        Classify resonance score into health category.
        
        Args:
            resonance_score: Resonance score (0-100)
            
        Returns:
            str: Health category (critical, degraded, normal, optimal)
        """
        if resonance_score < self.RESONANCE_THRESHOLDS["critical"]:
            return "critical"
        elif resonance_score < self.RESONANCE_THRESHOLDS["degraded"]:
            return "degraded"
        elif resonance_score < self.RESONANCE_THRESHOLDS["normal"]:
            return "normal"
        else:
            return "optimal"
    
    def get_resonance_aware_ttl(
        self,
        base_ttl: int,
        provider: str,
        environment: str
    ) -> int:
        """
        Calculate resonance-aware TTL for token.
        
        Args:
            base_ttl: Base TTL in seconds
            provider: Provider name
            environment: Environment name
            
        Returns:
            int: Adjusted TTL in seconds
        """
        resonance_score, health_status = self.get_resonance_score()
        category = self.classify_resonance(resonance_score)
        
        # Get TTL range for this resonance category
        min_ttl, max_ttl = self.TTL_RANGES[category]
        
        # Clamp base_ttl to the appropriate range
        adjusted_ttl = max(min_ttl, min(base_ttl, max_ttl))
        
        # Apply environment-specific adjustments
        if environment == "production":
            # Production gets shorter TTLs for security
            adjusted_ttl = int(adjusted_ttl * 0.8)
        elif environment == "development":
            # Development can have longer TTLs for convenience
            adjusted_ttl = int(adjusted_ttl * 1.2)
        
        # Apply policy constraints
        adjusted_ttl = max(
            self.policies["min_ttl_seconds"],
            min(adjusted_ttl, self.policies["max_ttl_seconds"])
        )
        
        return adjusted_ttl
    
    def should_trigger_rotation(self) -> Tuple[bool, str]:
        """
        Determine if root key rotation should be triggered.
        
        Returns:
            tuple: (should_rotate, reason)
        """
        if not self.policies["enable_auto_rotation"]:
            return False, "Auto-rotation disabled"
        
        try:
            state_path = Path(self.state_file)
            if not state_path.exists():
                return False, "No state file available"
            
            with open(state_path, 'r') as f:
                state = json.load(f)
            
            # Check last rotation time
            last_rotation = state.get("last_key_rotation")
            if not last_rotation:
                return True, "No previous rotation recorded"
            
            last_rotation_dt = datetime.fromisoformat(last_rotation.rstrip('Z'))
            rotation_age = datetime.utcnow() - last_rotation_dt
            
            # Rotate every 30 days
            if rotation_age > timedelta(days=30):
                return True, f"Last rotation {rotation_age.days} days ago"
            
            # Check for security events
            security_events = state.get("security_events", 0)
            if security_events > 10:
                return True, f"High security event count: {security_events}"
            
            return False, "Rotation not needed"
            
        except Exception as e:
            return False, f"Error checking rotation: {str(e)}"
    
    def enforce_policy_guard(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Enforce sovereign policy guard for action.
        
        Args:
            action: Action to validate (e.g., 'token_issuance', 'key_rotation')
            context: Action context
            
        Returns:
            tuple: (is_allowed, reason)
        """
        # Check zero-trust enforcement
        if self.policies["enforce_zero_trust"]:
            if not context.get("validated"):
                return False, "Zero-trust validation required"
        
        # Check resonance requirements
        if self.policies["require_resonance_check"]:
            resonance_score, _ = self.get_resonance_score()
            if resonance_score < self.RESONANCE_THRESHOLDS["critical"]:
                if action == "token_issuance" and context.get("environment") == "production":
                    return False, f"Resonance too low for production: {resonance_score}"
        
        # Action-specific guards
        if action == "key_rotation":
            if not context.get("authorized"):
                return False, "Key rotation requires authorization"
        
        return True, "Policy guard passed"
    
    def record_audit_event(
        self,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Record audit event to state file.
        
        Args:
            event_type: Type of event
            details: Event details
        """
        if not self.policies["audit_all_issuance"]:
            return
        
        try:
            state_path = Path(self.state_file)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing state
            state = {}
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state = json.load(f)
            
            # Add audit event
            if "audit_trail" not in state:
                state["audit_trail"] = []
            
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event_type": event_type,
                "details": details
            }
            
            state["audit_trail"].append(audit_entry)
            
            # Keep only last 1000 events
            if len(state["audit_trail"]) > 1000:
                state["audit_trail"] = state["audit_trail"][-1000:]
            
            # Update state file
            with open(state_path, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            # Don't fail on audit errors, just log
            pass
    
    def get_sovereign_status(self) -> Dict[str, Any]:
        """
        Get current sovereign integration status.
        
        Returns:
            dict: Status report
        """
        resonance_score, health_status = self.get_resonance_score()
        category = self.classify_resonance(resonance_score)
        should_rotate, rotation_reason = self.should_trigger_rotation()
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.9.7s-SOVEREIGN",
            "resonance": {
                "score": resonance_score,
                "category": category,
                "health_status": health_status
            },
            "policies": self.policies,
            "rotation": {
                "should_rotate": should_rotate,
                "reason": rotation_reason
            },
            "ttl_range": self.TTL_RANGES[category]
        }
