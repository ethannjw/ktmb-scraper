# KTMB Monitoring Guide

This guide explains how to use the continuous monitoring script to automatically check for train availability at specified intervals.

## Quick Start

### 1. Single Search (No Monitoring)
```bash
# Search once for a specific date
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --once
```

### 2. Continuous Monitoring
```bash
# Monitor every 30 minutes (default)
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg

# Monitor every 15 minutes
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 15

# Monitor every hour
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 60
```

### 3. Weekend Monitoring
```bash
# Monitor all weekends in August 2025 every 2 hours
docker-compose run --rm ktmb-scraper python monitor.py --weekends --year 2025 --month 8 --interval 120
```

## Command Line Options

### Required Arguments
- `--date DATE` or `-d DATE`: Specific date to search (YYYY-MM-DD format)
- `--weekends` or `-w`: Search weekends in a month (requires --year and --month)

### Optional Arguments
- `--year YEAR` or `-y YEAR`: Year for weekend search (required with --weekends)
- `--month MONTH` or `-m MONTH`: Month for weekend search (1-12, required with --weekends)
- `--direction {sg-to-jb,jb-to-sg}` or `-dir {sg-to-jb,jb-to-sg}`: Direction (default: sg-to-jb)
- `--time-slots {early_morning,morning,afternoon,evening,night}` or `-t {early_morning,morning,afternoon,evening,night}`: Time slots to search for (default: evening). Can specify multiple: `--time-slots morning evening`
- `--interval INTERVAL` or `-i INTERVAL`: Interval between checks in minutes (default: 30)
- `--once`: Run only once (no continuous monitoring)

## Examples

### Monitor Specific Date
```bash
# Monitor August 15, 2025 from JB to Singapore every 30 minutes (default: evening trains)
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg

# Monitor August 15, 2025 from Singapore to JB every 15 minutes with morning and evening trains
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction sg-to-jb --time-slots morning evening --interval 15

# Monitor specific date with morning trains only
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --time-slots morning --interval 30
```

### Monitor Weekends
```bash
# Monitor all weekends in August 2025 every hour
docker-compose run --rm ktmb-scraper python monitor.py --weekends --year 2025 --month 8 --interval 60

# Monitor all weekends in September 2025 every 2 hours
docker-compose run --rm ktmb-scraper python monitor.py --weekends --year 2025 --month 9 --interval 120
```

### Single Searches
```bash
# Search once for a specific date (default: evening trains)
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --once

# Search once for afternoon trains only
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --time-slots afternoon --once

# Search once for weekends in August 2025
docker-compose run --rm ktmb-scraper python monitor.py --weekends --year 2025 --month 8 --once
```

## Features

### 🚂 Continuous Monitoring
- Runs searches at specified intervals
- Graceful shutdown with Ctrl+C
- Error handling with automatic retry

### 📊 Real-time Results
- Shows available trains with seat counts
- Color-coded availability (🟢 5+ seats, 🟡 2-4 seats, 🔴 1 seat)
- Timestamps for each search

### 🔔 Notifications
- Integrates with Telegram notifications (if configured)
- Only sends notifications when trains are available
- Configurable minimum seat threshold

### 🛑 Graceful Shutdown
- Press Ctrl+C to stop monitoring
- Waits for current search to complete
- Clean exit with status message

## Configuration

### Environment Variables
The monitoring script uses the same environment variables as the main scraper:

```bash
# Telegram notifications (optional)
NOTIFICATION_TELEGRAM_ENABLED=true
NOTIFICATION_TELEGRAM_BOT_TOKEN=your_bot_token
NOTIFICATION_TELEGRAM_CHAT_ID=your_chat_id

# Notification settings
NOTIFICATION_MIN_SEATS=1
NOTIFICATION_ONLY_AVAILABLE=true
```

### Interval Recommendations
- **15 minutes**: High-frequency monitoring for urgent needs
- **30 minutes**: Standard monitoring (default)
- **60 minutes**: Daily checks
- **120 minutes**: Weekend monitoring
- **240 minutes**: Long-term monitoring

## Running in Background

### Using Docker Compose
```bash
# Run in background
docker-compose run -d --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 30

# Check logs
docker-compose logs -f ktmb-scraper
```

### Using Screen/Tmux
```bash
# Start a screen session
screen -S ktmb-monitor

# Run the monitoring command
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 30

# Detach from screen: Ctrl+A, then D
# Reattach: screen -r ktmb-monitor
```

## Troubleshooting

### Common Issues

1. **Script stops unexpectedly**
   - Check Docker logs: `docker-compose logs ktmb-scraper`
   - Ensure stable internet connection
   - Verify KTM website is accessible

2. **No notifications received**
   - Check Telegram bot configuration
   - Verify bot token and chat ID
   - Test with `--once` flag first

3. **High CPU/Memory usage**
   - Increase interval between checks
   - Monitor system resources
   - Consider running on dedicated server

### Logs and Debugging
```bash
# View real-time logs
docker-compose logs -f ktmb-scraper

# Check container status
docker-compose ps

# Restart monitoring
docker-compose restart ktmb-scraper
```

## Advanced Usage

### Custom Monitoring Scripts
You can create custom monitoring scripts by importing the `KTMBMonitor` class:

```python
from monitor import KTMBMonitor
from datetime import date
from config import Direction

# Create monitor with 15-minute interval
monitor = KTMBMonitor(interval_minutes=15)

# Run custom monitoring logic
monitor.run_continuous_monitoring(
    "specific_date",
    date=date(2025, 8, 15),
    direction=Direction.JB_TO_SG
)
```

### Integration with Cron
For scheduled monitoring, you can use cron jobs:

```bash
# Add to crontab (every 2 hours)
0 */2 * * * cd /path/to/ktmb-scraper && docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --once
```

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify your configuration
3. Test with `--once` flag first
4. Check the main README.md for general troubleshooting 