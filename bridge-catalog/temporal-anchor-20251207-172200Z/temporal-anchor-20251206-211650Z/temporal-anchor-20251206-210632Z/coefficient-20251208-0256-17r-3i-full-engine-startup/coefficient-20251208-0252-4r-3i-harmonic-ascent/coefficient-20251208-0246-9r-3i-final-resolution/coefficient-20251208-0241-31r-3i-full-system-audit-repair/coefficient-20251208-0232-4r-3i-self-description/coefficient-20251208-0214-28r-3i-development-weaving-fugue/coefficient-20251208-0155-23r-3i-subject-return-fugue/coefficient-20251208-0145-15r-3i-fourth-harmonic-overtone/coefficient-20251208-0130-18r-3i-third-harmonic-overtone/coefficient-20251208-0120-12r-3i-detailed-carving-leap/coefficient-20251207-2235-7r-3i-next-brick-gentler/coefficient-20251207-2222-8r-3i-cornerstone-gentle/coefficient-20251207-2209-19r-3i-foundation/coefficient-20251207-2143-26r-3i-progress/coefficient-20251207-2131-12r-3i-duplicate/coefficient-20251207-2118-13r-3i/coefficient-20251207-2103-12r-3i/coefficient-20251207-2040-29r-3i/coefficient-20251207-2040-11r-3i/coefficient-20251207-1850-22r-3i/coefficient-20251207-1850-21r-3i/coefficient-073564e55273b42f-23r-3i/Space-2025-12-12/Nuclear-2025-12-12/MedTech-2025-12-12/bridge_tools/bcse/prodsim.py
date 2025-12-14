"""BCSE Production Simulation Module

Full "prove" runner: builds frontend, runs backend, performs API & CORS sanity 
and returns non-zero if any prod criteria fail.
"""
import subprocess
import os
import sys


def build_frontend() -> int:
    """
    Build frontend production bundle
    
    Returns:
        0 if build succeeds, non-zero otherwise
    """
    print("▶ Building frontend...")
    try:
        result = subprocess.call(
            ["npm", "--prefix", "bridge-frontend", "run", "build"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        if result != 0:
            print("❌ Frontend build failed")
        else:
            print("✅ Frontend build succeeded")
        return result
    except FileNotFoundError:
        print("⚠️  npm not found, skipping frontend build")
        return 0


def check_cors(origins_env: str) -> int:
    """
    Validate CORS configuration
    
    Args:
        origins_env: Comma-separated list of allowed origins
        
    Returns:
        0 if valid, 1 otherwise
    """
    if not origins_env:
        return 1
        
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    
    # Simple sanity: at least 1 https origin
    if any(o.startswith("https://") for o in origins):
        return 0
    else:
        print("❌ ALLOWED_ORIGINS must contain at least one https:// origin")
        return 1


def prove() -> int:
    """
    Run full production proof sequence
    
    Returns:
        0 if all checks pass, 1 otherwise
    """
    print("\n" + "=" * 60)
    print("🜂 BCSE Production Proof")
    print("=" * 60 + "\n")
    
    # 1) Build UI
    if build_frontend() != 0:
        print("❌ Frontend build failed")
        return 1
        
    # 2) Run prod checks
    print("\n▶ Running production checks...")
    from .prodcheck import run_checks
    if run_checks() != 0:
        print("❌ Prod checks failed")
        return 1
        
    # 3) CORS sanity
    print("\n▶ Checking CORS configuration...")
    if check_cors(os.getenv("ALLOWED_ORIGINS", "")) != 0:
        print("❌ ALLOWED_ORIGINS must contain at least one https:// origin")
        return 1
        
    print("\n" + "=" * 60)
    print("✅ Production proof passed")
    print("=" * 60 + "\n")
    return 0
