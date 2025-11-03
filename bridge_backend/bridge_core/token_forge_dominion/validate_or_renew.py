"""
Token Lifecycle Manager - Token Forge Dominion v1.9.7s-SOVEREIGN

Validates tokens and auto-renews those nearing expiration.
Implements continuous token refresh for zero-downtime operation.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple, List
from pathlib import Path

from .quantum_authority import QuantumAuthority
from .sovereign_integration import SovereignIntegration


class TokenLifecycleManager:
    """
    Manages token lifecycle including validation and renewal.
    """
    
    # Renew tokens when they have less than this many seconds left
    RENEWAL_THRESHOLD_SECONDS = 300  # 5 minutes
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize lifecycle manager.
        
        Args:
            state_file: Path to token state file
        """
        self.state_file = state_file or ".alik/forge_tokens.json"
        self.authority = QuantumAuthority()
        self.sovereign = SovereignIntegration()
        self.tokens: Dict[str, Any] = {}
        self.load_state()
    
    def load_state(self) -> None:
        """Load token state from file."""
        state_path = Path(self.state_file)
        
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    self.tokens = json.load(f)
            except Exception:
                self.tokens = {}
        else:
            self.tokens = {}
    
    def save_state(self) -> None:
        """Save token state to file."""
        state_path = Path(self.state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(state_path, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception:
            pass
    
    def validate_token(
        self,
        provider: str,
        token_envelope: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate a token for a provider.
        
        Args:
            provider: Provider name
            token_envelope: Token envelope (if None, loads from state)
            
        Returns:
            tuple: (is_valid, payload or None)
        """
        # Get token envelope
        if token_envelope is None:
            if provider not in self.tokens:
                return False, None
            token_envelope = self.tokens[provider]
        
        # Verify token signature and expiration
        is_valid, payload = self.authority.verify_token(token_envelope)
        
        return is_valid, payload
    
    def needs_renewal(self, provider: str) -> Tuple[bool, str]:
        """
        Check if token needs renewal.
        
        Args:
            provider: Provider name
            
        Returns:
            tuple: (needs_renewal, reason)
        """
        if provider not in self.tokens:
            return True, "No token exists"
        
        is_valid, payload = self.validate_token(provider)
        
        if not is_valid:
            return True, "Token invalid or expired"
        
        # Check time to expiration
        expires_at = datetime.fromisoformat(payload["expires_at"].rstrip('Z'))
        time_remaining = (expires_at - datetime.utcnow()).total_seconds()
        
        if time_remaining < self.RENEWAL_THRESHOLD_SECONDS:
            return True, f"Expires in {int(time_remaining)}s (threshold: {self.RENEWAL_THRESHOLD_SECONDS}s)"
        
        return False, f"Valid for {int(time_remaining)}s"
    
    def renew_token(
        self,
        provider: str,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Renew token for a provider.
        
        Args:
            provider: Provider name
            ttl_seconds: Time-to-live (if None, uses resonance-aware default)
            metadata: Optional metadata
            
        Returns:
            tuple: (success, token_envelope or error)
        """
        try:
            # Get resonance-aware TTL if not specified
            if ttl_seconds is None:
                environment = os.getenv("FORGE_ENVIRONMENT", "production")
                ttl_seconds = self.sovereign.get_resonance_aware_ttl(
                    base_ttl=3600,  # 1 hour base
                    provider=provider,
                    environment=environment
                )
            
            # Mint new token
            token_envelope = self.authority.mint_quantum_token(
                provider=provider,
                ttl_seconds=ttl_seconds,
                metadata=metadata
            )
            
            # Save to state
            self.tokens[provider] = token_envelope
            self.save_state()
            
            # Record audit event
            self.sovereign.record_audit_event(
                "token_renewal",
                {
                    "provider": provider,
                    "ttl_seconds": ttl_seconds,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )
            
            return True, token_envelope
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def validate_or_renew(self, provider: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate token and renew if needed.
        
        Args:
            provider: Provider name
            
        Returns:
            tuple: (success, result with token or error)
        """
        needs_renewal, reason = self.needs_renewal(provider)
        
        if not needs_renewal:
            # Token is still valid
            is_valid, payload = self.validate_token(provider)
            return True, {
                "action": "validated",
                "provider": provider,
                "reason": reason,
                "token": self.tokens[provider],
                "payload": payload
            }
        
        # Renew token
        success, token_envelope = self.renew_token(provider)
        
        if success:
            return True, {
                "action": "renewed",
                "provider": provider,
                "reason": reason,
                "token": token_envelope
            }
        else:
            return False, {
                "action": "failed",
                "provider": provider,
                "error": token_envelope.get("error", "Unknown error")
            }
    
    def validate_or_renew_all(
        self,
        providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate or renew tokens for all providers.
        
        Args:
            providers: List of provider names (if None, uses default list)
            
        Returns:
            dict: Results for all providers
        """
        if providers is None:
            providers = ['github', 'netlify', 'render']
        
        results = {}
        
        for provider in providers:
            success, result = self.validate_or_renew(provider)
            results[provider] = {
                "success": success,
                **result
            }
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all managed tokens.
        
        Returns:
            dict: Status report
        """
        status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.9.7s",
            "tokens": {}
        }
        
        for provider, token_envelope in self.tokens.items():
            is_valid, payload = self.validate_token(provider, token_envelope)
            
            token_status = {
                "valid": is_valid,
            }
            
            if is_valid and payload:
                expires_at = datetime.fromisoformat(payload["expires_at"].rstrip('Z'))
                time_remaining = (expires_at - datetime.utcnow()).total_seconds()
                
                token_status.update({
                    "expires_at": payload["expires_at"],
                    "time_remaining_seconds": int(time_remaining),
                    "needs_renewal": time_remaining < self.RENEWAL_THRESHOLD_SECONDS
                })
            
            status["tokens"][provider] = token_status
        
        return status


def validate_or_renew(provider: str) -> int:
    """
    CLI entry point for validating or renewing a token.
    
    Args:
        provider: Provider name
        
    Returns:
        int: Exit code
    """
    manager = TokenLifecycleManager()
    success, result = manager.validate_or_renew(provider)
    
    if success:
        action = result.get("action")
        reason = result.get("reason")
        print(f"[Dominion] {provider}: {action} - {reason}")
        return 0
    else:
        error = result.get("error", "Unknown error")
        print(f"[Dominion] {provider}: failed - {error}")
        return 1


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m bridge_backend.bridge_core.token_forge_dominion.validate_or_renew <provider>")
        print("Providers: github, netlify, render")
        sys.exit(1)
    
    provider = sys.argv[1]
    exit_code = validate_or_renew(provider)
    sys.exit(exit_code)
