# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
import importlib.util, os, sys

os.environ["TRANSEG_MOCK"] = "1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "services"))

def load(name, tmp_env=None):
    for k, v in (tmp_env or {}).items(): os.environ[k] = v
    spec = importlib.util.spec_from_file_location(f"svc_{name}", os.path.join(ROOT, "services", name, "app.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

import pytest

@pytest.fixture()
def mesh(tmp_path):
    """The full component mesh, in-process, wired through the gateway (no network)."""
    memory = load("memory", {"TRANSEG_MEMORY_DB": str(tmp_path / "graph.db")})
    staggered = load("staggered", {"TRANSEG_STAGGERED_STATE": str(tmp_path / "stages.json")})
    apps = {"memory": memory.app, "staggered": staggered.app,
            "speech": load("speech").app, "vad": load("vad").app,
            "llm": load("llm").app, "tts": load("tts").app, "avatar": load("avatar").app}
    gw = load("gateway")
    gw.ASGI_APPS.clear(); gw.ASGI_APPS.update(apps)
    return {"gateway": gw.app, **apps}
