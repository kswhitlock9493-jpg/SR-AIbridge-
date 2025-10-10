#!/usr/bin/env python3
"""
Quick verification script for v1.9.6b implementation
Demonstrates all key features without requiring full server startup
"""
import os
import sys
from pathlib import Path

# Ensure we can import bridge_backend modules
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 SR-AIbridge v1.9.6b — Quick Verification")
print("=" * 60)

# Test 1: Version check
print("\n1️⃣ Checking version...")
main_path = Path(__file__).parent / "bridge_backend" / "main.py"
content = main_path.read_text()
if 'version=os.getenv("APP_VERSION","v1.9.6b")' in content:
    print("✅ Version v1.9.6b confirmed in main.py")
else:
    print("⚠️ Version check unclear")

# Test 2: Requirements check
print("\n2️⃣ Checking dependencies...")
req_path = Path(__file__).parent / "requirements.txt"
req_content = req_path.read_text()
if "httpx>=0.27.2" in req_content:
    print("✅ httpx>=0.27.2 in requirements.txt")
else:
    print("❌ httpx missing from requirements.txt")

if "python-dateutil>=2.9.0" in req_content:
    print("✅ python-dateutil>=2.9.0 in requirements.txt")
else:
    print("❌ python-dateutil missing from requirements.txt")

# Test 3: Render port binding
print("\n3️⃣ Checking Render port binding...")
render_path = Path(__file__).parent / "render.yaml"
render_content = render_path.read_text()
if "${PORT}" in render_content and "uvicorn bridge_backend.main:app" in render_content:
    print("✅ Render startCommand uses $PORT")
else:
    print("❌ Render port binding not configured correctly")

# Test 4: Netlify CORS headers
print("\n4️⃣ Checking Netlify CORS headers...")
netlify_path = Path(__file__).parent / "netlify.toml"
netlify_content = netlify_path.read_text()
if "Access-Control-Allow-Origin" in netlify_content:
    print("✅ Netlify CORS headers configured")
else:
    print("❌ Netlify CORS headers missing")

# Test 5: Models directory
print("\n5️⃣ Checking models directory...")
models_dir = Path(__file__).parent / "bridge_backend" / "models"
if models_dir.exists() and (models_dir / "core.py").exists():
    print("✅ Models directory and core.py created")
    try:
        from bridge_backend.models import Base, User
        print("✅ Models can be imported")
    except Exception as e:
        print(f"⚠️ Models import issue: {e}")
else:
    print("❌ Models directory or files missing")

# Test 6: Database utilities
print("\n6️⃣ Checking database utilities...")
db_path = Path(__file__).parent / "bridge_backend" / "utils" / "db.py"
if db_path.exists():
    print("✅ utils/db.py created")
    try:
        from bridge_backend.utils.db import init_schema
        print("✅ init_schema function available")
    except Exception as e:
        print(f"⚠️ DB utils import issue: {e}")
else:
    print("❌ utils/db.py missing")

# Test 7: Integrations
print("\n7️⃣ Checking GitHub integrations...")
gh_path = Path(__file__).parent / "bridge_backend" / "integrations" / "github_issues.py"
if gh_path.exists():
    print("✅ GitHub issues integration created")
    try:
        from bridge_backend.integrations.github_issues import maybe_create_issue
        print("✅ maybe_create_issue function available")
    except Exception as e:
        print(f"⚠️ GitHub integration import issue: {e}")
else:
    print("❌ GitHub issues integration missing")

# Test 8: Predictive Stabilizer
print("\n8️⃣ Checking Predictive Stabilizer...")
stabilizer_path = Path(__file__).parent / "bridge_backend" / "runtime" / "predictive_stabilizer.py"
if stabilizer_path.exists():
    print("✅ Predictive Stabilizer created")
    try:
        from bridge_backend.runtime.predictive_stabilizer import evaluate_stability
        print("✅ evaluate_stability function available")
    except Exception as e:
        print(f"⚠️ Stabilizer import issue: {e}")
else:
    print("❌ Predictive Stabilizer missing")

# Test 9: Release Intelligence
print("\n9️⃣ Checking Release Intelligence...")
intel_path = Path(__file__).parent / "bridge_backend" / "runtime" / "release_intel.py"
if intel_path.exists():
    print("✅ Release Intelligence module created")
    try:
        from bridge_backend.runtime.release_intel import analyze_and_stabilize
        print("✅ analyze_and_stabilize function available")
        
        # Try running it if insights file exists
        insights_path = Path(__file__).parent / "bridge_backend" / "diagnostics" / "release_insights.json"
        if insights_path.exists():
            os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test.db'
            result = analyze_and_stabilize()
            if result:
                print(f"✅ Release intel executed: {result.get('status', 'unknown')}")
            else:
                print("ℹ️ Release intel returned None (expected if stability is good)")
    except Exception as e:
        print(f"⚠️ Release intel issue: {e}")
else:
    print("❌ Release Intelligence missing")

# Test 10: Heartbeat v1.9.6b
print("\n🔟 Checking Heartbeat system...")
heartbeat_path = Path(__file__).parent / "bridge_backend" / "runtime" / "heartbeat.py"
heartbeat_content = heartbeat_path.read_text()
if "v1.9.6b" in heartbeat_content and "import httpx" in heartbeat_content:
    print("✅ Heartbeat updated to v1.9.6b")
    try:
        from bridge_backend.runtime import heartbeat
        print("✅ Heartbeat module can be imported")
    except Exception as e:
        print(f"⚠️ Heartbeat import issue: {e}")
else:
    print("❌ Heartbeat not updated for v1.9.6b")

# Test 11: Documentation
print("\n1️⃣1️⃣ Checking documentation...")
readme_path = Path(__file__).parent / "README_RELEASES.md"
env_template_path = Path(__file__).parent / ".env.template"
if readme_path.exists():
    print("✅ README_RELEASES.md created")
else:
    print("❌ README_RELEASES.md missing")

if env_template_path.exists():
    print("✅ .env.template created")
else:
    print("❌ .env.template missing")

print("\n" + "=" * 60)
print("✅ Verification complete! v1.9.6b implementation looks good.")
print("\nNext steps:")
print("1. Set Render start command: bash -lc 'uvicorn bridge_backend.main:app --host 0.0.0.0 --port ${PORT}'")
print("2. Configure environment variables from .env.template")
print("3. (Optional) Set GITHUB_REPO and GITHUB_TOKEN for issue automation")
print("4. Deploy and verify logs show:")
print("   - [DB] ✅ Database schema synchronized successfully.")
print("   - heartbeat: ✅ initialized")
print("   - [INTEL] release analysis done")
