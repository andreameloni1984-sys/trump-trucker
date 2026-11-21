import os
import unittest
from unittest.mock import patch

import sputnik_t212_demo_check as chk


class DemoCheckTests(unittest.TestCase):
    def test_split_credentials(self):
        self.assertEqual(chk.split_credentials("k\ns", "")[:2], ("k", "s"))
        self.assertEqual(chk.split_credentials("k:s", "")[:2], ("k", "s"))
        self.assertEqual(chk.split_credentials(" k ", " s "), ("k", "s", ""))

    def test_missing_keys(self):
        with patch.dict(os.environ, {"SPUTNIK_INVEST_DEMO_API_KEY": "", "SPUTNIK_INVEST_DEMO_API_SECRET": ""}):
            ok, text = chk.run()
        self.assertFalse(ok)
        self.assertIn("mancanti", text)

    def test_success_is_read_only(self):
        calls = []

        def fake_get(path, auth):
            calls.append(path)
            return {
                "/equity/account/cash": (200, {"total": 5000, "free": 4000, "invested": 1000, "ppl": 12}),
                "/equity/account/info": (200, {"currencyCode": "EUR"}),
                "/equity/portfolio": (200, [{"ticker": "AAPL_US_EQ", "quantity": 2, "ppl": 3}]),
            }[path]

        with patch.dict(os.environ, {"SPUTNIK_INVEST_DEMO_API_KEY": "k", "SPUTNIK_INVEST_DEMO_API_SECRET": "s"}), \
                patch.object(chk, "_get", side_effect=fake_get):
            ok, text = chk.run()
        self.assertTrue(ok)
        self.assertIn("4000 EUR", text)
        self.assertTrue(all("order" not in p for p in calls))

    def test_401_hint(self):
        with patch.dict(os.environ, {"SPUTNIK_INVEST_DEMO_API_KEY": "k", "SPUTNIK_INVEST_DEMO_API_SECRET": "s"}), \
                patch.object(chk, "_get", return_value=(401, None)):
            ok, text = chk.run()
        self.assertFalse(ok)
        self.assertIn("DEMO", text)


if __name__ == "__main__":
    unittest.main()
