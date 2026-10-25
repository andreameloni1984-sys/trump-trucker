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
    def candidate(self):
        return {
            "security": "ACME",
            "company": "ACME Corp",
            "ticker": "ACME",
            "score": 80,
            "signal": "COMPRA",
        }

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

    def test_overflowing_unit_size_stays_wait_with_finite_market_values(self):
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 1e-323, "stop": 5e-324, "target": 2e-323,
                      "timestamp": datetime.now(timezone.utc).isoformat()}},
        )
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertIsNone(rows[0]["units"])
        self.assertIsNone(rows[0]["entry"])

    def test_overflowing_risk_reward_stays_wait_with_finite_market_values(self):
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 2e-308, "stop": 1e-308, "target": 1e308,
                      "timestamp": datetime.now(timezone.utc).isoformat()}},
            capital=1,
            risk_pct=1,
        )
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertIsNone(rows[0]["units"])
        self.assertIsNone(rows[0]["entry"])


class ConditionalPlanDerivedLevelTests(unittest.TestCase):
    def fresh_quote(self, price, atr):
        return {
            "price": price,
            "atr": atr,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger_confirmed": True,
        }

    def assert_wait_without_levels(self, result):
        self.assertEqual(result["status"], "WAIT")
        for key in ("entry", "stop", "tp1", "tp2"):
            self.assertIsNone(result[key], key)
        self.assertIn("Livelli SL/TP derivati non validi", result["reason"])

    def test_long_with_stop_below_zero_stays_wait(self):
        result = build_conditional_trade_plan(
            {"candidate": "Gold", "bias": "LONG"},
            {"GOLD": self.fresh_quote(price=10, atr=100)},
        )
        self.assert_wait_without_levels(result)

    def test_short_with_target_below_zero_stays_wait(self):
        result = build_conditional_trade_plan(
            {"candidate": "Gold", "bias": "SHORT"},
            {"GOLD": self.fresh_quote(price=10, atr=100)},
        )
        self.assert_wait_without_levels(result)

    def test_levels_collapsing_after_rounding_stay_wait(self):
        result = build_conditional_trade_plan(
            {"candidate": "Gold", "bias": "LONG"},
            {"GOLD": self.fresh_quote(price=100.0000001, atr=1e-8)},
        )
        self.assert_wait_without_levels(result)


if __name__ == "__main__":
    unittest.main()
