import unittest

from sputnik_anticipation import adjacent_sentence_plan, anticipation_message


class SputnikAnticipationTests(unittest.TestCase):
    def test_adjacent_oil_action_and_topic_create_anticipation_only(self):
        text = (
            "Authorities disrupted the route overnight. "
            "Tanker traffic near Hormuz was affected."
        )
        plan = adjacent_sentence_plan(text)
        self.assertIsNotNone(plan)
        self.assertEqual(plan["id"], "oil_supply_disruption")
        self.assertEqual(plan["evidence_mode"], "ADJACENT_SENTENCES")
        self.assertEqual(plan["status"], "ANTICIPATION_ONLY_NEEDS_PRICE_VOLUME_CONFIRMATION")

        message = anticipation_message(plan, "Official public source", quotes={})
        self.assertIn("SPUTNIK — OPPORTUNITÀ ANTICIPATA", message)
        self.assertIn("PAPER TRADING", message)
        self.assertIn("ANTICIPAZIONE, NON SEGNALE CONFERMATO", message)
        self.assertIn("quotazione aggiornata e ATR necessari", message)
        self.assertNotIn("Entry", message)

    def test_ambiguous_adjacent_trade_policy_match_abstains(self):
        text = (
            "The administration announced a new measure. "
            "Tariffs on imports take effect next month."
        )
        self.assertIsNone(adjacent_sentence_plan(text))

    def test_negated_adjacent_action_does_not_create_anticipation(self):
        text = (
            "Authorities did not disrupt the route overnight. "
            "Tanker traffic near Hormuz was affected."
        )
        self.assertIsNone(adjacent_sentence_plan(text))

    def test_existing_strict_match_is_left_to_primary_decision_engine(self):
        text = "The Houthis attacked shipping near Hormuz."
        self.assertIsNone(adjacent_sentence_plan(text))


if __name__ == "__main__":
    unittest.main()
