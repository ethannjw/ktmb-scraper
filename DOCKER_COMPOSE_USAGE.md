# Docker Compose Usage Guide

This guide shows how to use the updated docker-compose services for KTMB monitoring with intervals.

## Available Services

### 1. `ktmb-scraper` - Main Scraper Service
For one-time searches and basic functionality.

### 2. `ktmb-monitor` - Date-Specific Monitoring
For continuous monitoring of specific dates with configurable intervals.



## Quick Examples

### Single Search (No Monitoring)
```bash
# Search for a specific date once
docker-compose run --rm ktmb-scraper python ktmb_search.py --date 2025-08-15 --direction jb-to-sg

# Search for weekends in August 2025
docker-compose run --rm ktmb-scraper python ktmb_search.py --month 8 --year 2025 --fridays-only
```

### Continuous Monitoring with Intervals

#### Monitor Specific Date
```bash
# Monitor August 15, 2025 every 30 minutes (default)
docker-compose run --rm ktmb-monitor

# Monitor with custom interval (15 minutes)
docker-compose run --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 15

# Monitor with custom interval (1 hour)
docker-compose run --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 60
```



## Advanced Usage

### Override Default Commands
All services allow you to override their default commands:

```bash
# Use any service with custom parameters
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-09-20 --direction sg-to-jb --interval 45

# Single search using monitor script
docker-compose run --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --once
```

### Background Monitoring
```bash
# Run monitoring in background
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 30

# Check logs
docker-compose logs -f ktmb-monitor

# Stop background monitoring
docker-compose stop ktmb-monitor
```

### Multiple Monitoring Sessions
```bash
# Monitor different dates simultaneously
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 30
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-22 --direction sg-to-jb --interval 45


```

## Service Configuration

### Default Commands
- **ktmb-scraper**: `python ktmb_search.py --help`
- **ktmb-monitor**: `python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 30`

### Environment Variables
All services support these environment variables:
- `PLAYWRIGHT_HEADLESS=true` - Run browser in headless mode
- `PLAYWRIGHT_TIMEOUT=60000` - Browser timeout in milliseconds
- Telegram notification variables (from .env file)

### Resource Limits
- Memory limit: 1GB
- Memory reservation: 512MB
- CPU: No specific limits (uses host CPU)

## Monitoring Best Practices

### Interval Recommendations
- **15 minutes**: High-frequency monitoring for urgent needs
- **30 minutes**: Standard monitoring (default)
- **60 minutes**: Daily checks
- **120 minutes**: Weekend monitoring
- **240 minutes**: Long-term monitoring

### Notification Setup
1. Create a `.env` file with Telegram credentials:
```bash
NOTIFICATION_TELEGRAM_ENABLED=true
NOTIFICATION_TELEGRAM_BOT_TOKEN=your_bot_token
NOTIFICATION_TELEGRAM_CHAT_ID=your_chat_id
```

2. Test notifications with single search:
```bash
docker-compose run --rm ktmb-scraper python monitor.py --date 2025-08-15 --direction jb-to-sg --once
```

### Logging and Debugging
```bash
# View real-time logs
docker-compose logs -f ktmb-monitor

# Check container status
docker-compose ps

# Restart a service
docker-compose restart ktmb-monitor

# Stop all services
docker-compose down
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Rebuild the image
   docker-compose build --no-cache
   
   # Check for errors
   docker-compose logs ktmb-monitor
   ```

2. **Monitoring stops unexpectedly**
   ```bash
   # Check resource usage
   docker stats
   
   # Increase memory limits in docker-compose.yml if needed
   ```

3. **No notifications received**
   ```bash
   # Verify .env file is mounted
   docker-compose run --rm ktmb-monitor cat /app/.env
   
   # Test notifications manually
   docker-compose run --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --once
   ```

### Performance Optimization
- Use longer intervals for less critical monitoring
- Monitor system resources with `docker stats`
- Consider running on dedicated server for 24/7 monitoring
- Use background mode (`-d` flag) for long-running monitoring

## Examples for Different Use Cases



### Last-Minute Booking
```bash
# Monitor specific date every 15 minutes for urgent booking
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 15
```

### Regular Commuting
```bash
# Monitor next week's Friday commute every hour
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-22 --direction sg-to-jb --interval 60
```

### Multiple Routes
```bash
# Monitor both directions for the same date
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction jb-to-sg --interval 30
docker-compose run -d --rm ktmb-monitor python monitor.py --date 2025-08-15 --direction sg-to-jb --interval 30
``` 