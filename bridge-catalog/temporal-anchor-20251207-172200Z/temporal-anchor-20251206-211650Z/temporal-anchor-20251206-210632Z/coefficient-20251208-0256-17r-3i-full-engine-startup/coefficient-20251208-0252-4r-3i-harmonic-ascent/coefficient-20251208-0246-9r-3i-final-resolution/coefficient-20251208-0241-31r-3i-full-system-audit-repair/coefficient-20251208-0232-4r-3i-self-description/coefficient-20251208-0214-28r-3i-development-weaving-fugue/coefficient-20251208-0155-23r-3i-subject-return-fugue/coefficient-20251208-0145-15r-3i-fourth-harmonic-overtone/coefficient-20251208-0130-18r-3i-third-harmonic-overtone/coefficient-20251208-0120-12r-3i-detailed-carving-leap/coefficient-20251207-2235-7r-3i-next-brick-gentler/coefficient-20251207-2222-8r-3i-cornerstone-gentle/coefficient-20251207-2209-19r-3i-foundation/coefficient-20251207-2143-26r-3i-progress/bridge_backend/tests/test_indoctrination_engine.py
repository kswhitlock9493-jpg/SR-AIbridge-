from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_onboard_and_certify():
    r = client.post("/engines/indoctrination/onboard",
        json={"name":"Athena","role":"analyst","specialties":["intel","docs"]})
    assert r.status_code==200
    aid = r.json()["id"]

    c = client.post(f"/engines/indoctrination/{aid}/certify",
        json={"doctrine":"intel-v1"})
    assert c.status_code==200
    cert = c.json()
    assert "seal" in cert

def test_revoke():
    r = client.post("/engines/indoctrination/onboard",
        json={"name":"Hermes","role":"messenger","specialties":[]})
    aid = r.json()["id"]
    v = client.post(f"/engines/indoctrination/{aid}/revoke",
        json={"reason":"drift"})
    assert v.status_code==200
    assert v.json()["status"]=="revoked"
