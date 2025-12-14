"""
Self-Test Engine
Bridge Autonomy Diagnostic Pulse

Runs full synthetic deploys, monitors all engines, and triggers auto-healing.
"""

from .core import SelfTestController
from .autoheal_trigger import AutoHealTrigger

__all__ = ["SelfTestController", "AutoHealTrigger"]
