# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# VAD service: Silero ONNX in-process, CPU only (2.3 MB graph — no backend container).
FROM python:3.12-slim
WORKDIR /app
COPY services/common /app/common
COPY services/vad/app.py /app/app.py
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic numpy onnxruntime
ENV TRANSEG_MOCK=0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
