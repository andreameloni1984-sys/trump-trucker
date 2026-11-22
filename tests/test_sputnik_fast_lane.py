import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import trump_tracker

FEED = b"""<?xml version="1.0"?><rss><channel><title>t</title>
<item><title>Trump announces new tariffs on steel imports</title>
<link>https://www.trumpstruth.org/statuses/42</link>
<pubDate>%s</pubDate><description>Tariffs on steel</description></item>
</channel></rss>"""


class FastLaneTests(unittest.TestCase):
    def test_feeds_only_skips_homepages_and_keeps_state_stable(self):
        now = datetime.now(timezone.utc)
        feed = FEED % (now - timedelta(minutes=2)).strftime("%a, %d %b %Y %H:%M:%S +0000").encode()
        state = {"intelligence_feed_initialized": {"https://www.trumpstruth.org/feed": "2026-11-01T00:00:00+00:00"}}
        with patch.object(trump_tracker, "fetch_public_text") as homepage, \
                patch.object(trump_tracker, "fetch_feed_with_fallback", return_value=feed), \
                patch.object(trump_tracker, "_configured_rss_feeds", return_value=["https://www.trumpstruth.org/feed"]):
            first = trump_tracker.intelligence_snapshot(state, feeds_only=True)
            second = trump_tracker.intelligence_snapshot(state, feeds_only=True)
        homepage.assert_not_called()
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])  # stesso post: nessun doppione
        self.assertEqual(state["intelligence_feed_initialized"]["https://www.trumpstruth.org/feed"],
                         "2026-11-01T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
