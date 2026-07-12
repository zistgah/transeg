# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""TransEg memory service — the identity graph.

Identity is a graph, never a flat database. Every node carries provenance,
timestamps, confidence, permissions, and a typed layer. Owner powers are
load-bearing: export, deletion, backup (encrypted), restore.
"""
import base64, json, os, sqlite3, time, uuid
from typing import Any, Optional
from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common.core import assert_layer

DB = os.environ.get("TRANSEG_MEMORY_DB", os.path.join(os.path.dirname(__file__), "identity_graph.db"))
app = FastAPI(title="transeg-memory")

def _conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.executescript("""
    CREATE TABLE IF NOT EXISTS nodes(
      id TEXT PRIMARY KEY, kind TEXT NOT NULL, layer TEXT NOT NULL,
      content TEXT NOT NULL, provenance TEXT NOT NULL,
      created_at REAL NOT NULL, updated_at REAL NOT NULL,
      confidence REAL NOT NULL, permissions TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS edges(
      src TEXT NOT NULL, dst TEXT NOT NULL, rel TEXT NOT NULL,
      created_at REAL NOT NULL, PRIMARY KEY(src,dst,rel));
    """)
    return c

NODE_KINDS = {"memory","publication","document","relationship","event","skill","preference","goal"}

class StoreReq(BaseModel):
    kind: str
    layer: str
    content: dict[str, Any]
    provenance: dict[str, Any]              # REQUIRED — no orphan facts
    confidence: float = Field(ge=0.0, le=1.0)
    permissions: dict[str, Any] = Field(default_factory=lambda: {"owner": "human", "share": "none"})
    edges: list[dict[str, str]] = Field(default_factory=list)  # [{dst, rel}]

class QueryReq(BaseModel):
    kind: Optional[str] = None
    layer: Optional[str] = None
    text: Optional[str] = None
    limit: int = 50

@app.get("/health")
def health(): return {"service": "memory", "status": "ok", "db": DB}

@app.post("/memory/store")
def store(r: StoreReq):
    if r.kind not in NODE_KINDS:
        raise HTTPException(422, f"kind must be one of {sorted(NODE_KINDS)}")
    try:
        assert_layer(r.layer)
    except ValueError as e:
        raise HTTPException(422, str(e))
    if not r.provenance:
        raise HTTPException(422, "provenance is required on every identity node")
    now = time.time(); nid = str(uuid.uuid4())
    c = _conn()
    with c:
        c.execute("INSERT INTO nodes VALUES(?,?,?,?,?,?,?,?,?)",
                  (nid, r.kind, r.layer, json.dumps(r.content), json.dumps(r.provenance),
                   now, now, r.confidence, json.dumps(r.permissions)))
        for e in r.edges:
            c.execute("INSERT OR REPLACE INTO edges VALUES(?,?,?,?)", (nid, e["dst"], e["rel"], now))
    return {"id": nid, "created_at": now}

@app.post("/memory/query")
def query(r: QueryReq):
    q = "SELECT * FROM nodes WHERE 1=1"; args: list[Any] = []
    if r.kind:  q += " AND kind=?";  args.append(r.kind)
    if r.layer:
        try: assert_layer(r.layer)
        except ValueError as e: raise HTTPException(422, str(e))
        q += " AND layer=?"; args.append(r.layer)
    if r.text:  q += " AND content LIKE ?"; args.append(f"%{r.text}%")
    q += " ORDER BY updated_at DESC LIMIT ?"; args.append(r.limit)
    rows = _conn().execute(q, args).fetchall()
    return {"nodes": [dict(row) | {"content": json.loads(row["content"]),
                                   "provenance": json.loads(row["provenance"]),
                                   "permissions": json.loads(row["permissions"])} for row in rows]}

@app.post("/memory/delete")
def delete(body: dict):
    nid = body.get("id")
    if not nid: raise HTTPException(422, "id required")
    c = _conn()
    with c:
        n = c.execute("DELETE FROM nodes WHERE id=?", (nid,)).rowcount
        c.execute("DELETE FROM edges WHERE src=? OR dst=?", (nid, nid))
    return {"deleted": bool(n)}

@app.post("/memory/export")
def export():
    c = _conn()
    nodes = [dict(r) for r in c.execute("SELECT * FROM nodes")]
    edges = [dict(r) for r in c.execute("SELECT * FROM edges")]
    return {"format": "transeg-identity-graph/1", "nodes": nodes, "edges": edges}

@app.post("/memory/backup")
def backup(body: dict):
    """Encrypted backup. Key stays with the owner; we never store it."""
    key = body.get("key") or Fernet.generate_key().decode()
    blob = Fernet(key.encode()).encrypt(json.dumps(export()).encode())
    return {"key": key, "ciphertext": base64.b64encode(blob).decode()}

@app.post("/memory/restore")
def restore(body: dict):
    try:
        data = json.loads(Fernet(body["key"].encode()).decrypt(base64.b64decode(body["ciphertext"])))
    except Exception:
        raise HTTPException(422, "bad key or ciphertext")
    c = _conn()
    with c:
        for n in data["nodes"]:
            c.execute("INSERT OR REPLACE INTO nodes VALUES(?,?,?,?,?,?,?,?,?)",
                      (n["id"], n["kind"], n["layer"], n["content"], n["provenance"],
                       n["created_at"], n["updated_at"], n["confidence"], n["permissions"]))
        for e in data["edges"]:
            c.execute("INSERT OR REPLACE INTO edges VALUES(?,?,?,?)",
                      (e["src"], e["dst"], e["rel"], e["created_at"]))
    return {"restored_nodes": len(data["nodes"]), "restored_edges": len(data["edges"])}
