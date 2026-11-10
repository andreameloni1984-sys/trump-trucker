import json
import unittest
from datetime import datetime, timedelta, timezone
from types import ModuleType
from unittest.mock import patch

from sputnik_cfd import (
    attach_silv_crosscheck,
    build_cfd_cart,
    cfd_cart_display_state,
    build_cfd_signal,
    fetch_silv_reference,
    fetch_yahoo_quote,
    format_cfd_signal,
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

    def test_missing_quote_preserves_long_bias_without_levels(self):
        rows = build_cfd_cart([self.candidate()], {})
        self.assertEqual(rows[0]["status"], "EARLY_BIAS")
        self.assertEqual(rows[0]["direction"], "LONG")
        self.assertEqual(rows[0]["paper_trade_status"], "NOT_EXECUTED")
        self.assertIsNone(rows[0]["entry"])
        self.assertIn("quotazione", rows[0]["reason"])

    def test_valid_long_levels_remain_a_setup_not_an_executed_trade(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp}},
            capital=300,
            risk_pct=1,
        )
        self.assertEqual(rows[0]["status"], "EARLY_SETUP")
        self.assertEqual(rows[0]["paper_trade_status"], "NOT_EXECUTED")
        self.assertEqual(rows[0]["direction"], "LONG")
        self.assertEqual(rows[0]["risk_eur"], 3.0)
        self.assertEqual(rows[0]["units"], 0.6)
        self.assertEqual(rows[0]["rr"], 2.0)

    def test_invalid_levels_keep_long_bias_without_sizing(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart(
            [self.candidate()],
            {"ACME": {"price": 100, "stop": 105, "target": 110, "timestamp": fresh_timestamp}},
        )
        self.assertEqual(rows[0]["status"], "EARLY_BIAS")
        self.assertEqual(rows[0]["direction"], "LONG")
        self.assertIsNone(rows[0]["entry"])
        self.assertIsNone(rows[0]["units"])

    def test_watch_candidate_has_explicit_no_direction(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart([self.candidate("OSSERVA")], {"ACME": {"price": 100, "stop": 95, "target": 110, "timestamp": fresh_timestamp}})
        self.assertEqual(rows[0]["status"], "NO_DIRECTION")
        self.assertEqual(rows[0]["direction"], "NEUTRAL")
        self.assertEqual(rows[0]["paper_trade_status"], "NOT_EXECUTED")

    def test_short_is_not_inferred_from_purchase_evidence(self):
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        rows = build_cfd_cart([self.candidate("COMPRA")], {"ACME": {"price": 100, "stop": 105, "target": 90, "timestamp": fresh_timestamp}})
        self.assertEqual(rows[0]["status"], "EARLY_BIAS")
        self.assertEqual(rows[0]["direction"], "LONG")
        self.assertIsNone(rows[0]["target"])


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
            "GOLD": ("GC=F", "troy_oz"),
            "SILVER": ("SI=F", "troy_oz"),
            "COPPER": ("HG=F", "pound"),
            "WTI": ("CL=F", "barrel"),
            "BRENT": ("BZ=F", "barrel"),
            "NATURAL_GAS": ("NG=F", "MMBtu"),
            "WHEAT": ("ZW=F", "bushel"),
            "CORN": ("ZC=F", "bushel"),
            "SOYBEAN": ("ZS=F", "bushel"),
        }
        for instrument, (symbol, unit) in expected.items():
            with self.subTest(instrument=instrument):
                with patch(
                    "sputnik_cfd.urllib.request.urlopen",
                    return_value=self.FakeResponse(self.payload()),
                ) as urlopen:
                    quote = fetch_yahoo_quote(instrument)
                self.assertIsNotNone(quote)
                self.assertEqual(quote["symbol"], symbol)
                self.assertEqual(quote["currency"], "USD")
                self.assertEqual(quote["unit"], unit)
                self.assertEqual(quote["market_type"], "FUTURES_CONTINUOUS")
                self.assertIn("exact expiry not exposed", quote["contract_description"])
                self.assertIsNone(quote["bid"])
                self.assertIsNone(quote["ask"])
                self.assertIsNotNone(quote["age_seconds"])
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
        self.assertEqual(signal["status"], "EARLY_SETUP")
        self.assertEqual(signal["setup_status"], "EARLY_SETUP")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["entry"], 80.0)
        self.assertEqual(signal["stop"], 77.0)
        self.assertEqual(signal["tp1"], 83.0)
        self.assertEqual(signal["tp2"], 86.0)
        self.assertEqual(signal["quote_provider"], "Yahoo Finance chart (1m futures)")
        self.assertEqual(signal["quote_symbol"], "CL=F")

    def test_build_cfd_signal_preserves_analyst_5m_direction_in_cfd_card(self):
        quote = {
            "price": 80.0,
            "atr": 2.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "CL=F",
        }
        recommendation = {
            "instrument": "WTI",
            "bias": "LONG",
            "score": 100,
            "reason": "Nessun catalizzatore direzionale verificato.",
            "technical_bias": "LONG",
            "technical_timeframe": "5m",
            "technical_reason": "EMA50 sopra EMA200; momentum positivo.",
            "catalyst_alignment": "NO_DIRECTIONAL_NEWS",
        }
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=quote), patch(
            "sputnik_cfd.attach_silv_crosscheck", side_effect=lambda value, instrument: value
        ):
            signal = build_cfd_signal(recommendation, {})
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["technical_direction"], "LONG")
        self.assertEqual(signal["technical_timeframe"], "5m")
        self.assertEqual(signal["technical_reason"], "EMA50 sopra EMA200; momentum positivo.")
        self.assertEqual(signal["technical_alignment"], "ALIGNS")
        self.assertEqual(signal["catalyst_alignment"], "NO_DIRECTIONAL_NEWS")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
        self.assertIn("TECNICA: LONG (5m | ALIGNS)", format_cfd_signal(signal))

    def test_build_cfd_signal_rejects_stale_yahoo_fallback_without_levels(self):
        stale_timestamp = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        quote = {"price": 80.0, "atr": 2.0, "timestamp": stale_timestamp}
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=quote):
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "LONG", "score": 80},
                {},
            )
        self.assertEqual(signal["status"], "EARLY_BIAS")
        self.assertEqual(signal["setup_status"], "EARLY_BIAS")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
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
        self.assertEqual(signal["status"], "EARLY_BIAS")
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["setup_status"], "EARLY_BIAS")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
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
        self.assertEqual(signal["status"], "EARLY_BIAS")
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["setup_status"], "EARLY_BIAS")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
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
        self.assertEqual(signal["status"], "EARLY_SETUP")
        self.assertEqual(signal["setup_status"], "EARLY_SETUP")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
        self.assertEqual(signal["direction"], "SHORT")
        self.assertEqual(signal["entry"], 75.0)
        self.assertEqual(signal["stop"], 76.5)
        self.assertEqual(signal["tp1"], 73.5)
        self.assertEqual(signal["tp2"], 72.0)
        self.assertEqual(signal["quote_provider"], "broker")


