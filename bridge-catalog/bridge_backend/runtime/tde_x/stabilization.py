"""
StabilizationDomain Context Manager
Isolates shard failures and produces tickets instead of crashing globally
"""
from contextlib import AbstractContextManager
from typing import Optional, Type
import logging

logger = logging.getLogger(__name__)


class StabilizationDomain(AbstractContextManager):
    """
    Context manager that catches exceptions and creates tickets
    instead of propagating them up the stack
    """
    
    def __init__(self, name: str):
        """
        Initialize StabilizationDomain
        
        Args:
            name: Domain name (e.g., "bootstrap", "runtime", "diagnostics")
        """
        self.name = name
    
    def __enter__(self):
        """Enter the context - lightweight trace, no side effects"""
        logger.debug(f"[StabilizationDomain:{self.name}] Entering")
        return self
    
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb
    ):
        """
        Exit the context - create ticket on exception and swallow it
        
        Returns:
            True to suppress exception (keep siblings alive)
        """
        if exc_type:
            from bridge_backend.runtime import tickets
            
            message = f"[TDE-X:{self.name}] {exc_type.__name__}: {exc}"
            tickets.create(message)
            logger.error(f"[StabilizationDomain:{self.name}] Error caught: {message}")
        
        # Swallow exception to keep siblings alive
        return True
