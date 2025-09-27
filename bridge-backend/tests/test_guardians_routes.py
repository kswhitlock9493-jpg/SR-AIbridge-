from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_guardians():
    r = client.get("/guardians")
    assert r.status_code == 200
    data = r.json()
    assert "guardians" in data
    assert any(g["name"] == "System" for g in data["guardians"])

def test_guardian_status():
    r = client.get("/guardians/System")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "System"
    assert body["state"] == "online"

def test_guardian_not_found():
    r = client.get("/guardians/NotReal")
    assert r.status_code == 404