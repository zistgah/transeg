# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""TTS adapter — Kokoro backend, CPU. Replaceable component."""
import base64, hashlib, os, sys
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock, backend_url

app = FastAPI(title="transeg-tts")
BACKEND = backend_url("kokoro", "http://kokoro-tts:8092/synthesize")

class VoiceReq(BaseModel):
    text: str
    voice: str = "default"

@app.get("/health")
def health(): return {"service": "tts", "status": "ok", "mock": is_mock(), "backend": BACKEND, "device": "cpu"}

@app.post("/voice")
async def voice(r: VoiceReq):
    if is_mock():
        fake = hashlib.sha256(r.text.encode()).digest() * 4
        return {"audio_b64": base64.b64encode(fake).decode(), "voice": r.voice,
                "sample_rate": 24000, "engine": "mock"}
    async with httpx.AsyncClient(timeout=300) as cx:
        resp = await cx.post(BACKEND, json={"text": r.text, "voice": r.voice}); resp.raise_for_status()
        return resp.json() | {"engine": "kokoro"}
