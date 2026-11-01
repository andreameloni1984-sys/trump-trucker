import unittest
from datetime import datetime, timedelta, timezone

from sputnik_competition_setup import evaluate_competition_setup


def sample(count=80):
    start = datetime(2026, 10, 30, 8, tzinfo=timezone.utc)
    rows = []
    price = 100.0
    for index in range(count):
        next_price = price + 0.08
        rows.append({
            "timestamp": (start + timedelta(minutes=index)).isoformat(),
            "open": price,
            "high": next_price + 0.04,
            "low": price - 0.04,
            "close": next_price,
            "volume": 1000,
        })
        price = next_price
    return rows


class CompetitionSetupTests(unittest.TestCase):
    def test_requires_timestamped_history(self):
        result = evaluate_competition_setup("WTI", sample(20))
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertEqual(result["setup_status"], "INSUFFICIENT_DATA")
        self.assertIsNone(result["entry"])

    def test_no_fake_orderflow_or_forced_signal(self):
        result = evaluate_competition_setup("WTI", sample())
        self.assertEqual(result["direction"], "LONG")
        self.assertEqual(result["status"], "EARLY_SETUP")
        self.assertEqual(result["method"], "DIRECTION_LOCATION_AGGRESSION")
        self.assertEqual(result["aggression_source"], "OHLCV_VOLUME_PROXY")
        self.assertFalse(result["order_flow_confirmed"])
        self.assertIsNone(result["entry"])
        self.assertIsNone(result["stop_reference"])

    def test_missing_timestamps_are_rejected(self):
        rows = sample()
        for row in rows:
            row.pop("timestamp")
        result = evaluate_competition_setup("GOLD", rows)
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertEqual(result["direction"], "NEUTRAL")

    def test_malformed_candles_are_ignored(self):
        rows = sample()
        rows.append({
            "timestamp": "2026-10-30T10:00:00+00:00",
            "open": 2, "high": 1, "low": 3, "close": 2, "volume": 100,
        })
        result = evaluate_competition_setup("BRENT", rows)
        self.assertEqual(result["instrument"], "BRENT")
        self.assertEqual(result["direction"], "LONG")

    def test_early_context_bias_survives_missing_breakout_trigger(self):
        rows = sample()
        resistance = max(row["high"] for row in rows[-31:-1])
        rows[-1]["close"] = resistance - 0.01
        rows[-1]["high"] = rows[-1]["open"] + 0.04
        result = evaluate_competition_setup("WTI", rows)
        self.assertEqual(result["direction"], "LONG")
        self.assertEqual(result["bias"], "LONG")
        self.assertEqual(result["status"], "EARLY_SETUP")
        self.assertIn("TRIGGER_NOT_CONFIRMED", result["missing_conditions"])
        self.assertIsNone(result["entry"])
        self.assertIsNone(result["stop_reference"])

    def test_confirmed_setup_requires_trigger_volume_and_structural_stop(self):
        rows = sample()
        rows[-1]["volume"] = 1500
        result = evaluate_competition_setup("WTI", rows)
        self.assertEqual(result["status"], "SETUP_CONFIRMED")
        self.assertEqual(result["direction"], "LONG")
        self.assertEqual(result["score"], 100)
        self.assertIsNotNone(result["entry"])
        self.assertLess(result["stop_reference"], result["entry"])
        self.assertFalse(result["order_flow_confirmed"])

    def test_unaligned_context_is_neutral_not_wait(self):
        start = datetime(2026, 10, 30, 8, tzinfo=timezone.utc)
        rows = [
            {
                "timestamp": (start + timedelta(minutes=index)).isoformat(),
                "open": 100.0, "high": 100.2, "low": 99.8,
                "close": 100.0, "volume": 1000,
            }
            for index in range(80)
        ]
        result = evaluate_competition_setup("GOLD", rows)
        self.assertEqual(result["direction"], "NEUTRAL")
        self.assertEqual(result["bias"], "NEUTRAL / NO_DIRECTION")
        self.assertEqual(result["status"], "NO_DIRECTION")
        self.assertIn("LOCATION_NOT_ALIGNED_WITH_TREND", result["missing_conditions"])

    def test_unordered_timestamps_are_rejected(self):
        rows = sample()
        rows[0], rows[1] = rows[1], rows[0]
        result = evaluate_competition_setup("WTI", rows)
        self.assertEqual(result["status"], "INVALID_DATA")
        self.assertIn("CANDLE_ORDER_INVALID", result["missing_conditions"])


if __name__ == "__main__":
    unittest.main()
