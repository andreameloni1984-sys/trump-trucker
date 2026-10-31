import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sputnik_cfd import (
    attach_silv_crosscheck,
    build_cfd_cart,
    build_cfd_signal,
    fetch_silv_reference,
    fetch_yahoo_quote,
)


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


class YahooQuoteFallbackTests(unittest.TestCase):
    @staticmethod
    def payload(candle_count=15):
        now = int(datetime.now(timezone.utc).timestamp())
        timestamps = [now - (candle_count - index - 1) * 60 for index in range(candle_count)]
        closes = [100.0 + index for index in range(candle_count)]
        return {
            "chart": {
                "result": [{
                    "timestamp": timestamps,
                    "indicators": {
                        "quote": [{
                            "high": [value + 1.0 for value in closes],
                            "low": [value - 1.0 for value in closes],
                            "close": closes,
                        }]
                    },
                }]
            }
        }

    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps(self.payload).encode("utf-8")

    def test_yahoo_fallback_maps_all_supported_commodity_futures(self):
        expected = {
            "GOLD": "GC=F",
            "SILVER": "SI=F",
            "COPPER": "HG=F",
            "WTI": "CL=F",
            "BRENT": "BZ=F",
            "NATURAL_GAS": "NG=F",
            "WHEAT": "ZW=F",
            "CORN": "ZC=F",
            "SOYBEAN": "ZS=F",
        }
        for instrument, symbol in expected.items():
            with self.subTest(instrument=instrument):
                with patch(
                    "sputnik_cfd.urllib.request.urlopen",
                    return_value=self.FakeResponse(self.payload()),
                ) as urlopen:
                    quote = fetch_yahoo_quote(instrument)
                self.assertIsNotNone(quote)
                self.assertEqual(quote["symbol"], symbol)
                self.assertEqual(urlopen.call_args.kwargs["timeout"], 8)

    def test_yahoo_fallback_calculates_atr_from_fourteen_true_ranges(self):
        with patch(
            "sputnik_cfd.urllib.request.urlopen",
            return_value=self.FakeResponse(self.payload()),
        ):
            quote = fetch_yahoo_quote("WTI")
        self.assertIsNotNone(quote)
        self.assertAlmostEqual(quote["atr"], 2.0)
        self.assertAlmostEqual(quote["price"], 114.0)
        self.assertEqual(quote["provider"], "Yahoo Finance chart (1m futures)")
        self.assertTrue(quote["timestamp"].endswith("+00:00"))

    def test_yahoo_fallback_rejects_insufficient_complete_candles(self):
        with patch(
            "sputnik_cfd.urllib.request.urlopen",
            return_value=self.FakeResponse(self.payload(candle_count=14)),
        ):
            self.assertIsNone(fetch_yahoo_quote("WTI"))

    def test_yahoo_fallback_fails_closed_on_malformed_response(self):
        with patch(
            "sputnik_cfd.urllib.request.urlopen",
            return_value=self.FakeResponse({"chart": {"result": None}}),
        ):
            self.assertIsNone(fetch_yahoo_quote("WTI"))

    def test_unknown_instrument_does_not_make_network_request(self):
        with patch("sputnik_cfd.urllib.request.urlopen") as urlopen:
            self.assertIsNone(fetch_yahoo_quote("UNKNOWN"))
        urlopen.assert_not_called()

    def test_build_cfd_signal_uses_fresh_yahoo_fallback(self):
        quote = {
            "price": 80.0,
            "atr": 2.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "CL=F",
        }
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=quote) as fallback:
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "LONG", "score": 80, "reason": "US crude draw"},
                {},
            )
        fallback.assert_called_once_with("WTI")
        self.assertEqual(signal["status"], "SIGNAL")
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["entry"], 80.0)
        self.assertEqual(signal["stop"], 77.0)
        self.assertEqual(signal["tp1"], 83.0)
        self.assertEqual(signal["tp2"], 86.0)
        self.assertEqual(signal["quote_provider"], "Yahoo Finance chart (1m futures)")
        self.assertEqual(signal["quote_symbol"], "CL=F")

    def test_build_cfd_signal_rejects_stale_yahoo_fallback_without_levels(self):
        stale_timestamp = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        quote = {"price": 80.0, "atr": 2.0, "timestamp": stale_timestamp}
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=quote):
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "LONG", "score": 80},
                {},
            )
        self.assertEqual(signal["status"], "WAIT")
        self.assertIsNone(signal["entry"])
        self.assertIsNone(signal["stop"])
        self.assertIsNone(signal["tp1"])
        self.assertIsNone(signal["tp2"])

    def test_build_cfd_signal_rejects_infinite_price_without_levels(self):
        quote = {
            "price": float("inf"),
            "atr": 2.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "test",
            "symbol": "CL=F",
        }
        with patch("sputnik_cfd.fetch_yahoo_quote") as fallback:
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "LONG", "score": 80},
                {"WTI": quote},
            )
        fallback.assert_not_called()
        self.assertEqual(signal["status"], "WAIT")
        self.assertIsNone(signal["entry"])
        self.assertIsNone(signal["stop"])
        self.assertIsNone(signal["tp1"])
        self.assertIsNone(signal["tp2"])

    def test_build_cfd_signal_rejects_infinite_atr_without_levels(self):
        quote = {
            "price": 80.0,
            "atr": float("inf"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "test",
            "symbol": "CL=F",
        }
        with patch("sputnik_cfd.fetch_yahoo_quote") as fallback:
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "LONG", "score": 80},
                {"WTI": quote},
            )
        fallback.assert_not_called()
        self.assertEqual(signal["status"], "WAIT")
        self.assertIsNone(signal["entry"])
        self.assertIsNone(signal["stop"])
        self.assertIsNone(signal["tp1"])
        self.assertIsNone(signal["tp2"])

    def test_fresh_stored_quote_avoids_yahoo_network_fallback(self):
        quote = {
            "price": 75.0,
            "atr": 1.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "broker",
            "symbol": "WTI",
        }
        with patch("sputnik_cfd.fetch_yahoo_quote") as fallback:
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "SHORT", "score": 75},
                {"WTI": quote},
            )
        fallback.assert_not_called()
        self.assertEqual(signal["status"], "SIGNAL")
        self.assertEqual(signal["direction"], "SHORT")
        self.assertEqual(signal["entry"], 75.0)
        self.assertEqual(signal["stop"], 76.5)
        self.assertEqual(signal["tp1"], 73.5)
        self.assertEqual(signal["tp2"], 72.0)
        self.assertEqual(signal["quote_provider"], "broker")


