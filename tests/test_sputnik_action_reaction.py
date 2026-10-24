import unittest

from sputnik_action_reaction import classify_event, classify_claim_status, select_watchlist, match_historical_reactions, infer_direction, action_reaction_message


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

    def test_deescalation_does_not_inherit_escalation_analogue(self):
        text = "The administration announced a tariff pause for 90 days"
        matches = match_historical_reactions(text)
        self.assertEqual([item["id"] for item in matches], ["tariff_pause_2025_04"])
        self.assertNotIn("china_tariff_escalation_2025_10", [item["id"] for item in matches])
        self.assertEqual(infer_direction(matches).get("US_EQUITIES"), "UP")

    def test_explicit_non_imposition_does_not_match_escalation(self):
        text = "The president says the US will not impose new tariffs on China"
        self.assertEqual(classify_event(text), "TRADE_DE_ESCALATION")
        self.assertEqual(match_historical_reactions(text), [])

    def test_denial_of_tariff_report_is_ambiguous(self):
        text = "The administration denies reports of a new tariff hike on China"
        self.assertEqual(classify_event(text), "TRADE_AMBIGUOUS")
        self.assertEqual(match_historical_reactions(text), [])

    def test_generic_tariff_mention_is_not_a_specific_historical_match(self):
        text = "Officials discussed tariffs with China"
        self.assertEqual(match_historical_reactions(text), [])
    def test_threat_is_not_labelled_formal_action(self):
        self.assertEqual(classify_claim_status("Trump threatens to impose new tariffs"), "PROPOSAL_OR_THREAT")

    def test_formal_action_wording_is_distinguished(self):
        self.assertEqual(classify_claim_status("The president signed an executive order imposing tariffs"), "FORMAL_ACTION_WORDING")

    def test_disputed_report_is_marked_unverified(self):
        self.assertEqual(classify_claim_status("Officials deny reports of a new tariff hike"), "UNVERIFIED_OR_DISPUTED")

    def test_alert_shows_claim_status(self):
        message = action_reaction_message("Trump threatens to impose new tariffs")
        self.assertIn("Stato della formulazione: PROPOSAL_OR_THREAT", message)

    def test_china_tariff_news_prioritises_nasdaq(self):
        self.assertEqual(select_watchlist('Trump threatens new tariffs on China')[0]['symbol'], 'NASDAQ-100')

    def test_oil_supply_news_selects_wti(self):
        self.assertEqual(select_watchlist('OPEC announces oil production cut')[0]['symbol'], 'WTI')

    def test_broad_macro_news_selects_sp500(self):
        self.assertEqual(select_watchlist('Federal Reserve interest rate decision')[0]['symbol'], 'S&P 500')

    def test_unrelated_text_does_not_force_instrument(self):
        self.assertEqual(select_watchlist('A political leader visits a museum'), [])

    def test_message_includes_ranked_watchlist(self):
        message = action_reaction_message('Trump threatens new tariffs on China')
        self.assertIn('NASDAQ-100', message)
        self.assertIn('non equivale a un segnale LONG/SHORT', message)

    def test_unknown_event_does_not_invent_direction(self):
        matches = match_historical_reactions("Trump discusses a topic with no documented analogue")
        self.assertEqual(matches, [])
        message = action_reaction_message("Trump discusses a topic with no documented analogue")
        self.assertIn("Nessun analogo storico", message)


if __name__ == "__main__":
    unittest.main()
