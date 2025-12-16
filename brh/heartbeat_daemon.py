# brh/heartbeat_daemon.py
"""
BRH Heartbeat Daemon
Establishes Bridge-to-Bridge pings and Forge health consensus loop.
"""
import os
import time
import hmac
import hashlib
import json
import threading
import requests

# Import forge for sovereign secret retrieval
try:
    from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
except ImportError:
    # Fallback if not available
    def retrieve_environment(key: str, default=None):
        return os.getenv(key, default)


# Use forge to retrieve environment variables
FORGE_ROOT = retrieve_environment("FORGE_DOMINION_ROOT", "dominion://sovereign.bridge")
HEARTBEAT_INTERVAL = int(retrieve_environment("BRH_HEARTBEAT_INTERVAL", "60"))


def forge_sig(epoch: int) -> str:
    """
    Generate HMAC-SHA256 signature for heartbeat.
    
    Args:
        epoch: Current Unix timestamp
        
    Returns:
        32-character hex signature
    """
    # Use forge to retrieve environment variable
    seal = retrieve_environment("DOMINION_SEAL", "forge-ephemeral")
    msg = f"{FORGE_ROOT}|{epoch}".encode()
    return hmac.new(seal.encode(), msg, hashlib.sha256).hexdigest()[:32]


def broadcast_heartbeat():
    """
    Continuously broadcast heartbeat pulses to the Forge.
    Runs in an infinite loop with configurable interval.
    """
    while True:
        epoch = int(time.time())
        sig = forge_sig(epoch)
        payload = {
            "epoch": epoch,
            "forge_root": FORGE_ROOT,
            "sig": sig,
            "node": os.getenv("BRH_NODE_ID", "unknown"),
            "status": "alive",
        }
        
        try:
            # Parse forge root to get actual HTTP endpoint
            forge_url = FORGE_ROOT
            if forge_url.startswith("dominion://"):
                # Convert dominion:// to https:// for actual HTTP calls
                forge_url = forge_url.replace("dominion://", "https://")
            
            # Send heartbeat to federation endpoint
            endpoint = f"{forge_url}/federation/heartbeat"
            r = requests.post(endpoint, json=payload, timeout=10)
            print(f"[HB] {payload['node']} pulse → {r.status_code}")
            
        except Exception as e:
            print(f"[HB] {payload['node']} failed pulse: {e}")
        
        time.sleep(HEARTBEAT_INTERVAL)


def start():
    """
    Start the heartbeat daemon in a background thread.
    This should be called during BRH startup.
    """
    enabled = os.getenv("BRH_HEARTBEAT_ENABLED", "true").lower() == "true"
    if not enabled:
        print("[HB] Heartbeat daemon disabled")
        return
    
    print(f"[HB] Starting heartbeat daemon (interval={HEARTBEAT_INTERVAL}s)")
    t = threading.Thread(target=broadcast_heartbeat, daemon=True)
    t.start()
    print("[HB] Heartbeat daemon started")


if __name__ == "__main__":
    # Allow running standalone for testing
    print("🔧 Running BRH Heartbeat Daemon in standalone mode")
    start()
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[HB] Shutting down...")
