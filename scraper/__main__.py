from config import ScraperSettings
from scraper.main import KTMBShuttleScraper
from datetime import date

if __name__ == '__main__':
    # Example: update these values or load from user input
    settings = ScraperSettings(
        direction='JB_TO_SG',
        depart_date=date.today(),
        num_pax=1,
        desired_timings=['morning', 'afternoon', 'evening']
    )
    scraper = KTMBShuttleScraper(settings)
    results = scraper.run()
    print('Available trains with seats:', results) 