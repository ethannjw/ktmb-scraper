# Logging Configuration

This document explains how to use the logging system in the KTMB Scraper.

## Overview

The scraper uses Python's built-in `logging` module with configurable levels, file rotation, and both console and file output. All `print()` statements have been replaced with appropriate logging calls.

## Logging Levels

The logging system uses the following levels:

- **DEBUG**: Internal details, parsing information, time slot calculations
- **INFO**: Main task progress (navigation, form filling, search completion)
- **WARNING**: Non-critical issues (parsing errors for individual rows)
- **ERROR**: Exceptions and critical failures

## Quick Start

### Basic Usage

```python
from utils.config import ScraperSettings, Direction
from datetime import date
from scraper.main import KTMBShuttleScraper

# Default logging (INFO level, both console and file)
settings = ScraperSettings(
    direction=Direction.JB_TO_SG,
    depart_date=date(2025, 7, 20),
    num_adults=2
)

scraper = KTMBShuttleScraper(settings)
results = scraper.run()
```

### Custom Logging Configuration

```python
from utils.logging_config import setup_logging, LoggingConfig

# Create custom configuration
config = LoggingConfig(
    log_level="DEBUG",
    log_file="my_scraper.log",
    console_output=True,
    file_output=True
)

# Setup logging
logger = setup_logging(config)

# Use scraper as normal
scraper = KTMBShuttleScraper(settings)
results = scraper.run()
```

## Predefined Configurations

### Debug Configuration
Shows all internal details for troubleshooting:

```python
from utils.logging_config import setup_logging, get_debug_config

logger = setup_logging(get_debug_config())
```

**Output**: All messages including internal parsing details, time slot calculations, and debugging information.

### Production Configuration
Only important information and errors:

```python
from utils.logging_config import setup_logging, get_production_config

logger = setup_logging(get_production_config())
```

**Output**: Main task progress and errors only. No console output, only file logging.

### Quiet Configuration
Errors only:

```python
from utils.logging_config import setup_logging, get_quiet_config

logger = setup_logging(get_quiet_config())
```

**Output**: Only error messages.

## Configuration Options

### LoggingConfig Parameters

- `log_level`: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
- `log_file`: Path to log file (default: "logs/ktmb_scraper.log")
- `log_format`: Log message format string
- `max_file_size`: Maximum log file size before rotation (default: 10MB)
- `backup_count`: Number of backup files to keep (default: 5)
- `console_output`: Whether to output to console (default: True)
- `file_output`: Whether to output to file (default: True)

### Example Configurations

```python
# Minimal configuration
config = LoggingConfig(log_level="ERROR")

# Verbose configuration
config = LoggingConfig(
    log_level="DEBUG",
    log_file="logs/verbose_scraper.log",
    log_format="%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    max_file_size=50 * 1024 * 1024,  # 50MB
    backup_count=10
)

# Console-only configuration
config = LoggingConfig(
    log_level="INFO",
    file_output=False,
    console_output=True
)
```

## Environment Variables

You can configure logging using environment variables:

```bash
# Set log level
export KTMB_LOG_LEVEL=DEBUG

# Set log file
export KTMB_LOG_FILE=logs/my_scraper.log

# Run scraper
python scraper/main.py
```

## Log File Rotation

Log files are automatically rotated when they reach the maximum size:

- Default maximum size: 10MB
- Default backup count: 5 files
- Files are named: `ktmb_scraper.log`, `ktmb_scraper.log.1`, `ktmb_scraper.log.2`, etc.

## Example Log Output

### Debug Level
```
2024-01-15 10:30:15,123 - __main__ - INFO - Initialized KTMB Shuttle Scraper with settings: direction=JB_TO_SG, depart_date=2025-07-20, passengers=2
2024-01-15 10:30:15,456 - __main__ - INFO - Starting KTMB Shuttle scraping process
2024-01-15 10:30:15,789 - __main__ - INFO - Navigating to KTMB Shuttle page
2024-01-15 10:30:16,012 - __main__ - INFO - Direction set to JB -> SG (JB Sentral -> Woodlands CIQ)
2024-01-15 10:30:16,234 - __main__ - INFO - Setting departure date to: 20 Jul 2025
2024-01-15 10:30:16,456 - __main__ - DEBUG - Time '08:30' falls into early_morning slot
2024-01-15 10:30:16,678 - __main__ - DEBUG - Train departure time '08:30' slot 'early_morning' is desired: True
```

### Info Level
```
2024-01-15 10:30:15,123 - __main__ - INFO - Initialized KTMB Shuttle Scraper with settings: direction=JB_TO_SG, depart_date=2025-07-20, passengers=2
2024-01-15 10:30:15,456 - __main__ - INFO - Starting KTMB Shuttle scraping process
2024-01-15 10:30:15,789 - __main__ - INFO - Navigating to KTMB Shuttle page
2024-01-15 10:30:16,012 - __main__ - INFO - Direction set to JB -> SG (JB Sentral -> Woodlands CIQ)
2024-01-15 10:30:16,234 - __main__ - INFO - Setting departure date to: 20 Jul 2025
2024-01-15 10:30:16,456 - __main__ - INFO - Departure date set successfully to: 20 Jul 2025
```

### Error Level
```
2024-01-15 10:30:15,123 - __main__ - ERROR - Error selecting departure date: Element not found
2024-01-15 10:30:15,456 - __main__ - ERROR - Scraping process failed: Element not found
```

## Integration with Existing Code

The logging system is designed to be non-intrusive. Existing code will continue to work with default logging settings. To customize logging, simply call `setup_logging()` with your desired configuration before using the scraper.

## Troubleshooting

### Common Issues

1. **No log output**: Check if the log level is set too high
2. **Permission errors**: Ensure write permissions for the log directory
3. **Large log files**: Adjust `max_file_size` and `backup_count` settings

### Debug Mode

For troubleshooting, use debug logging:

```python
from utils.logging_config import setup_logging, get_debug_config

logger = setup_logging(get_debug_config())
# This will show all internal details and help identify issues
```

## Best Practices

1. **Development**: Use DEBUG level for detailed troubleshooting
2. **Production**: Use INFO or WARNING level to reduce log volume
3. **Monitoring**: Use ERROR level for alerting systems
4. **File Management**: Set appropriate `max_file_size` and `backup_count` for your storage constraints 