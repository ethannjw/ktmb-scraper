from playwright.sync_api import sync_playwright
from utils.config import (
    ScraperSettings,
    Direction,
    DIRECTION_MAPPING,
    KTMB_CONFIG,
    TimeSlot,
    TIME_SLOT_RANGES,
)
from typing import Dict, Any, List
import time as time_module
from datetime import datetime, time as datetime_time
from utils.logging_config import setup_logging, LoggingConfig, get_logger

# Initialize logger with default configuration
logger = setup_logging()


class KTMBShuttleScraper:
    def __init__(self, settings: ScraperSettings):
        self.settings = settings
        logger.info(
            f"Initialized KTMB Shuttle Scraper with settings: direction={settings.direction}, "
            f"depart_date={settings.depart_date}, "
            f"return_date={settings.return_date}, "
            f"passengers={settings.total_pax}"
        )

    def _get_time_slot(self, time_str: str) -> TimeSlot:
        """Determine which time slot a given time falls into"""
        try:
            # Parse time string (e.g., "19:00" or "7:00 PM")
            from datetime import datetime

            # Try different time formats
            time_formats = ["%H:%M", "%I:%M %p", "%I:%M%p"]
            parsed_time = None

            for fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str.strip(), fmt).time()
                    break
                except ValueError:
                    continue

            if not parsed_time:
                # Default to evening if we can't parse the time
                logger.debug(
                    f"Could not parse time '{time_str}', defaulting to evening slot"
                )
                return TimeSlot.EVENING

            # Check which time slot this time falls into
            for slot, (start_time, end_time) in TIME_SLOT_RANGES.items():
                if slot == TimeSlot.NIGHT:
                    # Night slot spans midnight, so check if time is after 22:00 or before 05:00
                    if parsed_time >= start_time or parsed_time <= datetime_time(4, 59):
                        logger.debug(f"Time '{time_str}' falls into {slot} slot")
                        return slot
                else:
                    # Regular time slots
                    if start_time <= parsed_time <= end_time:
                        logger.debug(f"Time '{time_str}' falls into {slot} slot")
                        return slot

            # Default to evening if no match found
            logger.debug(
                f"Time '{time_str}' didn't match any slot, defaulting to evening"
            )
            return TimeSlot.EVENING

        except Exception as e:
            logger.error(f"Error parsing time '{time_str}': {e}")
            return TimeSlot.EVENING

    def _is_train_in_desired_time_slots(self, departure_time: str) -> bool:
        """Check if a train's departure time falls within desired time slots"""
        if (
            not self.settings.desired_time_slots
            or len(self.settings.desired_time_slots) == 0
        ):
            logger.debug("No time slots specified, accepting all trains")
            return True  # If no time slots specified, accept all trains

        train_time_slot = self._get_time_slot(departure_time)
        is_desired = train_time_slot in self.settings.desired_time_slots
        logger.debug(
            f"Train departure time '{departure_time}' slot '{train_time_slot}' is desired: {is_desired}"
        )
        return is_desired

    def run(self) -> Dict[str, Any]:
        logger.debug("Starting KTMB Shuttle scraping process")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Navigate to the KTMB Shuttle page
                logger.debug("Navigating to KTMB Shuttle page")
                page.goto("https://shuttleonline.ktmb.com.my/Home/Shuttle")
                page.wait_for_load_state("networkidle")

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
                logger.info("Scraping process completed successfully")
                return results

            except Exception as e:
                browser.close()
                logger.error(f"Scraping process failed: {e}", exc_info=True)
                return {"error": str(e), "success": False}

    def _select_direction(self, page):
        """Handle direction selection using JavaScript"""
        try:
            # Use JavaScript to set the direction directly
            if self.settings.direction == Direction.SG_TO_JB:
                # Set origin to Woodlands CIQ and destination to JB Sentral
                page.evaluate(
                    """
                    // Find the direction swap button and click it to get SG -> JB
                    const swapButton = document.querySelector('i[class*="swap"], i[class*="exchange"], i:nth-child(2)');
                    if (swapButton) {
                        swapButton.click();
                    }
                """
                )
                page.wait_for_timeout(1000)
                logger.debug("Direction set to SG -> JB (Woodlands CIQ -> JB Sentral)")
            else:
                # Default is JB -> SG, so no need to swap
                logger.debug("Direction set to JB -> SG (JB Sentral -> Woodlands CIQ)")

        except Exception as e:
            logger.error(f"Error selecting direction: {e}", exc_info=True)

    def _select_departure_date(self, page):
        """Handle departure date selection using JavaScript"""
        try:
            # Use JavaScript to set the date directly - this works reliably
            date_str = self.settings.depart_date.strftime(
                "%d %b %Y"
            )  # "01 Aug 2025" format
            logger.debug(f"Setting departure date to: {date_str}")

            page.evaluate(
                f"""
                document.querySelector('input[name="OnwardDate"]').value = '{date_str}';
                document.querySelector('input[name="OnwardDate"]').dispatchEvent(new Event('change', {{ bubbles: true }}));
            """
            )
            page.wait_for_timeout(500)

            logger.debug(f"Departure date set successfully to: {date_str}")

        except Exception as e:
            logger.error(f"Error selecting departure date: {e}", exc_info=True)
            raise e

    def _get_month_name(self, month_number):
        """Convert month number to month name"""
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
        return months.get(month_number, "January")

    def _get_month_number(self, month_name):
        """Convert month name to month number"""
        months = {
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12,
        }
        return months.get(month_name, 1)

    def _select_return_date(self, page):
        """Handle return date selection if specified"""
        try:
            if self.settings.return_date:
                # Use JavaScript to set the return date directly - similar to departure date
                return_date_str = self.settings.return_date.strftime(
                    "%d %b %Y"
                )  # "10 Aug 2025" format
                logger.debug(f"Setting return date to: {return_date_str}")

                page.evaluate(
                    f"""
                    document.querySelector('input[name="ReturnDate"]').value = '{return_date_str}';
                    document.querySelector('input[name="ReturnDate"]').dispatchEvent(new Event('change', {{ bubbles: true }}));
                """
                )
                page.wait_for_timeout(500)

                logger.debug(f"Return date set successfully to: {return_date_str}")

        except Exception as e:
            logger.error(f"Error selecting return date: {e}", exc_info=True)

    def _select_passengers(self, page):
        """Handle passenger selection"""
        try:
            # Select the passenger dropdown
            passenger_dropdown = page.locator("#PassengerCount")
            passenger_dropdown.click()

            # Select the appropriate number of passengers
            passenger_option = f"{self.settings.total_pax} Pax"
            passenger_dropdown.select_option(passenger_option)

            logger.info(f"Passengers set to: {passenger_option}")

        except Exception as e:
            logger.error(f"Error selecting passengers: {e}", exc_info=True)

    def _perform_search(self, page):
        """Perform the search and wait for results"""
        try:
            # Click the search button
            search_button = page.get_by_role("button", name="SEARCH")
            search_button.click()
            logger.debug("Search button clicked")

            # Wait a moment for the search to process (reduced timeout)
            page.wait_for_timeout(1000)

            # Check current URL to see if we were redirected
            current_url = page.url
            logger.debug(f"Current URL after search: {current_url}")

            # If we were redirected to the results page, that's good
            if "ShuttleTrip" in current_url:
                logger.debug("Successfully redirected to results page")
                return

            # Check for various possible outcomes on the search page
            try:
                # Wait for results table to appear (faster timeout)
                page.wait_for_selector("#tblTrainList", timeout=5000)
                logger.debug("Search completed successfully - results found")
            except:
                logger.warning("Results table not found, checking for errors...")

                # Check for validation error - use a more specific selector
                try:
                    error_element = page.locator("#OnwardDate-error")
                    if error_element.is_visible():
                        error_text = error_element.inner_text()
                        logger.error(f"Found validation error: {error_text}")
                        if "Please select departing date" in error_text:
                            raise Exception(
                                "Validation error: Please select departing date"
                            )
                except Exception as error_check:
                    logger.debug(f"Error check failed: {error_check}")

                # Check for other error messages
                try:
                    # Look for any error messages on the page
                    error_messages = page.locator(".alert, .error, .validation-error")
                    error_count = error_messages.count()
                    for i in range(error_count):
                        error_text = error_messages.nth(i).inner_text()
                        logger.error(f"Found error message: {error_text}")
                except:
                    pass

                # Take a screenshot for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"output/debug_screenshot_{timestamp}.png"
                page.screenshot(path=screenshot_path)
                logger.debug(f"Screenshot saved as {screenshot_path}")

                # Wait a bit more for results
                page.wait_for_timeout(3000)

        except Exception as e:
            logger.error(f"Error during search: {e}", exc_info=True)
            raise e

    def _parse_results(self, page) -> Dict[str, Any]:
        """Parse the search results table"""
        try:
            # Check if we're on the results page
            current_url = page.url
            logger.debug(f"Parsing results from URL: {current_url}")

            # Wait for page to load (faster timeout)
            page.wait_for_load_state("domcontentloaded")

            # Check if this is a round-trip search
            is_round_trip = bool(self.settings.return_date)

            if is_round_trip:
                return self._parse_round_trip_results(page)
            else:
                return self._parse_single_direction_results(page)

        except Exception as e:
            logger.error(f"Error parsing results: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Error parsing results: {str(e)}",
                "available_trains": [],
                "return_trains": [],
                "total_available": 0,
            }

    def _parse_single_direction_results(self, page) -> Dict[str, Any]:
        """Parse single direction search results"""
        # Try different selectors for the results table
        table_selectors = [
            "#tblTrainList",
            ".train-table",
            "table",
            ".results-table",
            '[data-testid="train-list"]',
        ]

        table_found = False
        selector = None
        for sel in table_selectors:
            try:
                page.wait_for_selector(sel, timeout=5000)
                logger.debug(f"Found results table with selector: {sel}")
                table_found = True
                selector = sel
                break
            except:
                continue

        if not table_found:
            # Take a screenshot to see what's on the page
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_screenshot_path = f"output/results_page_screenshot_{timestamp}.png"
            page.screenshot(path=results_screenshot_path)
            logger.warning(
                f"No results table found, screenshot saved as {results_screenshot_path}"
            )

            # Check if there's a "no results" message
            no_results_selectors = [
                'text="No trains available"',
                'text="No results found"',
                ".no-results",
                ".empty-state",
            ]

            for no_result_selector in no_results_selectors:
                try:
                    if page.locator(no_result_selector).is_visible():
                        logger.info("No trains available for the selected criteria")
                        return {
                            "success": True,
                            "available_trains": [],
                            "return_trains": [],
                            "total_available": 0,
                            "message": "No trains available for the selected criteria",
                            "search_criteria": {
                                "direction": self.settings.direction.value,
                                "depart_date": self.settings.depart_date.strftime(
                                    "%Y-%m-%d"
                                ),
                                "return_date": (
                                    self.settings.return_date.strftime("%Y-%m-%d")
                                    if self.settings.return_date
                                    else None
                                ),
                                "passengers": self.settings.total_pax,
                                "min_seats": self.settings.min_available_seats,
                            },
                            "scraped_at": datetime.now().isoformat(),
                        }
                except:
                    continue

            return {
                "success": False,
                "error": "Could not find results table or no results message",
                "available_trains": [],
                "return_trains": [],
                "total_available": 0,
            }

        # Get all train rows
        rows = page.query_selector_all(f"{selector} tbody tr, {selector} tr")
        logger.debug(f"Found {len(rows)} train rows to parse")

        available_trains = []

        for row in rows:
            cells = row.query_selector_all("td")
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

                logger.debug(
                    f"Parsed train: {train_number}, {departure_time}-{arrival_time}, {available_seats} seats"
                )

                # Check if this train meets our criteria
                if available_seats >= self.settings.min_available_seats:
                    # Check if train is in desired time slots
                    if self._is_train_in_desired_time_slots(departure_time):
                        train_info = {
                            "train_number": train_number,
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "available_seats": available_seats,
                            "direction": self.settings.direction.value,
                        }
                        available_trains.append(train_info)
                        logger.debug(f"Added train to available list: {train_number}")
                    else:
                        logger.debug(f"Train {train_number} not in desired time slots")
                else:
                    logger.debug(
                        f"Train {train_number} has insufficient seats ({available_seats} < {self.settings.min_available_seats})"
                    )

            except (ValueError, IndexError) as e:
                # Skip rows that can't be parsed
                logger.warning(f"Skipping row due to parsing error: {e}")
                continue

        logger.debug(
            f"Successfully parsed {len(available_trains)} available trains out of {len(rows)} total trains"
        )

        return {
            "success": True,
            "available_trains": available_trains,
            "return_trains": [],
            "total_available": len(available_trains),
            "search_criteria": {
                "direction": self.settings.direction.value,
                "depart_date": self.settings.depart_date.strftime("%Y-%m-%d"),
                "return_date": (
                    self.settings.return_date.strftime("%Y-%m-%d")
                    if self.settings.return_date
                    else None
                ),
                "passengers": self.settings.total_pax,
                "min_seats": self.settings.min_available_seats,
            },
            "scraped_at": datetime.now().isoformat(),
        }

    def _parse_round_trip_results(self, page) -> Dict[str, Any]:
        """Parse round-trip search results"""
        logger.info("Parsing round-trip results")

        # For round-trip searches, we need to look for multiple result sections
        # KTMB might show outbound and return results in separate sections

        # Try to find outbound and return sections
        outbound_trains = []
        return_trains = []

        # First, let's see what's actually on the page
        page_text = page.inner_text("body").lower()
        logger.debug(f"Page contains text: {page_text[:500]}...")  # First 500 chars

        # Look for section headers that might indicate outbound vs return
        section_headers = page.query_selector_all(
            "h2, h3, .section-header, .trip-header, .panel-title, .card-title"
        )

        if section_headers:
            logger.debug(f"Found {len(section_headers)} section headers")
            for i, header in enumerate(section_headers):
                header_text = header.inner_text().strip()
                logger.debug(f"Section header {i+1}: '{header_text}'")

                # Look for the next table after this header
                next_table = header.query_selector("xpath=following::table[1]")
                if next_table:
                    trains = self._parse_table_rows(next_table)
                    logger.debug(
                        f"Found {len(trains)} trains in section '{header_text}'"
                    )
                    if (
                        "outbound" in header_text.lower()
                        or "departure" in header_text.lower()
                        or "sg" in header_text.lower()
                        or "woodlands" in header_text.lower()
                    ):
                        outbound_trains.extend(trains)
                        logger.debug(
                            f"Added {len(trains)} outbound trains from section: {header_text}"
                        )
                    elif (
                        "return" in header_text.lower()
                        or "jb" in header_text.lower()
                        or "johor" in header_text.lower()
                    ):
                        return_trains.extend(trains)
                        logger.debug(
                            f"Added {len(trains)} return trains from section: {header_text}"
                        )
                    else:
                        logger.debug(
                            f"Unclassified section '{header_text}' with {len(trains)} trains"
                        )

        # If no sections found, try to parse all tables and assume first is outbound, second is return
        if not outbound_trains and not return_trains:
            tables = page.query_selector_all("table")
            logger.debug(f"Found {len(tables)} tables")

            if len(tables) >= 2:
                # Parse all tables and analyze their content
                all_table_trains = []
                for i, table in enumerate(tables):
                    trains = self._parse_table_rows(table)
                    logger.debug(f"Table {i+1}: {len(trains)} trains")
                    for train in trains:
                        logger.debug(
                            f"  Table {i+1} train: {train.get('train_number')} at {train.get('departure_time')}"
                        )
                    all_table_trains.append((i, trains))

                # Try to determine which table is which based on content
                # Look for patterns in train numbers or times
                for table_idx, trains in all_table_trains:
                    if not trains:
                        logger.debug(f"Table {table_idx+1} is empty")
                        continue

                    # Check if this looks like outbound trains (SG->JB)
                    # Outbound trains typically have even numbers and specific times
                    outbound_count = 0
                    return_count = 0

                    for train in trains:
                        train_number = train.get("train_number", "")
                        departure_time = train.get("departure_time", "")

                        # Check if this looks like an outbound train
                        # Outbound trains (SG->JB) typically have even numbers: 78, 80, 82, 84, 86, 88, 90, 92, 94, 96
                        # Return trains (JB->SG) typically have odd numbers: 77, 79, 81, 83, 85, 87, 89, 91, 93, 95
                        if any(
                            str(num) in train_number
                            for num in [78, 80, 82, 84, 86, 88, 90, 92, 94, 96]
                        ):
                            outbound_count += 1
                        elif any(
                            str(num) in train_number
                            for num in [77, 79, 81, 83, 85, 87, 89, 91, 93, 95]
                        ):
                            return_count += 1

                    logger.debug(
                        f"Table {table_idx+1}: {outbound_count} potential outbound, {return_count} potential return trains"
                    )

                    if outbound_count > return_count:
                        outbound_trains.extend(trains)
                        logger.debug(
                            f"Classified table {table_idx+1} as outbound with {len(trains)} trains"
                        )
                    elif return_count > outbound_count:
                        return_trains.extend(trains)
                        logger.debug(
                            f"Classified table {table_idx+1} as return with {len(trains)} trains"
                        )
                    else:
                        # If we can't determine, assume first table is outbound, second is return
                        if table_idx == 0:
                            outbound_trains.extend(trains)
                            logger.debug(
                                f"Assumed table {table_idx+1} is outbound (first table)"
                            )
                        else:
                            return_trains.extend(trains)
                            logger.debug(
                                f"Assumed table {table_idx+1} is return (not first table)"
                            )

                logger.debug(
                    f"Final classification: {len(outbound_trains)} outbound and {len(return_trains)} return trains"
                )

            elif len(tables) == 1:
                # Single table - might contain both directions or just one
                all_trains = self._parse_table_rows(tables[0])
                logger.debug(f"Single table found with {len(all_trains)} trains")
                # Try to separate by direction if possible
                for train in all_trains:
                    # This is a simplified approach - in practice, you might need more sophisticated logic
                    if train.get("direction") == Direction.SG_TO_JB.value:
                        outbound_trains.append(train)
                    else:
                        return_trains.append(train)

        # If still no trains found, try a different approach - look for any train data
        if not outbound_trains and not return_trains:
            logger.debug(
                "No trains found with section/table approach, trying alternative parsing..."
            )

            # Try to find any train rows on the page
            all_rows = page.query_selector_all("tr")
            logger.debug(f"Found {len(all_rows)} total rows on page")

            # Look for rows that might contain train data
            for i, row in enumerate(all_rows):
                cells = row.query_selector_all("td")
                if len(cells) >= 3:  # At least 3 columns (train, departure, arrival)
                    try:
                        # Try to parse this as a train row
                        if len(cells) >= 5:
                            train_number = cells[0].inner_text().strip()
                            departure_time = cells[1].inner_text().strip()
                            arrival_time = cells[2].inner_text().strip()
                            available_seats = int(cells[4].inner_text().strip())
                        elif len(cells) >= 4:
                            train_number = cells[0].inner_text().strip()
                            departure_time = cells[1].inner_text().strip()
                            arrival_time = cells[2].inner_text().strip()
                            available_seats = int(cells[3].inner_text().strip())
                        else:
                            continue

                        if train_number and departure_time and arrival_time:
                            train_info = {
                                "train_number": train_number,
                                "departure_time": departure_time,
                                "arrival_time": arrival_time,
                                "available_seats": available_seats,
                                "direction": self.settings.direction.value,
                            }
                            logger.debug(
                                f"Found train in row {i}: {train_number} at {departure_time}"
                            )
                            # For now, assume all trains are outbound (we'll need to refine this)
                            outbound_trains.append(train_info)
                    except (ValueError, IndexError) as e:
                        continue

        # Log raw train data before filtering
        logger.debug(f"Raw outbound trains before filtering: {len(outbound_trains)}")
        for train in outbound_trains:
            logger.debug(
                f"  Raw outbound: {train.get('train_number')} at {train.get('departure_time')} with {train.get('available_seats')} seats"
            )

        logger.debug(f"Raw return trains before filtering: {len(return_trains)}")
        for train in return_trains:
            logger.debug(
                f"  Raw return: {train.get('train_number')} at {train.get('departure_time')} with {train.get('available_seats')} seats"
            )

        # Filter trains based on criteria
        filtered_outbound = self._filter_trains(outbound_trains)
        filtered_return = self._filter_trains(return_trains)

        logger.info(
            f"Round-trip results: {len(filtered_outbound)} outbound, {len(filtered_return)} return trains"
        )

        return {
            "success": True,
            "available_trains": filtered_outbound,
            "return_trains": filtered_return,
            "total_available": len(filtered_outbound) + len(filtered_return),
            "search_criteria": {
                "direction": self.settings.direction.value,
                "depart_date": self.settings.depart_date.strftime("%Y-%m-%d"),
                "return_date": (
                    self.settings.return_date.strftime("%Y-%m-%d")
                    if self.settings.return_date
                    else None
                ),
                "passengers": self.settings.total_pax,
                "min_seats": self.settings.min_available_seats,
            },
            "scraped_at": datetime.now().isoformat(),
        }

    def _parse_table_rows(self, table) -> List[Dict]:
        """Parse train rows from a table element"""
        trains = []
        rows = table.query_selector_all("tbody tr, tr")

        for row in rows:
            cells = row.query_selector_all("td")
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
                    train_number = f"Train {len(trains) + 1}"
                    departure_time = cells[0].inner_text().strip()
                    arrival_time = cells[1].inner_text().strip()
                    available_seats = int(cells[2].inner_text().strip())

                train_info = {
                    "train_number": train_number,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "available_seats": available_seats,
                    "direction": self.settings.direction.value,
                }
                trains.append(train_info)

            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping row due to parsing error: {e}")
                continue

        return trains

    def _filter_trains(self, trains: List[Dict]) -> List[Dict]:
        """Filter trains based on criteria"""
        filtered = []

        logger.debug(
            f"Filtering {len(trains)} trains with criteria: min_seats={self.settings.min_available_seats}, time_slots={[ts.value for ts in self.settings.desired_time_slots]}"
        )

        for train in trains:
            available_seats = train.get("available_seats", 0)
            departure_time = train.get("departure_time", "")
            train_number = train.get("train_number", "Unknown")

            logger.debug(
                f"Checking train {train_number}: {departure_time} with {available_seats} seats"
            )

            # Check if this train meets our criteria
            if available_seats >= self.settings.min_available_seats:
                logger.debug(
                    f"  Train {train_number} has sufficient seats ({available_seats} >= {self.settings.min_available_seats})"
                )
                # Check if train is in desired time slots
                if self._is_train_in_desired_time_slots(departure_time):
                    filtered.append(train)
                    logger.debug(f"  ✓ Added train {train_number} to filtered list")
                else:
                    logger.debug(f"  ✗ Train {train_number} not in desired time slots")
            else:
                logger.debug(
                    f"  ✗ Train {train_number} has insufficient seats ({available_seats} < {self.settings.min_available_seats})"
                )

        logger.debug(f"Filtered result: {len(filtered)} trains out of {len(trains)}")
        return filtered
