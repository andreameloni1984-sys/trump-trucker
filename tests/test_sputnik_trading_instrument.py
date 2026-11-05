import json
import time
import unittest
from unittest.mock import patch

from sputnik_trading_instrument import format_trading_instrument_message, recommend_trading_instrument


def _finding(title, **overrides):
    finding = {
        "source": "REUTERS",
        "evidence": "PUBLIC_RSS_ITEM",
        "event_id": "energy-event-2026-10-30",
        "url": "https://example.com/energy-event",
        "published": "2026-10-30T21:00:00Z",
        "domains": ["ENERGY"],
        "title": title,
        "text": "",
    }
    finding.update(overrides)
    return finding


class TechnicalQuoteFreshnessTests(unittest.TestCase):
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps(self.payload).encode("utf-8")

    def test_stale_five_minute_candles_are_not_technical_confirmation(self):
        from sputnik_trading_instrument import _technical_market_bias

        now = int(time.time()) - 3600
        stamps = [now - (64 - index) * 300 for index in range(65)]
        closes = [100.0 + index * 0.1 for index in range(65)]
        payload = {
            "chart": {
                "result": [{
                    "timestamp": stamps,
                    "indicators": {"quote": [{"close": closes}]},
                }]
            }
        }
        with patch(
            "sputnik_trading_instrument.urllib.request.urlopen",
            return_value=self.FakeResponse(payload),
        ):
            result = _technical_market_bias("WTI")

        self.assertIsNone(result)

    def test_short_recent_history_uses_four_completed_candles(self):
        from sputnik_trading_instrument import _technical_market_bias

        now = int(time.time())
        stamps = [now - (64 - index) * 300 for index in range(65)]
        closes = [100.0 + index * 0.1 for index in range(65)]
        payload = {
            "chart": {
                "result": [{
                    "timestamp": stamps,
                    "indicators": {"quote": [{"close": closes}]},
                }]
            }
        }
        with patch("sputnik_trading_instrument.time.time", return_value=now), patch(
            "sputnik_trading_instrument.urllib.request.urlopen",
            return_value=self.FakeResponse(payload),
        ):
            result = _technical_market_bias("WTI")

        self.assertIsNotNone(result)
        self.assertEqual(result["bias"], "LONG")
        self.assertEqual(result["quote_timestamp"], stamps[-2])
        self.assertGreater(result["momentum_15m_pct"], 0)
        self.assertEqual(result["bias"], "LONG")

    def test_forming_five_minute_candle_cannot_reverse_completed_bias(self):
        from sputnik_trading_instrument import _technical_market_bias

        now = int(time.time())
        stamps = [now - (64 - index) * 300 for index in range(65)]
        closes = [100.0 + index * 0.1 for index in range(64)] + [95.0]
        payload = {
            "chart": {
                "result": [{
                    "timestamp": stamps,
                    "indicators": {"quote": [{"close": closes}]},
                }]
            }
        }
        with patch("sputnik_trading_instrument.time.time", return_value=now), patch(
            "sputnik_trading_instrument.urllib.request.urlopen",
            return_value=self.FakeResponse(payload),
        ):
            result = _technical_market_bias("WTI")

        self.assertIsNotNone(result)
        self.assertEqual(result["bias"], "LONG")
        self.assertEqual(result["price"], 100.3)
        self.assertEqual(result["quote_timestamp"], stamps[-2])

    def test_three_completed_bars_plus_one_forming_bar_are_insufficient(self):
        from sputnik_trading_instrument import _technical_market_bias

        now = int(time.time())
        stamps = [now - (3 - index) * 300 for index in range(4)]
        closes = [100.0, 100.1, 100.2, 99.0]
        payload = {
            "chart": {
                "result": [{
                    "timestamp": stamps,
                    "indicators": {"quote": [{"close": closes}]},
                }]
            }
        }
        with patch("sputnik_trading_instrument.time.time", return_value=now), patch(
            "sputnik_trading_instrument.urllib.request.urlopen",
            return_value=self.FakeResponse(payload),
        ):
            result = _technical_market_bias("WTI")

        self.assertIsNone(result)

    def test_null_close_does_not_shift_price_timestamp_pairing(self):
        from sputnik_trading_instrument import _technical_market_bias

        now = int(time.time())
        stamps = [now - (64 - index) * 300 for index in range(65)]
        closes = [100.0 + index * 0.1 for index in range(65)]
        closes[-2] = None
        payload = {
            "chart": {
                "result": [{
                    "timestamp": stamps,
                    "indicators": {"quote": [{"close": closes}]},
                }]
            }
        }
        with patch("sputnik_trading_instrument.time.time", return_value=now), patch(
            "sputnik_trading_instrument.urllib.request.urlopen",
            return_value=self.FakeResponse(payload),
        ):
            result = _technical_market_bias("WTI")

        self.assertIsNotNone(result)
        self.assertEqual(result["quote_timestamp"], stamps[-3])


