#!/usr/bin/env python3
"""
Quick validation script for Anchorhold Protocol v1.9.4
Verifies all key components without full server startup
"""
import sys
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent / "bridge_backend"))

print("🧪 SR-AIbridge v1.9.4 — Anchorhold Protocol Validation")
print("=" * 60)

# Test 1: Version check
print("\n1️⃣ Checking version...")
main_path = Path(__file__).parent / "bridge_backend" / "main.py"
content = main_path.read_text()
assert 'version="1.9.4"' in content
assert "Anchorhold" in content
print("✅ Version 1.9.4 with Anchorhold protocol confirmed")

# Test 2: Dynamic port binding
print("\n2️⃣ Checking dynamic port binding...")
assert 'port = int(os.environ.get("PORT", 8000))' in content
assert 'uvicorn.run("bridge_backend.main:app", host="0.0.0.0", port=port)' in content
print("✅ Dynamic port binding implemented")

# Test 3: Schema auto-sync
print("\n3️⃣ Checking automatic schema sync...")
assert "async def startup_event()" in content
assert "Base.metadata.create_all" in content
assert "Database schema synchronized successfully" in content
print("✅ Schema auto-sync on startup confirmed")

# Test 4: Heartbeat system
print("\n4️⃣ Checking heartbeat system...")
heartbeat_path = Path(__file__).parent / "bridge_backend" / "runtime" / "heartbeat.py"
assert heartbeat_path.exists()
heartbeat_content = heartbeat_path.read_text()
assert "async def bridge_heartbeat()" in heartbeat_content
assert "async def start_heartbeat()" in heartbeat_content
assert "HEARTBEAT_INTERVAL = 300" in heartbeat_content
print("✅ Heartbeat system with 5-minute interval confirmed")

# Test 5: CORS configuration
print("\n5️⃣ Checking CORS configuration...")
assert 'CORS_ALLOW_ORIGINS = os.getenv' in content
assert 'ALLOWED_ORIGINS' in content
assert "https://sr-aibridge.netlify.app" in content
assert "https://sr-aibridge.onrender.com" in content
print("✅ CORS with ALLOWED_ORIGINS configured")

# Test 6: httpx dependency
print("\n6️⃣ Checking httpx dependency...")
req_path = Path(__file__).parent / "bridge_backend" / "requirements.txt"
req_content = req_path.read_text()
assert "httpx>=0.24.0" in req_content
print("✅ httpx dependency added")

# Test 7: Auto-repair branding
print("\n7️⃣ Checking auto-repair branding...")
auto_repair_path = Path(__file__).parent / "bridge_backend" / "runtime" / "auto_repair.py"
auto_repair_content = auto_repair_path.read_text()
assert "SR-AIbridge v1.9.4" in auto_repair_content
assert "Anchorhold Protocol" in auto_repair_content
print("✅ Auto-repair with Anchorhold branding confirmed")

# Test 8: render.yaml configuration
print("\n8️⃣ Checking render.yaml configuration...")
render_path = Path(__file__).parent / "render.yaml"
render_content = render_path.read_text()
assert "PORT" in render_content
assert "sync: false" in render_content
assert "python -m bridge_backend.main" in render_content
assert "ALLOWED_ORIGINS" in render_content
print("✅ render.yaml with dynamic PORT and direct execution confirmed")

# Test 9: netlify.toml configuration
print("\n9️⃣ Checking netlify.toml configuration...")
netlify_path = Path(__file__).parent / "netlify.toml"
netlify_content = netlify_path.read_text()
assert "/api/*" in netlify_content
assert "https://sr-aibridge.onrender.com" in netlify_content
assert "VITE_BRIDGE_BASE" in netlify_content
assert "VITE_PUBLIC_API_BASE" in netlify_content
print("✅ netlify.toml with API proxy and environment configured")

# Test 10: Documentation
print("\n🔟 Checking documentation...")
protocol_doc = Path(__file__).parent / "docs" / "ANCHORHOLD_PROTOCOL.md"
quick_ref = Path(__file__).parent / "docs" / "ANCHORHOLD_QUICK_REF.md"
assert protocol_doc.exists()
assert quick_ref.exists()
protocol_content = protocol_doc.read_text()
assert "Dynamic Port Binding" in protocol_content
assert "Automatic Table Creation" in protocol_content
assert "Heartbeat Ping System" in protocol_content
assert "Netlify ↔ Render Header Alignment" in protocol_content
print("✅ Complete documentation confirmed")

print("\n" + "=" * 60)
print("🎉 ALL VALIDATION CHECKS PASSED!")
print("✅ SR-AIbridge v1.9.4 — Anchorhold Protocol is fully implemented")
print("\n📋 Summary:")
print("   • Version: 1.9.4")
print("   • Protocol: Anchorhold")
print("   • Dynamic port binding: ✓")
print("   • Schema auto-sync: ✓")
print("   • Heartbeat system: ✓")
print("   • CORS configuration: ✓")
print("   • Infrastructure config: ✓")
print("   • Documentation: ✓")
print("\n🚀 Ready for deployment!")
