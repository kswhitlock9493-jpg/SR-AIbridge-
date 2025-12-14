"""
Core Event Bus wrapper
Re-exports the heritage event bus for engine-wide access
"""

from ..heritage.event_bus import bus

__all__ = ["bus"]
