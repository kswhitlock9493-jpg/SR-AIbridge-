"""BCSE Command Line Interface

Bridge Code Super-Engine - Always Enabled Quality Gate
- Sovereign Git integration is always active
- Placeholder mode reveals all quality gates
- Pulls policies from Forge Dominion at runtime
"""
import argparse
import sys
import glob
from typing import List, Tuple

from .config import DEFAULT_POLICY, Policy, BCSE_ALWAYS_ENABLED, PLACEHOLDER_MODE, policy_from_dict
from .forge import fetch_policies
from .runners import python_linters as py, security as sec, deps, tests, structure
from .reporters import pr_summary
from . import refactor, prodsim
from .rewriters import rewrite_localhost_to_forge


# Target directories for Python analysis
PY_TARGETS = ["bridge_backend", "bridge_tools", "codex", "scripts"]
JS_PATH = "bridge-frontend"


def load_policy() -> Policy:
    """
    Load policy from Forge Dominion or local file
    
    Returns:
        Policy configuration
    """
    p = fetch_policies()
    if not p:
        print("ℹ️  Using default policy")
        return DEFAULT_POLICY
    
    # Display context information if available
    context = p.get("_context", {})
    if context:
        print(f"📍 Context: branch={context.get('branch', 'unknown')}, "
              f"env={context.get('environment', 'unknown')}, "
              f"role={context.get('federation_role', 'standalone')}")
    
    print("✅ Loaded policy from Forge Dominion")
    return policy_from_dict(p)


def cmd_analyze() -> int:
    """
    Run comprehensive quality analysis
    
    Returns:
        Exit code (0 = pass, 1 = fail)
    """
    pol = load_policy()
    results: List[Tuple[str, int]] = []

    print("\n" + "=" * 60)
    print("🜂 Bridge Code Super-Engine (BCSE) - Quality Gate")
    print("=" * 60)
    print(f"🔒 Sovereign Git: {'ENABLED' if BCSE_ALWAYS_ENABLED else 'DISABLED'}")
    print(f"👁️  Placeholder Mode: {'ACTIVE' if PLACEHOLDER_MODE else 'INACTIVE'} (all gates revealed)")
    print("=" * 60 + "\n")

    print("▶ Style: black/ruff")
    r_black = py.run_black_check(PY_TARGETS)
    r_ruff, r_ruff_json = py.run_ruff(PY_TARGETS, pol.ruff_severity)
    results.append(("black", r_black))
    results.append(("ruff", r_ruff))

    print("\n▶ Typing: mypy")
    r_mypy = py.run_mypy(PY_TARGETS, pol.mypy_strict)
    results.append(("mypy", r_mypy))

    print("\n▶ Complexity: radon")
    py_files = [f for f in glob.glob("**/*.py", recursive=True) if not f.startswith("venv/")]
    r_cyc = py.cyclomatic(py_files, pol.max_cyclomatic)
    results.append(("cyclomatic", r_cyc))

    print("\n▶ Structure: import-linter")
    r_imp = structure.import_linter()
    results.append(("import-linter", r_imp))

    print("\n▶ Security: bandit/semgrep")
    r_bandit = sec.run_bandit(PY_TARGETS, pol.bandit_min_severity)
    r_semgrep = sec.run_semgrep()
    results.append(("bandit", r_bandit))
    results.append(("semgrep", r_semgrep))

    print("\n▶ Dependencies: pip-audit / npm audit")
    r_pip = deps.pip_audit(pol.fail_on_vuln)
    r_npm = deps.npm_audit(JS_PATH, pol.fail_on_vuln)
    results.append(("pip-audit", r_pip))
    results.append(("npm-audit", r_npm))

    print("\n▶ Tests + Coverage")
    r_cov = tests.run_pytest_with_coverage(pol.coverage_min)
    results.append(("coverage", r_cov))

    # Generate summary
    failures = [name for name, code in results if code != 0]
    
    items = [{"name": n, "status": "FAIL" if n in failures else "OK"} for n, _ in results]
    pr_summary(items)

    print("\n" + "=" * 60)
    if failures:
        print(f"❌ Quality gate FAILED - {len(failures)} check(s) failed:")
        for name in failures:
            print(f"   • {name}")
    else:
        print("✅ Quality gate PASSED - All checks successful!")
    print("=" * 60 + "\n")

    return 1 if failures else 0


