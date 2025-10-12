"""
Umbra API Routes
RESTful endpoints for Umbra Cognitive Stack
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from .core import UmbraCore
from .memory import UmbraMemory
from .predictive import UmbraPredictive
from .echo import UmbraEcho

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/umbra", tags=["umbra"])

# Request/Response Models
class TelemetryInput(BaseModel):
    error_rate: Optional[float] = None
    response_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ChangeInput(BaseModel):
    actor: str = "Admiral"
    file: str
    diff: Optional[str] = ""
    commit_hash: Optional[str] = None
    lines_added: Optional[int] = 0
    lines_removed: Optional[int] = 0


class CommitInput(BaseModel):
    hash: str
    author: str = "Admiral"
    message: Optional[str] = ""
    files: List[Dict[str, Any]]


# Dependency injection for engine instances
def get_umbra_engines():
    """Get or create Umbra engine instances"""
    # Import here to avoid circular dependencies
    try:
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.bridge_core.engines.chronicleloom import ChronicleLoom
    except ImportError:
        from genesis.bus import genesis_bus
        from bridge_core.engines.chronicleloom import ChronicleLoom
    
    # Simple stub for truth - actual certification happens in the engines
    truth = None
    try:
        chronicle_loom = ChronicleLoom()
    except Exception:
        chronicle_loom = None
    
    memory = UmbraMemory(truth=truth, chronicle_loom=chronicle_loom)
    core = UmbraCore(memory=memory, truth=truth, genesis_bus=genesis_bus)
    predictive = UmbraPredictive(memory=memory, core=core)
    echo = UmbraEcho(memory=memory, truth=truth, genesis_bus=genesis_bus)
    
    return {
        "core": core,
        "memory": memory,
        "predictive": predictive,
        "echo": echo
    }


# === Core Endpoints ===

@router.post("/detect")
async def detect_anomaly(telemetry: TelemetryInput):
    """
    Detect anomalies from telemetry data
    
    **RBAC**: Admiral, Captain
    """
    engines = get_umbra_engines()
    core = engines["core"]
    
    try:
        anomaly = await core.detect_anomaly(telemetry.model_dump())
        
        if not anomaly:
            return {
                "status": "ok",
                "message": "No anomalies detected",
                "telemetry": telemetry.model_dump()
            }
        
        return {
            "status": "anomaly_detected",
            "anomaly": anomaly
        }
    except Exception as e:
        logger.error(f"Umbra detect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repair")
async def generate_and_apply_repair(telemetry: TelemetryInput):
    """
    Detect anomaly, generate repair, and apply it
    
    **RBAC**: Admiral only
    """
    engines = get_umbra_engines()
    core = engines["core"]
    
    try:
        # Detect anomaly
        anomaly = await core.detect_anomaly(telemetry.model_dump())
        
        if not anomaly:
            return {
                "status": "ok",
                "message": "No repair needed"
            }
        
        # Generate repair
        repair = await core.generate_repair(anomaly)
        
        # Apply repair
        result = await core.apply_repair(repair)
        
        return {
            "status": "repair_applied",
            "anomaly": anomaly,
            "repair": repair,
            "result": result
        }
    except Exception as e:
        logger.error(f"Umbra repair error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Memory Endpoints ===

@router.get("/memory")
async def get_memory(category: Optional[str] = None, limit: int = 10):
    """
    Recall experiences from Umbra Memory
    
    **RBAC**: Admiral, Captain (read-only)
    """
    engines = get_umbra_engines()
    memory = engines["memory"]
    
    try:
        experiences = await memory.recall(category=category, limit=limit)
        return {
            "experiences": experiences,
            "count": len(experiences),
            "category": category
        }
    except Exception as e:
        logger.error(f"Umbra memory recall error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/patterns")
async def learn_patterns(pattern_type: str = "repair"):
    """
    Learn patterns from stored experiences
    
    **RBAC**: Admiral, Captain
    """
    engines = get_umbra_engines()
    memory = engines["memory"]
    
    try:
        patterns = await memory.learn_pattern(pattern_type=pattern_type)
        return patterns
    except Exception as e:
        logger.error(f"Umbra pattern learning error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Predictive Endpoints ===

@router.post("/predict")
async def predict_issue(telemetry: TelemetryInput):
    """
    Predict potential issues from telemetry
    
    **RBAC**: Admiral, Captain
    """
    engines = get_umbra_engines()
    predictive = engines["predictive"]
    
    try:
        prediction = await predictive.predict_issue(telemetry.model_dump())
        
        if not prediction:
            return {
                "status": "no_prediction",
                "message": "No issues predicted"
            }
        
        return {
            "status": "prediction_made",
            "prediction": prediction
        }
    except Exception as e:
        logger.error(f"Umbra prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/prevent")
async def apply_preventive_repair(telemetry: TelemetryInput):
    """
    Predict issue and apply preventive repair
    
    **RBAC**: Admiral only
    """
    engines = get_umbra_engines()
    predictive = engines["predictive"]
    
    try:
        # Predict issue
        prediction = await predictive.predict_issue(telemetry.model_dump())
        
        if not prediction:
            return {
                "status": "no_action",
                "message": "No preventive action needed"
            }
        
        # Apply preventive repair
        result = await predictive.apply_preventive_repair(prediction)
        
        return {
            "status": "preventive_repair_applied",
            "prediction": prediction,
            "result": result
        }
    except Exception as e:
        logger.error(f"Umbra preventive repair error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Echo Endpoints ===

@router.post("/echo/capture")
async def capture_edit(change: ChangeInput):
    """
    Capture a manual edit/change
    
    **RBAC**: Admiral only (write)
    """
    engines = get_umbra_engines()
    echo = engines["echo"]
    
    try:
        entry = await echo.capture_edit(change.model_dump())
        return {
            "status": "captured",
            "entry": entry
        }
    except Exception as e:
        logger.error(f"Umbra echo capture error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/echo/observe")
async def observe_commit(commit: CommitInput):
    """
    Observe a git commit and capture all changes
    
    **RBAC**: Admiral only (write)
    """
    engines = get_umbra_engines()
    echo = engines["echo"]
    
    try:
        entries = await echo.observe_commit(commit.model_dump())
        return {
            "status": "observed",
            "entries": entries,
            "count": len(entries)
        }
    except Exception as e:
        logger.error(f"Umbra echo observe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Metrics Endpoints ===

@router.get("/metrics")
async def get_metrics():
    """
    Get Umbra Cognitive Stack metrics
    
    **RBAC**: Admiral, Captain, Observer
    """
    engines = get_umbra_engines()
    
    try:
        return {
            "umbra_core": engines["core"].get_metrics(),
            "umbra_memory": engines["memory"].get_metrics(),
            "umbra_predictive": engines["predictive"].get_metrics(),
            "umbra_echo": engines["echo"].get_metrics()
        }
    except Exception as e:
        logger.error(f"Umbra metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """
    Get Umbra engine status
    
    **RBAC**: All roles
    """
    engines = get_umbra_engines()
    
    return {
        "status": "active",
        "version": "1.9.7e",
        "engines": {
            "core": engines["core"].enabled,
            "memory": engines["memory"].enabled,
            "predictive": engines["predictive"].enabled,
            "echo": engines["echo"].enabled
        }
    }
