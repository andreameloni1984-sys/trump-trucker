import unittest

from sputnik_catalyst import catalyst_watchlist


class CatalystWatchlistTests(unittest.TestCase):
    def test_primary_energy_event_creates_energy_watchlist(self):
        rows = catalyst_watchlist([{
            "source": "WHITE_HOUSE",
            "domains": ["ENERGY"],
            "evidence": "PUBLIC_SOURCE_TEXT",
            "event_id": "diesel-2026",
        }])
        instruments = {row["instrument"] for row in rows}
        self.assertEqual({"WTI", "BRENT"}, instruments)
        self.assertTrue(all(row["status"] == "WATCH" for row in rows))
        self.assertTrue(all(row["primary_source"] if "primary_source" in row else True for row in rows))

    def test_multiple_public_events_raise_evidence_score_without_creating_buy(self):
        rows = catalyst_watchlist([
            {"source": "WHITE_HOUSE", "domains": ["ENERGY"], "event_id": "a", "evidence": "PUBLIC_SOURCE_TEXT"},
            {"source": "OGE", "domains": ["ENERGY"], "event_id": "b", "evidence": "PUBLIC_SOURCE_TEXT"},
        ])
        self.assertEqual(rows[0]["status"], "WATCH")
        self.assertGreaterEqual(rows[0]["score"], 60)
        self.assertIn("BUY/SELL", rows[0]["reason"])

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
