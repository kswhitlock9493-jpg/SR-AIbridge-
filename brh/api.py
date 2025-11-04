# brh/api.py
import os
import subprocess
import time
import re
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from brh import role

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

app = FastAPI()

# Event log storage (in-memory)
EVENT_LOG = []

# Configure CORS based on environment
ALLOWED_ORIGINS = os.getenv("BRH_ALLOWED_ORIGINS", "").split(",") if os.getenv("BRH_ALLOWED_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

if DOCKER_AVAILABLE:
    client = docker.from_env()

# Valid image name pattern (prevents command injection)
# Supports: name, name:tag, registry/name:tag, registry:port/name:tag
IMAGE_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._:/-]*$')

def validate_image_name(image: str) -> bool:
    """Validate Docker image name to prevent command injection"""
    if not image or len(image) > 256:
        return False
    # Reject images with shell metacharacters
    dangerous_chars = [';', '&', '|', '$', '`', '(', ')', '<', '>', '\n', '\r', ' ']
    if any(char in image for char in dangerous_chars):
        return False
    return IMAGE_PATTERN.match(image) is not None


@app.post("/deploy")
async def deploy(req: Request):
    """Deploy endpoint for triggering BRH node restart"""
    # Only leader can accept deploy hooks
    if not role.am_leader():
        return {"status": "ignored", "reason": "not-leader"}
    
    data = await req.json()
    image = data.get("image", "")
    branch = data.get("branch", "unknown")
    
    # Validate image name to prevent command injection
    if not validate_image_name(image):
        raise HTTPException(status_code=400, detail="Invalid image name")
    
    print(f"[BRH] Deploy request for {image} (branch: {branch})")

    try:
        subprocess.call(["docker", "pull", image])
        subprocess.call(["python3", "-m", "brh.run"])
        return {"status": "restarted", "image": image}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/status")
def status():
    """Get status of running containers"""
    if not DOCKER_AVAILABLE:
        return {
            "error": "Docker SDK not available",
            "forge_root": os.getenv("FORGE_DOMINION_ROOT", "unset"),
            "container_count": 0,
            "containers": [],
            "timestamp": time.time()
        }

    containers = client.containers.list(all=True)
    info = []
    for c in containers:
        info.append({
            "id": c.short_id,
            "name": c.name,
            "image": c.image.tags[0] if c.image.tags else "unknown",
            "status": c.status,
            "started": c.attrs.get("State", {}).get("StartedAt", "N/A"),
        })
    return {
        "forge_root": os.getenv("FORGE_DOMINION_ROOT", "unset"),
        "container_count": len(info),
        "containers": info,
        "timestamp": time.time()
    }


@app.post("/restart/{name}")
def restart_container(name: str):
    """Restart a specific container"""
    if not DOCKER_AVAILABLE:
        return {"error": "Docker SDK not available"}

    try:
        c = client.containers.get(name)
        c.restart()
        return {"status": "restarted", "name": name}
    except Exception as e:
        return {"error": str(e)}


@app.post("/drain/{name}")
def drain(name: str):
    """Stop and remove a specific container"""
    if not DOCKER_AVAILABLE:
        return {"error": "Docker SDK not available"}

    try:
        c = client.containers.get(name)
        c.stop(timeout=10)
        c.remove()
        return {"status": "drained", "name": name}
    except Exception as e:
        return {"error": str(e)}


def log_event(msg: str):
    """
    Log an event to the in-memory event log.
    Used by heartbeat, consensus, chaos, and recovery modules.
    
    Args:
        msg: Event message to log
    """
    from datetime import timezone
    EVENT_LOG.append({"time": datetime.now(timezone.utc).isoformat(), "message": msg})
    if len(EVENT_LOG) > 1000:
        EVENT_LOG.pop(0)


@app.get("/federation/state")
def federation_state():
    """
    Get current federation state including leader and peers.
    Used by FederationConsole UI component.
    """
    from brh import consensus
    return {
        "leader": role.leader_id(),
        "peers": [
            {
                "node": n,
                "epoch": d.get("epoch", 0),
                "status": d.get("status", "unknown"),
                "uptime": "ok"
            }
            for n, d in consensus.peers.items()
        ],
    }


@app.get("/events")
def events():
    """
    Get recent events from the event log.
    Returns up to the last 50 events.
    """
    return EVENT_LOG[-50:]
