# Defects found in transeg v0.1.0 (found by reading upstream code + executing)
© 1993-2026 Abhishek Choudhary · AyeAI

| # | Defect | Where | Fix in this patch | Oracle |
|---|---|---|---|---|
| D1 | **Avatar backend was a stub** — `liveportrait_server.py` returned `b"onnx-or-trt-frames"`. The mock pipeline test passed *through the adapter*, so nothing caught it. Also: FLP is driving-video, not audio-driven; audio needs JoyVASA. | docker/liveportrait_server.py, docker/liveportrait.Dockerfile | Real server on FLP's own audio-driven path (JoyVASA → run_with_pkl → ffmpeg mux); upstream image `shaoguo/faster_liveportrait:v3` replaces the hand-rolled CUDA Dockerfile | scripts/avatar_smoke.sh (on-target) |
| D2 | **VAD pointed at a host that compose never defined** (`http://silero-vad:8091`). Real mode would 500 on the first `/speech` call. | services/vad/app.py, compose | Silero ONNX (2.3 MB) runs **in-process**, CPU. Contract verified by execution here: 512-sample frames @16k, state (2,1,128), sr int64. Silence → 0.0006. | pytest + on-target with real speech |
| D3 | **staggered port not published** — transeg-research's GatewayAdapter reads `localhost:8082/capability/...`; compose exposed nothing. | compose | `ports: ["8082:80"]` on staggered | `runner.py --mode gateway` |
| D4 | whisper.cpp / kokoro image tags **unverified** from my sandbox. | compose | made env-overridable + `--profile tts`; pin with `bootstrap.sh --pin` | your `docker pull` |
| D5 | Tarball carried a literal `{docs,docker,...}` directory (sh has no brace expansion; my first mkdir made a directory with that name). | — | you already `rm -rf`'d it before the push; the pushed tree is clean | your `tree` output |

Not fixed, tracked: per-node ed25519 signatures (idgov envelope has the field, core does not
enforce), at-rest DB encryption, real-time webcam avatar mode.
