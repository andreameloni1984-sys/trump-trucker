import unittest
from sputnik_release_calendar import classify_scheduled_release, release_time_in_rome, prepare_release_watch

class ReleaseCalendarTests(unittest.TestCase):
    def test_cpi_is_high_impact_and_maps_instruments(self):
        row = classify_scheduled_release("Consumer Price Index")
        self.assertEqual(row["impact"], "HIGH")
        self.assertIn("NASDAQ-100", row["instruments"])

    def test_eia_inventory_maps_only_wti(self):
        row = classify_scheduled_release("EIA crude oil inventories")
        self.assertEqual(row["instruments"], ["WTI"])

    def test_unknown_event_is_not_forced(self):
        row = classify_scheduled_release("Local museum opens")
        self.assertFalse(row["matched"])
        self.assertEqual(row["instruments"], [])

    def test_timezone_conversion_respects_offsets(self):
        # 13:30 UTC is 15:30 in Rome during summer time.
        self.assertEqual(release_time_in_rome("2026-07-15T13:30:00Z"), "2026-07-15T15:30+02:00")

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            release_time_in_rome("2026-07-15T13:30:00")

    def test_watch_prepares_but_does_not_infer_direction(self):
        row = prepare_release_watch("FOMC interest rate decision", "2026-10-28T14:00:00-04:00")
        self.assertEqual(row["status"], "PREPARE_BEFORE_RELEASE")
        self.assertEqual(row["direction"], "NOT_INFERRED")

if __name__ == "__main__":
    unittest.main()
