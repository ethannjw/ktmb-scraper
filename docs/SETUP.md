# Setup Guide

This guide explains how to properly set up the KTMB Scraper project with all dependencies.

## Prerequisites

- Python 3.8 or higher
- uv package manager (recommended) or pip

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd ktmb-scraper
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
# Using uv (recommended)
uv pip install pydantic>=2.0.0 playwright>=1.40.0 python-dotenv>=1.0.0 requests>=2.25.0 python-dateutil>=2.8.0 click>=8.0.0

# Or using pip
pip install pydantic>=2.0.0 playwright>=1.40.0 python-dotenv>=1.0.0 requests>=2.25.0 python-dateutil>=2.8.0 click>=8.0.0
```

### 4. Install Playwright browsers
```bash
playwright install chromium
```

## Project Structure

```
ktmb-scraper/
├── utils/                    # Configuration and logging utilities
│   ├── __init__.py
│   ├── config.py            # Pydantic models and configuration
│   └── logging_config.py    # Logging configuration
├── scraper/                  # Main scraper modules
│   ├── __init__.py
│   ├── main.py              # Main scraper class
│   ├── parser.py            # HTML parsing utilities
│   ├── browser.py           # Browser automation
│   └── __main__.py          # Entry point
├── monitor.py               # Continuous monitoring script
├── ktmb_search.py           # Search script
├── notifications.py         # Notification utilities
├── example_with_logging.py  # Logging examples
└── pyproject.toml           # Project dependencies
```

## Usage

### Basic Usage
```python
from utils.config import ScraperSettings, Direction
from datetime import date
from scraper.main import KTMBShuttleScraper

# Create settings
settings = ScraperSettings(
    direction=Direction.JB_TO_SG,
    depart_date=date(2025, 7, 20),
    num_adults=2
)

# Run scraper
scraper = KTMBShuttleScraper(settings)
results = scraper.run()
```

### With Custom Logging
```python
from utils.logging_config import setup_logging, get_debug_config

# Setup debug logging
logger = setup_logging(get_debug_config())

# Use scraper as normal
scraper = KTMBShuttleScraper(settings)
results = scraper.run()
```

### Command Line Usage
```bash
# Run the scraper directly
python -m scraper

# Run monitoring
python monitor.py --date 2025-08-15 --direction jb-to-sg

# Run search script
python ktmb_search.py --fridays 2025 8
```

## Dependencies

### Required Dependencies
- **pydantic>=2.0.0**: Data validation and settings management
- **playwright>=1.40.0**: Browser automation
- **python-dotenv>=1.0.0**: Environment variable management
- **requests>=2.25.0**: HTTP requests
- **python-dateutil>=2.8.0**: Date utilities
- **click>=8.0.0**: Command line interface

### Optional Dependencies
- **loguru**: Alternative logging (not used in current version)

## Troubleshooting

### Import Errors
If you encounter import errors:

1. **Ensure virtual environment is activated**:
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

2. **Check if dependencies are installed**:
   ```bash
   python -c "import pydantic; print('Pydantic available')"
   ```

3. **Reinstall dependencies**:
   ```bash
   uv pip install --force-reinstall pydantic playwright
   ```

### Playwright Issues
If Playwright doesn't work:

1. **Install browsers**:
   ```bash
   playwright install chromium
   ```

2. **Check browser installation**:
   ```bash
   playwright --version
   ```

### Logging Issues
If logging doesn't work:

1. **Check log directory permissions**:
   ```bash
   mkdir -p logs
   chmod 755 logs
   ```

2. **Test logging setup**:
   ```python
   from utils.logging_config import setup_logging
   logger = setup_logging()
   logger.info("Test message")
   ```

## Development

### Running Tests
```bash
# Test imports
python -c "from utils import *; from scraper.main import KTMBShuttleScraper; print('All imports successful')"

# Test logging
python -c "from utils.logging_config import setup_logging; logger = setup_logging(); logger.info('Test')"
```

### Adding New Dependencies
1. Add to `pyproject.toml`
2. Install with `uv pip install <package>`
3. Update this documentation

## Notes

- The project uses a `utils` package for configuration and logging utilities
- All imports should use the `utils` package: `from utils.config import ...`
- The virtual environment must be activated for all operations
- Pydantic is required for the configuration system to work properly 