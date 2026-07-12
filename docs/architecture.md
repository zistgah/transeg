# TransEg architecture (v0.1)
<!-- content CC-BY-SA-4.0 · © 1993-2026 Abhishek Choudhary · AyeAI -->
TransEg is a component mesh behind a single composing gateway. Nine containers implement
the pipeline mic → VAD → ASR → gateway → memory → LLM → TTS → avatar; two more host the
Whisper.cpp and Ollama backends. Services never call each other — the gateway composes, so
every stage is replaceable by swapping one container and one URL (Component Based
Engineering). The identity graph is the only durable store: typed nodes (memory,
publication, document, relationship, event, skill, preference, goal) each carrying
provenance, timestamps, confidence, and permissions, on one of four typed layers
(HumanIdentity, Representation, DigitalTwin, TransEg) that are never conflated. The
Staggered Upload machine gates capability by stage; the gateway consults it before memory
reads/writes and before face rendering. The vector store is pluggable behind the memory
service; v0.1 ships the builtin SQLite retrieval and reserves the plugin seam. Reasoning
and planning are explicit seams delegated to the LLM component in v0.1 — a future PEDLER
integration replaces that component without redesign, PRATIK slots beneath it as execution
substrate, ILM/Hindawi attach at the gateway as interaction surfaces, and BCI/robotics
embodiments attach as new actors on the same mesh. VRAM discipline on the 4 GB target:
the avatar is the sole GPU tenant; everything else is CPU; no duplicate model loading
(models/ is mounted read-only into backends).
