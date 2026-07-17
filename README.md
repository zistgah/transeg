# Project TransEg — Local Digital Twin Reference Implementation

**TransEg™** · © 1993–2026 Abhishek Choudhary · AyeAI, Hyderabad, India · sole author.
Software GPL-3.0-or-later · content CC-BY-SA-4.0 · metadata CC0-1.0 · novel methods proprietary.
DOI: 10.5281/zenodo.21321558NNNNNNNN · derived from PEDLER (Nov 2001, doi:10.5281/zenodo.17497559)

This is not a chatbot. It is not merely a talking avatar. It is an **identity continuity
research platform** — the first executable reference implementation of the TransEg
architecture. Fully local: no cloud, no telemetry, no hidden uploads.

**TransEg exists within Zistgah.** Zistgah is an institution, not a website or a software
project; this repository, its DOIs, images, and services are artifacts and interfaces of
Zistgah. TransEg is one class of computational representative within Zistgah — the
inhabitant that lives on in Zistgah after the bioform. In the broader program, PEDLER
provides adaptive cognition, PRATIK the execution substrate, PAT.AL societal participation,
VIDYA the knowledge ecosystem, and Zistgah the enduring institutional substrate.

## The four typed layers — never conflated
Human Identity → Representation → Digital Twin → TransEg. Types, permissions, and
lifecycle rules are specified in [`zistgah/transeg-idgov`](../transeg-idgov); benchmarks
and experiments live in [`zistgah/transeg-research`](../transeg-research). Component Based
Engineering: three repos, one architecture.

## Quick start (target: Ryzen 7 · 16 GB · RTX 3050 4 GB · Ubuntu 26.04 · Docker)
```
scripts/test.sh                     # hermetic venv; 10/10 before anything else
./scripts/bootstrap.sh --dry-run    # read the plan
./scripts/bootstrap.sh              # validate host, build, models, start, health, pin
```

### Avatar (the face; the sole GPU tenant)
```
scripts/avatar_setup.sh                                # FLP source + LivePortrait onnx + JoyVASA + hubert + silero
cp <frontal portrait> models/liveportrait/source.png   # your Stage-0 artifact; never leaves the box
docker compose -f compose/docker-compose.yml --profile tts up -d --build
scripts/avatar_smoke.sh                                # THE ORACLE — writes avatar_out.mp4 or fails loudly
```
Full walkthrough: [HOWTO.md](HOWTO.md) · avatar internals + licences: [docs/avatar.md](docs/avatar.md)


## Staggered Upload
Identity acquisition is incremental and typed: face · voice · documents · knowledge ·
memory · preferences · reasoning · delegated tasks. Each stage is independently enabled,
revoked, versioned, and auditable. No stage implicitly grants another. The gateway enforces
the gates (`/chat` needs stage *memory*; `/avatar/render` needs stage *face*).

## Verification (VGC)
In-container CI: `python3 -m pytest tests/` — health mesh, identity-graph roundtrips
including encrypted backup/restore, staggered gating, full pipeline in mock mode.
On-target: `./scripts/bootstrap.sh --validate` — the only oracle for model/GPU/audio/camera
claims. The AAB painting and quest ledger: `aab/manifest.json`, `QUESTS.md`.

## Owner powers (load-bearing)
`/memory/export` · `/memory/delete` · `/memory/backup` (Fernet-encrypted, key stays with
you) · `/memory/restore`. All personal information belongs to the owner.

Docs: `docs/` (architecture, deployment, API, threat model, reproducibility; identity model
→ transeg-idgov; benchmark methodology → transeg-research).
