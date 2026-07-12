# SPDX-License-Identifier: GPL-3.0-or-later
"""Owner powers are load-bearing: store/query/delete/export + encrypted backup/restore.
Every node must carry provenance and a valid typed layer; conflation is rejected."""
import httpx, pytest

@pytest.fixture
def anyio_backend(): return "asyncio"

def C(app): return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t")

NODE = {"kind": "memory", "layer": "DigitalTwin",
        "content": {"text": "state gold medal, 10m air pistol"},
        "provenance": {"source": "owner-entry", "session": "t1"},
        "confidence": 0.95}

@pytest.mark.anyio
async def test_store_query_delete_roundtrip(mesh):
    m = C(mesh["memory"])
    nid = (await m.post("/memory/store", json=NODE)).json()["id"]
    q = (await m.post("/memory/query", json={"text": "air pistol"})).json()
    assert q["nodes"] and q["nodes"][0]["id"] == nid
    n = q["nodes"][0]
    assert n["provenance"]["source"] == "owner-entry" and n["confidence"] == 0.95
    assert n["created_at"] > 0 and n["permissions"]["owner"] == "human"
    assert (await m.post("/memory/delete", json={"id": nid})).json()["deleted"]
    assert not (await m.post("/memory/query", json={"text": "air pistol"})).json()["nodes"]

@pytest.mark.anyio
async def test_provenance_and_layer_are_enforced(mesh):
    m = C(mesh["memory"])
    r = await m.post("/memory/store", json=NODE | {"provenance": {}})
    assert r.status_code == 422                       # no orphan facts
    r = await m.post("/memory/store", json=NODE | {"layer": "Twin"})
    assert r.status_code == 422                # the four layers are typed; no conflation
    r = await m.post("/memory/store", json=NODE | {"kind": "flatrow"})
    assert r.status_code == 422                       # graph, not a flat database

@pytest.mark.anyio
async def test_encrypted_backup_restore_roundtrip(mesh):
    m = C(mesh["memory"])
    await m.post("/memory/store", json=NODE)
    b = (await m.post("/memory/backup", json={})).json()
    assert "ciphertext" in b and "graph" not in b["ciphertext"]     # actually encrypted
    for n in (await m.post("/memory/export", json={})).json()["nodes"]:
        await m.post("/memory/delete", json={"id": n["id"]})
    assert not (await m.post("/memory/export", json={})).json()["nodes"]
    r = (await m.post("/memory/restore", json=b)).json()
    assert r["restored_nodes"] == 1
    assert (await m.post("/memory/query", json={"text": "air pistol"})).json()["nodes"]
    bad = await m.post("/memory/restore", json={"key": "x"*44, "ciphertext": b["ciphertext"]})
    assert bad.status_code == 422                     # wrong key never restores
