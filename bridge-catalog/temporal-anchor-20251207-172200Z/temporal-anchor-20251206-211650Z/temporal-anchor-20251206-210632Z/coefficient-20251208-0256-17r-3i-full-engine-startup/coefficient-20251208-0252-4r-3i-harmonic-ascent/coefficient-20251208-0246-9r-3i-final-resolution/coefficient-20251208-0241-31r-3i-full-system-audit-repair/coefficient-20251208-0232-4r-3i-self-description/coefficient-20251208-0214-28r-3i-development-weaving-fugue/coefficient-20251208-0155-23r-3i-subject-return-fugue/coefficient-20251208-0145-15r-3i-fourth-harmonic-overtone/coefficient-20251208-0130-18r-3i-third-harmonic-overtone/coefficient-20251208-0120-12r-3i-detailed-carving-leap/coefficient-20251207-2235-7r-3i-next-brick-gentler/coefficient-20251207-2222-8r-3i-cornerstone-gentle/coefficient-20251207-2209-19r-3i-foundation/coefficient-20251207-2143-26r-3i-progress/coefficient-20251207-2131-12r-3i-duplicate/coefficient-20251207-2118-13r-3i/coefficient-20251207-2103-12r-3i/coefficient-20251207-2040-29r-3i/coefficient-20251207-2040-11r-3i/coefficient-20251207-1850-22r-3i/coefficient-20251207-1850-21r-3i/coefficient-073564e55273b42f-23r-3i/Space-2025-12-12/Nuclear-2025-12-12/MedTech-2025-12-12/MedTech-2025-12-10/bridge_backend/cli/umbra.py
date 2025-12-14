"""
Umbra CLI - Command-line interface for Umbra Lattice Memory
"""

import click
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@click.group()
def umbra():
    """Umbra Lattice Memory CLI"""
    pass


@umbra.group("lattice")
def lattice():
    """Umbra Lattice operations"""
    pass


@lattice.command("report")
@click.option("--since", default="24h", help="Time window (e.g., 7d, 24h, 1w)")
@click.option("--format", type=click.Choice(["mermaid", "summary", "both"]), default="mermaid", help="Output format")
def report(since, format):
    """Generate lattice report"""
    
    async def _run():
        try:
            from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
            
            lattice = UmbraLattice()
            await lattice.initialize()
            
            if format in ["mermaid", "both"]:
                click.echo("\n" + "="*60)
                click.echo(f"UMBRA LATTICE MEMORY - Last {since}")
                click.echo("="*60 + "\n")
                
                mermaid = await lattice.mermaid(since=since)
                click.echo(mermaid)
                click.echo()
            
            if format in ["summary", "both"]:
                click.echo("\n" + "="*60)
                click.echo("SUMMARY")
                click.echo("="*60 + "\n")
                
                summary = await lattice.get_summary(since=since)
                
                click.echo(f"Window: {summary.get('window')}")
                click.echo(f"Total Nodes: {summary.get('total_nodes', 0)}")
                click.echo(f"Total Edges: {summary.get('total_edges', 0)}")
                
                click.echo("\nNode Types:")
                for kind, count in summary.get('node_types', {}).items():
                    click.echo(f"  - {kind}: {count}")
                
                click.echo("\nEdge Types:")
                for kind, count in summary.get('edge_types', {}).items():
                    click.echo(f"  - {kind}: {count}")
                
                click.echo()
            
        except ImportError as e:
            click.echo(f"❌ Error: {e}", err=True)
            click.echo("Make sure you're in the correct directory.", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


@lattice.command("export")
@click.option("--since", default=None, help="Time window (e.g., 7d, 24h, 1w)")
def export(since):
    """Export lattice snapshot to JSON"""
    
    async def _run():
        try:
            from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
            
            lattice = UmbraLattice()
            await lattice.initialize()
            
            snapshot = await lattice.export_snapshot(since=since)
            
            click.echo(f"✅ Snapshot exported successfully")
            click.echo(f"   Nodes: {snapshot.summary.get('nodes', 0)}")
            click.echo(f"   Edges: {snapshot.summary.get('edges', 0)}")
            click.echo(f"   File: .umbra/snapshots/snapshot_{snapshot.ts.strftime('%Y%m%d_%H%M%S')}.json")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


@lattice.command("bloom")
def bloom():
    """Run bloom analysis to identify causal patterns"""
    
    async def _run():
        try:
            from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
            
            lattice = UmbraLattice()
            await lattice.initialize()
            
            results = await lattice.bloom()
            
            click.echo("\n" + "="*60)
            click.echo("UMBRA LATTICE BLOOM ANALYSIS")
            click.echo("="*60 + "\n")
            
            click.echo(f"Nodes Analyzed: {results.get('nodes_analyzed', 0)}")
            click.echo(f"Edges Analyzed: {results.get('edges_analyzed', 0)}")
            click.echo(f"Causal Chains: {results.get('causal_chains', 0)}")
            
            click.echo("\nTop Causes:")
            for cause in results.get('top_causes', []):
                click.echo(f"  - {cause['cause']}: {cause['frequency']} occurrences")
            
            click.echo("\nFrequent Fixes:")
            for fix in results.get('frequent_fixes', []):
                click.echo(f"  - {fix['fix']}: {fix['frequency']} applications")
            
            click.echo()
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


@lattice.command("stats")
def stats():
    """Show lattice storage statistics"""
    
    async def _run():
        try:
            from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
            
            lattice = UmbraLattice()
            await lattice.initialize()
            
            stats = await lattice.storage.get_stats()
            
            click.echo("\n" + "="*60)
            click.echo("UMBRA LATTICE STORAGE STATISTICS")
            click.echo("="*60 + "\n")
            
            click.echo(f"Total Nodes: {stats.get('nodes', 0)}")
            click.echo(f"  Certified: {stats.get('certified_nodes', 0)}")
            click.echo(f"\nTotal Edges: {stats.get('edges', 0)}")
            click.echo(f"  Certified: {stats.get('certified_edges', 0)}")
            click.echo(f"\nPending Certification: {stats.get('pending', 0)}")
            click.echo(f"Snapshots: {stats.get('snapshots', 0)}")
            click.echo(f"\nDatabase: {stats.get('db_path')}")
            click.echo()
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


if __name__ == "__main__":
    umbra()
