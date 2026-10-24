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


    def test_infinite_target_is_wait_not_trade(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 100, "stop": 95, "target": float("inf"), "timestamp": fresh_timestamp}},
        )
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertIsNone(rows[0]["target"])


class ConditionalPlanNumericValidationTests(unittest.TestCase):
    def fresh_quote(self, price=100, atr=2):
        return {
            "price": price,
            "atr": atr,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger_confirmed": True,
        }

    def test_infinite_price_cannot_confirm_conditional_plan(self):
        result = build_conditional_trade_plan(
            {"candidate": "Gold", "bias": "LONG"},
            {"GOLD": self.fresh_quote(price=float("inf"))},
        )
        self.assertEqual(result["status"], "WAIT")
        self.assertIsNone(result["entry"])

    def test_infinite_atr_cannot_confirm_conditional_plan(self):
        result = build_conditional_trade_plan(
            {"candidate": "Gold", "bias": "LONG"},
            {"GOLD": self.fresh_quote(atr=float("inf"))},
        )
        self.assertEqual(result["status"], "WAIT")
        self.assertIsNone(result["entry"])

    def test_unrepresentably_large_integer_is_rejected_without_exception(self):
        rows = build_cfd_cart(
            [{"security": "ACME", "company": "ACME Corp", "ticker": "ACME", "score": 80, "signal": "COMPRA"}],
            {"ACME": {"price": 10 ** 10000, "stop": 95, "target": 110,
                      "timestamp": datetime.now(timezone.utc).isoformat()}},
        )
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertIsNone(rows[0]["entry"])


if __name__ == "__main__":
    unittest.main()
