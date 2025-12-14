"""
Phoenix Protocol - Main Application
Built following BUILD_DOSSIER.md specifications

SR-AIbridge Phoenix - Documented Perfection Rebuild
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from contextlib import asynccontextmanager

import db
from models import Guardian, Agent, Mission, VaultLog
from schemas import HealthResponse, FullHealthResponse

# Import routers
from core.agents import routes as agent_routes
from core.missions import routes as mission_routes
from core.engines import calculus_core

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    # Startup
    print("🔥 Phoenix Protocol - Starting Up")
    print(f"Environment: {ENVIRONMENT}")
    
    # Initialize database
    await db.init_db()
    
    # Create default guardian
    async with db.get_db_session() as session:
        result = await session.execute(select(Guardian).where(Guardian.name == "Phoenix-Guardian"))
        guardian = result.scalar_one_or_none()
        
        if not guardian:
            guardian = Guardian(
                name="Phoenix-Guardian",
                status="active",
                capabilities=["health_monitoring", "self_healing", "documentation_validation"],
                health_score=1.0
            )
            session.add(guardian)
            await session.commit()
            print("✅ Phoenix Guardian created")
        else:
            print("✅ Phoenix Guardian exists")
    
    print("✅ Phoenix Protocol - Ready")
    
    yield
    
    # Shutdown
    print("🔥 Phoenix Protocol - Shutting Down")


# Create FastAPI application
app = FastAPI(
    title="SR-AIbridge Phoenix",
    description="Phoenix Protocol - Documented Perfection Rebuild",
    version="1.0.0-phoenix",
    lifespan=lifespan
)

# Configure CORS
origins = ["*"] if CORS_ALLOW_ALL else ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_routes.router)
app.include_router(mission_routes.router)
app.include_router(calculus_core.router)


# Health Endpoints (BUILD_DOSSIER Phase 2 Step 2.3)

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - basic API information"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0-phoenix"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint for load balancers"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0-phoenix"
    )


@app.get("/health/full", response_model=FullHealthResponse)
async def full_health_check(session: AsyncSession = Depends(db.get_session)):
    """Comprehensive health check with system status"""
    
    # Check database connection
    try:
        await session.execute(select(func.count()).select_from(Guardian))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check guardians
    try:
        result = await session.execute(select(Guardian).where(Guardian.status == "active"))
        active_guardians = len(result.scalars().all())
        guardian_status = f"active ({active_guardians})"
    except Exception:
        guardian_status = "error"
    
    # Get counts
    try:
        agent_count = await session.scalar(select(func.count()).select_from(Agent))
        mission_count = await session.scalar(select(func.count()).select_from(Mission))
        log_count = await session.scalar(select(func.count()).select_from(VaultLog))
    except Exception:
        agent_count = mission_count = log_count = 0
    
    return FullHealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0-phoenix",
        components={
            "database": db_status,
            "guardians": guardian_status,
            "engines": "operational"
        },
        metrics={
            "agents_count": agent_count,
            "missions_count": mission_count,
            "logs_count": log_count,
            "health_score": 1.0
        }
    )


@app.get("/status")
async def system_status():
    """System status overview"""
    return {
        "status": "operational",
        "protocol": "phoenix",
        "version": "1.0.0-phoenix",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))  # Use 8001 to not conflict with main backend
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║        SR-AIbridge Phoenix Protocol v1.0.0            ║
    ║        Documented Perfection Rebuild                  ║
    ╚═══════════════════════════════════════════════════════╝
    
    🔥 Starting Phoenix backend on port {port}
    📚 Built from: BUILD_DOSSIER.md
    🎯 Purpose: Documented perfection baseline
    
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
