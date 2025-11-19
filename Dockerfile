# PROJ344 Dashboards - Docker Configuration

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY dashboards/ ./dashboards/
COPY scanners/ ./scanners/
COPY scripts/ ./scripts/
COPY core/ ./core/
COPY README.md .

# Expose Streamlit ports
EXPOSE 8501 8502 8503

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Default: Run PROJ344 Master Dashboard
ENTRYPOINT ["streamlit", "run", "dashboards/proj344_master_dashboard.py"]
CMD ["--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
