import os
import urllib.error
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import trump_tracker


WHITE_HOUSE = "https://www.whitehouse.gov/news/feed/"
OTHER_FEED = "https://example.gov/feed.xml"
EMPTY_RSS = b"<rss version='2.0'><channel></channel></rss>"


class SputnikPublicFeedBackoffTests(unittest.TestCase):
    def _offline_page(self, *_args, **_kwargs):
        raise OSError("offline fixture")

    def _scan(self, state, now, fetch):
        env = {
            "SPUTNIK_SOCIAL_ENABLED": "1",
            "SPUTNIK_RSS_FEEDS": f"{WHITE_HOUSE};{OTHER_FEED}",
        }
        with (
            patch.dict(os.environ, env),
            patch.object(trump_tracker, "fetch_public_text", side_effect=self._offline_page),
            patch.object(trump_tracker, "fetch_public_feed", side_effect=fetch),
            patch.object(trump_tracker, "utc_now", return_value=now),
        ):
            return trump_tracker.intelligence_snapshot(state)

    def test_429_retry_after_persists_per_feed_then_retries_after_expiry(self):
        fixed = datetime(2026, 10, 28, 4, 0, tzinfo=timezone.utc)
        state, calls = {}, []

        def fetch(url):
            calls.append(url)
            if url == WHITE_HOUSE and calls.count(url) == 1:
                raise urllib.error.HTTPError(url, 429, "Too Many Requests", {"Retry-After": "900"}, None)
            return EMPTY_RSS

        self._scan(state, fixed, fetch)
        saved = state["intelligence_feed_backoff"][WHITE_HOUSE]
        self.assertEqual(saved["reason"], "HTTP_429")
        self.assertEqual(saved["retry_at"], (fixed + timedelta(seconds=900)).isoformat())

        self._scan(state, fixed + timedelta(minutes=5), fetch)
        self.assertEqual(calls.count(WHITE_HOUSE), 1)
        self.assertEqual(calls.count(OTHER_FEED), 2)

        self._scan(state, fixed + timedelta(minutes=16), fetch)
        self.assertEqual(calls.count(WHITE_HOUSE), 2)
        self.assertNotIn(WHITE_HOUSE, state["intelligence_feed_backoff"])

    def test_403_cooldown_is_scoped_to_failing_feed(self):
        fixed = datetime(2026, 10, 28, 4, 0, tzinfo=timezone.utc)
        state, calls = {}, []

        def fetch(url):
            calls.append(url)
            if url == WHITE_HOUSE:
                raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)
            return EMPTY_RSS

        self._scan(state, fixed, fetch)
        self.assertEqual(
            state["intelligence_feed_backoff"][WHITE_HOUSE]["retry_at"],
            (fixed + timedelta(hours=6)).isoformat(),
        )
        self._scan(state, fixed + timedelta(minutes=10), fetch)
        self.assertEqual(calls.count(WHITE_HOUSE), 1)
        self.assertEqual(calls.count(OTHER_FEED), 2)


if __name__ == "__main__":
    unittest.main()
