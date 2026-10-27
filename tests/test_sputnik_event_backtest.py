import unittest
from datetime import datetime, timedelta, timezone

from sputnik_event_backtest import backtest_event


def candles(rows, start=None):
    start = start or datetime(2026, 1, 1, tzinfo=timezone.utc)
    output = []
    for i, (open_, high, low, close, volume) in enumerate(rows):
        output.append({
            "timestamp": start + timedelta(minutes=5 * i),
            "open": float(open_), "high": float(high), "low": float(low),
            "close": float(close), "volume": float(volume),
        })
    return output


class SputnikEventBacktestTests(unittest.TestCase):
    def test_exploratory_short_can_enter_before_breakout(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 100.5, 98.8, 99, 1200),
            (99, 99.2, 97.5, 98, 1500),
            (97.4, 98.2, 96.0, 97, 1800),
            (97, 97.2, 95.0, 96, 1900),
        ])
        result = backtest_event(data, "2026-01-01T00:02:00+00:00", "SHORT", 1.0, breakout_lookback=2)
        self.assertEqual(result["early"]["entry"], 100.0)
        self.assertEqual(result["early"]["status"], "TARGET")
        self.assertNotEqual(result["breakout"]["status"], "NO_BREAKOUT")
        # Close-confirmed breakouts can only be filled on the following bar.
        self.assertEqual(result["breakout"]["entry"], 97.4)
        self.assertEqual(result["breakout"]["signal_time"], data[2]["timestamp"].isoformat())
        self.assertEqual(result["breakout"]["entry_time"], data[3]["timestamp"].isoformat())
        self.assertEqual(result["breakout"]["entry_model"], "next_bar_open_after_close_confirmation")
        self.assertGreater(result["early"]["pnl_r"], 0)

    def test_stop_wins_when_stop_and_target_hit_in_same_candle(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 103, 97, 100, 1000),
            (100, 100, 100, 100, 1000),
        ])
        result = backtest_event(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0, target_r=2.0)
        self.assertEqual(result["early"]["status"], "STOP_AMBIGUOUS_STOP_FIRST")
        self.assertEqual(result["early"]["pnl_r"], -1.0)

    def test_entry_bar_is_checked_for_stop_and_target(self):
        data = candles([
            (100, 103, 97, 100, 1000),
            (100, 100, 100, 100, 1000),
        ])
        result = backtest_event(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0, target_r=2.0)
        self.assertEqual(result["early"]["status"], "STOP_AMBIGUOUS_STOP_FIRST")
        self.assertEqual(result["early"]["bars_held"], 1)

    def test_no_future_candle_does_not_invent_entry(self):
        data = candles([(100, 101, 99, 100, 1000)])
        result = backtest_event(data, "2026-01-02T00:00:00+00:00", "LONG", 1.0)
        self.assertEqual(result["early"]["status"], "NO_POST_EVENT_CANDLE")

    def test_invalid_direction_rejected(self):
        with self.assertRaises(ValueError):
            backtest_event(candles([(100, 101, 99, 100, 1000)]), "2026-01-01T00:00:00+00:00", "MAYBE", 1.0)

    def test_both_results_are_reported_even_when_breakout_absent(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (100, 100.4, 99.4, 100, 1000),
            (100, 100.3, 99.5, 100, 1000),
            (100, 100.2, 99.6, 100, 1000),
        ])
        result = backtest_event(data, "2025-12-31T23:59:00+00:00", "SHORT", 1.0, breakout_lookback=2)
        self.assertIn("status", result["early"])
        self.assertEqual(result["breakout"]["status"], "NO_BREAKOUT")

    def test_duplicate_candle_timestamps_are_rejected(self):
        data = candles([
            (100, 101, 99, 100, 1000),
            (99, 100, 98, 99, 1200),
        ])
        data[1]["timestamp"] = data[0]["timestamp"]
        with self.assertRaisesRegex(ValueError, "timestamps must be unique"):
            backtest_event(data, "2025-12-31T23:59:00+00:00", "SHORT", 1.0)

    def test_naive_candle_timestamps_are_rejected(self):
        data = candles(
            [(100, 101, 99, 100, 1000)],
            start=datetime(2026, 1, 1),
        )
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            backtest_event(data, "2025-12-31T23:59:00+00:00", "LONG", 1.0)

    def test_gap_through_short_stop_fills_at_worse_open(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 100.5, 99.5, 100, 1000),
            (102.5, 103, 102, 102.8, 1400),
        ])
        result = backtest_event(data, "2026-01-01T00:00:00+00:00", "SHORT", 1.0)
        self.assertEqual(result["early"]["status"], "STOP_GAP")
        self.assertEqual(result["early"]["stop"], 101.0)
        self.assertEqual(result["early"]["exit"], 102.5)
        self.assertEqual(result["early"]["pnl_r"], -2.5)

    def test_gap_through_long_target_does_not_assume_better_fill(self):
        data = candles([
            (100, 100.5, 99.5, 100, 1000),
            (100, 100.5, 99.5, 100, 1000),
            (103, 104, 102.5, 103.5, 1400),
        ])
        result = backtest_event(data, "2026-01-01T00:00:00+00:00", "LONG", 1.0, target_r=2.0)
        self.assertEqual(result["early"]["status"], "TARGET_GAP")
        self.assertEqual(result["early"]["target"], 102.0)
        self.assertEqual(result["early"]["exit"], 102.0)
        self.assertEqual(result["early"]["pnl_r"], 2.0)


if __name__ == "__main__":
    unittest.main()
