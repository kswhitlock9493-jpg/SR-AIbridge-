# brh/role.py
"""
BRH Role State Management
Tracks whether this node is leader or witness in the federation.
"""
import os
import threading

BRH_NODE_ID = os.getenv("BRH_NODE_ID", "node-unknown")

_state = {
    "leader_id": None,       # who is leader per last consensus
    "i_am_leader": False,    # cached bool
    "lease_token": None,     # optional: forge lease token
    "lock": threading.RLock()
}


def set_leader(leader_id: str, lease_token: str | None = None):
    """
    Set the current leader and update local role state.
    
    Args:
        leader_id: Node ID of the current leader
        lease_token: Optional lease token from Forge
    """
    with _state["lock"]:
        _state["leader_id"] = leader_id
        _state["i_am_leader"] = (leader_id == BRH_NODE_ID)
        _state["lease_token"] = lease_token


def am_leader() -> bool:
    """
    Check if this node is currently the leader.
    
    Returns:
        bool: True if this node is the leader
    """
    with _state["lock"]:
        return _state["i_am_leader"]


def leader_id() -> str | None:
    """
    Get the current leader node ID.
    
    Returns:
        str or None: Current leader node ID
    """
    with _state["lock"]:
        return _state["leader_id"]


def lease_token() -> str | None:
    """
    Get the current lease token.
    
    Returns:
        str or None: Current lease token
    """
    with _state["lock"]:
        return _state["lease_token"]
