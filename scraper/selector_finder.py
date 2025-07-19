"""Helper tool to find and test selectors on KTMB website."""

from playwright.sync_api import sync_playwright
from loguru import logger
import time


class SelectorFinder:
    """Interactive tool to help find correct selectors on KTMB website."""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
    
    def inspect_page(self):
        """Launch browser in non-headless mode to inspect elements."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            print("🚀 Opening KTMB website for inspection...")
            page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
            
            print("\n📋 INSPECTION GUIDE:")
            print("1. Right-click on any element → 'Inspect Element'")
            print("2. In DevTools, right-click the highlighted HTML → 'Copy' → 'Copy selector'")
            print("3. Test selectors using the console or this tool")
            print("\n⏳ Browser will stay open for 60 seconds for inspection...")
            
            # Keep browser open for inspection
            time.sleep(60)
            browser.close()
    
    def test_selectors(self):
        """Test various selector strategies on the KTMB page."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
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
                            
                            # Get element details
                            first_element = elements.first
                            tag_name = first_element.evaluate("el => el.tagName")
                            
                            if tag_name.lower() == 'select':
                                options = first_element.locator('option').all_inner_texts()
                                print(f"     Options: {options[:3]}...")  # Show first 3 options
                            elif tag_name.lower() == 'input':
                                input_type = first_element.get_attribute('type')
                                placeholder = first_element.get_attribute('placeholder')
                                print(f"     Type: {input_type}, Placeholder: {placeholder}")
                        else:
                            print(f"  ❌ {selector} → Not found")
                            
                    except Exception as e:
                        print(f"  ⚠️  {selector} → Error: {str(e)[:50]}...")
                
                print()
            
            browser.close()
    
    def extract_page_structure(self):
        """Extract and display the page structure for analysis."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
            page.wait_for_load_state('networkidle')
            
            print("📄 KTMB Page Structure Analysis\n")
            
            # Extract forms
            forms = page.locator('form').all()
            print(f"🔍 Found {len(forms)} form(s):")
            
            for i, form in enumerate(forms):
                form_id = form.get_attribute('id')
                form_action = form.get_attribute('action')
                print(f"  Form {i+1}: id='{form_id}', action='{form_action}'")
                
                # Get form inputs
                inputs = form.locator('input, select, textarea').all()
                print(f"    Inputs ({len(inputs)}):")
                
                for input_elem in inputs:
                    tag = input_elem.evaluate("el => el.tagName").lower()
                    name = input_elem.get_attribute('name')
                    input_type = input_elem.get_attribute('type')
                    input_id = input_elem.get_attribute('id')
                    
                    print(f"      <{tag}> name='{name}' type='{input_type}' id='{input_id}'")
                print()
            
            # Extract tables (for results)
            tables = page.locator('table').all()
            print(f"📊 Found {len(tables)} table(s):")
            
            for i, table in enumerate(tables):
                table_class = table.get_attribute('class')
                table_id = table.get_attribute('id')
                headers = table.locator('th').all_inner_texts()
                
                print(f"  Table {i+1}: class='{table_class}', id='{table_id}'")
                if headers:
                    print(f"    Headers: {headers}")
                print()
            
            browser.close()


def main():
    """Interactive selector finder tool."""
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
            finder.inspect_page()
        elif choice == '2':
            finder.test_selectors()
        elif choice == '3':
            finder.extract_page_structure()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()