# 🐳 Docker Run Commands for KTMB Scraper

This guide shows you how to run the KTMB scraper container with environment variables for configuration.

## 🔧 Environment Variables

The KTMB scraper supports the following environment variables:

### Notification Settings
- `NOTIFICATION_TELEGRAM_ENABLED` - Enable Telegram notifications (true/false)
- `NOTIFICATION_TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `NOTIFICATION_TELEGRAM_CHAT_ID` - Your Telegram chat ID
- `NOTIFICATION_MIN_SEATS` - Minimum seats threshold for notifications (default: 1)
- `NOTIFICATION_ONLY_AVAILABLE` - Only notify when trains are available (true/false)

### Browser Settings
- `PLAYWRIGHT_HEADLESS` - Run browser in headless mode (true/false)
- `PLAYWRIGHT_TIMEOUT` - Browser timeout in milliseconds (default: 30000)

### Scraper Settings
- `MIN_AVAILABLE_SEATS` - Minimum available seats to consider (default: 1)
- `CHECK_INTERVAL` - Monitoring check interval in seconds (default: 300)

## 🚀 Basic Docker Run Commands

### 1. Simple Search
```bash
docker run --rm \
  -v $(pwd)/output:/app/output \
  ktmb-scraper:latest \
  python -u ktmb_search.py --date 2025-01-15 --direction jb_to_sg
```

### 2. Search with Telegram Notifications
```bash
docker run --rm -v $(pwd)/output:/app/output -e NOTIFICATION_TELEGRAM_ENABLED=true -e NOTIFICATION_TELEGRAM_BOT_TOKEN=<> -e NOTIFICATION_TELEGRAM_CHAT_ID=<> ethannjw/ktmb-scraper:latest python -u monitor.py --continuous --interval 60
```
