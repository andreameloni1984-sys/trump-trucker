import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import sputnik_wti_alert as wti


def make_bars(closes, ranges=None):
    bars = []
    ranges = ranges or [0.3] * len(closes)
    for i, close in enumerate(closes):
        op = close + 0.05 if i == len(closes) - 1 else close - 0.02
        bars.append({
            "timestamp": f"2026-10-28T15:{i:02d}:00+00:00",
            "epoch": 1793200000 + i * 300,
            "open": op,
            "high": max(op, close) + ranges[i] / 2,
            "low": min(op, close) - ranges[i] / 2,
            "close": close,
        })
    return bars


class WTIAlertTests(unittest.TestCase):
    def test_never_uses_continuous_future_symbol(self):
        with patch.dict("os.environ", {"SPUTNIK_WTI_CONTRACT": "CL=F"}):
            self.assertIsNone(wti.fetch_intraday())

    def test_pre_alert_from_lower_highs_is_early_and_explicit(self):
        bars = make_bars([80, 80.2, 80.4, 80.5, 80.6, 80.7, 80.65, 80.55, 80.45])
        result = wti.classify_state(bars)
        self.assertEqual(result["state"], "PRE-ALLARME DI POSSIBILE INVERSIONE")
        self.assertIn("massimi", result["evidence"])

    def test_confirmed_inversion_requires_consecutive_closes_below_support(self):
        bars = make_bars([80, 80.2, 80.4, 80.5, 80.6, 80.7, 80.3, 80.1, 79.8, 79.6])
        result = wti.classify_state(bars)
        self.assertEqual(result["state"], "INVERSIONE CONFERMATA")

    def test_same_state_does_not_send_duplicate(self):
        quote = {
            "symbol": "CLZ26.NYM", "expiry": "2026-11-20", "price": 80.1,
            "timestamp": "2026-10-28T17:00:00+00:00", "delay_seconds": 0,
            "exchange": "NYM", "source": "test", "bars": make_bars([80,80.2,80.4,80.5,80.6,80.7,80.8,80.9]),
        }
        state = {"wti_state_change_alert": {"state": "LONG IN TENUTA"}}
        sender = MagicMock(return_value=True)
        result = wti.check_and_send(state, sender, quote=quote)
        self.assertEqual(result, "UNCHANGED")
        sender.assert_not_called()

    def test_failed_send_does_not_advance_state(self):
        quote = {
            "symbol": "CLZ26.NYM", "expiry": "2026-11-20", "price": 80.1,
            "timestamp": "2026-10-28T17:00:00+00:00", "delay_seconds": 0,
            "exchange": "NYM", "source": "test", "bars": make_bars([80,80.2,80.4,80.5,80.6,80.7,80.8,80.9]),
        }
        state = {}
        result = wti.check_and_send(state, lambda _: False, quote=quote)
        self.assertEqual(result, "SEND_FAILED")
        self.assertNotIn("wti_state_change_alert", state)


if __name__ == "__main__":
    unittest.main()