class SilvCrosscheckTests(unittest.TestCase):
    @staticmethod
    def reference(**overrides):
        value = {
            "price": 49.0,
            "bid": 48.9,
            "ask": 49.1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "provider": "SILV DATA spot reference",
            "symbol": "Ag",
            "currency": "USD",
            "unit": "troy_oz",
            "market_type": "SPOT",
            "age_seconds": 10.0,
        }
        value.update(overrides)
        return value

    def test_silv_reference_preserves_currency_unit_bid_ask_and_source_time(self):
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "commodities": {
                "silver": {
                    "price": 49.0,
                    "bid": 48.9,
                    "ask": 49.1,
                    "currency": "USD",
                    "unit": "troy_oz",
                    "last_updated": now,
                    "timestamp": now,
                    "symbol": "Ag",
                }
            },
            "metadata": {"updated": now},
        }

        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, traceback):
                return False
            def read(self):
                return json.dumps(payload).encode("utf-8")

        with patch("sputnik_cfd.urllib.request.urlopen", return_value=FakeResponse()):
            reference = fetch_silv_reference("SILVER")

        self.assertIsNotNone(reference)
        self.assertEqual(reference["currency"], "USD")
        self.assertEqual(reference["unit"], "troy_oz")
        self.assertEqual(reference["market_type"], "SPOT")
        self.assertEqual(reference["bid"], 48.9)
        self.assertEqual(reference["ask"], 49.1)
        self.assertEqual(reference["timestamp"], now)
        self.assertIsNotNone(reference["age_seconds"])

    def test_matching_currency_and_unit_produce_signed_basis_not_generic_spread(self):
        quote = {
            "price": 50.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "currency": "USD",
            "unit": "troy_oz",
            "market_type": "FUTURES_CONTINUOUS",
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "SI=F",
        }
        with patch("sputnik_cfd.fetch_silv_reference", return_value=self.reference()):
            result = attach_silv_crosscheck(quote, "SILVER")

        self.assertEqual(result["crosscheck_status"], "SPOT_VS_FUTURES_BASIS_CHECK")
        self.assertEqual(result["spot_futures_basis_definition"], "spot_minus_futures")
        self.assertEqual(result["spot_futures_basis_price"], -1.0)
        self.assertEqual(result["spot_futures_basis_pct"], -2.0)
        self.assertNotIn("crosscheck_spread_pct", result)
        self.assertEqual(result["price"], 50.0)

    def test_currency_unit_and_market_type_mismatches_are_not_compared(self):
        cases = [
            ({"currency": "EUR"}, "UNCOMPARABLE_CURRENCY"),
            ({"unit": "pound"}, "UNCOMPARABLE_UNIT"),
            ({"market_type": "CFD"}, "UNCOMPARABLE_MARKET_TYPE"),
            ({"unit": None}, "UNCOMPARABLE_METADATA_MISSING"),
        ]
        for overrides, expected_status in cases:
            with self.subTest(overrides=overrides):
                quote = {
                    "price": 50.0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "currency": "USD",
                    "unit": "troy_oz",
                    "market_type": "FUTURES_CONTINUOUS",
                    "provider": "broker",
                    "symbol": "SI=F",
                }
                reference = self.reference(**overrides)
                with patch("sputnik_cfd.fetch_silv_reference", return_value=reference):
                    result = attach_silv_crosscheck(quote, "SILVER")
                self.assertEqual(result["crosscheck_status"], expected_status)
                self.assertIsNone(result["spot_futures_basis_price"])
                self.assertIsNone(result["spot_futures_basis_pct"])

    def test_cfd_signal_keeps_futures_execution_price_and_exposes_basis_metadata(self):
        timestamp = datetime.now(timezone.utc).isoformat()
        quote = {
            "price": 50.0,
            "atr": 1.0,
            "timestamp": timestamp,
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "SI=F",
            "currency": "USD",
            "unit": "troy_oz",
            "market_type": "FUTURES_CONTINUOUS",
            "bid": None,
            "ask": None,
        }
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=quote):
            with patch("sputnik_cfd.fetch_silv_reference", return_value=self.reference()):
                signal = build_cfd_signal(
                    {"instrument": "SILVER", "bias": "LONG", "score": 80, "reason": "test"},
                    {},
                )

        self.assertEqual(signal["entry"], 50.0)
        self.assertEqual(signal["quote_provider"], "Yahoo Finance chart (1m futures)")
        self.assertEqual(signal["quote_symbol"], "SI=F")
        self.assertEqual(signal["quote_currency"], "USD")
        self.assertEqual(signal["quote_unit"], "troy_oz")
        self.assertEqual(signal["quote_market_type"], "FUTURES_CONTINUOUS")
        self.assertEqual(signal["crosscheck_status"], "SPOT_VS_FUTURES_BASIS_CHECK")
        self.assertEqual(signal["spot_futures_basis_price"], -1.0)
        self.assertEqual(signal["crosscheck_currency"], "USD")
        self.assertEqual(signal["crosscheck_unit"], "troy_oz")
        self.assertEqual(signal["crosscheck_bid"], 48.9)
        self.assertEqual(signal["crosscheck_ask"], 49.1)




if __name__ == "__main__":
    unittest.main()
