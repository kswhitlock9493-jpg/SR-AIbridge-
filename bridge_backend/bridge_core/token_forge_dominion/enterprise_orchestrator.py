"""
Enterprise Orchestrator - Token Forge Dominion v1.9.7s-SOVEREIGN

CI/CD orchestration, deployment automation, and rollback capabilities.
Implements enterprise-grade deployment workflows with compliance checks.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .quantum_authority import QuantumAuthority
from .zero_trust_validator import ZeroTrustValidator
from .sovereign_integration import SovereignIntegration
from .quantum_scanner import QuantumScanner


class EnterpriseOrchestrator:
    """
    Enterprise orchestrator for sovereign deployment workflows.
    Manages token lifecycle, compliance checks, and automated rollback.
    """
    
    def __init__(self, environment: str = "production"):
        """
        Initialize enterprise orchestrator.
        
        Args:
            environment: Deployment environment
        """
        self.environment = environment
        self.authority = QuantumAuthority()
        self.validator = ZeroTrustValidator()
        self.integration = SovereignIntegration()
        self.scanner = QuantumScanner()
        
        self.deployment_log: List[Dict[str, Any]] = []
        self.pulse_events: List[Dict[str, Any]] = []
        self.pulse_state_file = ".alik/forge_pulse.json"
    
    def pre_deployment_checks(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Run pre-deployment compliance and security checks.
        
        Returns:
            tuple: (passed, report)
        """
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": self.environment,
            "checks": {}
        }
        
        # Check 1: Environment validation
        valid_envs = ["production", "staging", "development"]
        if self.environment not in valid_envs:
            report["checks"]["environment"] = {
                "passed": False,
                "reason": f"Invalid environment: {self.environment}"
            }
            report["overall"] = "FAILED"
            return False, report
        
        report["checks"]["environment"] = {"passed": True}
        
        # Check 2: Root key validation
        try:
            fingerprint = self.authority.get_key_fingerprint()
            report["checks"]["root_key"] = {
                "passed": True,
                "fingerprint": fingerprint
            }
        except Exception as e:
            report["checks"]["root_key"] = {
                "passed": False,
                "reason": f"Root key validation failed: {str(e)}"
            }
            report["overall"] = "FAILED"
            return False, report
        
        # Check 3: Quantum scanner
        scan_report = self.scanner.quantum_scan()
        
        # Allow low/medium risk in non-production
        if self.environment == "production":
            scan_passed = scan_report["status"] in ["CLEAN", "LOW_RISK"]
        else:
            scan_passed = scan_report["status"] not in ["CRITICAL"]
        
        report["checks"]["security_scan"] = {
            "passed": scan_passed,
            "status": scan_report["status"],
            "findings": scan_report["total_findings"],
            "risk_score": scan_report["risk_score"]
        }
        
        if not scan_passed:
            report["overall"] = "FAILED"
            return False, report
        
        # Check 4: Sovereign integration status
        sovereign_status = self.integration.get_sovereign_status()
        
        # Check if rotation is needed
        if sovereign_status["rotation"]["should_rotate"]:
            report["checks"]["key_rotation"] = {
                "passed": False,
                "reason": sovereign_status["rotation"]["reason"],
                "recommendation": "Trigger key rotation before deployment"
            }
            # This is a warning, not a failure
        else:
            report["checks"]["key_rotation"] = {"passed": True}
        
        report["checks"]["resonance"] = {
            "passed": True,
            "score": sovereign_status["resonance"]["score"],
            "category": sovereign_status["resonance"]["category"]
        }
        
        # All critical checks passed
        report["overall"] = "PASSED"
        return True, report
    
    def execute_sovereign_deployment(
        self,
        providers: List[str],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute sovereign deployment for specified providers.
        
        Args:
            providers: List of provider names
            dry_run: If True, simulate without actual token generation
            
        Returns:
            dict: Deployment report
        """
        deployment_report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": self.environment,
            "providers": providers,
            "dry_run": dry_run,
            "results": {}
        }
        
        # Run pre-deployment checks
        checks_passed, checks_report = self.pre_deployment_checks()
        deployment_report["pre_deployment_checks"] = checks_report
        
        if not checks_passed:
            deployment_report["status"] = "FAILED"
            deployment_report["reason"] = "Pre-deployment checks failed"
            return deployment_report
        
        # Process each provider
        successful_providers = []
        failed_providers = []
        
        for provider in providers:
            provider_result = self._deploy_provider(provider, dry_run)
            deployment_report["results"][provider] = provider_result
            
            if provider_result["success"]:
                successful_providers.append(provider)
            else:
                failed_providers.append(provider)
        
        # Determine overall status
        if len(failed_providers) == 0:
            deployment_report["status"] = "SUCCESS"
        elif len(successful_providers) > 0:
            deployment_report["status"] = "PARTIAL"
        else:
            deployment_report["status"] = "FAILED"
        
        deployment_report["successful_providers"] = successful_providers
        deployment_report["failed_providers"] = failed_providers
        
        # Record deployment
        self.deployment_log.append(deployment_report)
        
        # Audit the deployment
        self.integration.record_audit_event("deployment", {
            "status": deployment_report["status"],
            "providers": providers,
            "environment": self.environment
        })
        
        return deployment_report
    
    def _deploy_provider(self, provider: str, dry_run: bool) -> Dict[str, Any]:
        """
        Deploy to a specific provider.
        
        Args:
            provider: Provider name
            dry_run: Simulation mode
            
        Returns:
            dict: Provider deployment result
        """
        result = {
            "provider": provider,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": False
        }
        
        try:
            # Validate issuance context
            is_valid, reason, validation_report = self.validator.validate_issuance_context(
                provider=provider,
                environment=self.environment,
                requester="enterprise_orchestrator",
                metadata={"deployment": True}
            )
            
            if not is_valid:
                result["error"] = f"Validation failed: {reason}"
                return result
            
            result["validation"] = validation_report
            
            # Get resonance-aware TTL
            base_ttl = 300  # 5 minutes base
            ttl = self.integration.get_resonance_aware_ttl(
                base_ttl=base_ttl,
                provider=provider,
                environment=self.environment
            )
            
            result["ttl_seconds"] = ttl
            
            if not dry_run:
                # Mint token
                token = self.authority.mint_quantum_token(
                    provider=provider,
                    ttl_seconds=ttl,
                    metadata={
                        "environment": self.environment,
                        "orchestrated": True
                    }
                )
                
                # Store token ID for tracking (avoid storing full token in logs)
                result["token_id"] = token.get("token_id", "unknown")
                result["token_generated"] = True
            else:
                result["token_generated"] = False
                result["note"] = "Dry run - no token generated"
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def rollback_deployment(
        self,
        deployment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rollback a deployment (revoke issued tokens).
        
        Args:
            deployment_id: Specific deployment to rollback (default: last)
            
        Returns:
            dict: Rollback report
        """
        rollback_report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "rollback",
            "status": "NOT_IMPLEMENTED"
        }
        
        # In a full implementation, this would:
        # 1. Identify tokens issued in the deployment
        # 2. Mark them as revoked in a revocation list
        # 3. Notify providers to invalidate the tokens
        # 4. Generate replacement tokens if needed
        
        rollback_report["note"] = "Token revocation requires distributed coordination"
        
        return rollback_report
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report for audit purposes.
        
        Returns:
            dict: Compliance report
        """
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.9.7s-SOVEREIGN",
            "environment": self.environment
        }
        
        # Include validation metrics
        report["validation_metrics"] = self.validator.get_validation_metrics()
        
        # Include sovereign status
        report["sovereign_status"] = self.integration.get_sovereign_status()
        
        # Include recent deployments
        report["recent_deployments"] = self.deployment_log[-10:]
        
        # Security scan summary
        if self.scanner.scan_results:
            report["security_scan"] = {
                "status": self.scanner.scan_results["status"],
                "risk_score": self.scanner.scan_results["risk_score"],
                "findings": self.scanner.scan_results["findings_by_severity"]
            }
        
        # Compliance status
        all_checks_passing = (
            report["validation_metrics"]["success_rate"] > 95.0 and
            report["sovereign_status"]["resonance"]["score"] > 60.0
        )
        
        report["compliance_status"] = "COMPLIANT" if all_checks_passing else "NON_COMPLIANT"
        
        return report
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of all forge components.
        
        Returns:
            dict: Health status
        """
        health = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "components": {}
        }
        
        # Check quantum authority
        try:
            fingerprint = self.authority.get_key_fingerprint()
            health["components"]["quantum_authority"] = {
                "status": "healthy",
                "fingerprint": fingerprint
            }
        except Exception as e:
            health["components"]["quantum_authority"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check validator
        metrics = self.validator.get_validation_metrics()
        health["components"]["validator"] = {
            "status": "healthy" if metrics["success_rate"] > 80 else "degraded",
            "success_rate": metrics["success_rate"]
        }
        
        # Check sovereign integration
        sovereign_status = self.integration.get_sovereign_status()
        health["components"]["sovereign_integration"] = {
            "status": "healthy",
            "resonance_category": sovereign_status["resonance"]["category"]
        }
        
        # Overall health
        component_statuses = [c["status"] for c in health["components"].values()]
        if all(s == "healthy" for s in component_statuses):
            health["overall_status"] = "healthy"
        elif any(s == "unhealthy" for s in component_statuses):
            health["overall_status"] = "unhealthy"
        else:
            health["overall_status"] = "degraded"
        
        return health
    
    def record_pulse_event(self, event_type: str, provider: str = None) -> None:
        """
        Record a pulse event (mint/renew/reject).
        
        Args:
            event_type: Type of event (mint, renew, reject)
            provider: Provider name (optional)
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "provider": provider
        }
        
        self.pulse_events.append(event)
        
        # Save to state file
        try:
            state_path = Path(self.pulse_state_file)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing events
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    events = state.get("events", [])
            else:
                events = []
            
            events.append(event)
            
            # Keep only last 1000 events
            events = events[-1000:]
            
            with open(state_path, 'w') as f:
                json.dump({"events": events}, f, indent=2)
        except Exception:
            pass
    
    def check_pulse(self) -> Dict[str, Any]:
        """
        Check governance pulse and detect rate limit violations.
        
        Returns:
            dict: Pulse status with governance alerts
        """
        pulse_status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.9.7s",
            "governance_lock": False,
            "alerts": []
        }
        
        # Load recent events
        try:
            state_path = Path(self.pulse_state_file)
            if state_path.exists():
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    events = state.get("events", [])
            else:
                events = []
        except Exception:
            events = []
        
        # Analyze events in last 5 minutes
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=5)
        
        recent_events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"].rstrip('Z')) > window_start
        ]
        
        # Count event types
        mints = len([e for e in recent_events if e["event_type"] == "mint"])
        renews = len([e for e in recent_events if e["event_type"] == "renew"])
        rejects = len([e for e in recent_events if e["event_type"] == "reject"])
        
        pulse_status["pulse_metrics"] = {
            "window_minutes": 5,
            "mints": mints,
            "renews": renews,
            "rejects": rejects,
            "total_events": len(recent_events)
        }
        
        # Check governance thresholds
        # >5 mints or >10 renews in 5min triggers lock
        if mints > 5:
            pulse_status["governance_lock"] = True
            pulse_status["alerts"].append({
                "level": "critical",
                "type": "rate_limit",
                "message": f"Excessive mints detected: {mints} in 5 minutes (limit: 5)"
            })
        
        if renews > 10:
            pulse_status["governance_lock"] = True
            pulse_status["alerts"].append({
                "level": "critical",
                "type": "rate_limit",
                "message": f"Excessive renews detected: {renews} in 5 minutes (limit: 10)"
            })
        
        # Check for inactivity (>20 minutes since last event)
        if events:
            last_event = datetime.fromisoformat(events[-1]["timestamp"].rstrip('Z'))
            inactive_minutes = (now - last_event).total_seconds() / 60
            
            pulse_status["inactive_minutes"] = inactive_minutes
            
            if inactive_minutes > 20:
                pulse_status["alerts"].append({
                    "level": "warning",
                    "type": "inactivity",
                    "message": f"Inactive for {int(inactive_minutes)} minutes (threshold: 20)"
                })
        
        # Calculate pulse strength
        if pulse_status["governance_lock"]:
            pulse_status["pulse_strength"] = "red"
            pulse_status["pulse_message"] = "rate limit triggered"
        elif pulse_status["alerts"]:
            pulse_status["pulse_strength"] = "silver"
            pulse_status["pulse_message"] = "manual review required"
        else:
            pulse_status["pulse_strength"] = "gold"
            pulse_status["pulse_message"] = "healthy"
        
        return pulse_status
