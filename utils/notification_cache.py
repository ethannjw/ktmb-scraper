#!/usr/bin/env python3
"""
Notification Cache Module
Prevents duplicate Telegram notifications for the same train availability
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from utils.config import Direction

logger = logging.getLogger(__name__)


class NotificationCache:
    """Manages notification cache to prevent duplicate alerts"""

    def __init__(self, cache_file_path: str = "./cache/notification_cache.json", expiry_hours: int = 24):
        """
        Initialize notification cache
        
        Args:
            cache_file_path: Path to JSON cache file
            expiry_hours: Hours until cache entries expire (default: 24)
        """
        self.cache_file_path = Path(cache_file_path)
        self.expiry_hours = expiry_hours
        self.cache_data = self._load_cache()
    
    @staticmethod
    def _get_opposite_direction(direction: Direction) -> Direction:
        """Get the opposite direction for return trips"""
        if direction == Direction.SG_TO_JB:
            return Direction.JB_TO_SG
        else:
            return Direction.SG_TO_JB

    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from JSON file"""
        try:
            if self.cache_file_path.exists():
                with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Loaded cache with {len(data.get('entries', {}))} entries")
                    return data
            else:
                logger.info("No existing cache file found, creating new cache")
                return {"cache_version": "1.0", "entries": {}}
        except Exception as e:
            logger.warning(f"Failed to load cache file: {e}, creating new cache")
            return {"cache_version": "1.0", "entries": {}}

    def _save_cache(self) -> None:
        """Save cache to JSON file"""
        try:
            # Create directory if it doesn't exist
            self.cache_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cache saved with {len(self.cache_data.get('entries', {}))} entries")
        except Exception as e:
            logger.error(f"Failed to save cache file: {e}")

    def _generate_cache_key(self, result: Dict[str, Any], search_settings: Any) -> str:
        """
        Generate unique cache key based on search parameters and results
        
        Args:
            result: Search result containing available trains
            search_settings: Search settings with date, direction, etc.
            
        Returns:
            MD5 hash as cache key
        """
        # Extract key components
        depart_date = search_settings.depart_date.isoformat()
        direction = search_settings.direction.value
        
        # Sort trains by train number for consistent hashing
        available_trains = result.get("available_trains", [])
        return_trains = result.get("return_trains", [])
        
        # Determine directions
        outbound_direction = search_settings.direction.value
        return_direction = self._get_opposite_direction(search_settings.direction).value if return_trains else None
        
        # Create train signatures (train_number, departure_time, available_seats, direction)
        train_signatures = []
        
        for train in sorted(available_trains, key=lambda t: t.get("train_number", "")):
            train_signatures.append({
                "train_number": train.get("train_number"),
                "departure_time": train.get("departure_time"),
                "available_seats": train.get("available_seats", 0),
                "direction": outbound_direction
            })
        
        # For round-trip, include return trains with their direction
        if return_trains:
            return_date = search_settings.return_date.isoformat() if search_settings.return_date else None
            for train in sorted(return_trains, key=lambda t: t.get("train_number", "")):
                train_signatures.append({
                    "train_number": train.get("train_number"),
                    "departure_time": train.get("departure_time"),
                    "available_seats": train.get("available_seats", 0),
                    "direction": return_direction
                })
        else:
            return_date = None
        
        # Create hashable string
        key_data = {
            "date": depart_date,
            "direction": direction,
            "return_date": return_date,
            "trains": train_signatures
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode('utf-8')).hexdigest()
        
        logger.debug(f"Generated cache key: {cache_key} for {depart_date} {direction}")
        return cache_key

    def should_send_notification(self, result: Dict[str, Any], search_settings: Any) -> bool:
        """
        Check if notification should be sent based on cache
        
        Args:
            result: Search result containing available trains
            search_settings: Search settings with date, direction, etc.
            
        Returns:
            True if notification should be sent, False if already notified
        """
        # Don't check cache if search was not successful
        if not result.get("success", False):
            return True
        
        # Check if there are any available trains
        available_trains = result.get("available_trains", [])
        return_trains = result.get("return_trains", [])
        
        if not available_trains and not return_trains:
            # No trains available, no need to cache or notify
            return False
        
        cache_key = self._generate_cache_key(result, search_settings)
        
        # Check if this exact availability was already notified
        if cache_key in self.cache_data["entries"]:
            entry = self.cache_data["entries"][cache_key]
            expires_at = datetime.fromisoformat(entry["expires_at"])
            
            if datetime.now() < expires_at:
                logger.info(f"Cache hit: Already notified for this availability (expires at {expires_at})")
                return False
            else:
                logger.info(f"Cache expired: Will send notification again")
                # Remove expired entry
                del self.cache_data["entries"][cache_key]
        
        logger.info(f"Cache miss: New availability detected, will send notification")
        return True

    def add_to_cache(self, result: Dict[str, Any], search_settings: Any) -> None:
        """
        Add notification to cache after successful send
        
        Args:
            result: Search result containing available trains
            search_settings: Search settings with date, direction, etc.
        """
        cache_key = self._generate_cache_key(result, search_settings)
        
        # Prepare trains data for storage
        available_trains = result.get("available_trains", [])
        return_trains = result.get("return_trains", [])
        
        # Determine directions
        outbound_direction = search_settings.direction.value
        return_direction = self._get_opposite_direction(search_settings.direction).value if return_trains else None
        
        trains_data = []
        for train in available_trains:
            trains_data.append({
                "train_number": train.get("train_number"),
                "departure_time": train.get("departure_time"),
                "available_seats": train.get("available_seats", 0),
                "direction": outbound_direction
            })
        
        for train in return_trains:
            trains_data.append({
                "train_number": train.get("train_number"),
                "departure_time": train.get("departure_time"),
                "available_seats": train.get("available_seats", 0),
                "direction": return_direction
            })
        
        now = datetime.now()
        expires_at = now + timedelta(hours=self.expiry_hours)
        
        # Store cache entry
        self.cache_data["entries"][cache_key] = {
            "date": search_settings.depart_date.isoformat(),
            "direction": search_settings.direction.value,
            "return_date": search_settings.return_date.isoformat() if search_settings.return_date else None,
            "trains": trains_data,
            "notified_at": now.isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        self._save_cache()
        logger.info(f"Added to cache: {cache_key} (expires at {expires_at})")

    def cleanup_expired(self) -> None:
        """Remove expired cache entries"""
        now = datetime.now()
        initial_count = len(self.cache_data["entries"])
        
        # Find expired entries
        expired_keys = []
        for key, entry in self.cache_data["entries"].items():
            try:
                expires_at = datetime.fromisoformat(entry["expires_at"])
                if now >= expires_at:
                    expired_keys.append(key)
            except Exception as e:
                logger.warning(f"Invalid cache entry {key}: {e}, removing")
                expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self.cache_data["entries"][key]
        
        if expired_keys:
            self._save_cache()
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries ({initial_count} -> {len(self.cache_data['entries'])})")
