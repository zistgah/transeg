#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# Fetch everything the avatar (and VAD) need. In-folder only. Idempotent.
#   scripts/avatar_setup.sh            onnx path (works today, slower)
#   scripts/avatar_setup.sh --trt      + convert onnx -> TensorRT inside the FLP image (faster)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$HERE"
CK="models/liveportrait/checkpoints"
log(){ printf '\033[1m[avatar]\033[0m %s\n' "$*"; }

command -v huggingface-cli >/dev/null || pip install -U "huggingface_hub[cli]"

log "1/5 FasterLivePortrait source (MIT) -> third_party/"
[ -d third_party/FasterLivePortrait ] \
  || git clone --depth 1 https://github.com/warmshao/FasterLivePortrait third_party/FasterLivePortrait

log "2/5 LivePortrait ONNX models -> $CK"
mkdir -p "$CK"
huggingface-cli download warmshao/FasterLivePortrait --local-dir "$CK"

log "3/5 JoyVASA audio->motion + hubert audio encoder (this is what makes it AUDIO-driven)"
huggingface-cli download jdh-algo/JoyVASA --local-dir "$CK/JoyVASA"
huggingface-cli download TencentGameMate/chinese-hubert-base --local-dir "$CK/chinese-hubert-base"

log "4/5 Silero VAD onnx (2.3 MB, CPU) -> models/"
[ -f models/silero_vad.onnx ] || curl -fsSL -o models/silero_vad.onnx \
  https://raw.githubusercontent.com/snakers4/silero-vad/master/src/silero_vad/data/silero_vad.onnx

log "5/5 your face — the Stage 0 artifact"
if [ ! -f models/liveportrait/source.png ]; then
  echo "  PUT A FRONTAL PORTRAIT AT models/liveportrait/source.png (any size; one clear face)"
  echo "  it is never uploaded anywhere; it is mounted read-only into the avatar container"
fi

if [ "${1:-}" = "--trt" ]; then
  log "TensorRT conversion inside the FLP image (10-30 min, one time)"
  docker run --rm --gpus=all \
    -v "$HERE/third_party/FasterLivePortrait:/root/FasterLivePortrait" \
    -v "$HERE/$CK:/root/FasterLivePortrait/checkpoints" \
    -w /root/FasterLivePortrait shaoguo/faster_liveportrait:v3 \
    bash -lc "sh scripts/all_onnx2trt.sh"
  log "now run with: TRANSEG_FLP_CFG=configs/trt_infer.yaml docker compose -f compose/docker-compose.yml up -d"
fi
log "done. next: scripts/avatar_smoke.sh"
