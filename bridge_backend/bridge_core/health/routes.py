from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check for load balancers and monitoring"""
    return {
        "status": "ok",
        "service": "SR-AIbridge",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
async def status_check():
    """System status endpoint"""
    return {
        "status": "healthy",
        "service": "SR-AIbridge",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }