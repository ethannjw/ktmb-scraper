#!/usr/bin/env python3
"""
KTMB Notification Module
Sends Telegram notifications when trains are available
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from config import TrainTiming, ScrapingResult, Direction, DIRECTION_MAPPING

# Set up logging
logger = logging.getLogger(__name__)


class NotificationConfig:
    """Configuration for Telegram notification settings from environment variables"""
    
    def __init__(self):
        # Telegram bot configuration
        self.telegram_enabled = os.getenv('NOTIFICATION_TELEGRAM_ENABLED', 'false').lower() == 'true'
        self.telegram_bot_token = os.getenv('NOTIFICATION_TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('NOTIFICATION_TELEGRAM_CHAT_ID')
        
        # Notification settings
        self.min_seats_threshold = int(os.getenv('NOTIFICATION_MIN_SEATS', '1'))
        self.only_notify_on_availability = os.getenv('NOTIFICATION_ONLY_AVAILABLE', 'true').lower() == 'true'
        
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if self.telegram_enabled:
            if not self.telegram_bot_token:
                errors.append("NOTIFICATION_TELEGRAM_BOT_TOKEN is required when Telegram notifications are enabled")
            if not self.telegram_chat_id:
                errors.append("NOTIFICATION_TELEGRAM_CHAT_ID is required when Telegram notifications are enabled")
        
        return errors


class NotificationSender:
    """Handles sending notifications through various channels"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.errors = config.validate()
        if self.errors:
            logger.warning(f"Notification configuration errors: {self.errors}")
    
    def should_send_notification(self, result: Dict[str, Any]) -> bool:
        """Determine if notification should be sent based on results"""
        if not result.get("success", False):
            return False
        
        if self.config.only_notify_on_availability:
            # Check if there are any available trains with sufficient seats
            available_trains = result.get("available_trains", [])
            return any(
                train.get("available_seats", 0) >= self.config.min_seats_threshold
                for train in available_trains
            )
        
        return True
    
    def format_train_info(self, trains: List[Dict[str, Any]], direction: str) -> str:
        """Format train information for notification"""
        if not trains:
            return f"❌ No trains available for {direction}"
        
        available_trains = [t for t in trains if t.get("available_seats", 0) >= self.config.min_seats_threshold]
        if not available_trains:
            return f"⚠️ No trains with {self.config.min_seats_threshold}+ seats for {direction}"
        
        lines = [f"✅ {len(available_trains)} trains available for {direction}:"]
        for train in available_trains:
            seats = train.get("available_seats", 0)
            status = "🟢" if seats >= 5 else "🟡" if seats >= 2 else "🔴"
            lines.append(
                f"   {status} {train.get('train_number', 'Unknown')}: {train.get('departure_time', '')} → {train.get('arrival_time', '')} "
                f"({seats} seats)"
            )
        
        return "\n".join(lines)
    
    def create_notification_content(self, result: Dict[str, Any], search_settings: Any) -> Dict[str, str]:
        """Create notification content for different channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create subject/title
        direction_name = DIRECTION_MAPPING.get(search_settings.direction, str(search_settings.direction))
        date_str = search_settings.depart_date.strftime("%A, %d %B %Y")
        
        if result.get("success", False):
            available_trains = result.get("available_trains", [])
            has_available = any(t.get("available_seats", 0) >= self.config.min_seats_threshold for t in available_trains)
            
            if has_available:
                subject = f"🚂 KTMB Trains Available - {date_str}"
            else:
                subject = f"⚠️ KTMB Search Complete - {date_str}"
        else:
            subject = f"❌ KTMB Search Failed - {date_str}"
        
        # Create message body
        body_lines = [
            f"**KTMB Shuttle Search Results**",
            f"**Date:** {date_str}",
            f"**Direction:** {direction_name}",
            f"**Searched at:** {timestamp}",
            "",
        ]
        
        if result.get("success", False):
            available_trains = result.get("available_trains", [])
            body_lines.append(self.format_train_info(available_trains, "Available Trains"))
        else:
            body_lines.append(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        
        body = "\n".join(body_lines)
        
        return {
            "subject": subject,
            "body": body,
            "plain_text": body.replace("**", "").replace("✅", "✓").replace("❌", "✗").replace("⚠️", "!"),
            "timestamp": timestamp
        }
    

    
    def send_telegram_notification(self, content: Dict[str, str]) -> bool:
        """Send Telegram bot notification"""
        if not self.config.telegram_enabled or self.errors:
            return False
        
        try:
            # Telegram supports markdown formatting
            message = f"*{content['subject']}*\n\n{content['body']}"
            
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.config.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Telegram notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def send_notification(self, result: Dict[str, Any], search_settings: Any) -> bool:
        """Send Telegram notification when trains are available"""
        if not self.should_send_notification(result):
            logger.info("Skipping notification - no available trains or notification not required")
            return False
        
        if not self.config.telegram_enabled:
            logger.info("Telegram notifications are disabled")
            return False
        
        content = self.create_notification_content(result, search_settings)
        
        if self.send_telegram_notification(content):
            logger.info("Telegram notification sent successfully")
            return True
        else:
            logger.warning("Failed to send Telegram notification")
            return False


def create_notification_sender() -> NotificationSender:
    """Factory function to create notification sender with configuration"""
    config = NotificationConfig()
    return NotificationSender(config) 