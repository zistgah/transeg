# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""Avatar adapter — FasterLivePortrait, the SOLE GPU tenant (CONTRACT §4).

Everything else runs CPU so the RTX 3050's 4 GB VRAM belongs to facial animation.
"""
import base64, hashlib, os, sys
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock, backend_url

app = FastAPI(title="transeg-avatar")
BACKEND = backend_url("liveportrait", "http://faster-liveportrait:8093/render")

class RenderReq(BaseModel):
    audio_b64: str
    source_image_b64: str = ""     # Stage 0 (face) artifact, gated by staggered upload
    fps: int = 25

@app.get("/health")
def health(): return {"service": "avatar", "status": "ok", "mock": is_mock(),
                      "backend": BACKEND, "device": "cuda", "gpu_sole_tenant": True}

@app.post("/avatar/render")
async def render(r: RenderReq):
    if is_mock():
        h = hashlib.sha256((r.audio_b64 + r.source_image_b64).encode()).hexdigest()
        return {"video_b64": base64.b64encode(h.encode()).decode(),
                "frames": max(1, len(r.audio_b64) // 4096), "fps": r.fps, "engine": "mock"}
    async with httpx.AsyncClient(timeout=600) as cx:
        resp = await cx.post(BACKEND, json=r.model_dump()); resp.raise_for_status()
        return resp.json() | {"engine": "faster-liveportrait"}
