import unittest

from trump_tracker import gagarin_confirmation_message


def render_row(row):
    return gagarin_confirmation_message({
        "events": [{
            "title": "Test catalyst",
            "status": "WATCH_ONLY",
            "matched_instruments": [row],
        }]
    })


class GagarinConfirmationMessageTests(unittest.TestCase):
    def test_legacy_wait_keeps_long_bias_and_shows_not_executed(self):
        message = render_row({
            "commodity": "WTI",
            "direction": "LONG",
            "action": "WAIT",
            "price": 72.5,
            "probability": 68,
        })
        self.assertIn("BIAS LONG", message)
        self.assertIn("SETUP EARLY_BIAS", message)
        self.assertIn("TRADE PAPER NOT_EXECUTED", message)
        self.assertIn("72.5", message)
        self.assertNotIn("WAIT", message)

    def test_missing_action_keeps_short_opportunity_direction(self):
        message = render_row({
            "symbol": "BRENT",
            "opportunity_direction": "SHORT",
            "price": 81.2,
        })
        self.assertIn("BIAS SHORT", message)
        self.assertIn("SETUP EARLY_BIAS", message)
        self.assertIn("TRADE PAPER NOT_EXECUTED", message)
        self.assertNotIn("WAIT", message)

    def test_unsupported_direction_is_explicitly_neutral(self):
        message = render_row({
            "commodity": "WHEAT",
            "action": "WAIT",
        })
        self.assertIn("BIAS NEUTRAL / NO_DIRECTION", message)
        self.assertIn("SETUP NEUTRAL", message)
        self.assertIn("TRADE PAPER NOT_EXECUTED", message)
        self.assertNotIn("WAIT", message)

    def test_paper_signal_does_not_infer_confirmed_setup(self):
        message = render_row({
            "commodity": "GOLD",
            "bias": "LONG",
            "action": "PAPER_SIGNAL",
        })
        self.assertIn("BIAS LONG", message)
        self.assertIn("SETUP EARLY_BIAS", message)
        self.assertIn("TRADE PAPER PAPER_CANDIDATE", message)
        self.assertNotIn("WAIT", message)

    def test_explicit_confirmed_setup_is_preserved(self):
        message = render_row({
            "commodity": "GOLD",
            "bias": "LONG",
            "action": "PAPER_SIGNAL",
            "setup": "CONFIRMED",
            "trade_paper": "SIGNAL_ONLY_NOT_EXECUTED",
        })
        self.assertIn("BIAS LONG", message)
        self.assertIn("SETUP CONFIRMED", message)
        self.assertIn("TRADE PAPER SIGNAL_ONLY_NOT_EXECUTED", message)

    def test_confirmed_can_be_inferred_only_from_explicit_paper_authorization(self):
        message = render_row({
            "commodity": "WTI",
            "bias": "SHORT",
            "action": "PAPER_ENTRY",
            "trade_paper": "ENTRY_AUTHORIZED_PAPER_ONLY",
        })
        self.assertIn("BIAS SHORT", message)
        self.assertIn("SETUP CONFIRMED", message)
        self.assertIn("TRADE PAPER ENTRY_AUTHORIZED_PAPER_ONLY", message)


if __name__ == "__main__":
    unittest.main()
