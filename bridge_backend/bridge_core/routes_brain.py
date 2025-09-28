"""
Brain Management Routes for SR-AIbridge Sovereign Brain
FastAPI endpoints for memory management and brain operations
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from bridge_backend.src.brain import create_brain_ledger
from bridge_backend.src.signer import create_signer

# Create router
router = APIRouter(prefix="/brain", tags=["brain"])

# Global brain instance (initialized on first use)
_brain_ledger = None
_signer = None

def get_brain_ledger():
    """Get or create brain ledger instance"""
    global _brain_ledger, _signer
    if _brain_ledger is None:
        _brain_ledger = create_brain_ledger("./brain.sqlite")
        _signer = create_signer("./keys")
    return _brain_ledger

def get_signer():
    """Get or create signer instance"""
    global _signer
    if _signer is None:
        _signer = create_signer("./keys")
    return _signer

# Pydantic models
class MemoryCreate(BaseModel):
    content: str
    category: str = "general"
    classification: str = "public"
    metadata: Optional[Dict[str, Any]] = None
    sign: bool = True

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
    classification: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    resign: bool = True

class MemoryResponse(BaseModel):
    id: int
    content: str
    category: str
    classification: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    signed: bool
    signed_hash: Optional[str] = None

class BrainStats(BaseModel):
    total_memories: int
    signed_memories: int
    unsigned_memories: int
    categories: Dict[str, int]
    classifications: Dict[str, int]
    recent_activity: int
    database_size: int

class ExportRequest(BaseModel):
    category: Optional[str] = None
    classification: Optional[str] = None
    include_signatures: bool = True


@router.get("/status")
async def get_brain_status():
    """Get brain subsystem status"""
    try:
        brain = get_brain_ledger()
        stats = brain.get_statistics()
        
        return {
            "status": "operational",
            "database_path": brain.db_path,
            "database_exists": True,
            "total_memories": stats["total_memories"],
            "signed_memories": stats["signed_memories"],
            "recent_activity": stats["recent_activity"],
            "version": "1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain status error: {str(e)}")


@router.get("/stats", response_model=BrainStats)
async def get_brain_statistics():
    """Get detailed brain statistics"""
    try:
        brain = get_brain_ledger()
        stats = brain.get_statistics()
        
        return BrainStats(
            total_memories=stats["total_memories"],
            signed_memories=stats["signed_memories"],
            unsigned_memories=stats["unsigned_memories"],
            categories=stats["categories"],
            classifications=stats["classifications"],
            recent_activity=stats["recent_activity"],
            database_size=stats["database_size"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")


@router.post("/memories", response_model=Dict[str, Any])
async def create_memory(memory: MemoryCreate):
    """Add a new memory to the brain"""
    try:
        brain = get_brain_ledger()
        
        entry_id = brain.add_memory(
            content=memory.content,
            category=memory.category,
            classification=memory.classification,
            metadata=memory.metadata or {},
            sign=memory.sign
        )
        
        return {
            "status": "success",
            "entry_id": entry_id,
            "message": "Memory added successfully",
            "signed": memory.sign
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {str(e)}")


@router.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: int):
    """Get a specific memory by ID"""
    try:
        brain = get_brain_ledger()
        memory = brain.get_memory(memory_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Parse metadata if it's a string
        metadata = memory.metadata
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata)
        
        return MemoryResponse(
            id=memory.id,
            content=memory.content,
            category=memory.category,
            classification=memory.classification,
            metadata=metadata,
            created_at=memory.created_at.isoformat() if isinstance(memory.created_at, datetime) else memory.created_at,
            updated_at=memory.updated_at.isoformat() if isinstance(memory.updated_at, datetime) else memory.updated_at,
            signed=bool(memory.signed_hash),
            signed_hash=memory.signed_hash
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")


@router.get("/memories", response_model=List[MemoryResponse])
async def search_memories(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    limit: int = Query(20, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset results")
):
    """Search memory entries"""
    try:
        brain = get_brain_ledger()
        memories = brain.search_memories(
            query=query,
            category=category,
            classification=classification,
            limit=limit,
            offset=offset
        )
        
        results = []
        for memory in memories:
            # Parse metadata if it's a string
            metadata = memory.metadata
            if isinstance(metadata, str):
                import json
                metadata = json.loads(metadata)
            
            results.append(MemoryResponse(
                id=memory.id,
                content=memory.content,
                category=memory.category,
                classification=memory.classification,
                metadata=metadata,
                created_at=memory.created_at.isoformat() if isinstance(memory.created_at, datetime) else memory.created_at,
                updated_at=memory.updated_at.isoformat() if isinstance(memory.updated_at, datetime) else memory.updated_at,
                signed=bool(memory.signed_hash),
                signed_hash=memory.signed_hash
            ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.put("/memories/{memory_id}", response_model=Dict[str, Any])
async def update_memory(memory_id: int, update: MemoryUpdate):
    """Update a memory entry"""
    try:
        brain = get_brain_ledger()
        
        success = brain.update_memory(
            entry_id=memory_id,
            content=update.content,
            category=update.category,
            classification=update.classification,
            metadata=update.metadata,
            resign=update.resign
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found or update failed")
        
        return {
            "status": "success",
            "message": "Memory updated successfully",
            "entry_id": memory_id,
            "resigned": update.resign
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update memory: {str(e)}")


@router.delete("/memories/{memory_id}", response_model=Dict[str, Any])
async def delete_memory(memory_id: int):
    """Delete a memory entry"""
    try:
        brain = get_brain_ledger()
        
        success = brain.delete_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "status": "success",
            "message": "Memory deleted successfully",
            "entry_id": memory_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")


@router.get("/categories")
async def get_categories():
    """Get all memory categories with counts"""
    try:
        brain = get_brain_ledger()
        categories = brain.get_categories()
        
        return {
            "status": "success",
            "categories": [{"name": cat, "count": count} for cat, count in categories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.post("/export")
async def export_memories(export_request: ExportRequest):
    """Export brain memories"""
    try:
        brain = get_brain_ledger()
        
        export_data = brain.export_memories(
            category=export_request.category,
            classification=export_request.classification,
            include_signatures=export_request.include_signatures
        )
        
        # Sign the export
        signer = get_signer()
        signed_export = signer.sign_payload(export_data)
        
        return {
            "status": "success",
            "export_data": signed_export,
            "memory_count": export_data["memory_count"],
            "signed": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@router.post("/verify-signatures")
async def verify_memory_signatures():
    """Verify all memory signatures in the brain"""
    try:
        brain = get_brain_ledger()
        results = brain.verify_memory_signatures()
        
        return {
            "status": "success",
            "verification_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")


@router.get("/health")
async def brain_health_check():
    """Brain subsystem health check"""
    try:
        brain = get_brain_ledger()
        stats = brain.get_statistics()
        
        # Basic health checks
        healthy = True
        issues = []
        
        # Check database exists and is accessible
        import os
        if not os.path.exists(brain.db_path):
            healthy = False
            issues.append("Database file not found")
        
        # Check if we can query the database
        try:
            brain.get_statistics()
        except Exception as e:
            healthy = False
            issues.append(f"Database query failed: {str(e)}")
        
        # Check signing capabilities
        try:
            signer = get_signer()
            test_payload = {"test": True, "timestamp": datetime.now().isoformat()}
            signed = signer.sign_payload(test_payload, "admiral")
            is_valid, _ = signer.verify_signature(signed)
            if not is_valid:
                healthy = False
                issues.append("Signature verification failed")
        except Exception as e:
            healthy = False
            issues.append(f"Signing test failed: {str(e)}")
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "issues": issues,
            "database_size": stats.get("database_size", 0),
            "total_memories": stats.get("total_memories", 0),
            "signed_memories": stats.get("signed_memories", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "issues": [f"Health check failed: {str(e)}"],
            "database_size": 0,
            "total_memories": 0,
            "signed_memories": 0
        }