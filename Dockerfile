FROM python:3.11-slim

WORKDIR /app

# System libraries EasyOCR / OpenCV need at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first (better layer caching).
COPY requirements.txt ./
COPY web/requirements.txt ./web/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r web/requirements.txt

COPY . .

# Keep model downloads inside the container (self-contained).
ENV HF_HOME=/app/.cache/huggingface
ENV FORCE_CPU=1

EXPOSE 8000
CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "8000"]
