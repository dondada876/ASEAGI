# Batch Processor Dockerfile
# For processing 7TB Google Drive documents using Vast.ai GPU orchestration

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vastai_client.py .
COPY google_drive_sync.py .
COPY batch_manager.py .
COPY api_endpoints.py .

# Create directories for state and cache
RUN mkdir -p /app/batch_state /app/cache /app/credentials

# Environment variables (will be overridden by docker-compose)
ENV PYTHONUNBUFFERED=1
ENV SUPABASE_URL=""
ENV SUPABASE_KEY=""
ENV VAST_AI_API_KEY=""
ENV CLAUDE_API_KEY=""

# Expose API port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run batch processor API server
CMD ["uvicorn", "api_endpoints:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
