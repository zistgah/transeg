# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""VAD adapter — Silero, ONNX Runtime, CPU, IN-PROCESS.

Fix: the previous version pointed at a `silero-vad` backend container that compose
never defined — real mode would have failed on the first call. Silero is a 2.3 MB
ONNX graph; a whole container for it is waste. It now runs in this service.

Contract verified by execution (CPU, onnxruntime): frames of 512 samples @ 16 kHz,
state (2, 1, 128) float32, sr int64 scalar; outputs (speech_prob, next_state).
Audio in is base64 16-bit PCM mono @ 16 kHz (raw or WAV — a 44-byte RIFF header is
detected and skipped).
"""
import base64, os, sys
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import is_mock

app = FastAPI(title="transeg-vad")
MODEL = os.environ.get("TRANSEG_SILERO_ONNX", "/models/silero_vad.onnx")
SR, FRAME = 16000, 512
THRESH = float(os.environ.get("TRANSEG_VAD_THRESHOLD", "0.5"))
_sess = None


def _session():
    global _sess
    if _sess is None:
        import onnxruntime as ort            # imported lazily: mock mode needs no runtime
        _sess = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    return _sess


def _pcm(raw: bytes) -> np.ndarray:
    if raw[:4] == b"RIFF":
        i = raw.find(b"data")
        raw = raw[i + 8:] if i != -1 else raw[44:]
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return x


class VadReq(BaseModel):
    audio_b64: str


@app.get("/health")
def health():
    return {"service": "vad", "status": "ok", "mock": is_mock(), "device": "cpu",
            "backend": "silero-onnx", "model": MODEL,
            "model_present": os.path.exists(MODEL)}


@app.post("/vad")
def vad(r: VadReq):
    raw = base64.b64decode(r.audio_b64 or b"")
    if is_mock():
        n = len(raw)
        return {"speech": n > 0, "segments": ([[0.0, round(n / (2 * SR), 3)]] if n else []),
                "engine": "mock"}
    x = _pcm(raw)
    s = _session()
    state = np.zeros((2, 1, 128), dtype=np.float32)
    sr = np.array(SR, dtype=np.int64)
    probs = []
    for i in range(0, len(x) - FRAME + 1, FRAME):
        p, state = s.run(None, {"input": x[i:i + FRAME][None, :], "state": state, "sr": sr})
        probs.append(float(p[0][0]))
    segments, start = [], None
    for i, p in enumerate(probs):
        t = i * FRAME / SR
        if p >= THRESH and start is None:
            start = t
        elif p < THRESH and start is not None:
            segments.append([round(start, 3), round(t, 3)]); start = None
    if start is not None:
        segments.append([round(start, 3), round(len(x) / SR, 3)])
    return {"speech": bool(segments), "segments": segments,
            "max_prob": round(max(probs), 4) if probs else 0.0, "engine": "silero-onnx"}
