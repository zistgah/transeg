# CONTEXT — zistgah/transeg (cold-start map)

## Mission (one line)
TransEg is a fully local, privacy-preserving identity-continuity research platform — the
first executable reference implementation of the TransEg architecture. Not a chatbot; not
merely a talking avatar. Zistgah is the habitat; TransEg is the inhabitant that lives on in
Zistgah after the bioform.

## Institutional framing
Zistgah is an **institution**, not a website or a software project. This repository, its
DOIs, images, and services are **artifacts and interfaces of Zistgah**. TransEg exists
within Zistgah; it does not "live in a repository."

## The three-repo partition (Component Based Engineering)
- `zistgah/transeg` — THIS repo: executable core (VAD, ASR, memory, LLM, TTS, avatar, gateway).
- `zistgah/transeg-idgov` — identity governance ONLY: typed layers, provenance, consent,
  ownership, permissions, delegation, attestation, revocation, audit. Ecosystem governance
  stays in `zistgah/governance` — separate concerns, never merge them.
- `zistgah/transeg-research` — benchmark framework (9 benchmarks, machine-readable output)
  and the seven reference experiments.

## Pipeline (every stage replaceable)
mic → VAD (Silero, CPU) → ASR (Whisper.cpp, CPU) → gateway → memory (identity graph) →
LLM (Ollama capability contract, CPU) → TTS (Kokoro, CPU) → avatar (FasterLivePortrait,
sole GPU tenant, 4 GB VRAM budget) → human.

## Layout
services/{gateway,memory,staggered,speech,vad,llm,tts,avatar} · compose/ · docker/ ·
scripts/{bootstrap.sh,zistgah_seed_transeg.sh} · tests/ · configs/transeg.yaml ·
aab/manifest.json + QUESTS.md (AAB painting + quest ledger) · INTENT.md (verbatim, append-only).

## Verification tiers
- IN-CONTAINER (CI): pytest over in-process ASGI — health mesh, identity-graph roundtrips
  incl. encryption, staggered-upload gating, full pipeline in mock mode, compose YAML sanity.
- ON-TARGET (Ryzen 7 · 16 GB · RTX 3050 4 GB · Ubuntu 26.04): `bootstrap.sh --validate` —
  real models, GPU, audio, camera. Only this tier verifies model-dependent claims.

## Lineage & provenance
Derived from PEDLER (Nov 2001; doi:10.5281/zenodo.17497559 — verified by direct read
2026-06-29, corroborated 2026-07-12; resolve-check before mint). TransEg concept is decades
old; hindawi.in Wayback evidence is Declared — retrieval procedure in QUESTS.md Q-PROV.
Registry gap: PEDLER DOI missing from governance REGISTRY.json known_dois — patch on push
(seed.json carries the registry_patch).

## Standing instruction
Maintain contract and context. Read INTENT.md before touching anything.
