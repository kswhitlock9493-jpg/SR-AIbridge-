# brh/api.py
import os
import subprocess
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this to bridge domains in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

if DOCKER_AVAILABLE:
    client = docker.from_env()


@app.post("/deploy")
async def deploy(req: Request):
    """Deploy endpoint for triggering BRH node restart"""
    data = await req.json()
    image = data.get("image")
    branch = data.get("branch")
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
