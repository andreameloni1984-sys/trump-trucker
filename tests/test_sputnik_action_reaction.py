import unittest

from sputnik_action_reaction import (
    action_reaction_message,
    build_action_reaction_record,
    classify_event,
    infer_direction,
    match_historical_reactions,
)


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

    def test_iran_no_war_and_settlement_statement_is_deescalation_not_escalation(self):
        text = (
            "Oil Prices are DROPPING LIKE A ROCK because people feel that there "
            "will not be a War with Iran. Iran wants a settlement, as soon as possible."
        )
        self.assertEqual(classify_event(text), "GEOPOLITICAL_DE_ESCALATION")
        self.assertEqual(match_historical_reactions(text), [])

        record = build_action_reaction_record({"event_id": "truth-43202"}, text)
        self.assertEqual(record["event_type"], "GEOPOLITICAL_DE_ESCALATION")
        self.assertEqual(record["historical_matches"], [])
        self.assertEqual(record["evidence"], "NO_ANALOGUE")

        message = action_reaction_message(text)
        self.assertIn("GEOPOLITICAL_DE_ESCALATION", message)
        self.assertIn("Nessun analogo storico", message)

    def test_explicit_iran_missile_attack_remains_escalation(self):
        text = "Iran launches missiles and threatens to close the Strait of Hormuz"
        self.assertEqual(classify_event(text), "GEOPOLITICAL_ESCALATION")

    def test_homepage_only_analogue_is_excluded(self):
        matches = match_historical_reactions("Trump announces a tariff pause for 90 days")
        self.assertEqual(matches, [])

    def test_deescalation_does_not_inherit_unrelated_same_class_analogue(self):
        matches = match_historical_reactions("Trump announces a tariff pause for 90 days")
        matched_ids = {item["id"] for item in matches}
        self.assertNotIn("trade_softening_2025_10", matched_ids)
        self.assertNotIn("tariff_pause_2025_04", matched_ids)

    def test_unknown_event_does_not_invent_direction(self):
        matches = match_historical_reactions("Trump discusses a topic with no documented analogue")
        self.assertEqual(matches, [])
        message = action_reaction_message("Trump discusses a topic with no documented analogue")
        self.assertIn("Nessun analogo storico", message)


if __name__ == "__main__":
    unittest.main()
