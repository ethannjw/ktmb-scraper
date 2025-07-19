#!/usr/bin/env python3
"""
Example script showing how to use KTMB Scraper with Telegram notifications
"""

import os
from dotenv import load_dotenv
from scraper.main import KTMBShuttleScraper
from config import ScraperSettings, Direction, TimeSlot
from notifications import create_notification_sender
from datetime import date

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Create notification sender
    notification_sender = create_notification_sender()
    
    # Example search settings
    settings = ScraperSettings(
        direction=Direction.SG_TO_JB,  # Woodlands → JB
        depart_date=date(2025, 8, 10),  # Example date
        num_adults=1,
        min_available_seats=1,
        desired_time_slots=[TimeSlot.EVENING]  # Only evening trains
    )
    
    print(f"Searching for trains on {settings.depart_date.strftime('%A, %d %B %Y')}")
    print(f"Direction: {Direction.SG_TO_JB}")
    print(f"Time slots: {[slot.value for slot in settings.desired_time_slots]}")
    print("-" * 50)
    
    # Run the scraper
    scraper = KTMBShuttleScraper(settings)
    result = scraper.run()
    
    # Send notification if trains are available
    if notification_sender.send_notification(result, settings):
        print("✅ Notification sent successfully!")
    else:
        print("❌ No notification sent (no available trains or notification disabled)")
    
    # Display results
    if result.get("success", False):
        available_trains = result.get("available_trains", [])
        print(f"\nSearch Results:")
        print(f"Available trains found: {len(available_trains)}")
        
        if available_trains:
            print("\nAvailable Trains:")
            for train in available_trains:
                seats = train.get("available_seats", 0)
                status = "✅" if seats >= 1 else "❌"
                print(f"  {status} {train.get('train_number', 'Unknown')}: {train.get('departure_time', '')} → {train.get('arrival_time', '')} ({seats} seats)")
    else:
        print(f"❌ Search failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 