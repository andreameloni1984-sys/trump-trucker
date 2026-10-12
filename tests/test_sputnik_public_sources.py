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

    def test_invalid_xml_raises(self):
        with self.assertRaises(ValueError):
            parse_public_feed(b"<html>not a feed</html>", "https://example.gov/feed")

    def test_empty_feed_is_valid(self):
        self.assertEqual(parse_public_feed(b"<rss><channel/></rss>", "https://example.gov/feed"), [])

if __name__ == "__main__":
    unittest.main()
