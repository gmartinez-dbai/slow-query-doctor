# Multi-stage build for Slow Query Doctor
# Production-ready Docker image with minimal size and security best practices

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app
WORKDIR /app

# Install the package in the virtual environment
RUN pip install --no-cache-dir .

# Stage 2: Production stage
FROM python:3.11-slim as production

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    SLOW_QUERY_DOCTOR_VERSION=v0.1.8

# Create non-root user for security
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --shell /bin/bash --create-home appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --from=builder /app /app

# Create directories with proper permissions
RUN mkdir -p /app/logs /app/reports /app/input && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import slowquerydoctor; print('OK')" || exit 1

# Labels for metadata
LABEL maintainer="Giovanni Martinez <gio@iqtoolkit.ai>" \
      version="0.2.2a1" \
      description="AI-powered PostgreSQL slow query analyzer" \
      org.opencontainers.image.title="Slow Query Doctor" \
      org.opencontainers.image.description="AI-powered PostgreSQL performance analyzer" \
      org.opencontainers.image.version="0.2.2a1" \
      org.opencontainers.image.authors="Giovanni Martinez <gio@iqtoolkit.ai>" \
      org.opencontainers.image.source="https://github.com/iqtoolkit/slow-query-doctor" \
      org.opencontainers.image.licenses="MIT"

# Default command
ENTRYPOINT ["slow-query-doctor"]
CMD ["--help"]
LABEL version="0.2.2a1"
