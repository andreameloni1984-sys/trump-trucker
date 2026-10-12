import unittest

from sputnik_decision import conditional_plans, decision_message


class ConditionalDecisionTests(unittest.TestCase):
    def test_tariff_mention_returns_if_then_plan(self):
        rows = conditional_plans("Trump announces new tariffs on imports")
        self.assertTrue(rows)
        self.assertEqual(rows[0]["candidate"], "ORO (XAU/USD)")
        self.assertIn("Se viene annunciato", rows[0]["if_then"])

    def test_oil_supply_topic_returns_brent_conditional_plan(self):
        rows = conditional_plans("Iran threatens shipping near Hormuz and oil exports")
        self.assertTrue(any(row["candidate"] == "BRENT (petrolio)" for row in rows))

    def test_unrelated_text_does_not_invent_a_trade(self):
        self.assertEqual(conditional_plans("A speech about education"), [])
        self.assertIn("NESSUN TRADE CONDIZIONALE", decision_message("A speech about education"))

    def test_message_contains_confirmation_and_invalidation(self):
        message = decision_message("A new tariff announcement")
        self.assertIn("Conferma richiesta", message)
        self.assertIn("Annulla lo scenario", message)


if __name__ == "__main__":
    unittest.main()
