import unittest
from sputnik_decision_engine import conditional_plans, decision_message
from sputnik_cfd import build_conditional_trade_plan

class StrictDecisionTests(unittest.TestCase):
    def test_tariff_action(self):
        rows = conditional_plans("The President announces new tariffs on imports.")
        self.assertTrue(rows)
        self.assertEqual(rows[0]["candidate"], "ORO (XAU/USD)")

    def test_generic_mention_is_not_enough(self):
        self.assertEqual(conditional_plans("A speech mentioned tariffs and trade."), [])

    def test_oil_flow_risk(self):
        rows = conditional_plans("Iran threatens shipping near Hormuz and oil exports.")
        self.assertTrue(any(row["candidate"] == "BRENT (petrolio)" for row in rows))

    def test_houthi_attack_language_maps_to_conditional_brent_scenario(self):
        text = "The Houthis emerged again, hitting Saudi Arabia and trying to drive up oil prices."
        rows = conditional_plans(text)
        self.assertTrue(any(row["candidate"] == "BRENT (petrolio)" for row in rows))
        brent = next(row for row in rows if row["candidate"] == "BRENT (petrolio)")
        self.assertIn("LONG", brent["bias"])
        self.assertIn("break", brent["confirmation"].lower())

    def test_not_nice_does_not_suppress_real_attack_evidence(self):
        rows = conditional_plans("The Houthis are hitting Saudi Arabia and trying to drive up oil prices — NOT NICE.")
        self.assertTrue(any(row["candidate"] == "BRENT (petrolio)" for row in rows))

    def test_explicit_negation_still_blocks_oil_disruption_signal(self):
        rows = conditional_plans("The report confirms shipping was not disrupted and oil exports continue normally.")
        self.assertEqual(rows, [])

    def test_message_has_confirmation_and_invalidation(self):
        message = decision_message("The President announces new tariffs on imports.")
        self.assertIn("Conferma richiesta", message)
        self.assertIn("Annulla lo scenario", message)


    def test_broad_topic_gets_useful_watch_result(self):
        message = decision_message("Markets discuss tariffs and trade tensions.")
        self.assertIn("SPUTNIK — OPPORTUNITÀ DI MERCATO", message)
        self.assertIn("PAPER TRADING", message)
        self.assertIn("quotazione aggiornata", message.lower())

    def test_unrelated_text_still_returns_operational_monitoring_result(self):
        message = decision_message("Hello world, nothing market-related here.")
        self.assertIn("SPUTNIK — OPPORTUNITÀ DI MERCATO", message)
        self.assertIn("DIREZIONE: WAIT", message)
        self.assertIn("PAPER TRADING", message)

    def test_empty_legacy_snapshot_still_returns_result(self):
        message = decision_message("")
        self.assertIn("SPUTNIK — OPPORTUNITÀ DI MERCATO", message)
        self.assertIn("IN ATTESA DI CATALIZZATORE", message)

    def test_legacy_domain_labels_produce_domain_watchlist(self):
        message = decision_message("ENERGY METALS DEFENSE")
        self.assertIn("DIREZIONE: WAIT", message)
        self.assertIn("Settore difesa, petrolio e oro", message)

class ConditionalTradePlanTests(unittest.TestCase):
    def test_levels_require_fresh_quote_and_atr(self):
        plan = {"candidate": "BRENT (petrolio)", "bias": "LONG condizionale"}
        missing = build_conditional_trade_plan(plan, {})
        self.assertEqual(missing["status"], "WAIT")
        self.assertIsNone(missing["stop"])

    def test_atr_levels_are_calculated_but_not_auto_confirmed(self):
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).isoformat()
        plan = {"candidate": "BRENT (petrolio)", "bias": "LONG condizionale"}
        quote = {"BRENT": {"price": 100.0, "atr": 2.0, "timestamp": stamp}}
        result = build_conditional_trade_plan(plan, quote)
        self.assertEqual(result["status"], "PREPARE")
        self.assertEqual(result["entry"], 100.0)
        self.assertEqual(result["stop"], 97.0)
        self.assertEqual(result["tp1"], 103.0)
        self.assertEqual(result["tp2"], 106.0)

    def test_old_quote_is_rejected(self):
        plan = {"candidate": "ORO (XAU/USD)", "bias": "LONG condizionale"}
        quote = {"GOLD": {"price": 4200.0, "atr": 20.0, "timestamp": "2020-01-01T00:00:00+00:00"}}
        result = build_conditional_trade_plan(plan, quote)
        self.assertEqual(result["status"], "WAIT")
        self.assertIsNone(result["entry"])

    def test_word_fragment_does_not_count_as_oil_disruption_action(self):
        # "White" contains the substring "hit", but is not evidence of an attack.
        self.assertEqual(
            conditional_plans("White House discusses oil prices in a routine briefing."),
            [],
        )


if __name__ == "__main__":
    unittest.main()

