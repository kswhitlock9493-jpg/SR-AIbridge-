from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

def test_tts_and_stt(tmp_path, monkeypatch):
    # TTS
    r = client.post("/engines/speech/tts", data={"text": "hello world"})
    assert r.status_code == 200
    data = r.json()["result"]
    assert "id" in data
    assert data["text"] == "hello world"

    # STT (stub)
    files = {"file": ("test.wav", b"RIFF....")}
    r = client.post("/engines/speech/stt", files=files)
    assert r.status_code == 200
    data = r.json()["result"]
    assert "text" in data