class DirectionStateAndTelegramTests(unittest.TestCase):
    def test_missing_recommendation_is_neutral_not_wait(self):
        signal = build_cfd_signal(None, {})
        self.assertEqual(signal["direction"], "NEUTRAL")
        self.assertEqual(signal["status"], "NO_DIRECTION")
        self.assertEqual(signal["bias_status"], "NO_DIRECTION")
        self.assertEqual(signal["setup_status"], "NO_DIRECTION")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
        self.assertIsNone(signal["entry"])

    def test_directional_bias_without_fresh_quote_is_preserved_in_telegram(self):
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=None):
            signal = build_cfd_signal(
                {"instrument": "WTI", "bias": "LONG", "score": 80, "reason": "US crude draw"},
                {},
            )
        message = format_cfd_signal(signal)
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["status"], "EARLY_BIAS")
        self.assertIsNone(signal["entry"])
        self.assertIn("BIAS: LONG", message)
        self.assertIn("SETUP: EARLY_BIAS", message)
        self.assertIn("TRADE PAPER: NOT_EXECUTED", message)
        self.assertIn("livelli omessi", message.lower())
        self.assertNotIn("WAIT", message)

    def test_no_direction_telegram_does_not_report_wait_or_missing_quote(self):
        message = format_cfd_signal(build_cfd_signal(None, {}))
        self.assertIn("BIAS: NEUTRAL", message)
        self.assertIn("SETUP: NO_DIRECTION", message)
        self.assertIn("TRADE PAPER: NOT_EXECUTED", message)
        self.assertIn("NO_DIRECTION", message)
        self.assertNotIn("WAIT", message)


    def test_opposite_confirmed_dla_does_not_flip_news_bias(self):
        now = datetime.now(timezone.utc).isoformat()
        quote = {
            "price": 80.0,
            "atr": 2.0,
            "timestamp": now,
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "CL=F",
            "candles": [{"timestamp": now} for _ in range(60)],
        }
        focused_module = ModuleType("sputnik_focused_trader")
        focused_module.analyze_focused_market = lambda instrument, candles: {
            "status": "DIRECTIONAL", "direction": "SHORT", "reason": "short-term trend down"
        }
        setup_module = ModuleType("sputnik_competition_setup")
        setup_module.evaluate_competition_setup = lambda instrument, candles: {
            "status": "SETUP_CONFIRMED", "direction": "SHORT",
            "confirmations": ["trend", "location", "retest", "volume proxy"], "reasons": []
        }
        with patch.dict("sys.modules", {
            "sputnik_focused_trader": focused_module,
            "sputnik_competition_setup": setup_module,
        }):
            with patch("sputnik_cfd.attach_silv_crosscheck", side_effect=lambda q, instrument: q):
                signal = build_cfd_signal(
                    {"instrument": "WTI", "bias": "LONG", "score": 85, "reason": "supply disruption catalyst"},
                    {"WTI": quote},
                )
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["technical_direction"], "SHORT")
        self.assertEqual(signal["technical_alignment"], "CONTRASTS")
        self.assertEqual(signal["setup_direction"], "SHORT")
        self.assertEqual(signal["setup_alignment"], "CONTRASTS")
        self.assertEqual(signal["status"], "EARLY_SETUP")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
        self.assertTrue(signal["market_direction_conflict"])
        self.assertIn("MERCATO CONTRO BIAS", signal["market_direction_warning"])


    def test_early_dla_direction_is_visible_and_does_not_override_news_bias(self):
        now = datetime.now(timezone.utc).isoformat()
        quote = {
            "price": 80.0, "atr": 2.0, "timestamp": now,
            "provider": "Yahoo Finance chart (1m futures)", "symbol": "CL=F",
            "candles": [{"timestamp": now} for _ in range(60)],
        }
        focused_module = ModuleType("sputnik_focused_trader")
        focused_module.analyze_focused_market = lambda instrument, candles: {
            "status": "WAIT_CONFIRMATION", "direction": "NEUTRAL",
            "reason": "trigger non confermato",
        }
        setup_module = ModuleType("sputnik_competition_setup")
        setup_module.evaluate_competition_setup = lambda instrument, candles: {
            "status": "EARLY_SETUP", "direction": "SHORT",
            "confirmations": ["Direction SHORT", "Location SHORT"],
            "missing_conditions": ["TRIGGER_NOT_CONFIRMED"],
            "reasons": ["bias SHORT, trigger mancante"],
        }
        with patch.dict("sys.modules", {
            "sputnik_focused_trader": focused_module,
            "sputnik_competition_setup": setup_module,
        }):
            with patch("sputnik_cfd.attach_silv_crosscheck", side_effect=lambda q, instrument: q):
                signal = build_cfd_signal(
                    {"instrument": "WTI", "bias": "LONG", "score": 85, "reason": "supply disruption"},
                    {"WTI": quote},
                )
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["setup_direction"], "SHORT")
        self.assertEqual(signal["setup_alignment"], "CONTRASTS")
        self.assertEqual(signal["status"], "EARLY_SETUP")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")
        message = format_cfd_signal(signal)
        self.assertIn("BIAS: LONG", message)
        self.assertIn("D-L-A: SHORT (CONTRASTS)", message)
        self.assertIn("MERCATO CONTRO BIAS", message)
        self.assertIn("ipotesi news non confermata dal prezzo", message)

    def test_early_dla_can_publish_technical_only_bias_when_news_is_neutral(self):
        now = datetime.now(timezone.utc).isoformat()
        quote = {
            "price": 80.0, "atr": 2.0, "timestamp": now,
            "provider": "Yahoo Finance chart (1m futures)", "symbol": "CL=F",
            "candles": [{"timestamp": now} for _ in range(60)],
        }
        focused_module = ModuleType("sputnik_focused_trader")
        focused_module.analyze_focused_market = lambda instrument, candles: {
            "status": "WAIT_CONFIRMATION", "direction": "NEUTRAL",
            "reason": "trigger non confermato",
        }
        setup_module = ModuleType("sputnik_competition_setup")
        setup_module.evaluate_competition_setup = lambda instrument, candles: {
            "status": "EARLY_SETUP", "direction": "LONG",
            "confirmations": ["Direction LONG", "Location LONG"],
            "missing_conditions": ["TRIGGER_NOT_CONFIRMED"],
            "reasons": ["bias LONG, trigger mancante"],
        }
        with patch.dict("sys.modules", {
            "sputnik_focused_trader": focused_module,
            "sputnik_competition_setup": setup_module,
        }):
            with patch("sputnik_cfd.attach_silv_crosscheck", side_effect=lambda q, instrument: q):
                signal = build_cfd_signal(
                    {"instrument": "WTI", "bias": "NEUTRAL", "score": 0, "reason": "no news side"},
                    {"WTI": quote},
                )
        self.assertEqual(signal["direction"], "LONG")
        self.assertEqual(signal["bias_source"], "DLA_EARLY")
        self.assertEqual(signal["setup_direction"], "LONG")
        self.assertEqual(signal["setup_alignment"], "TECHNICAL_ONLY")
        self.assertEqual(signal["status"], "EARLY_SETUP")
        self.assertEqual(signal["paper_trade_status"], "NOT_EXECUTED")


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
            "source_components": ["kitco", "fault", "chainlink", "nfusion"],
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
                    "source_prices": [
                        {"source": "kitco", "price": 49.0},
                        {"source": "fault", "price": 49.1},
                    ],
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

        self.assertEqual(
            result["crosscheck_status"],
            "SPOT_VS_FUTURES_BASIS_CHECK_INDEPENDENCE_UNVERIFIED",
        )
        self.assertEqual(result["spot_futures_basis_definition"], "spot_minus_futures")
        self.assertEqual(result["spot_futures_basis_price"], -1.0)
        self.assertEqual(result["spot_futures_basis_pct"], -2.0)
        self.assertIsNone(result["crosscheck_independent"])
        self.assertEqual(
            result["crosscheck_independence_status"],
            "PROVIDER_REPORTED_NOT_AUDITED",
        )
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
                    "provider": "Yahoo Finance chart (1m futures)",
                    "symbol": "SI=F",
                }
                reference = self.reference(**overrides)
                with patch("sputnik_cfd.fetch_silv_reference", return_value=reference):
                    result = attach_silv_crosscheck(quote, "SILVER")
                self.assertEqual(result["crosscheck_status"], expected_status)
                self.assertIsNone(result["spot_futures_basis_price"])
                self.assertIsNone(result["spot_futures_basis_pct"])

    def test_yahoo_source_overlap_disables_spot_futures_basis(self):
        quote = {
            "price": 6.50,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "currency": "USD",
            "unit": "pound",
            "market_type": "FUTURES_CONTINUOUS",
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "HG=F",
        }
        reference = self.reference(
            price=6.48,
            unit="pound",
            symbol="Cu",
            source_components=["yahoo", "fault"],
        )
        with patch("sputnik_cfd.fetch_silv_reference", return_value=reference):
            result = attach_silv_crosscheck(quote, "COPPER")

        self.assertEqual(result["crosscheck_status"], "SOURCE_OVERLAP")
        self.assertFalse(result["crosscheck_independent"])
        self.assertEqual(result["crosscheck_independence_status"], "KNOWN_SOURCE_OVERLAP")
        self.assertEqual(result["crosscheck_source_components"], ["yahoo", "fault"])
        self.assertIsNone(result["spot_futures_basis_price"])
        self.assertIsNone(result["spot_futures_basis_pct"])

    def test_missing_source_composition_is_not_claimed_independent(self):
        quote = {
            "price": 50.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "currency": "USD",
            "unit": "troy_oz",
            "market_type": "FUTURES_CONTINUOUS",
            "provider": "Yahoo Finance chart (1m futures)",
            "symbol": "SI=F",
        }
        reference = self.reference(source_components=[])
        with patch("sputnik_cfd.fetch_silv_reference", return_value=reference):
            result = attach_silv_crosscheck(quote, "SILVER")

        self.assertEqual(result["crosscheck_status"], "UNVERIFIED_SOURCE_COMPOSITION")
        self.assertIsNone(result["crosscheck_independent"])
        self.assertEqual(result["crosscheck_independence_status"], "NOT_ASSESSED")
        self.assertIsNone(result["spot_futures_basis_pct"])

    def test_unknown_execution_provider_is_not_claimed_independent(self):
        quote = {
            "price": 50.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "currency": "USD",
            "unit": "troy_oz",
            "market_type": "FUTURES_CONTINUOUS",
            "provider": "unknown broker feed",
            "symbol": "SI=F",
        }
        with patch("sputnik_cfd.fetch_silv_reference", return_value=self.reference()):
            result = attach_silv_crosscheck(quote, "SILVER")

        self.assertEqual(result["crosscheck_status"], "UNVERIFIED_EXECUTION_SOURCE")
        self.assertIsNone(result["crosscheck_independent"])
        self.assertEqual(result["crosscheck_independence_status"], "NOT_ASSESSED")
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
        self.assertEqual(
            signal["crosscheck_status"],
            "SPOT_VS_FUTURES_BASIS_CHECK_INDEPENDENCE_UNVERIFIED",
        )
        self.assertEqual(signal["spot_futures_basis_price"], -1.0)
        self.assertIsNone(signal["crosscheck_independent"])
        self.assertEqual(
            signal["crosscheck_independence_status"],
            "PROVIDER_REPORTED_NOT_AUDITED",
        )
        self.assertIn("indipendenza non verificata", format_cfd_signal(signal).lower())
        self.assertEqual(signal["crosscheck_currency"], "USD")
        self.assertEqual(signal["crosscheck_unit"], "troy_oz")
        self.assertEqual(signal["crosscheck_bid"], 48.9)
        self.assertEqual(signal["crosscheck_ask"], 49.1)




