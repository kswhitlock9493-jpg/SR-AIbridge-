#!/usr/bin/env python3
"""
Script Execution Sovereignty
Comprehensive management and control of script execution environment
"""

import os
import sys
import subprocess
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from pathlib import Path


class ScriptExecutionSovereignty:
    """
    Sovereign Script Execution Management
    
    Provides control over:
    - Script execution environment
    - Dependency resolution
    - Automated health checks
    - Error recovery mechanisms
    """
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.execution_log = []
        self.environment_config = self._detect_environment()
    
    def _detect_environment(self) -> Dict[str, Any]:
        """Detect and configure execution environment"""
        config = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_path": sys.executable,
            "workspace_root": str(self.workspace_root),
            "platform": sys.platform,
            "path": os.environ.get("PATH", ""),
            "detected_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Detect Node.js
        try:
            node_version = subprocess.check_output(
                ["node", "--version"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            config["node_version"] = node_version
        except (subprocess.CalledProcessError, FileNotFoundError):
            config["node_version"] = None
        
        # Detect npm
        try:
            npm_version = subprocess.check_output(
                ["npm", "--version"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            config["npm_version"] = npm_version
        except (subprocess.CalledProcessError, FileNotFoundError):
            config["npm_version"] = None
        
        return config
    
    def validate_dependencies(self, dep_type: str = "python") -> Dict[str, Any]:
        """
        Validate that required dependencies are installed
        
        Args:
            dep_type: Type of dependencies to check ('python', 'node', 'system')
        
        Returns:
            Validation results
        """
        validation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": dep_type,
            "valid": True,
            "missing": [],
            "installed": []
        }
        
        if dep_type == "python":
            # Check Python dependencies
            requirements_file = self.workspace_root / "requirements.txt"
            if requirements_file.exists():
                try:
                    import importlib.util
                    
                    # Read requirements
                    with open(requirements_file, 'r') as f:
                        requirements = [
                            line.strip().split('>=')[0].split('==')[0].split('[')[0]
                            for line in f
                            if line.strip() and not line.startswith('#')
                        ]
                    
                    # Check each requirement using importlib
                    for req in requirements:
                        package_name = req.replace('-', '_')
                        spec = importlib.util.find_spec(package_name)
                        if spec is not None:
                            validation["installed"].append(req)
                        else:
                            validation["missing"].append(req)
                            validation["valid"] = False
                
                except Exception as e:
                    validation["error"] = str(e)
                    validation["valid"] = False
        
        elif dep_type == "node":
            # Check Node.js dependencies
            package_json = self.workspace_root / "bridge-frontend" / "package.json"
            if package_json.exists():
                node_modules = self.workspace_root / "bridge-frontend" / "node_modules"
                if not node_modules.exists():
                    validation["missing"].append("node_modules (run npm install)")
                    validation["valid"] = False
                else:
                    validation["installed"].append("node_modules")
        
        return validation
    
    def execute_script(
        self,
        script_path: str,
        interpreter: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a script with proper environment and error handling
        
        Args:
            script_path: Path to script to execute
            interpreter: Script interpreter (python3, node, bash, etc.)
            args: Arguments to pass to script
            env: Environment variables
        
        Returns:
            Execution results
        """
        script_path = Path(script_path)
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Auto-detect interpreter if not provided
        if not interpreter:
            if script_path.suffix == '.py':
                interpreter = 'python3'
            elif script_path.suffix == '.js':
                interpreter = 'node'
            elif script_path.suffix == '.sh':
                interpreter = 'bash'
            else:
                interpreter = str(script_path)  # Try executing directly
        
        # Build command
        cmd = [interpreter, str(script_path)]
        if args:
            cmd.extend(args)
        
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        
        # Execute
        try:
            start_time = datetime.now(timezone.utc)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=exec_env,
                timeout=300,  # 5 minute timeout
                cwd=self.workspace_root
            )
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            execution_result = {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "script": str(script_path),
                "interpreter": interpreter
            }
            
            # Log execution
            self.execution_log.append({
                "script": str(script_path),
                "success": execution_result["success"],
                "timestamp": execution_result["timestamp"]
            })
            
            return execution_result
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Script execution timeout (5 minutes)",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script": str(script_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "script": str(script_path)
            }
    
    def health_check_scripts(self, script_paths: List[str]) -> Dict[str, Any]:
        """
        Perform health checks on multiple scripts
        
        Args:
            script_paths: List of script paths to check
        
        Returns:
            Health check results
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_scripts": len(script_paths),
            "accessible": 0,
            "inaccessible": 0,
            "details": []
        }
        
        for script_path in script_paths:
            path = Path(script_path)
            
            check = {
                "script": str(script_path),
                "exists": path.exists(),
                "executable": path.exists() and os.access(path, os.X_OK),
                "readable": path.exists() and os.access(path, os.R_OK)
            }
            
            if check["exists"] and check["readable"]:
                results["accessible"] += 1
            else:
                results["inaccessible"] += 1
            
            results["details"].append(check)
        
        return results
    
    def setup_environment_variables(self, env_config: Dict[str, str]) -> None:
        """
        Setup environment variables for script execution
        
        Args:
            env_config: Dictionary of environment variables
        """
        for key, value in env_config.items():
            os.environ[key] = value
    
    def export_execution_report(self, output_file: str) -> None:
        """Export script execution report"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "environment": self.environment_config,
            "execution_log": self.execution_log,
            "total_executions": len(self.execution_log),
            "successful_executions": sum(1 for log in self.execution_log if log["success"]),
            "failed_executions": sum(1 for log in self.execution_log if not log["success"])
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def auto_resolve_dependencies(self) -> Dict[str, Any]:
        """
        Automatically resolve missing dependencies
        
        Returns:
            Resolution results
        """
        resolution = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resolved": [],
            "failed": []
        }
        
        # Check Python dependencies
        python_deps = self.validate_dependencies("python")
        if not python_deps["valid"] and python_deps.get("missing"):
            # Install missing Python dependencies
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install"] + python_deps["missing"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                resolution["resolved"].extend(python_deps["missing"])
            except subprocess.CalledProcessError:
                resolution["failed"].extend(python_deps["missing"])
        
        # Check Node dependencies
        node_deps = self.validate_dependencies("node")
        if not node_deps["valid"]:
            # Install Node dependencies
            frontend_dir = self.workspace_root / "bridge-frontend"
            if frontend_dir.exists():
                try:
                    subprocess.check_call(
                        ["npm", "ci"],
                        cwd=frontend_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    resolution["resolved"].append("node_modules")
                except subprocess.CalledProcessError:
                    resolution["failed"].append("node_modules")
        
        return resolution


def main():
    """Main execution for script sovereignty"""
    print("⚙️  Script Execution Sovereignty System")
    print("=" * 70)
    
    executor = ScriptExecutionSovereignty()
    
    # Display environment
    print("\n🔍 Execution Environment:")
    print(f"  Python: {executor.environment_config['python_version']}")
    print(f"  Node: {executor.environment_config.get('node_version', 'Not found')}")
    print(f"  npm: {executor.environment_config.get('npm_version', 'Not found')}")
    print(f"  Platform: {executor.environment_config['platform']}")
    
    # Validate dependencies
    print("\n📦 Validating Dependencies...")
    python_deps = executor.validate_dependencies("python")
    print(f"  Python Dependencies: {'✅ Valid' if python_deps['valid'] else '❌ Missing packages'}")
    if python_deps.get("missing"):
        print(f"    Missing: {', '.join(python_deps['missing'][:5])}")
    
    node_deps = executor.validate_dependencies("node")
    print(f"  Node Dependencies: {'✅ Valid' if node_deps['valid'] else '❌ Missing packages'}")
    
    # Health check critical scripts
    critical_scripts = [
        "scripts/firewall_watchdog.py",
        "scripts/validate_netlify.py",
        "scripts/netlify_build.sh"
    ]
    
    print("\n🏥 Script Health Check:")
    health_results = executor.health_check_scripts(critical_scripts)
    print(f"  Total Scripts: {health_results['total_scripts']}")
    print(f"  Accessible: {health_results['accessible']}")
    print(f"  Inaccessible: {health_results['inaccessible']}")
    
    for detail in health_results['details']:
        status = "✅" if detail['exists'] and detail['readable'] else "❌"
        print(f"  {status} {detail['script']}")
    
    # Export report
    output_file = "bridge_backend/diagnostics/script_execution_report.json"
    executor.export_execution_report(output_file)
    print(f"\n💾 Execution report exported to: {output_file}")
    
    print("\n" + "=" * 70)
    print("✅ Script Execution Sovereignty Check Complete")


if __name__ == "__main__":
    main()
