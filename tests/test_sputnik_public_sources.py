import unittest
from sputnik_public_sources import parse_public_feed

class PublicFeedParserTests(unittest.TestCase):
    def test_rss_keeps_title_date_url_and_plain_text(self):
        raw = b'''<rss><channel><item>
          <title>President announces new tariffs</title>
          <link>/briefings/tariffs</link><guid>item-123</guid>
          <pubDate>Mon, 12 Oct 2026 06:00:00 GMT</pubDate>
          <description><![CDATA[<p>Policy details <b>here</b>.</p>]]></description>
        </item></channel></rss>'''
        rows = parse_public_feed(raw, "https://example.gov/feed/")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "President announces new tariffs")
        self.assertEqual(rows[0]["url"], "https://example.gov/briefings/tariffs")
        self.assertEqual(rows[0]["id"], "item-123")
        self.assertEqual(rows[0]["published"], "Mon, 12 Oct 2026 06:00:00 GMT")
        self.assertEqual(rows[0]["text"], "Policy details here.")

    def test_atom_link_and_original_url(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:truth="https://example.test/truth">
          <entry><id>status-7</id><title>Oil supply disruption</title>
          <link href="https://archive.example/statuses/7"/>
          <updated>2026-10-12T06:00:00Z</updated>
          <summary type="html">&lt;p&gt;Shipping halted&lt;/p&gt;</summary>
          <truth:originalUrl>https://social.example/@public/7</truth:originalUrl>
          </entry></feed>'''
        rows = parse_public_feed(raw, "https://archive.example/feed")
        self.assertEqual(rows[0]["url"], "https://archive.example/statuses/7")
        self.assertEqual(rows[0]["primary_url"], "https://social.example/@public/7")
        self.assertEqual(rows[0]["text"], "Shipping halted")

    def test_atom_prefers_alternate_link_over_self_link(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><id>status-8</id><title>Oil supply update</title>
          <link rel="self" href="https://archive.example/api/statuses/8"/>
          <link rel="alternate" type="text/html" href="https://archive.example/statuses/8"/>
          <updated>2026-10-26T08:00:00Z</updated>
        </entry></feed>'''
        rows = parse_public_feed(raw, "https://archive.example/feed")
        self.assertEqual(rows[0]["url"], "https://archive.example/statuses/8")

    def test_atom_self_link_alone_is_not_emitted_as_an_item(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><id>status-9</id><title>Oil supply update</title>
          <link rel="self" href="https://archive.example/api/statuses/9"/>
          <updated>2026-10-26T08:00:00Z</updated>
        </entry></feed>'''
        rows = parse_public_feed(raw, "https://archive.example/feed")
        self.assertEqual(rows, [])

    def test_original_public_url_can_supply_missing_archive_permalink(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:truth="https://example.test/truth">
          <entry><id>status-10</id><title>Oil supply update</title>
          <truth:originalUrl>https://social.example/@public/10</truth:originalUrl>
          <updated>2026-10-26T08:00:00Z</updated>
        </entry></feed>'''
        rows = parse_public_feed(raw, "https://archive.example/feed")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["url"], "https://social.example/@public/10")

    def test_invalid_xml_raises(self):
        with self.assertRaises(ValueError):
            parse_public_feed(b"<html>not a feed</html>", "https://example.gov/feed")

    def test_empty_feed_is_valid(self):
        self.assertEqual(parse_public_feed(b"<rss><channel/></rss>", "https://example.gov/feed"), [])

    def test_clean_public_text_ignores_non_visible_markup_content(self):
        from sputnik_public_sources import clean_public_text

        html = """
          <p>Official statement: shipping remains open.</p>
          <script>Oil supply disrupted; tariffs imposed.</script>
          <style>.war { color: red; }</style>
          <template>Hormuz closed; exports halted.</template>
          <noscript>Iran attacks tankers.</noscript>
          <p>Continue monitoring official data.</p>
        """
        cleaned = clean_public_text(html)
        self.assertEqual(
            cleaned,
            "Official statement: shipping remains open. Continue monitoring official data.",
        )
        for hidden_term in ("disrupted", "tariffs", "war", "Hormuz", "tankers"):
            self.assertNotIn(hidden_term.lower(), cleaned.lower())

if __name__ == "__main__":
    unittest.main()
