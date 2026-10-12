import unittest
from sputnik_entities import normalize_cik, normalize_ticker, normalize_company_name, resolve_sec_issuer

class EntityResolutionTests(unittest.TestCase):
    def test_cik_is_canonical_and_stable(self):
        self.assertEqual(normalize_cik("1849635"), "0001849635")
        self.assertEqual(normalize_cik("CIK 0001849635"), "0001849635")

    def test_invalid_cik_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_cik("")
        with self.assertRaises(ValueError):
            normalize_cik("12345678901")

    def test_ticker_normalization_is_exact(self):
        self.assertEqual(normalize_ticker(" djt "), "DJT")
        self.assertEqual(normalize_ticker("BRK.B"), "BRK.B")
        self.assertEqual(normalize_ticker("not a ticker"), "")

    def test_company_normalization_does_not_change_display_name(self):
        resolved = resolve_sec_issuer("1849635", "  Trump Media & Technology Group Corp.  ", ["DJT"])
        self.assertEqual(resolved["company"], "Trump Media & Technology Group Corp.")
        self.assertEqual(resolved["normalized_company"], "trump media technology group corp")
        self.assertEqual(resolved["entity_id"], "sec:cik:0001849635")
        self.assertEqual(resolved["ticker"], "DJT")
        self.assertEqual(resolved["resolution_method"], "SEC_CIK_EXACT")

    def test_multiple_tickers_are_not_arbitrarily_collapsed(self):
        resolved = resolve_sec_issuer("1849635", "Issuer", ["DJT", "DJT.W"])
        self.assertEqual(resolved["ticker"], "")
        self.assertEqual(resolved["tickers"], "DJT,DJT.W")

if __name__ == "__main__":
    unittest.main()
