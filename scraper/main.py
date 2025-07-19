from playwright.sync_api import sync_playwright
from config import ScraperSettings, Direction, DIRECTION_MAPPING, KTMB_CONFIG
from typing import Dict, Any
import time
from datetime import datetime

class KTMBShuttleScraper:
    def __init__(self, settings: ScraperSettings):
        self.settings = settings

    def run(self) -> Dict[str, Any]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the KTMB Shuttle page
                page.goto('https://shuttleonline.ktmb.com.my/Home/Shuttle')
                page.wait_for_load_state('networkidle')
                
                # Handle direction selection
                self._select_direction(page)
                
                # Handle date selection
                self._select_departure_date(page)
                
                # Handle return date if specified
                if self.settings.return_date:
                    self._select_return_date(page)
                
                # Select number of passengers
                self._select_passengers(page)
                
                # Perform search
                self._perform_search(page)
                
                # Parse results
                results = self._parse_results(page)
                browser.close()
                return results
                
            except Exception as e:
                browser.close()
                return {"error": str(e), "success": False}

    def _select_direction(self, page):
        """Handle direction selection using JavaScript"""
        try:
            # Use JavaScript to set the direction directly
            if self.settings.direction == Direction.SG_TO_JB:
                # Set origin to Woodlands CIQ and destination to JB Sentral
                page.evaluate("""
                    // Find the direction swap button and click it to get SG -> JB
                    const swapButton = document.querySelector('i[class*="swap"], i[class*="exchange"], i:nth-child(2)');
                    if (swapButton) {
                        swapButton.click();
                    }
                """)
                page.wait_for_timeout(1000)
                print("Direction set to SG -> JB (Woodlands CIQ -> JB Sentral)")
            else:
                # Default is JB -> SG, so no need to swap
                print("Direction set to JB -> SG (JB Sentral -> Woodlands CIQ)")
                    
        except Exception as e:
            print(f"Error selecting direction: {e}")

    def _select_departure_date(self, page):
        """Handle departure date selection using JavaScript"""
        try:
            # Use JavaScript to set the date directly - this works reliably
            date_str = self.settings.depart_date.strftime('%d %b %Y')  # "01 Aug 2025" format
            print(f"Setting departure date to: {date_str}")
            
            page.evaluate(f"""
                document.querySelector('input[name="OnwardDate"]').value = '{date_str}';
                document.querySelector('input[name="OnwardDate"]').dispatchEvent(new Event('change', {{ bubbles: true }}));
            """)
            page.wait_for_timeout(500)
            
            print(f"Departure date set successfully to: {date_str}")
            
        except Exception as e:
            print(f"Error selecting departure date: {e}")
            raise e
    
    def _get_month_name(self, month_number):
        """Convert month number to month name"""
        months = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        return months.get(month_number, 'January')
    
    def _get_month_number(self, month_name):
        """Convert month name to month number"""
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        return months.get(month_name, 1)

    def _select_return_date(self, page):
        """Handle return date selection if specified"""
        try:
            if self.settings.return_date:
                # Click on the return date field
                return_field = page.get_by_role('textbox', name='Return')
                return_field.click()
                page.wait_for_timeout(500)
                
                # Fill the return date
                return_date_str = self.settings.return_date.strftime('%d/%m/%Y')
                return_field.fill(return_date_str)
                return_field.press('Enter')
                page.wait_for_timeout(500)
                
                print(f"Return date set to: {return_date_str}")
                
        except Exception as e:
            print(f"Error selecting return date: {e}")

    def _select_passengers(self, page):
        """Handle passenger selection"""
        try:
            # Select the passenger dropdown
            passenger_dropdown = page.locator('#PassengerCount')
            passenger_dropdown.click()
            
            # Select the appropriate number of passengers
            passenger_option = f"{self.settings.total_pax} Pax"
            passenger_dropdown.select_option(passenger_option)
            
            print(f"Passengers set to: {passenger_option}")
            
        except Exception as e:
            print(f"Error selecting passengers: {e}")

    def _perform_search(self, page):
        """Perform the search and wait for results"""
        try:
            # Click the search button
            search_button = page.get_by_role('button', name='SEARCH')
            search_button.click()
            print("Search button clicked")
            
            # Wait a moment for the search to process (reduced timeout)
            page.wait_for_timeout(1000)
            
            # Check current URL to see if we were redirected
            current_url = page.url
            print(f"Current URL after search: {current_url}")
            
            # If we were redirected to the results page, that's good
            if "ShuttleTrip" in current_url:
                print("Successfully redirected to results page")
                return
            
            # Check for various possible outcomes on the search page
            try:
                # Wait for results table to appear (faster timeout)
                page.wait_for_selector('#tblTrainList', timeout=5000)
                print("Search completed successfully - results found")
            except:
                print("Results table not found, checking for errors...")
                
                # Check for validation error - use a more specific selector
                try:
                    error_element = page.locator('#OnwardDate-error')
                    if error_element.is_visible():
                        error_text = error_element.inner_text()
                        print(f"Found validation error: {error_text}")
                        if "Please select departing date" in error_text:
                            raise Exception("Validation error: Please select departing date")
                except Exception as error_check:
                    print(f"Error check failed: {error_check}")
                
                # Check for other error messages
                try:
                    # Look for any error messages on the page
                    error_messages = page.locator('.alert, .error, .validation-error')
                    error_count = error_messages.count()
                    for i in range(error_count):
                        error_text = error_messages.nth(i).inner_text()
                        print(f"Found error message: {error_text}")
                except:
                    pass
                
                # Take a screenshot for debugging
                page.screenshot(path="debug_screenshot.png")
                print("Screenshot saved as debug_screenshot.png")
                
                # Wait a bit more for results
                page.wait_for_timeout(3000)
                    
        except Exception as e:
            print(f"Error during search: {e}")
            raise e

    def _parse_results(self, page) -> Dict[str, Any]:
        """Parse the search results table"""
        try:
            # Check if we're on the results page
            current_url = page.url
            print(f"Parsing results from URL: {current_url}")
            
            # Wait for page to load (faster timeout)
            page.wait_for_load_state('domcontentloaded')
            
            # Try different selectors for the results table
            table_selectors = [
                '#tblTrainList',
                '.train-table',
                'table',
                '.results-table',
                '[data-testid="train-list"]'
            ]
            
            table_found = False
            for selector in table_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    print(f"Found results table with selector: {selector}")
                    table_found = True
                    break
                except:
                    continue
            
            if not table_found:
                # Take a screenshot to see what's on the page
                page.screenshot(path="results_page_screenshot.png")
                print("No results table found, screenshot saved as results_page_screenshot.png")
                
                # Check if there's a "no results" message
                no_results_selectors = [
                    'text="No trains available"',
                    'text="No results found"',
                    '.no-results',
                    '.empty-state'
                ]
                
                for no_result_selector in no_results_selectors:
                    try:
                        if page.locator(no_result_selector).is_visible():
                            print("No trains available for the selected criteria")
                            return {
                                "success": True,
                                "available_trains": [],
                                "total_available": 0,
                                "message": "No trains available for the selected criteria",
                                "search_criteria": {
                                    "direction": self.settings.direction.value,
                                    "depart_date": self.settings.depart_date.strftime('%Y-%m-%d'),
                                    "return_date": self.settings.return_date.strftime('%Y-%m-%d') if self.settings.return_date else None,
                                    "passengers": self.settings.total_pax,
                                    "min_seats": self.settings.min_available_seats
                                },
                                "scraped_at": datetime.now().isoformat()
                            }
                    except:
                        continue
                
                return {
                    "success": False,
                    "error": "Could not find results table or no results message",
                    "available_trains": [],
                    "total_available": 0
                }
            
            # Get all train rows
            rows = page.query_selector_all(f'{selector} tbody tr, {selector} tr')
            
            available_trains = []
            
            for row in rows:
                cells = row.query_selector_all('td')
                if not cells or len(cells) < 3:
                    continue
                
                try:
                    # Extract train information - try different column layouts
                    if len(cells) >= 5:
                        # Standard layout: train number, departure, arrival, duration, seats
                        train_number = cells[0].inner_text().strip()
                        departure_time = cells[1].inner_text().strip()
                        arrival_time = cells[2].inner_text().strip()
                        available_seats = int(cells[4].inner_text().strip())
                    elif len(cells) >= 4:
                        # Alternative layout: train number, departure, arrival, seats
                        train_number = cells[0].inner_text().strip()
                        departure_time = cells[1].inner_text().strip()
                        arrival_time = cells[2].inner_text().strip()
                        available_seats = int(cells[3].inner_text().strip())
                    else:
                        # Minimal layout: departure, arrival, seats
                        train_number = f"Train {len(available_trains) + 1}"
                        departure_time = cells[0].inner_text().strip()
                        arrival_time = cells[1].inner_text().strip()
                        available_seats = int(cells[2].inner_text().strip())
                    
                    # Check if this train meets our criteria
                    if available_seats >= self.settings.min_available_seats:
                        train_info = {
                            "train_number": train_number,
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "available_seats": available_seats,
                            "direction": self.settings.direction.value
                        }
                        available_trains.append(train_info)
                        
                except (ValueError, IndexError) as e:
                    # Skip rows that can't be parsed
                    print(f"Skipping row due to parsing error: {e}")
                    continue
            
            return {
                "success": True,
                "available_trains": available_trains,
                "total_available": len(available_trains),
                "search_criteria": {
                    "direction": self.settings.direction.value,
                    "depart_date": self.settings.depart_date.strftime('%Y-%m-%d'),
                    "return_date": self.settings.return_date.strftime('%Y-%m-%d') if self.settings.return_date else None,
                    "passengers": self.settings.total_pax,
                    "min_seats": self.settings.min_available_seats
                },
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error parsing results: {str(e)}",
                "available_trains": [],
                "total_available": 0
            }

# Example usage:
# from config import ScraperSettings, Direction
# from datetime import date
# 
# settings = ScraperSettings(
#     direction=Direction.JB_TO_SG,
#     depart_date=date(2025, 7, 20),
#     num_adults=2,
#     min_available_seats=2
# )
# 
# scraper = KTMBShuttleScraper(settings)
# results = scraper.run()
# print(results) 