"""HTML parsing module for KTMB train data."""

from playwright.sync_api import Page
from loguru import logger
from config import TrainTiming, TimeSlot, TIME_SLOT_RANGES
from typing import List, Optional
from datetime import time
import re


class TrainDataParser:
    """Parses train timing and availability data from KTMB pages."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def parse_train_table(self) -> List[TrainTiming]:
        """Parse the train timetable from the results page."""
        trains = []
        
        try:
            # Wait for table to load
            self.page.wait_for_selector("table", timeout=10000)
            
            # Find all train rows
            rows = self.page.query_selector_all("table tbody tr")
            
            if not rows:
                logger.warning("No train rows found in table")
                return trains
            
            logger.info(f"Found {len(rows)} train rows to parse")
            
            for i, row in enumerate(rows):
                try:
                    train = self._parse_train_row(row)
                    if train:
                        trains.append(train)
                        logger.debug(f"Parsed train: {train.train_number} at {train.departure_time}")
                except Exception as e:
                    logger.warning(f"Failed to parse row {i}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(trains)} trains")
            
        except Exception as e:
            logger.error(f"Failed to parse train table: {e}")
        
        return trains
    
    def _parse_train_row(self, row) -> Optional[TrainTiming]:
        """Parse a single train row."""
        try:
            cells = row.query_selector_all("td")
            
            if len(cells) < 4:
                logger.debug("Row has insufficient columns")
                return None
            
            # Extract data from cells (adjust indices based on actual table structure)
            train_number = self._extract_text(cells[0])
            departure_time = self._extract_text(cells[1])
            arrival_time = self._extract_text(cells[2])
            
            # Try to find seat availability (could be in different columns)
            available_seats = self._extract_seat_count(cells)
            
            if not all([train_number, departure_time, arrival_time]):
                logger.debug("Missing required train data")
                return None
            
            # Determine time slot
            time_slot = self._determine_time_slot(departure_time)
            
            # Check if seats are available
            is_available = available_seats > 0
            
            return TrainTiming(
                train_number=train_number,
                departure_time=departure_time,
                arrival_time=arrival_time,
                available_seats=available_seats,
                time_slot=time_slot,
                is_available=is_available
            )
            
        except Exception as e:
            logger.warning(f"Error parsing train row: {e}")
            return None
    
    def _extract_text(self, cell) -> str:
        """Extract clean text from a table cell."""
        if not cell:
            return ""
        
        text = cell.inner_text().strip()
        return text
    
    def _extract_seat_count(self, cells) -> int:
        """Extract available seat count from table cells."""
        # Look for seat information in various possible columns
        for cell in cells:
            text = self._extract_text(cell)
            
            # Look for patterns like "5 seats", "Available: 3", etc.
            seat_patterns = [
                r'(\d+)\s*seats?',
                r'available:?\s*(\d+)',
                r'(\d+)\s*available',
                r'^(\d+)$'  # Just a number
            ]
            
            for pattern in seat_patterns:
                match = re.search(pattern, text.lower())
                if match:
                    try:
                        return int(match.group(1))
                    except ValueError:
                        continue
            
            # Check for "FULL" or "SOLD OUT" indicators
            if any(keyword in text.upper() for keyword in ['FULL', 'SOLD', 'UNAVAILABLE']):
                return 0
        
        # Default to 0 if no seat info found
        logger.debug("No seat count found, defaulting to 0")
        return 0
    
    def _determine_time_slot(self, time_str: str) -> TimeSlot:
        """Determine which time slot a departure time falls into."""
        try:
            # Extract time from string (handle formats like "07:30", "7:30 AM", etc.)
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            
            if not time_match:
                logger.debug(f"Could not parse time from: {time_str}")
                return TimeSlot.MORNING  # Default fallback
            
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            
            # Handle AM/PM if present
            if 'PM' in time_str.upper() and hour != 12:
                hour += 12
            elif 'AM' in time_str.upper() and hour == 12:
                hour = 0
            
            departure_time = time(hour, minute)
            
            # Check which time slot this falls into
            for slot, (start_time, end_time) in TIME_SLOT_RANGES.items():
                if start_time <= end_time:  # Normal range (not crossing midnight)
                    if start_time <= departure_time <= end_time:
                        return slot
                else:  # Range crosses midnight (like night slot)
                    if departure_time >= start_time or departure_time <= end_time:
                        return slot
            
            # Default fallback
            return TimeSlot.MORNING
            
        except Exception as e:
            logger.warning(f"Error determining time slot for {time_str}: {e}")
            return TimeSlot.MORNING
    
    def check_for_errors(self) -> Optional[str]:
        """Check if the page contains any error messages."""
        try:
            # Common error selectors
            error_selectors = [
                ".alert-danger",
                ".error-message",
                ".validation-summary-errors",
                "[class*='error']"
            ]
            
            for selector in error_selectors:
                error_elements = self.page.query_selector_all(selector)
                for element in error_elements:
                    error_text = element.inner_text().strip()
                    if error_text:
                        return error_text
            
            # Check for "no results" messages
            no_results_text = [
                "no trains available",
                "no results found",
                "tidak ada keretapi",
                "tiada keputusan"
            ]
            
            page_text = self.page.inner_text("body").lower()
            for text in no_results_text:
                if text in page_text:
                    return f"No trains available for selected criteria"
            
            return None
            
        except Exception as e:
            logger.warning(f"Error checking for page errors: {e}")
            return None