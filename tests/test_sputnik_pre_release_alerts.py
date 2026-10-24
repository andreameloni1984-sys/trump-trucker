import unittest
from datetime import datetime, timezone
from sputnik_pre_release_alerts import parse_bls_ics, upcoming_classified_events, format_alert

SAMPLE = """BEGIN:VCALENDAR
BEGIN:VEVENT
UID:cpi-2026@example.gov
DTSTART;TZID=America/New_York:20261028T083000
SUMMARY:Consumer Price Index (CPI)
URL:https://www.bls.gov/example
END:VEVENT
BEGIN:VEVENT
UID:all-day@example.gov
DTSTART;VALUE=DATE:20261029
SUMMARY:Holiday
END:VEVENT
BEGIN:VEVENT
UID:unknown@example.gov
DTSTART:20261028T123000Z
SUMMARY:Local museum opens
END:VEVENT
END:VCALENDAR
"""

class PreReleaseAlertsTests(unittest.TestCase):
    def test_parses_timed_event_and_source_url(self):
        rows = parse_bls_ics(SAMPLE)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["uid"], "cpi-2026@example.gov")
        self.assertEqual(rows[0]["url"], "https://www.bls.gov/example")

    def test_only_classified_events_inside_window_are_selected(self):
        now = datetime(2026, 10, 28, 12, 10, tzinfo=timezone.utc)  # 08:10 ET
        rows = upcoming_classified_events(parse_bls_ics(SAMPLE), now=now)
        self.assertEqual([row["uid"] for row in rows], ["cpi-2026@example.gov"])
        self.assertEqual(rows[0]["minutes_until"], 20)
        self.assertIn("NASDAQ-100", rows[0]["instruments"])

    def test_no_alert_for_event_outside_window_or_unknown(self):
        now = datetime(2026, 10, 28, 11, 0, tzinfo=timezone.utc)
        self.assertEqual(upcoming_classified_events(parse_bls_ics(SAMPLE), now=now), [])

    def test_message_does_not_infer_direction(self):
        event = upcoming_classified_events(
            parse_bls_ics(SAMPLE),
            now=datetime(2026, 10, 28, 12, 10, tzinfo=timezone.utc),
        )[0]
        message = format_alert(event)
        self.assertIn("Direzione: NON INFERITA", message)
        self.assertIn("Fonte ufficiale", message)

if __name__ == "__main__":
    unittest.main()
