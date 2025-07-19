# KTMB Scraper Makefile Quick Reference

This document provides a quick reference for all available Makefile commands.

## 🚀 Quick Start

```bash
# Show all available commands
make help

# Build the Docker image
make build

# Search for a specific date
make search DATE=2025-01-15 DIRECTION=jb_to_sg
```

## 📋 Available Commands

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

## 🎯 Common Use Cases

### Basic Search
```bash
make search DATE=2025-01-15 DIRECTION=jb_to_sg
```

### Monitor for Seats
```bash
make monitor DATE=2025-01-15 SEATS=2 INTERVAL=300
```

### Search Weekends
```bash
make weekend START=2025-01-01 END=2025-01-31
```

### Custom Command with Telegram
```bash
make custom ARGS="--date 2025-01-15 --telegram-token YOUR_TOKEN --telegram-chat-id YOUR_CHAT_ID"
```

### Schedule Daily Check
```bash
make schedule-cron SCHEDULE='0 8 * * *' COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'
```

### Schedule Monitoring
```bash
make schedule-cron SCHEDULE='0 */6 * * *' COMMAND='monitor DATE=2025-01-15 SEATS=2 INTERVAL=300'
```

## 🔧 Parameters Reference

### Search Parameters
- `DATE` - Date in YYYY-MM-DD format
- `DIRECTION` - `jb_to_sg` (JB to Singapore) or `sg_to_jb` (Singapore to JB)

### Monitor Parameters
- `DATE` - Date in YYYY-MM-DD format
- `SEATS` - Number of seats to monitor for (default: 2)
- `INTERVAL` - Check interval in seconds (default: 300)

### Weekend Parameters
- `START` - Start date in YYYY-MM-DD format
- `END` - End date in YYYY-MM-DD format

### Friday/Sunday Parameters
- `YEAR` - Year (e.g., 2025)
- `MONTH` - Month (1-12)

### Custom Parameters
- `ARGS` - Full command line arguments as a string

### Scheduling Parameters
- `SCHEDULE` - Cron schedule (e.g., '0 8 * * *' for daily at 8 AM)
- `COMMAND` - Make command to run (e.g., 'search DATE=2025-01-15 DIRECTION=jb_to_sg')
- `NAME` - Name for systemd timer
- `JOB_ID` - Line number for cron jobs or name for systemd timers

## 📝 Examples

### Build and Test
```bash
make build
make test
```

### Search Different Directions
```bash
make search DATE=2025-01-15 DIRECTION=jb_to_sg
make search DATE=2025-01-15 DIRECTION=sg_to_jb
```

### Monitor with Different Settings
```bash
make monitor DATE=2025-01-15 SEATS=1 INTERVAL=600
make monitor DATE=2025-01-15 SEATS=4 INTERVAL=180
```

### Batch Searches
```bash
make friday YEAR=2025 MONTH=1
make sunday YEAR=2025 MONTH=1
make weekend START=2025-01-01 END=2025-01-31
```

### Debug Mode
```bash
make debug DATE=2025-01-15 DIRECTION=jb_to_sg
make debug-shell
```

### Scheduling Examples
```bash
# Daily morning check
make schedule-cron SCHEDULE='0 8 * * *' COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'

# Every 6 hours monitoring
make schedule-cron SCHEDULE='0 */6 * * *' COMMAND='monitor DATE=2025-01-15 SEATS=2 INTERVAL=300'

# Weekend search every Friday
make schedule-cron SCHEDULE='0 9 * * 5' COMMAND='weekend START=2025-01-01 END=2025-01-31'

# Systemd daily timer
make schedule-systemd NAME=daily-check SCHEDULE=daily COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'
```

## 🛠️ Troubleshooting

### View Logs
```bash
make logs
make logs-follow
```

### Test Connectivity
```bash
make test
```

### Access Shell
```bash
make shell
make debug-shell
```

### Clean Up
```bash
make clean
```

### List Scheduled Jobs
```bash
make list-jobs
```

### Remove Scheduled Job
```bash
make remove-job JOB_ID=1
make remove-job JOB_ID=daily-check
``` 