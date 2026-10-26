import json
import os
import unittest
from datetime import datetime, timezone
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
    @patch("trump_tracker.urllib.request.urlopen")
    def test_send_telegram_removes_persistent_reply_keyboard(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({"ok": True}).encode("utf-8")
        urlopen.return_value = response
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "TELEGRAM_CHAT_ID": "12345",
        }):
            sent = trump_tracker.send_telegram("Sputnik test")

        self.assertTrue(sent)
        request = urlopen.call_args.args[0]
        from urllib.parse import parse_qs
        payload = parse_qs(request.data.decode("utf-8"))
        self.assertEqual(json.loads(payload["reply_markup"][0]), {"remove_keyboard": True})
        self.assertEqual(payload["text"][0], "Sputnik test")

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
        with (
            patch.dict(os.environ, {"SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml"}),
            patch.object(trump_tracker, "utc_now", return_value=datetime(2026, 10, 19, 6, 1, tzinfo=timezone.utc)),
        ):
            first = trump_tracker.intelligence_snapshot(state)
            second = trump_tracker.intelligence_snapshot(state)

        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        item = first[0]
        self.assertEqual(item["title"], "President announces new tariffs on China")
        self.assertEqual(item["published"], "Mon, 19 Oct 2026 06:00:00 GMT")
        self.assertEqual(item["event_time"], "2026-10-19T06:00:00+00:00")
        self.assertEqual(item["available_at"], "2026-10-19T06:01:00+00:00")
        self.assertEqual(item["url"], "https://example.gov/news/tariffs")
        self.assertIn("TRADE_POLICY", item["domains"])
        self.assertEqual(item["evidence"], "PUBLIC_RSS_ITEM")

    def test_feed_candidates_need_valid_publication_time_and_item_permalink(self):
        fixed_now = datetime(2026, 10, 26, 6, 0, tzinfo=timezone.utc)
        cases = [
            ("missing publication date", FEED.replace(
                b"<pubDate>Mon, 19 Oct 2026 06:00:00 GMT</pubDate>", b""
            )),
            ("unparseable publication date", FEED.replace(
                b"<pubDate>Mon, 19 Oct 2026 06:00:00 GMT</pubDate>",
                b"<pubDate>soon</pubDate>",
            )),
            ("future publication date", FEED.replace(
                b"<pubDate>Mon, 19 Oct 2026 06:00:00 GMT</pubDate>",
                b"<pubDate>Mon, 26 Oct 2026 06:10:00 GMT</pubDate>",
            )),
            ("feed URL used as item permalink", FEED.replace(
                b"<link>https://example.gov/news/tariffs</link>", b""
            )),
        ]
        for label, feed in cases:
            with self.subTest(case=label):
                state = {}
                with (
                    patch.object(trump_tracker, "fetch_public_text", side_effect=OSError("offline in test")),
                    patch.object(trump_tracker, "fetch_public_feed", return_value=feed),
                    patch.object(trump_tracker, "utc_now", return_value=fixed_now),
                    patch.dict(os.environ, {
                        "SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml",
                        "SPUTNIK_SOCIAL_ENABLED": "1",
                    }),
                ):
                    findings = trump_tracker.intelligence_snapshot(state)
                self.assertEqual(findings, [])
                self.assertEqual(state.get("intelligence_items"), {})

    def test_default_feeds_include_item_level_trump_archive_rss(self):
        with patch.dict(os.environ, {}, clear=True):
            feeds = trump_tracker._configured_rss_feeds()

        self.assertIn("https://www.whitehouse.gov/feed/", feeds)
        self.assertIn("https://www.trumpstruth.org/feed", feeds)

    def test_page_level_archive_message_warns_not_an_individual_catalyst(self):
        message = trump_tracker.intelligence_message({
            "source": "TRUTH_ARCHIVE",
            "evidence": "PUBLIC_SOURCE_TEXT_PAGE_LEVEL",
            "domains": ["METALS", "AI_TECH"],
            "text": "Trump's Truth archive page with generic metadata",
            "url": "https://www.trumpstruth.org/",
        })
        self.assertIn("EVIDENZA INSUFFICIENTE", message)
        self.assertIn("non un post o articolo individuale", message)
        self.assertIn("Non trattare le parole chiave della pagina come notizia", message)
        self.assertNotIn("Stato: CATALIZZATORE DA VERIFICARE", message)

    def test_directional_news_candidates_maps_explicit_trade_escalation_to_hypotheses(self):
        findings = [{
            "event_id": "tariff-1",
            "evidence": "PUBLIC_RSS_ITEM",
            "title": "President announces new tariffs on China",
            "text": "New tariffs on imports were announced.",
            "url": "https://example.gov/tariffs",
            "published": "2026-10-26T10:00:00Z",
            "source": "WHITE_HOUSE",
            "detected_at": "2026-10-26T10:01:00Z",
            "domains": ["TRADE_POLICY"],
        }]
        candidates = trump_tracker.directional_news_candidates(findings, now=datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc))
        self.assertEqual({x["instrument"] for x in candidates}, {"NASDAQ100", "GOLD"})
        self.assertEqual({x["bias"] for x in candidates}, {"SHORT_BIAS", "LONG_BIAS"})
        self.assertTrue(all(x["status"] == "BIAS_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION" for x in candidates))

    def test_directional_news_candidates_rejects_page_level_and_ambiguous_headlines(self):
        page_level = [{
            "event_id": "page-1", "evidence": "PUBLIC_SOURCE_TEXT_PAGE_LEVEL",
            "title": "New tariffs", "text": "new tariffs", "url": "https://example.gov/",
            "published": "2026-10-26T10:00:00Z", "domains": ["TRADE_POLICY"],
        }]
        vague = [{
            "event_id": "evt-2", "evidence": "PUBLIC_RSS_ITEM",
            "title": "Trump speaks today", "text": "Remarks are expected.",
            "url": "https://example.gov/remarks", "published": "2026-10-26T10:00:00Z",
            "domains": ["TRADE_POLICY"],
        }]
        self.assertEqual(trump_tracker.directional_news_candidates(page_level, now=datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc)), [])
        self.assertEqual(trump_tracker.directional_news_candidates(vague, now=datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc)), [])


    def test_directional_news_candidates_rejects_stale_future_and_unparseable_timestamps(self):
        from sputnik_catalyst import directional_news_candidates

        now = datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc)
        base = {
            "event_id": "tariff-point-in-time",
            "evidence": "PUBLIC_RSS_ITEM",
            "title": "President announces new tariffs on China",
            "text": "New tariffs on imports were announced.",
            "url": "https://example.gov/tariffs",
            "source": "WHITE_HOUSE",
            "detected_at": "2026-10-26T10:01:00Z",
            "domains": ["TRADE_POLICY"],
        }
        for published in (
            "2026-10-26T05:00:00Z",  # older than the four-hour action window
            "2026-10-26T10:20:00Z",  # materially in the future
            "not-a-timestamp",
            None,
        ):
            with self.subTest(published=published):
                self.assertEqual(
                    directional_news_candidates([{**base, "published": published}], now=now),
                    [],
                )

    def test_directional_news_candidates_enforces_event_available_decision_order(self):
        from sputnik_catalyst import directional_news_candidates

        now = datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc)
        base = {
            "event_id": "ordered-tariff",
            "evidence": "PUBLIC_RSS_ITEM",
            "title": "President announces new tariffs on China",
            "text": "New tariffs on imports were announced.",
            "url": "https://example.gov/tariffs",
            "published": "2026-10-26T10:04:00Z",
            "source": "WHITE_HOUSE",
            "detected_at": "2026-10-26T10:04:30Z",
            "domains": ["TRADE_POLICY"],
        }
        candidates = directional_news_candidates([base], now=now)
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0]["event_time"], "2026-10-26T10:04:00+00:00")
        self.assertEqual(candidates[0]["available_at"], "2026-10-26T10:04:30+00:00")
        self.assertEqual(candidates[0]["decision_time"], "2026-10-26T10:05:00+00:00")

        invalid_availability = [
            {**base, "detected_at": None},
            {**base, "detected_at": "2026-10-26T10:06:00Z"},
            {**base, "published": "2026-10-26T10:10:00Z"},
        ]
        for finding in invalid_availability:
            with self.subTest(finding=finding):
                self.assertEqual(directional_news_candidates([finding], now=now), [])

    def test_directional_news_candidates_accepts_fresh_iso_and_rfc822_times(self):
        from sputnik_catalyst import directional_news_candidates

        now = datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc)
        base = {
            "event_id": "fresh-tariff",
            "evidence": "PUBLIC_RSS_ITEM",
            "title": "President announces new tariffs on China",
            "text": "New tariffs on imports were announced.",
            "url": "https://example.gov/tariffs",
            "source": "WHITE_HOUSE",
            "detected_at": "2026-10-26T10:01:00Z",
            "domains": ["TRADE_POLICY"],
        }
        for published in ("2026-10-26T10:00:00Z", "Mon, 26 Oct 2026 10:00:00 GMT"):
            with self.subTest(published=published):
                rows = directional_news_candidates([{**base, "published": published}], now=now)
                self.assertEqual({row["instrument"] for row in rows}, {"NASDAQ100", "GOLD"})

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


    def test_intelligence_digest_batches_many_items_and_labels_them_not_signals(self):
        items = [
            {
                "event_id": f"evt-{i}",
                "evidence": "PUBLIC_RSS_ITEM",
                "source": "PUBLIC_RSS",
                "title": f"Public event {i}",
                "published": f"2026-10-26T06:{i:02d}:00Z",
                "url": f"https://example.gov/news/{i}",
                "domains": ["ENERGY"],
            }
            for i in range(60)
        ]
        message = trump_tracker.intelligence_digest_message(items)
        self.assertIn("Nuovi eventi pubblici verificabili: 60", message)
        self.assertIn("NON segnali confermati", message)
        self.assertIn("Nessun LONG/SHORT viene emesso senza identificazione dello strumento", message)
        self.assertIn("e altri 55 eventi", message)
        self.assertEqual(message.count("https://example.gov/news/"), 5)

    def test_intelligence_digest_suppresses_page_level_and_missing_metadata(self):
        items = [
            {
                "event_id": "page-1",
                "evidence": "PUBLIC_SOURCE_TEXT_PAGE_LEVEL",
                "url": "https://example.gov/",
                "title": "Generic homepage",
                "published": "",
            },
            {
                "event_id": "no-url",
                "evidence": "PUBLIC_RSS_ITEM",
                "title": "Missing permalink",
                "published": "2026-10-26T06:00:00Z",
            },
        ]
        self.assertIsNone(trump_tracker.intelligence_digest_message(items))

    @patch.object(trump_tracker, "fetch_public_text", side_effect=OSError("offline in test"))
    def test_first_scan_seeds_feed_backlog_without_emitting_old_items(self, _fetch_page):
        fixed_now = datetime(2026, 10, 26, 6, 0, tzinfo=timezone.utc)
        two_hours_old = FEED.replace(
            b"Mon, 19 Oct 2026 06:00:00 GMT", b"Mon, 26 Oct 2026 04:00:00 GMT"
        )
        two_days_old = FEED.replace(
            b"Mon, 19 Oct 2026 06:00:00 GMT", b"Sat, 24 Oct 2026 06:00:00 GMT"
        )
        for label, feed in (("recent backlog", two_hours_old), ("stale item", two_days_old)):
            with self.subTest(case=label):
                state = {}
                with (
                    patch.dict(os.environ, {
                        "SPUTNIK_RSS_FEEDS": "https://example.gov/feed.xml",
                        "SPUTNIK_SOCIAL_ENABLED": "1",
                        "SPUTNIK_PUBLIC_ITEM_MAX_AGE_HOURS": "24",
                    }),
                    patch.object(trump_tracker, "fetch_public_feed", return_value=feed),
                    patch.object(trump_tracker, "utc_now", return_value=fixed_now),
                ):
                    findings = trump_tracker.intelligence_snapshot(state)
                self.assertEqual(findings, [])
                self.assertEqual(len(state.get("intelligence_items", {})), 1)
                self.assertIn("https://example.gov/feed.xml", state.get("intelligence_feed_initialized", {}))


    def test_directional_candidates_sort_mixed_timestamp_formats_by_utc(self):
        now = datetime(2026, 10, 26, 10, 5, tzinfo=timezone.utc)
        base = {
            "evidence": "PUBLIC_RSS_ITEM",
            "title": "President announces new tariffs on China",
            "text": "New tariffs on imports were announced.",
            "url": "https://example.gov/tariffs",
            "source": "WHITE_HOUSE",
            "domains": ["TRADE_POLICY"],
        }
        older_rfc822 = {
            **base,
            "event_id": "older-rfc822",
            "published": "Mon, 26 Oct 2026 09:00:00 GMT",
            "detected_at": "2026-10-26T09:01:00Z",
        }
        newer_iso = {
            **base,
            "event_id": "newer-iso",
            "published": "2026-10-26T10:00:00Z",
            "detected_at": "2026-10-26T10:01:00Z",
        }

        rows = trump_tracker.directional_news_candidates(
            [older_rfc822, newer_iso], now=now
        )
        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(rows[0]["event_id"], "newer-iso")
        self.assertEqual(rows[0]["event_time"], "2026-10-26T10:00:00+00:00")

if __name__ == "__main__":
    unittest.main()
