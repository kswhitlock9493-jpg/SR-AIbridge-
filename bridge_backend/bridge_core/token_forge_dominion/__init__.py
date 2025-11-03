"""
Token Forge Dominion v1.9.7s-SOVEREIGN

Military-grade cryptographic immunity with zero-trust secrets management.
Quantum-resistant token authority for sovereign environment control.
"""

from .quantum_authority import QuantumAuthority, generate_root_key
from .zero_trust_validator import ZeroTrustValidator
from .sovereign_integration import SovereignIntegration
from .quantum_scanner import QuantumScanner
from .enterprise_orchestrator import EnterpriseOrchestrator
from .validate_or_renew import TokenLifecycleManager, validate_or_renew

__version__ = "1.9.7s-SOVEREIGN"
__all__ = [
    "QuantumAuthority",
    "ZeroTrustValidator",
    "SovereignIntegration",
    "QuantumScanner",
    "EnterpriseOrchestrator",
    "TokenLifecycleManager",
    "validate_or_renew",
    "generate_root_key"
]
