# ==============================================================================
# Production Dockerfile for Top-Down AI Trading Agent
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for rapid dependency installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Final minimal runtime image
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy installed site-packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root system user for security
RUN useradd -m -u 1001 trader && \
    mkdir -p /app/logs && \
    chown -R trader:trader /app

# Copy application source
COPY --chown=trader:trader . /app

USER trader

ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    PYTHONPATH=/app

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
  CMD python -c "from health_check import run_health_checks; import sys; sys.exit(0 if run_health_checks() else 1)"

CMD ["python", "main.py"]
