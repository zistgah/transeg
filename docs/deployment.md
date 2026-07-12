# Deployment guide
<!-- content CC-BY-SA-4.0 -->
Target: Ubuntu 26.04, Ryzen 7, 16 GB RAM, RTX 3050 (4 GB), Docker with the NVIDIA
container toolkit. Run `./scripts/bootstrap.sh` — it validates the host (docker, compose
v2, nvidia-smi ≥ 4 GB, ALSA capture, /dev/video*), builds all containers, fetches
ggml-base.en.bin into models/, pulls the LLM by preference order (qwen 3B/4B instruct q4,
then llama3.2:3b, unless configs/transeg.yaml user_override is set), starts the mesh with
TRANSEG_MOCK=0, polls the gateway health mesh for up to 120 s, and pins image digests into
provenance/pins.txt. FasterLivePortrait weights go under models/liveportrait/ (the
container mounts models/ read-only). Everything is local; networking beyond model download
is opt-in in configs/transeg.yaml. To run the mesh in mock mode for development on any
machine: TRANSEG_MOCK=1 docker compose -f compose/docker-compose.yml up.
