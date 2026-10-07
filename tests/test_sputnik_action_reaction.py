import unittest

from sputnik_action_reaction import classify_event, match_historical_reactions, infer_direction, action_reaction_message


class ActionReactionTests(unittest.TestCase):
    def test_tariff_escalation_matches_historical_event(self):
        text = "Trump announces massive increase in tariffs on China"
        self.assertEqual(classify_event(text), "TRADE_ESCALATION")
        matches = match_historical_reactions(text)
        self.assertTrue(matches)
        self.assertIn("US_EQUITIES", infer_direction(matches))

    def test_trade_softening_matches_deescalation(self):
        text = "Trump says the US wants to help China, not hurt it"
        self.assertEqual(classify_event(text), "TRADE_DE_ESCALATION")
        directions = infer_direction(match_historical_reactions(text))
        self.assertEqual(directions.get("GOLD"), "UP")

    def test_unknown_event_does_not_invent_direction(self):
        matches = match_historical_reactions("Trump discusses a topic with no documented analogue")
        self.assertEqual(matches, [])
        message = action_reaction_message("Trump discusses a topic with no documented analogue")
        self.assertIn("Nessun analogo storico", message)


if __name__ == "__main__":
    unittest.main()
