# ASEAGI Vast.ai GPU Worker
# GPU-accelerated document processing

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /worker

# Copy requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy worker script
COPY worker.py .
COPY process_document.py .

# Environment variables (will be overridden by Vast.ai)
ENV SUPABASE_URL=""
ENV SUPABASE_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV S3_ENDPOINT=""
ENV S3_ACCESS_KEY=""
ENV S3_SECRET_KEY=""
ENV S3_BUCKET=""

# Run worker
CMD ["python3", "worker.py"]
