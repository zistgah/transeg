# Reproducibility guide
<!-- content CC-BY-SA-4.0 -->
Everything needed to reproduce v0.1 is in-repo: compose + Dockerfiles (no host installs of
CUDA/Python/Torch/TensorRT), configs/transeg.yaml, and scripts/bootstrap.sh. After a
successful bring-up, provenance/pins.txt records image digests and file hashes — commit it.
Releases are tarred, sha256-summed, and OpenTimestamps-stamped by
scripts/zistgah_seed_transeg.sh --ots. Models are versioned and attributable: whisper
ggml-base.en.bin by upstream hash, the LLM by its ollama tag recorded in the /models
endpoint output, liveportrait weights by the files placed under models/liveportrait/.
CI verification is deterministic (mock mode, in-process ASGI, no network). The identity
model and its schemas are reproducible from zistgah/transeg-idgov; benchmark methodology
from zistgah/transeg-research. Developer guide: read INTENT.md, CONTRACT.md, CONTEXT.md,
then tests/ — the tests are the executable specification. User guide: README quick start
plus docs/deployment.md.
