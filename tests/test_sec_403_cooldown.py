import urllib.error
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import trump_tracker


class SEC403CooldownTests(unittest.TestCase):
    def setUp(self):
        self._state_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._state_dir.cleanup)
        state_patcher = patch.object(
            trump_tracker, "STATE_FILE", Path(self._state_dir.name) / "sputnik_state.json"
        )
        state_patcher.start()
        self.addCleanup(state_patcher.stop)
        trump_tracker._SEC_403_COOLDOWN_UNTIL = 0.0
        trump_tracker._SEC_403_COOLDOWN_RESTORED = False

    def tearDown(self):
        trump_tracker._SEC_403_COOLDOWN_UNTIL = 0.0
        trump_tracker._SEC_403_COOLDOWN_RESTORED = False

    @patch("trump_tracker.time.monotonic")
    @patch("trump_tracker.urllib.request.urlopen")
    def test_sec_403_suppresses_following_sec_requests(self, urlopen, monotonic):
        url = "https://data.sec.gov/submissions/CIK0000000001.json"
        monotonic.return_value = 100.0
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

    @patch("trump_tracker.time.monotonic", return_value=100.0)
    @patch("trump_tracker.utc_now")
    def test_sec_retry_after_http_date_extends_cooldown(self, utc_now, monotonic):
        from datetime import datetime, timezone

        utc_now.return_value = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
        url = "https://data.sec.gov/submissions/CIK0000000001.json"
        headers = {"Retry-After": "Mon, 26 Oct 2026 20:00:00 GMT"}
        error = urllib.error.HTTPError(url, 403, "Forbidden", headers, None)

        trump_tracker._record_sec_http_error(url, error)

        self.assertEqual(trump_tracker._SEC_403_COOLDOWN_UNTIL, 100.0 + 8 * 60 * 60)

    @patch("trump_tracker.time.monotonic", return_value=100.0)
    def test_invalid_sec_retry_after_falls_back_to_six_hours(self, monotonic):
        url = "https://data.sec.gov/submissions/CIK0000000001.json"
        error = urllib.error.HTTPError(url, 403, "Forbidden", {"Retry-After": "NaN"}, None)

        trump_tracker._record_sec_http_error(url, error)

        self.assertEqual(
            trump_tracker._SEC_403_COOLDOWN_UNTIL,
            100.0 + trump_tracker.SEC_403_COOLDOWN_SECONDS,
        )


    @patch("trump_tracker.time.monotonic", return_value=100.0)
    @patch("trump_tracker.utc_now")
    def test_sec_403_cooldown_survives_restart_and_stale_state_save(self, utc_now, monotonic):
        from datetime import datetime, timezone

        utc_now.return_value = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)
        url = "https://data.sec.gov/submissions/CIK0000000001.json"
        headers = {"Retry-After": "28800"}
        error = urllib.error.HTTPError(url, 403, "Forbidden", headers, None)

        with tempfile.TemporaryDirectory() as temp_dir, patch.object(
            trump_tracker, "STATE_FILE", Path(temp_dir) / "sputnik_state.json"
        ):
            trump_tracker._record_sec_http_error(url, error)
            saved = trump_tracker.load_state()
            deadline = trump_tracker._parse_sec_cooldown_deadline(
                saved.get("sec_cooldown_until_utc")
            )
            self.assertEqual(deadline, datetime(2026, 10, 26, 20, 0, tzinfo=timezone.utc))

            # Simulate a main-cycle state object loaded before the 403. Saving it
            # must not erase the newer cooldown written by the HTTP error handler.
            trump_tracker.save_state({"events": {}, "updated_at": None})
            saved_again = trump_tracker.load_state()
            self.assertEqual(saved_again.get("sec_cooldown_until_utc"), deadline.isoformat())

            # Simulate a process restart: the monotonic value is lost, but the
            # persisted UTC deadline must block the next SEC request.
            trump_tracker._SEC_403_COOLDOWN_UNTIL = 0.0
            trump_tracker._SEC_403_COOLDOWN_RESTORED = False
            with self.assertRaises(trump_tracker.SECSourceCooldown):
                trump_tracker._check_sec_cooldown(url)
            self.assertEqual(
                trump_tracker._SEC_403_COOLDOWN_UNTIL,
                100.0 + 8 * 60 * 60,
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
