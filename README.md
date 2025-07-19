# KTMB Shuttle Train Scraper

This tool automates the process of scraping train timings and seat availability from [KTMB Shuttle Online](https://shuttleonline.ktmb.com.my/Home/Shuttle).

## Features
- **Direction Switching**: Automatically switches between JB Sentral ↔ Woodlands CIQ directions
- **Date Selection**: Handles both departure and return date selection with date picker interaction
- **Passenger Configuration**: Supports 1-6 passengers with adult/child breakdown
- **Smart Search**: Performs searches and handles validation errors
- **Result Parsing**: Extracts train numbers, timings, and seat availability
- **Error Handling**: Robust error handling with detailed logging
- **Configurable**: Flexible settings for dates, directions, and passenger counts

## Installation
1. Install dependencies:
   ```bash
   uv sync
   uv run playwright install
   ```

## Usage

### Basic Usage
```python
from scraper.main import KTMBShuttleScraper
from config import ScraperSettings, Direction
from datetime import date

# Create settings
settings = ScraperSettings(
    direction=Direction.JB_TO_SG,  # JB Sentral -> Woodlands CIQ
    depart_date=date(2025, 7, 20),
    num_adults=2,
    min_available_seats=2
)

# Run scraper
scraper = KTMBShuttleScraper(settings)
results = scraper.run()
print(results)
```

### Round Trip Booking
```python
settings = ScraperSettings(
    direction=Direction.JB_TO_SG,
    depart_date=date(2025, 7, 20),
    return_date=date(2025, 7, 22),  # Return date
    num_adults=2,
    num_children=1,
    min_available_seats=3
)
```

### Different Direction
```python
settings = ScraperSettings(
    direction=Direction.SG_TO_JB,  # Woodlands CIQ -> JB Sentral
    depart_date=date(2025, 7, 20),
    num_adults=1,
    min_available_seats=1
)
```

### Running Tests
```bash
uv run python test_scraper.py
```

## Configuration

### ScraperSettings Options
- `direction`: `Direction.JB_TO_SG` or `Direction.SG_TO_JB`
- `depart_date`: Required departure date
- `return_date`: Optional return date for round trips
- `num_adults`: Number of adult passengers (1-9)
- `num_children`: Number of child passengers (0-9)
- `min_available_seats`: Minimum seats required for a train to be considered available

### Output Format
```json
{
  "success": true,
  "available_trains": [
    {
      "train_number": "TS1",
      "departure_time": "06:30",
      "arrival_time": "07:00",
      "available_seats": 45,
      "direction": "JB_TO_SG"
    }
  ],
  "total_available": 1,
  "search_criteria": {
    "direction": "JB_TO_SG",
    "depart_date": "2025-07-20",
    "return_date": null,
    "passengers": 2,
    "min_seats": 2
  },
  "scraped_at": "2025-07-16T14:30:00"
}
```

## How It Works

1. **Direction Selection**: Uses the swap button (↔) to toggle between directions
2. **Date Selection**: Clicks date fields and fills them directly with formatted dates
3. **Passenger Selection**: Selects from dropdown options (1-6 Pax)
4. **Search**: Clicks search button and waits for results or validation errors
5. **Parsing**: Extracts train information from the results table

## Error Handling

The scraper handles various scenarios:
- Validation errors (missing departure date)
- Network timeouts
- Missing elements
- Invalid data in results table

## Files
- `scraper/main.py` - Main scraper implementation
- `config.py` - Configuration and settings classes
- `test_scraper.py` - Test script with examples
- `SELECTOR_GUIDE.md` - Detailed element interaction guide
- `pyproject.toml` - Project configuration and dependencies

## Folder Structure
```
ktmb-scraper/
├── scraper/
│   ├── __init__.py
│   ├── main.py          # Main scraper class
│   └── ...
├── config.py            # Settings and configuration
├── test_scraper.py      # Test examples
├── SELECTOR_GUIDE.md    # Element interaction guide
├── pyproject.toml       # Project configuration and dependencies
└── README.md           # This file
```

---
**Note**: This project is for educational and personal use only. Please respect the website's terms of service and rate limiting policies. 