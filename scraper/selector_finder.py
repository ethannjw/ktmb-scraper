"""Helper tool to find and test selectors on KTMB website."""

from playwright.sync_api import sync_playwright
from .logging_config import get_logger
import time

# Get logger for this module
logger = get_logger(__name__)


class SelectorFinder:
    """Interactive tool to help find correct selectors on KTMB website."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
    
    def inspect_page(self):
        """Launch browser in non-headless mode to inspect elements."""
        logger.info("Starting page inspection mode")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            print("🚀 Opening KTMB website for inspection...")
            logger.info("Navigating to KTMB website")
            page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
            
            print("\n📋 INSPECTION GUIDE:")
            print("1. Right-click on any element → 'Inspect Element'")
            print("2. In DevTools, right-click the highlighted HTML → 'Copy' → 'Copy selector'")
            print("3. Test selectors using the console or this tool")
            print("\n⏳ Browser will stay open for 60 seconds for inspection...")
            
            # Keep browser open for inspection
            logger.info("Browser will stay open for 60 seconds for inspection")
            time.sleep(60)
            browser.close()
            logger.info("Page inspection completed")
    
    def test_selectors(self):
        """Test various selector strategies on the KTMB page."""
        logger.info("Starting selector testing")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            logger.info("Page loaded successfully")
            
            print("🔍 Testing common selectors on KTMB page...\n")
            
            # Test different selector strategies
            selectors_to_test = {
                "Direction dropdown": [
                    "select[name='Direction']",
                    "#Direction",
                    "select:has-text('Direction')",
                    "//select[contains(@name, 'Direction')]"
                ],
                "Date input": [
                    "input[name='DepartDate']",
                    "input[type='date']",
                    "#DepartDate",
                    "//input[contains(@placeholder, 'date')]"
                ],
                "Adult passengers": [
                    "select[name='Adult']",
                    "#Adult",
                    "select:has-text('Adult')",
                    "//select[contains(@name, 'Adult')]"
                ],
                "Search button": [
                    "input[type='submit']",
                    "button:has-text('Search')",
                    "#btnSearch",
                    "//input[@value='Search']"
                ]
            }
            
            for element_name, selectors in selectors_to_test.items():
                print(f"🎯 Testing selectors for: {element_name}")
                logger.debug(f"Testing selectors for: {element_name}")
                
                for selector in selectors:
                    try:
                        if selector.startswith('//'):
                            # XPath selector
                            elements = page.locator(f"xpath={selector}")
                        else:
                            # CSS selector
                            elements = page.locator(selector)
                        
                        count = elements.count()
                        if count > 0:
                            print(f"  ✅ {selector} → Found {count} element(s)")
                            logger.debug(f"Selector '{selector}' found {count} element(s)")
                            
                            # Get element details
                            first_element = elements.first
                            tag_name = first_element.evaluate("el => el.tagName")
                            
                            if tag_name.lower() == 'select':
                                options = first_element.locator('option').all_inner_texts()
                                print(f"     Options: {options[:3]}...")  # Show first 3 options
                                logger.debug(f"Select options: {options[:3]}...")
                            elif tag_name.lower() == 'input':
                                input_type = first_element.get_attribute('type')
                                placeholder = first_element.get_attribute('placeholder')
                                print(f"     Type: {input_type}, Placeholder: {placeholder}")
                                logger.debug(f"Input type: {input_type}, placeholder: {placeholder}")
                        else:
                            print(f"  ❌ {selector} → Not found")
                            logger.debug(f"Selector '{selector}' not found")
                            
                    except Exception as e:
                        print(f"  ⚠️  {selector} → Error: {str(e)[:50]}...")
                        logger.warning(f"Error testing selector '{selector}': {e}")
                
                print()
            
            browser.close()
            logger.info("Selector testing completed")
    
    def extract_page_structure(self):
        """Extract and display the page structure for analysis."""
        logger.info("Starting page structure analysis")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
            page.wait_for_load_state('networkidle')
            logger.info("Page loaded for structure analysis")
            
            print("📄 KTMB Page Structure Analysis\n")
            
            # Extract forms
            forms = page.locator('form').all()
            print(f"🔍 Found {len(forms)} form(s):")
            logger.info(f"Found {len(forms)} form(s)")
            
            for i, form in enumerate(forms):
                form_id = form.get_attribute('id')
                form_action = form.get_attribute('action')
                print(f"  Form {i+1}: id='{form_id}', action='{form_action}'")
                logger.debug(f"Form {i+1}: id='{form_id}', action='{form_action}'")
                
                # Get form inputs
                inputs = form.locator('input, select, textarea').all()
                print(f"    Inputs ({len(inputs)}):")
                logger.debug(f"Form {i+1} has {len(inputs)} inputs")
                
                for input_elem in inputs:
                    tag = input_elem.evaluate("el => el.tagName").lower()
                    name = input_elem.get_attribute('name')
                    input_type = input_elem.get_attribute('type')
                    input_id = input_elem.get_attribute('id')
                    
                    print(f"      <{tag}> name='{name}' type='{input_type}' id='{input_id}'")
                    logger.debug(f"Input: <{tag}> name='{name}' type='{input_type}' id='{input_id}'")
                print()
            
            # Extract tables (for results)
            tables = page.locator('table').all()
            print(f"📊 Found {len(tables)} table(s):")
            logger.info(f"Found {len(tables)} table(s)")
            
            for i, table in enumerate(tables):
                table_class = table.get_attribute('class')
                table_id = table.get_attribute('id')
                headers = table.locator('th').all_inner_texts()
                
                print(f"  Table {i+1}: class='{table_class}', id='{table_id}'")
                logger.debug(f"Table {i+1}: class='{table_class}', id='{table_id}'")
                if headers:
                    print(f"    Headers: {headers}")
                    logger.debug(f"Table {i+1} headers: {headers}")
                print()
            
            browser.close()
            logger.info("Page structure analysis completed")


def main():
    """Interactive selector finder tool."""
    logger.info("Starting KTMB Selector Finder Tool")
    finder = SelectorFinder()
    
    print("🔧 KTMB Selector Finder Tool")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Open browser for manual inspection")
        print("2. Test common selectors automatically")
        print("3. Extract page structure")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            logger.info("User selected: Manual inspection")
            finder.inspect_page()
        elif choice == '2':
            logger.info("User selected: Test selectors")
            finder.test_selectors()
        elif choice == '3':
            logger.info("User selected: Extract page structure")
            finder.extract_page_structure()
        elif choice == '4':
            logger.info("User selected: Exit")
            print("👋 Goodbye!")
            break
        else:
            logger.warning(f"Invalid choice entered: {choice}")
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()