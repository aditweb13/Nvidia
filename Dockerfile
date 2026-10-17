FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (standard for Hugging Face Spaces uid 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Install python dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY --chown=user . $HOME/app

# Ensure directories exist and are writable
RUN mkdir -p data eval/results .cache/responses

# Expose ports: 7860 (Hugging Face default app port) and 8000 (FastAPI internal)
EXPOSE 7860 8000

RUN chmod +x scripts/entrypoint.sh

ENTRYPOINT ["bash", "scripts/entrypoint.sh"]
