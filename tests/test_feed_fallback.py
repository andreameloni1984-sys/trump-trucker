import unittest
import urllib.error
from unittest.mock import patch

import trump_tracker


def http_error(code):
    return urllib.error.HTTPError("u", code, "x", {}, None)


class FeedFallbackTests(unittest.TestCase):
    def test_404_uses_first_working_alternative(self):
        calls = []

        def fake(url, timeout=20):
            calls.append(url)
            if url == "https://www.whitehouse.gov/presidential-actions/feed/":
                return b"<rss/>"
            raise http_error(404)

        with patch.object(trump_tracker, "fetch_public_feed", side_effect=fake):
            self.assertEqual(trump_tracker.fetch_feed_with_fallback("https://www.whitehouse.gov/feed/"), b"<rss/>")
        self.assertEqual(calls[0], "https://www.whitehouse.gov/feed/")
        self.assertIn("https://www.whitehouse.gov/news/feed/", calls)

    def test_other_errors_not_retried(self):
        with patch.object(trump_tracker, "fetch_public_feed", side_effect=http_error(403)):
            with self.assertRaises(urllib.error.HTTPError):
                trump_tracker.fetch_feed_with_fallback("https://www.whitehouse.gov/feed/")

    def test_unknown_feed_404_raises(self):
        with patch.object(trump_tracker, "fetch_public_feed", side_effect=http_error(404)):
            with self.assertRaises(urllib.error.HTTPError):
                trump_tracker.fetch_feed_with_fallback("https://www.trumpstruth.org/feed")


if __name__ == "__main__":
    unittest.main()
