#!/usr/bin/env python3
"""
Sovereign Orchestrator
Master controller that brings together all sovereignty systems
"""

import os
import sys
import json
from typing import Dict, Any
from datetime import datetime, timezone
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager
from bridge_backend.tools.firewall_sovereignty.network_resilience import NetworkResilienceLayer
from bridge_backend.tools.firewall_sovereignty.validation_sovereignty import ValidationSovereignty
from bridge_backend.tools.firewall_sovereignty.script_execution import ScriptExecutionSovereignty


class SovereignOrchestrator:
    """
    Sovereign Orchestrator
    
    Master controller that coordinates:
    - Firewall configuration management
    - Network resilience and health
    - Validation sovereignty
    - Script execution authority
    """
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        print("👑 SOVEREIGN ORCHESTRATOR - INITIALIZING")
        print("=" * 70)
        print(f"Session ID: {self.session_id}")
        print(f"Workspace: {self.workspace_root}")
        print("=" * 70)
        
        # Initialize sovereign systems
        self.firewall_manager = FirewallConfigManager()
        self.network_resilience = NetworkResilienceLayer()
        self.validator = ValidationSovereignty()
        self.script_executor = ScriptExecutionSovereignty(str(self.workspace_root))
        
        self.execution_summary = {
            "session_id": self.session_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "systems_initialized": 4,
            "operations_performed": []
        }
    
    def execute_sovereignty_protocol(self) -> Dict[str, Any]:
        """
        Execute the complete sovereignty protocol
        
        Returns:
            Comprehensive sovereignty report
        """
        print("\n🚀 EXECUTING SOVEREIGNTY PROTOCOL")
        print("=" * 70)
        
        results = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress",
            "systems": {}
        }
        
        # Step 1: Firewall Configuration Sovereignty
        print("\n1️⃣  FIREWALL CONFIGURATION SOVEREIGNTY")
        print("-" * 70)
        firewall_result = self._execute_firewall_sovereignty()
        results["systems"]["firewall"] = firewall_result
        self.execution_summary["operations_performed"].append("firewall_sovereignty")
        
        # Step 2: Network Resilience Sovereignty
        print("\n2️⃣  NETWORK RESILIENCE SOVEREIGNTY")
        print("-" * 70)
        network_result = self._execute_network_sovereignty()
        results["systems"]["network"] = network_result
        self.execution_summary["operations_performed"].append("network_sovereignty")
        
        # Step 3: Validation Sovereignty
        print("\n3️⃣  VALIDATION SOVEREIGNTY")
        print("-" * 70)
        validation_result = self._execute_validation_sovereignty()
        results["systems"]["validation"] = validation_result
        self.execution_summary["operations_performed"].append("validation_sovereignty")
        
        # Step 4: Script Execution Sovereignty
        print("\n4️⃣  SCRIPT EXECUTION SOVEREIGNTY")
        print("-" * 70)
        script_result = self._execute_script_sovereignty()
        results["systems"]["script_execution"] = script_result
        self.execution_summary["operations_performed"].append("script_execution_sovereignty")
        
        # Step 5: Generate Comprehensive Report
        print("\n5️⃣  GENERATING SOVEREIGNTY REPORT")
        print("-" * 70)
        results["status"] = "completed"
        results["summary"] = self._generate_summary(results)
        
        # Save report
        self._save_sovereignty_report(results)
        
        return results
    
    def _execute_firewall_sovereignty(self) -> Dict[str, Any]:
        """Execute firewall configuration sovereignty"""
        print("  → Validating firewall configuration...")
        validation = self.firewall_manager.validate_firewall_config()
        
        print("  → Generating firewall summary...")
        summary = self.firewall_manager.generate_summary()
        
        print("  → Exporting firewall configuration...")
        export_file = str(self.workspace_root / "network_policies" / "firewall_config_export.json")
        self.firewall_manager.export_config(export_file)
        
        result = {
            "status": "completed",
            "validation": validation,
            "summary": summary,
            "export_file": export_file
        }
        
        print(f"  ✅ Firewall sovereignty: {summary['total_allowed_domains']} domains managed")
        return result
    
    def _execute_network_sovereignty(self) -> Dict[str, Any]:
        """Execute network resilience sovereignty"""
        print("  → Testing critical network endpoints...")
        
        critical_endpoints = [
            "https://api.netlify.com",
            "https://api.github.com",
            "https://pypi.org",
            "https://registry.npmjs.org"
        ]
        
        health_results = self.network_resilience.batch_health_check(critical_endpoints)
        
        print("  → Exporting network health report...")
        export_file = str(self.workspace_root / "bridge_backend" / "diagnostics" / "network_health_report.json")
        self.network_resilience.export_health_report(export_file, health_results)
        
        stats = self.network_resilience.get_connection_stats()
        
        result = {
            "status": "completed",
            "health_check": health_results,
            "statistics": stats,
            "export_file": export_file
        }
        
        print(f"  ✅ Network sovereignty: {health_results['successful']}/{health_results['total_checked']} endpoints healthy")
        return result
    
    def _execute_validation_sovereignty(self) -> Dict[str, Any]:
        """Execute validation sovereignty"""
        print("  → Performing comprehensive validation...")
        
        config_paths = {
            "netlify_config": str(self.workspace_root / "netlify.toml"),
            "network_policies": str(self.workspace_root / "network_policies" / "sovereign_allowlist.yaml"),
            "headers_file": str(self.workspace_root / "_headers")
        }
        
        validation_results = self.validator.validate_all(config_paths)
        
        print("  → Exporting validation report...")
        export_file = str(self.workspace_root / "bridge_backend" / "diagnostics" / "validation_report.json")
        self.validator.export_validation_report(export_file, validation_results)
        
        result = {
            "status": "completed",
            "validation_results": validation_results,
            "export_file": export_file
        }
        
        status_text = "✅ VALID" if validation_results["overall_valid"] else "⚠️  WARNINGS"
        print(f"  {status_text} Validation sovereignty: {len(validation_results['validations'])} systems checked")
        return result
    
    def _execute_script_sovereignty(self) -> Dict[str, Any]:
        """Execute script execution sovereignty"""
        print("  → Validating execution environment...")
        
        python_deps = self.script_executor.validate_dependencies("python")
        node_deps = self.script_executor.validate_dependencies("node")
        
        print("  → Checking script health...")
        critical_scripts = [
            str(self.workspace_root / "scripts" / "firewall_watchdog.py"),
            str(self.workspace_root / "scripts" / "validate_netlify.py"),
            str(self.workspace_root / "scripts" / "netlify_build.sh")
        ]
        
        health_results = self.script_executor.health_check_scripts(critical_scripts)
        
        print("  → Exporting execution report...")
        export_file = str(self.workspace_root / "bridge_backend" / "diagnostics" / "script_execution_report.json")
        self.script_executor.export_execution_report(export_file)
        
        result = {
            "status": "completed",
            "dependencies": {
                "python": python_deps,
                "node": node_deps
            },
            "script_health": health_results,
            "export_file": export_file
        }
        
        print(f"  ✅ Script sovereignty: {health_results['accessible']}/{health_results['total_scripts']} scripts accessible")
        return result
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of sovereignty protocol"""
        summary = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "systems_executed": len(results.get("systems", {})),
            "overall_status": "healthy",
            "recommendations": []
        }
        
        # Analyze results and generate recommendations
        systems = results.get("systems", {})
        
        # Check firewall
        if systems.get("firewall", {}).get("validation", {}).get("valid") == False:
            summary["recommendations"].append("Review and fix firewall configuration errors")
            summary["overall_status"] = "needs_attention"
        
        # Check network
        network_health = systems.get("network", {}).get("health_check", {})
        if network_health.get("failed", 0) > 0:
            summary["recommendations"].append(f"Investigate {network_health['failed']} failed network endpoints")
            summary["overall_status"] = "needs_attention"
        
        # Check validation
        if not systems.get("validation", {}).get("validation_results", {}).get("overall_valid", True):
            summary["recommendations"].append("Address configuration validation warnings")
        
        # Check scripts
        script_health = systems.get("script_execution", {}).get("script_health", {})
        if script_health.get("inaccessible", 0) > 0:
            summary["recommendations"].append(f"Fix {script_health['inaccessible']} inaccessible scripts")
            summary["overall_status"] = "needs_attention"
        
        if not summary["recommendations"]:
            summary["recommendations"].append("All systems operating at sovereign level - no action required")
        
        return summary
    
    def _save_sovereignty_report(self, results: Dict[str, Any]) -> None:
        """Save comprehensive sovereignty report"""
        report_dir = self.workspace_root / "bridge_backend" / "diagnostics"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"sovereignty_report_{self.session_id}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Sovereignty report saved: {report_file}")
        
        # Also save as latest
        latest_file = report_dir / "sovereignty_report_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Latest report: {latest_file}")
    
    def display_final_summary(self, results: Dict[str, Any]) -> None:
        """Display final sovereignty summary"""
        summary = results.get("summary", {})
        
        print("\n" + "=" * 70)
        print("👑 SOVEREIGNTY PROTOCOL EXECUTION COMPLETE")
        print("=" * 70)
        
        print(f"\nSession ID: {summary['session_id']}")
        print(f"Systems Executed: {summary['systems_executed']}")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        
        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(summary.get("recommendations", []), 1):
            print(f"  {i}. {rec}")
        
        print("\n🎯 SOVEREIGNTY METRICS:")
        
        # Firewall metrics
        firewall = results["systems"]["firewall"]
        print(f"  🛡️  Firewall: {firewall['summary']['total_allowed_domains']} domains under sovereign control")
        
        # Network metrics
        network = results["systems"]["network"]
        health = network["health_check"]
        print(f"  🌐 Network: {health['successful']}/{health['total_checked']} endpoints operational")
        
        # Validation metrics
        validation = results["systems"]["validation"]
        val_count = len(validation["validation_results"]["validations"])
        print(f"  🔒 Validation: {val_count} systems validated")
        
        # Script metrics
        scripts = results["systems"]["script_execution"]
        script_health = scripts["script_health"]
        print(f"  ⚙️  Scripts: {script_health['accessible']}/{script_health['total_scripts']} scripts ready")
        
        print("\n" + "=" * 70)
        print("✅ SOVEREIGN AUTHORITY ESTABLISHED")
        print("=" * 70)


def main():
    """Main execution for sovereign orchestrator"""
    orchestrator = SovereignOrchestrator()
    
    # Execute sovereignty protocol
    results = orchestrator.execute_sovereignty_protocol()
    
    # Display final summary
    orchestrator.display_final_summary(results)
    
    return results


if __name__ == "__main__":
    main()
