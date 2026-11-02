import unittest

from sputnik_catalyst import catalyst_watchlist, directional_news_candidates


class CatalystWatchlistTests(unittest.TestCase):
    def test_primary_energy_event_creates_energy_watchlist(self):
        rows = catalyst_watchlist([{
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "evidence": "PUBLIC_SOURCE_TEXT",
            "event_id": "diesel-2026",
            "title": "US strategic petroleum reserve release announced",
            "text": "The release is intended to increase available petroleum supply.",
        }])
        instruments = {row["instrument"] for row in rows}
        self.assertEqual({"WTI", "BRENT"}, instruments)
        self.assertTrue(all(row["status"] == "WATCH" for row in rows))
        self.assertTrue(all(row["primary_source"] for row in rows))

    def test_multiple_public_events_raise_evidence_score_without_creating_buy(self):
        rows = catalyst_watchlist([
            {"source": "WHITE_HOUSE", "domains": ["ENERGY"], "event_id": "a", "evidence": "PUBLIC_SOURCE_TEXT", "title": "OPEC announces crude oil production cut"},
            {"source": "OGE", "domains": ["ENERGY"], "event_id": "b", "evidence": "PUBLIC_SOURCE_TEXT", "title": "Crude exports disrupted after pipeline attack"},
        ])
        self.assertEqual(rows[0]["status"], "WATCH")
        self.assertGreaterEqual(rows[0]["score"], 60)
        self.assertIn("BUY/SELL", rows[0]["reason"])

    def test_generic_energy_dominance_does_not_create_oil_watchlist(self):
        rows = catalyst_watchlist([{
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "evidence": "PUBLIC_SOURCE_TEXT",
            "event_id": "energy-speech-2026",
            "title": "Unleash American Energy DOMINANCE",
            "text": "The speech discusses jobs, manufacturing and national leadership.",
        }])
        self.assertEqual(rows, [])

    def test_specific_crude_supply_event_creates_energy_watchlist(self):
        rows = catalyst_watchlist([{
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "evidence": "PUBLIC_SOURCE_TEXT",
            "event_id": "crude-supply-2026",
            "title": "US crude output falls after pipeline disruption",
        }])
        self.assertEqual({row["instrument"] for row in rows}, {"WTI", "BRENT"})

    def test_oil_vessel_and_hormuz_closure_are_market_context(self):
        for title in (
            "Oil vessel struck near Saudi Arabia",
            "Iran warns it could close the Strait of Hormuz",
        ):
            with self.subTest(title=title):
                rows = catalyst_watchlist([{
                    "source": "WHITE_HOUSE",
                    "domains": ["ENERGY"],
                    "evidence": "PUBLIC_SOURCE_TEXT",
                    "event_id": title,
                    "title": title,
                }])
                self.assertEqual(
                    {row["instrument"] for row in rows}, {"WTI", "BRENT"}
                )

    def test_unknown_domain_is_ignored(self):
        self.assertEqual(catalyst_watchlist([{"source": "WHITE_HOUSE", "domains": ["UNKNOWN"], "event_id": "x"}]), [])

    def test_limit(self):
        rows = catalyst_watchlist([{
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY", "METALS", "AGRICULTURE"],
            "event_id": "x",
        }], limit=2)
        self.assertEqual(len(rows), 2)



    def test_directional_us_crude_production_cut_maps_only_to_wti(self):
        rows = directional_news_candidates([{
            "evidence": "PUBLIC_RSS_ITEM",
            "event_id": "us-production-cut",
            "url": "https://example.gov/us-oil",
            "published": "2026-11-02T10:00:00Z",
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "title": "U.S. crude oil production cut announced",
            "text": "",
        }])
        self.assertEqual({row["instrument"] for row in rows}, {"WTI"})

    def test_directional_hormuz_shipping_disruption_maps_only_to_brent(self):
        rows = directional_news_candidates([{
            "evidence": "PUBLIC_RSS_ITEM",
            "event_id": "hormuz-shipping",
            "url": "https://example.gov/hormuz",
            "published": "2026-11-02T10:00:00Z",
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "title": "Shipping disruption through the Strait of Hormuz",
            "text": "",
        }])
        self.assertEqual({row["instrument"] for row in rows}, {"BRENT"})

    def test_generic_oil_supply_disruption_has_no_directional_benchmark(self):
        rows = directional_news_candidates([{
            "evidence": "PUBLIC_RSS_ITEM",
            "event_id": "generic-oil-supply",
            "url": "https://example.gov/oil",
            "published": "2026-11-02T10:00:00Z",
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "title": "Oil supply disruption reported",
            "text": "",
        }])
        self.assertEqual(rows, [])

    def test_foreign_producer_crude_output_cut_maps_to_brent(self):
        rows = directional_news_candidates([{
            "evidence": "PUBLIC_RSS_ITEM",
            "event_id": "foreign-output-cut",
            "url": "https://example.gov/producer",
            "published": "2026-11-02T10:00:00Z",
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "title": "Saudi crude oil production cut announced",
            "text": "",
        }])
        self.assertEqual({row["instrument"] for row in rows}, {"BRENT"})

if __name__ == "__main__":
    unittest.main()
