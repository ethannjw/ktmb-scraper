import requests
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)


class HealthCheckPinger:
    """A class to handle periodic healthcheck pings to healthchecks.io"""

    def __init__(self, url: str, ping_interval_sec: int = 300):
        """
        Initialize the HealthCheckPinger.

        Args:
            url: The healthchecks.io URL to ping
            ping_interval_sec: Interval between pings in seconds (default: 300 = 5 minutes)
        """
        self.url = url
        self.ping_interval_sec = ping_interval_sec
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> bool:
        """
        Start the periodic ping thread.

        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            logger.warning("HealthCheckPinger is already running")
            return False

        if not self.url:
            logger.error("No healthcheck URL provided")
            return False

        try:
            # Send initial ping
            self.send_healthchecks_ping(self.url)

            # Start background thread
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._ping_loop, daemon=True)
            self._thread.start()
            self._running = True

            logger.info(
                f"HealthCheckPinger started with {self.ping_interval_sec}s interval"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start HealthCheckPinger: {e}")
            return False

    def stop(self) -> None:
        """Stop the periodic ping thread."""
        if not self._running:
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        self._running = False
        logger.info("HealthCheckPinger stopped")

    def _ping_loop(self) -> None:
        """Background thread that sends periodic pings."""
        while not self._stop_event.is_set():
            try:
                # Wait for the ping interval or until stop is requested
                if self._stop_event.wait(self.ping_interval_sec):
                    break

                # Send ping
                self.send_healthchecks_ping(self.url)

            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
                # Continue running even if one ping fails

    def is_running(self) -> bool:
        """Check if the pinger is currently running."""
        return self._running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

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
