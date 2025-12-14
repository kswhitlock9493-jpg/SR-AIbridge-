"""
Test Total-Stack Triage Mesh (v1.8.3)
Verifies all workflows, scripts, and documentation are in place
"""

import pytest
import json
import pathlib
import subprocess
import os


class TestWorkflows:
    """Test that all required workflow files exist and are valid"""
    
    def test_build_triage_netlify_workflow(self):
        """Test that build_triage_netlify.yml workflow exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        workflow_path = root / ".github" / "workflows" / "build_triage_netlify.yml"
        
        assert workflow_path.exists(), "build_triage_netlify.yml should exist"
        
        # Parse YAML to ensure it's valid
        import yaml
        workflow = yaml.safe_load(workflow_path.read_text())
        
        assert workflow["name"] == "Build Triage (Netlify)"
        assert "jobs" in workflow
        assert "build-triage" in workflow["jobs"]
        # YAML parser converts 'on' to True
        triggers = workflow.get("on") or workflow.get(True)
        assert triggers["schedule"][0]["cron"] == "15 */6 * * *"
    
    def test_runtime_triage_render_workflow(self):
        """Test that runtime_triage_render.yml workflow exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        workflow_path = root / ".github" / "workflows" / "runtime_triage_render.yml"
        
        assert workflow_path.exists(), "runtime_triage_render.yml should exist"
        
        import yaml
        workflow = yaml.safe_load(workflow_path.read_text())
        
        assert workflow["name"] == "Runtime Triage (Render)"
        assert "jobs" in workflow
        assert "runtime-triage" in workflow["jobs"]
        triggers = workflow.get("on") or workflow.get(True)
        assert triggers["schedule"][0]["cron"] == "45 */6 * * *"
    
    def test_deploy_gate_workflow(self):
        """Test that deploy_gate.yml workflow exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        workflow_path = root / ".github" / "workflows" / "deploy_gate.yml"
        
        assert workflow_path.exists(), "deploy_gate.yml should exist"
        
        import yaml
        workflow = yaml.safe_load(workflow_path.read_text())
        
        assert workflow["name"] == "Deploy Gate"
        assert "jobs" in workflow
        assert "gate" in workflow["jobs"]
        triggers = workflow.get("on") or workflow.get(True)
        assert "main" in triggers["push"]["branches"]
    
    def test_endpoint_api_sweep_workflow(self):
        """Test that endpoint_api_sweep.yml workflow exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        workflow_path = root / ".github" / "workflows" / "endpoint_api_sweep.yml"
        
        assert workflow_path.exists(), "endpoint_api_sweep.yml should exist"
        
        import yaml
        workflow = yaml.safe_load(workflow_path.read_text())
        
        assert workflow["name"] == "Endpoints & Hooks Sweep"
        assert "jobs" in workflow
        assert "sweep" in workflow["jobs"]
        triggers = workflow.get("on") or workflow.get(True)
        assert triggers["schedule"][0]["cron"] == "5 */12 * * *"
    
    def test_environment_parity_guard_workflow(self):
        """Test that environment_parity_guard.yml workflow exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        workflow_path = root / ".github" / "workflows" / "environment_parity_guard.yml"
        
        assert workflow_path.exists(), "environment_parity_guard.yml should exist"
        
        import yaml
        workflow = yaml.safe_load(workflow_path.read_text())
        
        assert workflow["name"] == "Environment Parity Guard"
        assert "jobs" in workflow
        assert "env-parity" in workflow["jobs"]
        triggers = workflow.get("on") or workflow.get(True)
        assert triggers["schedule"][0]["cron"] == "0 2 * * *"
    
    def test_netlify_config_guard_workflow(self):
        """Test that netlify_config_guard.yml workflow exists (v1.8.3)"""
        root = pathlib.Path(__file__).resolve().parents[2]
        workflow_path = root / ".github" / "workflows" / "netlify_config_guard.yml"
        
        assert workflow_path.exists(), "netlify_config_guard.yml should exist"
        
        import yaml
        workflow = yaml.safe_load(workflow_path.read_text())
        
        assert workflow["name"] == "Netlify Config Guard & Egress Sync (v1.8.3)"
        assert "jobs" in workflow
        assert "guard" in workflow["jobs"]
        triggers = workflow.get("on") or workflow.get(True)
        assert "main" in triggers["push"]["branches"]


class TestScripts:
    """Test that all required scripts exist and have valid syntax"""
    
    def test_net_helper_script(self):
        """Test that _net.py exists and has expected functions"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "_net.py"
        
        assert script_path.exists(), "_net.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def dns_warmup" in code
        assert "def http" in code
    
    def test_build_triage_netlify_script(self):
        """Test that build_triage_netlify.py exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "build_triage_netlify.py"
        
        assert script_path.exists(), "build_triage_netlify.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def normalize_netlify_toml" in code
        assert "def check_functions_dependency" in code
        assert "def generate_report" in code
    
    def test_runtime_triage_render_script(self):
        """Test that runtime_triage_render.py exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "runtime_triage_render.py"
        
        assert script_path.exists(), "runtime_triage_render.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def main" in code
        assert "from _net import http, dns_warmup" in code
    
    def test_endpoint_api_sweep_script(self):
        """Test that endpoint_api_sweep.py exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "endpoint_api_sweep.py"
        
        assert script_path.exists(), "endpoint_api_sweep.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def routes_backend" in code
        assert "def calls_frontend" in code
    
    def test_env_parity_guard_script(self):
        """Test that env_parity_guard.py exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "env_parity_guard.py"
        
        assert script_path.exists(), "env_parity_guard.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def load_env_files" in code
        assert "CANON" in code
    
    def test_deploy_triage_script(self):
        """Test that deploy_triage.py exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "deploy_triage.py"
        
        assert script_path.exists(), "deploy_triage.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def readj" in code
        assert "total_stack_report.json" in code
    
    def test_netlify_config_triage_script(self):
        """Test that netlify_config_triage.py exists (v1.8.3)"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "netlify_config_triage.py"
        
        assert script_path.exists(), "netlify_config_triage.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def validate_toml" in code
        assert "def normalize_redirects" in code
        assert "def ensure_headers" in code
        assert "netlify_config_report.json" in code
    
    def test_egress_sync_check_script(self):
        """Test that egress_sync_check.py exists (v1.8.3)"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "egress_sync_check.py"
        
        assert script_path.exists(), "egress_sync_check.py should exist"
        
        code = script_path.read_text()
        compile(code, str(script_path), 'exec')
        
        assert "def probe" in code
        assert "api.netlify.com" in code
        assert "api.render.com" in code


class TestScriptExecution:
    """Test that scripts can execute without errors"""
    
    def test_endpoint_api_sweep_runs(self):
        """Test that endpoint_api_sweep.py executes"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "endpoint_api_sweep.py"
        
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=str(root),
            capture_output=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        report_path = root / "bridge_backend" / "diagnostics" / "endpoint_api_sweep.json"
        assert report_path.exists()
        
        report = json.loads(report_path.read_text())
        assert "backend_routes" in report
        assert "frontend_calls" in report
        assert "missing_from_frontend" in report
        assert "missing_from_backend" in report
    
    def test_env_parity_guard_runs(self):
        """Test that env_parity_guard.py executes"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "env_parity_guard.py"
        
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=str(root),
            capture_output=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        report_path = root / "bridge_backend" / "diagnostics" / "env_parity_report.json"
        assert report_path.exists()
        
        report = json.loads(report_path.read_text())
        assert "canonical" in report
        assert "files" in report
        assert "missing" in report
    
    def test_deploy_triage_runs(self):
        """Test that deploy_triage.py executes"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "deploy_triage.py"
        
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=str(root),
            capture_output=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        report_path = root / "bridge_backend" / "diagnostics" / "total_stack_report.json"
        assert report_path.exists()
        
        report = json.loads(report_path.read_text())
        assert "federation" in report
        assert "build" in report
        assert "runtime" in report
        assert "endpoints" in report
        assert "env" in report
    
    def test_netlify_config_triage_runs(self):
        """Test that netlify_config_triage.py executes (v1.8.3)"""
        root = pathlib.Path(__file__).resolve().parents[2]
        script_path = root / ".github" / "scripts" / "netlify_config_triage.py"
        
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=str(root),
            capture_output=True,
            timeout=30
        )
        
        assert result.returncode == 0
        
        report_path = root / "bridge_backend" / "diagnostics" / "netlify_config_report.json"
        assert report_path.exists()
        
        report = json.loads(report_path.read_text())
        assert "toml_issues" in report
        assert "redirects_fixes" in report
        assert "headers_created" in report
        assert "ok" in report


