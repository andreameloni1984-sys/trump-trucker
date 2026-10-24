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
            {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp, "trigger_confirmed": True, "price_confirmed": True, "volume_confirmed": True}},
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
            {"ACME": {"price": 100, "stop": 105, "target": 110, "timestamp": fresh_timestamp, "trigger_confirmed": True, "price_confirmed": True, "volume_confirmed": True}},
        )
        self.assertEqual(rows[0]["status"], "WAIT")

    def test_fresh_quote_without_price_volume_confirmation_stays_wait(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp}},
        )
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertIsNone(rows[0]["units"])
        self.assertIn("prezzo e volume", rows[0]["reason"])

    def test_each_confirmation_flag_is_required_for_cfd_cart(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        base = {
            "price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp,
            "trigger_confirmed": True, "price_confirmed": True, "volume_confirmed": True,
        }
        for missing_flag in ("trigger_confirmed", "price_confirmed", "volume_confirmed"):
            with self.subTest(missing_flag=missing_flag):
                quote = dict(base)
                quote.pop(missing_flag)
                rows = build_cfd_cart([self.candidate()], {"ACME": quote})
                self.assertEqual(rows[0]["status"], "WAIT")

    def test_watch_candidate_never_becomes_cfd(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart([self.candidate("OSSERVA")], {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp}})
        self.assertEqual(rows[0]["status"], "WAIT")
        self.assertEqual(rows[0]["direction"], "WAIT")

    def test_short_is_not_inferred_from_purchase_evidence(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart([self.candidate("COMPRA")], {"ACME": {"price": 100, "stop": 105, "target": 90, "timestamp": fresh_timestamp, "trigger_confirmed": True, "price_confirmed": True, "volume_confirmed": True}})
        self.assertEqual(rows[0]["status"], "WAIT")


    def test_non_finite_quote_values_cannot_create_cfd_trade(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        for field in ("price", "stop", "target"):
            with self.subTest(field=field):
                quote = {
                    "price": 100, "stop": 95, "target": 110,
                    "timestamp": fresh_timestamp,
                    "trigger_confirmed": True, "price_confirmed": True,
                    "volume_confirmed": True,
                }
                quote[field] = float("inf")
                rows = build_cfd_cart([self.candidate()], {"ACME": quote})
                self.assertEqual(rows[0]["status"], "WAIT")
                self.assertIsNone(rows[0]["units"])

    def test_non_finite_price_or_atr_cannot_create_conditional_levels(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        for field in ("price", "atr"):
            with self.subTest(field=field):
                quote = {
                    "price": 100, "atr": 2, "timestamp": fresh_timestamp,
                    "trigger_confirmed": True, "price_confirmed": True,
                    "volume_confirmed": True,
                }
                quote[field] = float("inf")
                result = build_conditional_trade_plan(
                    {"candidate": "GOLD", "bias": "LONG"}, {"GOLD": quote}
                )
                self.assertEqual(result["status"], "WAIT")
                self.assertIsNone(result["entry"])
                self.assertIsNone(result["stop"])


    def test_invalid_or_ambiguous_bias_never_creates_directional_levels(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        quote = {
            "price": 100, "atr": 2, "timestamp": fresh_timestamp,
            "trigger_confirmed": True, "price_confirmed": True,
            "volume_confirmed": True,
        }
        for bias in (None, "", "NEUTRAL", "WAIT", "LONG_SETUP", "NOT_SHORT"):
            with self.subTest(bias=bias):
                result = build_conditional_trade_plan(
                    {"candidate": "GOLD", "bias": bias}, {"GOLD": quote}
                )
                self.assertEqual(result["status"], "WAIT")
                self.assertIsNone(result["entry"])
                self.assertIsNone(result["stop"])
                self.assertIsNone(result["tp1"])
                self.assertIsNone(result["tp2"])
                self.assertIn("LONG oppure SHORT", result["reason"])


    def test_invalid_or_collapsed_derived_levels_stay_wait(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        cases = (
            ("LONG", 1, 2),       # stop would be non-positive
            ("SHORT", 1, 1),      # target levels would be non-positive
            ("LONG", 100, 1e-10), # levels collapse after six-decimal rounding
        )
        for bias, price, atr in cases:
            with self.subTest(bias=bias, price=price, atr=atr):
                quote = {
                    "price": price, "atr": atr, "timestamp": fresh_timestamp,
                    "trigger_confirmed": True, "price_confirmed": True,
                    "volume_confirmed": True,
                }
                result = build_conditional_trade_plan(
                    {"candidate": "GOLD", "bias": bias}, {"GOLD": quote}
                )
                self.assertEqual(result["status"], "WAIT")
                self.assertIsNone(result["entry"])
                self.assertIsNone(result["stop"])
                self.assertIsNone(result["tp1"])
                self.assertIsNone(result["tp2"])


if __name__ == "__main__":
    unittest.main()