class EarlyBrentCatalystTests(unittest.TestCase):
    def setUp(self):
        # Ranking tests must not depend on live Yahoo candles. Each test below
        # supplies technical evidence explicitly when that behavior is under test.
        self.technical_patcher = patch(
            "sputnik_trading_instrument._technical_market_bias",
            return_value={
                "bias": "NEUTRAL",
                "score": 45.0,
                "reason": "Fixture tecnica neutrale",
                "timeframe": "5m",
                "candles": 60,
            },
        )
        self.technical_patcher.start()
        self.addCleanup(self.technical_patcher.stop)

    def test_mixed_technical_snapshot_does_not_erase_news_direction(self):
        finding = _finding("EIA reports U.S. crude inventories fell by 2.1 million barrels")
        mixed = {
            "bias": "NEUTRAL",
            "score": 45.0,
            "reason": "EMA and swing structure are mixed",
            "price": 80.0,
            "ema20": 80.1,
            "ema50": 79.9,
            "timeframe": "5m",
            "candles": 60,
        }
        with patch("sputnik_trading_instrument._technical_market_bias", return_value=mixed):
            recommendation = recommend_trading_instrument([finding])

        self.assertEqual(recommendation["instrument"], "WTI")
        self.assertEqual(recommendation["catalyst_bias"], "LONG")
        self.assertEqual(recommendation["technical_bias"], "NEUTRAL")
        self.assertEqual(recommendation["bias"], "LONG")
        self.assertEqual(recommendation["status"], "EARLY_BIAS")

    def test_opposite_technical_direction_does_not_override_catalyst_bias(self):
        finding = _finding("Oil tanker near Saudi Arabia was struck")
        technical = {
            "bias": "SHORT",
            "score": 78.0,
            "reason": "Prezzo sotto EMA20/EMA50 e swing decrescenti",
            "price": 79.0,
            "ema20": 79.2,
            "ema50": 80.0,
            "timeframe": "5m",
            "candles": 60,
            "quote_timestamp": 1793566800,
        }
        with patch("sputnik_trading_instrument._technical_market_bias", return_value=technical):
            recommendation = recommend_trading_instrument([finding])

        self.assertEqual(recommendation["catalyst_bias"], "LONG")
        self.assertEqual(recommendation["technical_bias"], "SHORT")
        self.assertEqual(recommendation["bias"], "LONG")
        self.assertEqual(recommendation["catalyst_alignment"], "CONTRASTS")
        self.assertEqual(recommendation["status"], "EARLY_BIAS")
        message = format_trading_instrument_message(recommendation)
        self.assertIn("BIAS PRELIMINARE: LONG", message)
        self.assertIn("DIREZIONE TECNICA: SHORT", message)
        self.assertIn("ALLINEAMENTO NOTIZIE: CONTRASTS", message)

    def test_aligned_technical_direction_does_not_promote_catalyst_to_confirmed(self):
        finding = _finding("Oil tanker near Saudi Arabia was struck")
        technical = {
            "bias": "LONG",
            "score": 78.0,
            "reason": "Prezzo sopra EMA20/EMA50 e swing crescenti",
            "timeframe": "5m",
            "candles": 60,
        }
        with patch("sputnik_trading_instrument._technical_market_bias", return_value=technical):
            recommendation = recommend_trading_instrument([finding])

        self.assertEqual(recommendation["bias"], "LONG")
        self.assertEqual(recommendation["catalyst_alignment"], "ALIGNS")
        self.assertEqual(recommendation["status"], "EARLY_BIAS")
        self.assertNotEqual(recommendation["status"], "CONFIRMED")

    def test_tanker_near_saudi_struck_creates_preliminary_brent_long(self):
        recommendation = recommend_trading_instrument([
            _finding("Oil tanker near Saudi Arabia was struck")
        ])

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "LONG")
        self.assertEqual(recommendation["status"], "EARLY_BIAS")
        self.assertEqual(recommendation["url"], "https://example.com/energy-event")

    def test_attack_on_oil_vessel_near_hormuz_creates_preliminary_brent_long(self):
        recommendation = recommend_trading_instrument([
            _finding("Attack reported on oil vessel near the Strait of Hormuz")
        ])

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "LONG")

    def test_us_troop_withdrawal_without_oil_supply_link_does_not_create_brent_bias(self):
        recommendation = recommend_trading_instrument([
            _finding("US troops withdraw from Saudi Arabia")
        ])

        self.assertIsNone(recommendation)

    def test_early_brent_bias_still_requires_dated_url_backed_rss_item(self):
        base = _finding("Oil tanker near Saudi Arabia was struck")
        for missing_field in ("url", "published", "event_id"):
            with self.subTest(missing_field=missing_field):
                item = dict(base)
                item.pop(missing_field)
                recommendation = recommend_trading_instrument([item])

                self.assertIsNotNone(recommendation)
                self.assertEqual(recommendation["bias"], "NEUTRAL")


    def test_blank_event_id_cannot_create_directional_pre_alert(self):
        for event_id in ("", "   "):
            with self.subTest(event_id=event_id):
                recommendation = recommend_trading_instrument([
                    _finding(
                        "Oil tanker near Saudi Arabia was struck",
                        event_id=event_id,
                    )
                ])

                self.assertIsNotNone(recommendation)
                self.assertEqual(recommendation["instrument"], "BRENT")
                self.assertEqual(recommendation["bias"], "NEUTRAL")
                self.assertEqual(recommendation["status"], "NO_DIRECTION")

    def test_hormuz_reopening_is_brent_short_not_long(self):
        recommendation = recommend_trading_instrument([
            _finding("Strait of Hormuz reopened after ceasefire; shipping resumes")
        ])

        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "SHORT")

    def test_unrelated_ceasefire_does_not_create_oil_short(self):
        recommendation = recommend_trading_instrument([
            _finding("Ceasefire agreement reached in Gaza after negotiations")
        ])

        self.assertIsNone(recommendation)

    def test_bare_hormuz_mention_stays_neutral(self):
        recommendation = recommend_trading_instrument([
            _finding("Officials discuss the Strait of Hormuz at a diplomatic summit")
        ])

        self.assertIsNone(recommendation)

    def test_negated_oil_supply_disruption_does_not_create_long(self):
        recommendation = recommend_trading_instrument([
            _finding("Officials report no oil supply disruption after talks on Hormuz")
        ])

        self.assertEqual(recommendation["bias"], "NEUTRAL")

    def test_unrelated_negation_in_previous_clause_does_not_hide_tanker_attack(self):
        recommendation = recommend_trading_instrument([
            _finding("No details were released, an oil tanker was struck near Hormuz")
        ])

        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "LONG")

    def test_negated_tanker_attack_does_not_create_long(self):
        recommendation = recommend_trading_instrument([
            _finding("No attack was reported on an oil tanker near Hormuz")
        ])

        self.assertEqual(recommendation["bias"], "NEUTRAL")

    def test_alternative_threat_to_close_wording_creates_brent_long(self):
        recommendation = recommend_trading_instrument([
            _finding("Iran warns it could close the Strait of Hormuz")
        ])

        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "LONG")

    def test_shipping_resumption_alternative_creates_brent_short(self):
        recommendation = recommend_trading_instrument([
            _finding("Shipping has resumed through Hormuz after the reopening")
        ])

        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "SHORT")

    def test_mixed_escalation_and_reopening_stays_neutral(self):
        recommendation = recommend_trading_instrument([
            _finding(
                "Iran threatens to close Hormuz, but shipping is restored through the Strait"
            )
        ])

        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "NEUTRAL")


    def test_us_crude_inventory_draw_maps_specifically_to_wti_long(self):
        recommendation = recommend_trading_instrument([
            _finding("EIA reports U.S. crude inventories fell by 2.1 million barrels")
        ])

        self.assertEqual(recommendation["instrument"], "WTI")
        self.assertEqual(recommendation["bias"], "LONG")
        self.assertEqual(recommendation["type"], "US_CRUDE_INVENTORY_EARLY_RULE")

    def test_us_crude_inventory_build_maps_specifically_to_wti_short(self):
        recommendation = recommend_trading_instrument([
            _finding("API reports U.S. crude stockpiles built by 3.4 million barrels")
        ])

        self.assertEqual(recommendation["instrument"], "WTI")
        self.assertEqual(recommendation["bias"], "SHORT")
        self.assertEqual(recommendation["type"], "US_CRUDE_INVENTORY_EARLY_RULE")

    def test_negated_us_crude_inventory_draw_does_not_create_wti_long(self):
        recommendation = recommend_trading_instrument([
            _finding("EIA says U.S. crude inventories did not fall")
        ])

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["bias"], "NEUTRAL")

    def test_conflicting_us_inventory_draw_and_build_stays_neutral(self):
        recommendation = recommend_trading_instrument([
            _finding(
                "EIA says U.S. crude inventories fell, but EIA later says "
                "U.S. crude inventories rose"
            )
        ])

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["bias"], "NEUTRAL")

    def test_non_us_crude_inventory_move_does_not_map_to_wti(self):
        recommendation = recommend_trading_instrument([
            _finding("European crude inventories fell by 1.2 million barrels")
        ])

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["bias"], "NEUTRAL")



