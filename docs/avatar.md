# Running the avatar on the target box
<!-- content CC-BY-SA-4.0 · © 1993-2026 Abhishek Choudhary · AyeAI -->

## What actually drives the face
FasterLivePortrait alone is **driving-video** animation. The audio-driven path is
FLP + **JoyVASA**: audio → motion sequence → LivePortrait warping → frames → ffmpeg
muxes the original audio back on. `docker/liveportrait_server.py` implements exactly
that path (mirrors FLP's own `run_audio_driving` and `api.py::run_with_pkl`, minus
gradio). TransEg's avatar adapter posts `{audio_b64, source_image_b64, fps}` to it.

The v0.1.0 tarball shipped a **stub** server that returned fake bytes. It is replaced.
Do not trust any avatar claim until `scripts/avatar_smoke.sh` writes a playable mp4.

## Three commands
```
scripts/avatar_setup.sh                     # FLP source + onnx + JoyVASA + hubert + silero
cp <your frontal portrait> models/liveportrait/source.png
docker compose -f compose/docker-compose.yml --profile tts up -d --build
scripts/avatar_smoke.sh                     # THE ORACLE: writes avatar_out.mp4 or fails
```

## RTX 3050, 4 GB — the real constraints
- The avatar is the sole GPU tenant. Ollama is pinned CPU (`OLLAMA_NUM_GPU=0`),
  whisper.cpp CPU, Silero CPU, Kokoro CPU. Do not "helpfully" give the LLM the GPU;
  the face will OOM.
- ONNX path works out of the box but is slow (seconds/frame is normal on 3050).
  TensorRT is the fast path: `scripts/avatar_setup.sh --trt` (one-time, 10–30 min),
  then run with `TRANSEG_FLP_CFG=configs/trt_infer.yaml`. Upstream needs **TensorRT 8.x**
  — the `shaoguo/faster_liveportrait:v3` image already carries it, which is why we use
  the upstream image instead of building CUDA ourselves.
- Rendering is offline-batch (a whole utterance at a time), not a live stream. Real-time
  webcam mode exists upstream (`run.py --realtime`) and needs the TRT path; it is a
  v0.2 quest, not a v0.1 claim.
- JoyVASA's shipped audio encoder is `chinese-hubert-base`; it drives Hindi/Urdu/English
  audio too (it is an acoustic encoder, not a language model) but lip-sync quality on
  non-Chinese phonetics is **unmeasured** — that is exactly what transeg-research
  benchmarks are for. Measure before claiming.

## Model licences (not GPL — check before you redistribute)
FLP code is MIT; LivePortrait/JoyVASA/hubert/Kokoro weights carry their own licences.
TransEg ships **no weights**; `avatar_setup.sh` fetches them to your disk. Keep it that way.

## Kokoro TTS
The tts service needs *an* endpoint returning audio for `{text, voice}`. The compose
entry is opt-in (`--profile tts`) and the image tag is **unverified** — pin your own:
`TRANSEG_KOKORO_IMAGE=... TRANSEG_KOKORO_URL=...`. Or skip TTS entirely and feed
`avatar_smoke.sh` any 16 kHz mono wav (your own recorded voice is the better Stage-1
artifact anyway).
