from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_init_and_sign_and_verify():
    # init
    r = client.post("/custody/init")
    assert r.status_code == 200
    verify_key = r.json()["verify_key"]
    assert verify_key

    # sign
    r = client.post("/custody/sign", json={"data": "hello"})
    assert r.status_code == 200
    sig = r.json()["signature"]

    # verify
    r = client.post("/custody/verify", json={"data": "hello", "signature": sig})
    assert r.status_code == 200
    assert r.json()["valid"] is True

def test_verify_fail():
    # make sure verify fails with wrong sig
    client.post("/custody/init")
    r = client.post("/custody/verify", json={"data": "hello", "signature": "bad"})
    assert r.status_code == 200
    assert r.json()["valid"] is False