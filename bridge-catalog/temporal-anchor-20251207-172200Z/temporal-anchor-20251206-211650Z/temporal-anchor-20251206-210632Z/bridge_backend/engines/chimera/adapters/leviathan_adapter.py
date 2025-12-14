"""Leviathan Adapter for Chimera Oracle"""

from typing import Dict, Any
from ...leviathan.simulator import LeviathanSimulator


class LeviathanAdapter:
    """Adapter connecting Chimera to Leviathan Simulator"""
    
    def __init__(self):
        self.simulator = LeviathanSimulator()
    
    async def simulate(self, ref: Dict[str, Any]) -> Dict[str, Any]:
        """Run build simulation"""
        return await self.simulator.run(ref)
