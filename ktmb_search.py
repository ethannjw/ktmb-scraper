#!/usr/bin/env python3
"""
KTMB Shuttle Search Tool
Searches for evening train slots on KTMB Shuttle service
Configurable for any dates, directions, and time slots
"""

from scraper.main import KTMBShuttleScraper
from utils.config import ScraperSettings, Direction, TimeSlot, TIME_SLOT_RANGES
from datetime import date, timedelta, time
import json
import calendar
import argparse
import sys
import os
from datetime import datetime

def get_fridays_in_month(year, month):
    """Get all Friday dates in a specific month"""
    fridays = []
    start_date = date(year, month, 1)
    
    # Find the first Friday of the month
    current_date = start_date
    while current_date.weekday() != calendar.FRIDAY:
        current_date += timedelta(days=1)
    
    # Get all Fridays in the month
    while current_date.month == month:
        fridays.append(current_date)
        current_date += timedelta(days=7)
    
    return fridays

def get_sundays_in_month(year, month):
    """Get all Sunday dates in a specific month"""
    sundays = []
    start_date = date(year, month, 1)
    
    # Find the first Sunday of the month
    current_date = start_date
    while current_date.weekday() != calendar.SUNDAY:
        current_date += timedelta(days=1)
    
    # Get all Sundays in the month
    while current_date.month == month:
        sundays.append(current_date)
        current_date += timedelta(days=7)
    
    return sundays

def filter_evening_trains(trains):
    """Filter trains to only include evening slots (18:00 - 21:59)"""
    evening_start, evening_end = TIME_SLOT_RANGES[TimeSlot.EVENING]
    evening_trains = []
    for train in trains:
        try:
            departure_time_str = train["departure_time"]
            departure_hour, departure_minute = map(int, departure_time_str.split(":"))
            departure_time = time(departure_hour, departure_minute)
            
            # Check if departure time falls within evening range
            if evening_start <= departure_time <= evening_end:
                evening_trains.append(train)
        except (ValueError, IndexError):
            continue
    return evening_trains

def search_friday_evening_slots(fridays):
    """Search for Friday evening slots from Woodlands to JB"""
    print("=" * 60)
    print("SEARCHING FOR FRIDAY EVENING SLOTS")
    print("Direction: Woodlands CIQ → JB Sentral")
    print("=" * 60)
    
    all_results = []
    
    for i, friday in enumerate(fridays, 1):
        print(f"\n--- Friday {friday.strftime('%A, %d %B %Y')} ({i}/{len(fridays)}) ---")
        
        settings = ScraperSettings(
            direction=Direction.SG_TO_JB,  # Woodlands → JB
            depart_date=friday,
            num_adults=1,
            min_available_seats=1
        )
        
        scraper = KTMBShuttleScraper(settings)
        results = scraper.run()
        
        if results.get("success") and results.get("available_trains"):
            # Filter for evening slots using TimeSlot.EVENING range (18:00 - 21:59)
            evening_trains = filter_evening_trains(results["available_trains"])
            
            if evening_trains:
                print(f"✅ Found {len(evening_trains)} evening trains:")
                for train in evening_trains:
                    print(f"   🚂 {train['train_number']}: {train['departure_time']} → {train['arrival_time']} ({train['available_seats']} seats)")
                
                all_results.append({
                    "date": friday.strftime('%Y-%m-%d'),
                    "day": friday.strftime('%A'),
                    "direction": "Woodlands → JB",
                    "evening_trains": evening_trains,
                    "total_evening": len(evening_trains)
                })
            else:
                print("❌ No evening trains available")
        else:
            print("❌ No trains available or search failed")
    
    return all_results

