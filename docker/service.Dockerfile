# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
FROM python:3.12-slim
ARG SERVICE
WORKDIR /app
COPY services/common /app/common
COPY services/${SERVICE}/app.py /app/app.py
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic cryptography
ENV TRANSEG_MOCK=0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
