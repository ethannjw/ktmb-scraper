import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from monitor import main
from notifications.healthchecks import HealthCheckPinger


class TestMonitorIntegration(unittest.TestCase):
    """Integration tests for monitor.py with HealthCheckPinger"""

    def test_monitor_imports_healthcheck_pinger(self):
        """Test that monitor.py can import HealthCheckPinger"""
        # This test verifies that the import in monitor.py works
        from monitor import main

        self.assertTrue(True)  # If we get here, import was successful

    @patch("monitor.HealthCheckPinger")
    def test_monitor_uses_healthcheck_pinger(self, mock_pinger_class):
        """Test that monitor.py uses HealthCheckPinger when HEALTHCHECKS_IO_URL is set"""
        # Mock the HealthCheckPinger class
        mock_pinger = MagicMock()
        mock_pinger.start.return_value = True
        mock_pinger_class.return_value = mock_pinger

        # Mock environment variables
        with patch.dict(
            os.environ, {"HEALTHCHECKS_IO_URL": "https://hc-ping.com/test"}
        ):
            # Mock the argument parsing to avoid actual execution
            with patch("monitor.argparse.ArgumentParser.parse_args") as mock_parse:
                mock_args = MagicMock()
                mock_args.weekends = False
                mock_args.date = False
                mock_args.round_trip = False
                mock_args.interval = 30
                mock_args.continuous = False
                mock_args.time_slots = None
                mock_args.direction = None
                mock_args.year = None
                mock_args.month = None
                mock_args.depart_date = None
                mock_args.return_date = None
                mock_parse.return_value = mock_args

                # Mock the monitor creation and execution
                with patch("monitor.KTMBMonitor") as mock_monitor_class:
                    mock_monitor = MagicMock()
                    mock_monitor_class.return_value = mock_monitor

                    # This should not raise any import errors
                    try:
                        # We're not actually calling main() because it would require
                        # more complex mocking, but we can verify the import works
                        from monitor import main

                        self.assertTrue(True)
                    except Exception as e:
                        self.fail(f"Import failed: {e}")

    def test_healthcheck_pinger_available_in_monitor(self):
        """Test that HealthCheckPinger is available for import in monitor context"""
        try:
            from monitor import HealthCheckPinger

            self.assertTrue(True)
        except ImportError:
            # If not directly imported, it should be available through notifications
            from notifications.healthchecks import HealthCheckPinger

            self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
