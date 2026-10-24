import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import trump_tracker
from trump_tracker import TextExtractor
from sputnik_catalyst import catalyst_watchlist


FEED = b"""<rss><channel><item>
<title>President announces new tariffs on China</title>
<link>https://example.gov/news/tariffs</link>
<guid>tariff-event-1</guid>
<pubDate>Sat, 24 Oct 2026 06:00:00 GMT</pubDate>
<description><![CDATA[New trade measures announced.]]></description>
</item></channel></rss>"""


class SputnikItemIntelligenceTests(unittest.TestCase):
    def test_page_text_extractor_ignores_jsonld_and_site_navigation(self):
        html = """
        <html><head>
          <script type="application/ld+json">
            {"@type":"WebSite","name":"Example","description":"Gold AI Federal Reserve"}
          </script>
          <style>.hidden { color: red }</style>
        </head><body>
          <nav>Gold silver AI menu</nav>
          <main><h1>White House announces a new energy policy</h1>
            <p>Official details of the policy.</p>
          </main>
          <footer>Media rates macro site links</footer>
        </body></html>
        """
        parser = TextExtractor()
        parser.feed(html)
        visible = parser.text()

        self.assertIn("White House announces a new energy policy", visible)
        self.assertIn("Official details of the policy.", visible)
        self.assertNotIn("Federal Reserve", visible)
        self.assertNotIn("Gold silver AI menu", visible)
        self.assertNotIn("Media rates macro site links", visible)
        self.assertNotIn("@type", visible)

    def setUp(self):
        clock = patch.object(
            trump_tracker, "utc_now",
            return_value=datetime(2026, 10, 24, 7, 0, tzinfo=timezone.utc),
        )
        clock.start()
        self.addCleanup(clock.stop)

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
        self.assertEqual(item["published"], "Sat, 24 Oct 2026 06:00:00 GMT")
        self.assertEqual(item["url"], "https://example.gov/news/tariffs")
        self.assertIn("TRADE_POLICY", item["domains"])
        self.assertEqual(item["evidence"], "PUBLIC_RSS_ITEM")

    @patch.object(trump_tracker, "fetch_public_text", side_effect=OSError("offline in test"))
    @patch.object(trump_tracker, "fetch_public_feed", return_value=FEED)
    def test_same_permalink_in_two_feeds_is_emitted_once(self, _fetch_feed, _fetch_page):
        state = {}
        with patch.dict(os.environ, {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": "https://feed-a.example/rss;https://feed-b.example/rss",
        }):
            findings = trump_tracker.intelligence_snapshot(state)

        self.assertEqual(len(findings), 1)
        self.assertEqual(len(state["intelligence_items"]), 1)
        self.assertEqual(findings[0]["url"], "https://example.gov/news/tariffs")

    def test_generic_homepages_are_not_emitted_as_individual_catalysts(self):
        with patch.dict(os.environ, {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml",
        }):
            with patch.object(
                trump_tracker, "fetch_public_text",
                return_value="Gold artificial intelligence federal reserve generic homepage",
            ), patch.object(
                trump_tracker, "fetch_public_feed", return_value=b"<rss><channel/></rss>"
            ):
                findings = trump_tracker.intelligence_snapshot({})

        self.assertEqual(findings, [])

    def test_default_feeds_include_truth_archive_and_white_house(self):
        with patch.dict(os.environ, {"SPUTNIK_RSS_FEEDS": ""}, clear=False):
            feeds = trump_tracker._configured_rss_feeds()
        self.assertIn("https://www.whitehouse.gov/news/feed/", feeds)
        self.assertIn("https://www.trumpstruth.org/feed", feeds)

    def test_truth_archive_feed_is_labelled_separately(self):
        with patch.dict(os.environ, {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": "https://www.trumpstruth.org/feed",
        }):
            with patch.object(trump_tracker, "fetch_public_text", side_effect=OSError("offline in test")), patch.object(
                trump_tracker, "fetch_public_feed", return_value=FEED
            ):
                findings = trump_tracker.intelligence_snapshot({})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["source"], "TRUTH_ARCHIVE_RSS")
        self.assertEqual(findings[0]["evidence"], "PUBLIC_RSS_ITEM")

    @patch.object(trump_tracker, "fetch_public_text", side_effect=OSError("offline in test"))
    def test_stale_public_item_is_not_emitted_as_a_new_catalyst(self, _fetch_page):
        stale_feed = FEED.replace(
            b"Sat, 24 Oct 2026 06:00:00 GMT",
            b"Mon, 19 Oct 2026 06:00:00 GMT",
        )
        state = {}
        with patch.dict(os.environ, {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml",
            "SPUTNIK_MAX_NEWS_AGE_HOURS": "72",
        }):
            with patch.object(trump_tracker, "fetch_public_feed", return_value=stale_feed):
                findings = trump_tracker.intelligence_snapshot(state)

        self.assertEqual(findings, [])
        self.assertEqual(state.get("intelligence_items", {}), {})

    def test_recent_atom_update_does_not_resurface_old_publication(self):
        atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <id>old-tariff-story</id><title>President announces new tariffs on China</title>
        <link rel="alternate" href="https://example.gov/news/old-tariffs"/>
        <published>Mon, 19 Oct 2026 06:00:00 GMT</published>
        <updated>Sat, 24 Oct 2026 06:00:00 GMT</updated>
        <summary>New trade measures announced.</summary></entry></feed>"""
        state = {}
        with patch.dict(os.environ, {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml",
            "SPUTNIK_MAX_NEWS_AGE_HOURS": "72",
        }), patch.object(
            trump_tracker, "fetch_public_text", side_effect=OSError("offline in test")
        ), patch.object(trump_tracker, "fetch_public_feed", return_value=atom):
            findings = trump_tracker.intelligence_snapshot(state)

        self.assertEqual(findings, [])
        self.assertEqual(state.get("intelligence_items", {}), {})

    def test_feed_failures_are_recorded_and_alerted_once_until_recovery(self):
        state = {}
        feed_url = "https://www.trumpstruth.org/feed"
        env = {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": feed_url,
        }
        with patch.dict(os.environ, env), patch.object(
            trump_tracker, "fetch_public_text", side_effect=OSError("offline in test")
        ), patch.object(
            trump_tracker, "fetch_public_feed", side_effect=OSError("feed offline")
        ):
            self.assertEqual(trump_tracker.intelligence_snapshot(state), [])

        health = state["public_feed_health"][feed_url]
        self.assertEqual(health["source"], "TRUTH_ARCHIVE_RSS")
        self.assertEqual(health["status"], "ERROR")
        self.assertEqual(health["error_type"], "OSError")

        alert = trump_tracker.public_feed_health_alert(state)
        self.assertIsNotNone(alert)
        self.assertIn("TRUTH_ARCHIVE_RSS", alert["message"])
        self.assertIn("OSError", alert["message"])
        self.assertIn("Nessun segnale di mercato", alert["message"])
        self.assertNotIn("LONG", alert["message"])
        self.assertNotIn("SHORT", alert["message"])

        # The caller records the signature only after Telegram confirms send.
        state["public_feed_health_alert_signature"] = alert["signature"]
        self.assertIsNone(trump_tracker.public_feed_health_alert(state))

        with patch.dict(os.environ, env), patch.object(
            trump_tracker, "fetch_public_text", side_effect=OSError("offline in test")
        ), patch.object(trump_tracker, "fetch_public_feed", return_value=FEED):
            trump_tracker.intelligence_snapshot(state)

        self.assertEqual(state["public_feed_health"][feed_url]["status"], "OK")
        self.assertIsNone(trump_tracker.public_feed_health_alert(state))
        self.assertEqual(state["public_feed_health_alert_signature"], "")

    def test_valid_empty_feed_is_not_misreported_as_an_outage(self):
        state = {}
        with patch.dict(os.environ, {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml",
        }), patch.object(
            trump_tracker, "fetch_public_text", side_effect=OSError("offline in test")
        ), patch.object(
            trump_tracker, "fetch_public_feed", return_value=b"<rss><channel/></rss>"
        ):
            trump_tracker.intelligence_snapshot(state)

        health = state["public_feed_health"]["https://example.gov/feed.xml"]
        self.assertEqual(health["status"], "OK_NO_ELIGIBLE_ITEMS")
        self.assertIsNone(trump_tracker.public_feed_health_alert(state))

    def test_intelligence_alert_shows_validated_original_permalink(self):
        message = trump_tracker.intelligence_message({
            "source": "TRUTH_ARCHIVE_RSS",
            "title": "Policy announcement",
            "published": "2026-10-24T06:00:00Z",
            "domains": ["TRADE_POLICY"],
            "evidence": "PUBLIC_RSS_ITEM",
            "url": "https://archive.example/posts/123",
            "primary_url": "https://social.example/@public/123?utm_source=feed",
        })
        self.assertIn("🔗 Articolo/archivio: https://archive.example/posts/123", message)
        self.assertIn("🔗 Post originale: https://social.example/@public/123", message)
        self.assertIn("non è un segnale LONG/SHORT", message)

    def test_intelligence_alert_omits_invalid_original_permalink(self):
        message = trump_tracker.intelligence_message({
            "source": "TRUTH_ARCHIVE_RSS",
            "title": "Policy announcement",
            "published": "2026-10-24T06:00:00Z",
            "domains": ["TRADE_POLICY"],
            "evidence": "PUBLIC_RSS_ITEM",
            "url": "https://archive.example/posts/123",
            "primary_url": "javascript:alert(1)",
        })
        self.assertIn("🔗 Articolo/archivio: https://archive.example/posts/123", message)
        self.assertNotIn("javascript:", message)
        self.assertNotIn("🔗 Post originale:", message)

    def test_failed_telegram_delivery_releases_dedup_key_for_retry(self):
        state = {"intelligence_items": {"evt-1": "2026-10-24T07:00:00+00:00"}}
        finding = {
            "event_id": "evt-1",
            "source": "TRUTH_ARCHIVE_RSS",
            "title": "Tariff announcement",
            "published": "2026-10-24T06:00:00Z",
            "domains": ["TRADE_POLICY"],
            "evidence": "PUBLIC_RSS_ITEM",
            "url": "https://archive.example/posts/1",
        }
        with patch.object(trump_tracker, "send_telegram", return_value=False), patch.object(
            trump_tracker, "save_state"
        ) as save_state:
            trump_tracker.deliver_intelligence_findings([finding], state, chat_id="test-chat")

        self.assertNotIn("evt-1", state["intelligence_items"])
        save_state.assert_called_once_with(state)

    def test_successful_telegram_delivery_keeps_dedup_key(self):
        state = {"intelligence_items": {"evt-1": "2026-10-24T07:00:00+00:00"}}
        finding = {
            "event_id": "evt-1",
            "source": "TRUTH_ARCHIVE_RSS",
            "title": "Tariff announcement",
            "published": "2026-10-24T06:00:00Z",
            "domains": ["TRADE_POLICY"],
            "evidence": "PUBLIC_RSS_ITEM",
            "url": "https://archive.example/posts/1",
        }
        with patch.object(trump_tracker, "send_telegram", return_value=True), patch.object(
            trump_tracker, "save_state"
        ) as save_state:
            trump_tracker.deliver_intelligence_findings([finding], state, chat_id="test-chat")

        self.assertIn("evt-1", state["intelligence_items"])
        save_state.assert_not_called()

    def test_trade_policy_maps_to_watch_candidates_not_orders(self):
        rows = catalyst_watchlist(
            [{"source": "WHITE_HOUSE_RSS", "domains": ["TRADE_POLICY"], "event_id": "evt-1", "evidence": "PUBLIC_RSS_ITEM"}]
        )
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "WATCH" for row in rows))
        self.assertTrue(all("LONG" not in row["status"] and "BUY" not in row["status"] for row in rows))


    def test_gagarin_handoff_is_disabled_without_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            result = trump_tracker.forward_findings_to_gagarin([{
                "event_id": "evt-1",
                "evidence": "PUBLIC_RSS_ITEM",
                "title": "Tariff headline",
                "url": "https://example.gov/news/1",
                "domains": ["TRADE_POLICY"],
            }])
        self.assertIsNone(result)

    @patch("trump_tracker.urllib.request.urlopen")
    def test_gagarin_handoff_posts_only_item_level_catalysts(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "events": [{"event_id": "evt-1", "status": "WATCH_ONLY", "trade_placed": False}]
        }).encode("utf-8")
        urlopen.return_value = response
        findings = [
            {
                "event_id": "evt-1",
                "evidence": "PUBLIC_RSS_ITEM",
                "title": "Tariff headline",
                "url": "https://example.gov/news/1",
                "published": "2026-10-19",
                "domains": ["TRADE_POLICY"],
                "text": "Tariff headline details",
            },
            {
                "event_id": "page-1",
                "evidence": "PUBLIC_SOURCE_TEXT_PAGE_LEVEL",
                "title": "",
                "url": "https://example.gov/",
                "domains": ["TRADE_POLICY"],
            },
        ]
        with patch.dict(os.environ, {
            "GAGARIN_CLOUD_API_URL": "https://gagarin.example",
            "GAGARIN_CLOUD_API_KEY": "test-secret",
        }):
            result = trump_tracker.forward_findings_to_gagarin(findings)

        self.assertFalse(result["events"][0]["trade_placed"])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://gagarin.example/api/sputnik/confirm")
        self.assertEqual(request.get_header("X-api-key"), "test-secret")
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(len(payload["events"]), 1)
        self.assertEqual(payload["events"][0]["event_id"], "evt-1")
        self.assertNotIn("order", payload["events"][0])


if __name__ == "__main__":
    unittest.main()
