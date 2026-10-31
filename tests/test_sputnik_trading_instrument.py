import unittest

from sputnik_trading_instrument import recommend_trading_instrument


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


class EarlyBrentCatalystTests(unittest.TestCase):
    def test_tanker_near_saudi_struck_creates_preliminary_brent_long(self):
        recommendation = recommend_trading_instrument([
            _finding("Oil tanker near Saudi Arabia was struck")
        ])

        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation["instrument"], "BRENT")
        self.assertEqual(recommendation["bias"], "LONG")
        self.assertEqual(recommendation["status"], "PRELIMINARY_DIRECTIONAL_BIAS")
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
                self.assertEqual(recommendation["status"], "WATCH_NEUTRAL")

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



if __name__ == "__main__":
    unittest.main()