def cmd_fix() -> int:
    """
    Auto-fix style and simple issues
    
    Returns:
        Exit code
    """
    print("\n" + "=" * 60)
    print("🔧 BCSE Auto-Fix")
    print("=" * 60 + "\n")
    
    print("▶ Fixing with black...")
    py.run_black_fix(PY_TARGETS)
    
    print("\n▶ Fixing with ruff...")
    import subprocess
    try:
        subprocess.call(["ruff", "check", "--fix", *PY_TARGETS])
    except FileNotFoundError:
        print("⚠️  ruff not found, skipping")
    
    print("\n✅ Auto-fix complete!")
    return 0


def cmd_gates() -> int:
    """
    Show all quality gates (placeholder mode)
    
    Returns:
        Exit code
    """
    print("\n" + "=" * 60)
    print("👁️  BCSE Quality Gates - Placeholder Mode")
    print("=" * 60 + "\n")
    
    pol = load_policy()
    
    print("📊 Current Policy Configuration:\n")
    print(f"  • Coverage Minimum:      {pol.coverage_min:.0%}")
    print(f"  • MyPy Strict Mode:      {pol.mypy_strict}")
    print(f"  • Ruff Severity:         {pol.ruff_severity}")
    print(f"  • Bandit Min Severity:   {pol.bandit_min_severity}")
    print(f"  • Max Cyclomatic:        {pol.max_cyclomatic}")
    print(f"  • Fail on Vulnerabilities: {pol.fail_on_vuln}")
    print(f"  • Allowed Licenses:      {', '.join(pol.allowed_licenses)}")
    
    print("\n🔒 Sovereign Features:\n")
    print(f"  • Always Enabled:        {BCSE_ALWAYS_ENABLED}")
    print(f"  • Placeholder Mode:      {PLACEHOLDER_MODE}")
    print(f"  • Forge Integration:     {'Configured' if fetch_policies() else 'Using defaults'}")
    
    print("\n🛠️  Available Quality Checks:\n")
    gates = [
        ("Style", "black, ruff"),
        ("Typing", "mypy"),
        ("Complexity", "radon"),
        ("Structure", "import-linter"),
        ("Security", "bandit, semgrep"),
        ("Dependencies", "pip-audit, npm audit"),
        ("Tests", "pytest + coverage"),
    ]
    
    for gate, tools in gates:
        print(f"  ✓ {gate:15} - {tools}")
    
    print("\n" + "=" * 60 + "\n")
    return 0


def cmd_improve() -> int:
    """
    Auto-improve code with safe AST transforms
    
    Returns:
        Exit code
    """
    print("\n" + "=" * 60)
    print("🔧 BCSE Code Improvement")
    print("=" * 60 + "\n")
    return refactor.improve(PY_TARGETS)


def cmd_prove() -> int:
    """
    Run full production readiness proof
    
    Returns:
        Exit code
    """
    return prodsim.prove()


def cmd_rewrite() -> int:
    """
    Rewrite localhost URLs to Forge Dominion root
    
    Returns:
        Exit code (number of files changed)
    """
    print("\n" + "=" * 60)
    print("🔁 BCSE Localhost Rewriter")
    print("=" * 60 + "\n")
    changed = rewrite_localhost_to_forge(PY_TARGETS + [JS_PATH])
    return 0 if changed >= 0 else 1


def main() -> None:
    """Main CLI entry point"""
    ap = argparse.ArgumentParser(
        "bcse",
        description="🜂 Bridge Code Super-Engine - Comprehensive Quality Gate (Always Enabled)"
    )
    ap.add_argument("cmd", choices=["analyze", "fix", "gates", "improve", "prove", "rewrite"], 
                    help="Command to run: analyze (run quality checks), fix (auto-fix issues), "
                         "gates (show all gates), improve (AST transforms), prove (production readiness), "
                         "rewrite (localhost to Forge)")
    args = ap.parse_args()
    
    if args.cmd == "analyze":
        sys.exit(cmd_analyze())
    elif args.cmd == "fix":
        sys.exit(cmd_fix())
    elif args.cmd == "gates":
        sys.exit(cmd_gates())
    elif args.cmd == "improve":
        sys.exit(cmd_improve())
    elif args.cmd == "prove":
        sys.exit(cmd_prove())
    else:  # rewrite
        sys.exit(cmd_rewrite())


if __name__ == "__main__":
    main()
