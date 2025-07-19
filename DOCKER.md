# KTMB Scraper Docker Setup

This document explains how to use the Docker setup for the KTMB scraper to run it on-demand or schedule it for automated execution using the Makefile.

## Quick Start

### 1. Build the Docker Image

```bash
# Build the image
make build

# Or build without cache (if you have issues)
make build-no-cache
```

### 2. Run a Simple Search

```bash
# Search for a specific date
make search DATE=2025-01-15 DIRECTION=jb_to_sg

# Or use docker-compose directly
docker-compose run --rm ktmb-scraper python ktmb_search.py --date 2025-01-15 --direction jb_to_sg
```

## Available Commands

### Using the Makefile

The `Makefile` provides easy access to all operations:

```bash
# Show all available commands
make help

# Build the Docker image
make build

# Search for a specific date
make search DATE=2025-01-15 DIRECTION=jb_to_sg

# Monitor until seats become available
make monitor DATE=2025-01-15 SEATS=2 INTERVAL=300

# Search all weekends in a date range
make weekend START=2025-01-01 END=2025-01-31

# Search all Fridays in a month
make friday YEAR=2025 MONTH=1

# Search all Sundays in a month
make sunday YEAR=2025 MONTH=1

# Run with custom arguments
make custom ARGS="--date 2025-01-15 --telegram-token YOUR_TOKEN --telegram-chat-id YOUR_CHAT_ID"

# Run pre-configured services
make monitor-service
make weekend-service
```

### Using Docker Compose Directly

```bash
# Basic search
docker-compose run --rm ktmb-scraper python ktmb_search.py --date 2025-01-15 --direction jb_to_sg

# Monitor mode
docker-compose run --rm ktmb-scraper python ktmb_search.py --date 2025-01-15 --monitor --target-seats 2 --check-interval 300

# Weekend search
docker-compose run --rm ktmb-scraper python ktmb_search.py --start-date 2025-01-01 --end-date 2025-01-31 --weekend-only

# With Telegram notifications
docker-compose run --rm ktmb-scraper python ktmb_search.py --date 2025-01-15 --telegram-token YOUR_TOKEN --telegram-chat-id YOUR_CHAT_ID
```

## Scheduling and Automation

### Using Cron Jobs

The Makefile includes scheduling commands:

```bash
# Setup daily check at 8 AM
make schedule-cron SCHEDULE='0 8 * * *' COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'

# Setup monitoring every 6 hours
make schedule-cron SCHEDULE='0 */6 * * *' COMMAND='monitor DATE=2025-01-15 SEATS=2 INTERVAL=300'

# Setup weekend search every Friday at 9 AM
make schedule-cron SCHEDULE='0 9 * * 5' COMMAND='weekend START=2025-01-01 END=2025-01-31'

# List current jobs
make list-jobs

# Remove a job (by line number)
make remove-job JOB_ID=1
```

### Using Systemd Timers

For more advanced scheduling with systemd:

```bash
# Setup daily timer
make schedule-systemd NAME=daily-check SCHEDULE=daily COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'

# Setup custom schedule (every 4 hours)
make schedule-systemd NAME=monitor-4h SCHEDULE='OnCalendar=*:0/4' COMMAND='monitor DATE=2025-01-15 SEATS=2 INTERVAL=300'

# Check timer status
sudo systemctl status ktmb-daily-check.timer

# View logs
sudo journalctl -u ktmb-daily-check.service
```

## Configuration

### Environment Variables

Create a `.env` file in the project root for configuration:

```bash
# Telegram notifications
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Browser settings
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=60000

# Scraper settings
MIN_AVAILABLE_SEATS=2
CHECK_INTERVAL=300
```

### Docker Compose Services

The `docker-compose.yml` file includes three pre-configured services:

1. **ktmb-scraper**: Basic scraper service
2. **ktmb-monitor**: Pre-configured for monitoring
3. **ktmb-weekend-search**: Pre-configured for weekend searches

You can run these directly:

```bash
# Run the monitoring service
make monitor-service

# Run the weekend search service
make weekend-service
```

## Output and Results

### Output Directory

Results are saved to the `output/` directory, which is mounted as a volume:

```bash
# View results
ls -la output/

# View latest results
cat output/ktmb_*.json | jq '.'
```

### Logs

View container logs:

```bash
# View logs from the last run
make logs

# Follow logs in real-time
make logs-follow
```

## Advanced Usage

### Custom Docker Commands

