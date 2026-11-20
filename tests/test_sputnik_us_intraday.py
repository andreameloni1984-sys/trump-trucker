"""Historical catalysts with deterministic one-minute bars and simulated Telegram."""
from datetime import datetime, timedelta, timezone
from http.client import IncompleteRead
import unittest
from unittest.mock import Mock, patch

from sputnik_public_sources import parse_public_feed
from sputnik_us_intraday import deliver, scan
from sputnik_us_market import evaluate
from sputnik_us_news import FEEDS, catalyst, collect_news, configured_feeds, original_url, read_feed

FED_RELEASE = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm"
PUBLISHED = datetime(2024, 9, 18, 18, tzinfo=timezone.utc)
NOW = PUBLISHED + timedelta(minutes=2)


def fed_notice():
    return {
        "kind": "fed", "source": "Federal Reserve", "published": PUBLISHED.isoformat(),
        "url": FED_RELEASE, "issuer": "", "title": "Federal Reserve issues FOMC statement",
        "text": "The Committee decided to lower the target range for the federal funds rate by 1/2 percentage point.",
    }


def quotes(direction="LONG"):
    start = int(NOW.timestamp()) - 21 * 60
    sign = 1 if direction == "LONG" else -1
    close = [100.0] * 20 + [100 + sign * 0.30]
    return {
        "meta": {
            "symbol": "QQQ", "currency": "USD", "exchangeName": "NGM",
            "instrumentType": "ETF", "currentTradingPeriod": {
                "regular": {"start": start - 3 * 3600, "end": start + 2 * 3600},
            },
        },
        "timestamp": list(range(start, int(NOW.timestamp()), 60)),
        "indicators": {"quote": [{
            "close": close, "high": [p + 0.10 for p in close],
            "low": [p - 0.10 for p in close], "volume": [1000] * 20 + [2000],
        }]},
    }