class NarwhalReferenceTests(unittest.TestCase):
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, traceback):
            return False
        def read(self):
            return json.dumps(self.payload).encode("utf-8")

    @staticmethod
    def payload(root="CL", **overrides):
        value = {
            "id": root, "name": "WTI Crude Oil", "exchange": "NYMEX",
            "currency": "USD", "unit": "usd_per_barrel", "price": "75.25",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market_session": "open", "stale": False, "delayed": True,
        }
        value.update(overrides)
        return value

    def setUp(self):
        import sputnik_cfd
        sputnik_cfd._NARWHAL_SLOT_CACHE.clear()

    def test_free_reference_is_disabled_without_explicit_opt_in(self):
        import sputnik_cfd
        with patch.dict("os.environ", {}, clear=True):
            with patch("sputnik_cfd.urllib.request.urlopen") as urlopen:
                result = sputnik_cfd.fetch_narwhal_reference("WTI")
        self.assertEqual(result["status"], "DISABLED")
        urlopen.assert_not_called()

    def test_missing_key_never_calls_endpoint(self):
        import sputnik_cfd
        with patch.dict("os.environ", {"NARWHAL_REFERENCE_ENABLED": "1"}, clear=True):
            with patch("sputnik_cfd.urllib.request.urlopen") as urlopen:
                result = sputnik_cfd.fetch_narwhal_reference("WTI")
        self.assertEqual(result["status"], "NOT_CONFIGURED")
        urlopen.assert_not_called()

    def test_delayed_price_keeps_provenance_and_is_reference_only(self):
        import sputnik_cfd
        with patch.dict("os.environ", {
            "NARWHAL_REFERENCE_ENABLED": "1", "NARWHAL_API_KEY": "free-test-key"
        }):
            slot = next(i for i in range(100) if i % 7 == 3)
            with patch("sputnik_cfd.time.time", return_value=slot * 1800 + 10):
                with patch("sputnik_cfd.urllib.request.urlopen", return_value=self.FakeResponse(
                    self.payload(timestamp=datetime.now(timezone.utc).isoformat())
                )) as urlopen:
                    result = sputnik_cfd.fetch_narwhal_reference("WTI")
        self.assertEqual(result["status"], "DELAYED_15M")
        self.assertEqual(result["price"], 75.25)
        self.assertEqual(result["symbol"], "CL")
        self.assertEqual(result["currency"], "USD")
        self.assertIsNone(result["bid"])
        self.assertIsNone(result["ask"])
        self.assertIsNone(result["contract_month"])
        self.assertIsNone(result["deviation_pct"])
        self.assertIn("REFERENCE_ONLY", result["use_restriction"])
        self.assertIn("Authorization", urlopen.call_args.args[0].headers)

    def test_stale_reference_is_flagged(self):
        import sputnik_cfd
        with patch.dict("os.environ", {
            "NARWHAL_REFERENCE_ENABLED": "1", "NARWHAL_API_KEY": "free-test-key"
        }):
            slot = next(i for i in range(100) if i % 7 == 3)
            old_stamp = (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            with patch("sputnik_cfd.time.time", return_value=slot * 1800 + 10):
                with patch("sputnik_cfd.urllib.request.urlopen", return_value=self.FakeResponse(
                    self.payload(timestamp=old_stamp, stale=True)
                )):
                    result = sputnik_cfd.fetch_narwhal_reference("WTI")
        self.assertEqual(result["status"], "STALE")
        self.assertIsNone(result["deviation_pct"])

    def test_signal_and_telegram_expose_reference_without_changing_execution(self):
        import sputnik_cfd
        quote = {
            "price": 80.0, "atr": 2.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "Yahoo Finance chart (1m futures)", "symbol": "CL=F",
        }
        reference = {
            "provider": "NARWHAL", "symbol": "CL", "price": 75.25,
            "currency": "USD", "unit": "usd_per_barrel",
            "source_timestamp": datetime.now(timezone.utc).isoformat(),
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "age_seconds": 900, "status": "DELAYED_15M",
            "deviation_pct": None,
            "use_restriction": "REFERENCE_ONLY_NOT_FOR_TRADE_EXECUTION",
        }
        with patch("sputnik_cfd.fetch_yahoo_quote", return_value=quote):
            with patch("sputnik_cfd.fetch_narwhal_reference", return_value=reference):
                with patch("sputnik_cfd.attach_silv_crosscheck", side_effect=lambda q, instrument: q):
                    signal = sputnik_cfd.build_cfd_signal(
                        {"instrument": "WTI", "bias": "LONG", "score": 80}, {}
                    )
        self.assertEqual(signal["entry"], 80.0)
        self.assertEqual(signal["quote_provider"], "Yahoo Finance chart (1m futures)")
        self.assertEqual(signal["narwhal_reference"]["price"], 75.25)
        message = sputnik_cfd.format_cfd_signal(signal)
        self.assertIn("NARWHAL REF", message)
        self.assertIn("usd_per_barrel", message)
        self.assertIn("bid/ask n.d.", message)
        self.assertIn("Fonte Narwhal:", message)
        self.assertIn("non usare per entry/sl/tp", message.lower())




class CfdCartDisplayStateTests(unittest.TestCase):
    def test_missing_quote_keeps_long_bias_and_marks_paper_not_executed(self):
        state = cfd_cart_display_state({
            "direction": "LONG", "status": "EARLY_BIAS",
            "setup_status": "EARLY_BIAS", "paper_trade_status": "NOT_EXECUTED",
        })
        self.assertEqual(state["direction"], "LONG")
        self.assertEqual(state["bias"], "DIRECTIONAL_BIAS")
        self.assertEqual(state["setup"], "EARLY_BIAS")
        self.assertEqual(state["paper_trade"], "NOT_EXECUTED")
        self.assertNotIn("WAIT", str(state))

    def test_levels_available_are_early_setup_not_an_executed_trade(self):
        state = cfd_cart_display_state({
            "direction": "SHORT", "status": "EARLY_SETUP",
            "setup_status": "EARLY_SETUP", "paper_trade_status": "NOT_EXECUTED",
        })
        self.assertEqual(state["direction"], "SHORT")
        self.assertEqual(state["setup"], "EARLY_SETUP")
        self.assertEqual(state["paper_trade"], "NOT_EXECUTED")

    def test_unsupported_side_is_neutral_no_direction(self):
        state = cfd_cart_display_state({
            "direction": "NEUTRAL", "status": "NO_DIRECTION",
        })
        self.assertEqual(state, {
            "direction": "NEUTRAL", "bias": "NO_DIRECTION",
            "setup": "NO_DIRECTION", "paper_trade": "NOT_EXECUTED",
        })
        self.assertNotIn("WAIT", str(state))

    def test_unknown_setup_cannot_be_promoted_to_confirmed(self):
        state = cfd_cart_display_state({
            "direction": "LONG", "status": "TRADE",
            "setup_status": "TRADE", "paper_trade_status": "TRADE",
        })
        self.assertEqual(state["setup"], "EARLY_BIAS")
        self.assertEqual(state["paper_trade"], "NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main()
