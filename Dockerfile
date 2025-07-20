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
COPY config.py ./
COPY ktmb_search.py ./
COPY example_with_notifications.py ./
COPY notifications.py ./
COPY monitor.py ./

# Install uv for dependency management
RUN pip install uv

# Install Python dependencies directly using uv
RUN uv pip install --system click>=8.0.0 playwright>=1.40.0 pydantic>=2.0.0 python-dateutil>=2.8.0 requests>=2.25.0 python-dotenv>=1.0.0

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Create a non-root user for security
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app

# Install Playwright browsers as root (needed for system dependencies)
RUN playwright install --with-deps chromium

# Ensure the scraper user has access to the Playwright browsers
RUN chown -R scraper:scraper /ms-playwright

# Switch to non-root user
USER scraper

# Default command (can be overridden)
CMD ["python", "ktmb_search.py", "--help"] 