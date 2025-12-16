"""BCSE Production Readiness Check Module

Hard "production readiness" gate. Fails on unsafe flags, permissive CORS, 
missing health, etc.
"""
import json
import os
import subprocess
import time
import socket
import http.client

FAIL = 1
OK = 0


def _env_asserts() -> int:
    """
    Assert production environment configuration
    
    Returns:
        0 if all checks pass, 1 otherwise
    """
    problems = []
    
    # Check CORS configuration
    if os.getenv("CORS_ALLOW_ALL", "false").lower() == "true":
        problems.append("CORS_ALLOW_ALL must be false in production.")
        
    # Check DEBUG flag
    if os.getenv("DEBUG", "false").lower() == "true":
        problems.append("DEBUG must be false in production.")
        
    # Check ALLOWED_ORIGINS is set
    if os.getenv("ALLOWED_ORIGINS", "").strip() == "":
        problems.append("ALLOWED_ORIGINS must be set (comma-separated).")
        
    # Check Forge Dominion root (Sovereign requirement)
    if os.getenv("FORGE_DOMINION_ROOT", "") == "":
        problems.append("FORGE_DOMINION_ROOT must be set (Sovereign).")
        
    if problems:
        print("❌ ENV PROBLEMS:\n- " + "\n- ".join(problems))
        return FAIL
        
    return OK


def _port_open(host: str, port: int, timeout: int = 5) -> bool:
    """
    Check if a port is open
    
    Args:
        host: Hostname or IP
        port: Port number
        timeout: Connection timeout in seconds
        
    Returns:
        True if port is open, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def _backend_smoke(url: str = "http://127.0.0.1:8000") -> int:
    """
    Run smoke test on backend health endpoint
    
    Args:
        url: Base URL for backend
        
    Returns:
        0 if healthy, 1 otherwise
    """
    try:
        time.sleep(0.7)  # Give server time to start
        conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=3)
        conn.request("GET", "/health")
        r = conn.getresponse()
        ok = (r.status == 200)
        body = r.read()[:200].decode(errors="ignore")
        print(f"Health: {r.status} {body}")
        conn.close()
        return OK if ok else FAIL
    except Exception as e:
        print(f"Backend check error: {e}")
        return FAIL


def run_fastapi_local() -> int:
    """
    Boot FastAPI locally and test health endpoint
    
    Returns:
        0 if all checks pass, 1 otherwise
    """
    proc = subprocess.Popen(
        ["python", "bridge_backend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    try:
        # Wait for port to open
        for _ in range(30):
            if _port_open("127.0.0.1", 8000):
                break
            time.sleep(0.2)
        else:
            print("❌ Backend failed to start within timeout")
            return FAIL
            
        res = _backend_smoke()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
            
    return res


def run_checks() -> int:
    """
    Run all production readiness checks
    
    Returns:
        0 if all checks pass, 1 otherwise
    """
    # Check environment configuration
    env_ok = _env_asserts()
    if env_ok != OK:
        return FAIL
        
    # Ensure no placeholder mode
    from .placeholders import scan
    hits = scan(".")
    if hits:
        print("❌ Placeholder/Stubs detected:")
        for f, ln, snip in hits[:25]:
            print(f"  {f}:{ln} :: {snip[:120]}")
        return FAIL
        
    # Boot backend quickly and ping /health
    # Skip in CI or test environment
    if os.getenv("CI") or os.getenv("PYTEST_CURRENT_TEST"):
        print("⚠️  Skipping backend health check in CI/test environment")
        return OK
        
    return run_fastapi_local()
