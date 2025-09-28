from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_guardians_list_and_detail():
    r = client.get("/guardians")
    assert r.status_code == 200
    data = r.json()
    assert "guardians" in data
    assert any(g["id"] == "prim" for g in data["guardians"])

    r = client.get("/guardians/prim")
    assert r.status_code == 200
    detail = r.json()
    assert detail["id"] == "prim"

def test_missing_guardian():
    r = client.get("/guardians/notreal")
    assert r.status_code == 200
    assert "error" in r.json()