class TestDocumentation:
    """Test that all documentation exists"""
    
    def test_total_stack_triage_doc(self):
        """Test that TOTAL_STACK_TRIAGE.md exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        doc_path = root / "docs" / "TOTAL_STACK_TRIAGE.md"
        
        assert doc_path.exists(), "TOTAL_STACK_TRIAGE.md should exist"
        
        content = doc_path.read_text()
        
        # Check for key sections
        assert "Total-Stack Triage Mesh" in content
        assert "Signals" in content
        assert "Build Triage (Netlify)" in content
        assert "Runtime Triage (Render)" in content
        assert "Deploy Gate" in content
        assert "Endpoints & Hooks Sweep" in content
        assert "Environment Parity Guard" in content
        assert "Escalation" in content
        assert "Post-Merge Checklist" in content
    
    def test_badges_doc(self):
        """Test that BADGES.md exists"""
        root = pathlib.Path(__file__).resolve().parents[2]
        doc_path = root / "docs" / "BADGES.md"
        
        assert doc_path.exists(), "BADGES.md should exist"
        
        content = doc_path.read_text()
        
        # Check for badge examples
        assert "Bridge Health" in content
        assert "Build Triage" in content
        assert "Runtime Triage" in content
        assert "Env Parity" in content
        assert "shields.io" in content.lower()


class TestReportStructure:
    """Test that generated reports have the correct structure"""
    
    def test_endpoint_api_sweep_report_structure(self):
        """Test endpoint_api_sweep.json structure"""
        root = pathlib.Path(__file__).resolve().parents[2]
        
        # Generate fresh report
        script_path = root / ".github" / "scripts" / "endpoint_api_sweep.py"
        subprocess.run(["python3", str(script_path)], cwd=str(root), check=True)
        
        report_path = root / "bridge_backend" / "diagnostics" / "endpoint_api_sweep.json"
        report = json.loads(report_path.read_text())
        
        assert isinstance(report["backend_routes"], list)
        assert isinstance(report["frontend_calls"], list)
        assert isinstance(report["missing_from_frontend"], list)
        assert isinstance(report["missing_from_backend"], list)
    
    def test_env_parity_report_structure(self):
        """Test env_parity_report.json structure"""
        root = pathlib.Path(__file__).resolve().parents[2]
        
        # Generate fresh report
        script_path = root / ".github" / "scripts" / "env_parity_guard.py"
        subprocess.run(["python3", str(script_path)], cwd=str(root), check=True)
        
        report_path = root / "bridge_backend" / "diagnostics" / "env_parity_report.json"
        report = json.loads(report_path.read_text())
        
        assert isinstance(report["canonical"], list)
        assert isinstance(report["files"], dict)
        assert isinstance(report["missing"], dict)
        
        # Check canonical variables
        canonical = report["canonical"]
        assert "BRIDGE_API_URL" in canonical
        assert "CASCADE_MODE" in canonical
        assert "VAULT_URL" in canonical
    
    def test_total_stack_report_structure(self):
        """Test total_stack_report.json structure"""
        root = pathlib.Path(__file__).resolve().parents[2]
        
        # Generate fresh report
        script_path = root / ".github" / "scripts" / "deploy_triage.py"
        subprocess.run(["python3", str(script_path)], cwd=str(root), check=True)
        
        report_path = root / "bridge_backend" / "diagnostics" / "total_stack_report.json"
        report = json.loads(report_path.read_text())
        
        assert "federation" in report
        assert "build" in report
        assert "runtime" in report
        assert "endpoints" in report
        assert "env" in report
    
    def test_netlify_config_report_structure(self):
        """Test netlify_config_report.json structure (v1.8.3)"""
        root = pathlib.Path(__file__).resolve().parents[2]
        
        # Generate fresh report
        script_path = root / ".github" / "scripts" / "netlify_config_triage.py"
        subprocess.run(["python3", str(script_path)], cwd=str(root), check=True)
        
        report_path = root / "bridge_backend" / "diagnostics" / "netlify_config_report.json"
        report = json.loads(report_path.read_text())
        
        assert isinstance(report["toml_issues"], list)
        assert isinstance(report["redirects_fixes"], list)
        assert isinstance(report["headers_created"], bool)
        assert isinstance(report["ok"], bool)


class TestIntegration:
    """Test that components integrate correctly"""
    
    def test_all_workflows_have_artifact_upload(self):
        """Verify all triage workflows upload artifacts"""
        root = pathlib.Path(__file__).resolve().parents[2]
        
        workflows = [
            "build_triage_netlify.yml",
            "runtime_triage_render.yml",
            "endpoint_api_sweep.yml",
            "environment_parity_guard.yml"
        ]
        
        import yaml
        for workflow_name in workflows:
            workflow_path = root / ".github" / "workflows" / workflow_name
            workflow = yaml.safe_load(workflow_path.read_text())
            
            # Find upload-artifact step
            workflow_text = workflow_path.read_text()
            assert "actions/upload-artifact@v4" in workflow_text, \
                f"{workflow_name} should upload artifacts"
    
    def test_deploy_gate_downloads_all_artifacts(self):
        """Verify Deploy Gate downloads all required artifacts"""
        root = pathlib.Path(__file__).resolve().parents[2]
        
        workflow_path = root / ".github" / "workflows" / "deploy_gate.yml"
        workflow_text = workflow_path.read_text()
        
        # Check for artifact downloads
        assert "federation_repair_report" in workflow_text
        assert "build_triage_report" in workflow_text
        assert "runtime_triage_report" in workflow_text
        assert "actions/download-artifact@v4" in workflow_text
    
    def test_diagnostics_directory_structure(self):
        """Verify diagnostics directory exists and can be written to"""
        root = pathlib.Path(__file__).resolve().parents[2]
        diag_dir = root / "bridge_backend" / "diagnostics"
        
        assert diag_dir.exists()
        assert diag_dir.is_dir()
        
        # Test write permissions
        test_file = diag_dir / ".test"
        test_file.write_text("test")
        assert test_file.exists()
        test_file.unlink()
