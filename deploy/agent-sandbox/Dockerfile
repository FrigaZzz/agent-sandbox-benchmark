# Official Kubernetes-SIGs Agent-Sandbox Container Image
# https://github.com/kubernetes-sigs/agent-sandbox
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and OpenMP
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install AI/data packages and FastAPI runtime
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    pydantic \
    requests \
    numpy \
    pandas \
    scipy \
    psutil

# Copy sandbox server code
COPY server.py /app/main.py

# Run as unprivileged non-root user (UID 1000) for security isolation
RUN mkdir -p /tmp/agent-sandbox-data && chown -R 1000:1000 /app /tmp/agent-sandbox-data
USER 1000

ENV SANDBOX_BASE_DIR=/tmp/agent-sandbox-data
ENV PORT=8888

EXPOSE 8888

# Launch Uvicorn ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]
