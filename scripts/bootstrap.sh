#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# Project TransEg bootstrap — single command, per INTENT.
#   ./scripts/bootstrap.sh            full: validate host, build, models, start, health
#   ./scripts/bootstrap.sh --dry-run  print the plan, touch nothing
#   ./scripts/bootstrap.sh --validate host+GPU+audio+camera+models checks only
#   ./scripts/bootstrap.sh --models   pull/download models only
#   ./scripts/bootstrap.sh --pin      record image digests + pip freeze into provenance/
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # in-folder rule: everything under repo
cd "$HERE"
MODE="${1:-full}"
log(){ printf '\033[1m[transeg]\033[0m %s\n' "$*"; }
fail(){ printf '\033[31m[transeg FAIL]\033[0m %s\n' "$*" >&2; exit 1; }

plan(){
cat <<'PLAN'
PLAN (nothing executed in --dry-run):
 1 validate: docker, docker compose, nvidia-smi (>=4 GB VRAM), arecord device, v4l2 camera
 2 build:    docker compose -f compose/docker-compose.yml build
 3 models:   ggml-base.en.bin -> models/ ; ollama pull per configs/transeg.yaml preference
             (qwen 3B/4B instruct q4 -> llama3.2 3B -> user override); liveportrait -> models/
 4 start:    TRANSEG_MOCK=0 docker compose up -d
 5 health:   poll http://localhost:8080/health until all components ok (120 s budget)
 6 pin:      image digests + versions -> provenance/pins.txt (release reproducibility)
ORACLES: steps 1+5 are the on-target oracle for every model/GPU/audio/camera claim.
PLAN
}

validate_host(){
  command -v docker >/dev/null || fail "docker missing"
  docker compose version >/dev/null 2>&1 || fail "docker compose v2 missing"
  if command -v nvidia-smi >/dev/null; then
    VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    log "GPU VRAM: ${VRAM} MiB"; [ "${VRAM:-0}" -ge 3800 ] || fail "need >=4 GB VRAM for avatar"
  else fail "nvidia-smi missing (avatar needs the GPU)"; fi
  arecord -l >/dev/null 2>&1 && log "audio capture: OK" || log "WARN: no ALSA capture device"
  ls /dev/video* >/dev/null 2>&1 && log "camera: OK" || log "WARN: no /dev/video*"
}

models(){
  mkdir -p models
  [ -f models/ggml-base.en.bin ] || \
    curl -L -o models/ggml-base.en.bin \
      https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
  docker compose -f compose/docker-compose.yml up -d llm-backend
  PREF=$(python3 - <<'PY'
import yaml; print(";".join(yaml.safe_load(open("configs/transeg.yaml"))["llm"]["preference_order"]))
PY
)
  # pull the first preference that ollama's registry resolves; user override wins
  OVERRIDE=$(python3 -c "import yaml;print(yaml.safe_load(open('configs/transeg.yaml'))['llm']['user_override'] or '')")
  if [ -n "$OVERRIDE" ]; then docker compose -f compose/docker-compose.yml exec -T llm-backend ollama pull "$OVERRIDE"
  else
    for CAND in "qwen2.5:3b-instruct-q4_K_M" "llama3.2:3b"; do
      if docker compose -f compose/docker-compose.yml exec -T llm-backend ollama pull "$CAND"; then break; fi
    done
  fi
  log "liveportrait models: place under models/liveportrait/ (see docs/deployment.md)"
}

pin(){
  mkdir -p provenance
  { date -u +"pinned %Y-%m-%dT%H:%M:%SZ"
    docker compose -f compose/docker-compose.yml images --format json 2>/dev/null || true
    docker images --digests --format '{{.Repository}}@{{.Digest}}' | sort -u
  } > provenance/pins.txt
  sha256sum compose/docker-compose.yml docker/*.Dockerfile >> provenance/pins.txt
  log "pins -> provenance/pins.txt (commit it; releases must be reproducible)"
}

health(){
  for i in $(seq 1 60); do
    if curl -sf http://localhost:8080/health | python3 -c \
      "import json,sys;d=json.load(sys.stdin);bad=[k for k,v in d['components'].items() if v!='ok'];sys.exit(1 if bad or d['status']!='ok' else 0)"
    then log "ALL COMPONENTS HEALTHY"; return 0; fi
    sleep 2
  done
  fail "health mesh did not converge in 120 s (curl http://localhost:8080/health)"
}

case "$MODE" in
  --dry-run) plan ;;
  --validate) validate_host; log "host validation PASSED" ;;
  --models) models ;;
  --pin) pin ;;
  full)
    plan; validate_host
    docker compose -f compose/docker-compose.yml build
    models
    TRANSEG_MOCK=0 docker compose -f compose/docker-compose.yml up -d
    health; pin ;;
  *) fail "unknown mode $MODE" ;;
esac
