"""Browser automation module for KTMB scraper."""

from playwright.sync_api import sync_playwright, Page, Browser
from utils.logging_config import get_logger
from utils.config import BROWSER_CONFIG, KTMB_CONFIG
from typing import Optional
import time

# Get logger for this module
logger = get_logger(__name__)


class BrowserManager:
    """Manages browser lifecycle and page interactions."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def start(self):
        """Initialize browser and page."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self.page = self.browser.new_page(
                viewport=BROWSER_CONFIG["viewport"],
                user_agent=BROWSER_CONFIG["user_agent"]
            )
            
            # Set default timeout
            self.page.set_default_timeout(BROWSER_CONFIG["timeout"])
            
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            self.close()
            raise
    
    def close(self):
        """Clean up browser resources."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
    
    def navigate_to_ktmb(self) -> bool:
        """Navigate to KTMB shuttle booking page."""
        try:
            logger.info(f"Navigating to {KTMB_CONFIG['base_url']}")
            self.page.goto(KTMB_CONFIG['base_url'])
            
            # Wait for page to load
            self.page.wait_for_load_state('networkidle')
            
            # Check if we're on the right page
            if "shuttle" not in self.page.url.lower():
                logger.error("Failed to navigate to KTMB shuttle page")
                return False
                
            logger.info("Successfully navigated to KTMB shuttle page")
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to be visible."""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Element {selector} not found: {e}")
            return False
    
    def safe_click(self, selector: str) -> bool:
        """Safely click an element."""
        try:
            if self.wait_for_element(selector):
                self.page.click(selector)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click {selector}: {e}")
            return False
    
    def safe_fill(self, selector: str, value: str) -> bool:
        """Safely fill an input field."""
        try:
            if self.wait_for_element(selector):
                self.page.fill(selector, value)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to fill {selector}: {e}")
            return False
    
    def safe_select(self, selector: str, value: str) -> bool:
        """Safely select from dropdown."""
        try:
            if self.wait_for_element(selector):
                self.page.select_option(selector, value)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to select {selector}: {e}")
            return False