class TrendClassificationTests(unittest.TestCase):
    def test_ema_trend_not_short_momentum_sets_direction(self):
        from sputnik_trading_instrument import _classify_technical_trend
        rising = [100.0 + i * 0.2 for i in range(100)]
        rising[-3:] = [rising[-4] - 0.1, rising[-4] - 0.2, rising[-4] - 0.3]
        result = _classify_technical_trend(rising)
        self.assertEqual(result["bias"], "LONG")
        self.assertLess(rising[-1], rising[-4])

    def test_downtrend_with_short_bounce_keeps_short_trend(self):
        from sputnik_trading_instrument import _classify_technical_trend
        falling = [200.0 - i * 0.2 for i in range(100)]
        falling[-3:] = [falling[-4] + 0.1, falling[-4] + 0.2, falling[-4] + 0.3]
        result = _classify_technical_trend(falling)
        self.assertEqual(result["bias"], "SHORT")

    def test_insufficient_history_has_no_ema(self):
        from sputnik_trading_instrument import _classify_technical_trend
        result = _classify_technical_trend([100.0 + i for i in range(20)])
        self.assertEqual(result["bias"], "NEUTRAL")
        self.assertIsNone(result["ema20"])
        self.assertIsNone(result["ema50"])


if __name__ == "__main__":
    unittest.main()
