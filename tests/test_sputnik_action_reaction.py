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

    def test_homepage_only_analogue_is_excluded(self):
        matches = match_historical_reactions("Trump announces a tariff pause for 90 days")
        self.assertEqual(matches, [])

    def test_deescalation_does_not_inherit_unrelated_same_class_analogue(self):
        matches = match_historical_reactions("Trump announces a tariff pause for 90 days")
        matched_ids = {item["id"] for item in matches}
        self.assertNotIn("trade_softening_2025_10", matched_ids)
        self.assertNotIn("tariff_pause_2025_04", matched_ids)

    def test_energy_permitting_bill_china_mention_does_not_match_tariff_analogue(self):
        text = (
            "I am urging all Senators to vote for The American Affordability and Jobs Act (S. 5653). "
            "This permitting reform will allow pipelines, mines and power plants to be built faster. "
            "Data centers should build and pay for their own electricity. China will take any data center "
            "that we do not want."
        )
        self.assertEqual(classify_event(text), "OTHER")
        self.assertEqual(match_historical_reactions(text), [])

    def test_truth_archive_snapshot_with_energy_bill_and_iran_does_not_match_tariff_analogue(self):
        text = (
            "I am urging all Senators to vote for The American Affordability and Jobs Act (S. 5653). "
            "This permitting reform will allow pipelines, mines and power plants to be built faster. "
            "China will take any data center that we do not want. "
            "I had an excellent conversation with the Prime Minister of Qatar about Iran and the naval blockade."
        )
        self.assertEqual(classify_event(text), "GEOPOLITICAL_ESCALATION")
        self.assertEqual(match_historical_reactions(text), [])

    def test_unknown_event_does_not_invent_direction(self):
        matches = match_historical_reactions("Trump discusses a topic with no documented analogue")
        self.assertEqual(matches, [])
        message = action_reaction_message("Trump discusses a topic with no documented analogue")
        self.assertIn("Nessun analogo storico", message)


if __name__ == "__main__":
    unittest.main()
