"""
Tests for the holiday-aware travel date logic in utils/holidays.py
"""

import sys
import os
import unittest
from datetime import date
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.holidays import get_holidays, get_travel_dates_for_week, get_years_for_month


class TestGetTravelDatesForWeek(unittest.TestCase):
    """Test the core get_travel_dates_for_week function"""

    def test_normal_weekend_no_holidays(self):
        """Normal Friday→Sunday when no holidays"""
        friday = date(2026, 4, 3)  # A Friday
        holiday_set = set()

        pairs = get_travel_dates_for_week(friday, holiday_set)

        self.assertEqual(pairs, [(date(2026, 4, 3), date(2026, 4, 5))])

    def test_friday_is_holiday(self):
        """When Friday is a holiday, outbound should be Thursday"""
        friday = date(2026, 5, 1)  # A Friday
        holiday_set = {date(2026, 5, 1)}  # Friday is a holiday

        pairs = get_travel_dates_for_week(friday, holiday_set)

        # Should replace Friday with Thursday
        self.assertEqual(pairs, [(date(2026, 4, 30), date(2026, 5, 3))])

    def test_thursday_and_friday_both_holidays(self):
        """When Thu+Fri are holidays, outbound should walk back to Wednesday"""
        friday = date(2026, 5, 1)  # A Friday
        holiday_set = {date(2026, 4, 30), date(2026, 5, 1)}  # Thu + Fri

        pairs = get_travel_dates_for_week(friday, holiday_set)

        # Should walk back to Wednesday
        self.assertEqual(pairs, [(date(2026, 4, 29), date(2026, 5, 3))])

    def test_monday_is_holiday(self):
        """When Monday is a holiday, add Monday as additional return"""
        friday = date(2026, 4, 3)
        monday = date(2026, 4, 6)
        holiday_set = {monday}

        pairs = get_travel_dates_for_week(friday, holiday_set)

        # Normal outbound (Friday), but two returns: Sunday + Monday
        self.assertEqual(
            pairs,
            [
                (date(2026, 4, 3), date(2026, 4, 5)),
                (date(2026, 4, 3), date(2026, 4, 6)),
            ],
        )

    def test_friday_and_monday_both_holidays(self):
        """Fri is a holiday + Mon is a holiday: outbound=Thu, returns=Sun+Mon"""
        friday = date(2026, 5, 1)
        holiday_set = {date(2026, 5, 1), date(2026, 5, 4)}  # Fri + Mon

        pairs = get_travel_dates_for_week(friday, holiday_set)

        # Outbound moved to Thursday, returns on both Sunday and Monday
        self.assertEqual(
            pairs,
            [
                (date(2026, 4, 30), date(2026, 5, 3)),
                (date(2026, 4, 30), date(2026, 5, 4)),
            ],
        )

    def test_thursday_is_holiday_friday_is_not(self):
        """Thursday is a holiday but Friday isn't: add Thursday as extra outbound"""
        friday = date(2026, 4, 3)
        thursday = date(2026, 4, 2)
        holiday_set = {thursday}

        pairs = get_travel_dates_for_week(friday, holiday_set)

        # Should have both Thursday and Friday outbound with Sunday return
        self.assertEqual(
            pairs,
            [
                (date(2026, 4, 2), date(2026, 4, 5)),
                (date(2026, 4, 3), date(2026, 4, 5)),
            ],
        )

    def test_not_a_friday_raises(self):
        """Should raise ValueError if the date is not a Friday"""
        saturday = date(2026, 4, 4)
        with self.assertRaises(ValueError):
            get_travel_dates_for_week(saturday, set())

    def test_year_boundary_december(self):
        """December Friday with January Sunday should work correctly"""
        # Find a Friday in late December 2026
        friday = date(2026, 12, 25)  # Dec 25, 2026 is a Friday
        # Christmas is a SG holiday
        holiday_set = {date(2026, 12, 25)}

        pairs = get_travel_dates_for_week(friday, holiday_set)

        # Friday is Christmas (holiday) → outbound should be Thursday Dec 24
        self.assertEqual(pairs[0][0], date(2026, 12, 24))
        # Return should be Sunday Dec 27
        self.assertEqual(pairs[0][1], date(2026, 12, 27))


class TestGetYearsForMonth(unittest.TestCase):
    """Test get_years_for_month helper"""

    def test_normal_month(self):
        self.assertEqual(get_years_for_month(2026, 6), [2026])

    def test_december(self):
        self.assertEqual(get_years_for_month(2026, 12), [2026, 2027])


class TestGetHolidays(unittest.TestCase):
    """Test the get_holidays function"""

    def test_returns_sg_holidays(self):
        """Should return a non-empty set of SG holidays"""
        holiday_set = get_holidays(2026)
        self.assertIsInstance(holiday_set, set)
        self.assertTrue(len(holiday_set) > 0)

    def test_multiple_years(self):
        """Should handle multiple years"""
        holiday_set = get_holidays([2026, 2027])
        years = {d.year for d in holiday_set}
        self.assertIn(2026, years)
        self.assertIn(2027, years)

    def test_custom_overrides_add(self):
        """Should add custom holidays from file"""
        mock_json = '{"add": ["2026-06-15"], "remove": []}'
        with patch("builtins.open", mock_open(read_data=mock_json)):
            with patch("os.path.exists", return_value=True):
                holiday_set = get_holidays(2026, custom_holidays_path="fake.json")
                self.assertIn(date(2026, 6, 15), holiday_set)

    def test_custom_overrides_remove(self):
        """Should remove holidays from custom file"""
        # Get a known holiday first
        base_holidays = get_holidays(2026)
        if not base_holidays:
            self.skipTest("No SG holidays found for 2026")

        known_holiday = sorted(base_holidays)[0]
        mock_json = f'{{"add": [], "remove": ["{known_holiday.isoformat()}"]}}'
        with patch("builtins.open", mock_open(read_data=mock_json)):
            with patch("os.path.exists", return_value=True):
                holiday_set = get_holidays(
                    2026, custom_holidays_path="fake.json"
                )
                self.assertNotIn(known_holiday, holiday_set)


if __name__ == "__main__":
    unittest.main()
