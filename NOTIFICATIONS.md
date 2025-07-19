# KTMB Scraper - Telegram Notifications

This module adds Telegram notification support to the KTMB Scraper. It will send notifications when trains are available based on your search criteria.

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the bot token (you'll need it for configuration)

### 2. Get Your Chat ID

1. Start a conversation with your bot
2. Send any message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `chat.id` field in the response

### 3. Configure Environment Variables

Copy the `.env.example` file to `.env` and fill in your details:

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
# Telegram Bot Configuration
NOTIFICATION_TELEGRAM_ENABLED=true
NOTIFICATION_TELEGRAM_BOT_TOKEN=your_bot_token_here
NOTIFICATION_TELEGRAM_CHAT_ID=your_chat_id_here

# Notification Settings
NOTIFICATION_MIN_SEATS=1
NOTIFICATION_ONLY_AVAILABLE=true
```

## Usage

### Basic Usage

```python
from dotenv import load_dotenv
from scraper.main import KTMBShuttleScraper
from config import ScraperSettings, Direction, TimeSlot
from notifications import create_notification_sender
from datetime import date

# Load environment variables
load_dotenv()

# Create notification sender
notification_sender = create_notification_sender()

# Configure search
settings = ScraperSettings(
    direction=Direction.SG_TO_JB,
    depart_date=date(2025, 1, 10),
    num_adults=1,
    min_available_seats=1,
    desired_time_slots=[TimeSlot.EVENING]
)

# Run scraper
scraper = KTMBShuttleScraper(settings)
result = scraper.run()

# Send notification if trains are available
notification_sender.send_notification(result, settings)
```

### Example Script

Run the example script to test notifications:

```bash
python example_with_notifications.py
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `NOTIFICATION_TELEGRAM_ENABLED` | Enable/disable Telegram notifications | `false` |
| `NOTIFICATION_TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `NOTIFICATION_TELEGRAM_CHAT_ID` | Your Telegram chat ID | Required |
| `NOTIFICATION_MIN_SEATS` | Minimum seats required to trigger notification | `1` |
| `NOTIFICATION_ONLY_AVAILABLE` | Only send notifications when trains are available | `true` |

## Notification Content

The notification will include:

- **Subject**: Status and date (e.g., "🚂 KTMB Trains Available - Friday, 10 January 2025")
- **Body**: 
  - Search date and direction
  - Available trains with seat counts
  - Color-coded seat availability (🟢 5+ seats, 🟡 2-4 seats, 🔴 1 seat)
  - Timestamp of when the search was performed

## Integration with Existing Code

To add notifications to your existing scraper code:

```python
# Add these imports
from dotenv import load_dotenv
from notifications import create_notification_sender

# Load environment variables
load_dotenv()

# Create notification sender
notification_sender = create_notification_sender()

# After running your scraper
result = scraper.run()

# Send notification
notification_sender.send_notification(result, settings)
```

## Troubleshooting

### Common Issues

1. **"Telegram notifications are disabled"**
   - Check that `NOTIFICATION_TELEGRAM_ENABLED=true` in your `.env` file

2. **"Bot token not configured"**
   - Make sure `NOTIFICATION_TELEGRAM_BOT_TOKEN` is set correctly

3. **"Chat ID not configured"**
   - Verify `NOTIFICATION_TELEGRAM_CHAT_ID` is correct

4. **"Failed to send Telegram notification"**
   - Check that your bot token is valid
   - Ensure you've started a conversation with your bot
   - Verify the chat ID is correct

### Testing Your Bot

You can test your bot configuration by sending a test message:

```python
import requests

bot_token = "your_bot_token"
chat_id = "your_chat_id"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "Test message from KTMB Scraper"
}

response = requests.post(url, json=payload)
print(response.json())
```

## Security Notes

- Keep your bot token secure and never commit it to version control
- Use `.env` files for local development
- Consider using environment variables in production
- The bot token gives full access to your bot, so keep it private 