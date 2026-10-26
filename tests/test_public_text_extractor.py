import unittest

from trump_tracker import TextExtractor, _domains_for_public_text


class PublicPageTextExtractorTests(unittest.TestCase):
    def test_json_ld_scripts_styles_and_metadata_do_not_create_market_catalysts(self):
        html = """<!doctype html>
        <html><head>
          <title>Oil, gold and tariffs metadata</title>
          <script type="application/ld+json">
            {"headline":"Oil futures surge after tariffs","keywords":"gold, crude"}
          </script>
        </head><body>
          <p>The public notice says the meeting has been postponed.</p>
          <script>const headline = "gold crude tariffs";</script>
          <style>.headline::after { content: "oil gold"; }</style>
          <noscript>tariffs and oil</noscript>
          <svg><text>gold futures</text></svg>
        </body></html>"""
        parser = TextExtractor()
        parser.feed(html)
        text = parser.text()

        self.assertEqual(text, "The public notice says the meeting has been postponed.")
        self.assertEqual(_domains_for_public_text(text), [])

    def test_visible_body_text_is_preserved_for_source_classification(self):
        parser = TextExtractor()
        parser.feed(
            '<html><head><title>generic metadata</title></head>'
            '<body><h1>President announces new tariffs</h1>'
            '<script>{"headline":"gold prices"}</script></body></html>'
        )

        self.assertEqual(parser.text(), "President announces new tariffs")
        self.assertEqual(_domains_for_public_text(parser.text()), ["TRADE_POLICY"])


if __name__ == "__main__":
    unittest.main()
