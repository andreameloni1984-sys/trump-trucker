import unittest
from datetime import datetime, timezone

from sputnik_cfd import build_cfd_cart, build_conditional_trade_plan


class CfdCartTests(unittest.TestCase):
    def candidate(self, signal="COMPRA"):
        return {
            "security": "ACME",
            "company": "ACME Corp",
            "ticker": "ACME",
            "score": 80,
            "signal": signal,
        }

    def test_missing_quote_is_wait_not_invented_trade(self):
        rows = build_cfd_cart([self.candidate()], {})
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertIsNone(rows[0]["entry"])
        self.assertIn("quotazione", rows[0]["reason"])

    def test_valid_long_calculates_size_and_rr(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp}},
            capital=300,
            risk_pct=1,
        )
        self.assertEqual(rows[0]["status"], "TRADE")
        self.assertEqual(rows[0]["direction"], "LONG")
        self.assertEqual(rows[0]["risk_eur"], 3.0)
        self.assertEqual(rows[0]["units"], 0.6)
        self.assertEqual(rows[0]["rr"], 2.0)

    def test_invalid_levels_are_wait(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 100, "stop": 105, "target": 110, "timestamp": fresh_timestamp}},
        )
        self.assertEqual(rows[0]["status"], "WAIT")

    def test_watch_candidate_never_becomes_cfd(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart([self.candidate("OSSERVA")], {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp}})
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertEqual(rows[0]["direction"], "WAIT")

    def test_short_is_not_inferred_from_purchase_evidence(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart([self.candidate("COMPRA")], {"ACME": {"price": 100, "stop": 105, "target": 90, "timestamp": fresh_timestamp}})
        self.assertEqual(rows[0]["status"], "WAIT")




class ConditionalPlanDirectionTests(unittest.TestCase):
    def setUp(self):
        self.quote = {
            "price": 100,
            "atr": 2,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger_confirmed": True,
        }
        self.quotes = {"GOLD": self.quote}

    def test_missing_or_ambiguous_bias_never_creates_directional_plan(self):
        for bias in (None, "", "NEUTRAL", "WAIT", "LONG_SETUP", "NOT_SHORT"):
            with self.subTest(bias=bias):
                result = build_conditional_trade_plan(
                    {"candidate": "GOLD", "bias": bias}, self.quotes
                )
                self.assertEqual(result["status"], "WAIT")
                self.assertIsNone(result["entry"])
                self.assertIsNone(result["stop"])
                self.assertIsNone(result.get("direction"))
                self.assertIn("esplicito", result["reason"])

    def test_explicit_long_and_short_directions_are_preserved(self):
        for bias in ("LONG", "SHORT"):
            with self.subTest(bias=bias):
                result = build_conditional_trade_plan(
                    {"candidate": "GOLD", "bias": bias}, self.quotes
                )
                self.assertEqual(result["direction"], bias)
                self.assertEqual(result["status"], "TRIGGER CONFIRMED")
                if bias == "LONG":
                    self.assertLess(result["stop"], result["entry"])
                    self.assertLess(result["entry"], result["tp1"])
                else:
                    self.assertGreater(result["stop"], result["entry"])
                    self.assertGreater(result["entry"], result["tp1"])


if __name__ == "__main__":
    unittest.main()
