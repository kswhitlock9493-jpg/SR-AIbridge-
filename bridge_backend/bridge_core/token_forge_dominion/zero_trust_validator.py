"""
Zero-Trust Validator - Token Forge Dominion v1.9.7s-SOVEREIGN

Behavioral anomaly detection and entropy validation for token issuance.
Implements zero-trust security model with context-aware validation.
"""
import os
import re
import hashlib
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import Counter


class ZeroTrustValidator:
    """
    Zero-trust validation matrix for token issuance context.
    Validates behavioral patterns, entropy, and security posture.
    """
    
    # Entropy thresholds
    MIN_ENTROPY_BITS = 4.0  # Minimum Shannon entropy for secrets
    MIN_SECRET_LENGTH = 16  # Minimum length for secret values
    
    # Behavioral anomaly thresholds
    MAX_ISSUANCE_RATE_PER_MINUTE = 60
    MAX_FAILED_VALIDATIONS_PER_HOUR = 10
    
    def __init__(self):
        """Initialize zero-trust validator."""
        self.validation_history: List[Dict[str, Any]] = []
        self.failed_validations: List[Dict[str, Any]] = []
    
    def calculate_entropy(self, data: str) -> float:
        """
        Calculate Shannon entropy of a string.
        
        Args:
            data: String to analyze
            
        Returns:
            float: Shannon entropy in bits
        """
        if not data:
            return 0.0
        
        # Count character frequencies
        counter = Counter(data)
        length = len(data)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def validate_secret_entropy(self, secret: str, min_entropy: Optional[float] = None) -> Tuple[bool, str]:
        """
        Validate that a secret has sufficient entropy.
        
        Args:
            secret: Secret string to validate
            min_entropy: Minimum entropy threshold (default: MIN_ENTROPY_BITS)
            
        Returns:
            tuple: (is_valid, reason)
        """
        if min_entropy is None:
            min_entropy = self.MIN_ENTROPY_BITS
        
        if len(secret) < self.MIN_SECRET_LENGTH:
            return False, f"Secret too short (minimum {self.MIN_SECRET_LENGTH} characters)"
        
        entropy = self.calculate_entropy(secret)
        if entropy < min_entropy:
            return False, f"Insufficient entropy: {entropy:.2f} bits (minimum {min_entropy} bits)"
        
        return True, "Secret entropy sufficient"
    
    def detect_hardcoded_patterns(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect potential hardcoded secrets in content.
        
        Args:
            content: Content to scan
            
        Returns:
            list: List of detected patterns with metadata
        """
        detections = []
        
        # Common secret patterns
        patterns = {
            "api_key": r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
            "secret_key": r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
            "password": r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([a-zA-Z0-9_\-@!#$%^&*]{8,})["\']?',
            "token": r'(?i)(token|access[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            "private_key": r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
            "aws_key": r'(?i)(AKIA[0-9A-Z]{16})',
            "github_token": r'(?i)(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}',
            "generic_secret": r'(?i)(secret|key|token|password)\s*[:=]\s*["\']([^"\']{16,})["\']'
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                detections.append({
                    "pattern": pattern_name,
                    "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                    "position": match.start(),
                    "severity": "high" if pattern_name in ["private_key", "aws_key", "github_token"] else "medium"
                })
        
        return detections
    
    def validate_issuance_context(
        self,
        provider: str,
        environment: str,
        requester: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate the context of a token issuance request.
        
        Args:
            provider: Provider requesting token
            environment: Environment context (e.g., 'production', 'staging')
            requester: Optional requester identifier
            metadata: Optional additional context
            
        Returns:
            tuple: (is_valid, reason, validation_report)
        """
        validation_report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "provider": provider,
            "environment": environment,
            "requester": requester,
            "checks": {}
        }
        
        # Check 1: Valid provider
        valid_providers = ["render", "netlify", "github", "local", "test"]
        if provider not in valid_providers:
            validation_report["checks"]["provider"] = {
                "passed": False,
                "reason": f"Unknown provider: {provider}"
            }
            return False, f"Invalid provider: {provider}", validation_report
        
        validation_report["checks"]["provider"] = {
            "passed": True,
            "reason": "Provider validated"
        }
        
        # Check 2: Valid environment
        valid_environments = ["production", "staging", "development", "test", "local"]
        if environment not in valid_environments:
            validation_report["checks"]["environment"] = {
                "passed": False,
                "reason": f"Unknown environment: {environment}"
            }
            return False, f"Invalid environment: {environment}", validation_report
        
        validation_report["checks"]["environment"] = {
            "passed": True,
            "reason": "Environment validated"
        }
        
        # Check 3: Rate limiting (simplified - in production use Redis/distributed cache)
        recent_validations = [
            v for v in self.validation_history[-100:]
            if (datetime.utcnow() - datetime.fromisoformat(v["timestamp"].rstrip('Z'))).total_seconds() < 60
        ]
        
        if len(recent_validations) > self.MAX_ISSUANCE_RATE_PER_MINUTE:
            validation_report["checks"]["rate_limit"] = {
                "passed": False,
                "reason": f"Rate limit exceeded: {len(recent_validations)} requests in last minute"
            }
            return False, "Rate limit exceeded", validation_report
        
        validation_report["checks"]["rate_limit"] = {
            "passed": True,
            "reason": f"{len(recent_validations)} requests in last minute (limit: {self.MAX_ISSUANCE_RATE_PER_MINUTE})"
        }
        
        # Check 4: Behavioral anomaly detection
        failed_count = len([
            f for f in self.failed_validations[-100:]
            if (datetime.utcnow() - datetime.fromisoformat(f["timestamp"].rstrip('Z'))).total_seconds() < 3600
        ])
        
        if failed_count > self.MAX_FAILED_VALIDATIONS_PER_HOUR:
            validation_report["checks"]["behavioral"] = {
                "passed": False,
                "reason": f"Too many failed validations: {failed_count} in last hour"
            }
            self.failed_validations.append(validation_report)
            return False, "Behavioral anomaly detected", validation_report
        
        validation_report["checks"]["behavioral"] = {
            "passed": True,
            "reason": f"{failed_count} failed validations in last hour (limit: {self.MAX_FAILED_VALIDATIONS_PER_HOUR})"
        }
        
        # Check 5: Metadata validation
        if metadata:
            if "resonance_score" in metadata:
                resonance = metadata["resonance_score"]
                if not isinstance(resonance, (int, float)) or resonance < 0 or resonance > 100:
                    validation_report["checks"]["metadata"] = {
                        "passed": False,
                        "reason": f"Invalid resonance_score: {resonance}"
                    }
                    return False, "Invalid metadata", validation_report
        
        validation_report["checks"]["metadata"] = {
            "passed": True,
            "reason": "Metadata validated"
        }
        
        # All checks passed
        validation_report["overall"] = "PASSED"
        self.validation_history.append(validation_report)
        
        # Keep history bounded
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-500:]
        
        return True, "Validation successful", validation_report
    
    def scan_environment_for_secrets(self, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """
        Scan environment variables for potential hardcoded secrets.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            dict: Scan report with findings
        """
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_vars": len(env_vars),
            "findings": [],
            "summary": {
                "high_risk": 0,
                "medium_risk": 0,
                "low_entropy": 0
            }
        }
        
        for key, value in env_vars.items():
            # Skip non-secret-like variables
            if not any(keyword in key.lower() for keyword in ["key", "secret", "token", "password", "auth"]):
                continue
            
            # Check entropy
            is_valid, reason = self.validate_secret_entropy(value)
            if not is_valid:
                report["findings"].append({
                    "variable": key,
                    "issue": "low_entropy",
                    "severity": "medium",
                    "reason": reason
                })
                report["summary"]["low_entropy"] += 1
            
            # Check for patterns
            detections = self.detect_hardcoded_patterns(f"{key}={value}")
            for detection in detections:
                report["findings"].append({
                    "variable": key,
                    "issue": "pattern_match",
                    "severity": detection["severity"],
                    "pattern": detection["pattern"]
                })
                if detection["severity"] == "high":
                    report["summary"]["high_risk"] += 1
                else:
                    report["summary"]["medium_risk"] += 1
        
        report["total_findings"] = len(report["findings"])
        report["risk_level"] = "high" if report["summary"]["high_risk"] > 0 else \
                              "medium" if report["summary"]["medium_risk"] > 0 else "low"
        
        return report
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """
        Get validation metrics for monitoring.
        
        Returns:
            dict: Validation metrics
        """
        return {
            "total_validations": len(self.validation_history),
            "total_failures": len(self.failed_validations),
            "success_rate": (
                (len(self.validation_history) - len(self.failed_validations)) / len(self.validation_history) * 100
                if self.validation_history else 0.0
            ),
            "recent_validations": len([
                v for v in self.validation_history[-100:]
                if (datetime.utcnow() - datetime.fromisoformat(v["timestamp"].rstrip('Z'))).total_seconds() < 300
            ])
        }
