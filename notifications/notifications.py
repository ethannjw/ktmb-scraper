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
from utils.config import TrainTiming, ScrapingResult, Direction, DIRECTION_MAPPING
from notifications.healthchecks import HealthCheckPinger
from utils.notification_cache import NotificationCache

# Set up logging
logger = logging.getLogger(__name__)


class NotificationConfig:
    """Configuration for Telegram and healthchecks.io notification settings from environment variables"""

    def __init__(self):
        # Telegram bot configuration
        self.telegram_enabled = (
            os.getenv("NOTIFICATION_TELEGRAM_ENABLED", "false").lower() == "true"
        )
        self.telegram_bot_token = os.getenv("NOTIFICATION_TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("NOTIFICATION_TELEGRAM_CHAT_ID")

        # Notification settings
        self.min_seats_threshold = int(os.getenv("NOTIFICATION_MIN_SEATS", "1"))
        self.only_notify_on_availability = (
            os.getenv("NOTIFICATION_ONLY_AVAILABLE", "true").lower() == "true"
        )
        self.stdout_enabled = (
            os.getenv("NOTIFICATION_STDOUT_ENABLED", "false").lower() == "true"
        )

        # Healthchecks.io configuration
        self.healthchecks_io_url = os.getenv("HEALTHCHECKS_IO_URL")
        
        # Cache configuration
        self.cache_enabled = os.getenv("NOTIFICATION_CACHE_ENABLED", "true").lower() == "true"
        self.cache_file_path = os.getenv("NOTIFICATION_CACHE_FILE", "./cache/notification_cache.json")
        self.cache_expiry_hours = float(os.getenv("NOTIFICATION_CACHE_EXPIRY_HOURS", "24"))

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        if self.telegram_enabled:
            if not self.telegram_bot_token:
                errors.append(
                    "NOTIFICATION_TELEGRAM_BOT_TOKEN is required when Telegram notifications are enabled"
                )
            if not self.telegram_chat_id:
                errors.append(
                    "NOTIFICATION_TELEGRAM_CHAT_ID is required when Telegram notifications are enabled"
                )
        # No required fields for healthchecks.io
        return errors


class NotificationSender:
    """Handles sending notifications through various channels"""

    def __init__(self, config: NotificationConfig):
        self.config = config
        self.errors = config.validate()
        if self.errors:
            logger.warning(f"Notification configuration errors: {self.errors}")
        
        # Initialize notification cache
        if config.cache_enabled:
            self.cache = NotificationCache(
                cache_file_path=config.cache_file_path,
                expiry_hours=config.cache_expiry_hours
            )
            logger.info(f"Notification cache enabled (expiry: {config.cache_expiry_hours}h)")
        else:
            self.cache = None
            logger.info("Notification cache disabled")

    def should_send_notification(self, result: Dict[str, Any]) -> bool:
        """Determine if notification should be sent based on results"""
        if not result.get("success", False):
            return False

        if self.config.only_notify_on_availability:
            # Check if there are any available trains with sufficient seats
            available_trains = result.get("available_trains", [])
            return_trains = result.get("return_trains", [])

            # For round-trip searches, check both outbound and return trains
            has_available_outbound = any(
                train.get("available_seats", 0) >= self.config.min_seats_threshold
                for train in available_trains
            )

            has_available_return = any(
                train.get("available_seats", 0) >= self.config.min_seats_threshold
                for train in return_trains
            )

            # Send notification if either direction has available trains
            return has_available_outbound or has_available_return

        return True

    def format_train_info(self, trains: List[Dict[str, Any]], direction: str) -> str:
        """Format train information for notification"""
        if not trains:
            return f"❌ No trains available for {direction}"

        available_trains = [
            t
            for t in trains
            if t.get("available_seats", 0) >= self.config.min_seats_threshold
        ]
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

    def create_notification_content(
        self, result: Dict[str, Any], search_settings: Any
    ) -> Dict[str, str]:
        """Create notification content for different channels"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create subject/title
        direction_name = DIRECTION_MAPPING.get(
            search_settings.direction, str(search_settings.direction)
        )
        depart_date_str = search_settings.depart_date.strftime("%A, %d %B %Y")
        return_date_str = None
        # Check if this is a round-trip search
        is_round_trip = bool(search_settings.return_date)

        if is_round_trip:
            return_date_str = search_settings.return_date.strftime("%A, %d %B %Y")

        if result.get("success", False):
            available_trains = result.get("available_trains", [])
            return_trains = result.get("return_trains", [])

            has_available_outbound = any(
                t.get("available_seats", 0) >= self.config.min_seats_threshold
                for t in available_trains
            )
            has_available_return = any(
                t.get("available_seats", 0) >= self.config.min_seats_threshold
                for t in return_trains
            )

            if is_round_trip:
                if has_available_outbound and has_available_return:
                    subject = f"🚂 KTMB Round-Trip Available - {depart_date_str}"
                elif has_available_outbound:
                    subject = f"🚂 KTMB Outbound Available - {depart_date_str}"
                elif has_available_return:
                    subject = f"🚂 KTMB Return Available - {return_date_str}"
                else:
                    subject = f"⚠️ KTMB Round-Trip Search Complete - {depart_date_str}"
            else:
                if has_available_outbound:
                    subject = f"🚂 KTMB Trains Available - {depart_date_str}"
                else:
                    subject = f"⚠️ KTMB Search Complete - {depart_date_str}"
        else:
            subject = f"❌ KTMB Search Failed - {depart_date_str}"

        # Create message body
        body_lines = [
            f"**KTMB Shuttle Search Results**",
            f"**Date:** {depart_date_str}",
        ]

        if is_round_trip:
            return_date_str = search_settings.return_date.strftime("%A, %d %B %Y")
            body_lines.extend(
                [
                    f"**Type:** Round-Trip",
                    f"**Outbound:** {depart_date_str}",
                    f"**Return:** {return_date_str}",
                ]
            )
        else:
            body_lines.extend(
                [
                    f"**Direction:** {direction_name}",
                ]
            )

        body_lines.extend(
            [
                f"**Searched at:** {timestamp}",
                "",
            ]
        )

        if result.get("success", False):
            available_trains = result.get("available_trains", [])
            return_trains = result.get("return_trains", [])

            if is_round_trip:
                body_lines.append(
                    self.format_train_info(available_trains, "Outbound Trains (SG→JB)")
                )
                body_lines.append("")  # Add spacing
                body_lines.append(
                    self.format_train_info(return_trains, "Return Trains (JB→SG)")
                )
            else:
                body_lines.append(
                    self.format_train_info(available_trains, "Available Trains")
                )
        else:
            body_lines.append(
                f"❌ Search failed: {result.get('error', 'Unknown error')}"
            )

        body = "\n".join(body_lines)

        return {
            "subject": subject,
            "body": body,
            "plain_text": body.replace("**", "")
            .replace("✅", "✓")
            .replace("❌", "✗")
            .replace("⚠️", "!"),
            "timestamp": timestamp,
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
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Telegram notification sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    def send_stdout_notification(self, content: Dict[str, str]) -> bool:
        """Print notification content for script/cron integrations."""
        if not self.config.stdout_enabled:
            return False

        message = f"*{content['subject']}*\n\n{content['body']}"
        print(message)
        logger.info("Stdout notification emitted successfully")
        return True

    def send_notification(self, result: Dict[str, Any], search_settings: Any) -> bool:
        """Send configured notifications when trains are available"""
        should_notify = self.should_send_notification(result)
        
        if not should_notify:
            logger.debug("Skipping notification (not required)")
            return False
        
        # Check cache before sending
        if self.cache and not self.cache.should_send_notification(result, search_settings):
            logger.info("Skipping notification (already notified - cache hit)")
            return False
        
        content = self.create_notification_content(result, search_settings)
        telegram_sent = False
        stdout_sent = False
        if self.config.telegram_enabled:
            telegram_sent = self.send_telegram_notification(content)
            if telegram_sent:
                logger.info("Telegram notification sent successfully")
            else:
                logger.warning("Failed to send Telegram notification")
        else:
            logger.info("Skipping Telegram notification (disabled)")

        if self.config.stdout_enabled:
            stdout_sent = self.send_stdout_notification(content)

        notification_sent = telegram_sent or stdout_sent
        if notification_sent and self.cache:
            self.cache.add_to_cache(result, search_settings)
            self.cache.cleanup_expired()

        return notification_sent


def create_notification_sender() -> NotificationSender:
    """Factory function to create notification sender with configuration"""
    config = NotificationConfig()
    return NotificationSender(config)
