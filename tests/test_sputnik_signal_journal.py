import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import sputnik_signal_journal
import telegram_listener


class SputnikSignalJournalTests(unittest.TestCase):
    def state(self, quotes=None):
        detected = datetime.now(timezone.utc).isoformat()
        return {
            "intelligence_history": {
                "evt-oil-1": {
                    "event_id": "evt-oil-1",
                    "source": "WHITE_HOUSE",
                    "url": "https://www.whitehouse.gov/example",
                    "domains": ["ENERGY"],
                    "text": "Iran threatens shipping near Hormuz and oil exports.",
                    "detected_at": detected,
                }
            },
            "market_quotes": quotes or {},
        }

    def test_action_reaction_records_levels_and_source_quote_timestamps(self):
        quote_time = datetime.now(timezone.utc).isoformat()
        quotes = {
            "BRENT": {
                "price": 100.0,
                "atr": 2.0,
                "timestamp": quote_time,
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data" / "sputnik_signal_journal.jsonl"
            with patch.object(sputnik_signal_journal, "JOURNAL_PATH", path):
                message = telegram_listener.action_reaction_result(self.state(quotes))

            self.assertIn("SPUTNIK — OPPORTUNITÀ DI MERCATO", message)
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["record_type"], "SPUTNIK_ANALYSIS")
            self.assertEqual(row["event_id"], "evt-oil-1")
            self.assertEqual(row["instrument"], "BRENT (petrolio)")
            self.assertEqual(row["direction"], "LONG")
            self.assertEqual(row["entry"], 100.0)
            self.assertEqual(row["stop_loss"], 97.0)
            self.assertEqual(row["take_profit_1"], 103.0)
            self.assertEqual(row["take_profit_2"], 106.0)
            self.assertEqual(row["quote_timestamp"], quote_time)
            self.assertEqual(row["outcome_status"], "NOT_YET_SCORED")
            self.assertIsNone(row["outcome"])

    def test_missing_fresh_quote_is_logged_without_invented_levels(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sputnik_signal_journal.jsonl"
            with patch.object(sputnik_signal_journal, "JOURNAL_PATH", path):
                telegram_listener.action_reaction_result(self.state())

            row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(row["direction"], "LONG")
            self.assertEqual(row["decision_status"], "WAIT")
            self.assertEqual(row["outcome_status"], "NOT_SCORABLE_NO_FRESH_QUOTE")
            self.assertIsNone(row["entry"])
            self.assertIsNone(row["stop_loss"])
            self.assertIsNone(row["take_profit_1"])
            self.assertIsNone(row["quote_timestamp"])

    def test_non_specific_text_is_recorded_as_wait_not_as_a_trade(self):
        record = sputnik_signal_journal.build_signal_record(
            "Hello world, no market catalyst here.",
            "Test source",
            {},
        )
        self.assertEqual(record["direction"], "WAIT")
        self.assertEqual(record["decision_status"], "WAIT")
        self.assertIsNone(record["instrument"])
        self.assertEqual(record["outcome_status"], "NOT_SCORABLE_NO_SPECIFIC_CATALYST")


if __name__ == "__main__":
    unittest.main()
