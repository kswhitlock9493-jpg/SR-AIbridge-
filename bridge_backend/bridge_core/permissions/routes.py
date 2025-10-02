from fastapi import APIRouter, HTTPException
from .service import Tier, get_rules

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.get("/tiers")
def list_tiers():
    return {"tiers": {t.value: get_rules(t) for t in Tier}}

@router.get("/tiers/{tier_name}")
def tier_detail(tier_name: str):
    try:
        tier = Tier(tier_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="tier_not_found")
    return {"tier": tier.value, "rules": get_rules(tier)}
