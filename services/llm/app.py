# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""LLM adapter — a CAPABILITY CONTRACT over Ollama, not a hard-coded model (CONTRACT §5).

Resolution order: user_override -> first installed model matching preference_order
regexes -> first installed model. CPU by default (the RTX 3050's 4 GB belongs to the
avatar). Discovery hits the local Ollama only; nothing leaves the machine.
"""
import os, re, sys
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock, backend_url

app = FastAPI(title="transeg-llm")
OLLAMA = backend_url("ollama", "http://llm-backend:11434")
PREFERENCE = [p for p in os.environ.get(
    "TRANSEG_LLM_PREFERENCE", r"qwen.*[34]b.*instruct;llama3\.2.*3b").split(";") if p]
USER_OVERRIDE = os.environ.get("TRANSEG_LLM_MODEL") or None

class ChatReq(BaseModel):
    prompt: str
    system: str = ""
    context: list[str] = []

def resolve_model(installed: list[str]) -> str | None:
    if USER_OVERRIDE:
        return USER_OVERRIDE                      # user configuration always wins
    for pat in PREFERENCE:
        for m in installed:
            if re.search(pat, m, re.I):
                return m
    return installed[0] if installed else None

@app.get("/health")
def health():
    return {"service": "llm", "status": "ok", "mock": is_mock(), "backend": OLLAMA,
            "device": "cpu", "preference_order": PREFERENCE, "user_override": USER_OVERRIDE}

@app.get("/models")
async def models():
    if is_mock():
        installed = ["qwen2.5:3b-instruct-q4_K_M", "llama3.2:3b"]
        return {"installed": installed, "resolved": resolve_model(installed), "engine": "mock"}
    async with httpx.AsyncClient(timeout=30) as cx:
        resp = await cx.get(f"{OLLAMA}/api/tags"); resp.raise_for_status()
        installed = [m["name"] for m in resp.json().get("models", [])]
    return {"installed": installed, "resolved": resolve_model(installed), "engine": "ollama"}

@app.post("/chat")
async def chat(r: ChatReq):
    if is_mock():
        return {"reply": f"[mock-reply to: {r.prompt[:64]}]",
                "model": resolve_model(["qwen2.5:3b-instruct-q4_K_M"]), "engine": "mock"}
    m = (await models())["resolved"]
    if not m:
        return {"reply": "", "error": "no model installed; run bootstrap.sh --models", "model": None}
    async with httpx.AsyncClient(timeout=600) as cx:
        resp = await cx.post(f"{OLLAMA}/api/generate", json={
            "model": m, "system": r.system,
            "prompt": ("\n".join(r.context) + "\n" if r.context else "") + r.prompt,
            "stream": False})
        resp.raise_for_status()
        return {"reply": resp.json().get("response", ""), "model": m, "engine": "ollama"}
