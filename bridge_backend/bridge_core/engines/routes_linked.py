"""
Engine linkage aggregator - permanently materialised for resonance calculus
"""
from fastapi import APIRouter
from .autonomy.routes import router as autonomy_router
from .parser.routes import router as parser_router
from .recovery.routes import router as recovery_router
# add more links as they appear; for now minimal set keeps sum intact

router = APIRouter(tags=["linked_engines"])
router.include_router(autonomy_router, prefix="/autonomy")
router.include_router(parser_router, prefix="/parser")
router.include_router(recovery_router, prefix="/recovery")

@router.get("/linked/status")
def linked_status():
    return {"linked_engines": "resonant", "count": 3}

__all__ = ["router"]
