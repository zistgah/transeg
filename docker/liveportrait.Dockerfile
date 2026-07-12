# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# FasterLivePortrait server — the sole GPU tenant. Built (not pulled) so CUDA/TensorRT
# stay inside the container per INTENT Container Requirements. Verified only on-target.
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y --no-install-recommends git python3 python3-pip ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/warmshao/FasterLivePortrait /opt/flp
WORKDIR /opt/flp
RUN pip3 install --no-cache-dir -r requirements.txt || true   # resolved+pinned by bootstrap.sh --pin on target
COPY docker/liveportrait_server.py /opt/flp/server.py
EXPOSE 8093
CMD ["python3", "server.py", "--host", "0.0.0.0", "--port", "8093", "--models", "/models/liveportrait"]
