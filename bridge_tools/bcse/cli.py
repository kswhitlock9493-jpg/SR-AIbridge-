"""BCSE Command Line Interface"""
import argparse
import sys
import glob
from typing import List, Tuple

from .config import DEFAULT_POLICY, Policy
from .forge import fetch_policies
from .runners import python_linters as py, security as sec, deps, tests, structure
from .reporters import pr_summary


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
    
    print("✅ Loaded policy from Forge Dominion")
    return Policy(
        coverage_min=p.get("coverage_min", DEFAULT_POLICY.coverage_min),
        mypy_strict=p.get("mypy_strict", DEFAULT_POLICY.mypy_strict),
        ruff_severity=p.get("ruff_severity", DEFAULT_POLICY.ruff_severity),
        bandit_min_severity=p.get("bandit_min_severity", DEFAULT_POLICY.bandit_min_severity),
        max_cyclomatic=p.get("max_cyclomatic", DEFAULT_POLICY.max_cyclomatic),
        fail_on_vuln=p.get("fail_on_vuln", DEFAULT_POLICY.fail_on_vuln),
        allowed_licenses=p.get("allowed_licenses", DEFAULT_POLICY.allowed_licenses),
    )


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


def main() -> None:
    """Main CLI entry point"""
    ap = argparse.ArgumentParser(
        "bcse",
        description="🜂 Bridge Code Super-Engine - Comprehensive Quality Gate"
    )
    ap.add_argument("cmd", choices=["analyze", "fix"], help="Command to run")
    args = ap.parse_args()
    
    if args.cmd == "analyze":
        sys.exit(cmd_analyze())
    else:
        sys.exit(cmd_fix())


if __name__ == "__main__":
    main()
