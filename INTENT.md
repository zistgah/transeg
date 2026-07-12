<!-- ORIGINAL INTENT — VERBATIM. Per AAB discipline this file is never edited, only appended
     below the appendix line. It is the painting's ground truth for continuity, audit, and
     gap analysis. Recorded 2026-07-12 from the author's specification. -->

Project: TransEg Local Digital Twin Reference Implementation

Mission

Build a fully local, privacy-preserving, modular, containerized digital twin platform that serves as the first executable implementation of the TransEg architecture.

This is not a chatbot.

It is not merely a talking avatar.

It is an identity continuity research platform.

---

Core Objectives

The system shall:

operate completely offline
be reproducible
preserve user ownership
be modular
support future research
expose well-defined APIs
be extensible

The first release is a reference implementation.

---

Hardware Target

Minimum target: Ryzen 7, 16 GB RAM, RTX 3050 Laptop GPU, 4 GB VRAM, Ubuntu 26.04, Docker.
Everything must optimize for this configuration.

---

Primary Constraints

GPU memory is scarce. Therefore: GPU primarily reserved for facial animation. CPU performs speech recognition where practical. CPU hosts the LLM unless GPU capacity permits. Minimize VRAM fragmentation. Avoid duplicate model loading.

---

Functional Architecture

Human -> Microphone -> Voice Activity Detection -> Speech Recognition -> Conversation Engine -> Memory -> Reasoning -> Planning -> Text Generation -> Speech Synthesis -> Talking Face -> Human

Every stage must be replaceable.

---

System Principles

The system shall be: API first, containerized, reproducible, deterministic, observable, testable. No hidden state.

---

Required Services

Speech Recognition: Whisper.cpp · Voice Activity Detection: Silero · LLM: Ollama · Memory: separate service · Vector Store: pluggable · Talking Face: FasterLivePortrait · Speech: Kokoro · Gateway: FastAPI

---

Container Requirements

One Docker Compose starts everything. No manual installation of CUDA Toolkit, Python packages, Torch, TensorRT outside containers.

---

Bootstrap

Single command bootstrap.sh must: clone repositories, build containers, download models, validate GPU, validate Docker, validate audio, validate camera, start services, run health checks.

---

Repository Layout

transEg/: docs/ docker/ compose/ scripts/ services/{speech,memory,llm,tts,avatar,gateway} tests/ examples/ models/ configs/ benchmarks/ papers/

---

API Requirements

Every service exposes REST API. No direct coupling.
Examples: POST /speech · POST /chat · POST /memory/query · POST /memory/store · POST /avatar/render · POST /voice · GET /health

---

Identity Layer

The system must distinguish: Human Identity -> Representation -> Digital Twin -> TransEg.
These are NOT interchangeable.

---

Staggered Upload

Identity acquisition must be incremental.
Stage 0 Face · Stage 1 Voice · Stage 2 Documents · Stage 3 Knowledge · Stage 4 Memory · Stage 5 Preferences · Stage 6 Reasoning · Stage 7 Delegated Tasks.
Every stage is independently configurable.

---

Identity Graph

Identity is represented as a graph. Nodes include: memories, publications, documents, relationships, events, skills, preferences, goals.
Every node contains: provenance, timestamps, confidence, permissions.

---

Governance Layer

Identity must never be treated as a flat database. Every identity artifact includes: provenance, consent, ownership, signature, version, revocation.

---

Trust Layer

Every release: signed, checksummed, reproducible. Every model: versioned, attributable. Every memory: traceable.

---

Security

Default assumptions: No cloud. No telemetry. No hidden uploads. Everything local. Explicit opt-in for networking.

---

Privacy

All personal information belongs to the owner. Memory must support: export, deletion, backup, encryption.

---

Benchmarks

Include benchmark framework for: Latency, Speech, Identity Fidelity, Memory Retention, Preference Consistency, Reasoning Stability, Conversation Quality, Representation Drift.

---

Research Requirements

Implementation must expose experiments for: Identity Drift, Incremental Upload, Representation Fidelity, Delegated Agency, Memory Compression, Long-term Memory, Graph Retrieval.

---

Future Extensions

Architecture must anticipate: PEDLER integration, PRATIK execution substrate, ILM multilingual interaction, Hindawi programming interface, BCI integration, robotics embodiment, distributed identity, multiple TransEg instances — without requiring architectural redesign.

---

Documentation

Produce: architecture document, deployment guide, API specification, threat model, governance model, identity model, benchmark methodology, developer guide, user guide, reproducibility guide.

---
<!-- APPENDIX (append-only, dated) -->

2026-07-12 — Author decisions on the open questions:
- Three repositories under zistgah — transeg (core), transeg-idgov (identity governance),
  transeg-research (benchmarks + experiments). Component Based Engineering: always prefer
  partition where feasible.
- LLM stays a capability contract: discovery + preference order (Qwen 3B/4B Instruct Q4 →
  Llama 3.2 3B → user-configurable); never hard-code a model family.
- Lineage: TransEg is derived from PEDLER (first published November 2001; authoritative
  record doi:10.5281/zenodo.17497559). NOT derived from the VGC methodology — VGC is the
  process by which this implementation is built, not the concept's parent.
- TransEg is the final mark.
- Zistgah is an institution, not a website or software project. TransEg exists within
  Zistgah; repositories, DOIs, images, and services are artifacts and interfaces of Zistgah.
  TransEg lives on in Zistgah after the bioform.
- Positioning: PEDLER provides adaptive cognition; PRATIK the execution substrate; PAT.AL
  the societal participation framework; VIDYA the educational and knowledge ecosystem;
  Zistgah the enduring institutional substrate. TransEg is one class of computational
  representative within Zistgah; the architecture must admit future computational
  representatives and embodied systems without redesign.
- TransEg as a concept is decades old; archival evidence on hindawi.in (Wayback Machine)
  is recorded as a Declared claim pending retrieval — see QUESTS.md quest Q-PROV.
