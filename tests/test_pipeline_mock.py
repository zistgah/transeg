# SPDX-License-Identifier: GPL-3.0-or-later
"""Full pipeline through the gateway in mock mode: gates, memory persistence,
speech->chat->voice->avatar. MOCK ORACLE — proves the API contracts and the
composition, never the models (CONTRACT §9)."""
import base64, httpx, pytest

@pytest.fixture
def anyio_backend(): return "asyncio"

def C(app): return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t")

@pytest.mark.anyio
async def test_chat_respects_memory_gate_and_persists(mesh):
    gw, s, m = C(mesh["gateway"]), C(mesh["staggered"]), C(mesh["memory"])
    await s.post("/reset")
    r1 = (await gw.post("/chat", json={"text": "salaam"})).json()
    assert r1["reply"].startswith("[mock-reply") and not r1["memory_gate"]["granted"]
    assert not (await m.post("/memory/query", json={"kind": "event"})).json()["nodes"]  # gate held
    await s.post("/stages/enable", json={"stage": "memory"})
    r2 = (await gw.post("/chat", json={"text": "yaad rakho: zamin"})).json()
    assert r2["memory_gate"]["granted"] and r2["latency_s"] >= 0
    ev = (await m.post("/memory/query", json={"kind": "event"})).json()["nodes"]
    assert ev and ev[0]["provenance"]["source"] == "gateway/chat"     # traceable memory

@pytest.mark.anyio
async def test_speech_vad_and_avatar_gate(mesh):
    gw, s = C(mesh["gateway"]), C(mesh["staggered"])
    await s.post("/reset")
    silent = (await gw.post("/speech", json={"audio_b64": ""})).json()
    assert silent["text"] == "" and not silent["vad"]["speech"]       # VAD short-circuits
    audio = base64.b64encode(b"\x01" * 32000).decode()
    heard = (await gw.post("/speech", json={"audio_b64": audio})).json()
    assert heard["text"].startswith("[mock-transcript")
    v = (await gw.post("/voice", json={"text": heard["text"]})).json()
    assert v["audio_b64"] and v["sample_rate"] == 24000
    blocked = (await gw.post("/avatar/render", json={"audio_b64": v["audio_b64"]})).json()
    assert "error" in blocked                                          # face stage not granted
    await s.post("/stages/enable", json={"stage": "face"})
    ok = (await gw.post("/avatar/render", json={"audio_b64": v["audio_b64"]})).json()
    assert ok.get("video_b64") and ok["gate"]["granted"]

@pytest.mark.anyio
async def test_llm_capability_contract_resolution(mesh):
    llm = C(mesh["llm"])
    r = (await llm.get("/models")).json()
    assert r["resolved"] == "qwen2.5:3b-instruct-q4_K_M"               # preference order, not hard-coding