```bash
# Run with custom environment variables
docker-compose run --rm -e PLAYWRIGHT_HEADLESS=false ktmb-scraper python ktmb_search.py --date 2025-01-15

# Run with custom volume mounts
docker-compose run --rm -v $(pwd)/custom-output:/app/output ktmb-scraper python ktmb_search.py --date 2025-01-15

# Run with resource limits
docker-compose run --rm --memory=512m --cpus=1 ktmb-scraper python ktmb_search.py --date 2025-01-15
```

### Debugging

```bash
# Run with browser visible (for debugging)
make debug DATE=2025-01-15 DIRECTION=jb_to_sg

# Run with increased timeout
docker-compose run --rm -e PLAYWRIGHT_TIMEOUT=120000 ktmb-scraper python ktmb_search.py --date 2025-01-15

# Access container shell
make shell

# Access debug container shell
make debug-shell

# Test network connectivity
make test
```

### Utility Commands

```bash
# Show Docker container status
make status

# Clean up Docker resources
make clean

# Show example commands
make examples
```

## Production Deployment

For production use, consider:

1. **Resource Limits**: Set appropriate memory and CPU limits
2. **Logging**: Configure proper logging to external systems
3. **Monitoring**: Set up health checks and monitoring
4. **Security**: Run as non-root user (already configured)
5. **Backup**: Regularly backup the output directory

Example production docker-compose:

```yaml
version: '3.8'
services:
  ktmb-scraper:
    build: .
    container_name: ktmb-scraper-prod
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - PLAYWRIGHT_HEADLESS=true
      - PLAYWRIGHT_TIMEOUT=60000
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('https://shuttleonline.ktmb.com.my')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Troubleshooting

### Common Issues

1. **Browser Installation Fails**
   ```bash
   # Rebuild with fresh browser installation
   make build-no-cache
   ```

2. **Permission Issues**
   ```bash
   # Fix script permissions
   chmod +x scripts/*.sh
   ```

3. **Network Issues**
   ```bash
   # Test network connectivity
   make test
   ```

4. **Memory Issues**
   ```bash
   # Increase memory limit
   docker-compose run --rm --memory=2g ktmb-scraper python ktmb_search.py --date 2025-01-15
   ```

### Getting Help

```bash
# Show help for all commands
make help

# Show example commands
make examples

# Show available arguments
docker-compose run --rm ktmb-scraper python ktmb_search.py --help
```

## Security Considerations

1. **Non-root User**: The container runs as a non-root user for security
2. **Minimal Base Image**: Uses Python slim image to reduce attack surface
3. **Volume Mounts**: Only necessary directories are mounted
4. **Environment Variables**: Sensitive data should be passed via environment variables
5. **Network Isolation**: Container has limited network access

## Performance Tips

1. **Resource Allocation**: Monitor memory and CPU usage, adjust limits as needed
2. **Caching**: The Docker image caches dependencies for faster builds
3. **Parallel Execution**: Run multiple searches in parallel using different containers
4. **Scheduling**: Use appropriate intervals to avoid overwhelming the target website
5. **Logging**: Use structured logging for better performance monitoring

## Makefile Reference

### Build Commands
- `make build` - Build Docker image
- `make build-no-cache` - Build without cache
- `make clean` - Clean up Docker resources

### Run Commands
- `make run` - Run with default settings
- `make search DATE=... DIRECTION=...` - Search specific date
- `make monitor DATE=... SEATS=... INTERVAL=...` - Monitor for seats
- `make weekend START=... END=...` - Search weekends
- `make friday YEAR=... MONTH=...` - Search Fridays
- `make sunday YEAR=... MONTH=...` - Search Sundays
- `make custom ARGS="..."` - Run with custom arguments

### Service Commands
- `make monitor-service` - Run monitoring service
- `make weekend-service` - Run weekend search service

### Scheduling Commands
- `make schedule-cron SCHEDULE=... COMMAND=...` - Setup cron job
- `make schedule-systemd NAME=... SCHEDULE=... COMMAND=...` - Setup systemd timer
- `make list-jobs` - List scheduled jobs
- `make remove-job JOB_ID=...` - Remove scheduled job

### Utility Commands
- `make logs` - View container logs
- `make logs-follow` - Follow logs in real-time
- `make shell` - Access container shell
- `make test` - Test network connectivity
- `make status` - Show container status

### Debug Commands
- `make debug DATE=... DIRECTION=...` - Run with browser visible
- `make debug-shell` - Access debug container shell

### Help Commands
- `make help` - Show all available commands
- `make examples` - Show example commands 