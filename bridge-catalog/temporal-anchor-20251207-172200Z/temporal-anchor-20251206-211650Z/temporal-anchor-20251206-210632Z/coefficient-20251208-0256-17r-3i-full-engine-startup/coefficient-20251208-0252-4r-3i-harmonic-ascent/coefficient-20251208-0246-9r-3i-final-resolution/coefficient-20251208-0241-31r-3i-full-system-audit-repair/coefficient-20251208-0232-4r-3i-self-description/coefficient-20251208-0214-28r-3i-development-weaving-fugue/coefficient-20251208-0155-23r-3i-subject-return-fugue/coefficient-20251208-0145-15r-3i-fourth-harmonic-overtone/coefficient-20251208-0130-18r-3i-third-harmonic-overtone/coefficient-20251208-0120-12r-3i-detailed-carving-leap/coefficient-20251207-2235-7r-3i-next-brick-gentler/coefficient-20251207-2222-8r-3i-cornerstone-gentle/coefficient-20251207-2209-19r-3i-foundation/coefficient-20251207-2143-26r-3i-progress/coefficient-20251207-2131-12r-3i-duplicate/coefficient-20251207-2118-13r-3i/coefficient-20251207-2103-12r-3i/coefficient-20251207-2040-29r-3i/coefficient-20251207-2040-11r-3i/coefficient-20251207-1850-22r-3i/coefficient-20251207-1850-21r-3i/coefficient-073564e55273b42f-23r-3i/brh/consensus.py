# brh/consensus.py
"""
BRH Consensus Coordinator Module
Manages peer discovery, leader election, and consensus broadcasting.
"""
import os
import time
import json
import hashlib
import hmac
import threading
import requests
from brh import role, handover

# Import forge for sovereign secret retrieval
try:
    from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
except ImportError:
    # Fallback if not available
    def retrieve_environment(key: str, default=None):
        return os.getenv(key, default)

# Use forge to retrieve environment variables
FORGE_ROOT = retrieve_environment("FORGE_DOMINION_ROOT", "dominion://sovereign.bridge")
CONSENSUS_INTERVAL = int(retrieve_environment("BRH_CONSENSUS_INTERVAL", "180"))
ENV = retrieve_environment("BRH_ENV", "dev")

peers = {}  # node_id → {epoch, uptime, sig, status}


def forge_sig(node_id, epoch):
    """Generate HMAC signature for consensus payload"""
    # Use forge to retrieve environment variable
    seal = retrieve_environment("DOMINION_SEAL", "forge-ephemeral")
    msg = f"{node_id}|{epoch}".encode()
    return hmac.new(seal.encode(), msg, hashlib.sha256).hexdigest()[:32]


def heartbeat_listener(pulse):
    """
    Register heartbeat from peer node.
    
    Args:
        pulse: Dictionary containing node heartbeat data
    """
    node = pulse.get("node")
    peers[node] = {
        "epoch": pulse["epoch"],
        "sig": pulse["sig"],
        "status": "alive",
        "last_seen": time.time()
    }
    # Log event
    try:
        from brh.api import log_event
        log_event(f"HEARTBEAT: received from {node} at epoch {pulse['epoch']}")
    except Exception:
        pass  # Event logging not required for operation


def elect_leader():
    """
    Elect leader from active peers.
    Leader selection: highest epoch (most recent), fallback to alphabetical.
    
    Returns:
        str or None: Node ID of elected leader
    """
    now = time.time()
    active = [
        (node, data) for node, data in peers.items()
        if now - data["last_seen"] < 300
    ]
    if not active:
        return None

    # pick highest epoch (most recent), fallback to alphabetical
    leader = sorted(active, key=lambda x: (-x[1]["epoch"], x[0]))[0][0]
    return leader


