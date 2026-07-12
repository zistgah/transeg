# SPDX-License-Identifier: GPL-3.0-or-later
"""Stages 0-7: independently enabled/revoked/versioned/auditable.
No stage may implicitly grant capabilities from any other stage."""
import httpx, pytest

@pytest.fixture
def anyio_backend(): return "asyncio"

def C(app): return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t")

@pytest.mark.anyio
async def test_no_implicit_grants(mesh):
    s = C(mesh["staggered"]); await s.post("/reset")
    await s.post("/stages/enable", json={"stage": "documents"})       # stage 2
    for other in ["face","voice","knowledge","memory","preferences","reasoning","delegated_tasks"]:
        assert not (await s.get(f"/capability/{other}")).json()["granted"], other
    assert (await s.get("/capability/documents")).json()["granted"]

@pytest.mark.anyio
async def test_independent_revocation_versioning_audit(mesh):
    s = C(mesh["staggered"]); await s.post("/reset")
    await s.post("/stages/enable", json={"stage": "memory"})
    await s.post("/stages/enable", json={"stage": "voice"})
    await s.post("/stages/revoke", json={"stage": "memory"})
    assert not (await s.get("/capability/memory")).json()["granted"]  # revoked
    assert (await s.get("/capability/voice")).json()["granted"]       # untouched: independent
    st = (await s.get("/stages")).json()
    assert st["memory"]["version"] == 2 and st["voice"]["version"] == 1
    acts = [a["action"] for a in st["memory"]["audit"]]
    assert acts == ["enable", "revoke"] and all("t" in a and "actor" in a for a in st["memory"]["audit"])

@pytest.mark.anyio
async def test_unknown_stage_rejected(mesh):
    s = C(mesh["staggered"])
    assert (await s.post("/stages/enable", json={"stage": "soul"})).status_code == 422
