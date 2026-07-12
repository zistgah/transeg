#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# THE ORACLE for the avatar (O-TARGET). Writes a real mp4 or fails loudly.
#   scripts/avatar_smoke.sh [some.wav]      (16 kHz mono wav; defaults to a TTS-made one)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$HERE"
WAV="${1:-}"
GW=http://localhost:8080
ST=http://localhost:8082

[ -f models/liveportrait/source.png ] || { echo "no models/liveportrait/source.png — run avatar_setup.sh"; exit 1; }

echo "== backend health =="
curl -sf http://localhost:8093/health 2>/dev/null || docker compose -f compose/docker-compose.yml exec -T faster-liveportrait curl -sf localhost:8093/health
echo

echo "== stage 0 (face) must be granted, else the gateway refuses — by design =="
curl -sf -XPOST "$ST/stages/enable" -H 'Content-Type: application/json' -d '{"stage":"face"}' >/dev/null
curl -sf "$ST/capability/face"; echo

if [ -z "$WAV" ]; then
  echo "== make audio via TTS (needs --profile tts) =="
  curl -sf -XPOST "$GW/voice" -H 'Content-Type: application/json' \
    -d '{"text":"Salaam. Main TransEg hoon."}' | python3 -c \
    'import sys,json,base64;open("out.wav","wb").write(base64.b64decode(json.load(sys.stdin)["audio_b64"]))'
  WAV=out.wav
fi

echo "== render =="
python3 - "$WAV" <<'PY'
import base64, json, sys, time, urllib.request
wav = base64.b64encode(open(sys.argv[1],"rb").read()).decode()
img = base64.b64encode(open("models/liveportrait/source.png","rb").read()).decode()
req = urllib.request.Request("http://localhost:8080/avatar/render",
      json.dumps({"audio_b64": wav, "source_image_b64": img}).encode(),
      {"Content-Type":"application/json"})
t0=time.time(); r=json.loads(urllib.request.urlopen(req, timeout=1800).read())
if "error" in r: print("FAIL:", r["error"]); sys.exit(1)
open("avatar_out.mp4","wb").write(base64.b64decode(r["video_b64"]))
print("OK: avatar_out.mp4  frames=%s fps=%s median_ms/frame=%s wall=%.1fs"
      % (r.get("frames"), r.get("fps"), r.get("median_ms_per_frame"), time.time()-t0))
PY
ls -l avatar_out.mp4
echo "PASSED — this, and only this, flips QUESTS.md Q5 avatar to on-target verified."
