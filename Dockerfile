# Use Python 3.11 slim image as base (pinned to Bookworm for Playwright compatibility)
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock ./
COPY scraper/ ./scraper/
COPY utils/ ./utils/
COPY monitor.py ./
COPY notifications/ ./notifications/


# Install uv for dependency management
RUN pip install uv

# Install Python dependencies from lockfile
RUN uv sync --frozen --no-dev --no-editable

RUN mkdir -p output logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PATH="/app/.venv/bin:$PATH"

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Expose healthcheck port
EXPOSE 8080

# Add Docker healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
