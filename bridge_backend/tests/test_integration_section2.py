from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_section2_endpoints_exist():
    # Minimal ping checks for all Section 2 endpoints
    urls = [
        "/missions",
        "/vault/logs",
        "/fleet",
        "/armada/status",
        "/guardians",
        "/health",
        "/status",
    ]
    for u in urls:
        r = client.get(u)
        assert r.status_code == 200, f"{u} failed"
        assert r.headers["content-type"].startswith("application/json")