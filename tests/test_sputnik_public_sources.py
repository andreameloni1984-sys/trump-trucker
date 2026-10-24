import unittest
from datetime import datetime, timezone
from sputnik_public_sources import (
    canonical_public_item_url, parse_public_feed, parse_publication_datetime,
    public_item_identity, publication_is_recent,
)


class PublicationFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 24, 7, 0, tzinfo=timezone.utc)

    def test_iso_and_rfc2822_dates_are_normalized_to_utc(self):
        iso = parse_publication_datetime("2026-10-24T08:30:00+01:00")
        rfc = parse_publication_datetime("Sat, 24 Oct 2026 07:30:00 GMT")
        self.assertEqual(iso, datetime(2026, 10, 24, 7, 30, tzinfo=timezone.utc))
        self.assertEqual(rfc, iso)

    def test_recent_publication_is_accepted(self):
        self.assertTrue(publication_is_recent(
            "Sat, 24 Oct 2026 06:00:00 GMT", now=self.now, max_age_hours=72
        ))

    def test_stale_and_implausibly_future_publications_are_rejected(self):
        self.assertFalse(publication_is_recent(
            "Mon, 19 Oct 2026 06:00:00 GMT", now=self.now, max_age_hours=72
        ))
        self.assertFalse(publication_is_recent(
            "2026-10-24T08:00:00Z", now=self.now, max_age_hours=72
        ))

    def test_naive_iso_timestamp_is_treated_as_utc(self):
        self.assertEqual(
            parse_publication_datetime("2026-10-24T06:00:00"),
            datetime(2026, 10, 24, 6, 0, tzinfo=timezone.utc),
        )

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

    def test_requires_title_valid_date_and_individual_permalink(self):
        raw = b'''<rss><channel>
          <item><title>Missing link</title><pubDate>Mon, 12 Oct 2026 06:00:00 GMT</pubDate></item>
          <item><title>Missing date</title><link>/briefings/no-date</link></item>
          <item><title>Invalid date</title><link>/briefings/bad-date</link><pubDate>soon-ish</pubDate></item>
          <item><title>Homepage only</title><link>https://example.gov/</link><pubDate>Mon, 12 Oct 2026 06:00:00 GMT</pubDate></item>
          <item><title>Valid item</title><link>/briefings/valid</link><guid>valid-1</guid><pubDate>Mon, 12 Oct 2026 06:00:00 GMT</pubDate></item>
        </channel></rss>'''
        rows = parse_public_feed(raw, "https://example.gov/feed/")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Valid item")
        self.assertEqual(rows[0]["url"], "https://example.gov/briefings/valid")

    def test_atom_prefers_alternate_permalink_over_self_link(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><id>item-8</id><title>Tariff decision</title>
          <link rel="self" href="https://example.gov/feed/item-8"/>
          <link rel="alternate" href="https://example.gov/news/tariff-decision"/>
          <updated>2026-10-12T06:00:00Z</updated><summary>Details</summary></entry></feed>'''
        rows = parse_public_feed(raw, "https://example.gov/feed")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["url"], "https://example.gov/news/tariff-decision")

    def test_atom_self_link_without_alternate_is_not_treated_as_article(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><id>item-9</id><title>Generic feed item</title>
          <link rel="self" href="https://example.gov/feed/item-9"/>
          <updated>2026-10-24T06:00:00Z</updated><summary>Details</summary></entry></feed>'''
        rows = parse_public_feed(raw, "https://example.gov/feed")
        self.assertEqual(rows, [])


    def test_canonical_url_removes_tracking_query_and_fragment(self):
        self.assertEqual(
            canonical_public_item_url(
                "HTTPS://Example.GOV/news/story/?utm_source=mail&fbclid=abc&id=7#section"
            ),
            "https://example.gov/news/story?id=7",
        )

    def test_item_identity_prefers_original_permalink_across_archive_mirrors(self):
        first = {
            "url": "https://archive-a.example/post/9?utm_medium=rss",
            "primary_url": "https://social.example/@public/9?utm_source=feed",
            "title": "Same public post",
            "published": "2026-10-24T08:00:00Z",
        }
        second = {
            "url": "https://archive-b.example/post/9",
            "primary_url": "https://social.example/@public/9",
            "title": "Same public post mirrored elsewhere",
            "published": "2026-10-24T08:00:00Z",
        }
        self.assertEqual(public_item_identity(first), public_item_identity(second))

    def test_empty_feed_is_valid(self):
        self.assertEqual(parse_public_feed(b"<rss><channel/></rss>", "https://example.gov/feed"), [])

if __name__ == "__main__":
    unittest.main()
