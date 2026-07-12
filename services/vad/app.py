# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""VAD adapter — Silero backend, CPU. Replaceable component."""
import base64, os, sys
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock, backend_url

app = FastAPI(title="transeg-vad")
BACKEND = backend_url("silero", "http://silero-vad:8091/vad")

class VadReq(BaseModel):
    audio_b64: str

@app.get("/health")
def health(): return {"service": "vad", "status": "ok", "mock": is_mock(), "backend": BACKEND, "device": "cpu"}

@app.post("/vad")
async def vad(r: VadReq):
    if is_mock():
        n = len(base64.b64decode(r.audio_b64 or b""))
        return {"speech": n > 0, "segments": ([[0.0, round(n / 16000, 3)]] if n else []), "engine": "mock"}
    async with httpx.AsyncClient(timeout=60) as cx:
        resp = await cx.post(BACKEND, json={"audio": r.audio_b64}); resp.raise_for_status()
        return resp.json() | {"engine": "silero"}
