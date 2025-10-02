import unittest
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from notifications.healthchecks import HealthCheckPinger


class TestHealthCheckPinger(unittest.TestCase):
    """Integration tests for HealthCheckPinger class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_url = "https://hc-ping.com/test-uuid"
        self.short_interval = 1  # 1 second for faster testing

    def tearDown(self):
        """Clean up after tests"""
        pass

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_initialization(self, mock_get):
        """Test HealthCheckPinger initialization"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        pinger = HealthCheckPinger(self.test_url, self.short_interval)

        self.assertEqual(pinger.url, self.test_url)
        self.assertEqual(pinger.ping_interval, self.short_interval)
        self.assertFalse(pinger.is_running())

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_start_stop(self, mock_get):
        """Test starting and stopping the pinger"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        pinger = HealthCheckPinger(self.test_url, self.short_interval)

        # Test start
        result = pinger.start()
        self.assertTrue(result)
        self.assertTrue(pinger.is_running())

        # Wait a bit to ensure thread is running
        time.sleep(0.1)

        # Test stop
        pinger.stop()
        self.assertFalse(pinger.is_running())

        # Verify pings were sent
        self.assertGreaterEqual(mock_get.call_count, 1)

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_context_manager(self, mock_get):
        """Test using HealthCheckPinger as a context manager"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with HealthCheckPinger(self.test_url, self.short_interval) as pinger:
            self.assertTrue(pinger.is_running())
            time.sleep(0.1)  # Let it run for a bit

        # Should be stopped after context exit
        self.assertFalse(pinger.is_running())

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_failure_ping(self, mock_get):
        """Test sending failure pings"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        pinger = HealthCheckPinger(self.test_url, self.short_interval)

        # Send failure ping
        result = pinger.send_failure_ping()
        self.assertTrue(result)

        # Verify failure URL was called
        expected_failure_url = f"{self.test_url}/fail"
        mock_get.assert_called_with(expected_failure_url, timeout=10)

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_no_url(self, mock_get):
        """Test pinger behavior with no URL"""
        pinger = HealthCheckPinger("", self.short_interval)

        # Should not start without URL
        result = pinger.start()
        self.assertFalse(result)
        self.assertFalse(pinger.is_running())

        # Should not send pings without URL
        result = pinger.send_failure_ping()
        self.assertFalse(result)

        # No HTTP requests should be made
        mock_get.assert_not_called()

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_double_start(self, mock_get):
        """Test that pinger cannot be started twice"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        pinger = HealthCheckPinger(self.test_url, self.short_interval)

        # First start should succeed
        result1 = pinger.start()
        self.assertTrue(result1)

        # Second start should fail
        result2 = pinger.start()
        self.assertFalse(result2)

        pinger.stop()

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_network_error(self, mock_get):
        """Test pinger behavior when network requests fail"""
        # Mock network error
        mock_get.side_effect = Exception("Network error")

        pinger = HealthCheckPinger(self.test_url, self.short_interval)

        # Start should still succeed even if initial ping fails
        result = pinger.start()
        self.assertTrue(result)
        self.assertTrue(pinger.is_running())

        # Wait a bit for the ping loop to run
        time.sleep(0.1)

        pinger.stop()

        # Verify that requests were attempted despite errors
        self.assertGreaterEqual(mock_get.call_count, 1)

    @patch("notifications.healthchecks.requests.get")
    def test_healthcheck_pinger_multiple_pings(self, mock_get):
        """Test that multiple pings are sent over time"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        pinger = HealthCheckPinger(self.test_url, self.short_interval)

        # Start pinger
        pinger.start()

        # Wait for multiple ping intervals
        time.sleep(2.5)  # Should trigger at least 2 pings

        pinger.stop()

        # Verify multiple pings were sent
        self.assertGreaterEqual(mock_get.call_count, 2)

    def test_send_healthchecks_ping_function(self):
        """Test the standalone send_healthchecks_ping function"""
        with patch("notifications.healthchecks.requests.get") as mock_get:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # Test success ping
            result = HealthCheckPinger.send_healthchecks_ping(self.test_url, success=True)
            self.assertTrue(result)
            mock_get.assert_called_with(self.test_url, timeout=10)

            # Test failure ping
            result = HealthCheckPinger.send_healthchecks_ping(self.test_url, success=False)
            self.assertTrue(result)
            expected_failure_url = f"{self.test_url}/fail"
            mock_get.assert_called_with(expected_failure_url, timeout=10)

            # Test with empty URL
            result = HealthCheckPinger.send_healthchecks_ping("", success=True)
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
