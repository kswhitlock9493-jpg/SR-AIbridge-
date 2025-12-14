"""
Genesis Link Adapters
Connect all engines to the Genesis event bus
"""

from .genesis_link import register_all_genesis_links

__all__ = ["register_all_genesis_links"]
