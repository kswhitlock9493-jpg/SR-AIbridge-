from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_screen_lifecycle_and_overlay(tmp_path, monkeypatch):
    # redirect vault to temp if you like; the engine uses static paths but this is fine for smoke.
    r = client.post("/engines/screen/start", json={
        "mode": "share",
        "project": "nova",
        "captain": "Kyle",
        "permissions": {"observe": ["screen"], "annotate": ["overlay"]}
    })
    assert r.status_code == 200
    sid = r.json()["session"]["id"]

    # go live
    r = client.post(f"/engines/screen/{sid}/state", json={"state":"live"})
    assert r.status_code == 200 and r.json()["session"]["state"] == "live"

    # signaling placeholders
    r = client.post(f"/engines/screen/{sid}/offer", json={"sdp":{"type":"offer","sdp":"..."}})
    assert r.status_code == 200
    r = client.post(f"/engines/screen/{sid}/answer", json={"sdp":{"type":"answer","sdp":"..."}})
    assert r.status_code == 200
    r = client.post(f"/engines/screen/{sid}/ice", json={"candidates":[{"candidate":"a"}, {"candidate":"b"}]})
    assert r.status_code == 200 and r.json()["count"] == 2

    # overlay
    r = client.post(f"/engines/screen/{sid}/overlay", json={
        "widgets":[
            {"type":"badge","text":"LIVE","x":12,"y":12},
            {"type":"highlight","rect":[100,160,240,80],"color":"#ff0"}
        ]
    })
    assert r.status_code == 200 and r.json()["ok"] is True

    # list & stop
    r = client.get("/engines/screen/list?project=nova&state=live")
    assert r.status_code == 200 and any(s["id"]==sid for s in r.json()["sessions"])
    r = client.post(f"/engines/screen/{sid}/state", json={"state":"stopped"})
    assert r.status_code == 200 and r.json()["session"]["state"] == "stopped"
