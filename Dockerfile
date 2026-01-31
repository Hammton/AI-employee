# PocketAgent - Unified Dockerfile (Python Backend)
# For the split architecture, use Dockerfile.python instead
# 
# This file is kept for backwards compatibility with single-container deployments
# For production, use docker-compose.yml with separate services

FROM python:3.11-slim

# Install system dependencies for optional features
RUN apt-get update && apt-get install -y \
    curl \
    libgbm-dev \
    libnss3 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxrandr2 \
    ca-certificates \
    fonts-liberation \
    libgtk-3-0 \
    procps \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY .env* ./

# Expose port for FastAPI
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application (using main_v2 with WPP Bridge architecture)
CMD ["uvicorn", "main_v2:app", "--host", "0.0.0.0", "--port", "8000"]
