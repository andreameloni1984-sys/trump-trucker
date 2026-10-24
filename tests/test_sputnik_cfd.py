import unittest
from datetime import datetime, timezone

from sputnik_cfd import build_cfd_cart


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


if __name__ == "__main__":
    unittest.main()
