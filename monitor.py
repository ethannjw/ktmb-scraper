#!/usr/bin/env python3
"""
KTMB Continuous Monitoring Script
Runs the scraper at specified intervals and sends notifications

Environment Variables:
- HEALTHCHECKS_IO_URL: (optional) If set, a ping will be sent to this healthchecks.io URL every 5 minutes in a background thread, independent of notification logic.
"""

import os
import sys
import time
import signal
import argparse
from datetime import datetime, date, timedelta
from typing import Optional, List
from dotenv import load_dotenv
import threading

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.main import KTMBShuttleScraper
from utils.config import ScraperSettings, Direction, TimeSlot
from notifications.notifications import create_notification_sender
from utils.logging_config import setup_logging, get_logger
from scraper.healthcheck import run_healthcheck_server
from notifications.healthchecks import HealthCheckPinger

# Setup logging
logger = setup_logging()


class KTMBMonitor:
    """Continuous monitoring for KTMB train availability"""

    def __init__(self, interval_minutes: int = 30):
        self.interval_minutes = interval_minutes
        self.running = True
        self.notification_sender = create_notification_sender()

        # Set up signal handlers for graceful shutdown (only SIGTERM)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
        # If we get a second signal, force exit
        if hasattr(self, '_shutdown_requested'):
            logger.warning("Force shutdown requested, exiting immediately...")
            import sys
            sys.exit(1)
        else:
            self._shutdown_requested = True


    def search_specific_date(
        self,
        search_date: date,
        direction: Direction,
        time_slots: Optional[List[TimeSlot]] = None,
    ) -> tuple[dict, ScraperSettings]:
        """Search for trains on a specific date"""
        if time_slots is None:
            time_slots = [TimeSlot.EVENING]  # Default to evening

        settings = ScraperSettings(
            direction=direction,
            depart_date=search_date,
            num_adults=1,
            min_available_seats=1,
            desired_time_slots=time_slots,
        )

        logger.info(f"Searching for trains on {search_date.strftime('%A, %d %B %Y')}")
        logger.info(f"Direction: {direction.value}")
        logger.info(f"Time slots: {[slot.value for slot in time_slots]}")

        scraper = KTMBShuttleScraper(settings)
        result = scraper.run()

        return result, settings

    def search_weekend_round_trip(
        self,
        friday_date: date,
        sunday_date: date,
        time_slots: Optional[List[TimeSlot]] = None,
    ) -> tuple[dict, ScraperSettings]:
        """Search for round-trip weekend trains (Friday SG->JB, Sunday JB->SG) in a single scrape"""
        if time_slots is None:
            time_slots = [TimeSlot.EVENING]  # Default to evening

        settings = ScraperSettings(
            direction=Direction.SG_TO_JB,  # Start with SG->JB direction
            depart_date=friday_date,
            return_date=sunday_date,  # Add return date for round-trip search
            num_adults=1,
            min_available_seats=1,
            desired_time_slots=time_slots,
        )

        logger.info(
            f"Searching for weekend round-trip: {friday_date.strftime('%A, %d %B %Y')} (SG->JB) to {sunday_date.strftime('%A, %d %B %Y')} (JB->SG)"
        )
        logger.info(f"Time slots: {[slot.value for slot in time_slots]}")

        scraper = KTMBShuttleScraper(settings)
        result = scraper.run()

        return result, settings

    def search_weekends(
        self,
        year: int,
        month: int,
        direction: Direction,
        time_slots: Optional[List[TimeSlot]] = None,
    ) -> List[tuple]:
        """Search for weekend trains in a month using round-trip searches for efficiency"""
        results = []
        today = date.today()

        # Get all Fridays and Sundays in the month
        current_date = date(year, month, 1)
        while current_date.month == month:
            # Only search for future dates
            if current_date >= today:
                if current_date.weekday() == 4:  # Friday
                    # Search for round-trip: Friday (SG->JB) and Sunday (JB->SG)
                    friday_date = current_date
                    sunday_date = current_date + timedelta(days=2)

                    # Only search if Sunday is also in the same month
                    if sunday_date.month == month:
                        result, settings = self.search_weekend_round_trip(
                            friday_date, sunday_date, time_slots
                        )
                        results.append((result, settings))
                    else:
                        # If Sunday is in next month, just search Friday one-way
                        result, settings = self.search_specific_date(
                            friday_date, Direction.SG_TO_JB, time_slots
                        )
                        results.append((result, settings))

            current_date += timedelta(days=1)

        return results

    def search_next_two_months_weekends(
        self, time_slots: Optional[List[TimeSlot]] = None
    ) -> List[tuple]:
        """Search for weekend trains in the next 2 months"""
        results = []
        current_date = datetime.now().date()

        # Get next 2 months (starting from next month)
        for i in range(1, 3):  # Start from 1 to skip current month
            # Calculate next month properly
            if current_date.month == 12:
                year = current_date.year + 1
                month = 1
            else:
                year = current_date.year
                month = current_date.month + i

            logger.info(
                f"Searching weekends in {date(year, month, 1).strftime('%B %Y')}"
            )
            month_results = self.search_weekends(
                year, month, Direction.SG_TO_JB, time_slots
            )
            results.extend(month_results)

        return results

    def run_single_search(self, search_type: str, **kwargs) -> None:
        """Run a single search based on type"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("=" * 60)
        logger.info(f"KTMB Monitor - {timestamp}")
        logger.info("=" * 60)

        if search_type == "specific_date":
            search_date = kwargs["date"]
            direction = kwargs["direction"]
            time_slots = kwargs.get("time_slots")
            result, settings = self.search_specific_date(
                search_date, direction, time_slots
            )

            # Send notification
            if self.notification_sender.send_notification(result, settings):
                logger.info("Notification sent successfully!")
            else:
                logger.info("No notification sent")

            # Display results
            self._display_results(result)

        elif search_type == "round_trip":
            depart_date = kwargs["depart_date"]
            return_date = kwargs["return_date"]
            time_slots = kwargs.get("time_slots")

            logger.info(
                f"Searching for round-trip: {depart_date.strftime('%A, %d %B %Y')} to {return_date.strftime('%A, %d %B %Y')}"
            )

            result, settings = self.search_weekend_round_trip(
                depart_date, return_date, time_slots
            )

            # Send notification
            if self.notification_sender.send_notification(result, settings):
                logger.info("Notification sent successfully!")
            else:
                logger.info("No notification sent")

            # Display results
            self._display_results(result)

        elif search_type == "weekends":
            year = kwargs["year"]
            month = kwargs["month"]
            direction = kwargs["direction"]
            time_slots = kwargs.get("time_slots")

            logger.info(
                f"Searching weekends in {date(year, month, 1).strftime('%B %Y')}"
            )
            logger.info(f"Direction: {direction.value}")

            results = self.search_weekends(year, month, direction, time_slots)

            # Send notifications for each result
            for result, settings in results:
                if self.notification_sender.send_notification(result, settings):
                    logger.info(
                        f"Notification sent for {settings.depart_date.strftime('%A, %d %B')}"
                    )
                else:
                    logger.info(
                        f"No notification for {settings.depart_date.strftime('%A, %d %B')}"
                    )

                self._display_results(result)

        elif search_type == "next_two_months":
            time_slots = kwargs.get("time_slots")

            logger.info("Searching weekends for the next 2 months")

            results = self.search_next_two_months_weekends(time_slots)

            # Send notifications for each result
            for result, settings in results:
                if self.notification_sender.send_notification(result, settings):
                    logger.info(
                        f"Notification sent for {settings.depart_date.strftime('%A, %d %B')}"
                    )
                else:
                    logger.info(
                        f"No notification for {settings.depart_date.strftime('%A, %d %B')}"
                    )

                self._display_results(result)

    def _display_results(self, result: dict) -> None:
        """Display search results"""
        if result.get("success", False):
            available_trains = result.get("available_trains", [])
            return_trains = result.get("return_trains", [])

            # Check if this is a round-trip search
            is_round_trip = bool(return_trains)

            if is_round_trip:
                logger.info(
                    f"Round-trip Results: {len(available_trains)} outbound trains, {len(return_trains)} return trains found"
                )

                if available_trains:
                    logger.info("Outbound Trains (SG→JB):")
                    for train in available_trains:
                        seats = train.get("available_seats", 0)
                        status = "🟢" if seats >= 5 else "🟡" if seats >= 2 else "🔴"
                        logger.info(
                            f"   {status} {train.get('train_number', 'Unknown')}: "
                            f"{train.get('departure_time', '')} → {train.get('arrival_time', '')} "
                            f"({seats} seats)"
                        )
                else:
                    logger.info("No available outbound trains found")

                if return_trains:
                    logger.info("Return Trains (JB→SG):")
                    for train in return_trains:
                        seats = train.get("available_seats", 0)
                        status = "🟢" if seats >= 5 else "🟡" if seats >= 2 else "🔴"
                        logger.info(
                            f"   {status} {train.get('train_number', 'Unknown')}: "
                            f"{train.get('departure_time', '')} → {train.get('arrival_time', '')} "
                            f"({seats} seats)"
                        )
                else:
                    logger.info("No available return trains found")
            else:
                # Single direction search
                logger.info(f"Results: {len(available_trains)} trains found")

                if available_trains:
                    logger.info("Available Trains:")
                    for train in available_trains:
                        seats = train.get("available_seats", 0)
                        status = "🟢" if seats >= 5 else "🟡" if seats >= 2 else "🔴"
                        logger.info(
                            f"   {status} {train.get('train_number', 'Unknown')}: "
                            f"{train.get('departure_time', '')} → {train.get('arrival_time', '')} "
                            f"({seats} seats)"
                        )
                else:
                    logger.info("No available trains found")
        else:
            logger.error(f"Search failed: {result.get('error', 'Unknown error')}")

    def run_continuous_monitoring(self, search_type: str, healthcheck_pinger=None, **kwargs) -> None:
        """Run continuous monitoring with specified interval"""
        logger.info("Starting continuous monitoring...")
        logger.info(f"Interval: {self.interval_minutes} minutes")
        logger.info(f"Search type: {search_type}")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        iteration = 1

        while self.running:
            try:
                logger.info(
                    f"Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Send healthcheck ping at the start of each iteration
                if healthcheck_pinger:
                    if healthcheck_pinger.ping():
                        logger.debug("Healthcheck ping sent successfully")
                    else:
                        logger.warning("Failed to send healthcheck ping")

                self.run_single_search(search_type, **kwargs)

                if not self.running:
                    break

                logger.info(
                    f"Waiting {self.interval_minutes} minutes until next check..."
                )
                logger.info(
                    f"Next check: {(datetime.now() + timedelta(minutes=self.interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Sleep in smaller intervals to allow for graceful shutdown
                for _ in range(self.interval_minutes * 60):
                    if not self.running:
                        break
                    time.sleep(1)

                iteration += 1

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                # Check if this is a user interruption
                if "Interrupted by user" in str(e):
                    logger.info("Monitoring interrupted by user")
                    break
                
                # Send error healthcheck ping if encountering any error
                if healthcheck_pinger:
                    if healthcheck_pinger.ping_fail():
                        logger.debug("Error healthcheck ping sent successfully")
                    else:
                        logger.warning("Failed to send error healthcheck ping")
                
                logger.error(f"Error during monitoring: {e}")
                logger.info("Waiting 5 minutes before retrying...")
                
                # Sleep in smaller intervals to allow for graceful shutdown
                for _ in range(300):  # 5 minutes = 300 seconds
                    if not self.running:
                        break
                    time.sleep(1)

        logger.info("Monitoring stopped")


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: {date_str}. Use YYYY-MM-DD"
        )


def main():
    parser = argparse.ArgumentParser(
        description="KTMB Continuous Monitoring Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: Search weekends for next 2 months (evening trains)
  python monitor.py

  # Single search for specific date (default: evening trains)
  python monitor.py --date 2025-08-15 --direction jb-to-sg

  # Single search for specific date with morning and evening trains
  python monitor.py --date 2025-08-15 --direction jb-to-sg --time-slots morning evening

  # Single search for weekends in August 2025
  python monitor.py --weekends --year 2025 --month 8

  # Single search for afternoon trains only
  python monitor.py --date 2025-08-15 --direction jb-to-sg --time-slots afternoon

  # Round-trip search for specific dates (Friday to Sunday)
  python monitor.py --round-trip --depart-date 2025-08-15 --return-date 2025-08-17

  # Round-trip search with specific time slots
  python monitor.py --round-trip --depart-date 2025-08-15 --return-date 2025-08-17 --time-slots morning evening

  # Continuous monitoring for next 2 months every 30 minutes
  python monitor.py --continuous --interval 30

  # Continuous monitoring for specific date every 30 minutes
  python monitor.py --date 2025-08-15 --direction jb-to-sg --continuous --interval 30

  # Continuous monitoring for weekends every hour
  python monitor.py --weekends --year 2025 --month 8 --continuous --interval 60

  # Continuous monitoring for weekends with early morning and evening trains
  python monitor.py --weekends --year 2025 --month 8 --time-slots early_morning evening --continuous --interval 120

  # Continuous monitoring for round-trip every 30 minutes
  python monitor.py --round-trip --depart-date 2025-08-15 --return-date 2025-08-17 --continuous --interval 30
        """,
    )

    # Search type options
    parser.add_argument(
        "--date",
        "-d",
        type=parse_date,
        help="Specific date to search (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--weekends",
        "-w",
        action="store_true",
        help="Search weekends in a specific month (requires --year and --month)",
    )
    parser.add_argument(
        "--round-trip",
        "-rt",
        action="store_true",
        help="Search for round-trip trains (requires --depart-date and --return-date)",
    )

    # Weekend search options
    parser.add_argument(
        "--year",
        "-y",
        type=int,
        help="Year for weekend search (required with --weekends)",
    )
    parser.add_argument(
        "--month",
        "-m",
        type=int,
        choices=range(1, 13),
        help="Month for weekend search (required with --weekends)",
    )

    # Round-trip search options
    parser.add_argument(
        "--depart-date",
        "-dd",
        type=parse_date,
        help="Departure date for round-trip search (YYYY-MM-DD format, required with --round-trip)",
    )
    parser.add_argument(
        "--return-date",
        "-rd",
        type=parse_date,
        help="Return date for round-trip search (YYYY-MM-DD format, required with --round-trip)",
    )

    # Direction option
    parser.add_argument(
        "--direction",
        "-dir",
        choices=["sg-to-jb", "jb-to-sg"],
        default="sg-to-jb",
        help="Direction for specific date search (default: sg-to-jb)",
    )

    # Time slot options
    parser.add_argument(
        "--time-slots",
        "-t",
        nargs="+",
        choices=["early_morning", "morning", "afternoon", "evening", "night"],
        help="Time slots to search for (default: evening). Can specify multiple: --time-slots morning evening",
    )

    # Monitoring options
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=60,
        help="Interval between checks in minutes (default: 30)",
    )
    parser.add_argument(
        "--continuous", action="store_true", help="Run continuous monitoring"
    )
    args = parser.parse_args()

    # Validate arguments
    if args.weekends:
        if args.year is None or args.month is None:
            parser.error("--year and --month are required when using --weekends")

    if args.round_trip:
        if args.depart_date is None or args.return_date is None:
            parser.error(
                "--depart-date and --return-date are required when using --round-trip"
            )
        if args.depart_date >= args.return_date:
            parser.error("--return-date must be after --depart-date")

    # Check if any search type is specified
    if not args.date and not args.weekends and not args.round_trip:
        # Default to next two months weekends
        args.weekends = True
        logger.info(
            "No specific search type provided, defaulting to weekends for next 2 months"
        )

    if args.interval < 1:
        parser.error("Interval must be at least 1 minute")

    # Load environment variables
    load_dotenv()

    # Start healthcheck server in a background thread
    if os.environ.get("HEALTHCHECK") == "1":
        t = threading.Thread(target=run_healthcheck_server, daemon=True)
        t.start()

    # Initialize healthchecks.io pinger if configured
    healthchecks_url = os.getenv("HEALTHCHECKS_IO_URL")
    healthcheck_pinger = None
    if healthchecks_url:
        healthcheck_pinger = HealthCheckPinger(healthchecks_url)
        logger.info("HealthCheckPinger initialized for on-demand pings")
    else:
        logger.info("HEALTHCHECKS_IO_URL not set, HealthCheckPinger not configured")

    # Create monitor
    monitor = KTMBMonitor(interval_minutes=args.interval)

    # Parse time slots
    time_slots = None
    if args.time_slots:
        time_slots = [TimeSlot(slot) for slot in args.time_slots]

    # Determine search type and parameters
    if args.round_trip:
        search_type = "round_trip"
        kwargs = {
            "depart_date": args.depart_date,
            "return_date": args.return_date,
            "time_slots": time_slots,
        }
    elif args.date:
        search_type = "specific_date"
        direction = (
            Direction.JB_TO_SG if args.direction == "jb-to-sg" else Direction.SG_TO_JB
        )
        kwargs = {"date": args.date, "direction": direction, "time_slots": time_slots}
    elif args.weekends:
        if args.year is not None and args.month is not None:
            # Specific month weekends
            search_type = "weekends"
            direction = (
                Direction.JB_TO_SG
                if args.direction == "jb-to-sg"
                else Direction.SG_TO_JB
            )
            kwargs = {
                "year": args.year,
                "month": args.month,
                "direction": direction,
                "time_slots": time_slots,
            }
        else:
            # Next two months weekends (default)
            search_type = "next_two_months"
            kwargs = {"time_slots": time_slots}


    # Run monitoring
    if args.continuous:
        monitor.run_continuous_monitoring(search_type, healthcheck_pinger=healthcheck_pinger, **kwargs)
    else:
        monitor.run_single_search(search_type, **kwargs)



if __name__ == "__main__":
    main()
