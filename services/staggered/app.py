# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""TransEg Staggered Upload — a typed state machine.

Stages 0-7 are independent: independently enabled, independently revoked,
independently versioned, independently auditable. No stage may implicitly
grant capabilities from any other stage (CONTRACT §8).
"""
import json, os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

STAGES = ["face","voice","documents","knowledge","memory","preferences","reasoning","delegated_tasks"]
STATE_PATH = os.environ.get("TRANSEG_STAGGERED_STATE",
                            os.path.join(os.path.dirname(__file__), "staggered_state.json"))
app = FastAPI(title="transeg-staggered")

def _fresh():
    return {s: {"stage": i, "enabled": False, "revoked": False, "version": 0, "audit": []}
            for i, s in enumerate(STAGES)}

def _load():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f: return json.load(f)
    return _fresh()

def _save(st):
    with open(STATE_PATH, "w") as f: json.dump(st, f, indent=1)

def _audit(rec, action, actor):
    rec["version"] += 1
    rec["audit"].append({"t": time.time(), "action": action, "actor": actor, "version": rec["version"]})

class StageReq(BaseModel):
    stage: str
    actor: str = "owner"

@app.get("/health")
def health(): return {"service": "staggered", "status": "ok", "stages": STAGES}

@app.get("/stages")
def stages(): return _load()

@app.post("/stages/enable")
def enable(r: StageReq):
    st = _load()
    if r.stage not in st: raise HTTPException(422, f"unknown stage {r.stage!r}")
    rec = st[r.stage]; rec["enabled"] = True; rec["revoked"] = False
    _audit(rec, "enable", r.actor); _save(st)
    return rec

@app.post("/stages/revoke")
def revoke(r: StageReq):
    st = _load()
    if r.stage not in st: raise HTTPException(422, f"unknown stage {r.stage!r}")
    rec = st[r.stage]; rec["enabled"] = False; rec["revoked"] = True
    _audit(rec, "revoke", r.actor); _save(st)
    return rec

@app.get("/capability/{stage}")
def capability(stage: str):
    """The ONLY question other services may ask. Exactly this stage, nothing implied."""
    st = _load()
    if stage not in st: raise HTTPException(422, f"unknown stage {stage!r}")
    rec = st[stage]
    return {"stage": stage, "granted": bool(rec["enabled"] and not rec["revoked"]),
            "version": rec["version"]}

@app.post("/reset")
def reset():
    _save(_fresh()); return {"reset": True}
