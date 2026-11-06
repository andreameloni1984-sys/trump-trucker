import unittest
from datetime import datetime, timezone

from sputnik_macro_calendar import (
    due_calendar_alerts,
    format_calendar_alert,
    parse_bls_ical,
)


class SputnikMacroCalendarTests(unittest.TestCase):
    def test_parses_bls_timezone_and_floating_eastern_times(self):
        raw = b"""BEGIN:VCALENDAR\r
BEGIN:VEVENT\r
UID:nfp-2026-11\r
DTSTART;TZID=America/New_York:20261106T083000\r
SUMMARY:Employment Situation for October 2026\r
URL:https://www.bls.gov/news.release/empsit.nr0.htm\r
END:VEVENT\r
BEGIN:VEVENT\r
UID:cpi-2026-11\r
DTSTART:20261110T083000\r
SUMMARY:Consumer Price Index for October 2026\r
END:VEVENT\r
END:VCALENDAR\r
"""
        events = parse_bls_ical(raw)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_id"], "nfp-2026-11")
        self.assertEqual(events[0]["start_utc"], "2026-11-06T13:30:00+00:00")
        self.assertEqual(events[1]["start_utc"], "2026-11-10T13:30:00+00:00")

    def test_ignores_all_day_events_without_release_time(self):
        raw = b"""BEGIN:VCALENDAR
BEGIN:VEVENT
UID:holiday
DTSTART;VALUE=DATE:20261111
SUMMARY:Veterans Day
END:VEVENT
END:VCALENDAR
"""
        self.assertEqual(parse_bls_ical(raw), [])

    def test_emits_24h_1h_15m_and_release_window_once(self):
        event = {
            "event_id": "nfp",
            "summary": "Employment Situation",
            "start_utc": "2026-11-06T13:30:00+00:00",
            "source": "BLS_OFFICIAL_ICAL",
        }
        cases = [
            ("2026-11-05T14:00:00+00:00", "24_HOURS"),
            ("2026-11-06T12:45:00+00:00", "1_HOUR"),
            ("2026-11-06T13:20:00+00:00", "15_MIN"),
            ("2026-11-06T13:32:00+00:00", "RELEASE_WINDOW"),
        ]
        for now_text, expected in cases:
            now = datetime.fromisoformat(now_text)
            due = due_calendar_alerts([event], {}, now)
            self.assertEqual(due[0]["stage"], expected)
            sent = {"nfp": [expected]}
            self.assertEqual(due_calendar_alerts([event], sent, now), [])

    def test_rejects_naive_current_time(self):
        with self.assertRaises(ValueError):
            due_calendar_alerts([], {}, datetime(2026, 11, 6, 13, 0))

    def test_message_identifies_itself_as_calendar_not_trade_signal(self):
        event = {
            "event_id": "nfp",
            "summary": "Employment Situation",
            "start_utc": "2026-11-06T13:30:00+00:00",
            "stage": "15_MIN",
            "minutes_to_release": 15,
            "source_url": "https://www.bls.gov/schedule/2026/",
        }
        message = format_calendar_alert(event)
        self.assertIn("CALENDARIO MACRO UFFICIALE", message)
        self.assertIn("non è un segnale LONG/SHORT", message)


if __name__ == "__main__":
    unittest.main()
