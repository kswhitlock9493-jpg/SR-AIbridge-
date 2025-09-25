"""
SR-AIbridge Core Modules
Modular separation for critical AI Bridge components
"""

from .claude_watcher import ClaudeWatcher
from .fault_injector import FaultInjector
from .self_healing_adapter import SelfHealingMASAdapter
from .federation_client import FederationClient
from .registry_payloads import current_registry_payloads

__all__ = [
    "ClaudeWatcher",
    "FaultInjector", 
    "SelfHealingMASAdapter",
    "FederationClient",
    "current_registry_payloads"
]