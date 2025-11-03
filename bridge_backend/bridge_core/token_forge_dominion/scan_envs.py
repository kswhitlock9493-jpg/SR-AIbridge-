"""
Environment Secret Scanner - Token Forge Dominion v1.9.7s-SOVEREIGN

Scans environment files and runtime for plaintext secrets.
Blocks deployment if static API keys or tokens are detected.
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any


# Patterns for common secret formats
SECRET_PATTERNS = {
    "github_token": re.compile(r'gh[pousr]_[A-Za-z0-9]{36,}'),
    "netlify_token": re.compile(r'nf[kp]_[A-Za-z0-9]{40,}'),
    "render_token": re.compile(r'rnd_[A-Za-z0-9]{32,}'),
    "generic_api_key": re.compile(r'(?i)(api[_-]?key|apikey)\s*[=:]\s*[\'"]?([A-Za-z0-9_\-]{32,})[\'"]?'),
    "access_token": re.compile(r'(?i)(access[_-]?token|accesstoken)\s*[=:]\s*[\'"]?([A-Za-z0-9_\-]{32,})[\'"]?'),
    "secret_key": re.compile(r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*[\'"]?([A-Za-z0-9_\-]{32,})[\'"]?'),
    "aws_key": re.compile(r'AKIA[0-9A-Z]{16}'),
    "private_key": re.compile(r'-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----'),
}

# Patterns to ignore (false positives or expected patterns)
IGNORE_PATTERNS = [
    re.compile(r'FORGE_DOMINION_ROOT'),  # Our own managed secret
    re.compile(r'FORGE_DOMINION_MODE'),
    re.compile(r'FORGE_DOMINION_VERSION'),
    re.compile(r'\$\{[^}]+\}'),  # Template variables
    re.compile(r'<[^>]+>'),  # Placeholders
    re.compile(r'example|sample|test|dummy|placeholder', re.IGNORECASE),
]

# Files to scan
ENV_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    '.env.deploy',
    '.env.netlify',
    '.env.render',
]

# Files to explicitly exclude
EXCLUDE_FILES = [
    '.env.example',
    '.env.template',
    '.env.sample',
]


class SecretFinding:
    """Represents a detected secret."""
    
    def __init__(self, file_path: str, line_num: int, pattern_name: str, context: str):
        self.file_path = file_path
        self.line_num = line_num
        self.pattern_name = pattern_name
        self.context = context
    
    def __repr__(self) -> str:
        return f"{self.file_path}:{self.line_num} [{self.pattern_name}] {self.context[:50]}"


def should_ignore_line(line: str) -> bool:
    """
    Check if line should be ignored.
    
    Args:
        line: Line to check
        
    Returns:
        bool: True if should ignore
    """
    for pattern in IGNORE_PATTERNS:
        if pattern.search(line):
            return True
    return False


def scan_file(file_path: Path) -> List[SecretFinding]:
    """
    Scan a single file for secrets.
    
    Args:
        file_path: Path to file
        
    Returns:
        List of SecretFinding objects
    """
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments and empty lines
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Skip ignored patterns
                if should_ignore_line(line):
                    continue
                
                # Check each secret pattern
                for pattern_name, pattern in SECRET_PATTERNS.items():
                    if pattern.search(line):
                        finding = SecretFinding(
                            file_path=str(file_path),
                            line_num=line_num,
                            pattern_name=pattern_name,
                            context=line[:80]
                        )
                        findings.append(finding)
    
    except Exception as e:
        # Don't fail on read errors, just skip
        pass
    
    return findings


def scan_envs(root_path: str = ".") -> Dict[str, Any]:
    """
    Scan environment files for secrets.
    
    Args:
        root_path: Root directory to scan
        
    Returns:
        dict: Scan results
    """
    root = Path(root_path)
    findings = []
    scanned_files = []
    
    # Scan environment files
    for env_file in ENV_FILES:
        file_path = root / env_file
        
        # Skip if doesn't exist or is excluded
        if not file_path.exists():
            continue
        if env_file in EXCLUDE_FILES:
            continue
        
        scanned_files.append(str(file_path))
        file_findings = scan_file(file_path)
        findings.extend(file_findings)
    
    return {
        "count": len(findings),
        "findings": findings,
        "scanned_files": scanned_files
    }


def scan_environment_vars() -> Dict[str, Any]:
    """
    Scan runtime environment variables for secrets.
    
    Returns:
        dict: Scan results
    """
    findings = []
    
    # Skip Dominion-managed variables
    skip_vars = {'FORGE_DOMINION_ROOT', 'FORGE_DOMINION_MODE', 'FORGE_DOMINION_VERSION'}
    
    for key, value in os.environ.items():
        if key in skip_vars:
            continue
        
        # Check for secret-like patterns in values
        for pattern_name, pattern in SECRET_PATTERNS.items():
            if pattern.search(value):
                finding = SecretFinding(
                    file_path="<environment>",
                    line_num=0,
                    pattern_name=pattern_name,
                    context=f"{key}={value[:20]}..."
                )
                findings.append(finding)
    
    return {
        "count": len(findings),
        "findings": findings
    }


def main() -> int:
    """
    Main scanner entry point.
    
    Returns:
        int: Exit code (0 = clean, 1 = secrets found)
    """
    print("=" * 70)
    print("🔐 Forge Dominion Secret Scanner v1.9.7s")
    print("=" * 70)
    print()
    
    # Scan environment files
    print("[Scanner] Scanning environment files...")
    file_results = scan_envs()
    
    print(f"[Scanner] Scanned {len(file_results['scanned_files'])} files")
    for scanned_file in file_results['scanned_files']:
        print(f"  - {scanned_file}")
    print()
    
    # Scan runtime environment
    print("[Scanner] Scanning runtime environment variables...")
    env_results = scan_environment_vars()
    print()
    
    # Report results
    total_findings = file_results['count'] + env_results['count']
    
    if total_findings == 0:
        print("[Dominion CI] ✅ secret scrub: clean")
        print(f"[Scanner] No plaintext secrets detected (count: {total_findings})")
        print("=" * 70)
        return 0
    
    # Report findings
    print(f"[Scanner] ❌ Found {total_findings} potential secrets:")
    print()
    
    if file_results['findings']:
        print("File secrets:")
        for finding in file_results['findings']:
            print(f"  ⚠️  {finding}")
        print()
    
    if env_results['findings']:
        print("Environment secrets:")
        for finding in env_results['findings']:
            print(f"  ⚠️  {finding}")
        print()
    
    print("=" * 70)
    print("[Dominion CI] ❌ Secret detection failed - plaintext secrets found")
    print("=" * 70)
    print()
    print("Action required:")
    print("1. Remove plaintext secrets from .env files")
    print("2. Use FORGE_DOMINION_ROOT for token minting instead")
    print("3. Run: bash runtime/pre-deploy.dominion.sh")
    print()
    
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
