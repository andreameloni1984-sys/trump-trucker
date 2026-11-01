import json
import os
import tempfile
import unittest
from pathlib import Path
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
        response.__enter__.return_value.read.return_value = json.dumps({"ok": True, "result": {"message_id": 731}}).encode("utf-8")
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

    @patch("trump_tracker.urllib.request.urlopen")
    def test_send_telegram_rejects_missing_or_invalid_message_id(self, urlopen):
        invalid_responses = [
            {"ok": True, "result": {}},
            {"ok": True, "result": {"message_id": 0}},
            {"ok": True, "result": {"message_id": "731"}},
            {"ok": "true", "result": {"message_id": 731}},
        ]
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "TELEGRAM_CHAT_ID": "12345",
        }):
            for payload in invalid_responses:
                response = MagicMock()
                response.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")
                urlopen.return_value = response
                with self.subTest(payload=payload):
                    self.assertFalse(trump_tracker.send_telegram("Sputnik test"))

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
        self.assertEqual(item["url"], "https://example.gov/news/tariffs")
        self.assertIn("TRADE_POLICY", item["domains"])
        self.assertEqual(item["evidence"], "PUBLIC_RSS_ITEM")

    def test_public_item_timestamp_requires_explicit_timezone_and_normalizes_utc(self):
        self.assertIsNone(
            trump_tracker._parse_public_item_timestamp("2026-10-26T06:00:00")
        )
        self.assertIsNone(
            trump_tracker._parse_public_item_timestamp("2026-10-26")
        )
        parsed = trump_tracker._parse_public_item_timestamp(
            "2026-10-26T08:00:00+02:00"
        )
        self.assertEqual(parsed, datetime(2026, 10, 26, 6, 0, tzinfo=timezone.utc))

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
            ("timezone missing", FEED.replace(
                b"<pubDate>Mon, 19 Oct 2026 06:00:00 GMT</pubDate>",
                b"<pubDate>2026-10-26T06:00:00</pubDate>",
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
            "domains": ["TRADE_POLICY"],
        }]
        candidates = trump_tracker.directional_news_candidates(findings)
        self.assertEqual({x["instrument"] for x in candidates}, {"NASDAQ100", "GOLD"})
        self.assertEqual({x["bias"] for x in candidates}, {"SHORT_BIAS", "LONG_BIAS"})
        self.assertTrue(all(x["status"] == "EARLY_BIAS_NEEDS_PRICE_VOLUME_CONFIRMATION" for x in candidates))

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
        self.assertEqual(trump_tracker.directional_news_candidates(page_level), [])
        self.assertEqual(trump_tracker.directional_news_candidates(vague), [])

    def test_directional_news_candidates_rejects_blank_event_identity(self):
        for event_id in ("", "   "):
            with self.subTest(event_id=event_id):
                finding = {
                    "event_id": event_id,
                    "evidence": "PUBLIC_RSS_ITEM",
                    "title": "President announces new tariffs on China",
                    "text": "New tariffs on imports were announced.",
                    "url": "https://example.gov/tariffs",
                    "published": "2026-10-26T10:00:00Z",
                    "source": "WHITE_HOUSE",
                    "domains": ["TRADE_POLICY"],
                }
                self.assertEqual(
                    trump_tracker.directional_news_candidates([finding]), []
                )

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
        self.assertIn("prezzo/volume/ATR graduano SETUP e livelli, non cancellano il BIAS", message)
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
        fresh_item = FEED.replace(
            b"Mon, 19 Oct 2026 06:00:00 GMT", b"Mon, 26 Oct 2026 05:56:00 GMT"
        )
        two_hours_old = FEED.replace(
            b"Mon, 19 Oct 2026 06:00:00 GMT", b"Mon, 26 Oct 2026 04:00:00 GMT"
        )
        two_days_old = FEED.replace(
            b"Mon, 19 Oct 2026 06:00:00 GMT", b"Sat, 24 Oct 2026 06:00:00 GMT"
        )
        cases = (
            ("fresh item", fresh_item, 1),
            ("recent backlog", two_hours_old, 0),
            ("stale item", two_days_old, 0),
        )
        for label, feed, expected_findings in cases:
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
                self.assertEqual(len(findings), expected_findings)
                self.assertEqual(len(state.get("intelligence_items", {})), 1)
                self.assertIn(
                    "https://example.gov/feed.xml",
                    state.get("intelligence_feed_initialized", {}),
                )
                if expected_findings:
                    self.assertEqual(
                        findings[0]["event_id"],
                        next(iter(state["intelligence_items"])),
                    )


    def test_save_state_writes_valid_json_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "sputnik_state.json"
            state = {"events": {"evt-1": {"filed_at": "2026-10-31"}}, "transactions": {}}
            with (
                patch.object(trump_tracker, "STATE_FILE", state_path),
                patch.object(
                    trump_tracker,
                    "utc_now",
                    return_value=datetime(2026, 10, 31, tzinfo=timezone.utc),
                ),
            ):
                trump_tracker.save_state(state)

            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), state)
            self.assertEqual(list(state_path.parent.glob(".sputnik_state.json.*.tmp")), [])

    def test_save_state_never_persists_telegram_chat_id(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "sputnik_state.json"
            state = {
                "events": {"evt-1": {"filed_at": "2026-10-31"}},
                "transactions": {},
                "telegram_chat_id": "private-chat-id",
            }
            with (
                patch.object(trump_tracker, "STATE_FILE", state_path),
                patch.object(
                    trump_tracker,
                    "utc_now",
                    return_value=datetime(2026, 10, 31, tzinfo=timezone.utc),
                ),
            ):
                trump_tracker.save_state(state)

            persisted = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertNotIn("telegram_chat_id", persisted)
            self.assertEqual(state["telegram_chat_id"], "private-chat-id")

    def test_save_state_redacts_legacy_telegram_chat_id_even_without_other_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "sputnik_state.json"
            previous = {
                "events": {"evt-1": {"filed_at": "2026-10-31"}},
                "transactions": {},
                "telegram_chat_id": "legacy-private-chat-id",
                "updated_at": "old",
            }
            state_path.write_text(json.dumps(previous), encoding="utf-8")
            state = dict(previous)
            with (
                patch.object(trump_tracker, "STATE_FILE", state_path),
                patch.object(
                    trump_tracker,
                    "utc_now",
                    return_value=datetime(2026, 11, 1, tzinfo=timezone.utc),
                ),
            ):
                trump_tracker.save_state(state)

            persisted = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertNotIn("telegram_chat_id", persisted)
            self.assertEqual(persisted["events"], previous["events"])

    def test_save_state_preserves_previous_file_and_cleans_temp_on_replace_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "sputnik_state.json"
            previous = {"events": {"old": {"filed_at": "2026-10-30"}}, "updated_at": "old"}
            state_path.write_text(json.dumps(previous), encoding="utf-8")
            next_state = {"events": {"new": {"filed_at": "2026-10-31"}}}

            with (
                patch.object(trump_tracker, "STATE_FILE", state_path),
                patch.object(trump_tracker.os, "replace", side_effect=OSError("simulated replace failure")),
                patch.object(
                    trump_tracker,
                    "utc_now",
                    return_value=datetime(2026, 10, 31, tzinfo=timezone.utc),
                ),
            ):
                with self.assertRaisesRegex(OSError, "simulated replace failure"):
                    trump_tracker.save_state(next_state)

            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), previous)
            self.assertEqual(list(state_path.parent.glob(".sputnik_state.json.*.tmp")), [])


    def test_political_candidate_endorsements_do_not_receive_market_domain_tags(self):
        samples = [
            "Congressman John Rutherford is an incredible Representative for Florida; "
            "as the former Sheriff he is doing a fantastic job representing his district.",
            "It is my Great Honor to endorse Ryan Elijah, a MAGA Warrior running to "
            "represent Florida's 7th Congressional District.",
            "Congressman Randy Fine is a MAGA Warrior doing a fantastic job representing "
            "his district; he is a Harvard educated businessman.",
        ]
        for text in samples:
            with self.subTest(text=text):
                self.assertEqual(
                    trump_tracker._domains_for_public_text(text),
                    ["POLITICAL_CAMPAIGN"],
                )

    def test_endorsement_with_concrete_oil_market_action_keeps_energy_tag(self):
        text = (
            "I endorse the candidate. OPEC announced a crude oil production cut "
            "that reduces physical supply."
        )
        domains = trump_tracker._domains_for_public_text(text)
        self.assertIn("ENERGY", domains)
        self.assertIn("POLITICAL_CAMPAIGN", domains)



    def test_scheduled_workflow_fails_closed_without_telegram_chat_id(self):
        workflow_path = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "trump_tracker.yml"
        )
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn('SPUTNIK_TELEGRAM_POLLING: "0"', workflow)
        self.assertIn(
            "TELEGRAM_CHAT_ID is required: the scheduled collector sets "
            "SPUTNIK_TELEGRAM_POLLING=0 and cannot auto-discover a destination.",
            workflow,
        )
        self.assertNotIn("AUTO-DISCOVERY ATTIVO", workflow)
        self.assertIn("tests/test_sputnik_item_intelligence.py", workflow)


if __name__ == "__main__":
    unittest.main()
