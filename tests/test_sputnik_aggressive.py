import unittest

from sputnik_aggressive import aggressive_message


class SputnikAggressiveTests(unittest.TestCase):
    def test_empty_state_returns_actionable_monitoring_report(self):
        message = aggressive_message({})
        self.assertIn("SPUTNIK AGGRESSIVO", message)
        self.assertIn("EARLY OPPORTUNITIES", message)
        self.assertIn("Nessun catalizzatore", message)
        self.assertIn("non TRADE", message)

    def test_mode_does_not_promise_automatic_orders(self):
        message = aggressive_message({"intelligence_history": {}, "transactions": {}})
        self.assertIn("NON", message)
        self.assertIn("ordini automatici", message)
        self.assertIn("quotazione aggiornata", message)


if __name__ == "__main__":
    unittest.main()
