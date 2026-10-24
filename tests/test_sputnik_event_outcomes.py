import json
import tempfile
import unittest
from pathlib import Path
from sputnik_event_outcomes import create_pre_event_record, evaluate_post_event, upsert_jsonl

class EventOutcomeTests(unittest.TestCase):
    def test_pre_event_record_does_not_invent_direction(self):
        row = create_pre_event_record("cpi-1", "CPI", "2026-10-28T12:30:00Z", "NASDAQ-100", "Volatility may rise")
        self.assertEqual(row["direction"], "NOT_INFERRED")
        self.assertEqual(row["evaluation_status"], "AWAITING_POST_EVENT_PRICE")

    def test_measures_observed_reaction_from_pre_event_baseline(self):
        row = create_pre_event_record("cpi-2", "CPI", "2026-10-28T12:30:00Z", "NASDAQ-100", "", 20000, "2026-10-28T12:29:00Z")
        result = evaluate_post_event(row, 20100, "2026-10-28T12:35:00Z")
        self.assertEqual(result["reaction_pct"], 0.5)
        self.assertEqual(result["evaluation_status"], "REACTION_MEASURED_DIRECTION_NOT_PREDICTED")

    def test_rejects_post_event_price_before_release(self):
        row = create_pre_event_record("cpi-3", "CPI", "2026-10-28T12:30:00Z", "NASDAQ-100", "", 20000, "2026-10-28T12:29:00Z")
        with self.assertRaises(ValueError):
            evaluate_post_event(row, 20100, "2026-10-28T12:28:00Z")

    def test_upsert_keeps_one_record_per_event_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "outcomes.jsonl"
            first = create_pre_event_record("same", "CPI", "2026-10-28T12:30:00Z", "NASDAQ-100", "first")
            second = create_pre_event_record("same", "CPI revised", "2026-10-28T12:30:00Z", "NASDAQ-100", "second")
            upsert_jsonl(path, first)
            upsert_jsonl(path, second)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["title"], "CPI revised")

if __name__ == "__main__":
    unittest.main()
