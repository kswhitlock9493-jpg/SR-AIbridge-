"""
Guardians Gate - Safety checks for Genesis events
Blocks recursion, destructive operations, and cross-namespace violations
"""
import re
import logging
from typing import Tuple, Optional, Dict, Any, Set
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import os

logger = logging.getLogger(__name__)

# Configuration
GUARDIANS_ENFORCE_STRICT = os.getenv("GUARDIANS_ENFORCE_STRICT", "true").lower() == "true"
GUARDIANS_RATE_LIMIT = int(os.getenv("GUARDIANS_RATE_LIMIT", "100"))  # events per topic per minute
GUARDIANS_MAX_DEPTH = int(os.getenv("GUARDIANS_MAX_DEPTH", "10"))  # max recursion depth


class GuardiansGate:
    """
    Safety gate for Genesis events
    
    Prevents:
    - Recursive event loops
    - Destructive operations without approval
    - Cross-namespace violations
    - Rate limit violations
    - Suspicious patterns
    """
    
    def __init__(self):
        self._enforce_strict = GUARDIANS_ENFORCE_STRICT
        self._rate_limit = GUARDIANS_RATE_LIMIT
        self._max_depth = GUARDIANS_MAX_DEPTH
        
        # Rate limiting state
        self._event_counts: Dict[str, list] = defaultdict(list)  # topic -> [timestamps]
        
        # Recursion tracking
        self._event_chain: list = []  # Stack of (event_id, topic)
        
        # Blocked patterns (regex)
        self._blocked_patterns = [
            r".*\.delete\.all$",  # Bulk deletes
            r".*\.destroy\..*",   # Destructive operations
            r".*\.purge\..*",     # Purge operations
            r".*\.wipe\..*",      # Wipe operations
        ]
        
        # Approved bypass keys (for emergency operations)
        self._bypass_keys: Set[str] = set()
        
        logger.info(f"🛡️ Guardians Gate initialized (strict={self._enforce_strict})")
    
    def add_bypass_key(self, key: str):
        """Add emergency bypass key for destructive operations"""
        self._bypass_keys.add(key)
        logger.warning(f"⚠️ Bypass key added: {key[:8]}...")
    
    def allow(self, event: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check if event is allowed
        
        Args:
            event: Event dictionary with id, topic, payload, etc.
        
        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
            If blocked, reason explains why
        """
        event_id = event.get("id", "unknown")
        topic = event.get("topic", "unknown")
        payload = event.get("payload", {})
        
        # Check for bypass key
        if payload.get("_bypass_key") in self._bypass_keys:
            logger.warning(f"⚠️ Event {event_id} bypassed guardians with valid key")
            return True, None
        
        # 1. Check for destructive patterns
        if self._enforce_strict:
            for pattern in self._blocked_patterns:
                if re.match(pattern, topic):
                    reason = f"Blocked destructive pattern: {pattern}"
                    logger.warning(f"🛡️ {reason} (event {event_id})")
                    return False, reason
        
        # 2. Check for recursion
        recursion_depth = self._check_recursion(event_id, topic)
        if recursion_depth > self._max_depth:
            reason = f"Recursion depth {recursion_depth} exceeds limit {self._max_depth}"
            logger.warning(f"🛡️ {reason} (event {event_id})")
            return False, reason
        
        # 3. Check rate limits
        if self._enforce_strict:
            if not self._check_rate_limit(topic):
                reason = f"Rate limit exceeded for topic {topic}"
                logger.warning(f"🛡️ {reason} (event {event_id})")
                return False, reason
        
        # 4. Check for suspicious payload patterns
        if self._check_suspicious_payload(payload):
            reason = "Suspicious payload detected"
            logger.warning(f"🛡️ {reason} (event {event_id})")
            return False, reason
        
        # 5. Check cross-namespace violations
        if self._enforce_strict:
            violation = self._check_namespace_violation(topic, payload)
            if violation:
                logger.warning(f"🛡️ Namespace violation: {violation} (event {event_id})")
                return False, violation
        
        # Event is allowed
        return True, None
    
    def _check_recursion(self, event_id: str, topic: str) -> int:
        """
        Check recursion depth by tracking event chain
        
        Returns depth (0 = no recursion)
        """
        # Count how many times this topic appears in the chain
        depth = sum(1 for _, t in self._event_chain if t == topic)
        
        # Add to chain
        self._event_chain.append((event_id, topic))
        
        # Keep chain bounded (last 100 events)
        if len(self._event_chain) > 100:
            self._event_chain.pop(0)
        
        return depth
    
    def _check_rate_limit(self, topic: str) -> bool:
        """
        Check if topic exceeds rate limit
        
        Returns True if within limit, False if exceeded
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        
        # Clean old timestamps
        self._event_counts[topic] = [
            ts for ts in self._event_counts[topic]
            if ts > cutoff
        ]
        
        # Check limit
        if len(self._event_counts[topic]) >= self._rate_limit:
            return False
        
        # Record new event
        self._event_counts[topic].append(now)
        return True
    
    def _check_suspicious_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Check for suspicious patterns in payload
        
        Returns True if suspicious, False otherwise
        """
        # Check for SQL injection patterns
        payload_str = str(payload).lower()
        
        sql_patterns = [
            "drop table",
            "delete from",
            "truncate",
            "; drop",
            "' or '1'='1",
            "exec(",
            "execute(",
        ]
        
        for pattern in sql_patterns:
            if pattern in payload_str:
                return True
        
        # Check for script injection
        script_patterns = [
            "<script",
            "javascript:",
            "onerror=",
            "onclick=",
        ]
        
        for pattern in script_patterns:
            if pattern in payload_str:
                return True
        
        return False
    
    def _check_namespace_violation(self, topic: str, payload: Dict[str, Any]) -> Optional[str]:
        """
        Check for cross-namespace violations
        
        Returns violation description if found, None otherwise
        """
        # Parse topic: namespace.component.domain.verb
        parts = topic.split(".")
        if len(parts) < 2:
            return None
        
        namespace = parts[0]  # e.g. "engine", "system", "runtime"
        
        # Check if payload tries to affect different namespace
        target_namespace = payload.get("target_namespace")
        if target_namespace and target_namespace != namespace:
            return f"Cross-namespace violation: {namespace} -> {target_namespace}"
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get guardian statistics"""
        return {
            "enforce_strict": self._enforce_strict,
            "rate_limit": self._rate_limit,
            "max_depth": self._max_depth,
            "chain_length": len(self._event_chain),
            "tracked_topics": len(self._event_counts),
            "bypass_keys": len(self._bypass_keys),
        }


# Global guardian gate instance
guardians_gate = GuardiansGate()
