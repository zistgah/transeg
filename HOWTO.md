# HOWTO — Project TransEg
© 1993–2026 Abhishek Choudhary · AyeAI

## 0. Tests — hermetic, owns its venv
Bare `pytest` dies with `ModuleNotFoundError: httpx` on python3.14 with no site-packages.
That is a missing environment, not a test failure.
```bash
scripts/test.sh                 # .venv + requirements-dev.txt + pytest
```
Expect `10 passed` (core), 14 (idgov), 7 (research).

## 1. Mock mesh — any machine, no GPU, no models
```bash
TRANSEG_MOCK=1 docker compose -f compose/docker-compose.yml up -d --build
curl -s localhost:8080/health          # seven components "ok"
```
Proves the API contracts and the composition. Proves NOTHING about the models.

## 2. The avatar — target box only (Ryzen 7 · 16 GB · RTX 3050 4 GB · Ubuntu 26.04)
```bash
scripts/avatar_setup.sh                                # FLP source + LivePortrait onnx + JoyVASA + hubert + silero
cp <frontal portrait> models/liveportrait/source.png   # your Stage-0 artifact; never leaves the box
docker compose -f compose/docker-compose.yml --profile tts up -d --build
scripts/avatar_smoke.sh                                # THE ORACLE — writes avatar_out.mp4 or fails loudly
```
`avatar_smoke.sh` is the only thing that may flip the avatar quest to verified. A green
mock suite is not an avatar. Internals, VRAM rules, TensorRT fast path, model licences:
`docs/avatar.md`. Stage 0 is gated — `/avatar/render` refuses until `face` is granted, and
that refusal is the feature.

## 3. Full local run
```bash
scripts/bootstrap.sh --dry-run     # read the plan
scripts/bootstrap.sh               # validate host → build → models → up → health → pin
scripts/bootstrap.sh --pin         # digests → provenance/pins.txt (commit it)
```

## 4. Benchmarks against the live mesh
```bash
cd ../transeg-research && python3 runner.py --mode gateway    # needs :8080 and :8082 up
```
The result document carries its own tier. A synthetic number is never a system claim.

## 5. Publish
`MINT_RUNBOOK.md` — sandbox → draft → publish. Nothing irreversible without your hand on it.
