# API specification (v0.1)
<!-- content CC-BY-SA-4.0 -->
Gateway (localhost:8080): GET /health aggregates every component. POST /speech
{audio_b64, lang} runs VAD then ASR and returns {text, vad}. POST /chat {text, persist}
checks the stage-memory gate, reads up to five memory nodes as context, generates via the
LLM capability contract, persists the exchange as an event node with provenance, and
returns {reply, model, memory_gate, context_used, latency_s}. POST /voice {text, voice}
returns {audio_b64, sample_rate}. POST /avatar/render {audio_b64, source_image_b64, fps}
requires the stage-face gate. POST /memory/store and /memory/query proxy the identity
graph. Memory service: /memory/store requires kind ∈ {memory, publication, document,
relationship, event, skill, preference, goal}, a typed layer, non-empty provenance, and
confidence ∈ [0,1]; /memory/export, /memory/delete {id}, /memory/backup {key?} →
{key, ciphertext}, /memory/restore {key, ciphertext}. Staggered service: GET /stages,
POST /stages/enable {stage, actor}, POST /stages/revoke, GET /capability/{stage} — the
only question other services may ask. All errors are explicit HTTP 4xx/5xx; no hidden state.
