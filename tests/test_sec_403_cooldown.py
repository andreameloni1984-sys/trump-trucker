import urllib.error
import unittest
from unittest.mock import Mock, patch

import trump_tracker


class SEC403CooldownTests(unittest.TestCase):
    def setUp(self):
        trump_tracker._SEC_403_COOLDOWN_UNTIL = 0.0

    def tearDown(self):
        trump_tracker._SEC_403_COOLDOWN_UNTIL = 0.0

    @patch("trump_tracker.time.monotonic")
    @patch("trump_tracker.urllib.request.urlopen")
    def test_sec_403_suppresses_following_sec_requests(self, urlopen, monotonic):
        url = "https://data.sec.gov/submissions/CIK0000000001.json"
        monotonic.side_effect = [100.0, 100.0, 101.0]
        urlopen.side_effect = urllib.error.HTTPError(url, 403, "Forbidden", {}, None)

        with self.assertRaises(urllib.error.HTTPError):
            trump_tracker.http_get_json(url, "SPUTNIK/test")

        with self.assertRaises(trump_tracker.SECSourceCooldown):
            trump_tracker.fetch_public_document(
                "https://www.sec.gov/Archives/edgar/data/1/index.json",
                "SPUTNIK/test",
            )

        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(
            trump_tracker._SEC_403_COOLDOWN_UNTIL,
            100.0 + trump_tracker.SEC_403_COOLDOWN_SECONDS,
        )

    @patch("trump_tracker.urllib.request.urlopen")
    def test_non_sec_public_documents_are_not_blocked_by_sec_cooldown(self, urlopen):
        trump_tracker._SEC_403_COOLDOWN_UNTIL = 99999.0
        response = Mock()
        response.read.return_value = b"public"
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        urlopen.return_value = context

        result = trump_tracker.fetch_public_document(
            "https://www.whitehouse.gov/feed/",
            "SPUTNIK/test",
        )

        self.assertEqual(result, b"public")
        urlopen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
