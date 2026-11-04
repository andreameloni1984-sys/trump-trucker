import unittest

from sputnik_catalyst import catalyst_watchlist


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

    def test_fresh_dated_catalyst_ranks_above_old_event_without_becoming_buy(self):
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        base = {
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "evidence": "PUBLIC_SOURCE_TEXT",
            "event_id": "same-event-class",
            "title": "OPEC announces crude oil production cut",
        }
        fresh = dict(base, published=(now - timedelta(minutes=30)).isoformat())
        old = dict(base, published=(now - timedelta(days=10)).isoformat())
        fresh_row = catalyst_watchlist([fresh])[0]
        old_row = catalyst_watchlist([old])[0]
        self.assertGreater(fresh_row["score"], old_row["score"])
        self.assertEqual(fresh_row["status"], "WATCH")
        self.assertEqual(fresh_row["recency_score"], 10)

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


if __name__ == "__main__":
    unittest.main()
