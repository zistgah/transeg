# SPDX-License-Identifier: GPL-3.0-or-later
import httpx, pytest

@pytest.mark.anyio
async def test_every_component_reports_ok(mesh):
    gw = httpx.AsyncClient(transport=httpx.ASGITransport(app=mesh["gateway"]), base_url="http://t")
    h = (await gw.get("/health")).json()
    assert h["status"] == "ok", h
    assert set(h["components"]) == {"memory","staggered","speech","vad","llm","tts","avatar"}
    assert all(v == "ok" for v in h["components"].values()), h["components"]

@pytest.fixture
def anyio_backend(): return "asyncio"
