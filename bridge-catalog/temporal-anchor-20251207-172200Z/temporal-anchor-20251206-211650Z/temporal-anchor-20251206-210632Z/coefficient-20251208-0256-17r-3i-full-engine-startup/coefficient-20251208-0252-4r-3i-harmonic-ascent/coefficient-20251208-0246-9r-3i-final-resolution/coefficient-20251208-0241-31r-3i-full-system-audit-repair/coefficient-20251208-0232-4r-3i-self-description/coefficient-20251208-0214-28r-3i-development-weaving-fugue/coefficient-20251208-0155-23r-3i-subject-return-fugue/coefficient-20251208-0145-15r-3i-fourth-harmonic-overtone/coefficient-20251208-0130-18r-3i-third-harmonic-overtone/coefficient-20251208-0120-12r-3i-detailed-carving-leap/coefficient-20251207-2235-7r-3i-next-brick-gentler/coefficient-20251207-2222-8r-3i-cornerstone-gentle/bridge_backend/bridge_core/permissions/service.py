from enum import Enum
from typing import Dict, Any

class Tier(str, Enum):
    FREE = "free"
    CAPTAIN = "captain"
    ADMIRAL = "admiral"

TIER_RULES: Dict[Tier, Dict[str, Any]] = {
    Tier.FREE: {
        "autonomy_hours": 2,
        "features": ["basic-agents", "parser", "truth"],
    },
    Tier.CAPTAIN: {
        "autonomy_hours": 14,
        "features": ["agents", "indoctrination", "parser", "truth", "leviathan"],
    },
    Tier.ADMIRAL: {
        "autonomy_hours": 24,
        "features": ["agents", "indoctrination", "parser", "truth", "leviathan", "creativity", "screen"],
    },
}

def get_rules(tier: Tier) -> Dict[str, Any]:
    return TIER_RULES.get(tier, TIER_RULES[Tier.FREE])
