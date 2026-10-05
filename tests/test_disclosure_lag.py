import unittest

from trump_tracker import disclosure_lag_days


class DisclosureLagTests(unittest.TestCase):
    def test_calendar_day_lag(self):
        self.assertEqual(disclosure_lag_days("2026-10-01", "2026-10-03"), 2)

    def test_same_day(self):
        self.assertEqual(disclosure_lag_days("2026-10-03", "2026-10-03"), 0)

    def test_invalid_or_missing_dates(self):
        self.assertIsNone(disclosure_lag_days("", "2026-10-03"))
        self.assertIsNone(disclosure_lag_days("not-a-date", "2026-10-03"))


if __name__ == "__main__":
    unittest.main()
