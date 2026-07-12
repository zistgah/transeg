# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""ASR adapter — Whisper.cpp backend, CPU (CONTRACT §4). Replaceable component."""
import base64, hashlib, os, sys
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock, backend_url

app = FastAPI(title="transeg-speech")
BACKEND = backend_url("whisper", "http://whisper-cpp:8090/inference")

class SpeechReq(BaseModel):
    audio_b64: str
    lang: str = "auto"

@app.get("/health")
def health(): return {"service": "speech", "status": "ok", "mock": is_mock(), "backend": BACKEND, "device": "cpu"}

@app.post("/speech")
async def speech(r: SpeechReq):
    if is_mock():
        digest = hashlib.sha256(base64.b64decode(r.audio_b64 or b"")).hexdigest()[:8]
        return {"text": f"[mock-transcript {digest}]", "lang": r.lang, "engine": "mock"}
    async with httpx.AsyncClient(timeout=120) as cx:
        resp = await cx.post(BACKEND, json={"audio": r.audio_b64, "language": r.lang})
        resp.raise_for_status()
        return {"text": resp.json().get("text", ""), "lang": r.lang, "engine": "whisper.cpp"}