def search_sunday_evening_slots(sundays):
    """Search for Sunday evening slots from JB to Woodlands"""
    print("\n" + "=" * 60)
    print("SEARCHING FOR SUNDAY EVENING SLOTS")
    print("Direction: JB Sentral → Woodlands CIQ")
    print("=" * 60)
    
    all_results = []
    
    for i, sunday in enumerate(sundays, 1):
        print(f"\n--- Sunday {sunday.strftime('%A, %d %B %Y')} ({i}/{len(sundays)}) ---")
        
        settings = ScraperSettings(
            direction=Direction.JB_TO_SG,  # JB → Woodlands
            depart_date=sunday,
            num_adults=1,
            min_available_seats=1
        )
        
        scraper = KTMBShuttleScraper(settings)
        results = scraper.run()
        
        if results.get("success") and results.get("available_trains"):
            # Filter for evening slots using TimeSlot.EVENING range (18:00 - 21:59)
            evening_trains = filter_evening_trains(results["available_trains"])
            
            if evening_trains:
                print(f"✅ Found {len(evening_trains)} evening trains:")
                for train in evening_trains:
                    print(f"   🚂 {train['train_number']}: {train['departure_time']} → {train['arrival_time']} ({train['available_seats']} seats)")
                
                all_results.append({
                    "date": sunday.strftime('%Y-%m-%d'),
                    "day": sunday.strftime('%A'),
                    "direction": "JB → Woodlands",
                    "evening_trains": evening_trains,
                    "total_evening": len(evening_trains)
                })
            else:
                print("❌ No evening trains available")
        else:
            print("❌ No trains available or search failed")
    
    return all_results

def search_specific_dates(dates, direction):
    """Search for specific dates in a given direction"""
    print("=" * 60)
    print(f"SEARCHING FOR SPECIFIC DATES")
    print(f"Direction: {'Woodlands CIQ → JB Sentral' if direction == Direction.SG_TO_JB else 'JB Sentral → Woodlands CIQ'}")
    print("=" * 60)
    
    all_results = []
    
    for i, search_date in enumerate(dates, 1):
        print(f"\n--- {search_date.strftime('%A, %d %B %Y')} ({i}/{len(dates)}) ---")
        
        settings = ScraperSettings(
            direction=direction,
            depart_date=search_date,
            num_adults=1,
            min_available_seats=1
        )
        
        scraper = KTMBShuttleScraper(settings)
        results = scraper.run()
        
        if results.get("success") and results.get("available_trains"):
            # Filter for evening slots using TimeSlot.EVENING range (18:00 - 21:59)
            evening_trains = filter_evening_trains(results["available_trains"])
            
            if evening_trains:
                print(f"✅ Found {len(evening_trains)} evening trains:")
                for train in evening_trains:
                    print(f"   🚂 {train['train_number']}: {train['departure_time']} → {train['arrival_time']} ({train['available_seats']} seats)")
                
                all_results.append({
                    "date": search_date.strftime('%Y-%m-%d'),
                    "day": search_date.strftime('%A'),
                    "direction": "Woodlands → JB" if direction == Direction.SG_TO_JB else "JB → Woodlands",
                    "evening_trains": evening_trains,
                    "total_evening": len(evening_trains)
                })
            else:
                print("❌ No evening trains available")
        else:
            print("❌ No trains available or search failed")
    
    return all_results

