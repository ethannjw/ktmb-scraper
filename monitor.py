#!/usr/bin/env python3
"""
KTMB Continuous Monitoring Script
Runs the scraper at specified intervals and sends notifications
"""

import os
import sys
import time
import signal
import argparse
from datetime import datetime, date, timedelta
from typing import Optional, List
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.main import KTMBShuttleScraper
from config import ScraperSettings, Direction, TimeSlot
from notifications import create_notification_sender


class KTMBMonitor:
    """Continuous monitoring for KTMB train availability"""
    
    def __init__(self, interval_minutes: int = 30):
        self.interval_minutes = interval_minutes
        self.running = True
        self.notification_sender = create_notification_sender()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def search_specific_date(self, search_date: date, direction: Direction, time_slots: Optional[List[TimeSlot]] = None) -> tuple[dict, ScraperSettings]:
        """Search for trains on a specific date"""
        if time_slots is None:
            time_slots = [TimeSlot.EVENING]  # Default to evening
        
        settings = ScraperSettings(
            direction=direction,
            depart_date=search_date,
            num_adults=1,
            min_available_seats=1,
            desired_time_slots=time_slots
        )
        
        print(f"🔍 Searching for trains on {search_date.strftime('%A, %d %B %Y')}")
        print(f"   Direction: {direction.value}")
        print(f"   Time slots: {[slot.value for slot in time_slots]}")
        
        scraper = KTMBShuttleScraper(settings)
        result = scraper.run()
        
        return result, settings
    
    def search_weekends(self, year: int, month: int, direction: Direction, time_slots: Optional[List[TimeSlot]] = None) -> List[tuple]:
        """Search for weekend trains in a month"""
        results = []
        today = date.today()
        
        # Get all Fridays and Sundays in the month
        current_date = date(year, month, 1)
        while current_date.month == month:
            # Only search for future dates
            if current_date >= today:
                if current_date.weekday() == 4:  # Friday
                    result, settings = self.search_specific_date(current_date, Direction.SG_TO_JB, time_slots)
                    results.append((result, settings))
                elif current_date.weekday() == 6:  # Sunday
                    result, settings = self.search_specific_date(current_date, Direction.JB_TO_SG, time_slots)
                    results.append((result, settings))
            
            current_date += timedelta(days=1)
        
        return results
    
    def search_next_two_months_weekends(self, time_slots: Optional[List[TimeSlot]] = None) -> List[tuple]:
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
            
            print(f"🔍 Searching weekends in {date(year, month, 1).strftime('%B %Y')}")
            month_results = self.search_weekends(year, month, Direction.SG_TO_JB, time_slots)
            results.extend(month_results)
        
        return results
    
    def run_single_search(self, search_type: str, **kwargs) -> None:
        """Run a single search based on type"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🚂 KTMB Monitor - {timestamp}")
        print(f"{'='*60}")
        
        if search_type == "specific_date":
            search_date = kwargs['date']
            direction = kwargs['direction']
            time_slots = kwargs.get('time_slots')
            result, settings = self.search_specific_date(search_date, direction, time_slots)
            
            # Send notification
            if self.notification_sender.send_notification(result, settings):
                print("✅ Notification sent successfully!")
            else:
                print("ℹ️ No notification sent")
            
            # Display results
            self._display_results(result)
            
        elif search_type == "weekends":
            year = kwargs['year']
            month = kwargs['month']
            direction = kwargs['direction']
            time_slots = kwargs.get('time_slots')
            
            print(f"🔍 Searching weekends in {date(year, month, 1).strftime('%B %Y')}")
            print(f"   Direction: {direction.value}")
            
            results = self.search_weekends(year, month, direction, time_slots)
            
            # Send notifications for each result
            for result, settings in results:
                if self.notification_sender.send_notification(result, settings):
                    print(f"✅ Notification sent for {settings.depart_date.strftime('%A, %d %B')}")
                else:
                    print(f"ℹ️ No notification for {settings.depart_date.strftime('%A, %d %B')}")
                
                self._display_results(result)
        
        elif search_type == "next_two_months":
            time_slots = kwargs.get('time_slots')
            
            print("🔍 Searching weekends for the next 2 months")
            
            results = self.search_next_two_months_weekends(time_slots)
            
            # Send notifications for each result
            for result, settings in results:
                if self.notification_sender.send_notification(result, settings):
                    print(f"✅ Notification sent for {settings.depart_date.strftime('%A, %d %B')}")
                else:
                    print(f"ℹ️ No notification for {settings.depart_date.strftime('%A, %d %B')}")
                
                self._display_results(result)
    
    def _display_results(self, result: dict) -> None:
        """Display search results"""
        if result.get("success", False):
            available_trains = result.get("available_trains", [])
            print(f"\n📊 Results: {len(available_trains)} trains found")
            
            if available_trains:
                print("🚂 Available Trains:")
                for train in available_trains:
                    seats = train.get("available_seats", 0)
                    status = "🟢" if seats >= 5 else "🟡" if seats >= 2 else "🔴"
                    print(f"   {status} {train.get('train_number', 'Unknown')}: "
                          f"{train.get('departure_time', '')} → {train.get('arrival_time', '')} "
                          f"({seats} seats)")
            else:
                print("❌ No available trains found")
        else:
            print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
    
    def run_continuous_monitoring(self, search_type: str, **kwargs) -> None:
        """Run continuous monitoring with specified interval"""
        print(f"🚀 Starting continuous monitoring...")
        print(f"   Interval: {self.interval_minutes} minutes")
        print(f"   Search type: {search_type}")
        print(f"   Press Ctrl+C to stop")
        print(f"{'='*60}")
        
        iteration = 1
        
        while self.running:
            try:
                print(f"\n🔄 Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.run_single_search(search_type, **kwargs)
                
                if not self.running:
                    break
                
                print(f"\n⏰ Waiting {self.interval_minutes} minutes until next check...")
                print(f"   Next check: {(datetime.now() + timedelta(minutes=self.interval_minutes)).strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Sleep in smaller intervals to allow for graceful shutdown
                for _ in range(self.interval_minutes * 60):
                    if not self.running:
                        break
                    time.sleep(1)
                
                iteration += 1
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                print("⏰ Waiting 5 minutes before retrying...")
                time.sleep(300)
        
        print("👋 Monitoring stopped")


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


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

  # Continuous monitoring for next 2 months every 30 minutes
  python monitor.py --continuous --interval 30

  # Continuous monitoring for specific date every 30 minutes
  python monitor.py --date 2025-08-15 --direction jb-to-sg --continuous --interval 30

  # Continuous monitoring for weekends every hour
  python monitor.py --weekends --year 2025 --month 8 --continuous --interval 60

  # Continuous monitoring for weekends with early morning and evening trains
  python monitor.py --weekends --year 2025 --month 8 --time-slots early_morning evening --continuous --interval 120
        """
    )
    
    # Search type options
    parser.add_argument(
        "--date", "-d",
        type=parse_date,
        help="Specific date to search (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--weekends", "-w",
        action="store_true",
        help="Search weekends in a specific month (requires --year and --month)"
    )
    
    # Weekend search options
    parser.add_argument(
        "--year", "-y",
        type=int,
        help="Year for weekend search (required with --weekends)"
    )
    parser.add_argument(
        "--month", "-m",
        type=int,
        choices=range(1, 13),
        help="Month for weekend search (required with --weekends)"
    )
    
    # Direction option
    parser.add_argument(
        "--direction", "-dir",
        choices=["sg-to-jb", "jb-to-sg"],
        default="sg-to-jb",
        help="Direction for specific date search (default: sg-to-jb)"
    )
    
    # Time slot options
    parser.add_argument(
        "--time-slots", "-t",
        nargs="+",
        choices=["early_morning", "morning", "afternoon", "evening", "night"],
        help="Time slots to search for (default: evening). Can specify multiple: --time-slots morning evening"
    )
    
    # Monitoring options
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="Interval between checks in minutes (default: 30)"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuous monitoring"
    )
    args = parser.parse_args()
    
    # Validate arguments
    if args.weekends:
        if args.year is None or args.month is None:
            parser.error("--year and --month are required when using --weekends")
    
    # Check if any search type is specified
    if not args.date and not args.weekends:
        # Default to next two months weekends
        args.weekends = True
        print("ℹ️ No specific search type provided, defaulting to weekends for next 2 months")
    
    if args.interval < 1:
        parser.error("Interval must be at least 1 minute")
    
    # Load environment variables
    load_dotenv()
    
    # Create monitor
    monitor = KTMBMonitor(interval_minutes=args.interval)
    
    # Parse time slots
    time_slots = None
    if args.time_slots:
        time_slots = [TimeSlot(slot) for slot in args.time_slots]
    
    # Determine search type and parameters
    if args.date:
        search_type = "specific_date"
        direction = Direction.JB_TO_SG if args.direction == "jb-to-sg" else Direction.SG_TO_JB
        kwargs = {
            "date": args.date,
            "direction": direction,
            "time_slots": time_slots
        }
    elif args.weekends:
        if args.year is not None and args.month is not None:
            # Specific month weekends
            search_type = "weekends"
            direction = Direction.JB_TO_SG if args.direction == "jb-to-sg" else Direction.SG_TO_JB
            kwargs = {
                "year": args.year,
                "month": args.month,
                "direction": direction,
                "time_slots": time_slots
            }
        else:
            # Next two months weekends (default)
            search_type = "next_two_months"
            kwargs = {
                "time_slots": time_slots
            }
    
    # Run monitoring
    if args.continuous:
        monitor.run_continuous_monitoring(search_type, **kwargs)
    else:
        monitor.run_single_search(search_type, **kwargs)


if __name__ == "__main__":
    main() 