from fastapi import APIRouter, File, UploadFile, Form
from .stt import STTEngine
from .tts import TTSEngine

router = APIRouter(prefix="/engines/speech", tags=["speech"])
STT = STTEngine()
TTS = TTSEngine()

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    raw = await file.read()
    result = STT.transcribe(raw, filename=file.filename)
    return {"ok": True, "result": result}

@router.post("/tts")
async def text_to_speech(text: str = Form(...), voice: str = Form("default")):
    result = TTS.synthesize(text, voice=voice)
    return {"ok": True, "result": result}
