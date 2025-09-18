import requests
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)


class HealthCheckPinger:
    """A class to handle healthcheck pings to healthchecks.io on-demand"""

    def __init__(self, url: str):
        """
        Initialize the HealthCheckPinger.

        Args:
            url: The healthchecks.io URL to ping
        """
        self.url = url

    def ping(self) -> bool:
        """
        Send a healthcheck ping.

        Returns:
            True if ping was sent successfully, False otherwise
        """
        if not self.url:
            logger.error("No healthcheck URL provided")
            return False

        return self.send_healthchecks_ping(self.url)

    def ping_fail(self) -> bool:
        """
        Send a healthcheck fail ping to indicate an error occurred.

        Returns:
            True if ping was sent successfully, False otherwise
        """
        if not self.url:
            logger.error("No healthcheck URL provided")
            return False

        return self.send_healthchecks_ping_fail(self.url)

    @staticmethod
    def send_healthchecks_ping(url: str) -> bool:
        """Send a ping to healthchecks.io if URL is provided."""
        if not url:
            return False
        try:
            ping_url = url.rstrip("/")
            response = requests.get(ping_url, timeout=10)
            response.raise_for_status()
            logger.debug("Healthchecks.io ping sent")
            return True
        except Exception as e:
            logger.error(f"Failed to send healthchecks.io ping: {e}")
            return False

    @staticmethod
    def send_healthchecks_ping_fail(url: str) -> bool:
        """Send a fail ping to healthchecks.io if URL is provided."""
        if not url:
            return False
        try:
            ping_url = url.rstrip("/")
            fail_url = f"{ping_url}/fail"
            response = requests.post(fail_url, timeout=10)
            response.raise_for_status()
            logger.debug("Healthchecks.io fail ping sent")
            return True
        except Exception as e:
            logger.error(f"Failed to send healthchecks.io fail ping: {e}")
            return False
