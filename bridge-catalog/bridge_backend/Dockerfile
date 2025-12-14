# Dockerfile for SR-AIbridge Backend
# Build from repository root with: docker build -f bridge_backend/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire repository to maintain module structure
COPY . /app/

# Install dependencies from root requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check using curl
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Run the application
CMD ["uvicorn", "bridge_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
