import unittest
from sputnik_decision_engine import conditional_plans, decision_message

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

    def test_message_has_confirmation_and_invalidation(self):
        message = decision_message("The President announces new tariffs on imports.")
        self.assertIn("Conferma richiesta", message)
        self.assertIn("Annulla lo scenario", message)

if __name__ == "__main__":
    unittest.main()
