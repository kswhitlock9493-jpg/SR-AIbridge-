"""
Umbra Triage Mesh CLI
Command-line interface for Umbra unified triage system
"""

import click
import asyncio
import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@click.group()
def umbractl():
    """Umbra Triage Mesh CLI"""
    pass


@umbractl.command("run")
@click.option("--heal", is_flag=True, help="Execute heal plans")
@click.option("--report", is_flag=True, help="Generate and save report")
@click.option("--timeout", default=90, help="Timeout in seconds")
def run(heal, report, timeout):
    """Run a one-shot triage sweep"""
    
    async def _run():
        try:
            from bridge_backend.engines.umbra.core import UmbraTriageCore
            from bridge_backend.engines.umbra.healers import UmbraHealers
            
            core = UmbraTriageCore()
            healers = UmbraHealers()
            
            if not core.enabled:
                click.echo("❌ Umbra is disabled (set UMBRA_ENABLED=true)", err=True)
                sys.exit(1)
            
            click.echo("🧠 Running Umbra triage sweep...")
            
            # Run sweep
            sweep_report = await core.run_sweep(timeout=timeout)
            
            click.echo(f"✅ Sweep complete: {sweep_report.summary}")
            click.echo(f"   Tickets opened: {sweep_report.tickets_opened}")
            click.echo(f"   Critical: {sweep_report.critical_count}")
            click.echo(f"   Warnings: {sweep_report.warning_count}")
            click.echo(f"   Plans generated: {sweep_report.heal_plans_generated}")
            
            # Execute healing if requested
            if heal:
                if not healers.allow_heal:
                    click.echo("⚠️  Healing disabled (set UMBRA_ALLOW_HEAL=true)")
                else:
                    click.echo("\n🩹 Executing heal plans...")
                    
                    healed_count = 0
                    failed_count = 0
                    
                    for ticket in sweep_report.tickets:
                        if ticket.status == "open" and ticket.heal_plan:
                            click.echo(f"   Healing {ticket.ticket_id}...")
                            
                            result = await healers.execute_heal_plan(ticket.heal_plan, ticket)
                            
                            if result.get("status") == "success":
                                healed_count += 1
                                click.echo(f"   ✅ {ticket.ticket_id} healed")
                            else:
                                failed_count += 1
                                click.echo(f"   ❌ {ticket.ticket_id} failed: {result.get('reason', 'unknown')}")
                    
                    click.echo(f"\n✅ Healing complete: {healed_count} healed, {failed_count} failed")
                    
                    # Update report
                    sweep_report.tickets_healed = healed_count
                    sweep_report.tickets_failed = failed_count
                    sweep_report.heal_plans_applied = healed_count
            
            # Save report if requested
            if report:
                await core._save_report(sweep_report)
                click.echo(f"\n📄 Report saved to bridge_backend/logs/umbra_reports/{sweep_report.report_id}.json")
            
        except ImportError as e:
            click.echo(f"❌ Error: {e}", err=True)
            click.echo("Make sure you're in the correct directory.", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


@umbractl.command("tickets")
@click.option("--status", type=click.Choice(["open", "in_progress", "healed", "closed", "failed"]), help="Filter by status")
def tickets(status):
    """List triage tickets"""
    
    async def _run():
        try:
            from bridge_backend.engines.umbra.core import UmbraTriageCore
            
            core = UmbraTriageCore()
            
            ticket_list = core.list_tickets(status=status)
            
            if not ticket_list:
                click.echo("No tickets found")
                return
            
            click.echo(f"\n{'ID':<25} {'Kind':<10} {'Source':<10} {'Severity':<10} {'Status':<15}")
            click.echo("-" * 70)
            
            for ticket in ticket_list:
                click.echo(f"{ticket.ticket_id:<25} {ticket.kind:<10} {ticket.source:<10} {ticket.severity:<10} {ticket.status:<15}")
            
            click.echo(f"\nTotal: {len(ticket_list)} tickets")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


@umbractl.command("ticket")
@click.argument("ticket_id")
@click.option("--action", type=click.Choice(["close", "heal"]), help="Action to perform")
def ticket(ticket_id, action):
    """View or act on a specific ticket"""
    
    async def _run():
        try:
            from bridge_backend.engines.umbra.core import UmbraTriageCore
            from bridge_backend.engines.umbra.healers import UmbraHealers
            
            core = UmbraTriageCore()
            healers = UmbraHealers()
            
            tkt = core.get_ticket(ticket_id)
            if not tkt:
                click.echo(f"❌ Ticket not found: {ticket_id}", err=True)
                sys.exit(1)
            
            if not action:
                # Display ticket details
                click.echo(f"\nTicket: {tkt.ticket_id}")
                click.echo(f"Kind: {tkt.kind}")
                click.echo(f"Source: {tkt.source}")
                click.echo(f"Severity: {tkt.severity}")
                click.echo(f"Status: {tkt.status}")
                click.echo(f"Created: {tkt.created_at}")
                click.echo(f"\nIncidents: {len(tkt.incidents)}")
                for inc in tkt.incidents:
                    click.echo(f"  - {inc.incident_id}: {inc.message}")
                
                if tkt.heal_plan:
                    click.echo(f"\nHeal Plan: {tkt.heal_plan.plan_id}")
                    click.echo(f"Actions: {len(tkt.heal_plan.actions)}")
                    for act in tkt.heal_plan.actions:
                        click.echo(f"  - {act.action_type} -> {act.target}")
            
            elif action == "close":
                from datetime import datetime
                tkt.status = "closed"
                tkt.closed_at = datetime.utcnow()
                click.echo(f"✅ Ticket closed: {ticket_id}")
            
            elif action == "heal":
                if not tkt.heal_plan:
                    plan = await core.classify_and_decide(ticket_id)
                    if not plan:
                        click.echo(f"❌ Unable to generate heal plan", err=True)
                        sys.exit(1)
                
                click.echo(f"🩹 Executing heal plan for {ticket_id}...")
                result = await healers.execute_heal_plan(tkt.heal_plan, tkt)
                
                if result.get("status") == "success":
                    click.echo(f"✅ Heal plan executed successfully")
                else:
                    click.echo(f"❌ Heal plan failed: {result.get('reason', 'unknown')}", err=True)
                    sys.exit(1)
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


@umbractl.command("report")
@click.option("--format", type=click.Choice(["json", "summary"]), default="summary", help="Output format")
@click.option("--latest", is_flag=True, help="Show latest report only")
def report_cmd(format, latest):
    """View triage reports"""
    
    async def _run():
        try:
            from bridge_backend.engines.umbra.core import UmbraTriageCore
            
            core = UmbraTriageCore()
            
            if latest:
                rep = core.get_latest_report()
                if not rep:
                    click.echo("No reports available")
                    return
                reports = [rep]
            else:
                reports = core.reports
            
            if format == "json":
                for rep in reports:
                    click.echo(json.dumps(rep.dict(), indent=2, default=str))
            else:
                for rep in reports:
                    click.echo(f"\nReport: {rep.report_id}")
                    click.echo(f"Timestamp: {rep.run_timestamp}")
                    click.echo(f"Duration: {rep.duration_seconds:.2f}s")
                    click.echo(f"Summary: {rep.summary}")
                    click.echo(f"\nStats:")
                    click.echo(f"  Tickets opened: {rep.tickets_opened}")
                    click.echo(f"  Tickets healed: {rep.tickets_healed}")
                    click.echo(f"  Tickets failed: {rep.tickets_failed}")
                    click.echo(f"  Critical issues: {rep.critical_count}")
                    click.echo(f"  Warnings: {rep.warning_count}")
                    click.echo(f"  Heal plans generated: {rep.heal_plans_generated}")
                    click.echo(f"  Heal plans applied: {rep.heal_plans_applied}")
                    click.echo("")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_run())


if __name__ == "__main__":
    umbractl()
