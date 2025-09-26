"""
SR-AIbridge Protocol Registry

Minimal registry module containing only the ProtocolEntry class.
This establishes the foundation for future protocol management functionality.
"""


class ProtocolEntry:
    """
    A protocol entry representing a protocol and its state in the registry.
    
    Attributes:
        name (str): The name of the protocol
        state (str): The current state of the protocol (defaults to "vaulted")
    """
    
    def __init__(self, name: str, state: str = "vaulted"):
        """
        Initialize a new protocol entry.
        
        Args:
            name (str): The name of the protocol
            state (str, optional): The state of the protocol. Defaults to "vaulted".
        """
        self.name = name
        self.state = state