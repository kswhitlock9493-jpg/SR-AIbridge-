"""
deployctl - Predictive Deployment CLI
Single-command deployment with Chimera Oracle
"""

import asyncio
import json
import click
from ..engines.chimera.core import ChimeraOracle


@click.group()
def deployctl():
    """Chimera Oracle deployment control"""
    pass


@deployctl.command("predictive")
@click.option("--ref", default="HEAD", help="Git reference (commit SHA, branch, tag)")
def predictive(ref):
    """Execute predictive deployment pipeline"""
    async def _run():
        c = ChimeraOracle()
        res = await c.run({"ref": ref})
        print(json.dumps(res, indent=2))
    
    asyncio.run(_run())


if __name__ == "__main__":
    deployctl()
