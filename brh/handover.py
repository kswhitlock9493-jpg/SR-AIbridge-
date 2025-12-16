# brh/handover.py
"""
BRH Leader Promotion/Demotion Handover
Manages container ownership transfer during leader elections.
"""
import os
import time
from brh import role

try:
    import docker
    DOCKER_AVAILABLE = True
    client = docker.from_env()
except ImportError:
    DOCKER_AVAILABLE = False
    client = None

OWNER_LABEL = "brh.owner"
ENV_LABEL = "brh.env"


def adopt_containers(env: str):
    """
    Leader adoption: take over unmanaged containers by setting brh.owner label.
    
    Args:
        env: Environment name to filter containers
    """
    if not DOCKER_AVAILABLE:
        print("[PROMOTE] Docker SDK not available, skipping container adoption")
        return
        
    if not role.am_leader():
        return
        
    try:
        for c in client.containers.list(all=True):
            labels = (c.labels or {})
            if labels.get(ENV_LABEL) == env and labels.get(OWNER_LABEL) != role.BRH_NODE_ID:
                try:
                    c.update(labels={**labels, OWNER_LABEL: role.BRH_NODE_ID})
                    print(f"[PROMOTE] Adopted {c.name}")
                except Exception as e:
                    print(f"[PROMOTE] Failed adopt {c.name}: {e}")
    except Exception as e:
        print(f"[PROMOTE] Failed to list containers: {e}")


def relinquish_ownership(env: str):
    """
    Demotion: drop ownership label; do not kill workload (zero-downtime).
    
    Args:
        env: Environment name to filter containers
    """
    if not DOCKER_AVAILABLE:
        print("[DEMOTE] Docker SDK not available, skipping ownership release")
        return
        
    try:
        for c in client.containers.list(all=True):
            labels = (c.labels or {})
            if labels.get(ENV_LABEL) == env and labels.get(OWNER_LABEL) == role.BRH_NODE_ID:
                try:
                    labels_copy = dict(labels)
                    labels_copy.pop(OWNER_LABEL, None)
                    c.update(labels=labels_copy)
                    print(f"[DEMOTE] Released {c.name}")
                except Exception as e:
                    print(f"[DEMOTE] Failed release {c.name}: {e}")
    except Exception as e:
        print(f"[DEMOTE] Failed to list containers: {e}")


def drain_and_stop(env: str, timeout: int = 10):
    """
    Optional: if policy requires, gracefully stop on demotion.
    
    Args:
        env: Environment name to filter containers
        timeout: Seconds to wait for graceful stop
    """
    if not DOCKER_AVAILABLE:
        print("[DEMOTE] Docker SDK not available, skipping drain")
        return
        
    try:
        for c in client.containers.list(all=True):
            labels = (c.labels or {})
            if labels.get(ENV_LABEL) == env and labels.get(OWNER_LABEL) == role.BRH_NODE_ID:
                try:
                    c.stop(timeout=timeout)
                    print(f"[DEMOTE] Stopped {c.name}")
                except Exception as e:
                    print(f"[DEMOTE] Failed stop {c.name}: {e}")
    except Exception as e:
        print(f"[DEMOTE] Failed to list containers: {e}")
