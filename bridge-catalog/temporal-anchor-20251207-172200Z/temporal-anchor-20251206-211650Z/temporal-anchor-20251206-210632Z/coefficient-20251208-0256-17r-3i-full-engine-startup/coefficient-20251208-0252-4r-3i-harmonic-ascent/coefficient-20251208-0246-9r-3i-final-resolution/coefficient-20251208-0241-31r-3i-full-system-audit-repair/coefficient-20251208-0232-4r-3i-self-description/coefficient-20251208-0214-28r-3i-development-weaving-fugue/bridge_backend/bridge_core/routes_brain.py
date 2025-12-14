"""
Brain API Routes for SR-AIbridge Sovereign Brain
Provides tiered memory autonomy: Free (7hr), Paid (14hr), Admiral (24/7)
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/brain", tags=["brain"])

# Import brain ledger
try:
    from src.brain import create_brain_ledger
except ImportError:
    from bridge_backend.src.brain import create_brain_ledger

# Global brain instance
_brain_ledger = None

def get_brain_ledger():
    """Get or create brain ledger instance"""
    global _brain_ledger
    if _brain_ledger is None:
        _brain_ledger = create_brain_ledger()
    return _brain_ledger


class MemoryCreate(BaseModel):
    content: str
    category: str = "general"
    classification: str = "public"
    metadata: Optional[Dict[str, Any]] = None


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    category: Optional[str] = None
    classification: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/stats")
async def get_brain_stats(request: Request):
    """Get brain ledger statistics - tiered access based on user role"""
    try:
        brain = get_brain_ledger()
        stats = brain.get_statistics()
        
        # Add role-based info
        user = getattr(request.state, "user", None)
        role = getattr(user, "role", "captain") if user else "captain"
        
        # Memory autonomy tiers
        memory_tiers = {
            "admiral": {"retention": "24/7", "max_memories": "unlimited"},
            "captain": {"retention": "14hr", "max_memories": 10000},
            "agent": {"retention": "7hr", "max_memories": 1000}
        }
        
        tier_info = memory_tiers.get(role, memory_tiers["agent"])
        stats["tier"] = role
        stats["memory_autonomy"] = tier_info
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get brain stats: {str(e)}")


@router.get("/memories")
async def search_memories(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    request: Request = None
):
    """Search brain memories with filters"""
    try:
        brain = get_brain_ledger()
        memories = brain.search_memories(
            query=query,
            category=category,
            classification=classification,
            limit=limit,
            offset=offset
        )
        
        # Convert to dict format for JSON response
        return [
            {
                "id": m.id,
                "content": m.content,
                "category": m.category,
                "classification": m.classification,
                "metadata": m.metadata,
                "created_at": m.created_at.isoformat() if isinstance(m.created_at, datetime) else m.created_at,
                "updated_at": m.updated_at.isoformat() if isinstance(m.updated_at, datetime) else m.updated_at,
                "signed": bool(m.signed_hash)
            }
            for m in memories
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {str(e)}")


@router.post("/memories")
async def add_memory(memory: MemoryCreate, request: Request):
    """Add a new memory to the brain"""
    try:
        brain = get_brain_ledger()
        
        # Get user for attribution
        user = getattr(request.state, "user", None)
        role = getattr(user, "role", "captain") if user else "captain"
        
        # Add role to metadata
        metadata = memory.metadata or {}
        metadata["created_by_role"] = role
        if user:
            metadata["created_by_user"] = user.id
        
        entry_id = brain.add_memory(
            content=memory.content,
            category=memory.category,
            classification=memory.classification,
            metadata=metadata,
            sign=True
        )
        
        return {
            "status": "success",
            "entry_id": entry_id,
            "message": "Memory added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")


@router.get("/memories/{entry_id}")
async def get_memory(entry_id: int):
    """Get a specific memory by ID"""
    try:
        brain = get_brain_ledger()
        memory = brain.get_memory(entry_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "id": memory.id,
            "content": memory.content,
            "category": memory.category,
            "classification": memory.classification,
            "metadata": memory.metadata,
            "created_at": memory.created_at.isoformat() if isinstance(memory.created_at, datetime) else memory.created_at,
            "updated_at": memory.updated_at.isoformat() if isinstance(memory.updated_at, datetime) else memory.updated_at,
            "signed": bool(memory.signed_hash),
            "signature_data": memory.signature_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")


@router.patch("/memories/{entry_id}")
async def update_memory(entry_id: int, memory: MemoryUpdate):
    """Update an existing memory"""
    try:
        brain = get_brain_ledger()
        
        success = brain.update_memory(
            entry_id=entry_id,
            content=memory.content,
            category=memory.category,
            classification=memory.classification,
            metadata=memory.metadata,
            resign=True
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "status": "success",
            "message": "Memory updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update memory: {str(e)}")


@router.delete("/memories/{entry_id}")
async def delete_memory(entry_id: int):
    """Delete a memory"""
    try:
        brain = get_brain_ledger()
        success = brain.delete_memory(entry_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {
            "status": "success",
            "message": "Memory deleted successfully"
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
        categories_data = brain.get_categories()
        
        return {
            "categories": [
                {"name": cat, "count": count}
                for cat, count in categories_data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.post("/export")
async def export_memories(
    category: Optional[str] = None,
    classification: Optional[str] = None,
    include_signatures: bool = True
):
    """Export brain memories to portable format"""
    try:
        brain = get_brain_ledger()
        export_data = brain.export_memories(
            category=category,
            classification=classification,
            include_signatures=include_signatures
        )
        
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export memories: {str(e)}")


@router.post("/verify")
async def verify_signatures():
    """Verify all memory signatures"""
    try:
        brain = get_brain_ledger()
        verification_result = brain.verify_memory_signatures()
        
        return verification_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify signatures: {str(e)}")


@router.get("")
async def brain_console_status():
    """Return brain console status"""
    try:
        brain = get_brain_ledger()
        stats = brain.get_statistics()
        
        return {
            "brain": "online",
            "status": "operational",
            "total_memories": stats.get("total_memories", 0),
            "database": "connected"
        }
    except Exception as e:
        return {
            "brain": "degraded",
            "status": "error",
            "error": str(e)
        }