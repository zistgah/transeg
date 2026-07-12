# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""TransEg gateway — the only composer. Services never call each other (CONTRACT §3).

/chat is conversation-engine plumbing: staggered-upload gate check -> memory read
(context) -> LLM -> memory write (event node with provenance). Reasoning/planning are
replaceable stages that v0.1 delegates to the LLM component; the seams are explicit.
"""
import os, sys, time
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock, backend_url

app = FastAPI(title="transeg-gateway")
SVC = {n: backend_url(n, f"http://{n}:80{p}") for n, p in
       [("memory", "81"), ("staggered", "82"), ("speech", "83"), ("vad", "84"),
        ("llm", "85"), ("tts", "86"), ("avatar", "87")]}
# In-process test mode: tests inject ASGI apps here instead of network URLs.
ASGI_APPS: dict = {}

def _client(name: str) -> httpx.AsyncClient:
    if name in ASGI_APPS:
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=ASGI_APPS[name]),
                                 base_url="http://test")
    return httpx.AsyncClient(base_url=SVC[name], timeout=600)

class ChatReq(BaseModel):
    text: str
    persist: bool = True

class SpeechReq(BaseModel):
    audio_b64: str
    lang: str = "auto"

class VoiceReq(BaseModel):
    text: str
    voice: str = "default"

class RenderReq(BaseModel):
    audio_b64: str
    source_image_b64: str = ""
    fps: int = 25

@app.get("/health")
async def health():
    out = {"service": "gateway", "status": "ok", "mock": is_mock(), "components": {}}
    for name in SVC:
        try:
            async with _client(name) as cx:
                resp = await cx.get("/health")
                out["components"][name] = resp.json().get("status", "unknown")
        except Exception as e:
            out["components"][name] = f"unreachable: {type(e).__name__}"
            out["status"] = "degraded"
    return out

@app.post("/speech")
async def speech(r: SpeechReq):
    async with _client("vad") as cx:
        v = (await cx.post("/vad", json={"audio_b64": r.audio_b64})).json()
    if not v.get("speech"):
        return {"text": "", "vad": v}
    async with _client("speech") as cx:
        s = (await cx.post("/speech", json=r.model_dump())).json()
    return s | {"vad": v}

@app.post("/chat")
async def chat(r: ChatReq):
    t0 = time.time()
    # 1. gate: conversational memory use requires stage 4 ("memory") to be granted
    async with _client("staggered") as cx:
        gate = (await cx.get("/capability/memory")).json()
    context: list[str] = []
    if gate.get("granted"):
        async with _client("memory") as cx:
            q = (await cx.post("/memory/query", json={"kind": "memory", "limit": 5})).json()
            context = [str(n["content"].get("text", "")) for n in q.get("nodes", [])]
    # 2. reason/plan/generate (v0.1: delegated to the LLM component; seam is explicit)
    async with _client("llm") as cx:
        reply = (await cx.post("/chat", json={"prompt": r.text, "context": context})).json()
    # 3. persist the exchange as an event node — with provenance, per the identity graph rules
    if r.persist and gate.get("granted"):
        async with _client("memory") as cx:
            await cx.post("/memory/store", json={
                "kind": "event", "layer": "DigitalTwin",
                "content": {"user": r.text, "twin": reply.get("reply", "")},
                "provenance": {"source": "gateway/chat", "engine": reply.get("engine"),
                               "model": reply.get("model"), "t": t0},
                "confidence": 0.9})
    return {"reply": reply.get("reply", ""), "model": reply.get("model"),
            "memory_gate": gate, "context_used": len(context),
            "latency_s": round(time.time() - t0, 4)}

@app.post("/voice")
async def voice(r: VoiceReq):
    async with _client("tts") as cx:
        return (await cx.post("/voice", json=r.model_dump())).json()

@app.post("/avatar/render")
async def render(r: RenderReq):
    # Stage 0 gate: rendering the face requires the face stage
    async with _client("staggered") as cx:
        gate = (await cx.get("/capability/face")).json()
    if not gate.get("granted"):
        return {"error": "stage 'face' not granted; enable it via staggered upload", "gate": gate}
    async with _client("avatar") as cx:
        return (await cx.post("/avatar/render", json=r.model_dump())).json() | {"gate": gate}

@app.post("/memory/store")
async def mem_store(body: dict):
    async with _client("memory") as cx:
        return (await cx.post("/memory/store", json=body)).json()

@app.post("/memory/query")
async def mem_query(body: dict):
    async with _client("memory") as cx:
        return (await cx.post("/memory/query", json=body)).json()
