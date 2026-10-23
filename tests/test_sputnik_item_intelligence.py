import json
import os
import unittest
from unittest.mock import MagicMock, patch

import trump_tracker
from sputnik_catalyst import catalyst_watchlist


FEED = b"""<rss><channel><item>
<title>President announces new tariffs on China</title>
<link>https://example.gov/news/tariffs</link>
<guid>tariff-event-1</guid>
<pubDate>Mon, 19 Oct 2026 06:00:00 GMT</pubDate>
<description><![CDATA[New trade measures announced.]]></description>
</item></channel></rss>"""


class SputnikItemIntelligenceTests(unittest.TestCase):
    def test_tariff_headline_is_classified_as_a_market_catalyst(self):
        domains = trump_tracker._domains_for_public_text(
            "President announces new tariffs on China"
        )
        self.assertIn("TRADE_POLICY", domains)

    @patch.object(trump_tracker, "fetch_public_text", side_effect=OSError("offline in test"))
    @patch.object(trump_tracker, "fetch_public_feed", return_value=FEED)
    def test_rss_items_are_saved_with_title_date_url_and_deduplicated(
        self, _fetch_feed, _fetch_page
    ):
        state = {}
        with patch.dict(os.environ, {"SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml"}):
            first = trump_tracker.intelligence_snapshot(state)
            second = trump_tracker.intelligence_snapshot(state)

        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        item = first[0]
        self.assertEqual(item["title"], "President announces new tariffs on China")
        self.assertEqual(item["published"], "Mon, 19 Oct 2026 06:00:00 GMT")
        self.assertEqual(item["url"], "https://example.gov/news/tariffs")
        self.assertIn("TRADE_POLICY", item["domains"])
        self.assertEqual(item["evidence"], "PUBLIC_RSS_ITEM")

    def test_trade_policy_maps_to_watch_candidates_not_orders(self):
        rows = catalyst_watchlist(
            [{"source": "WHITE_HOUSE_RSS", "domains": ["TRADE_POLICY"], "event_id": "evt-1", "evidence": "PUBLIC_RSS_ITEM"}]
        )
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "WATCH" for row in rows))
        self.assertTrue(all("LONG" not in row["status"] and "BUY" not in row["status"] for row in rows))


    def test_item_level_news_message_contains_sputnik_market_analysis(self):
        message = trump_tracker.intelligence_message({
            "source": "WHITE_HOUSE_RSS",
            "title": "President announces new tariffs on imports",
            "published": "2026-10-22T12:00:00Z",
            "url": "https://example.gov/news/tariffs",
            "text": "The administration announces a concrete increase in import tariffs.",
            "evidence": "PUBLIC_RSS_ITEM",
        })
        self.assertIn("SPUTNIK — ANALISI NOTIZIA", message)
        self.assertIn("ORO (XAU/USD)", message)
        self.assertIn("LONG condizionale", message)
        self.assertIn("Conferma richiesta", message)
        self.assertNotIn("GAGARIN", message.upper())

    def test_page_level_metadata_is_never_sent_as_news(self):
        message = trump_tracker.intelligence_message({
            "source": "TRUTH_ARCHIVE",
            "title": "",
            "url": "https://www.trumpstruth.org/",
            "text": '{"@context":"https://schema.org","name":"Trump Truth","description":"archive"}',
            "evidence": "PUBLIC_SOURCE_TEXT_PAGE_LEVEL",
        })
        self.assertEqual(message, "")


if __name__ == "__main__":
    unittest.main()
