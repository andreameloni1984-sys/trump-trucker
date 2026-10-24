import unittest
from sputnik_bea_calendar import parse_bea_release_dates

SAMPLE = '{"Gross Domestic Product":{"release_dates":["2026-10-29T12:30:00+00:00","bad-date"]},"Personal Income and Outlays":{"release_dates":["2026-10-29T12:30:00+00:00"]},"file_last_updated":"2026-10-01"}'

class BeaCalendarTests(unittest.TestCase):
    def test_normalizes_release_dates(self):
        rows = parse_bea_release_dates(SAMPLE)
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0]["uid"].startswith("bea:gross domestic product:"))
        self.assertEqual(rows[0]["source"], "BEA")
        self.assertEqual(rows[0]["url"], "https://www.bea.gov/news/schedule")
        self.assertTrue(rows[0]["start"].endswith("+00:00"))

    def test_rejects_invalid_root_type(self):
        with self.assertRaises(ValueError):
            parse_bea_release_dates("[]")

if __name__ == "__main__":
    unittest.main()