class SputnikUSTests(unittest.TestCase):
    def setUp(self):
        issuer_lookup = patch("sputnik_us_news._sec_issuers", return_value={})
        issuer_lookup.start()
        self.addCleanup(issuer_lookup.stop)

    def test_historical_fomc_to_telegram_deduplicated_across_feeds_and_runs(self):
        fed = fed_notice()
        news = {**fed, "published": (PUBLISHED + timedelta(minutes=6)).isoformat(), "kind": "press", "title": "Fed cuts interest rates by half a point",
                "url": "https://www.marketwatch.com/story/fed-cuts-rates"}
        state = {}
        send = Mock(return_value=True)

        def confirm(ticker, direction, published, now):
            return evaluate(ticker, direction, published, now, lambda _: quotes())

        outbox = scan([fed, fed], state, NOW, check=confirm, clock=lambda: NOW)
        self.assertEqual(deliver(outbox, send=send, clock=lambda: NOW), 1)
        text = send.call_args.args[0]
        for expected in ("AZIONE: QQQ", "DIREZIONE: LONG", "ENTRY: 100.30", "STOP LOSS: 99.90",
                         "TP1: 100.90", "TP2: 101.30", FED_RELEASE,
                         "committee decided to lower the target range",
                         "STATO: CONFERMATO", "PAPER ONLY"):
            self.assertIn(expected, text)
        later = PUBLISHED + timedelta(minutes=7)
        self.assertEqual(scan([fed, news], state, later, check=confirm, clock=lambda: later), [])
        self.assertEqual(state["events"][news["url"]]["status"], "duplicato")

    def test_ambiguous_historical_executive_order_and_speculation_do_not_create_bias(self):
        item = {**fed_notice(), "kind": "policy", "source": "Casa Bianca",
                "url": "https://www.whitehouse.gov/presidential-actions/2025/04/modifying-reciprocal-tariff-rates-to-reflect-trading-partner-retaliation-and-alignment/",
                "published": "2025-04-10T03:30:00+00:00",
                "title": "Modifying Reciprocal Tariff Rates To Reflect Trading Partner Retaliation and Alignment"}
        self.assertIsNone(catalyst(item))
        for title in ("Trump may impose new tariffs on China", "Trump endorses a candidate",
                      "Trump imposed tariffs on China in 2018?"):
            self.assertIsNone(catalyst({**item, "title": title}))

    def test_verified_short_uses_inverted_levels(self):
        status, plan = evaluate("QQQ", "SHORT", PUBLISHED, NOW, lambda _: quotes("SHORT"))
        self.assertEqual(status, "CONFERMATO")
        self.assertGreater(plan["stop"], plan["entry"])
        self.assertGreater(plan["entry"], plan["tp1"])
        self.assertGreater(plan["tp1"], plan["tp2"])
        self.assertAlmostEqual(plan["rr2"], 2.5)

    def test_missing_data_retains_bias_and_technical_contradiction_blocks_levels(self):
        state = {}
        no_data = Mock(side_effect=OSError)

        def confirm(ticker, direction, published, now):
            return evaluate(ticker, direction, published, now, no_data)

        self.assertEqual(scan([fed_notice()], state, NOW, check=confirm, clock=lambda: NOW), [])
        event = state["events"][FED_RELEASE]
        self.assertEqual(event["bias"]["direction"], "LONG")
        self.assertNotIn("levels", event)
        status, plan = evaluate("QQQ", "LONG", PUBLISHED, NOW, lambda _: quotes("SHORT"))
        self.assertEqual(status, "tecnica contraria al bias")
        self.assertIsNone(plan)

    def test_stale_quote_pre_news_breakout_gaps_and_closed_session_are_ineligible(self):
        for change, published, now in [
            (lambda _: None, PUBLISHED, NOW + timedelta(minutes=5)),
            (lambda _: None, NOW - timedelta(seconds=30), NOW),
            (lambda series: series["timestamp"].__setitem__(-5, 0), PUBLISHED, NOW),
            (lambda series: series["meta"]["currentTradingPeriod"]["regular"].update(
                end=int(NOW.timestamp())), PUBLISHED, NOW),
        ]:
            with self.subTest(published=published, now=now):
                series = quotes()
                change(series)
                self.assertIsNone(evaluate("QQQ", "LONG", published, now, lambda _: series)[1])

    def test_telegram_simulation_drops_expired_message(self):
        send = Mock(return_value=True)
        message = {"quote_timestamp": NOW.isoformat(), "text": "PAPER ONLY"}
        self.assertEqual(deliver([message], send=send, clock=lambda: NOW + timedelta(minutes=2)), 0)
        send.assert_not_called()

    def test_reuters_is_optional_and_feed_failure_is_isolated(self):
        url = "https://feeds.reuters.com/reuters/businessNews"
        with patch.dict("os.environ", {"SPUTNIK_REUTERS_FEED_URL": ""}):
            self.assertEqual(configured_feeds(), FEEDS)
        with patch.dict("os.environ", {"SPUTNIK_REUTERS_FEED_URL": "https://reuters.com.example.org/rss"}):
            self.assertEqual(configured_feeds(), FEEDS)

        fed = next(feed for feed in FEEDS if feed.kind == "fed")
        xml = f"""<rss><channel><item><title>Federal Reserve issues FOMC statement</title>
            <link>{FED_RELEASE}</link>
            <pubDate>Wed, 18 Sep 2024 18:00:00 GMT</pubDate></item></channel></rss>""".encode()

        with patch.dict("os.environ", {"SPUTNIK_REUTERS_FEED_URL": url}):
            reuters = configured_feeds()[-1]
        for error in (OSError("Reuters unavailable"), IncompleteRead(b"")):
            with self.subTest(error=error):
                def fetch(feed_url, *, timeout):
                    if feed_url == url:
                        raise error
                    return xml

                with patch("sputnik_us_news.fetch_public_feed", side_effect=fetch):
                    self.assertEqual([item["url"] for item in collect_news((reuters, fed))], [FED_RELEASE])

    def test_ticker_bias_requires_a_concrete_action_with_unambiguous_direction(self):
        item = {**fed_notice(), "kind": "press"}
        for title in ("FDA approves a new Apple product", "Microsoft will cut revenue guidance",
                      "Will the Fed cut interest rates in December?",
                      "Microsoft didn’t cut revenue guidance",
                      "Microsoft raises revenue guidance but cuts earnings guidance"):
            with self.subTest(title=title):
                self.assertIsNone(catalyst({**item, "title": title}))
        for title, ticker, direction in (
            ("Microsoft cuts revenue guidance", "MSFT", "SHORT"),
            ("Nvidia raises revenue guidance", "NVDA", "LONG"),
            ("US imposes new tariffs on China", "SPY", "SHORT"),
        ):
            bias = catalyst({**item, "title": title})
            self.assertEqual((bias["ticker"], bias["direction"]), (ticker, direction))

    def test_distinct_events_for_same_ticker_can_be_reserved_in_one_scan(self):
        first = fed_notice()
        second = {**first, "url": FED_RELEASE + "-follow-up",
                  "published": (PUBLISHED + timedelta(minutes=1)).isoformat()}
        now = PUBLISHED + timedelta(minutes=12)
        levels = {"entry": 100.0, "stop": 99.0, "tp1": 101.5, "tp2": 102.5,
                  "rr1": 1.5, "rr2": 2.5, "quote_timestamp": now.isoformat()}
        state = {}
        check = Mock(return_value=("CONFERMATO", levels))
        outbox = scan([first, second], state, now, check=check, clock=lambda: now)
        self.assertEqual(len(outbox), 2)
        self.assertEqual(len(state["reservations"]), 2)
        self.assertEqual(scan([first, second], state, now, check=check, clock=lambda: now), [])

    def test_news_selects_new_us_issuer_without_scanning_other_symbols(self):
        item = {**fed_notice(), "kind": "wire",
                "title": "Advanced Micro Devices (NASDAQ: AMD) raises revenue guidance"}
        series = quotes()
        series["meta"].update(symbol="AMD", instrumentType="EQUITY")
        fetch = Mock(return_value=series)

        def confirm(ticker, direction, published, now):
            return evaluate(ticker, direction, published, now, fetch)

        state = {}
        result = scan([item], state, NOW, check=confirm, clock=lambda: NOW, reserve=False)
        self.assertEqual(len(result), 1)
        fetch.assert_called_once_with("AMD")
        self.assertFalse(state["reservations"])
        self.assertEqual(state["events"][item["url"]]["bias"]["uncertainty"], "media")
        with patch("sputnik_us_news._sec_issuers", return_value={"advanced micro devices": {"AMD"}}):
            bias = catalyst({**item, "title": "Advanced Micro Devices raises revenue guidance"})
        self.assertEqual(bias["ticker"], "AMD")

    def test_post_news_reversal_reclaims_support(self):
        series = quotes()
        bars = series["indicators"]["quote"][0]
        bars["low"][-2] = 99.8
        bars["close"][-2] = 99.95
        bars["close"][-1] = 100.05
        bars["high"][-1] = 100.10
        bars["low"][-1] = 99.95
        status, plan = evaluate("QQQ", "LONG", PUBLISHED, NOW, lambda _: series)
        self.assertEqual(status, "CONFERMATO")
        self.assertEqual(plan["setup"], "inversione")
        self.assertLess(plan["stop"], 99.8)

    def test_five_minute_contradiction_blocks_recent_one_minute_breakout(self):
        series = quotes()
        series["timestamp"] = [stamp + 480 for stamp in series["timestamp"]]
        bars = series["indicators"]["quote"][0]
        bars["close"][-6] = 99.98
        bars["close"][-11] = 100.01
        status, levels = evaluate("QQQ", "LONG", PUBLISHED, NOW + timedelta(minutes=8), lambda _: series)
        self.assertEqual(status, "barra a cinque minuti contraria al bias")
        self.assertIsNone(levels)

    def test_truth_uses_only_the_original_post_and_rejects_other_accounts(self):
        feed = next(feed for feed in FEEDS if feed.kind == "truth")
        xml = b"""<rss><channel><item><title>New tariffs</title>
            <link>https://www.trumpstruth.org/statuses/7</link>
            <originalUrl>https://truthsocial.com/@realDonaldTrump/123</originalUrl>
            <pubDate>Wed, 18 Sep 2024 18:00:00 GMT</pubDate>
            </item></channel></rss>"""
        with patch("sputnik_us_news.fetch_public_feed", return_value=xml):
            self.assertEqual(read_feed(feed)[0]["url"], "https://truthsocial.com/@realDonaldTrump/123")
        row = parse_public_feed(xml, feed.url)[0]
        for invalid in ("", "https://truthsocial.com/@other/123",
                        "https://truthsocial.com.example.org/@realDonaldTrump/123"):
            self.assertIsNone(original_url(feed, {**row, "primary_url": invalid}))


if __name__ == "__main__":
    unittest.main()
