# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock ./
COPY scraper/ ./scraper/
COPY utils/ ./utils/
COPY monitor.py ./

# Install uv for dependency management
RUN pip install uv

# Install Python dependencies directly using uv
RUN uv pip install --system click>=8.0.0 playwright>=1.40.0 pydantic>=2.0.0 python-dateutil>=2.8.0 requests>=2.25.0 python-dotenv>=1.0.0

RUN mkdir -p output logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Expose healthcheck port
EXPOSE 8080

# Add Docker healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
