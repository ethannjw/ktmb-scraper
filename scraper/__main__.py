from config import ScraperSettings, Direction, TimeSlot
from .main import KTMBShuttleScraper
from .logging_config import setup_logging
from datetime import date

if __name__ == '__main__':
    # Setup logging
    logger = setup_logging()
    
    # Example: update these values or load from user input
    settings = ScraperSettings(
        direction=Direction.JB_TO_SG,
        depart_date=date.today(),
        num_adults=1,
        desired_time_slots=[TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING]
    )
    
    logger.info("Starting KTMB scraper from __main__")
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    
    if results.get('success'):
        logger.info(f"Found {results.get('total_available', 0)} available trains")
    else:
        logger.error(f"Scraping failed: {results.get('error', 'Unknown error')}")
    
    print('Available trains with seats:', results) 