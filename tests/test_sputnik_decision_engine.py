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


    def test_broad_topic_gets_useful_watch_result(self):
        message = decision_message("Markets discuss tariffs and trade tensions.")
        self.assertIn("MONITORARE", message)
        self.assertIn("NASDAQ-100", message)
        self.assertIn("non comprare", message.lower())

    def test_unrelated_text_still_returns_operational_monitoring_result(self):
        message = decision_message("Hello world, nothing market-related here.")
        self.assertIn("MONITORAGGIO OPERATIVO", message)
        self.assertIn("Nasdaq-100, oro, Brent e USD", message)
        self.assertIn("non una previsione direzionale", message)

    def test_empty_legacy_snapshot_still_returns_result(self):
        message = decision_message("")
        self.assertIn("RISULTATO: MONITORARE, NON IGNORARE", message)
        self.assertIn("DATI INSUFFICIENTI", message)

    def test_legacy_domain_labels_produce_domain_watchlist(self):
        message = decision_message("ENERGY METALS DEFENSE")
        self.assertIn("PETROLIO / OFFERTA ENERGETICA", message)
        self.assertIn("Brent e WTI", message)

if __name__ == "__main__":
    unittest.main()