def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format"""
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def generate_output_filename(args):
    """Generate a descriptive filename based on search parameters"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.dates:
        # Specific dates
        date_str = "_".join([d.strftime("%Y%m%d") for d in args.dates])
        direction = args.direction.replace("-", "_")
        filename = f"ktmb_specific_dates_{date_str}_{direction}_{timestamp}.json"
    else:
        # Month search
        month_name = datetime(args.year, args.month, 1).strftime("%b").lower()
        direction = "both_directions"
        
        if args.fridays_only:
            search_type = "fridays_only"
        elif args.sundays_only:
            search_type = "sundays_only"
        else:
            search_type = "weekends"
        
        filename = f"ktmb_{month_name}_{args.year}_{search_type}_{timestamp}.json"
    
    return os.path.join("output", filename)

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Search for evening train slots on KTMB Shuttle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search August 2025 weekends
  python ktmb_search.py --month 8 --year 2025
  
  # Search specific dates
  python ktmb_search.py --dates 2025-08-01 2025-08-15 --direction sg-to-jb
  
  # Search September 2024 weekends
  python ktmb_search.py --month 9 --year 2024
  
  # Search only Fridays in October 2025
  python ktmb_search.py --month 10 --year 2025 --fridays-only
  
  # Search only Sundays in November 2025
  python ktmb_search.py --month 11 --year 2025 --sundays-only
        """
    )
    
    # Date range options
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        '--month', '-m',
        type=int,
        help='Month to search (1-12)'
    )
    date_group.add_argument(
        '--dates', '-d',
        nargs='+',
        type=parse_date,
        help='Specific dates to search (YYYY-MM-DD format)'
    )
    
    # Year option (required when using --month)
    parser.add_argument(
        '--year', '-y',
        type=int,
        help='Year to search (required when using --month)'
    )
    
    # Direction option (for specific dates)
    parser.add_argument(
        '--direction', '-dir',
        choices=['sg-to-jb', 'jb-to-sg'],
        default='sg-to-jb',
        help='Direction for specific dates (default: sg-to-jb)'
    )
    
    # Weekend options
    parser.add_argument(
        '--fridays-only',
        action='store_true',
        help='Search only Fridays (when using --month)'
    )
    parser.add_argument(
        '--sundays-only',
        action='store_true',
        help='Search only Sundays (when using --month)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file name (default: auto-generated based on search parameters)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.month and not args.year:
        parser.error("--year is required when using --month")
    
    if args.month and (args.month < 1 or args.month > 12):
        parser.error("Month must be between 1 and 12")
    
    if args.year and (args.year < 2024 or args.year > 2030):
        print("Warning: Year seems unusual. Continuing anyway...")
    
    # Generate output filename
    if args.output:
        output_file = os.path.join("output", args.output)
    else:
        output_file = generate_output_filename(args)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Determine search dates and directions
    if args.dates:
        # Search specific dates
        direction = Direction.SG_TO_JB if args.direction == 'sg-to-jb' else Direction.JB_TO_SG
        friday_results = []
        sunday_results = []
        specific_results = search_specific_dates(args.dates, direction)
        
        # Categorize results by day of week
        for result in specific_results:
            if result['day'] == 'Friday':
                friday_results.append(result)
            elif result['day'] == 'Sunday':
                sunday_results.append(result)
        
        search_type = f"Specific dates in {args.direction.upper()}"
        
    else:
        # Search month weekends
        fridays = get_fridays_in_month(args.year, args.month)
        sundays = get_sundays_in_month(args.year, args.month)
        
        if not fridays and not sundays:
            print(f"❌ No Fridays or Sundays found in {args.month}/{args.year}")
            sys.exit(1)
        
        friday_results = []
        sunday_results = []
        
        # Search Fridays
        if not args.sundays_only and fridays:
            friday_results = search_friday_evening_slots(fridays)
        
        # Search Sundays
        if not args.fridays_only and sundays:
            sunday_results = search_sunday_evening_slots(sundays)
        
        search_type = f"{args.month}/{args.year} weekends"
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\n📅 Friday Evening Slots (Woodlands → JB):")
    if friday_results:
        for result in friday_results:
            print(f"   {result['date']} ({result['day']}): {result['total_evening']} trains")
    else:
        print("   No evening slots found")
    
    print(f"\n📅 Sunday Evening Slots (JB → Woodlands):")
    if sunday_results:
        for result in sunday_results:
            print(f"   {result['date']} ({result['day']}): {result['total_evening']} trains")
    else:
        print("   No evening slots found")
    
    # Save detailed results to file
    all_results = {
        "search_type": search_type,
        "friday_evening": friday_results,
        "sunday_evening": sunday_results,
        "summary": {
            "total_fridays_with_evening": len(friday_results),
            "total_sundays_with_evening": len(sunday_results),
            "search_date": date.today().isoformat()
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("\n🎉 Search completed!")

if __name__ == "__main__":
    main() 