def apply_leader_change(new_leader: str, lease_token: str | None = None):
    """
    Apply leader change and trigger promotion/demotion hooks.
    
    Args:
        new_leader: Node ID of new leader
        lease_token: Optional lease token from Forge
    """
    prev = role.leader_id()
    prev_was_leader = role.am_leader()
    role.set_leader(new_leader, lease_token)

    now_leader = role.am_leader()

    if not prev_was_leader and now_leader:
        print(f"[CN] PROMOTE → I am leader ({new_leader})")
        handover.adopt_containers(ENV)
        # Log event
        try:
            from brh.api import log_event
            log_event(f"PROMOTION: node promoted to leader ({new_leader})")
        except Exception:
            pass

    if prev_was_leader and not now_leader:
        print(f"[CN] DEMOTE → I am witness (leader={new_leader})")
        # Non-disruptive default:
        handover.relinquish_ownership(ENV)
        # If you prefer to stop workloads on demotion:
        # handover.drain_and_stop(ENV)
        # Log event
        try:
            from brh.api import log_event
            log_event(f"DEMOTION: node demoted to witness (leader={new_leader})")
        except Exception:
            pass


def broadcast_election():
    """Continuous consensus election broadcast loop"""
    while True:
        leader = elect_leader()
        epoch = int(time.time())
        sig = forge_sig(leader or "none", epoch)

        payload = {
            "epoch": epoch,
            "forge_root": FORGE_ROOT,
            "leader": leader,
            "peers": list(peers.keys()),
            "sig": sig,
        }

        try:
            # Parse forge root to get actual HTTP endpoint
            forge_url = FORGE_ROOT
            if forge_url.startswith("dominion://"):
                forge_url = forge_url.replace("dominion://", "https://")
            
            r = requests.post(f"{forge_url}/federation/consensus", json=payload, timeout=10)
            print(f"[CN] Elected leader={leader} | peers={len(peers)} | → {r.status_code}")
            
            # Log event
            try:
                from brh.api import log_event
                log_event(f"CONSENSUS: elected leader={leader}, peers={len(peers)}")
            except Exception:
                pass
            
            # Send ledger feedback (optional, may not exist yet)
            try:
                ledger_payload = {
                    "epoch": epoch,
                    "leader": leader,
                    "peers": list(peers.keys()),
                    "status": "consensus-ok",
                    "signature": sig,
                    "bridge": "SR-AIBRIDGE"
                }
                requests.post(f"{forge_url}/api/ledger/feedback", json=ledger_payload, timeout=10)
            except Exception:
                pass  # Ledger feedback optional
                
        except Exception as e:
            print(f"[CN] consensus broadcast failed: {e}")

        time.sleep(CONSENSUS_INTERVAL)


def poll_forge_leader_loop():
    """Poll Forge for current leader and apply changes"""
    while True:
        try:
            # Parse forge root to get actual HTTP endpoint
            forge_url = FORGE_ROOT
            if forge_url.startswith("dominion://"):
                forge_url = forge_url.replace("dominion://", "https://")
            
            r = requests.get(f"{forge_url}/federation/leader", timeout=10)
            j = r.json()
            apply_leader_change(j.get("leader"), j.get("lease"))
        except Exception as e:
            print(f"[CN] leader poll failed: {e}")
        time.sleep(10)


def start():
    """
    Start consensus coordinator daemon.
    Launches both election broadcast and leader polling threads.
    """
    enabled = os.getenv("BRH_CONSENSUS_ENABLED", "true").lower() == "true"
    if not enabled:
        print("[CN] Consensus coordinator disabled")
        return
    
    print(f"[CN] Starting consensus coordinator (interval={CONSENSUS_INTERVAL}s)")
    threading.Thread(target=broadcast_election, daemon=True).start()
    threading.Thread(target=poll_forge_leader_loop, daemon=True).start()
    print("[CN] Consensus coordinator started")


if __name__ == "__main__":
    # Allow running standalone for testing
    print("🔧 Running BRH Consensus Coordinator in standalone mode")
    start()
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[CN] Shutting down...")
