#!/usr/bin/env python3
"""
Example script demonstrating different logging configurations for the KTMB Scraper
"""

from config import ScraperSettings, Direction
from datetime import date
from scraper.main import KTMBShuttleScraper
from scraper.logging_config import setup_logging, LoggingConfig, get_debug_config, get_production_config, get_quiet_config

def example_with_debug_logging():
    """Example with debug logging - shows all internal details"""
    print("=== Running with DEBUG logging ===")
    
    # Setup debug logging
    logger = setup_logging(get_debug_config())
    
    # Configure scraper settings
    settings = ScraperSettings(
        direction=Direction.JB_TO_SG,
        depart_date=date(2025, 7, 20),
        num_adults=2,
        min_available_seats=2
    )
    
    # Run scraper
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    
    print(f"Results: {results}")
    print()

def example_with_production_logging():
    """Example with production logging - only important info and errors"""
    print("=== Running with PRODUCTION logging ===")
    
    # Setup production logging
    logger = setup_logging(get_production_config())
    
    # Configure scraper settings
    settings = ScraperSettings(
        direction=Direction.SG_TO_JB,
        depart_date=date(2025, 7, 21),
        num_adults=1,
        min_available_seats=1
    )
    
    # Run scraper
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    
    print(f"Results: {results}")
    print()

def example_with_quiet_logging():
    """Example with quiet logging - only errors"""
    print("=== Running with QUIET logging (errors only) ===")
    
    # Setup quiet logging
    logger = setup_logging(get_quiet_config())
    
    # Configure scraper settings
    settings = ScraperSettings(
        direction=Direction.JB_TO_SG,
        depart_date=date(2025, 7, 22),
        num_adults=3,
        min_available_seats=3
    )
    
    # Run scraper
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    
    print(f"Results: {results}")
    print()

def example_with_custom_logging():
    """Example with custom logging configuration"""
    print("=== Running with CUSTOM logging configuration ===")
    
    # Create custom logging configuration
    custom_config = LoggingConfig(
        log_level="WARNING",
        log_file="logs/custom_scraper.log",
        log_format="%(asctime)s - %(levelname)s - %(message)s",
        console_output=True,
        file_output=True
    )
    
    # Setup custom logging
    logger = setup_logging(custom_config)
    
    # Configure scraper settings
    settings = ScraperSettings(
        direction=Direction.SG_TO_JB,
        depart_date=date(2025, 7, 23),
        num_adults=2,
        min_available_seats=2
    )
    
    # Run scraper
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    
    print(f"Results: {results}")
    print()

def example_with_environment_variables():
    """Example using environment variables for logging configuration"""
    print("=== Running with environment variable configuration ===")
    
    import os
    
    # Get logging level from environment variable (default to INFO)
    log_level = os.getenv("KTMB_LOG_LEVEL", "INFO")
    log_file = os.getenv("KTMB_LOG_FILE", "logs/env_scraper.log")
    
    # Create configuration from environment
    env_config = LoggingConfig(
        log_level=log_level,
        log_file=log_file,
        console_output=True,
        file_output=True
    )
    
    # Setup logging
    logger = setup_logging(env_config)
    
    # Configure scraper settings
    settings = ScraperSettings(
        direction=Direction.JB_TO_SG,
        depart_date=date(2025, 7, 24),
        num_adults=1,
        min_available_seats=1
    )
    
    # Run scraper
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    
    print(f"Results: {results}")
    print()

if __name__ == "__main__":
    print("KTMB Scraper Logging Examples")
    print("=" * 50)
    
    # Run examples with different logging configurations
    try:
        example_with_debug_logging()
    except Exception as e:
        print(f"Debug example failed: {e}")
    
    try:
        example_with_production_logging()
    except Exception as e:
        print(f"Production example failed: {e}")
    
    try:
        example_with_quiet_logging()
    except Exception as e:
        print(f"Quiet example failed: {e}")
    
    try:
        example_with_custom_logging()
    except Exception as e:
        print(f"Custom example failed: {e}")
    
    try:
        example_with_environment_variables()
    except Exception as e:
        print(f"Environment example failed: {e}")
    
    print("All examples completed!")
    print("\nLog files created:")
    print("- logs/ktmb_scraper_debug.log (debug logging)")
    print("- logs/ktmb_scraper.log (production logging)")
    print("- logs/ktmb_scraper_error.log (quiet logging)")
    print("- logs/custom_scraper.log (custom logging)")
    print("- logs/env_scraper.log (environment-based logging)") 